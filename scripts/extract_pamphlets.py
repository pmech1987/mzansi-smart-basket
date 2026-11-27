#!/usr/bin/env python3
"""
Mzansi Smart Basket — AI-assisted retail-offer candidate extractor.
--------------------------------------------------------------------
- Processes only exact local files and remote HTTPS hosts recorded in
  `approved_sources.json`; both source use and Gemini document upload require
  explicit operator approval and are disabled by default.
- Writes AI output to `deals_pending_review.json`, never straight to the live
  `deals.json` feed. A human must check the actual source and approve each offer.
- Preserves source and validity details and uses SHA-256 caching to reduce
  repeated Gemini processing. AI extraction is not proof that a price is true
  or that a source may be reused.
"""
import hashlib
import json
import os
import re
import sys
import tempfile
import time
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Dict, List, Literal, Optional, Tuple
from urllib.parse import urlparse

import requests
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

try:
    from pypdf import PdfReader, PdfWriter
    HAS_PYPDF = True
except Exception:
    HAS_PYPDF = False

PAMPHLET_DIR = Path("pamphlets")
URLS_FILE = Path("pamphlet_urls.txt")
APPROVED_SOURCES_FILE = Path("approved_sources.json")
CACHE_FILE = Path(".pamphlet_cache.json")
OUTPUT_FILE = Path("deals.json")
CANDIDATE_FILE = Path("deals_pending_review.json")
SUPPORTED_EXTS = {".pdf", ".png", ".jpg", ".jpeg", ".webp"}
CHUNK_PAGES = 1  # One-page units make coverage counts and retries attributable to exact pages
CACHE_SCHEMA_VERSION = 4
COVERAGE_FILE = Path("coverage_report.json")
MAX_SOURCE_FILE_BYTES = max(1, int(os.environ.get("MAX_SOURCE_FILE_MB", "100"))) * 1024 * 1024

HEADERS = {
    "User-Agent": "MzansiSmartBasket-OfferImporter/1.0 (authorised-source-only; contact details supplied by operator)",
    "Accept": "text/html,application/xhtml+xml,application/pdf,image/*;q=0.9,*/*;q=0.8",
}

DEPARTMENTS = Literal[
    "Staples & Grain",
    "Meat, Poultry & Deli",
    "Dairy & Eggs",
    "Bakery & Bread",
    "Fruit & Veg",
    "Pantry & Tins",
    "Snacks & Drinks",
    "Household & Cleaning",
    "Personal Care & Baby",
    "Gadgets & Appliances",
    "Clothing & Footwear",
    "Other Specials",
]

DEAL_TYPES = Literal[
    "3-Day Flash",
    "Weekly Special",
    "Monthly Combo",
    "Payday Deal",
    "Appliances & Tech",
]


class ExtractedDeal(BaseModel):
    canonical_name: str = Field(
        description="Standardized SA product name with pack size/model first, e.g. '5kg IQF Mixed Chicken Portions', '1kg Smoked Russians', '5L Digital Air Fryer'."
    )
    brand: Optional[str] = Field(default=None)
    pack_size: Optional[str] = Field(default=None)
    category: DEPARTMENTS
    emoji: str = Field(description="Single matching emoji")
    store: str = Field(description="Retailer name (Shoprite, Boxer, Pick n Pay, Checkers, SPAR, PEP, Ackermans, Game, etc.)")
    normal_price: float = Field(description="Regular non-card price in ZAR")
    reward_price: float = Field(description="Loyalty card price in ZAR if shown, else equal to normal_price")
    card: Optional[Literal["xtra", "smart", "boxer", "spar"]] = Field(default=None)
    multi_buy_note: Optional[str] = Field(default=None, description="e.g. '2 for R45', 'Combo Deal', 'Limit 4'")
    unit_price_note: Optional[str] = Field(default=None, description="e.g. 'R10.50/kg' or 'R15.00 each'")
    pamphlet_title: str = Field(description="Exact pamphlet title/campaign")
    deal_type: DEAL_TYPES = Field(default="Weekly Special")
    provinces: List[str] = Field(default_factory=lambda: ["All"])
    valid_from: Optional[str] = Field(default=None, description="YYYY-MM-DD if printed")
    valid_until: Optional[str] = Field(default=None, description="YYYY-MM-DD if printed")
    valid_from_at: Optional[str] = Field(default=None, description="ISO-8601 instant with +02:00 offset if a start time is explicitly printed; otherwise null")
    valid_until_at: Optional[str] = Field(default=None, description="ISO-8601 instant with +02:00 offset if an end time is explicitly printed; otherwise null")


class PamphletExtraction(BaseModel):
    store_detected: str
    pamphlet_title: str
    # Required per-page count. A zero-offer page must explicitly report zero.
    page_priced_offer_count: int = Field(..., ge=0, description="Count of every distinct visible priced offer on this single page")
    deals: List[ExtractedDeal]


class PageCountAudit(BaseModel):
    page_priced_offer_count: int = Field(..., ge=0, description="Independent second-pass count of distinct priced offer blocks visible on the page")
    observations: List[str] = Field(default_factory=list, description="Short notes about dense areas, grids or ambiguous price blocks")


PAGE_AUDIT_PROMPT = """
You are performing a separate second-pass visual completeness audit of ONE South African retail pamphlet page.
Do NOT extract product names, brands or prices. Count every visually distinct product/promotion block that has a price attached.
Count separate varieties or sizes separately when they are separately priced. Count a bundle/combination as one offer block when it has one displayed price. Do not count page numbers, footers, legal text, store addresses or unpriced editorial images.
Return the exact number of priced offer blocks and brief notes about dense grids, small corner offers, meat/butchery sections, electronics, clothing or other hard-to-read areas. If the page has no priced offers, return zero. Do not copy or reproduce the page artwork.
"""


