#!/usr/bin/env python3
"""Publish a manually reviewed candidate feed as deals.json.

This command does not verify prices itself. The operator must compare every
product/store offer with the authorized source pamphlet/page before running it.
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from math import isfinite
from zoneinfo import ZoneInfo
from pathlib import Path
from urllib.parse import urlparse


def valid_https_url(value):
    try:
        u = urlparse(str(value or ""))
        return u.scheme == "https" and bool(u.netloc)
    except Exception:
        return False


def main():
    parser = argparse.ArgumentParser(description="Publish manually checked retail offers")
    parser.add_argument("--reviewed-by", required=True, help="Your name or reviewer identifier")
    parser.add_argument("--i-have-checked-every-offer", action="store_true", help="Required acknowledgement that every offer was checked against its source")
    parser.add_argument("--i-have-confirmed-source-rights", action="store_true", help="Required acknowledgement that the source and planned commercial extraction/display have a valid permission or legal basis")
    parser.add_argument("--candidate", default="deals_pending_review.json")
    parser.add_argument("--output", default="deals.json")
    args = parser.parse_args()

    if not args.i_have_checked_every_offer:
        parser.error("Refusing to publish: pass --i-have-checked-every-offer only after checking every offer.")
    if not args.i_have_confirmed_source_rights:
        parser.error("Refusing to publish: first confirm the source and planned commercial extraction/display have a valid permission or legal basis.")
    if not args.reviewed_by.strip():
        parser.error("--reviewed-by cannot be blank.")

    candidate_path = Path(args.candidate)
    if not candidate_path.exists():
        print(f"Candidate feed not found: {candidate_path}", file=sys.stderr)
        return 2

    data = json.loads(candidate_path.read_text(encoding="utf-8"))
    products = data.get("products")
    if not isinstance(products, list) or not products:
        print("Candidate file has no products; nothing published.", file=sys.stderr)
        return 2

    coverage = data.get("coverage_run") or {}
    coverage_complete = (
        coverage.get("complete") is True
        and coverage.get("offerCountAuditComplete") is True
        and isinstance(coverage.get("pagesTotal"), int)
        and coverage.get("pagesTotal", 0) > 0
        and coverage.get("pagesComplete") == coverage.get("pagesTotal")
        and coverage.get("pagesIncomplete") == 0
        and coverage.get("expectedOfferCount") == coverage.get("extractedOfferCount")
        and coverage.get("mergeAuditComplete") is True
        and isinstance(coverage.get("mergeAudit"), dict)
        and coverage["mergeAudit"].get("invalidPriceRows") == 0
        and coverage["mergeAudit"].get("missingNameRows") == 0
        and coverage["mergeAudit"].get("invalidExpiryRows", 0) == 0
        and coverage["mergeAudit"].get("rawOfferCount") == coverage.get("extractedOfferCount")
        and int(coverage.get("unreadChunks") or 0) == 0
        and not bool(coverage.get("quotaExhausted"))
    )
    if not coverage_complete:
        print(
            "Not published: this candidate lacks a complete page-level offer-count audit, "
            "has unread/incomplete pages, or has an expected/extracted count mismatch. "
            "Finish and audit every source page before review and publication.",
            file=sys.stderr,
        )
        return 2

    issues = []
    today_sa = datetime.now(ZoneInfo("Africa/Johannesburg")).date()

    def offer_rows(store_offer):
        """Yield primary and alternate offers; none may bypass publication checks."""
        yield store_offer
        alternates = store_offer.get("moreOffers") or []
        if not isinstance(alternates, list):
            raise ValueError("moreOffers must be a list")
        for alternate in alternates:
            if not isinstance(alternate, dict):
                raise ValueError("moreOffers entries must be objects")
            yield alternate

    for product in products:
        pname = product.get("name") or product.get("id") or "(unnamed product)"
        offers = product.get("stores") or []
        if not offers:
            issues.append(f"{pname}: no store offers")
        for store_offer in offers:
            try:
                records = list(offer_rows(store_offer))
            except ValueError as exc:
                issues.append(f"{pname}: {exc}")
                continue
            for offer_index, offer in enumerate(records, start=1):
                label = f"{pname} / {offer.get('store', store_offer.get('store', '(unnamed store)'))} / offer {offer_index}"
                for field in ("price", "rewardPrice"):
                    price = offer.get(field, offer.get("price"))
                    try:
                        numeric_price = float(price)
                        if not isfinite(numeric_price) or numeric_price <= 0:
                            raise ValueError()
                    except Exception:
                        issues.append(f"{label}: {field} missing or invalid")

                until_raw = str(offer.get("validUntil") or product.get("validUntil") or "")
                until = until_raw[:10]
                try:
                    end_date = datetime.strptime(until, "%Y-%m-%d").date()
                    if end_date < today_sa:
                        issues.append(f"{label}: offer expiry date has already passed")
                except Exception:
                    end_date = None
                    issues.append(f"{label}: validity end date missing/invalid")

                until_at = str(offer.get("validUntilAt") or product.get("validUntilAt") or "").strip()
                expiry_instant = None
                if until_at:
                    try:
                        expiry_instant = datetime.fromisoformat(until_at.replace("Z", "+00:00"))
                        if expiry_instant.tzinfo is None:
                            expiry_instant = expiry_instant.replace(tzinfo=ZoneInfo("Africa/Johannesburg"))
                        expiry_instant = expiry_instant.astimezone(ZoneInfo("Africa/Johannesburg"))
                        if expiry_instant <= datetime.now(ZoneInfo("Africa/Johannesburg")):
                            issues.append(f"{label}: exact offer expiry time has already passed")
                        if end_date and expiry_instant.date() != end_date:
                            issues.append(f"{label}: exact expiry instant does not match validUntil date")
                    except Exception:
                        expiry_instant = None
                        issues.append(f"{label}: exact expiry instant is invalid")

                start = str(offer.get("validFrom") or product.get("validFrom") or "")[:10]
                start_date = None
                if start:
                    try:
                        start_date = datetime.strptime(start, "%Y-%m-%d").date()
                        if end_date and start_date > end_date:
                            issues.append(f"{label}: start date is after end date")
                    except Exception:
                        issues.append(f"{label}: validity start date is invalid")

                valid_from_at = str(offer.get("validFromAt") or product.get("validFromAt") or "").strip()
                if valid_from_at:
                    try:
                        start_instant = datetime.fromisoformat(valid_from_at.replace("Z", "+00:00"))
                        if start_instant.tzinfo is None:
                            start_instant = start_instant.replace(tzinfo=ZoneInfo("Africa/Johannesburg"))
                        start_instant = start_instant.astimezone(ZoneInfo("Africa/Johannesburg"))
                        if start_date and start_instant.date() != start_date:
                            issues.append(f"{label}: exact start instant does not match validFrom date")
                        if expiry_instant and start_instant >= expiry_instant:
                            issues.append(f"{label}: exact start instant is not before expiry instant")
                    except Exception:
                        issues.append(f"{label}: exact start instant is invalid")

                provinces = offer.get("provinces") or product.get("provinces") or ["All"]
                allowed_provinces = {
                    "All", "Eastern Cape", "Free State", "Gauteng", "KwaZulu-Natal",
                    "Limpopo", "Mpumalanga", "Northern Cape", "North West", "Western Cape",
                }
                if not isinstance(provinces, list) or not provinces or any(p not in allowed_provinces for p in provinces):
                    issues.append(f"{label}: province scope is missing or contains an unknown region")

                source = offer.get("sourceUrl") or product.get("sourceUrl")
                source_id = offer.get("sourceId") or product.get("sourceId")
                source_evidence = offer.get("sourceEvidenceReference") or product.get("sourceEvidenceReference")
                has_registry_provenance = bool(str(source_id or "").strip() and str(source_evidence or "").strip())
                if not valid_https_url(source) and not has_registry_provenance:
                    issues.append(f"{label}: requires an HTTPS source URL or approved local-source registry ID plus evidence reference")
    if issues:
        print("Not published. Fix these review issues first:", file=sys.stderr)
        for issue in issues[:100]:
            print(f" - {issue}", file=sys.stderr)
        if len(issues) > 100:
            print(f" - plus {len(issues)-100} more issue(s)", file=sys.stderr)
        return 2

    # Evidence references are internal compliance records and must not leak into
    # the public feed. Keep the non-sensitive source ID/label for offer provenance.
    for product in products:
        product.pop("sourceEvidenceReference", None)
        for offer in product.get("stores") or []:
            offer.pop("sourceEvidenceReference", None)
            for more in offer.get("moreOffers") or []:
                more.pop("sourceEvidenceReference", None)
    data["approvalStatus"] = "verified"
    data["verifiedAt"] = datetime.now(timezone.utc).isoformat()
    data["reviewedBy"] = args.reviewed_by.strip()
    data["sourceRightsCheckedAt"] = data["verifiedAt"]
    data["sourceRightsCheckedBy"] = args.reviewed_by.strip()
    data["sourceRightsAttestation"] = "Reviewer confirmed a documented permission, licence, applicable source terms or legal basis for the source access and intended commercial extraction/display. This is a human attestation, not an automated legal opinion."
    data.pop("coverage_run", None)
    Path(args.output).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Published {len(products)} human-reviewed products to {args.output}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
