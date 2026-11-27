# Price-feed review and complete-page coverage workflow

AI extraction is a candidate-generation aid, not proof that a price is correct or that the source may be used commercially. The extractor writes `deals_pending_review.json` and never changes the public `deals.json` feed. Each input PDF is enumerated and processed as individual pages. Images are treated as single-page inputs.

## 1. Approve the exact source first

`approved_sources.json` is an empty-by-default template. In GitHub Actions, the private `APPROVED_SOURCES_JSON` secret overrides the file so licence references and agreement identifiers do not need to be committed to source history. The source repository must be private while this workflow processes source records, pamphlets, cache or unpublished candidates. A source entry is eligible only when all of the following are present and confirmed by an operator:

- a unique `source_id` and descriptive `label`;
- `status: "approved"`;
- a permitted `permission_basis` value;
- a private `evidence_reference` to the agreement, licence, source terms or legal advice;
- `reviewed_by` and `reviewed_at`;
- `allow_commercial_data_extraction: true`;
- `allow_ai_document_upload: true`;
- for remote retrieval, the exact HTTPS host and `allow_remote_download: true`.

The pipeline distinguishes source access, commercial extraction/display, remote downloading and transfer of the original document to Gemini. They are not interchangeable permissions. A free printed leaflet, a publicly reachable PDF, or an OCR capability is not automatically a commercial-use or third-party-AI-processing licence.

For a locally supplied PDF, register the exact filename under `files`. For a remote direct PDF/image URL, register the exact hostname under `hosts`, add the direct file URL to `pamphlet_urls.txt`, and enable the matching workflow flags only after checking the source-specific terms. Remote downloads are streamed, limited to 100 MB per file by default (configurable using `MAX_SOURCE_FILE_MB`), and checked for PDF/image signatures. This is a per-file resource guard, not an item/page/pamphlet count cap. Broad crawling of third-party catalogue websites is not included. Redirects are disabled; do not bypass access controls or automate a site whose terms disallow this use.

## 2. Page-by-page extraction and audit

The extractor uses one page as the unit of work. For every page it records the file name, one-based page number, SHA-256 fingerprint, extraction status, extracted row count, extraction-reported count, second-pass AI audit count and cache status.

A page is considered technically complete only when all three counts agree:

1. the extraction response's `page_priced_offer_count`;
2. the number of extracted offer records;
3. a separate second-pass AI visual count using a different prompt and a count-only schema.

A truncated response, parse error, quota failure, count mismatch, failed page enumeration or missing second-pass count marks the page incomplete. Such pages are not cached as complete. A legacy cache without the current versioned audit schema is invalidated and reprocessed. The extractor preserves successfully completed pages so later runs can resume without silently treating a failed page as complete. GitHub Actions stores the page cache using the cache service and uploads the candidate plus coverage report as a private, short-lived workflow artifact; it does not commit the private cache or candidate into repository history.

**Important limitation:** the second-pass count is another AI estimate, not an independent human count or mathematically guaranteed computer-vision measurement. It can still miscount a dense or unclear page. A real pamphlet benchmark with manually labelled page totals and offer rows is required before claiming exhaustive accuracy. The operator must still inspect the actual source page. A matching count does not prove that the extracted product names, prices, pack sizes or conditions are correct.

## 3. What the extraction must capture

For each visible offer, review:

- exact product name, brand, variant and pack size/model;
- every separately priced variety, combo, multipack and loyalty-card tier;
- ordinary price, card/member price, multi-buy terms, quantity limits and unit price;
- valid-from and valid-until dates, region/province and participating-branch restrictions;
- an exact start/end clock time only when it is explicitly printed;
- exact source file, source page, source registry ID/label and authorised source URL where one exists.

Do not invent a time. If a pamphlet gives a date but no clock time, the app says **exact time not stated** and treats the printed end date as inclusive through that South African local calendar date. If an exact `validUntilAt` is printed, the app uses that timestamp. This is an operational interpretation, not a promise that stock remains available until that instant; retailer stock and branch availability can differ.

The merge layer retains distinct same-store offers even when their prices are identical, provided their source, campaign, dates, card or conditions differ. Only exact duplicates across the recorded offer identity are collapsed. It reports raw, represented, exact-duplicate, expired, invalid-price, invalid-expiry and missing-name counts. Invalid rows make the merge audit incomplete and block publication.

## 4. Inspect the coverage report

Every run writes `coverage_report.json`. Check:

- `status` is `complete`;
- `pagesComplete` equals `pagesTotal`;
- `pagesIncomplete` and `unreadChunks` are zero;
- `expectedOfferCount` equals `extractedOfferCount`;
- `offerCountAuditComplete` is true;
- every page record says `complete` and contains both count values;
- the candidate's `mergeAuditComplete` is true, with zero invalid price, invalid expiry and missing-name rows.

A report with status `blocked_ai_upload_disabled` or `blocked_no_approved_sources` means extraction did not run. It is not a successful zero-offer run. An incomplete report must never be treated as evidence that the pamphlet contained no more offers.

## 5. Review and publish

1. Open the private source document and `deals_pending_review.json`.
2. Use the `sourceFile` and `sourcePage` fields to inspect the exact page for every offer.
3. Compare product identity, price, pack size, card terms, multi-buy wording, validity, geography and branch restrictions.
4. Check that distinct offers from the same retailer have not been combined incorrectly.
5. Check the page-level coverage report and merge audit. Investigate every mismatch and every failed page.
6. Confirm the source registry evidence covers the access method, intended commercial extraction/display, and AI document transfer.
7. Correct or remove each inaccurate offer. Do not mark an offer verified merely because both AI count passes agree.
8. Run the publication command only after all required checks:

```bash
python scripts/publish_reviewed_deals.py --reviewed-by "YOUR REVIEWER NAME" --i-have-checked-every-offer --i-have-confirmed-source-rights
```

The publisher refuses a candidate without a full page-level audit, a matching count, a clean merge audit, a valid price, an unexpired validity date, a usable HTTPS URL or approved local-source registry provenance, and both human acknowledgements. Private `sourceEvidenceReference` values are stripped before writing the public feed; the non-sensitive source ID/label and page provenance remain.

The script is a workflow safeguard, not legal advice or automated proof of price truth. The person publishing remains responsible for the final checks.

## 6. Run the regression tests and workflow

Before any ingestion run, use:

```bash
python -m unittest discover -s tests -v
node tests/test_frontend_logic.mjs
python -m py_compile scripts/*.py
```

The GitHub workflow also checks that the repository is private, restores the audited page cache, runs both Python and frontend tests, extracts only when the explicit workflow variables are enabled, saves completed-page cache state even when a run is incomplete, and uploads `coverage_report.json` plus `deals_pending_review.json` as a short-lived workflow artifact. If the workflow is blocked because the source registry is empty or AI uploads are disabled, that is not a successful zero-offer extraction.
