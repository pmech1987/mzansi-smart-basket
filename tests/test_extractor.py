import sys, types, os, json, tempfile, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
for name in ("google", "google.genai", "google.genai.types", "pydantic"):   # stub heavy deps: tests run offline
    if name not in sys.modules:
        try: __import__(name)
        except Exception:
            m = types.ModuleType(name); sys.modules[name] = m
sys.modules["google"].genai = sys.modules["google.genai"]; sys.modules["google.genai"].types = sys.modules["google.genai.types"]
sys.modules["google.genai"].Client = object
pd = sys.modules["pydantic"]
if not hasattr(pd, "BaseModel"):
    pd.BaseModel = type("BaseModel", (), {}); pd.Field = lambda *a, **k: None
import extract_pamphlets as ep

def d(name, price, store="Shoprite", **kw):
    r = dict(canonical_name=name, normal_price=price + 10, reward_price=price, store=store, category="Pantry & Tins",
             pamphlet_title="W", valid_from="2026-11-23", valid_until="2099-01-01", card=None)
    r.update(kw); return r

class T(unittest.TestCase):
    def test_size(self):
        self.assertEqual(ep.parse_size("5kg"), (5000.0, "g"))
        self.assertEqual(ep.parse_size("6 x 330ml"), (1980.0, "ml"))
        self.assertEqual(ep.parse_size("2L Milk"), (2000.0, "ml"))
        self.assertIsNone(ep.parse_size("Air Fryer"))
    def test_salvage(self):
        t = '{"deals":[{"canonical_name":"A"},{"canonical_name":"B"},{"canonical_name":"C","no'
        self.assertEqual([x["canonical_name"] for x in ep.salvage_deals(t)], ["A", "B"])
    def test_merge_per_store_dates_and_single_price(self):
        out = ep.merge_deals([d("Milk 2L", 30, valid_until="2099-01-01"),
                              d("Milk 2L", 28, store="Boxer", valid_until="2099-02-02"),
                              d("Only Promo", 9, normal_price=0)])
        names = {p["name"]: p for p in out["products"]}
        self.assertIn("Only Promo", names)
        ends = {s["store"]: s["validUntil"] for s in names["Milk 2L"]["stores"]}
        self.assertEqual(ends, {"Shoprite": "2099-01-01", "Boxer": "2099-02-02"})
        self.assertEqual(names["Milk 2L"]["sizeUnit"], "ml")
    def test_second_offer_same_store_kept(self):
        out = ep.merge_deals([d("Chicken 5kg", 99), d("Chicken 5kg", 89, pamphlet_title="Combo")])
        st = out["products"][0]["stores"][0]
        self.assertEqual(st["rewardPrice"], 89); self.assertEqual(len(st["moreOffers"]), 1)
        self.assertEqual(st["moreOffers"][0]["rewardPrice"], 99)
    def test_expired_item_removed(self):
        out = ep.merge_deals([d("Old", 5, valid_until="2020-01-01"), d("New", 5)])
        self.assertEqual([p["name"] for p in out["products"]], ["New"])

    def test_remote_download_streams_and_checks_pdf_signature(self):
        class FakeResponse:
            headers = {"content-length": "13"}
            def iter_content(self, chunk_size):
                yield b"%PDF-1.7"
                yield b"\nbody"
        with tempfile.TemporaryDirectory() as td:
            out = ep.save_remote_response(FakeResponse(), Path(td), 1, max_bytes=100)
            self.assertEqual(out.suffix, ".pdf")
            self.assertEqual(out.read_bytes(), b"%PDF-1.7\nbody")

    def test_remote_download_rejects_html_even_if_url_looks_like_pdf(self):
        class FakeResponse:
            headers = {"content-length": "15"}
            def iter_content(self, chunk_size):
                yield b"<html>not pdf</html>"
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError, "recognised PDF"):
                ep.save_remote_response(FakeResponse(), Path(td), 2, max_bytes=100)
            self.assertFalse((Path(td) / "url_pamphlet_2.part").exists())

    def test_remote_download_rejects_oversize_content_length_before_streaming(self):
        class FakeResponse:
            headers = {"content-length": "101"}
            def iter_content(self, chunk_size):
                raise AssertionError("oversize response should not be streamed")
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError, "exceeds configured"):
                ep.save_remote_response(FakeResponse(), Path(td), 3, max_bytes=100)

    def test_remote_download_enforces_streamed_byte_limit_without_content_length(self):
        class FakeResponse:
            headers = {}
            def iter_content(self, chunk_size):
                yield b"%PDF-1.7" + b"a" * 60
                yield b"b" * 60
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError, "exceeds configured"):
                ep.save_remote_response(FakeResponse(), Path(td), 4, max_bytes=100)
            self.assertFalse((Path(td) / "url_pamphlet_4.part").exists())

    def test_remote_url_requires_https_and_exact_approved_host(self):
        approved = {"specials.example.org"}
        self.assertTrue(ep.host_is_approved("https://specials.example.org/weekly.pdf", approved))
        self.assertFalse(ep.host_is_approved("http://specials.example.org/weekly.pdf", approved))
        self.assertFalse(ep.host_is_approved("https://www.specials.example.org/weekly.pdf", approved))
        self.assertFalse(ep.host_is_approved("https://unapproved.example/weekly.pdf", approved))

    def test_private_source_registry_secret_overrides_repository_template(self):
        old_path = ep.APPROVED_SOURCES_FILE
        old_secret = os.environ.get("APPROVED_SOURCES_JSON")
        try:
            with tempfile.TemporaryDirectory() as td:
                ep.APPROVED_SOURCES_FILE = Path(td) / "approved_sources.json"
                ep.APPROVED_SOURCES_FILE.write_text(json.dumps({"sources": []}), encoding="utf-8")
                secret = {"sources": [{
                    "status": "approved", "source_id": "private-source", "label": "Private approved source",
                    "reviewed_at": "2026-11-25T10:00:00+02:00", "files": ["local.pdf"],
                    "allow_remote_download": False, "allow_commercial_data_extraction": True,
                    "allow_ai_document_upload": True, "permission_basis": "written_permission_or_licence",
                    "evidence_reference": "private-agreement-reference", "reviewed_by": "Reviewer",
                }]}
                os.environ["APPROVED_SOURCES_JSON"] = json.dumps(secret)
                records = ep.approved_source_records()
                self.assertEqual(len(records), 1)
                self.assertEqual(records[0]["source_id"], "private-source")
        finally:
            ep.APPROVED_SOURCES_FILE = old_path
            if old_secret is None: os.environ.pop("APPROVED_SOURCES_JSON", None)
            else: os.environ["APPROVED_SOURCES_JSON"] = old_secret

    def test_source_registry_requires_explicit_commercial_permission_evidence(self):
        old_path = ep.APPROVED_SOURCES_FILE
        try:
            with tempfile.TemporaryDirectory() as td:
                registry = Path(td) / "approved_sources.json"
                registry.write_text(json.dumps({"sources": [{
                    "status": "approved",
                    "source_id": "source-example",
                    "label": "Example approved source",
                    "reviewed_at": "2026-11-25T10:00:00+02:00",
                    "hosts": ["specials.example.org"],
                    "allow_remote_download": True,
                    "allow_commercial_data_extraction": True,
                    "allow_ai_document_upload": True,
                    "permission_basis": "written_permission_or_licence",
                    "evidence_reference": "agreement-2026-01",
                    "reviewed_by": "Reviewer"
                }]}), encoding="utf-8")
                ep.APPROVED_SOURCES_FILE = registry
                self.assertEqual(ep.approved_remote_source_hosts(), {"specials.example.org"})
                registry.write_text(json.dumps({"sources": [{
                    "status": "approved",
                    "source_id": "source-example",
                    "label": "Example approved source",
                    "reviewed_at": "2026-11-25T10:00:00+02:00",
                    "hosts": ["specials.example.org"],
                    "allow_remote_download": True,
                    "allow_commercial_data_extraction": True,
                    "allow_ai_document_upload": True,
                    "permission_basis": "unconfirmed",
                    "evidence_reference": "",
                    "reviewed_by": "Reviewer"
                }]}), encoding="utf-8")
                self.assertEqual(ep.approved_remote_source_hosts(), set())
        finally:
            ep.APPROVED_SOURCES_FILE = old_path

    def test_no_caps_3000(self):
        out = ep.merge_deals([d(f"Item {i} {i*3}g", 10 + i % 50) for i in range(3000)])
        self.assertEqual(len(out["products"]), 3000)

