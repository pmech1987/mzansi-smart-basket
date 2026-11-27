# Mzansi Smart Basket — Continuation Worklog

Updated: 25 November 2026  
Iteration: 2 — page-level completeness, offer integrity, regional validity and private workflow hardening  
Baseline: `mzansi_smart_basket_master_plan_v1.zip` (which includes the legal-reviewed project and Volume 1 plan)  
Plan: `docs/MASTER_PLAN_VOLUME_1.md`

## Iteration 2 — changes completed in this source tree

### Extraction and coverage

- Replaced multi-page extraction batches with individually numbered, one-page units. PDF page enumeration fails closed if the page count cannot be read.
- Added an explicit priced-offer count to the structured extraction schema.
- Added a separate second-pass AI count-only audit for each page. A page is technically complete only when the extraction-reported count, number of extracted rows and second-pass count all match.
- Added `coverage_report.json` with source filename, page number, SHA-256 audit key, all three counts, status and cache state.
- Incomplete, truncated, malformed, quota-limited or count-mismatched pages are not cached as complete. Complete page cache uses a schema/prompt/model fingerprint; legacy cache data is rejected.
- Cache pruning occurs only after all enumerated pages finish successfully.
- The second count is another AI estimate, not an independently proven count. The report says so, and human verification remains compulsory.

### Offer correctness and retention

- Distinct offers from the same store are retained even where prices match, when dates, source pages, source files, campaign, loyalty or multi-buy terms differ. Exact duplicates alone are collapsed.
- Added `mergeAudit` counts for raw rows, represented offers, exact duplicates, expired rows, invalid prices, invalid expiries and missing names. Invalid rows block publication.
- Offer-level province scope is retained in primary and alternate offers instead of relying only on a product-wide union.
- The frontend now filters each offer by the selected province, promotes a current offer over an upcoming/expired primary, and hides expired alternates unless the shopper explicitly shows expired offers.
- Basket provenance lookup can identify the date/region of the specific alternate price previously selected.
- Publication validates each primary and `moreOffers` record, including price, source provenance, date, timestamp, timestamp/date consistency and known South African province scope.

### Expiry and app trust

- An exact clock time is stored only when printed. Date-only offers stay valid through the printed South African local calendar date and are labelled “exact time not stated”.
- Added in-app refresh scheduling at offer start/end boundaries and refresh on return to a foreground tab.
- Imported JSON files cannot self-assert verified status. External feed URLs remain unverified; only a same-origin feed may use the reviewed-feed badge. The offline feed cache is now version 3 and strips external self-asserted verification metadata before saving, preventing an external feed from appearing verified after a disconnect.
- Added executable frontend logic tests for alternate expiry, region filtering, upcoming offers, import trust and basket offer provenance.

### Source and workflow security

- Remote files are streamed rather than loaded into memory at once. A configurable 100 MB per-file ceiling is enforced by default and actual file signatures must identify a PDF, PNG, JPEG or WebP. Redirects remain disabled and HTTPS host approval remains exact.
- `APPROVED_SOURCES_JSON` can hold the source-rights register as a private GitHub Actions secret, overriding the empty repository template.
- Workflow requires the source repository to be private before handling source evidence or candidate files.
- Workflow cache is restored/saved through GitHub Actions cache so completed pages can resume after partial runs; candidates and coverage reports are delivered as short-lived workflow artifacts instead of being committed to the repository.
- `.gitignore` now excludes extraction cache, report, candidate and temporary files.

## Verification performed for Iteration 2

Commands:

- `python -m unittest discover -s tests -v` — **42 tests passed**.
- `node tests/test_frontend_logic.mjs` — **passed** (7 frontend logic scenarios).
- `python -m py_compile scripts/*.py` — passed.
- `node --check scripts/build-web.mjs` — passed.
- Extracted inline app script `node --check` — passed.
- JSON validation for `deals.json`, `approved_sources.json`, `manifest.json`, `capacitor.config.json` and `package.json` — passed.
- Workflow YAML parsed with PyYAML — passed.
- Main inline application JavaScript syntax check — to be recorded after the final packaging validation below.

These are offline/synthetic code checks. They do not demonstrate successful extraction from a real retailer pamphlet or approval under a retailer's legal terms.

## Status after Iteration 2

- **COMPLETE (synthetic/code evidence):** one-page PDF enumeration; page count reconciliation gate; complete-only page cache; offer merge retention and audit; per-offer publication checks; offer-specific province scope; streamed file-signature/size checks; private source registry secret override; frontend alternate-offer expiry and province selection; rejection of imported/external feed self-verification.
- **PARTIAL:** IndexedDB complete-feed persistence (code exists; full browser/device quota testing remains); exact-time handling (works when the source prints an exact time; many pamphlets publish only dates); AI page count audit (second AI pass exists but still needs manually labelled real-page benchmarking).
- **BLOCKED:** live ingestion. `approved_sources.json` still has an empty `sources` list. The workflow flags for remote downloads and Gemini document uploads default to `false`. No retailer source has been entered with documented commercial extraction and AI-processing rights.
- **UNVERIFIED:** native Android build, signed APK/AAB, device testing, production Cloudflare deployment, live Gemini API integration and actual retailer-price accuracy.
- **NOT STARTED / NEXT:** real pamphlet benchmark set; structured multi-buy pricing and quantity rules; product identity/variant matching benchmark; branch-level availability model; alerts; account/sync backend; retailer agreements; affiliate tracking; business revenue measurements.

