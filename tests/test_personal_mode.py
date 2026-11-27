import json
import os
import tempfile
import unittest
from pathlib import Path

import scripts.extract_pamphlets as ep
import scripts.personal_sync as ps


class PersonalModeTests(unittest.TestCase):
    def test_safe_public_https_url_blocks_private_and_http(self):
        self.assertTrue(ep.is_safe_public_https_url("https://example.co.za/specials.pdf"))
        self.assertFalse(ep.is_safe_public_https_url("http://example.co.za/specials.pdf"))
        self.assertFalse(ep.is_safe_public_https_url("https://localhost/a.pdf"))
        self.assertFalse(ep.is_safe_public_https_url("https://127.0.0.1/a.pdf"))
        self.assertFalse(ep.is_safe_public_https_url("https://192.168.1.5/a.pdf"))

    def test_personal_sync_add_and_prune(self):
        with tempfile.TemporaryDirectory() as td:
            df = Path(td) / "deals.json"
            ps.add_personal_deal("Checkers|Clover Milk 2L|36,99|32,99|2026-12-06", deals_path=df)
            ps.add_personal_deal("Shoprite|Old Bread|15.00|12.00|2020-01-01", deals_path=df)
            data = json.loads(df.read_text(encoding="utf-8"))
            self.assertEqual(len(data["products"]), 2)
            milk = next(p for p in data["products"] if "Clover" in p["name"])
            self.assertEqual(milk["stores"][0]["rewardPrice"], 32.99)
            removed = ps.prune_expired(deals_path=df, today_iso="2026-11-27")
            self.assertEqual(removed, 1)
            data2 = json.loads(df.read_text(encoding="utf-8"))
            self.assertEqual(len(data2["products"]), 1)

    def test_index_has_personal_price_logger(self):
        html = (Path(__file__).resolve().parent.parent / "index.html").read_text(encoding="utf-8")
        self.assertIn("msb-add-price-btn", html)
        self.assertIn("msb_personal_deals_v1", html)


if __name__ == "__main__":
    unittest.main()
