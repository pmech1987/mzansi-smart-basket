#!/usr/bin/env python3
"""
Mzansi Smart Basket v6 — Unlimited Exhaustive SA Pamphlet Crawler & OCR Engine
------------------------------------------------------------------------------
- Zero item caps: chunks PDFs into 2-page batches with max_output_tokens=65536
  so EVERY item on EVERY page of every active pamphlet is extracted.
- Auto-discovers public pamphlet PDF/image links from configured SA retail
  catalogue pages (gracefully skips any site that blocks bots) AND processes
  every file in `pamphlets/` and every direct link in `pamphlet_urls.txt`.
- Strict date validation: preserves valid_from, valid_until, and source_url
  on every item, and automatically drops expired deals.
- SHA-256 caching (.pamphlet_cache.json) skips unchanged files to stay fast
  and preserve your free Gemini API quota.
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
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
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
CHUNK_PAGES = 2  # Small 2-page chunks ensure ZERO skipped items on dense 24-page flyers

# Public SA catalogue discovery pages (gracefully skips any page returning 403/anti-bot)
AUTO_DISCOVERY_SOURCES = [
    ("Shoprite", "https://www.guzzle.co.za/shoprite"),
    ("Boxer", "https://www.latestspecials.co.za/boxer/"),
    ("Pick n Pay", "https://www.guzzle.co.za/pick-n-pay"),
    ("Checkers", "https://www.guzzle.co.za/checkers"),
    ("SPAR", "https://www.guzzle.co.za/spar"),
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Mobile Safari/537.36",
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


class PamphletExtraction(BaseModel):
    store_detected: str
    pamphlet_title: str
    deals: List[ExtractedDeal]


EXTRACTION_PROMPT = """
You are an exhaustive South African retail pamphlet extraction engine.
CRITICAL REQUIREMENT: Extract EVERY SINGLE PRICED ITEM visible on these pages.
Do NOT summarize, do NOT sample, do NOT skip small corner deals, braai packs, chicken portions, Russians, pies, gadgets, appliances, clothing, or combos.
If a page has 40 items, return ALL 40 items.

Rules:
1. Standardize canonical_name with size/pack first so identical items across Shoprite, Boxer, Pick n Pay, Checkers, SPAR, PEP, and Game match onto the same comparison card.
2. Separate normal_price and reward_price. Map loyalty cards: Shoprite/Checkers -> "xtra", Pick n Pay -> "smart", Boxer -> "boxer", SPAR -> "spar", others -> null.
3. Capture exact valid_from and valid_until in YYYY-MM-DD whenever printed anywhere on the page/header.
4. Capture regional validity in provinces (e.g. Inland -> ["Gauteng","Mpumalanga","Limpopo","North West","Free State"]); otherwise ["All"].
5. Never invent a price — only extract prices visibly printed on the flyer.
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
        return date.fromisoformat(valid_until[:10]) < date.today()
    except Exception:
        return False



