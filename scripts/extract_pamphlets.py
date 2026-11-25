#!/usr/bin/env python3
"""
Mzansi Smart Basket — Automated SA Pamphlet OCR & Price Extractor
"""
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Literal, Optional

import requests
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

PAMPHLET_DIR = Path("pamphlets")
OUTPUT_FILE = Path("deals.json")
SUPPORTED_EXTS = {".pdf", ".png", ".jpg", ".jpeg", ".webp"}


class ExtractedDeal(BaseModel):
    canonical_name: str = Field(
        description="Standardized SA product name including pack size, e.g. '10kg White Maize Meal', '2L Sunflower Cooking Oil'."
    )
    category: Literal["Staples", "Food & Meat", "Snacks & Drinks", "Household", "Clothing"]
    emoji: str = Field(description="Single relevant emoji, e.g. 🌽, 🍗, 🌻, 🧻, 👕")
    store: str = Field(description="Retailer name, e.g. Shoprite, Boxer, Pick n Pay, Checkers, SPAR, PEP, Ackermans")
    normal_price: float = Field(description="Regular/non-card price in ZAR")
    reward_price: float = Field(description="Loyalty card price in ZAR if advertised, otherwise equal to normal_price")
    card: Optional[Literal["xtra", "smart", "boxer", "spar"]] = Field(
        default=None,
        description="'xtra' for Shoprite/Checkers, 'smart' for Pick n Pay, 'boxer' for Boxer, 'spar' for SPAR, or null."
    )
    provinces: List[str] = Field(
        default_factory=lambda: ["All"],
        description="Applicable SA provinces, or ['All'] if national."
    )
    valid_until: Optional[str] = Field(default=None, description="End date in YYYY-MM-DD if printed.")


class PamphletExtraction(BaseModel):
    store_detected: str
    deals: List[ExtractedDeal]


EXTRACTION_PROMPT = """
You are a South African grocery & retail specials data extractor.
Inspect the attached retail pamphlet (PDF or image) and extract every clear product special with a visible Rand (R) price.

Rules:
1. Standardize canonical_name with pack size first (e.g. "10kg White Maize Meal", "2L Sunflower Cooking Oil", "6 x 1L Full Cream Long-Life Milk", "5kg IQF Mixed Chicken Portions", "18-Roll 2-Ply Toilet Paper") so identical staples from Shoprite, Boxer, Pick n Pay, Checkers, and SPAR group together.
2. Separate normal_price from reward_price. If only one price is shown, set both equal.
3. Map cards strictly: Shoprite/Checkers -> "xtra", Pick n Pay -> "smart", Boxer -> "boxer", SPAR -> "spar", others -> null.
4. Skip blurry or unreadable prices — never guess.
"""


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def extract_file(client: genai.Client, model: str, file_path: Path) -> List[ExtractedDeal]:
    print(f"Uploading {file_path.name} to Gemini Files API...")
    uploaded = client.files.upload(file=str(file_path))
    try:
        response = client.models.generate_content(
            model=model,
            contents=[uploaded, EXTRACTION_PROMPT],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=PamphletExtraction,
                temperature=0.1,
            ),
        )
        parsed = PamphletExtraction.model_validate_json(response.text)
        print(f"  -> Extracted {len(parsed.deals)} deals from {parsed.store_detected} ({file_path.name})")
        return parsed.deals
    finally:
        try:
            client.files.delete(name=uploaded.name)
        except Exception:
            pass


def merge_deals(all_deals: List[ExtractedDeal]) -> dict:
    grouped = {}
    for d in all_deals:
        if d.normal_price <= 0:
            continue
        pid = slugify(d.canonical_name)
        if pid not in grouped:
            grouped[pid] = {
                "id": pid,
                "name": d.canonical_name.strip(),
                "category": d.category,
                "emoji": d.emoji or "🛒",
                "provinces": d.provinces or ["All"],
                "validUntil": d.valid_until or "",
                "stores": {},
            }
        entry = grouped[pid]
        if d.valid_until and not entry["validUntil"]:
            entry["validUntil"] = d.valid_until

        store_key = d.store.strip()
        reward_p = d.reward_price if d.reward_price > 0 else d.normal_price
        existing = entry["stores"].get(store_key)
        if not existing or reward_p < existing["rewardPrice"]:
            entry["stores"][store_key] = {
                "store": store_key,
                "price": round(float(d.normal_price), 2),
                "rewardPrice": round(float(reward_p), 2),
                "card": d.card,
            }

    products = []
    for item in grouped.values():
        item["stores"] = sorted(item["stores"].values(), key=lambda s: s["rewardPrice"])
        products.append(item)

    products.sort(key=lambda p: (p["category"], p["name"]))
    return {
        "updatedAt": datetime.now(timezone.utc).isoformat(),
        "sourceNote": f"Auto-extracted from {len(all_deals)} pamphlet offers via Gemini Vision",
        "products": products,
    }


def push_to_supabase(payload: dict) -> None:
    sb_url = os.environ.get("SUPABASE_URL", "").rstrip("/")
    sb_key = os.environ.get("SUPABASE_SERVICE_KEY", "")
    if not sb_url or not sb_key:
        return
    endpoint = f"{sb_url}/rest/v1/deals_feed"
    headers = {
        "apikey": sb_key,
        "Authorization": f"Bearer {sb_key}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates",
    }
    row = {"id": "latest", "updated_at": payload["updatedAt"], "payload": payload}
    resp = requests.post(endpoint, headers=headers, json=row, timeout=20)
    resp.raise_for_status()
    print("Synced latest feed to Supabase deals_feed table.")


def main() -> int:
    files = sorted(
        p for p in PAMPHLET_DIR.iterdir()
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTS
    ) if PAMPHLET_DIR.exists() else []

    if not files:
        print("No pamphlet PDFs or images found in pamphlets/. Keeping existing deals.json unchanged.")
        return 0

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY environment variable is not set.", file=sys.stderr)
        return 1

    model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
    client = genai.Client(api_key=api_key)

    all_deals: List[ExtractedDeal] = []
    for fpath in files:
        try:
            all_deals.extend(extract_file(client, model, fpath))
        except Exception as exc:
            print(f"WARNING: Failed to process {fpath.name}: {exc}", file=sys.stderr)

    if not all_deals:
        print("No deals extracted; keeping existing deals.json.")
        return 0

    payload = merge_deals(all_deals)
    OUTPUT_FILE.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(payload['products'])} merged products to {OUTPUT_FILE}.")

    try:
        push_to_supabase(payload)
    except Exception as exc:
        print(f"WARNING: Supabase sync skipped/failed: {exc}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