EXTRACTION_PROMPT = """
You are an exhaustive South African retail pamphlet extraction engine.
CRITICAL REQUIREMENT: Extract EVERY SINGLE PRICED ITEM visible on this ONE PAGE.
Do NOT summarize, do NOT sample, do NOT skip small corner deals, braai packs, chicken portions, Russians, pies, gadgets, appliances, clothing, or combos.
If the page has 40 offers, return ALL 40 offers. This is a single-page input, never a multi-page batch.

Rules:
1. Standardize canonical_name with size/pack first so identical items across Shoprite, Boxer, Pick n Pay, Checkers, SPAR, PEP, and Game match onto the same comparison card.
2. Separate normal_price and reward_price. Map loyalty cards: Shoprite/Checkers -> "xtra", Pick n Pay -> "smart", Boxer -> "boxer", SPAR -> "spar", others -> null.
3. Capture exact valid_from and valid_until in YYYY-MM-DD whenever printed anywhere on the page/header.
4. Capture regional validity in provinces (e.g. Inland -> ["Gauteng","Mpumalanga","Limpopo","North West","Free State"]); otherwise ["All"].
5a. valid_from/valid_until are PER ITEM (a '3-day weekend special' ends earlier than the pamphlet). For '2 for R45' put 22.50 in reward_price and the text in multi_buy_note.
5b. If an item shows only ONE price, put it in BOTH normal_price and reward_price; never skip an item for lacking a was-price.
5c. Before listing, count the priced items on each page and make sure your list has at least that many.
5. Never invent a price — only extract prices visibly printed on the page.
6. Capture an exact offer start/end time only when the time is explicitly printed. Encode South African local time with the +02:00 offset in ISO-8601. If no time is printed, leave valid_from_at/valid_until_at null; do not invent a clock time.
7. Set page_priced_offer_count to the exact number of distinct priced offers visible on this page.
8. Return exactly one deals record per priced offer counted. Do not merge distinct varieties, pack sizes, price tiers, bundles or loyalty offers.
9. A page with no priced offers MUST return page_priced_offer_count=0 and deals=[]. Never use zero as a fallback when the page is unclear.
"""


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def normalize_slug(text: str) -> str:
    s = text.lower()
    s = re.sub(r"(\d+)\s+(kg|g|l|ml|pack|pk)\b", r"\1\2", s)
    return re.sub(r"[^a-z0-9]+", "_", s).strip("_")


def today_sast() -> date:
    from datetime import timedelta
    return (datetime.now(timezone.utc) + timedelta(hours=2)).date()


def is_expired(valid_until: Optional[str], valid_until_at: Optional[str] = None) -> bool:
    """Use a printed expiry instant when present; otherwise include the printed end date."""
    try:
        from zoneinfo import ZoneInfo
        local_tz = ZoneInfo("Africa/Johannesburg")
        now_local = datetime.now(local_tz)
        if valid_until_at:
            raw = str(valid_until_at).strip().replace("Z", "+00:00")
            instant = datetime.fromisoformat(raw)
            if instant.tzinfo is None:
                instant = instant.replace(tzinfo=local_tz)
            return instant.astimezone(local_tz) <= now_local
        if not valid_until:
            return False
        return date.fromisoformat(str(valid_until)[:10]) < now_local.date()
    except Exception:
        # A malformed explicit instant must not silently keep an offer live.
        return bool(valid_until_at)



def load_previous_best_prices() -> Dict[str, float]:
    """Reads existing deals.json to detect real week-over-week price drops."""
    prev: Dict[str, float] = {}
    if not OUTPUT_FILE.exists():
        return prev
    try:
        old = json.loads(OUTPUT_FILE.read_text(encoding="utf-8"))
        for prod in old.get("products", []):
            stores = prod.get("stores") or []
            if stores:
                best = min(float(s.get("rewardPrice") or s.get("price") or 0) for s in stores)
                if best > 0:
                    prev[prod["id"]] = best
    except Exception:
        pass
    return prev

def load_carried_prev() -> Dict[str, float]:
    try:
        old = json.loads(OUTPUT_FILE.read_text(encoding="utf-8"))
        return {p["id"]: float(p["prevBestPrice"]) for p in old.get("products", []) if p.get("prevBestPrice")}
    except Exception:
        return {}


def load_source_registry() -> dict:
    """Prefer the private CI secret; fall back to the local registry for development."""
    secret_json = os.environ.get("APPROVED_SOURCES_JSON", "").strip()
    if secret_json:
        return json.loads(secret_json)
    if not APPROVED_SOURCES_FILE.exists():
        return {"sources": []}
    return json.loads(APPROVED_SOURCES_FILE.read_text(encoding="utf-8"))


def approved_source_records() -> List[dict]:
    """Load source records whose permission basis has been documented by a human."""
    try:
        registry = load_source_registry()
    except Exception as exc:
        print(f"WARNING: Cannot read approved source registry: {exc}", file=sys.stderr)
        return []

    acceptable_bases = {
        "written_permission_or_licence",
        "official_feed_or_api_agreement",
        "source_terms_expressly_allow_commercial_extraction",
        "legal_advice_confirms_basis",
    }
    approved = []
    for item in registry.get("sources", []):
        if not isinstance(item, dict):
            continue
        if item.get("status") != "approved":
            continue
        if item.get("allow_commercial_data_extraction") is not True:
            continue
        if item.get("allow_ai_document_upload") is not True:
            continue
        if item.get("permission_basis") not in acceptable_bases:
            continue
        if not str(item.get("source_id") or "").strip():
            continue
        if not str(item.get("label") or "").strip():
            continue
        if not str(item.get("evidence_reference") or "").strip():
            continue
        if not str(item.get("reviewed_by") or "").strip():
            continue
        if not str(item.get("reviewed_at") or "").strip():
            continue
        approved.append(item)
    return approved


