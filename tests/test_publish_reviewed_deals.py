import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "publish_reviewed_deals.py"


def candidate_payload(**overrides):
    payload = {
        "products": [
            {
                "id": "milk_2l",
                "name": "2L Full Cream Milk",
                "validUntil": "2099-12-31",
                "sourceUrl": "https://retailer.example/specials",
                "stores": [
                    {
                        "store": "Example Market",
                        "price": 32.99,
                        "rewardPrice": 29.99,
                        "validUntil": "2099-12-31",
                        "sourceUrl": "https://retailer.example/specials",
                    }
                ],
            }
        ],
        "coverage_run": {"pagesTotal": 1, "pagesComplete": 1, "pagesIncomplete": 0, "unreadChunks": 0, "quotaExhausted": False, "expectedOfferCount": 1, "extractedOfferCount": 1, "offerCountAuditComplete": True, "complete": True, "mergeAuditComplete": True, "mergeAudit": {"rawOfferCount": 1, "representedOfferCount": 1, "exactDuplicateRows": 0, "expiredOffersSkipped": 0, "invalidPriceRows": 0, "missingNameRows": 0, "invalidExpiryRows": 0, "complete": True}},
        "approvalStatus": "pending_review",
    }
    payload.update(overrides)
    return payload


class PublishReviewedDealsTests(unittest.TestCase):
    def _write_candidate(self, folder, payload):
        path = folder / "deals_pending_review.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def test_requires_explicit_review_acknowledgement(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            candidate = self._write_candidate(folder, candidate_payload())
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--reviewed-by", "Test Reviewer", "--candidate", str(candidate), "--output", str(folder / "deals.json")],
                cwd=folder, capture_output=True, text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((folder / "deals.json").exists())

    def test_requires_source_rights_attestation(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            candidate = self._write_candidate(folder, candidate_payload())
            output = folder / "deals.json"
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--reviewed-by", "Test Reviewer", "--i-have-checked-every-offer", "--candidate", str(candidate), "--output", str(output)],
                cwd=folder, capture_output=True, text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("source and planned commercial extraction/display", result.stderr)
            self.assertFalse(output.exists())

    def test_publishes_only_when_review_acknowledged_and_candidate_valid(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            candidate = self._write_candidate(folder, candidate_payload())
            output = folder / "deals.json"
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--reviewed-by", "Test Reviewer", "--i-have-checked-every-offer", "--i-have-confirmed-source-rights", "--candidate", str(candidate), "--output", str(output)],
                cwd=folder, capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            published = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(published["approvalStatus"], "verified")
            self.assertEqual(published["reviewedBy"], "Test Reviewer")
            self.assertIn("verifiedAt", published)
            self.assertIn("sourceRightsCheckedAt", published)
            self.assertEqual(published["sourceRightsCheckedBy"], "Test Reviewer")
            self.assertNotIn("coverage_run", published)

    def test_refuses_expired_offer(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            payload = candidate_payload()
            payload["products"][0]["stores"][0]["validUntil"] = "2000-01-01"
            candidate = self._write_candidate(folder, payload)
            output = folder / "deals.json"
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--reviewed-by", "Test Reviewer", "--i-have-checked-every-offer", "--i-have-confirmed-source-rights", "--candidate", str(candidate), "--output", str(output)],
                cwd=folder, capture_output=True, text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("expiry date has already passed", result.stderr)
            self.assertFalse(output.exists())

    def test_refuses_non_finite_price(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            payload = candidate_payload()
            payload["products"][0]["stores"][0]["price"] = float("nan")
            candidate = self._write_candidate(folder, payload)
            output = folder / "deals.json"
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--reviewed-by", "Test Reviewer", "--i-have-checked-every-offer", "--i-have-confirmed-source-rights", "--candidate", str(candidate), "--output", str(output)],
                cwd=folder, capture_output=True, text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(output.exists())

    def test_refuses_incomplete_extraction_coverage(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            payload = candidate_payload(coverage_run={"unreadChunks": 1, "quotaExhausted": False})
            candidate = self._write_candidate(folder, payload)
            output = folder / "deals.json"
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--reviewed-by", "Test Reviewer", "--i-have-checked-every-offer", "--i-have-confirmed-source-rights", "--candidate", str(candidate), "--output", str(output)],
                cwd=folder, capture_output=True, text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(output.exists())

    def test_refuses_candidate_without_page_level_audit(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            payload = candidate_payload()
            payload["coverage_run"] = {"unreadChunks": 0, "quotaExhausted": False}
            candidate = self._write_candidate(folder, payload)
            output = folder / "deals.json"
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--reviewed-by", "Test Reviewer", "--i-have-checked-every-offer", "--i-have-confirmed-source-rights", "--candidate", str(candidate), "--output", str(output)],
                cwd=folder, capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("page-level offer-count audit", result.stderr)
            self.assertFalse(output.exists())

    def test_refuses_offer_count_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            payload = candidate_payload()
            payload["coverage_run"]["expectedOfferCount"] = 2
            candidate = self._write_candidate(folder, payload)
            output = folder / "deals.json"
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--reviewed-by", "Test Reviewer", "--i-have-checked-every-offer", "--i-have-confirmed-source-rights", "--candidate", str(candidate), "--output", str(output)],
                cwd=folder, capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 2)
            self.assertFalse(output.exists())

    def test_refuses_exact_expiry_instant_in_the_past(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            payload = candidate_payload()
            payload["products"][0]["stores"][0]["validUntilAt"] = "2000-01-01T10:00:00+02:00"
            candidate = self._write_candidate(folder, payload)
            output = folder / "deals.json"
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--reviewed-by", "Test Reviewer", "--i-have-checked-every-offer", "--i-have-confirmed-source-rights", "--candidate", str(candidate), "--output", str(output)],
                cwd=folder, capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("exact offer expiry time has already passed", result.stderr)
            self.assertFalse(output.exists())

    def test_refuses_invalid_exact_expiry_instant(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            payload = candidate_payload()
            payload["products"][0]["stores"][0]["validUntilAt"] = "tomorrow after lunch"
            candidate = self._write_candidate(folder, payload)
            output = folder / "deals.json"
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--reviewed-by", "Test Reviewer", "--i-have-checked-every-offer", "--i-have-confirmed-source-rights", "--candidate", str(candidate), "--output", str(output)],
                cwd=folder, capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("exact expiry instant is invalid", result.stderr)
            self.assertFalse(output.exists())

    def test_refuses_expired_secondary_offer_in_more_offers(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            payload = candidate_payload()
            payload["products"][0]["stores"][0]["moreOffers"] = [{
                "store": "Example Market",
                "price": 35.99,
                "rewardPrice": 35.99,
                "validUntil": "2000-01-01",
                "sourceUrl": "https://retailer.example/old-special",
            }]
            candidate = self._write_candidate(folder, payload)
            output = folder / "deals.json"
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--reviewed-by", "Test Reviewer", "--i-have-checked-every-offer", "--i-have-confirmed-source-rights", "--candidate", str(candidate), "--output", str(output)],
                cwd=folder, capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("offer 2: offer expiry date has already passed", result.stderr)
            self.assertFalse(output.exists())

    def test_refuses_secondary_offer_without_source_provenance(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            payload = candidate_payload()
            payload["products"][0].pop("sourceUrl", None)
            payload["products"][0]["stores"][0]["moreOffers"] = [{
                "store": "Example Market",
                "price": 35.99,
                "rewardPrice": 35.99,
                "validUntil": "2099-12-31",
            }]
            candidate = self._write_candidate(folder, payload)
            output = folder / "deals.json"
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--reviewed-by", "Test Reviewer", "--i-have-checked-every-offer", "--i-have-confirmed-source-rights", "--candidate", str(candidate), "--output", str(output)],
                cwd=folder, capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("offer 2: requires an HTTPS source URL", result.stderr)
            self.assertFalse(output.exists())

    def test_refuses_exact_start_at_or_after_exact_expiry(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            payload = candidate_payload()
            offer = payload["products"][0]["stores"][0]
            offer["validFrom"] = "2099-12-31"
            offer["validUntil"] = "2099-12-31"
            offer["validFromAt"] = "2099-12-31T18:00:00+02:00"
            offer["validUntilAt"] = "2099-12-31T17:00:00+02:00"
            candidate = self._write_candidate(folder, payload)
            output = folder / "deals.json"
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--reviewed-by", "Test Reviewer", "--i-have-checked-every-offer", "--i-have-confirmed-source-rights", "--candidate", str(candidate), "--output", str(output)],
                cwd=folder, capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("exact start instant is not before expiry instant", result.stderr)
            self.assertFalse(output.exists())

    def test_refuses_unknown_offer_province(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            payload = candidate_payload()
            payload["products"][0]["stores"][0]["provinces"] = ["Somewhere Else"]
            candidate = self._write_candidate(folder, payload)
            output = folder / "deals.json"
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--reviewed-by", "Test Reviewer", "--i-have-checked-every-offer", "--i-have-confirmed-source-rights", "--candidate", str(candidate), "--output", str(output)],
                cwd=folder, capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("province scope is missing or contains an unknown region", result.stderr)
            self.assertFalse(output.exists())

    def test_allows_approved_local_source_with_registry_provenance(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            payload = candidate_payload()
            offer = payload["products"][0]["stores"][0]
            offer.pop("sourceUrl", None)
            offer["sourceId"] = "shoprite-local-weekly"
            offer["sourceLabel"] = "Shoprite locally supplied weekly PDF"
            offer["sourceEvidenceReference"] = "private/licence-register-entry-42"
            payload["products"][0].pop("sourceUrl", None)
            candidate = self._write_candidate(folder, payload)
            output = folder / "deals.json"
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--reviewed-by", "Test Reviewer", "--i-have-checked-every-offer", "--i-have-confirmed-source-rights", "--candidate", str(candidate), "--output", str(output)],
                cwd=folder, capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            published = json.loads(output.read_text(encoding="utf-8"))
            public_offer = published["products"][0]["stores"][0]
            self.assertEqual(public_offer["sourceId"], "shoprite-local-weekly")
            self.assertNotIn("sourceEvidenceReference", public_offer)


if __name__ == "__main__":
    unittest.main()