def discover_with_playwright(store_name: str, page_url: str, tmp_dir: Path, seen_urls: set) -> List[Tuple[Path, str]]:
    """Headless Chromium fallback for JS-rendered SA catalogue portals."""
    found: List[Tuple[Path, str]] = []
    try:
        from playwright.sync_api import sync_playwright
    except Exception:
        return found
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(user_agent=HEADERS["User-Agent"])
            page.goto(page_url, wait_until="networkidle", timeout=25000)
            links = page.eval_on_selector_all("a[href]", "els => els.map(e => e.href)")
            imgs = page.eval_on_selector_all("img", "els => els.map(e => e.currentSrc || e.src || e.getAttribute('data-src') || '')")
            browser.close()

        # 1) Direct PDF links
        pdf_links = [u for u in links if u and u.lower().endswith(".pdf") and u not in seen_urls]
        for idx, pdf_url in enumerate(pdf_links[:12], 1):
            seen_urls.add(pdf_url)
            try:
                pr = requests.get(pdf_url, headers=HEADERS, timeout=25)
                if pr.status_code == 200 and len(pr.content) > 5000:
                    out = tmp_dir / f"pw_{normalize_slug(store_name)}_{idx}.pdf"
                    out.write_bytes(pr.content)
                    found.append((out, pdf_url))
                    print(f"Playwright downloaded {store_name} PDF: {pdf_url}")
            except Exception:
                continue

        # 2) High-res flyer page images (many SA portals serve leaflets as JPG/WebP pages > 35KB)
        img_candidates = [
            u for u in imgs
            if u and u.startswith("http") and u not in seen_urls
            and any(ext_s in u.lower() for ext_s in (".jpg", ".jpeg", ".webp", ".png"))
            and not any(skip in u.lower() for skip in ("logo", "icon", "avatar", "sprite", "banner-ad"))
        ]
        for idx, img_url in enumerate(img_candidates[:20], 1):
            seen_urls.add(img_url)
            try:
                ir = requests.get(img_url, headers=HEADERS, timeout=20)
                if ir.status_code == 200 and len(ir.content) > 35000:
                    ext_guess = ".webp" if ".webp" in img_url.lower() else ".png" if ".png" in img_url.lower() else ".jpg"
                    out = tmp_dir / f"pw_img_{normalize_slug(store_name)}_{idx}{ext_guess}"
                    out.write_bytes(ir.content)
                    found.append((out, page_url))
                    print(f"Playwright downloaded {store_name} flyer image ({len(ir.content)//1024}KB): {img_url}")
            except Exception:
                continue
    except Exception as exc:
        print(f"Playwright fallback skipped {store_name}: {exc}")
    return found


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

def discover_public_pamphlets(tmp_dir: Path) -> List[Tuple[Path, str]]:
    """Attempts to discover direct PDF or high-res flyer images from public SA catalogue pages."""
    found: List[Tuple[Path, str]] = []
    seen_urls = set()
    for store_name, page_url in AUTO_DISCOVERY_SOURCES:
        try:
            r = requests.get(page_url, headers=HEADERS, timeout=20)
            if r.status_code != 200:
                print(f"Auto-discovery skipped {store_name} ({page_url}): HTTP {r.status_code}")
                continue
            soup = BeautifulSoup(r.text, "html.parser")
            pdf_links = []
            for a in soup.find_all("a", href=True):
                href = urljoin(page_url, a["href"])
                if href.lower().endswith(".pdf") and href not in seen_urls:
                    pdf_links.append(href)
                    seen_urls.add(href)
            for idx, pdf_url in enumerate(pdf_links[:12], 1):
                try:
                    pr = requests.get(pdf_url, headers=HEADERS, timeout=25)
                    if pr.status_code == 200 and len(pr.content) > 5000:
                        out = tmp_dir / f"auto_{normalize_slug(store_name)}_{idx}.pdf"
                        out.write_bytes(pr.content)
                        found.append((out, pdf_url))
                        print(f"Auto-downloaded {store_name} PDF: {pdf_url}")
                except Exception:
                    continue
            if not pdf_links:
                found.extend(discover_with_playwright(store_name, page_url, tmp_dir, seen_urls))
        except Exception as exc:
            print(f"Auto-discovery skipped {store_name}: {exc}")
            found.extend(discover_with_playwright(store_name, page_url, tmp_dir, seen_urls))
    return found


def download_url_list(tmp_dir: Path) -> List[Tuple[Path, str]]:
    found: List[Tuple[Path, str]] = []
    if not URLS_FILE.exists():
        return found
    for idx, line in enumerate(URLS_FILE.read_text(encoding="utf-8").splitlines(), 1):
        url = line.strip()
        if not url or url.startswith("#"):
            continue
        try:
            r = requests.get(url, headers=HEADERS, timeout=25)
            r.raise_for_status()
            ctype = r.headers.get("content-type", "").lower()
            ext = ".pdf" if "pdf" in ctype or url.lower().endswith(".pdf") else ".jpg"
            out = tmp_dir / f"url_pamphlet_{idx}{ext}"
            out.write_bytes(r.content)
            found.append((out, url))
            print(f"Downloaded pamphlet URL #{idx}: {url}")
        except Exception as exc:
            print(f"WARNING: Failed URL {url}: {exc}", file=sys.stderr)
    return found


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
        print(f"  Split {pdf_path.name} ({total} pages) into {len(chunks)} exhaustive 2-page chunks.")
        return chunks
    except Exception as exc:
        print(f"  PDF split fallback on {pdf_path.name}: {exc}")
        return [pdf_path]