def approved_local_source_files() -> set:
    """Return exact local filenames approved for extraction and AI upload."""
    names = set()
    for item in approved_source_records():
        for name in item.get("files", []):
            name = Path(str(name)).name
            if name and name != ".":
                names.add(name)
    return names


def source_record_for(fpath: Path, src_url: str, records: List[dict]) -> Optional[dict]:
    """Resolve the exact approved registry entry used for an input source."""
    for item in records:
        files = {Path(str(name)).name for name in item.get("files", [])}
        if fpath.name in files:
            return item
    if src_url:
        host = (urlparse(src_url).hostname or "").lower().rstrip(".")
        for item in records:
            hosts = {str(h).strip().lower().rstrip(".") for h in item.get("hosts", [])}
            if host and host in hosts and item.get("allow_remote_download") is True:
                return item
    return None


def approved_remote_source_hosts() -> set:
    """Return exact HTTPS hosts approved for downloading and AI processing."""
    hosts = set()
    for item in approved_source_records():
        if item.get("allow_remote_download") is not True:
            continue
        for host in item.get("hosts", []):
            host = str(host).strip().lower().rstrip(".")
            if host and "/" not in host and ":" not in host:
                hosts.add(host)
    return hosts


def host_is_approved(url: str, approved_hosts: set) -> bool:
    try:
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower().rstrip(".")
        return parsed.scheme == "https" and host in approved_hosts
    except Exception:
        return False


def save_remote_response(response, tmp_dir: Path, index: int, max_bytes: int = MAX_SOURCE_FILE_BYTES) -> Path:
    """Stream a permitted remote file with a hard byte ceiling and verify its file signature."""
    content_length = response.headers.get("content-length")
    if content_length:
        try:
            if int(content_length) > max_bytes:
                raise ValueError(f"source file exceeds configured {max_bytes // (1024 * 1024)} MB limit")
        except ValueError as exc:
            if "exceeds configured" in str(exc):
                raise
            # Ignore malformed Content-Length; the streaming byte counter remains authoritative.

    temporary = tmp_dir / f"url_pamphlet_{index}.part"
    total = 0
    prefix = bytearray()
    try:
        with temporary.open("wb") as target:
            for chunk in response.iter_content(chunk_size=65536):
                if not chunk:
                    continue
                total += len(chunk)
                if total > max_bytes:
                    raise ValueError(f"source file exceeds configured {max_bytes // (1024 * 1024)} MB limit")
                if len(prefix) < 32:
                    prefix.extend(chunk[:32 - len(prefix)])
                target.write(chunk)
            target.flush()
            os.fsync(target.fileno())
        head = bytes(prefix)
        if head.startswith(b"%PDF-"):
            extension = ".pdf"
        elif head.startswith(b"\x89PNG\r\n\x1a\n"):
            extension = ".png"
        elif head.startswith(b"\xff\xd8\xff"):
            extension = ".jpg"
        elif head.startswith(b"RIFF") and head[8:12] == b"WEBP":
            extension = ".webp"
        else:
            raise ValueError("download does not have a recognised PDF, PNG, JPEG or WebP file signature")
        if total == 0:
            raise ValueError("source returned an empty file")
        output = tmp_dir / f"url_pamphlet_{index}{extension}"
        temporary.replace(output)
        return output
    except Exception:
        temporary.unlink(missing_ok=True)
        raise




for _cls in (PamphletExtraction, PageCountAudit):
    if not hasattr(_cls, "model_validate_json"):
        _cls.model_validate_json = classmethod(lambda c, raw: c.parse_raw(raw))
    if not hasattr(_cls, "model_dump"):
        _cls.model_dump = lambda self: self.dict()

def _validate_json(model_cls, text: str):
    if hasattr(model_cls, "model_validate_json"):
        return model_cls.model_validate_json(text)
    return model_cls.parse_raw(text)


def _dump_model(obj) -> dict:
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    return obj.dict()


def is_personal_mode() -> bool:
    return os.environ.get("PERSONAL_MODE", "false").strip().lower() in ("1", "true", "yes")


def is_safe_public_https_url(url: str) -> bool:
    import ipaddress, urllib.parse
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname:
        return False
    host = parsed.hostname.lower().strip(".")
    if host in ("localhost", "localhost.localdomain") or host.endswith(".local") or host.endswith(".internal"):
        return False
    try:
        ip = ipaddress.ip_address(host)
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
            return False
    except ValueError:
        pass
    return True

