#!/usr/bin/env python3
"""
Mzansi Smart Basket v5 — Pro Multi-Pamphlet SA OCR & Price Engine
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
from typing import Dict, List, Literal, Optional

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
CACHE_FILE = Path(".pamphlet_cache.json")
OUTPUT_FILE = Path("deals.json")
SUPPORTED_EXTS = {".pdf", ".png", ".jpg", ".jpeg", ".webp"}
CHUNK_PAGES = 4

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
        description="Standardized SA product name with pack size/model first, e.g. '10kg White Super Maize Meal', '1kg Smoked Russians', '5L Digital Air Fryer'."
    )
    brand: Optional[str] = Field(default=None, description="Brand name if shown, e.g. Ace, White Star, Eskort, Sunlight, Hisense")
    pack_size: Optional[str] = Field(default=None, description="Size/weight/count, e.g. '10kg', '2L', '6 x 1L', '2-Pack'")
    category: DEPARTMENTS
    emoji: str = Field(description="Single matching emoji")
    store: str = Field(description="Store name: Shoprite, Boxer, Pick n Pay, Checkers, SPAR, PEP, Ackermans, Game, Makro, etc.")
    normal_price: float = Field(description="Regular non-card price in ZAR")
    reward_price: float = Field(description="Loyalty card price in ZAR if shown, else equal to normal_price")
    card: Optional[Literal["xtra", "smart", "boxer", "spar"]] = Field(default=None)
    multi_buy_note: Optional[str] = Field(default=None, description="Promo condition if any, e.g. '2 for R45', 'Combo Deal', 'Limit 4 per customer'")
    unit_price_note: Optional[str] = Field(default=None, description="Helpful unit math if clear, e.g. 'R10.50/kg' or 'R15.00 each'")
    pamphlet_title: str = Field(description="Pamphlet/campaign name, e.g. 'Shoprite 3-Day Payday Deals'")
    deal_type: DEAL_TYPES = Field(default="Weekly Special")
    provinces: List[str] = Field(
        default_factory=lambda: ["All"],
        description="SA provinces listed on the pamphlet (e.g. ['Mpumalanga', 'Gauteng']), or ['All'] if national."
    )
    valid_from: Optional[str] = Field(default=None, description="Start date YYYY-MM-DD if printed")
    valid_until: Optional[str] = Field(default=None, description="End date YYYY-MM-DD if printed")


class PamphletExtraction(BaseModel):
    store_detected: str
    pamphlet_title: str
    deals: List[ExtractedDeal]


EXTRACTION_PROMPT = """
You are an exhaustive South African retail pamphlet data extractor.
Extract EVERY SINGLE priced item on EVERY page of this document — do NOT summarize or stop early.

Cover ALL 12 departments:
- Staples & Grain (maize meal, rice, oil, flour, sugar, samp, oats)
- Meat, Poultry & Deli (chicken, beef, pork, boerewors, Russians, viennas, polony, fresh/frozen pies)
- Dairy & Eggs, Bakery & Bread, Fruit & Veg, Pantry & Tins, Snacks & Drinks
- Household & Cleaning, Personal Care & Baby
- Gadgets & Appliances (air fryers, microwaves, kettles, irons, stoves, smartphones, powerbanks, TVs, speakers, fans)
- Clothing & Footwear, Other Specials

Strict Rules:
1. Standardize canonical_name with pack size/capacity first (e.g. '10kg White Super Maize Meal', '2L Sunflower Cooking Oil', '1kg Smoked Russians') so identical items across Shoprite, Boxer, Pick n Pay, Checkers, SPAR, PEP, and Game group onto the same card.
2. For multi-buy deals ('2 for R45', '3 for R100'), put the bundle price as normal_price/reward_price, include '(2-Pack)' in canonical_name, and record '2 for R45' in multi_buy_note.
3. Map loyalty cards strictly: Shoprite/Checkers -> "xtra", Pick n Pay -> "smart", Boxer -> "boxer", SPAR -> "spar", others -> null.
4. Capture regional validity in provinces if printed (e.g. Inland -> ["Gauteng", "Mpumalanga", "Limpopo", "North West", "Free State"]); otherwise ["All"].
5. Extract valid_from and valid_until in YYYY-MM-DD if printed. Never guess unreadable prices.
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


def is_expired(valid_until: Optional[str]) -> bool:
    if not valid_until:
        return False
    try:
        end_d = date.fromisoformat(valid_until[:10])
        return end_d < date.today()
    except Exception:
        return False


def split_pdf_chunks(pdf_path: Path, tmp_dir: Path) -> List[Path]:
    if not HAS_PYPDF or pdf_path.suffix.lower() != ".pdf":
        return [pdf_path]
    try:
        reader = PdfReader(str(pdf_path))
        total = len(reader.pages)
        if total <= CHUNK_PAGES:
            return [pdf_path]
        chunks = []
        for start in range(0, total, CHUNK_PAGES):
            writer = PdfWriter()
            end = min(total, start + CHUNK_PAGES)
            for idx in range(start, end):
                writer.add_page(reader.pages[idx])
            out = tmp_dir / f"{pdf_path.stem}_p{start+1}-{end}.pdf"
            with out.open("wb") as f:
                writer.write(f)
            chunks.append(out)
        print(f"  Split {pdf_path.name} ({total} pages) into {len(chunks)} chunks for 100% coverage.")
        return chunks
    except Exception as exc:
        print(f"  PDF split fallback for {pdf_path.name}: {exc}")
        return [pdf_path]