## Next P0 work (Iteration 3)

1. Build a manually labelled benchmark from legally usable sample leaflets, including dense grocery grids, braai packs, chicken cuts/portions, butchery, gadgets/appliances and separate loyalty/variant prices. Record expected offer counts and offer-level ground truth for every page.
2. Test extraction recall, precision, product matching and price accuracy against that benchmark. A matching AI count is insufficient evidence that the right products/prices were extracted.
3. Implement explicit multi-buy fields (required quantity, bundle total, single-unit fallback and loyalty applicability) and basket arithmetic. Do not treat “2 for R50” as R25 per item when the shopper adds only one.
4. Validate regional scope and loyalty conditions from benchmark pages; include branch/stock caveats where sources permit.
5. Add safe source-specific URL path restrictions and DNS/IP egress controls before enabling remote downloads.
6. Test IndexedDB quota and recovery with a browser harness and large synthetic feeds; retain an explicit “full offline cache available / unavailable” status.
7. Install dependencies in a network-enabled environment, run `npm run build:web`, then create and test the native Android project on a real phone.
8. Obtain written/source-specific permissions or approved official feeds; keep Gemini uploads disabled until both source rights and AI processor terms are confirmed.

## Rules for future continuation

When the user says “Continue”, start from this newest project archive and worklog, inspect the actual code and tests again, choose the next concrete defect or coverage gap, implement it, add regression tests, re-run the relevant suites, update this worklog and create a new versioned bundle. Never claim that the app is live, complete, legally cleared or issue-free unless current evidence supports that claim.

## Iteration 3 — South African time-zone correctness and alternate-offer boundary handling

### Defects found and fixed

- **Device-timezone drift:** date-only validity was converted through the device's local timezone in parts of the UI. Date-only offer boundaries now resolve explicitly in South African Standard Time (UTC+02:00), independent of the phone's configured timezone. Invalid calendar dates are rejected.
- **Alternate-offer refresh gap:** the automatic boundary scheduler previously considered only the primary store offer. It now schedules start and end refreshes for every retained `moreOffers` record as well as the primary offer.
- **Mixed date/time inheritance:** an alternate offer with its own date-only start/end could accidentally inherit the primary offer's exact timestamp. Offer-specific dates and timestamps now take precedence, and a date-only alternate no longer inherits an unrelated primary timestamp. The same rule is used in catalogue decoration, basket provenance lookup and refresh scheduling.

### Verification performed after Iteration 3 changes

- `python -m unittest discover -s tests -v` — **42 tests passed**.
- `node tests/test_frontend_logic.mjs` — **passed; 10 frontend scenarios**, including SAST date boundaries, date-only expiry labels, alternate-offer start scheduling and alternate date/time precedence.
- `python -m py_compile scripts/*.py` — passed.
- `node --check scripts/build-web.mjs` — passed.
- All three inline script blocks extracted from `index.html` and passed `node --check` — passed.
- JSON validation — passed for `deals.json`, `approved_sources.json`, `manifest.json`, `capacitor.config.json` and `package.json`.
- Workflow YAML syntax parsed with PyYAML — passed.

### Current release status

- **COMPLETE (offline/code evidence):** fixes recorded in Iterations 2 and 3; current Python and frontend regression suites pass; SAST date-only boundaries and alternate offer timing are now tested.
- **PARTIAL:** complete-feed IndexedDB persistence is implemented but still needs browser quota, eviction and recovery tests on actual browsers/devices. The page-level second-pass AI count audit is a completeness signal, not ground truth; it needs a manually labelled, legally usable benchmark.
- **BLOCKED:** no source is approved in `approved_sources.json`; live pamphlet ingestion remains disabled by default. No real retailer PDF should be processed until the exact source and AI processor permissions/basis are documented.
- **UNVERIFIED:** real-world page extraction recall and price precision; Gemini API integration; npm production build; Cloudflare production deployment; Android Studio project generation, APK/AAB signing and physical-device behaviour; Google Play review; revenue or user retention.

### Next P0 engineering priorities

1. Implement structured multi-buy economics. Do not convert “2 for R45” into a R22.50 single-item price unless the offer and basket quantity satisfy the bundle condition. Store bundle quantity, bundle total, loyalty eligibility and any independently printed single-item fallback as separate fields. The basket must calculate exact totals or clearly mark the price as conditional/unknown; it must never invent a single-unit price.
2. Build a manually labelled, legally usable leaflet benchmark with dense grids, butchery, chicken portions, braai packs, appliances, electronics, apparel and small promotional blocks. Measure offer recall, precision, product identity accuracy and price accuracy by page/category.
3. Add product/variant matching safeguards (brand, pack size, cut/grade, model number and quantity) so unlike products are not compared as equivalent.
4. Stress-test the IndexedDB path with large synthetic feeds, quota failures, eviction and offline recovery; expose whether the saved snapshot is complete.
5. Install dependencies in a network-enabled environment, run `npm run build:web`, then produce and test the Android build. These tasks have not been completed in this environment.