def download_url_list(tmp_dir: Path) -> List[Tuple[Path, str]]:
    found: List[Tuple[Path, str]] = []
    if not URLS_FILE.exists():
        return found
    personal = is_personal_mode()
    enabled = personal or os.environ.get("ENABLE_APPROVED_REMOTE_DOWNLOADS", "false").strip().lower() in ("1", "true", "yes")
    ai_upload_enabled = personal or os.environ.get("ENABLE_GEMINI_DOCUMENT_UPLOADS", "false").strip().lower() in ("1", "true", "yes")
    if not enabled or not ai_upload_enabled:
        print("Remote pamphlet downloads are OFF. Both ENABLE_APPROVED_REMOTE_DOWNLOADS and ENABLE_GEMINI_DOCUMENT_UPLOADS must be enabled after source and AI-processing rights are checked.")
        return found
    approved_hosts = approved_remote_source_hosts()
    if not personal and not approved_hosts:
        print("Remote pamphlet downloads are OFF: approved_sources.json has no complete, approved source entries.")
        return found

    for idx, line in enumerate(URLS_FILE.read_text(encoding="utf-8").splitlines(), 1):
        url = line.strip()
        if not url or url.startswith("#"):
            continue
        if personal:
            if not is_safe_public_https_url(url):
                print(f"SKIPPED URL #{idx}: only public HTTPS URLs are allowed in PERSONAL_MODE.", file=sys.stderr)
                continue
        elif not host_is_approved(url, approved_hosts):
            print(f"SKIPPED URL #{idx}: HTTPS host is not approved in {APPROVED_SOURCES_FILE}.", file=sys.stderr)
            continue
        try:
            r = requests.get(url, headers=HEADERS, timeout=(10, 60), allow_redirects=False, stream=True)
            if 300 <= r.status_code < 400:
                print(f"SKIPPED URL #{idx}: redirects are disabled; add a direct approved file URL instead.", file=sys.stderr)
                continue
            r.raise_for_status()
            out = save_remote_response(r, tmp_dir, idx)
            found.append((out, url))
            print(f"Downloaded approved source URL #{idx}: {url} ({out.stat().st_size} bytes)")
        except Exception as exc:
            print(f"WARNING: Failed approved URL #{idx}: {exc}", file=sys.stderr)
        finally:
            if "r" in locals():
                try:
                    r.close()
                except Exception:
                    pass
                del r
    return found


def split_pdf_chunks(pdf_path: Path, tmp_dir: Path) -> List[Tuple[Path, int]]:
    """Return one file per source page, paired with its 1-based source page number.

    Images are single-page sources. PDFs fail closed if pypdf cannot enumerate and
    split every page; returning the original multi-page PDF would defeat page-level
    coverage accounting.
    """
    if pdf_path.suffix.lower() != ".pdf":
        out = tmp_dir / f"{pdf_path.stem}_p1-1{pdf_path.suffix.lower()}"
        out.write_bytes(pdf_path.read_bytes())
        return [(out, 1)]
    if not HAS_PYPDF:
        raise RuntimeError("pypdf is required for page-by-page coverage; install requirements.txt")
    reader = PdfReader(str(pdf_path))
    total = len(reader.pages)
    if total < 1:
        raise RuntimeError("PDF contains no readable pages")
    chunks: List[Tuple[Path, int]] = []
    for idx in range(total):
        writer = PdfWriter()
        writer.add_page(reader.pages[idx])
        out = tmp_dir / f"{pdf_path.stem}_p{idx+1}-{idx+1}.pdf"
        with out.open("wb") as fh:
            writer.write(fh)
        chunks.append((out, idx + 1))
    print(f"  Split {pdf_path.name} ({total} pages) into {len(chunks)} individually audited pages.")
    return chunks


def salvage_deals(text: str) -> List[dict]:
    out, dec = [], json.JSONDecoder()
    i = (text or "").find('"deals"')
    j = text.find("[", i) if i >= 0 else -1
    if j < 0:
        return out
    pos, n = j + 1, len(text)
    while pos < n:
        while pos < n and text[pos] in " \t\r\n,":
            pos += 1
        if pos >= n or text[pos] != "{":
            break
        try:
            obj, pos = dec.raw_decode(text, pos)
        except Exception:
            break
        if isinstance(obj, dict):
            out.append(obj)
    return out


def call_gemini_with_retry(client: genai.Client, model: str, file_path: Path, source_url: str) -> Tuple[List[dict], str, Optional[int], Optional[int]]:
    """Return (rows, status, extraction_count, second_pass_audit_count).

    A page is cacheable only when structured extraction count, extracted row
    count and a separate second-pass page count all agree. The second pass is
    another AI call, not a human/ground-truth guarantee; manual source review
    remains mandatory before publication.
    """
    status = "failed"
    for attempt in range(1, 4):
        uploaded = None
        try:
            uploaded = client.files.upload(file=str(file_path))
            resp = client.models.generate_content(
                model=model,
                contents=[uploaded, EXTRACTION_PROMPT],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=PamphletExtraction,
                    temperature=0.05,
                    max_output_tokens=65536,
                ),
            )
            extraction_count: Optional[int] = None
            parse_complete = True
            try:
                parsed = _validate_json(PamphletExtraction, resp.text)
                deal_dicts = [_dump_model(d) for d in parsed.deals]
                extraction_count = int(parsed.page_priced_offer_count)
            except Exception:
                deal_dicts = salvage_deals(resp.text)
                parse_complete = False
                print(f"    truncated/invalid JSON: salvaged {len(deal_dicts)} complete item records; extraction count unavailable")
            rows = []
            for row in deal_dicts:
                row["source_url"] = source_url
                rows.append(row)

            # A separate model call inspects the original page without seeing the
            # extracted product rows, reducing the chance of a shared omission.
            audit_resp = client.models.generate_content(
                model=os.environ.get("GEMINI_AUDIT_MODEL", model),
                contents=[uploaded, PAGE_AUDIT_PROMPT],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=PageCountAudit,
                    temperature=0.0,
                    max_output_tokens=2048,
                ),
            )
            try:
                audit = _validate_json(PageCountAudit, audit_resp.text)
                audit_count: Optional[int] = int(audit.page_priced_offer_count)
            except Exception as exc:
                print(f"    second-pass page audit could not be parsed: {exc}")
                return rows, "audit_failed", extraction_count, None

            if not parse_complete:
                return rows, "incomplete", extraction_count, audit_count
            if extraction_count != len(rows) or audit_count != len(rows) or audit_count != extraction_count:
                print(f"    PAGE COUNT MISMATCH: extraction reported {extraction_count}, second-pass audit counted {audit_count}, extracted {len(rows)} records")
                return rows, "count_mismatch", extraction_count, audit_count
            print(f"    -> {len(rows)} deals extracted; extraction and second-pass page audit agree ({audit_count})")
            return rows, "complete", extraction_count, audit_count
        except Exception as exc:
            print(f"    Attempt {attempt} failed on {file_path.name}: {exc}")
            if any(k in str(exc) for k in ("429", "RESOURCE_EXHAUSTED", "quota")):
                if "per day" in str(exc).lower() or attempt == 3:
                    return [], "quota", None, None
                time.sleep(30 * attempt)
                continue
            if attempt < 3:
                time.sleep(attempt * 6)
        finally:
            if uploaded is not None:
                try:
                    client.files.delete(name=uploaded.name)
                except Exception:
                    pass
    return [], status, None, None