class CoverageAndOfferCompletenessTests(unittest.TestCase):
    def test_store_and_alternate_offers_retain_independent_province_scope(self):
        out = ep.merge_deals([
            d("2kg Chicken Portions", 49.99, store="Shoprite", provinces=["Mpumalanga"], pamphlet_title="Mpumalanga Butchery"),
            d("2kg Chicken Portions", 49.99, store="Shoprite", provinces=["Limpopo"], pamphlet_title="Limpopo Butchery"),
        ])
        product = out["products"][0]
        self.assertIn("Mpumalanga", product["provinces"])
        self.assertIn("Limpopo", product["provinces"])
        primary = product["stores"][0]
        scopes = [primary["provinces"]] + [x["provinces"] for x in primary.get("moreOffers", [])]
        self.assertIn(["Mpumalanga"], scopes)
        self.assertIn(["Limpopo"], scopes)

    def test_same_price_offers_from_distinct_pamphlets_are_retained(self):
        rows = [
            d("Chicken Thigh Portions 2kg", 89.99, pamphlet_title="Weekly Food", source_file="shoprite_weekly.pdf", source_page=4, source_url="https://shoprite.example/a"),
            d("Chicken Thigh Portions 2kg", 89.99, pamphlet_title="Butchery Weekend", source_file="shoprite_butchery.pdf", source_page=2, source_url="https://shoprite.example/b", multi_buy_note="Weekend special"),
        ]
        result = ep.merge_deals(rows)
        product = result["products"][0]
        primary = product["stores"][0]
        self.assertEqual(primary["rewardPrice"], 89.99)
        self.assertEqual(len(primary["moreOffers"]), 1)
        self.assertEqual(primary["moreOffers"][0]["pamphletTitle"], "Butchery Weekend")
        self.assertEqual(primary["moreOffers"][0]["sourcePage"], 2)

    def test_exact_duplicate_offer_is_deduplicated(self):
        row = d("Chicken Thigh Portions 2kg", 89.99, pamphlet_title="Weekly Food", source_file="shoprite_weekly.pdf", source_page=4, source_url="https://shoprite.example/a")
        result = ep.merge_deals([row, dict(row)])
        self.assertEqual(len(result["products"]), 1)
        self.assertEqual(len(result["products"][0]["stores"]), 1)
        self.assertEqual(result["products"][0]["stores"][0].get("moreOffers", []), [])

    def test_lower_price_becomes_primary_and_old_offer_is_preserved(self):
        rows = [
            d("Air Fryer 5L", 999.00, store="Game", pamphlet_title="Appliance Month", source_page=1),
            d("Air Fryer 5L", 899.00, store="Game", pamphlet_title="Weekend Flash", source_page=3),
        ]
        result = ep.merge_deals(rows)
        store = result["products"][0]["stores"][0]
        self.assertEqual(store["rewardPrice"], 899.00)
        self.assertEqual(len(store["moreOffers"]), 1)
        self.assertEqual(store["moreOffers"][0]["rewardPrice"], 999.00)

    def test_pdf_is_split_into_individually_numbered_pages(self):
        if not ep.HAS_PYPDF:
            self.skipTest("pypdf is not installed")
        from pypdf import PdfWriter, PdfReader
        with tempfile.TemporaryDirectory() as td:
            folder = Path(td)
            source = folder / "multi.pdf"
            writer = PdfWriter()
            for _ in range(5):
                writer.add_blank_page(width=300, height=400)
            with source.open("wb") as fh:
                writer.write(fh)
            out_folder = folder / "chunks"
            out_folder.mkdir()
            pages = ep.split_pdf_chunks(source, out_folder)
            self.assertEqual([n for _, n in pages], [1, 2, 3, 4, 5])
            self.assertEqual([len(PdfReader(str(path)).pages) for path, _ in pages], [1, 1, 1, 1, 1])

    def test_legacy_cache_is_invalidated(self):
        old = ep.CACHE_FILE
        try:
            with tempfile.TemporaryDirectory() as td:
                ep.CACHE_FILE = Path(td) / "cache.json"
                ep.CACHE_FILE.write_text(json.dumps({"hash1": [{"canonical_name": "possibly partial"}]}), encoding="utf-8")
                self.assertEqual(ep.load_cache(), {})
        finally:
            ep.CACHE_FILE = old

    def test_versioned_complete_cache_round_trip(self):
        old = ep.CACHE_FILE
        try:
            with tempfile.TemporaryDirectory() as td:
                ep.CACHE_FILE = Path(td) / "cache.json"
                record = {"status": "complete", "expectedOfferCount": 0, "rows": []}
                ep.save_cache({"pagehash": record})
                loaded = ep.load_cache()
                self.assertEqual(loaded["pagehash"], record)
                self.assertEqual(json.loads(ep.CACHE_FILE.read_text())["schemaVersion"], ep.CACHE_SCHEMA_VERSION)
        finally:
            ep.CACHE_FILE = old

    def test_extraction_schema_requires_explicit_page_count(self):
        valid = {"store_detected": "Shoprite", "pamphlet_title": "Test", "page_priced_offer_count": 0, "deals": []}
        parsed = ep.PamphletExtraction.model_validate_json(json.dumps(valid))
        self.assertEqual(parsed.page_priced_offer_count, 0)
        missing_count = {"store_detected": "Shoprite", "pamphlet_title": "Test", "deals": []}
        with self.assertRaises(Exception):
            ep.PamphletExtraction.model_validate_json(json.dumps(missing_count))

    def test_no_offer_page_can_be_complete_only_when_zero_is_explicit(self):
        class Files:
            def upload(self, file): return type("Uploaded", (), {"name": "fake-upload"})()
            def delete(self, name): pass
        class Models:
            def __init__(self, texts): self.texts, self.calls = list(texts), 0
            def generate_content(self, **kwargs):
                text_value = self.texts[min(self.calls, len(self.texts) - 1)]
                self.calls += 1
                return type("Response", (), {"text": text_value})()
        zero_response = json.dumps({"store_detected": "Shoprite", "pamphlet_title": "Empty Page", "page_priced_offer_count": 0, "deals": []})
        mismatch_response = json.dumps({"store_detected": "Shoprite", "pamphlet_title": "Wrong Count", "page_priced_offer_count": 1, "deals": []})
        zero_audit = json.dumps({"page_priced_offer_count": 0, "observations": []})
        mismatch_audit = json.dumps({"page_priced_offer_count": 1, "observations": ["one offer block visible"]})
        class Client:
            def __init__(self, texts): self.files, self.models = Files(), Models(texts)
        with tempfile.TemporaryDirectory() as td:
            fake_page = Path(td) / "page.pdf"
            fake_page.write_bytes(b"not actually uploaded by the fake client")
            original_sleep = ep.time.sleep
            original_config = getattr(ep.types, "GenerateContentConfig", None)
            ep.time.sleep = lambda *_: None
            ep.types.GenerateContentConfig = lambda **kwargs: kwargs
            try:
                rows, status, extraction_count, audit_count = ep.call_gemini_with_retry(Client([zero_response, zero_audit]), "test-model", fake_page, "")
                self.assertEqual((rows, status, extraction_count, audit_count), ([], "complete", 0, 0))
                rows, status, extraction_count, audit_count = ep.call_gemini_with_retry(Client([zero_response, mismatch_audit]), "test-model", fake_page, "")
                self.assertEqual((rows, status, extraction_count, audit_count), ([], "count_mismatch", 0, 1))
                rows, status, extraction_count, audit_count = ep.call_gemini_with_retry(Client([mismatch_response, mismatch_audit]), "test-model", fake_page, "")
                self.assertEqual((rows, status, extraction_count, audit_count), ([], "count_mismatch", 1, 1))
            finally:
                ep.time.sleep = original_sleep
                if original_config is None:
                    delattr(ep.types, "GenerateContentConfig")
                else:
                    ep.types.GenerateContentConfig = original_config


    def test_explicit_expiry_instant_overrides_end_date(self):
        self.assertTrue(ep.is_expired("2099-12-31", "2000-01-01T10:00:00+02:00"))
        self.assertFalse(ep.is_expired("2000-01-01", "2099-12-31T23:59:00+02:00"))

    def test_malformed_explicit_expiry_fails_closed(self):
        self.assertTrue(ep.is_expired("2099-12-31", "not-a-timestamp"))

    def test_date_only_validity_includes_end_date(self):
        # A printed end date remains valid through that local calendar date.
        self.assertFalse(ep.is_expired("2999-12-31"))


    def test_merge_audit_records_invalid_prices_and_expiry(self):
        good = d("Valid Milk 2L", 25)
        no_price = d("No Price Product", 0, normal_price=0, reward_price=0)
        invalid_expiry = d("Bad Expiry Product", 10, valid_until="2099-12-31", valid_until_at="not-an-iso-date")
        no_name = d("", 10)
        out = ep.merge_deals([good, no_price, invalid_expiry, no_name])
        audit = out["mergeAudit"]
        self.assertEqual(audit["rawOfferCount"], 4)
        self.assertEqual(audit["invalidPriceRows"], 1)
        self.assertEqual(audit["invalidExpiryRows"], 1)
        self.assertEqual(audit["missingNameRows"], 1)
        self.assertFalse(audit["complete"])

    def test_disabled_ai_writes_explicit_blocked_coverage_report(self):
        old_paths = (ep.PAMPHLET_DIR, ep.APPROVED_SOURCES_FILE, ep.COVERAGE_FILE, ep.URLS_FILE)
        old_env = {key: os.environ.get(key) for key in ("ENABLE_GEMINI_DOCUMENT_UPLOADS", "ENABLE_APPROVED_REMOTE_DOWNLOADS", "APPROVED_SOURCES_JSON")}
        try:
            with tempfile.TemporaryDirectory() as td:
                folder = Path(td)
                ep.PAMPHLET_DIR = folder / "pamphlets"
                ep.PAMPHLET_DIR.mkdir()
                ep.APPROVED_SOURCES_FILE = folder / "approved_sources.json"
                ep.APPROVED_SOURCES_FILE.write_text(json.dumps({"sources": []}), encoding="utf-8")
                ep.URLS_FILE = folder / "pamphlet_urls.txt"
                ep.COVERAGE_FILE = folder / "coverage_report.json"
                os.environ["ENABLE_GEMINI_DOCUMENT_UPLOADS"] = "false"
                self.assertEqual(ep.main(), 0)
                report = json.loads(ep.COVERAGE_FILE.read_text(encoding="utf-8"))
                self.assertEqual(report["status"], "blocked_ai_upload_disabled")
                self.assertFalse(report["complete"])
        finally:
            ep.PAMPHLET_DIR, ep.APPROVED_SOURCES_FILE, ep.COVERAGE_FILE, ep.URLS_FILE = old_paths
            for key, value in old_env.items():
                if value is None: os.environ.pop(key, None)
                else: os.environ[key] = value

if __name__ == "__main__": unittest.main()
