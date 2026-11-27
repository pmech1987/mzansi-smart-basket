# Mzansi Smart Basket

A South African retail-specials comparison and shopping-basket web app, with a Capacitor 8 Android wrapper setup.

## Important data status

The included `deals.json` and embedded 75-item starter catalogue are **demonstration data**, not verified current retailer prices. They should not be presented as live offers. The app now marks demo and unreviewed feeds clearly. The extraction pipeline writes `deals_pending_review.json`; it never overwrites the public `deals.json` automatically.

## Main project files

- `index.html` — current app UI and browser logic.
- `deals.json` — public feed (currently a starter/demo catalogue).
- `scripts/extract_pamphlets.py` — one-page-at-a-time extraction from exact approved local files and explicitly approved remote PDF/image sources; it performs a separate second-pass AI count audit, validates source file signatures/size, and uses a versioned complete-only cache.
- `scripts/publish_reviewed_deals.py` — publication gate requiring complete page coverage, a clean merge audit, exact/dated expiry checks, price review and a source-rights attestation.
- `approved_sources.json` — empty-by-default source permission and AI-upload register.
- `docs/PRICE_REVIEW_WORKFLOW.md` — source approval, page-level coverage, count reconciliation and publication workflow.
- `tests/test_frontend_logic.mjs` — executable browser-logic tests for offer expiry, province filtering and feed trust.
- `docs/CONTINUATION_WORKLOG.md` — current completed, pending, blocked and unverified work.
- `coverage_report.json` — generated after an extraction run; reports blocked, incomplete or complete processing status and per-page results.
- `docs/ANDROID_SETUP.md` — create and run the Android project.
- `docs/DEPLOY_CLOUDFLARE_PAGES.md` — publish the web version and connect your domain.
- `docs/LEGAL_AND_BUSINESS_SA.md` — South African launch and copyright checklist.
- `docs/OWNER_SETUP_CHECKLIST.md` — account ownership, CIPC and asset-transfer steps.
- `terms.html`, `privacy.html`, `price-methodology.html` — draft user-facing policies; complete the placeholders before public launch.

## Build offline-ready web assets

Requires Node.js 22+ and npm:

```bash
npm install
npm run build:web
```

The compiled site is written to `www/`. Deploy `www/` as the Cloudflare Pages build output directory. The build replaces runtime Tailwind/Font CDN loading with local CSS and local Lucide assets so the UI can render offline after install/cache.

## Android

Read `docs/ANDROID_SETUP.md`. Create the native Android project with `npm run cap:add:android`, add location permissions as documented, then sync/open in Android Studio. This source package does not include a signed Play Store release binary.

## Security

Keep the source repository private while it contains retailer pamphlet PDFs/images, source-rights records, unpublished candidates or extraction cache. The scheduled workflow checks repository privacy before running. Store `GEMINI_API_KEY` and the JSON source-rights registry in GitHub Actions Secrets (`GEMINI_API_KEY`, `APPROVED_SOURCES_JSON`); configure remote download and AI upload switches as repository variables only after confirming the relevant rights. Never expose API keys or private agreement references in app code or the Android binary. Original PDFs/images are uploaded to Gemini only when the exact source record and AI processor terms permit it. See `docs/LEGAL_AND_BUSINESS_SA.md`, `docs/AI_MODE_LEGAL_RESEARCH_REVIEW.md` and `approved_sources.json` before enabling source processing.


## Price feed publishing safety

The bundled `deals.json` is demo content and is visibly labelled as unverified. The AI extractor writes `deals_pending_review.json`; it does not overwrite the public feed. The extractor uploads original PDF/image documents to Gemini only when enabled and covered by the exact source record; this is disabled by default. It is not local-only OCR. Broad catalogue-site crawling is not included. Local approved PDFs may be published using their private source-registry provenance even when no public HTTPS URL exists; the private evidence reference is stripped from the public feed.

For an approved source, compare every offer against the permitted source and confirm both price accuracy and source rights, then publish only after review with:

```bash
python scripts/publish_reviewed_deals.py --reviewed-by "YOUR NAME" --i-have-checked-every-offer --i-have-confirmed-source-rights
```

The second acknowledgement is a human attestation that the operator has checked the source-access and commercial-use basis. This command is a workflow guard, not proof of accuracy or a legal opinion. Keep `deals_pending_review.json`, original pamphlets and API keys out of a public repository.

## Iteration 2 coverage and data-integrity changes

The extractor now treats each page as a unit and checks the extracted row count against an explicit extraction count and a separate second-pass AI count. A match is a technical completeness gate, not proof of 100% recall; manually labelled real pamphlets remain required. Primary and alternative offers retain separate dates, times and province scopes. The app filters expired and out-of-region alternatives and does not allow imported or external JSON feeds to mark themselves verified. Remote files are streamed with a 100 MB configurable per-file ceiling and signature checks.

The workflow uses Actions cache for resume state and private workflow artifacts for candidate/report files; it no longer commits internal cache and unpublished candidates into repository history. Run local checks with:

```bash
python -m unittest discover -s tests -v
node tests/test_frontend_logic.mjs
python -m py_compile scripts/*.py
```

See `docs/CONTINUATION_WORKLOG.md` for the current status and next P0 work.

## Latest continuation status (Iteration 3)

The current source tree includes SAST-based date-only offer boundaries and refresh scheduling for primary and alternate offers. An alternate offer's own date-only validity no longer inherits an unrelated primary exact timestamp. The latest offline verification recorded 42 Python tests and 10 frontend logic scenarios passing. Live source ingestion remains blocked until `approved_sources.json` contains a reviewed source and the workflow secrets/variables are configured; no real pamphlet coverage or price accuracy is claimed. See `docs/CONTINUATION_WORKLOG.md` for the completed, partial, blocked, unverified and next-priority items.