def load_cache() -> Dict[str, dict]:
    """Load only versioned, complete page records; legacy list caches are invalidated."""
    if not CACHE_FILE.exists():
        return {}
    try:
        payload = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        if not isinstance(payload, dict) or payload.get("schemaVersion") != CACHE_SCHEMA_VERSION:
            print("Legacy extraction cache ignored: cache schema changed to require audited complete pages.")
            return {}
        chunks = payload.get("chunks")
        return chunks if isinstance(chunks, dict) else {}
    except Exception as exc:
        print(f"WARNING: cache could not be read and will be rebuilt: {exc}", file=sys.stderr)
        return {}


def save_cache(cache: Dict[str, dict]) -> None:
    """Atomically persist the versioned cache so interrupted writes do not corrupt it."""
    tmp = CACHE_FILE.with_suffix(CACHE_FILE.suffix + ".tmp")
    payload = {"schemaVersion": CACHE_SCHEMA_VERSION, "chunks": cache}
    tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(CACHE_FILE)


def parse_size(text: str):
    """'5kg' -> (5000,'g'); '6 x 330ml' -> (1980,'ml'); None when no size."""
    t = str(text or "").lower().replace(",", ".")
    m = re.search(r"(?:(\d+)\s*x\s*)?(\d+(?:\.\d+)?)\s*(kg|g|ml|l|litres?|liters?)\b", t)
    if not m:
        return None
    mult, n, u = int(m.group(1) or 1), float(m.group(2)), m.group(3)
    if u == "kg": return (n * 1000 * mult, "g")
    if u == "g": return (n * mult, "g")
    if u == "ml": return (n * mult, "ml")
    return (n * 1000 * mult, "ml")