def call_gemini_with_retry(client: genai.Client, model: str, file_path: Path) -> List[dict]:
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
                    temperature=0.1,
                    max_output_tokens=65536,
                ),
            )
            parsed = PamphletExtraction.model_validate_json(resp.text)
            print(f"    -> {len(parsed.deals)} deals ({parsed.store_detected} — {parsed.pamphlet_title})")
            return [d.model_dump() for d in parsed.deals]
        except Exception as exc:
            wait = attempt * 6
            print(f"    Attempt {attempt} failed on {file_path.name}: {exc}")
            if attempt < 3:
                time.sleep(wait)
        finally:
            if uploaded is not None:
                try:
                    client.files.delete(name=uploaded.name)
                except Exception:
                    pass
    return []


def download_url_pamphlets(tmp_dir: Path) -> List[Path]:
    downloaded = []
    if not URLS_FILE.exists():
        return downloaded
    for idx, line in enumerate(URLS_FILE.read_text(encoding="utf-8").splitlines(), 1):
        url = line.strip()
        if not url or url.startswith("#"):
            continue
        try:
            r = requests.get(url, timeout=25)
            r.raise_for_status()
            ctype = r.headers.get("content-type", "").lower()
            ext = ".pdf" if "pdf" in ctype or url.lower().endswith(".pdf") else ".jpg"
            out = tmp_dir / f"remote_pamphlet_{idx}{ext}"
            out.write_bytes(r.content)
            downloaded.append(out)
            print(f"Downloaded remote pamphlet #{idx} from {url}")
        except Exception as exc:
            print(f"WARNING: Could not download {url}: {exc}", file=sys.stderr)
    return downloaded


def load_cache() -> Dict[str, List[dict]]:
    if CACHE_FILE.exists():
        try:
            return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_cache(cache: Dict[str, List[dict]]) -> None:
    try:
        CACHE_FILE.write_text(json.dumps(cache, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass


def merge_deals(all_raw: List[dict]) -> dict:
    grouped = {}
    skipped_expired = 0
    for d in all_raw:
        if float(d.get("normal_price") or 0) <= 0:
            continue
        if is_expired(d.get("valid_until")):
            skipped_expired += 1
            continue

        name = str(d.get("canonical_name") or "").strip()
        if not name:
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
                "stores": {},
            }

        entry = grouped[pid]
        if d.get("valid_until") and not entry["validUntil"]:
            entry["validUntil"] = d["valid_until"]
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

        existing = entry["stores"].get(store_key)
        if not existing or rew_p < existing["rewardPrice"]:
            entry["stores"][store_key] = {
                "store": store_key,
                "price": norm_p,
                "rewardPrice": rew_p,
                "card": d.get("card"),
            }

    products = []
    for item in grouped.values():
        item["stores"] = sorted(item["stores"].values(), key=lambda s: s["rewardPrice"])
        products.append(item)

    products.sort(key=lambda p: (p["category"], p["name"]))
    print(f"Summary: {len(products)} unique products merged ({skipped_expired} expired offers skipped).")
    return {
        "updatedAt": datetime.now(timezone.utc).isoformat(),
        "sourceNote": f"Live AI v5: {len(products)} active specials across all departments ({skipped_expired} expired removed)",
        "products": products,
    }


def push_to_supabase(payload: dict) -> None:
    sb_url = os.environ.get("SUPABASE_URL", "").rstrip("/")
    sb_key = os.environ.get("SUPABASE_SERVICE_KEY", "")
    if not sb_url or not sb_key:
        return
    resp = requests.post(
        f"{sb_url}/rest/v1/deals_feed",
        headers={
            "apikey": sb_key,
            "Authorization": f"Bearer {sb_key}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates",
        },
        json={"id": "latest", "updated_at": payload["updatedAt"], "payload": payload},
        timeout=20,
    )
    resp.raise_for_status()
    print("Synced latest feed to Supabase.")


def main() -> int:
    local_files = sorted(
        p for p in PAMPHLET_DIR.iterdir()
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTS
    ) if PAMPHLET_DIR.exists() else []

    with tempfile.TemporaryDirectory() as tmp_str:
        tmp_dir = Path(tmp_str)
        all_files = local_files + download_url_pamphlets(tmp_dir)

        if not all_files:
            print("No pamphlet PDFs/images found. Keeping existing deals.json.")
            return 0

        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            print("ERROR: GEMINI_API_KEY secret is not set.", file=sys.stderr)
            return 1

        model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
        client = genai.Client(api_key=api_key)
        cache = load_cache()
        all_raw: List[dict] = []

        for fpath in all_files:
            fhash = sha256_file(fpath)
            if fhash in cache:
                print(f"Cached ({len(cache[fhash])} deals): {fpath.name}")
                all_raw.extend(cache[fhash])
                continue

            print(f"Processing new pamphlet: {fpath.name}")
            file_deals: List[dict] = []
            for chunk_path in split_pdf_chunks(fpath, tmp_dir):
                file_deals.extend(call_gemini_with_retry(client, model, chunk_path))
            if file_deals:
                cache[fhash] = file_deals
                all_raw.extend(file_deals)

        save_cache(cache)
        if not all_raw:
            print("No deals extracted; keeping existing deals.json.")
            return 0

        payload = merge_deals(all_raw)
        OUTPUT_FILE.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Wrote {OUTPUT_FILE} successfully.")
        try:
            push_to_supabase(payload)
        except Exception as exc:
            print(f"WARNING: Supabase sync skipped: {exc}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