def call_gemini_with_retry(client: genai.Client, model: str, file_path: Path, source_url: str) -> List[dict]:
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
            parsed = PamphletExtraction.model_validate_json(resp.text)
            rows = []
            for d in parsed.deals:
                row = d.model_dump()
                row["source_url"] = source_url
                rows.append(row)
            print(f"    -> {len(rows)} deals extracted ({parsed.store_detected} — {parsed.pamphlet_title})")
            return rows
        except Exception as exc:
            print(f"    Attempt {attempt} failed on {file_path.name}: {exc}")
            if attempt < 3:
                time.sleep(attempt * 6)
        finally:
            if uploaded is not None:
                try:
                    client.files.delete(name=uploaded.name)
                except Exception:
                    pass
    return []


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
                "sourceUrl": d.get("source_url") or "",
                "stores": {},
            }

        entry = grouped[pid]
        if d.get("valid_until") and (not entry["validUntil"] or d["valid_until"] > entry["validUntil"]):
            entry["validUntil"] = d["valid_until"]
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

        existing = entry["stores"].get(store_key)
        if not existing or rew_p < existing["rewardPrice"]:
            entry["stores"][store_key] = {
                "store": store_key,
                "price": norm_p,
                "rewardPrice": rew_p,
                "card": d.get("card"),
            }

    prev_prices = load_previous_best_prices()
    products = []
    for item in grouped.values():
        item["stores"] = sorted(item["stores"].values(), key=lambda s: s["rewardPrice"])
        if item["stores"]:
            new_best = item["stores"][0]["rewardPrice"]
            old_best = prev_prices.get(item["id"])
            if old_best and old_best > new_best + 0.5:
                item["prevBestPrice"] = round(old_best, 2)
        products.append(item)

    products.sort(key=lambda p: (p["category"], p["name"]))
    print(f"UNLIMITED MERGE COMPLETE: {len(products)} active products ({len(all_raw)} raw offers, {skipped_expired} expired removed).")
    return {
        "updatedAt": datetime.now(timezone.utc).isoformat(),
        "sourceNote": f"Live AI v6: {len(products)} active pamphlet items ({skipped_expired} expired removed)",
        "products": products,
    }


def main() -> int:
    local_files: List[Tuple[Path, str]] = [
        (p, "") for p in sorted(PAMPHLET_DIR.iterdir())
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTS
    ] if PAMPHLET_DIR.exists() else []

    with tempfile.TemporaryDirectory() as tmp_str:
        tmp_dir = Path(tmp_str)
        url_files = download_url_list(tmp_dir)
        auto_files = discover_public_pamphlets(tmp_dir)
        all_inputs = local_files + url_files + auto_files

        if not all_inputs:
            print("No local or auto-discovered pamphlet files found. Keeping existing deals.json.")
            return 0

        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            print("ERROR: GEMINI_API_KEY secret is not set.", file=sys.stderr)
            return 1

        model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
        client = genai.Client(api_key=api_key)
        cache = load_cache()
        all_raw: List[dict] = []

        for fpath, src_url in all_inputs:
            fhash = sha256_file(fpath)
            if fhash in cache:
                print(f"Cached ({len(cache[fhash])} deals): {fpath.name}")
                all_raw.extend(cache[fhash])
                continue
            print(f"Extracting ALL pages of {fpath.name}...")
            file_deals: List[dict] = []
            for chunk_path in split_pdf_chunks(fpath, tmp_dir):
                file_deals.extend(call_gemini_with_retry(client, model, chunk_path, src_url))
            if file_deals:
                cache[fhash] = file_deals
                all_raw.extend(file_deals)

        save_cache(cache)
        if not all_raw:
            print("No deals extracted; keeping existing deals.json.")
            return 0

        payload = merge_deals(all_raw)
        OUTPUT_FILE.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Wrote {OUTPUT_FILE} with {len(payload['products'])} active items.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