def merge_deals(all_raw: List[dict]) -> dict:
    grouped = {}
    skipped_expired = 0
    skipped_invalid_price = 0
    skipped_missing_name = 0
    skipped_invalid_expiry = 0
    duplicate_rows = 0
    represented_rows = 0
    for d in all_raw:
        try:
            normal_price = float(d.get("normal_price") or 0)
            reward_price = float(d.get("reward_price") or 0)
        except (TypeError, ValueError):
            skipped_invalid_price += 1
            continue
        if normal_price <= 0:
            normal_price = reward_price
        if normal_price <= 0:
            skipped_invalid_price += 1
            continue
        d = dict(d)
        d["normal_price"] = normal_price
        d["reward_price"] = reward_price or normal_price
        if d.get("valid_until_at"):
            try:
                raw_expiry = str(d["valid_until_at"]).strip().replace("Z", "+00:00")
                parsed_expiry = datetime.fromisoformat(raw_expiry)
                if parsed_expiry.tzinfo is None:
                    from zoneinfo import ZoneInfo
                    parsed_expiry = parsed_expiry.replace(tzinfo=ZoneInfo("Africa/Johannesburg"))
                if d.get("valid_until") and parsed_expiry.date().isoformat() != str(d["valid_until"])[:10]:
                    raise ValueError("valid_until_at date does not match valid_until")
            except Exception:
                skipped_invalid_expiry += 1
                continue
        if is_expired(d.get("valid_until"), d.get("valid_until_at")):
            skipped_expired += 1
            continue

        name = str(d.get("canonical_name") or "").strip()
        if not name:
            skipped_missing_name += 1
            continue
        pid = normalize_slug(name)

        if pid not in grouped:
            grouped[pid] = {
                "id": pid,
                "name": name,
                "brand": d.get("brand") or "",
                "packSize": d.get("pack_size") or "",
                "category": d.get("category") or "Other Specials",
                "emoji": d.get("emoji") or "🏷️",
                "pamphletTitle": d.get("pamphlet_title") or "Weekly Pamphlet",
                "dealType": d.get("deal_type") or "Weekly Special",
                "multiBuy": d.get("multi_buy_note") or "",
                "unitPrice": d.get("unit_price_note") or "",
                "provinces": d.get("provinces") or ["All"],
                "validFrom": d.get("valid_from") or "",
                "validUntil": d.get("valid_until") or "",
                "validFromAt": d.get("valid_from_at") or "",
                "validUntilAt": d.get("valid_until_at") or "",
                "sourceUrl": d.get("source_url") or "",
                "stores": {},
            }

        entry = grouped[pid]
        if d.get("valid_until") and (not entry["validUntil"] or d["valid_until"] > entry["validUntil"]):
            entry["validUntil"] = d["valid_until"]
        if d.get("valid_until_at") and (not entry.get("validUntilAt") or d["valid_until_at"] > entry["validUntilAt"]):
            entry["validUntilAt"] = d["valid_until_at"]
        if d.get("source_url") and not entry["sourceUrl"]:
            entry["sourceUrl"] = d["source_url"]
        if d.get("multi_buy_note") and not entry["multiBuy"]:
            entry["multiBuy"] = d["multi_buy_note"]
        if "All" not in entry["provinces"]:
            if "All" in (d.get("provinces") or []):
                entry["provinces"] = ["All"]
            else:
                entry["provinces"] = sorted(set(entry["provinces"]) | set(d.get("provinces") or []))

        store_key = str(d.get("store") or "Store").strip()
        norm_p = round(float(d["normal_price"]), 2)
        rew_p = round(float(d.get("reward_price") or norm_p), 2)
        if rew_p <= 0:
            rew_p = norm_p

        new_offer = {
            "store": store_key,
            "price": norm_p,
            "rewardPrice": rew_p,
            "card": d.get("card"),
            "validFrom": d.get("valid_from") or "",
            "validUntil": d.get("valid_until") or "",
            "validFromAt": d.get("valid_from_at") or "",
            "validUntilAt": d.get("valid_until_at") or "",
            "pamphletTitle": d.get("pamphlet_title") or "",
            "multiBuy": d.get("multi_buy_note") or "",
            "sourceUrl": d.get("source_url") or "",
            "sourceFile": d.get("source_file") or "",
            "sourcePage": d.get("source_page"),
            "sourceId": d.get("source_id") or "",
            "sourceLabel": d.get("source_label") or "",
            "sourceEvidenceReference": d.get("source_evidence_reference") or "",
            "provinces": d.get("provinces") or ["All"],
        }
        existing = entry["stores"].get(store_key)
        if not existing:
            represented_rows += 1
            entry["stores"][store_key] = new_offer
        else:
            # Keep every distinct offer for this product/store, including equal-price
            # offers from separate pamphlets, regions, dates or loyalty conditions.
            # Only byte-for-byte-equivalent commercial terms are collapsed.
            def offer_identity(offer):
                return (
                    offer.get("price"), offer.get("rewardPrice"), offer.get("card"),
                    offer.get("validFrom"), offer.get("validUntil"),
                    offer.get("validFromAt"), offer.get("validUntilAt"),
                    offer.get("pamphletTitle"), offer.get("multiBuy"),
                    offer.get("sourceUrl"), offer.get("sourceFile"), offer.get("sourcePage"),
                    offer.get("sourceId"), offer.get("sourceEvidenceReference"),
                    tuple(sorted(offer.get("provinces") or ["All"])),
                )

            more = entry.setdefault("_more", {}).setdefault(store_key, [])
            known = [existing] + more
            if not any(offer_identity(x) == offer_identity(new_offer) for x in known):
                represented_rows += 1
                if rew_p < existing["rewardPrice"]:
                    more.append(existing)
                    entry["stores"][store_key] = new_offer
                else:
                    more.append(new_offer)
            else:
                duplicate_rows += 1


    prev_prices = load_previous_best_prices()
    carried = load_carried_prev()
    products = []
    for item in grouped.values():
        more = item.pop("_more", {})
        item["stores"] = sorted(item["stores"].values(), key=lambda s: s["rewardPrice"])
        for st in item["stores"]:
            if more.get(st["store"]):
                st["moreOffers"] = more[st["store"]]
        sz = parse_size(item.get("packSize") or item["name"])
        if sz:
            item["sizeAmount"], item["sizeUnit"] = sz
        if item["stores"]:
            new_best = item["stores"][0]["rewardPrice"]
            old_best = prev_prices.get(item["id"])
            if old_best and old_best > new_best + 0.5:
                item["prevBestPrice"] = round(old_best, 2)
            elif item["id"] in carried and abs(old_best - new_best) <= 0.01:
                item["prevBestPrice"] = carried[item["id"]]  # same price as last run: keep the "was" price so the drop badge survives reruns
        products.append(item)

    products.sort(key=lambda p: (p["category"], p["name"]))
    merge_audit = {
        "rawOfferCount": len(all_raw),
        "representedOfferCount": represented_rows,
        "exactDuplicateRows": duplicate_rows,
        "expiredOffersSkipped": skipped_expired,
        "invalidPriceRows": skipped_invalid_price,
        "missingNameRows": skipped_missing_name,
        "invalidExpiryRows": skipped_invalid_expiry,
        "complete": skipped_invalid_price == 0 and skipped_missing_name == 0 and skipped_invalid_expiry == 0 and represented_rows + duplicate_rows + skipped_expired == len(all_raw),
    }
    print(f"UNLIMITED MERGE COMPLETE: {len(products)} active products ({represented_rows} represented offers, {duplicate_rows} exact duplicate rows, {skipped_expired} expired removed, {skipped_invalid_price + skipped_missing_name + skipped_invalid_expiry} invalid rows).")
    return {
        "updatedAt": datetime.now(timezone.utc).isoformat(),
        "sourceNote": f"AI-assisted candidate feed: {len(products)} active products ({skipped_expired} expired offers removed)",
        "products": products,
        "mergeAudit": merge_audit,
    }


