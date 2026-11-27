#!/usr/bin/env python3
"""Mzansi Smart Basket — Personal Edition 1-Command Termux Sync & Price Logger.

For private, personal use on your own phone:
  1. Quick-add a single shelf price into deals.json (no API key needed):
       python3 scripts/personal_sync.py --add "Checkers|Clover Milk 2L|36.99|32.99|2026-12-06"
  2. Prune expired offers from deals.json:
       python3 scripts/personal_sync.py --prune-expired
  3. Extract all local pamphlets/ and pamphlet_urls.txt in PERSONAL_MODE=true
     and publish straight to deals.json (requires GEMINI_API_KEY):
       GEMINI_API_KEY=... python3 scripts/personal_sync.py --extract
"""
import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEALS_FILE = ROOT / "deals.json"
CANDIDATE_FILE = ROOT / "deals_candidate.json"
SAST = timezone(timedelta(hours=2))


def sast_today() -> str:
    return datetime.now(SAST).strftime("%Y-%m-%d")


def load_deals(path: Path) -> dict:
    if not path.exists():
        return {"schemaVersion": 3, "updatedAt": datetime.now(timezone.utc).isoformat(), "products": []}
    return json.loads(path.read_text(encoding="utf-8"))


def save_deals_atomic(path: Path, data: dict) -> None:
    data["updatedAt"] = datetime.now(timezone.utc).isoformat()
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(path)


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60] or "item"


def add_personal_deal(spec: str, deals_path: Path = DEALS_FILE) -> dict:
    parts = [p.strip() for p in spec.split("|")]
    if len(parts) < 3:
        raise ValueError("Use format: Store|Item Name|NormalPrice[|SpecialPrice][|ValidUntilYYYY-MM-DD]")
    store, name = parts[0], parts[1]
    price = round(float(parts[2].replace(",", ".")), 2)
    reward = round(float(parts[3].replace(",", ".")), 2) if len(parts) >= 4 and parts[3] else price
    valid_until = parts[4] if len(parts) >= 5 and re.match(r"^\d{4}-\d{2}-\d{2}$", parts[4]) else "2099-12-31"
    if not store or not name or price <= 0 or reward <= 0:
        raise ValueError("Store, item name, and positive prices are required.")

    data = load_deals(deals_path)
    products = data.setdefault("products", [])
    pid = "personal-" + slugify(name)
    offer = {
        "store": store,
        "price": price,
        "rewardPrice": min(price, reward),
        "validFrom": sast_today(),
        "validUntil": valid_until,
        "pamphletTitle": "Personal Price Entry",
    }
    existing = next((p for p in products if p.get("id") == pid or p.get("name", "").lower() == name.lower()), None)
    if existing:
        stores = existing.setdefault("stores", [])
        stores[:] = [s for s in stores if s.get("store", "").lower() != store.lower()]
        stores.append(offer)
    else:
        products.insert(0, {"id": pid, "name": name, "category": "Personal", "provinces": ["All"], "stores": [offer]})

    save_deals_atomic(deals_path, data)
    return offer


def prune_expired(deals_path: Path = DEALS_FILE, today_iso: str = "") -> int:
    today = today_iso or sast_today()
    data = load_deals(deals_path)
    removed = 0
    kept_products = []
    for prod in data.get("products", []):
        kept_stores = []
        for s in prod.get("stores", []):
            vu = str(s.get("validUntil") or "")
            if re.match(r"^\d{4}-\d{2}-\d{2}$", vu) and vu < today:
                removed += 1
            else:
                kept_stores.append(s)
        if kept_stores:
            prod["stores"] = kept_stores
            kept_products.append(prod)
    data["products"] = kept_products
    save_deals_atomic(deals_path, data)
    return removed


def run_personal_extract() -> int:
    env = os.environ.copy()
    env["PERSONAL_MODE"] = "true"
    rc = subprocess.run([sys.executable, str(ROOT / "scripts" / "extract_pamphlets.py")], cwd=ROOT, env=env).returncode
    if rc != 0:
        return rc
    if CANDIDATE_FILE.exists():
        cand = load_deals(CANDIDATE_FILE)
        if cand.get("products"):
            cand["approvalStatus"] = "personal_local"
            save_deals_atomic(DEALS_FILE, cand)
            print(f"PERSONAL SYNC COMPLETE: published {len(cand['products'])} products directly to {DEALS_FILE.name}.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Mzansi Smart Basket — Personal Termux Sync")
    ap.add_argument("--add", help="Quick-add shelf price: Store|Item Name|Price[|SpecialPrice][|ValidUntil]")
    ap.add_argument("--prune-expired", action="store_true", help="Remove expired offers from deals.json")
    ap.add_argument("--extract", action="store_true", help="Run pamphlet extraction in PERSONAL_MODE=true")
    args = ap.parse_args()

    if args.add:
        offer = add_personal_deal(args.add)
        print(f"Added personal deal: {offer['store']} R{offer['rewardPrice']:.2f} (valid until {offer['validUntil']})")
    if args.prune_expired:
        n = prune_expired()
        print(f"Pruned {n} expired store offer(s) from deals.json")
    if args.extract:
        return run_personal_extract()
    if not (args.add or args.prune_expired or args.extract):
        ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