def main() -> int:
    available_local_files = [
        p for p in sorted(PAMPHLET_DIR.iterdir())
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTS
    ] if PAMPHLET_DIR.exists() else []
    personal = is_personal_mode()
    ai_upload_enabled = personal or os.environ.get("ENABLE_GEMINI_DOCUMENT_UPLOADS", "false").strip().lower() in ("1", "true", "yes")
    approved_records = approved_source_records()
    approved_names = approved_local_source_files()
    local_files: List[Tuple[Path, str, Optional[dict]]] = []
    skipped_local = []
    for p in available_local_files:
        if personal:
            rec = source_record_for(p, "", approved_records) or {
                "source_id": f"personal_local:{p.stem}",
                "label": f"Personal pamphlet ({p.name})",
                "status": "personal_use",
                "permission_basis": "personal_private_use",
            }
            local_files.append((p, "", rec))
        elif p.name not in approved_names:
            skipped_local.append(p.name)
            print(f"SKIPPED local file {p.name}: no approved source record with AI-processing permission in {APPROVED_SOURCES_FILE}.")
        elif ai_upload_enabled:
            local_files.append((p, "", source_record_for(p, "", approved_records)))

    def write_coverage(report: dict) -> None:
        tmp = COVERAGE_FILE.with_suffix(COVERAGE_FILE.suffix + ".tmp")
        tmp.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        tmp.replace(COVERAGE_FILE)

    base_report = {
        "schemaVersion": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": "blocked_configuration",
        "sourceFilesDiscovered": len(available_local_files),
        "sourceFilesApproved": len(approved_names),
        "sourceFilesReadyToProcess": len(local_files),
        "sourceFilesSkipped": skipped_local,
        "pagesTotal": 0,
        "pagesComplete": 0,
        "pagesIncomplete": 0,
        "expectedOfferCount": 0,
        "extractedOfferCount": 0,
        "offerCountAuditComplete": False,
        "complete": False,
        "pages": [],
    }

    if not ai_upload_enabled:
        base_report["status"] = "blocked_ai_upload_disabled"
        base_report["message"] = "Extraction did not run. Enable document upload only after confirming the approved source permits processing by the configured AI provider."
        write_coverage(base_report)
        print(base_report["message"])
        return 0

    with tempfile.TemporaryDirectory() as tmp_str:
        tmp_dir = Path(tmp_str)
        url_files = download_url_list(tmp_dir)
        print("Automatic catalogue crawling is disabled. Only exact approved source files and direct approved file URLs are eligible.")
        remote_inputs = [(path, url, source_record_for(path, url, approved_records)) for path, url in url_files]
        all_inputs = local_files + remote_inputs
        base_report["sourceFilesApproved"] = len(all_inputs)
        if not all_inputs:
            base_report["status"] = "blocked_no_approved_sources"
            base_report["message"] = "No approved local or remote sources were available. No price feed was changed."
            write_coverage(base_report)
            print(base_report["message"])
            return 0

        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            base_report["status"] = "failed_missing_api_key"
            base_report["message"] = "GEMINI_API_KEY is not configured."
            write_coverage(base_report)
            print(base_report["message"], file=sys.stderr)
            return 1

        model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
        client = genai.Client(api_key=api_key)
        cache = load_cache()
        all_raw: List[dict] = []
        used, page_records, failed_pages = set(), [], []
        quota_hit = False
        started = time.time()
        budget = float(os.environ.get("MAX_RUNTIME_MIN", "45")) * 60
        pace = float(os.environ.get("GEMINI_MIN_INTERVAL", "4"))

        def stamp(rows, fpath, source_page, src_url, source_record):
            m = re.match(r"(.+?)_(\d{4}-\d{2}-\d{2})_(\d{4}-\d{2}-\d{2})", fpath.stem)
            stamped = []
            for original in rows:
                r = dict(original)
                if m:
                    r["store"] = r.get("store") or m.group(1).replace("-", " ").title()
                    r["valid_from"] = r.get("valid_from") or m.group(2)
                    r["valid_until"] = r.get("valid_until") or m.group(3)
                r["source_url"] = src_url or r.get("source_url") or ""
                r["source_file"] = fpath.name
                r["source_page"] = source_page
                if source_record:
                    r["source_id"] = source_record.get("source_id") or ""
                    r["source_label"] = source_record.get("label") or ""
                    r["source_evidence_reference"] = source_record.get("evidence_reference") or ""
                stamped.append(r)
            return stamped

        def run_page(page_path, source_page, src_url, fpath, source_record):
            nonlocal quota_hit
            content_hash = sha256_file(page_path)
            # Invalidate cached extraction whenever the prompt, schema or either model changes.
            audit_model = os.environ.get("GEMINI_AUDIT_MODEL", model)
            key = hashlib.sha256(f"{content_hash}|page-audit-v4-independent|{model}|{audit_model}".encode("utf-8")).hexdigest()
            used.add(key)
            cached = cache.get(key)
            if isinstance(cached, dict) and cached.get("status") == "complete":
                cached_rows = cached.get("rows")
                expected = cached.get("expectedOfferCount")
                audited = cached.get("secondPassAuditCount")
                extracted = cached.get("extractionReportedOfferCount")
                if isinstance(cached_rows, list) and isinstance(expected, int) and expected == len(cached_rows) and audited == expected and extracted == expected:
                    rows = stamp(cached_rows, fpath, source_page, src_url, source_record)
                    return rows, {
                        "sourceFile": fpath.name, "sourcePage": source_page,
                        "sha256": key, "status": "complete", "expectedOfferCount": expected,
                        "extractedOfferCount": len(rows), "extractionReportedOfferCount": expected,
                        "secondPassAuditCount": expected, "fromCache": True,
                    }

            if quota_hit or time.time() - started > budget:
                status, rows = ("quota" if quota_hit else "time_budget"), []
                extraction_count, audit_count, expected = None, None, None
            else:
                time.sleep(pace)
                rows, status, extraction_count, audit_count = call_gemini_with_retry(client, model, page_path, src_url)
                expected = audit_count if isinstance(audit_count, int) else extraction_count
            rows = stamp(rows, fpath, source_page, src_url, source_record)
            complete = status == "complete" and isinstance(expected, int) and expected == len(rows) and extraction_count == expected and audit_count == expected
            record = {
                "sourceFile": fpath.name, "sourcePage": source_page,
                "sha256": key, "status": "complete" if complete else status,
                "expectedOfferCount": expected, "extractedOfferCount": len(rows),
                "extractionReportedOfferCount": extraction_count,
                "secondPassAuditCount": audit_count,
                "fromCache": False,
            }
            if complete:
                # Cache only fully parsed pages with an explicit matching count, including audited zero-offer pages.
                cache[key] = {
                    "schemaVersion": CACHE_SCHEMA_VERSION,
                    "status": "complete",
                    "expectedOfferCount": expected,
                    "extractionReportedOfferCount": extraction_count,
                    "secondPassAuditCount": audit_count,
                    "rows": rows,
                }
                save_cache(cache)
            else:
                failed_pages.append(record)
                if status == "quota":
                    quota_hit = True
            return rows, record

        for fpath, src_url, source_record in all_inputs:
            print(f"Enumerating every page in {fpath.name}...")
            try:
                page_files = split_pdf_chunks(fpath, tmp_dir)
            except Exception as exc:
                record = {"sourceFile": fpath.name, "sourcePage": None, "status": "page_enumeration_failed", "error": str(exc), "expectedOfferCount": None, "extractedOfferCount": 0, "fromCache": False}
                page_records.append(record)
                failed_pages.append(record)
                print(f"ERROR: Could not enumerate all pages for {fpath.name}: {exc}", file=sys.stderr)
                continue
            for page_path, source_page in page_files:
                rows, record = run_page(page_path, source_page, src_url, fpath, source_record)
                all_raw.extend(rows)
                page_records.append(record)
                print(f"  Page {source_page}: {record['status']} ({record.get('extractedOfferCount', 0)} extracted / {record.get('expectedOfferCount')} expected)")

        # Prune old cache only after every known page in this run completed successfully.
        if not failed_pages:
            for key in list(cache):
                if key not in used:
                    del cache[key]
            save_cache(cache)

        complete_pages = [r for r in page_records if r.get("status") == "complete"]
        expected_known = all(
            isinstance(r.get("expectedOfferCount"), int)
            and r.get("extractionReportedOfferCount") == r.get("expectedOfferCount")
            and r.get("secondPassAuditCount") == r.get("expectedOfferCount")
            for r in page_records
        )
        expected_total = sum(r.get("expectedOfferCount") or 0 for r in page_records if isinstance(r.get("expectedOfferCount"), int))
        extracted_total = sum(int(r.get("extractedOfferCount") or 0) for r in page_records)
        run_complete = bool(page_records) and len(complete_pages) == len(page_records) and expected_known and expected_total == extracted_total
        coverage_run = {
            "pagesTotal": len(page_records),
            "pagesComplete": len(complete_pages),
            "pagesIncomplete": len(page_records) - len(complete_pages),
            "unreadChunks": len(failed_pages),
            "quotaExhausted": quota_hit,
            "expectedOfferCount": expected_total if expected_known else None,
            "extractedOfferCount": extracted_total,
            "offerCountAuditComplete": expected_known and all(r.get("status") == "complete" for r in page_records),
            "auditMethod": "Separate second-pass AI visual count compared with extraction-reported count and extracted record count; human review still required",
            "complete": run_complete,
        }
        report = {
            **base_report,
            "status": "complete" if run_complete else "incomplete",
            "sourceFilesApproved": len(all_inputs),
            **coverage_run,
            "pages": page_records,
            "message": "Every enumerated page has a matching explicit offer count." if run_complete else "One or more pages failed, were truncated, had count mismatches, or could not be enumerated. Do not publish this run.",
        }
        write_coverage(report)
        print(f"COVERAGE: {coverage_run['pagesComplete']}/{coverage_run['pagesTotal']} pages complete; {coverage_run['extractedOfferCount']}/{coverage_run['expectedOfferCount']} audited offers extracted.")

        if not all_raw:
            print("No offer rows extracted. No candidate feed was written and the live deals.json was not changed.")
            return 0 if run_complete else 2

        payload = merge_deals(all_raw)
        payload["approvalStatus"] = "pending_review"
        payload["verifiedAt"] = ""
        payload["coverage_run"] = {
            **coverage_run,
            "mergeAuditComplete": bool(payload.get("mergeAudit", {}).get("complete")),
            "mergeAudit": payload.get("mergeAudit", {}),
        }
        payload["coverage_report"] = "coverage_report.json"
        CANDIDATE_FILE.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Wrote {CANDIDATE_FILE} with {len(payload['products'])} candidate products. Public deals.json was NOT changed.")
        if not run_complete:
            print("WARNING: Candidate feed is PARTIAL and the publication script must refuse it. Finish/retry all incomplete pages first.", file=sys.stderr)
            return 2
        print("Every page passed the explicit count audit. A human must still compare every offer with its authorised source before publishing.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
