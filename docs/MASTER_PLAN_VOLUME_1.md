# Mzansi Smart Basket
## Master Product, Business, Legal and Engineering Plan
### Volume 1 — Product foundation, exhaustive coverage, source governance and launch architecture

**Project:** Mzansi Smart Basket  
**Plan version:** 1.0 — Volume 1  
**Research cut-off:** 25 November 2026  
**Jurisdiction:** Republic of South Africa  
**Status:** Foundational master plan; implementation and legal sign-off remain outstanding  
**Long-form target:** 200,000 words across a controlled series of volumes. This file is Volume 1, not the entire 200,000-word programme.

---

# 0. How this master plan is organised

This is a working product specification and operating plan, not a promise that the current app already performs every function described here. It defines what Mzansi Smart Basket is intended to become, what the existing project actually contains, what must change, how the data will move through the system, how the business can earn revenue, and what evidence is required before launch.

A 200,000-word plan is too large to deliver responsibly as one undivided document. The full programme is therefore divided into ten volumes, with a target of approximately 20,000 words per volume. The target is a planning goal, not a word-count quota that should cause repetition or filler.

| Volume | Subject | Main outcome |
|---|---|---|
| 1 | Product foundation, exhaustive coverage, source governance and launch architecture | Establishes the whole system and its non-negotiable rules |
| 2 | South African legal research and source-rights operating manual | Source-by-source legal decision framework, contract checklist, takedown process and compliance register |
| 3 | Pamphlet intake, OCR, AI extraction and page-level completeness engine | Detailed ingestion design, queue logic, audit process, retry model and extraction schemas |
| 4 | Product catalogue, offer data model and price-comparison algorithms | Matching, variants, unit pricing, multi-buy maths, price history and basket optimisation |
| 5 | User experience and complete feature specification | Every screen, interaction, filter, accessibility rule and shopper workflow |
| 6 | Backend, database, API, cloud architecture and security | Production architecture, deployment, data storage, secrets, access control and resilience |
| 7 | Testing, quality assurance, monitoring and operational playbooks | Test catalogue, coverage metrics, incident response and release gates |
| 8 | Company ownership, finance, monetisation and retailer partnerships | CIPC, IP, accounts, cost model, revenue strategy and commercial agreements |
| 9 | Android, Google Play, growth, support and marketing | Capacitor delivery, store listing, beta testing, acquisition and customer service |
| 10 | Full technical specification and implementation backlog | Detailed schemas, APIs, acceptance criteria, migration plan and prioritised build programme |

## 0.1 Rules for future continuation

When the project is continued, the next iteration must start from the newest supplied project ZIP and this master plan. It must inspect the real files rather than rely on old summaries. For every continuation cycle:

1. Inventory the current project and compare it with the plan.
2. Run existing tests and record actual results.
3. Inspect for missing requirements, defects, security issues, legal-risk controls, silent limits and confusing user experiences.
4. Select the next coherent improvement set.
5. Change the actual source files where implementation is requested and feasible.
6. Add or update tests for every changed behaviour.
7. Run the tests and clearly distinguish passing checks from checks not run.
8. Update the plan, changelog and work ledger.
9. Package the changed project with a new version number and provide it.

“Continue” means resume this process from the latest artefact. It does not mean repeat the previous answer, add random code, inflate file size, or claim that a project has no remaining defects. The goal is continuous measurable improvement. No software can honestly be declared permanently issue-free.

---

# 1. Executive direction

## 1.1 The product in one sentence

**Mzansi Smart Basket is an independent South African shopping-information and price-comparison platform that turns authorised, current retail offers into a complete, searchable, comparable shopping catalogue and helps households build the most useful basket for their budget, location and shopping conditions.**

It is not intended to be a digital photocopy of retailer pamphlets. It is not intended to invent prices, pretend that every retailer is covered, or imply that an advertised item is in stock at a particular branch when that has not been verified.

## 1.2 The problem it solves

South African shoppers often need to compare multiple retailers, multiple pamphlets, loyalty-card prices, regional promotions, pack sizes and special conditions. The information is spread across printed leaflets, retailer websites, retailer apps, authorised feeds and store-specific promotions. A shopper may have to search several sources to answer simple questions:

- Where is the cheapest comparable pack of chicken portions this week?
- Which shop has the best braai pack for the quantity and quality advertised?
- Is the advertised price a normal price or a loyalty-card price?
- Is the deal available in Mpumalanga, Gauteng or only a specific region?
- Does the offer end tonight, on Friday, or at the end of the pamphlet period?
- Is the “2 for R50” offer actually cheaper per item than buying a different pack elsewhere?
- Can the shopper buy everything at one store, or will a split basket still save money after transport costs?
- Are gadgets, appliances, clothing, household products, personal care, pet products and other non-food specials included as well as groceries?

Mzansi Smart Basket should reduce this work by bringing the relevant information into one interface and showing the evidence, conditions and freshness of each offer.

## 1.3 What success looks like

The app succeeds when a shopper can:

1. Find an offer without knowing the exact catalogue or pamphlet it came from.
2. See all offers currently loaded from the app's declared, authorised source universe—not an arbitrary sample.
3. Understand which retailer, region, branch conditions, loyalty requirements and dates apply.
4. Compare like-for-like products without confusing different sizes, brands, variants or multipacks.
5. Build a basket, compare one-store and multi-store strategies, and account for travel or delivery costs.
6. See when information was last checked and whether the price is independently verified.
7. Report an error and receive a correction or status update.
8. Use the core shopping features on a low-cost Android phone and on a slow or intermittent connection.

The business succeeds when it can maintain accurate and lawfully sourced data, build repeat usage, control operating costs, establish retailer relationships and generate sustainable revenue without compromising ranking integrity or user trust.

## 1.4 The core promise

The product promise is **complete processing of every in-scope authorised pamphlet and every price-bearing offer in it, with visible proof of what was processed and what remains incomplete**.

That promise must be precise. It cannot honestly mean “every deal at every retailer in South Africa” unless the company has a reliable and authorised way to discover the complete universe of retailer promotions. The system can promise exhaustive treatment of the sources it has registered, received, lawfully accessed and successfully processed. It must separately disclose when a retailer has not provided a current source or when a source is unavailable.

---

# 2. Non-negotiable product rules

These rules apply to the interface, extraction engine, database, workflow, commercial model and future developers.

## 2.1 No arbitrary content caps

There must be no hidden business rule such as:

- Stop after the first 12 pamphlet PDFs from a source.
- Stop after the first 20 images from a retailer page.
- Extract only the first 50, 75, 100, 500 or 1,500 offer names.
- Ignore later pamphlet pages because the first pages look sufficient.
- Exclude braai packs, chicken portions, small corner deals, gadgets or non-food categories to reduce work.
- Keep only the cheapest offer and discard other valid offers from the same store.
- Publish only the first page of valid results while implying the rest do not exist.

The original project notes identified hidden discovery caps of 12 PDFs and 20 images per site in the old crawler. They also identified a 75-item demonstration catalogue. Those are precisely the types of behaviours the new system must prevent or label honestly.

The reviewed project has a separate display behaviour that initially renders up to 100 results and provides “load more” and “show all” controls. That is a presentation/performance mechanism, not necessarily a data-extraction cap. It must nevertheless be redesigned so a shopper cannot mistake the first rendered page for the entire catalogue. The total result count, page count and navigation state must always be visible.

## 2.2 Resource limits must queue work, not delete work

There are legitimate technical limits: API quotas, runtime windows, response-token limits, file-size security checks, memory, network interruptions and hosting quotas. The solution is resumable processing, not silently ignoring content.

A resource limit may pause a job. It must not convert unfinished work into a “complete” result. Every outstanding pamphlet, page and chunk must remain in a persistent queue with a status and retry reason. The next worker run must resume from the first unfinished unit.

Examples:

- If a workflow has 45 minutes available and 120 pages remain, process as many pages as are safe in that run, save checkpoints, mark the remaining pages as pending, and resume later.
- If an AI API returns a quota error, record the exact page/chunk that failed, keep the previous valid public feed, and retry after quota reset or through a permitted alternative processing route.
- If one page is too dense for one model response, split the work by page or extraction batches. Do not truncate silently.
- If a file exceeds a safe upload limit, report the exact file, size and reason; allow a controlled local processing path or a permitted chunked path. Do not pretend it was processed.

A performance optimisation is acceptable only if it preserves access to all relevant data and provides a complete route to retrieve it.

## 2.3 No fabricated offers

The application must never create a real-looking retailer offer from sample data, a model guess, a previous price, a common market price or a likely promotion.

If the source is missing, unclear, illegible or inaccessible, the offer must be marked as missing evidence or sent to review. A price can be blank or withheld; it must not be invented.

## 2.4 No false completeness claims

The interface must distinguish:

- **Source universe:** Which retailers and source endpoints are registered and expected.
- **Source discovery:** Which current pamphlets or offer feeds were actually found or received.
- **Page coverage:** Which pages of each pamphlet were processed.
- **Extraction completeness:** Whether the system found every price-bearing offer visible on each processed page.
- **Verification completeness:** Whether extracted offer details were checked against the source.
- **Publication status:** Whether the checked offers are live, pending, rejected, expired or withdrawn.

A green “complete” indicator must not mean only that the Python script exited with code 0. It must mean all defined completeness checks passed for the stated source set.

## 2.5 Facts, sources and artwork must be treated separately

The app should normally publish independently structured factual offer fields—such as product name, pack size, price, offer dates, loyalty condition and region—rather than copied pamphlet pages. It must not assume that the source's photographs, logos, artwork, layout or curated selection can be reproduced merely because the source document is free to view.

The extraction method does not create rights. OCR, AI vision, manual typing, a user upload or a publicly reachable PDF does not automatically grant the company commercial reuse permission.

## 2.6 A retailer price is not a stock guarantee

The app must separate:

- Promotion advertised by the source.
- Promotion validity period.
- Branch participation, where known.
- Stock availability, where independently confirmed.
- Price confirmed at checkout, which only the retailer can ultimately confirm.

A valid pamphlet is evidence of an advertised offer for its stated period. It is not proof that stock remains at a specific branch. The product must say “advertised offer; branch stock not confirmed” unless live stock information is authorised and reliable.

## 2.7 Never mislead about affiliation or ranking

Retailer names may be used to identify the source of a comparison offer, subject to honest and legally reviewed use. The app must not suggest that Shoprite, Checkers, Boxer, Pick n Pay, SPAR or another retailer owns, sponsors, approves or endorses Mzansi Smart Basket unless a written agreement says so.

Sponsored placement must be labelled. Payment must not secretly change the “cheapest” calculation or hide a better deal.

## 2.8 Preserve evidence and history

Every live offer must retain internal provenance: source record, document identifier, page number, date imported, extraction version, reviewer, review date, source-rights record, and the original observed offer values. Public display may expose a concise source citation without exposing restricted source files.

---

# 3. Existing project audit: what is actually present

This section distinguishes inspected project facts from future recommendations.

## 3.1 Original supplied project

The original `mzansi_v15.zip` project expands to a directory named `mzansi-v9-final`. That version contains a PWA-style application with:

- `index.html` — the main user interface and much of the browser logic.
- `deals.json` — the offer feed, containing a 75-item starter/demo catalogue.
- `scripts/extract_pamphlets.py` — the original Python extractor.
- `.github/workflows/update-prices.yml` — scheduled extraction workflow.
- `sw.js` — service worker/offline cache.
- `manifest.json` — PWA manifest.
- `tests/test_extractor.py` — a small extractor test suite.
- `pamphlets/README.txt` — instructions for placing source files in a folder.

The older workflow scheduled extraction twice daily, used Gemini Vision, included browser-based discovery, and committed changes to the feed. The old extractor had a hard-coded two-page chunk size, and the user's notes identified the hidden 12-PDF and 20-image discovery limits. The old source list included third-party catalogue portals such as Guzzle, Kaufino and LatestSpecials. That approach created both a coverage problem and a source-rights problem.

The original feed describes itself as a starter catalogue. It cannot be considered evidence that the listed prices are current retailer offers.

## 3.2 Legal-reviewed project package

The latest inspected package, `mzansi_smart_basket_legal_reviewed_v2.zip`, includes the following additions:

- `approved_sources.json` — source register, empty by default.
- `scripts/publish_reviewed_deals.py` — human publication gate.
- Updated extractor and tests.
- Terms, privacy and price-methodology draft pages.
- Capacitor 8 configuration and Android setup notes.
- Cloudflare Pages deployment guide.
- Company ownership and legal/business notes.

The current source register is empty. The public `deals.json` still contains 75 demonstration offers, explicitly labelled as examples and unverified. Therefore this package is a safer development base, not a live, complete retailer catalogue.

## 3.3 Verified test state for the legal-reviewed package

I ran the package's automated tests in the inspected environment on 25 November 2026. The result was:

- 14 tests passed.
- Python scripts compiled successfully.
- The JavaScript build script passed Node syntax checking.
- The native bridge passed Node syntax checking.

The tests cover synthetic examples including size parsing, expired-offer removal, multiple offers from one store, 3,000 records, remote URL host approval, source-rights registry requirements, publication acknowledgements, expiry rejection, incomplete-coverage refusal and non-finite price rejection.

These are useful unit tests. They do **not** prove that an actual Shoprite, Boxer or Pick n Pay multi-page pamphlet has been fully extracted. They do not prove that Gemini will never omit an offer. They do not prove Android Studio has generated and built an APK. They do not establish any retailer's permission. They do not test every screen or device size.

## 3.4 Current code gaps that the plan must close

The current reviewed project still has important gaps:

1. **No real authorised sources are configured.** The source registry is empty, so the pipeline cannot produce a live retailer feed.
2. **The public catalogue is demo data.** The 75-item feed must remain clearly marked until replaced with verified offers.
3. **No actual page-by-page count audit is implemented in the reviewed extractor.** The extraction prompt tells the AI to count, but a prompt is not a reliable independent audit.
4. **A two-page PDF chunk is not proof of completeness.** A valid JSON response can omit items without being truncated.
5. **The current offer schema stores dates but no precise item-level end time.** The current expiry helper compares dates only. It can leave an offer active for the entire end date and treats a missing or malformed end date as not expired.
6. **An offer with no valid end date can remain active indefinitely unless a separate publication rule rejects it.** The publication gate should require a validated date policy.
7. **The current main UI is a large monolithic `index.html`.** This is workable for a prototype but makes future development, regression testing and accessibility more difficult.
8. **The category list is narrower than the product ambition.** It includes core groceries and gadgets/clothing but does not yet represent every desired department such as liquor, health/pharmacy, pet care, home/garden, toys/stationery and other retail categories.
9. **The app's 100-item rendering window is not clearly enough distinguished from catalogue completeness.** It provides “load more” and “show all”, but the experience should make total matched results and page state clearer.
10. **There is no proven retailer branch-stock integration.** The app must not make stock claims based only on a pamphlet.
11. **There is no evidence of a complete device and Play Store release test.** Capacitor setup is prepared, but a native Android build still needs to be created and physically tested.
12. **There is no production operations dashboard.** Source freshness, page coverage, review queues, error rates, expiry jobs and user corrections need a proper view.
13. **The legal documents are templates.** They need real company identity, contact details, purpose, data retention rules, operators, user rights and legal review before publication.
14. **The current Gemini route uploads whole source files.** It is disabled unless enabled, but a future local OCR option should reduce third-party document transfer where practical. Local processing does not remove copyright or source-rights obligations.
15. **Build reproducibility needs strengthening.** The package should commit a package lockfile, pin supported dependency ranges, run security updates and use repeatable CI builds.

These findings become implementation requirements in later volumes.

---

# 4. Target shopper experience

## 4.1 Core navigation

The app should have a simple bottom or side navigation that can grow without overcrowding the screen:

1. **Discover** — all current offers with search, categories, filters and sorting.
2. **Compare** — direct product comparison between retailers.
3. **My Basket** — quantities, budget, substitutions, store split and shopping checklist.
4. **Pamphlets & Sources** — current pamphlet coverage, source dates, page coverage and source links, without copying restricted pages.
5. **Saved** — regular purchases, favourites and watched products.
6. **Alerts** — price drops, selected category alerts and expiry reminders.
7. **Account / Settings** — region, language, accessibility, privacy, notification controls and optional account features.

For an initial release, some of these can be tabs within the existing app rather than separate native screens. The structure should still be planned so features are not bolted onto a single giant render function.

## 4.2 Discover screen

The Discover screen is the main catalogue. It should show:

- Number of active offers in the current selected area.
- Number of stores represented.
- Number of current pamphlets received and processed.
- Data freshness, such as “Updated 25 Nov at 14:15 SAST”.
- Clear verified/unverified/source-warning labels.
- Search input with spelling tolerance and common South African product names.
- Category filters.
- Store filters.
- Province/region filters.
- Validity filters: ending today, ending tomorrow, ending this week, longer-running, date unclear.
- Offer-type filters: weekly special, multi-buy, loyalty price, clearance, flash offer, appliance deal and other categories.
- Sorts: lowest comparable unit price, cheapest shelf price, largest verified saving, most stores, recently updated, ending soonest, alphabetical.

Search must include product synonyms and normalised names. For example, a shopper might search “chicken pieces”, “chicken portions”, “mixed portions”, “drumsticks” or a brand. The system should return relevant results without merging distinct products into a false match.

## 4.3 Complete results and user-visible pagination

The Discover and Compare results must never silently stop at 100. A page may render a finite number for performance, but the page must display:

- “143 matching offers”.
- “Showing 1–50 of 143”.
- A next/previous control or reliable infinite scrolling.
- A search/filter count after every filter change.
- A “show all” or export function where performance permits.
- An indicator when the server has not delivered all pages.

Virtualisation is a display optimisation, not a reason to omit offers from the source database. The application must not change its total count to the visible count.

## 4.4 Product detail

Every product detail should display:

- Product name, brand, variant and exact pack size.
- Product category.
- Every current offer record for the selected product identity.
- Retailer name in plain text.
- Shelf/standard price.
- Loyalty/card price and required membership.
- Multi-buy condition in its original form and a correctly calculated comparable value.
- Unit price when pack data is sufficient.
- Offer start and end date/time.
- Region, province or branch restriction.
- Source title, source page and source timestamp.
- Human review state and last checked time.
- Availability note: “Advertised offer; branch stock not confirmed” unless stock data is authorised and current.
- Report a correction button.

If there is a “was” price, it must be captured only when the source actually states it and must not be confused with Mzansi Smart Basket's historical observed price. A previous observed price and a retailer's advertised “was” price are two different data fields.

## 4.5 Basket and shopping optimiser

The basket is one of the app's strongest features and should become reliable before the company invests heavily in decorative extras.

Users should be able to:

- Add products and set quantities.
- Select a specific store offer.
- Compare the cheapest single-store basket.
- Compare a multi-store basket.
- Include estimated transport costs, delivery charges and optional travel time.
- Set a total budget.
- Mark items as already bought or not required.
- Substitute equivalent products only when equivalence is clear.
- See the savings difference between strategies.
- Share or print the shopping list.
- Keep a private regular-shopping list on the device without requiring an account.

The optimiser must not split a basket purely on sticker price. It should include travel/delivery costs and the user's selected constraints. A R20 saving that requires an expensive extra journey should not be portrayed as an unquestionable saving.

## 4.6 Price alerts and history

Later releases should support:

- Watch a product and alert when a verified price falls below a chosen amount.
- Alert when a watched offer is about to expire.
- Show a product's observed offer-price history.
- Distinguish observed price history from a retailer's claimed regular/was price.
- Let users choose which categories, stores and regions they care about.
- Let users turn off marketing alerts while keeping service alerts, where technically and legally appropriate.

Do not promise a price history before enough dated observations exist. Display “history starts on [date]” rather than fabricating earlier values.

## 4.7 Helpful additional features

Prioritise features that solve real shopping tasks:

- Barcode scan to identify a product or find a matching offer.
- Shopping-list sharing between household members.
- Pantry staples / repeat-purchase reminders.
- Price-per-kilogram, litre, unit, 100 g or 100 ml calculations.
- Regional offer filters.
- Loyalty-card price explanation.
- “Why is this deal ranked first?” explanation.
- User-reported correction workflow.
- Data-saver mode and offline cached catalogue.
- Clear low-data image policy: do not download product images if the app can work with a text-first display.
- Accessible text sizes, screen-reader labels and high contrast.
- English, isiZulu and Afrikaans initially; later expand through reviewed translations rather than machine-only text.

Avoid collecting unnecessary personal information. A shopper should be able to browse and create a local basket without creating an account.

---

# 5. Exhaustive pamphlet and offer coverage system

This is the most important technical and trust requirement.

## 5.1 Define the source universe before claiming completeness

The app needs a maintained inventory of retailers and their source channels. Potential source groups include:

**Food and general retailers:** Shoprite, Checkers, Usave, Boxer, Pick n Pay, SPAR, Woolworths Food, Makro, Game, OK Foods, Cambridge Food, Food Lover's Market and other authorised local retailers.

**Health and personal care:** Clicks, Dis-Chem, pharmacies and personal-care retailers, subject to source terms and relevant product restrictions.

**Clothing and household:** PEP, Ackermans, Mr Price, Jet, clothing outlets, homeware, furniture and appliance retailers.

**Building, hardware and garden:** Builders, hardware stores, garden centres and other stores that publish promotional catalogues.

The names above are targets for source onboarding, not a statement that every retailer has granted permission or provides a usable feed. Each source must be individually researched and registered.

For each retailer the source inventory must record:

- Store identity and aliases.
- Official corporate site.
- Official app or digital offer page, if any.
- Current pamphlet or offer source endpoint.
- Whether the source is public, partner-only or privately supplied.
- Whether commercial extraction is permitted.
- Whether automated download is permitted.
- Whether AI document upload is permitted.
- Whether local OCR is permitted.
- Whether derived offer facts may be cached and republished.
- Whether product images or logos may be displayed.
- Region or branch scope.
- Last terms review date.
- Permission expiry/review date.
- Contact/contract evidence reference.
- Current source status: pending, approved, suspended, expired or rejected.

## 5.2 Source access and legal permission are separate fields

A source register must not have one generic `approved=true` flag. It must distinguish at least the following permissions:

1. View/open a source.
2. Download or receive a source file.
3. Process it with local OCR.
4. Upload it to an external AI processor.
5. Extract structured factual offers for commercial use.
6. Store/copy the extracted fields in a commercial database.
7. Display the extracted fields to users.
8. Store a source copy for audit/retention.
9. Display source photographs or logos.
10. Use an affiliate link or retailer API.

These permissions may have different answers. For example, a document could be publicly viewable but not licensed for automated downloading, external AI transfer or commercial aggregation. A retailer may permit offer facts to be displayed in an affiliate feed but prohibit saving or reusing images.

Each permission requires a basis, evidence and a review date. A source record is an operational control, not a legal opinion.

## 5.3 Allowed source pathways

The preferred source order is:

1. A direct written retailer agreement or official API/feed that covers the proposed fields and uses.
2. An approved affiliate feed whose terms explicitly permit price comparison, caching, presentation and required attribution.
3. A retailer-supplied PDF/image or direct official document with written permission or legal-reviewed terms for the proposed extraction and processing.
4. A physical pamphlet supplied by an authorised partner under a documented arrangement.
5. A user-contributed source only when contribution terms, user authority, rights review and moderation rules are established. User upload alone is not proof of permission.
6. Other sources only after source-specific legal review.

Do not make uncontrolled crawlers that discover all PDFs and images on a third-party catalogue portal. A third-party catalogue website may have its own protected compilation and terms. If an aggregator provides a permitted API or written licence, record those permissions and use the API within its scope.

## 5.4 Complete coverage is measured at four levels

### Level A — Source coverage

Did the system find or receive every expected active source document in its declared source inventory?

Example status for one retailer:

- Official source endpoint checked at 06:00 SAST.
- Current pamphlet for 24–30 November received.
- Two additional campaign leaflets received.
- No current appliance catalogue found.
- One source unavailable or blocked.

The app must not hide a missing source. It should show “No authorised current pamphlet received” rather than generate sample offers.

### Level B — Page coverage

How many pages are in every source document? Was every page queued, processed or marked as a documented failure?

A 24-page PDF must have 24 explicit page records. A page cannot disappear because it was blank, mostly visual, rotated, corrupt or difficult to read. If a page truly contains no priced offers, it must still have an audit status saying that it was inspected and no offer was found.

### Level C — Extraction coverage

For each page, how many separately priced offer units were observed, and how many structured offer records were extracted?

The extraction audit should count each separately priced product variant. A single visual card that offers four pack sizes at four prices represents four offer records. A multi-buy offer is one offer with a purchase condition and calculation, not a reason to delete the original deal wording.

A model's own count is not independent proof. Use at least two separate checks where practical:

- A dedicated page-count pass that counts price-bearing items.
- A separate extraction pass that returns every offer record.
- A consistency comparison between expected and extracted counts.
- A visual or human check on every mismatch and a risk-based sample of matching pages.

For the strict complete-coverage claim, any unexplained count mismatch means **GAP**, not complete. The earlier v16 notes proposed a 3% tolerance; this master plan rejects that tolerance for the user's “every item” requirement. A 3% missing-item allowance is still missing items. A counting tool can itself miscount, so exact count equality should be supported by an independent review process, not treated as infallible.

### Level D — Publication coverage

How many extracted offers passed identity, price, date, region, condition and rights checks? Which remain pending? Which were rejected? Which are expired?

The system must not call the entire data run complete while it has unread pages, unexplained count gaps or unreviewed prices. It may publish a partial data set only if the UI states clearly that coverage is partial and does not imply all pamphlets have been included. The safer default is to keep the previous verified feed until the new complete reviewed snapshot is ready.

## 5.5 Page-by-page extraction strategy

A reliable process should work at the page level or small, resumable page batches:

1. Register the pamphlet and create a durable `pamphlet_id`.
2. Validate the source permission record.
3. Download or import the source through the authorised route.
4. Record file name, source URL, retrieval time, file size, media type and SHA-256 hash.
5. Check for malware and malformed/corrupt files.
6. Count PDF pages or image pages.
7. Create a record for every page.
8. Detect page rotation, scan quality, text layer and image density.
9. Run local text extraction where possible.
10. Run OCR for image-only or difficult text.
11. Use a permitted vision/AI provider only where the source record allows external processing.
12. Extract all item-level offers from each page.
13. Preserve the source page number and bounding-box or region reference internally where practical.
14. Run a separate price-bearing-item count audit.
15. Reprocess gaps at smaller granularity, including page-level extraction.
16. Create a pending review package.
17. Have a reviewer confirm the extracted values and source basis.
18. Publish an immutable verified feed snapshot.

A two-page chunk may be a useful performance default, but it must not be treated as the completeness mechanism. Dense meat, grocery and appliance pages should be capable of being split into one-page or sub-page regions. The processing engine should select the smallest unit needed to preserve all entries.

## 5.6 Every category must be included

The extraction prompt, schema and QA tests must not over-focus on groceries. The target catalogue includes at minimum:

- Staples, grains and maize meal.
- Meat, poultry, braai packs, chicken portions, beef, pork, lamb, mince and processed meat.
- Fish and seafood.
- Dairy, milk, yoghurt, cheese, eggs and butter.
- Bakery and bread.
- Fruit and vegetables.
- Pantry items, tins, sauces, oils and spices.
- Snacks, sweets, cold drinks and other beverages.
- Household and cleaning.
- Personal care and baby.
- Health and pharmacy, subject to applicable restrictions.
- Pet food and pet supplies.
- Home, garden and outdoor products.
- Toys, stationery and school products.
- Gadgets, electronics, appliances and accessories.
- Clothing, footwear and textiles.
- Liquor and age-restricted products only after separate legal/age-marketing review.
- Other specials and mixed bundles.

Category is a label, not a filter that removes an item. If the classifier is unsure, retain the offer under “Other / Needs classification” and let a human classify it later.

## 5.7 Braai packs and meat offers need special handling

Meat and poultry offers often contain conditions that make naive comparison misleading. Capture:

- Whether the meat is fresh, frozen, chilled, marinated or processed.
- Cut and portion type.
- Bone-in or boneless where specified.
- Pack weight or weight range.
- Price per pack, per kilogram or “from” price.
- Whether the pack is fixed-weight or variable-weight.
- Whether it is a multi-buy or combo.
- Whether the offer is limited to a particular day, branch, region or stock quantity.
- Whether the offer requires a loyalty card.

A 5 kg mixed chicken portions pack must not automatically be matched to a 5 kg bag of drumsticks or a pack of chicken wings. A braai pack is a product bundle; its contents must be recorded where shown, and only comparable to another bundle when the contents and weights are sufficiently similar.

## 5.8 Gadgets and appliances need a different comparison model

For appliances and gadgets, capture:

- Brand, model number and exact model variant.
- Capacity, wattage, screen size, storage, RAM, dimensions or other relevant specification.
- Warranty period if printed.
- Included accessories.
- Cash price, finance condition or loyalty price.
- Model-specific discount conditions.

Do not match two products merely because both are called “air fryer” or “television”. Model identity is critical. If specs are missing, show the offer as a separate product with limited comparability.

## 5.9 Expiry rules

Each offer must have an item-level validity interval, not just the overall pamphlet end date.

Required fields:

- `valid_from_local`.
- `valid_until_local_date`.
- `valid_until_local_time` if printed.
- `timezone` (use `Africa/Johannesburg` for South African retail offers).
- `validity_source` (explicit item text, pamphlet header, official feed, human-confirmed, or unclear).
- `expiry_confidence`.

Rules:

- If the offer itself prints a special end time, use that exact time.
- If no time is printed but the end date is clear, define end-of-day in South African local time as the technical display convention, and label it as such. Do not tell the shopper a specific retailer time was printed when it was not.
- If an item has a shorter flash period than the main pamphlet, use the item's shorter validity period.
- If the date is missing, unreadable or contradictory, do not invent a seven-day period. Set `expiry_status=unknown` and keep the offer out of the verified active catalogue until reviewed.
- A file name can help prefill dates but should not override conflicting printed source information without a reviewer decision.
- Expired offers must become inactive at their true expiry instant, not merely on the next nightly extraction.
- The client must also hide or label expired offers when a stale cached feed is opened offline.

The earlier proposed automatic seven-day validity window is not accepted for verified public offers. It can make an unverified offer look current after its real end date.

## 5.10 Quota and retry model

Use a persistent work queue with fields such as:

- `job_id`, `source_id`, `pamphlet_id`, `page_id`, `chunk_id`.
- `status`: queued, running, complete, gap, failed, quota_wait, rights_blocked, review_required.
- `attempt_count`, `next_attempt_at`, `last_error`.
- `processor`, `model_version`, `prompt_version`.
- `started_at`, `finished_at`, `duration_ms`.
- `sha256`, `output_version`.

Failed pages stay in the queue. The workflow should be idempotent: rerunning a completed, unchanged page should use a valid cache; changing the source hash or extraction prompt version should invalidate the relevant result. A changed prompt must not silently reuse old extraction output as if it had been produced by the new prompt.

Do not log only the first 10 errors and forget the rest. The user-facing summary may show the first 10 for readability, but the full machine-readable report must retain every page error.

## 5.11 Publish an atomic snapshot

A partial run must not overwrite the last good feed. The pipeline should:

1. Build a candidate data snapshot.
2. Verify schema and offer counts.
3. Check every required page status.
4. Check every offer status and source-rights record.
5. Run duplicate, date, price and identity checks.
6. Have a reviewer approve every candidate or a controlled group with an auditable process.
7. Generate a versioned release file.
8. Atomically switch the public feed pointer to the new version.
9. Keep a rollback pointer to the last approved snapshot.

If one page is unread, the candidate snapshot can still be stored for review but must be labelled partial and must not replace a complete approved feed as though it were complete.

---

# 6. Offer data model and comparison rules

The current flat JSON feed is useful for a small PWA prototype, but the production model should separate the product identity from individual retail offers.

## 6.1 Core entities

### Retailer

A retailer is a store brand or chain. Fields include retailer ID, public display name, aliases, official domain, support contact if relevant, affiliate status, permitted logo/image display flag, and legal/source contact.

### Retail location

A physical branch or area served by a retailer. Fields include branch ID if supplied, retailer ID, name, address, coordinates where authorised, province, town, branch-specific offer participation and stock freshness. Do not invent branch IDs or stock status.

### Source

A source is an authorised data origin: retailer feed, retailer PDF, licensed partner portal, user-contributed document under accepted terms, or another counsel-approved origin. It has the separate permissions defined in Section 5.2.

### Pamphlet / campaign

A source document has a title, retailer, campaign type, issue dates, region, file hash, page count, source location and access record.

### Page

Every page has a status, page hash, extraction result, count audit, image quality metadata, and review status.

### Product identity

Represents the actual thing being sold. Fields include canonical name, brand, GTIN/barcode when available, model number, category, variant, flavour/colour, size, unit, package quantity and matching confidence.

### Offer

A time- and retailer-specific promotion for a product. It contains the source, product identity, price, conditions, region, loyalty rules and validity interval.

### Offer observation / price history

A dated observation that records what the source showed at a particular time. A new flyer should create a new observation rather than destroy the historical record.

### Review event

A reviewer action with reviewer identity, timestamp, decision, corrections and rationale.

## 6.2 Product identity and duplicate prevention

The product matching engine must prefer exact identifiers:

1. Barcode / GTIN, if available and valid.
2. Manufacturer model number for electronics/appliances.
3. Brand + exact product name + exact quantity + exact variant.
4. A normalised text match with human confirmation when needed.

Do not merge products merely because the names look similar. Examples:

- 2 kg chicken thighs vs 2 kg mixed chicken portions.
- 2 L full-cream milk vs 2 L low-fat milk.
- 1 kg frozen chips vs 1 kg fresh potatoes.
- Air fryer model A vs air fryer model B.
- 6-pack of 330 ml cans vs 2 L bottle.

The matching engine should store a `match_confidence` score and a `match_reason`. Low-confidence matches stay separate until reviewed.

## 6.3 Price fields

An offer should support:

- `regular_price`.
- `advertised_price`.
- `loyalty_price`.
- `loyalty_program`.
- `multi_buy_type`.
- `multi_buy_quantity`.
- `multi_buy_total`.
- `price_range_min` and `price_range_max` for “from” or variable-weight offers.
- `deposit_or_fee` where applicable.
- `unit_price_value` and `unit_price_unit`.
- `currency=ZAR`.
- `price_basis` (per item, per kg, per 100 g, per litre, per pack, per service, etc.).

Never label a loyalty price as the universal price. Never convert “2 for R50” to R25 each without retaining the two-item purchase condition. The app can calculate an effective per-unit comparison, but it must display the original condition.

## 6.4 Unit-price normalisation

For compatible products:

- Convert kg to g and L to ml for storage precision.
- Compare by a standard unit such as R/kg, R/100 g, R/L, R/100 ml or R/item.
- Keep exact original pack size and original offer text.
- Do not compare products where quantity or content is unknown.
- Do not imply that price per kilogram alone means identical quality or product type.

Examples:

- 2 kg maize meal at R35 = R17.50/kg.
- 1.5 L oil at R42 = R28/L.
- 6 × 330 ml cooldrink at R45 = 1.98 L total, but a multipack may still be a different shopping choice from a single 2 L bottle.
- 2 for R50 means R25 per unit only when the customer buys two and the items are indeed the same eligible unit.

## 6.5 Price difference and savings

For comparable offers, show:

- Rand difference between the lowest and highest observed comparable offer.
- Percentage difference relative to a clearly stated baseline.
- Unit-price difference where possible.
- Whether the comparison includes a loyalty-card condition.
- Whether the promotion applies to the shopper's selected province.

Avoid vague “save 40%” labels unless the source states a valid reference price and the app can support the calculation. A price drop from last week's observed price is not automatically the retailer's advertised saving.

## 6.6 Multiple offers from one store

Keep every distinct valid offer record. If a store has two concurrent offers for the same product through different pamphlets or conditions, store both. The UI may highlight the cheapest qualifying offer, but the other valid offers must remain available through the details view or “all offers” list.

Do not collapse everything into a single store price if the date windows, branch scope, loyalty eligibility or multi-buy conditions differ.

---

# 7. South African legal and compliance framework

**Important:** This is product-planning research, not legal advice. The exact collection method, source agreements, commercial scale, user-generated content, advertising and pricing claims should be reviewed by a South African intellectual-property/commercial attorney before public launch.

## 7.1 Retailer pamphlets are free to receive, not automatically free to reuse

Your argument is commercially understandable: retailers publish and distribute pamphlets to advertise specials and encourage customers to visit. A comparison app can potentially help retailers reach shoppers who want to see those specials. That is a sensible basis for a partnership pitch.

However, the fact that a retailer gives away a printed pamphlet or publishes a free PDF does not, by itself, grant every recipient a broad commercial licence to copy the pamphlet, its photographs, artwork, design or a substantial part of its compiled selection into another business.

The legal analysis separates several things:

- Individual factual information, such as one price, product name or date.
- Original text or wording.
- Photographs and artistic works.
- Logos and trade marks.
- The pamphlet's design and layout.
- The original selection and arrangement of a compilation.
- The source website's terms and access restrictions.
- The method and scale of extraction.
- The proposed use, monetisation and external processing.

The safer model is to independently structure relevant offer facts in Mzansi Smart Basket's own format, avoid reproducing creative artwork, avoid bulk copying another publisher's curated database, keep source provenance, and obtain permission or legal advice for the actual source and processing method.

## 7.2 Copyright Act 98 of 1978

The current copyright framework is the Copyright Act 98 of 1978, as amended and in force. The Act's definition of literary work includes tables and compilations, including data stored in a computer or computer-associated medium. This matters because a collection of retail offers or prices may involve more than isolated individual facts.

In *National Soccer League t/a Premier Soccer League v Gidani (Pty) Ltd* [2014] ZAGPJHC 33, the court considered copyright protection in fixture lists and compilations. It discussed the collection/arrangement of information and found the relevant fixture lists protectable. It is not a supermarket pamphlet case, but it is a warning against assuming that all commercial compilations are free to copy simply because the entries are factual.

A lower-risk design is:

- Do not reproduce entire pamphlet pages.
- Do not crop or reuse price-tag graphics or product photographs.
- Do not copy the source layout, distinctive design or branding.
- Store only the facts needed to compare offers, where the extraction and compilation itself has a valid legal basis.
- Do not copy an entire third-party catalogue site's selection as a shortcut to building your own dataset.
- Keep evidence of independent compilation and source provenance.
- Ask counsel to review how much of a particular source's compilation is being used and the applicable licence/exception.

The quotation or fair-dealing exceptions are not a universal commercial database licence. Attribution is useful, but attribution alone does not make a use lawful.

## 7.3 Copyright Amendment Bill status as at 25 November 2026

The Constitutional Court handed down *Ex parte President of the Republic of South Africa: In re Constitutionality of the Copyright Amendment Bill and the Performers' Protection Amendment Bill* [2026] ZACC 26. The Court's order held that certain referred provisions, including the proposed fair-use provision in section 12A, were not unconstitutional on the grounds referred to it, while declaring the specified educational exceptions in section 12D(1)–(5) unconstitutional. The judgment did not itself turn the entire Bill into an operative Act.

A report dated 20 November 2026 describes the Department of Trade, Industry and Competition briefing Parliament on outstanding intellectual-property reforms and indicates that the Bill requires further work following the Constitutional Court findings. The Parliamentary bill page still displays a historical “sent for assent” stage dated 29 February 2024; that status page should not be treated as proof that the post-judgment Bill has become law.

For the product, the operating rule is simple: **do not rely on proposed fair-use amendments as though they are already in force.** Use the existing Copyright Act as the baseline until an attorney confirms the relevant Act has been assented to, gazetted and commenced. Re-check the Gazette and Parliament status immediately before launch and during periodic legal reviews.

## 7.4 Trade Marks Act 194 of 1993

Retailer names are often needed to tell shoppers where an offer is advertised. The Trade Marks Act contains provisions dealing with bona fide descriptive use, but that does not grant a general right to use logos, brand artwork or presentation that implies sponsorship or approval.

Product rules:

- Use retailer names in ordinary text to identify the source of an offer, after legal review.
- Do not use official retailer logos unless licensed.
- Do not create a retailer-branded app header that makes the app look official.
- Do not imitate a retailer's website, app or pamphlet layout.
- Do not use a retailer's trade mark in the Mzansi brand name or app icon in a way likely to imply affiliation.
- Display a clear non-affiliation statement.
- If the retailer grants written permission, follow its exact approved brand-use rules.

## 7.5 Consumer Protection Act 68 of 2008

The Consumer Protection Act addresses misleading and deceptive marketing, including representations about price and specific price advantages. For a price-comparison service, the most important product controls concern accuracy, context and disclosure.

The app must disclose or preserve:

- Exact product identity and pack size.
- The actual price field being compared.
- Whether a loyalty card is required.
- Whether the offer is a multi-buy.
- Start and end dates.
- Regional and branch restrictions.
- Known exclusions and quantity limits.
- Whether stock availability is confirmed.
- When the offer was last checked.

A disclaimer does not cure a false price or misleading representation. If an offer is wrong, expired, regionally restricted or subject to a condition that the app omits, users may be misled even if the footer says to check with the retailer.

The product should have a prominent correction/report feature and a documented process for quickly suspending disputed offers.

## 7.6 Electronic Communications and Transactions Act 25 of 2002

Section 86 addresses intentional access to data without authority or permission, and related interference with data. This does not mean every automated request or all scraping is automatically a criminal offence. The exact source terms, authorisation, access controls and conduct matter.

The company should not:

- Bypass authentication, CAPTCHA, paywalls or technical controls.
- Reuse private or undocumented app endpoints without authorisation.
- Circumvent rate limits or access restrictions.
- Treat a `robots.txt` file as a commercial licence.
- Treat a publicly accessible URL as proof of permission to extract and republish commercially.

A `robots.txt` check is one operational signal; it is not a replacement for reading terms and obtaining rights. Conversely, the absence of a robots.txt block does not create a commercial extraction licence.

If the company sells subscriptions or other services through an electronic transaction, ECTA's applicable online supplier disclosure requirements should be reviewed and reflected in the website/checkout flow, including the correct supplier identity, legal status, contact details, price and terms where applicable.

## 7.7 POPIA and personal information

The core catalogue consists of retail offer information, not personal information. However, the app may process personal information when it stores accounts, email addresses, phone numbers, device IDs, precise location, shopping behaviour linked to a user, loyalty-card numbers, support tickets or user-uploaded material containing personal details.

Design for data minimisation:

- Browsing should work without a user account.
- Let users choose a province manually.
- Ask for location permission only when needed and explain why.
- Prefer approximate area/province use over storing precise GPS coordinates.
- Keep local baskets on the device unless the user explicitly enables cloud sync.
- Do not collect loyalty-card numbers unless a clearly explained feature requires them.
- Avoid storing payment card data; use a compliant payment provider if paid subscriptions are introduced.
- Do not use user shopping lists to target advertising without a reviewed lawful basis and clear disclosure.

The business must identify its responsible party, register its Information Officer, maintain a privacy notice, define retention periods, manage operator agreements and implement reasonable technical and organisational security measures. Where a third party processes personal information for the company, the operator relationship and instructions must be documented.

Section 22 of POPIA requires notification of security compromises to the Information Regulator and affected data subjects as soon as reasonably possible where the statutory conditions apply. The Information Regulator's 2025 fact sheet says there is no low-risk threshold that excuses reporting. The incident-response plan must therefore be ready before collecting meaningful user data.

Section 69 regulates direct marketing by unsolicited electronic communications. Do not use purchased contact lists or send marketing email/SMS/push campaigns without a reviewed consent and opt-out model. The customer exception has conditions and should not be treated as blanket marketing permission. Keep service alerts and promotional marketing distinct.

Section 72 governs transfers of personal information outside South Africa. If data is sent to overseas infrastructure or an AI processor, confirm the appropriate transfer basis and contractual protections. Do not assume that because an AI service is useful, user or uploaded data may automatically be transferred to it.

## 7.8 Advertising and affiliate disclosures

Paid placements must be distinguishable from ordinary comparison results. The Advertising Regulatory Board's current social-media appendix recognises clear identifiers such as `#Ad`, `#Advertisement` and `#Sponsored` for paid social content. The exact requirements depend on the channel and format, but the product rule should be to label paid placements clearly wherever they appear.

Recommended labels:

- “Sponsored” for paid placement.
- “Affiliate link” when Mzansi may earn commission from a click or purchase.
- “Retailer promotion” only where the retailer has commissioned the placement.

The app's default “cheapest” ranking must be computed from qualifying prices, not sponsor payments. A sponsored offer may appear in a clearly separated sponsored area, but must not masquerade as the unbiased cheapest offer.

## 7.9 User uploads and crowdsourcing

Allowing shoppers to upload pamphlet photos or till slips may help coverage, but creates additional risks:

- The uploader may not own or control the rights in the document.
- A till slip may contain personal information, loyalty identifiers or payment-related data.
- A photo may include people, house interiors or unrelated personal information.
- The company may receive illegal, harmful or infringing material.
- A user's warranty cannot automatically cure the source-rights issue.

If user uploads are introduced, design a restricted upload process with a clear permission statement, redaction guidance, malware scanning, private storage, automatic deletion schedule, moderation and takedown process. Till-slip processing should initially redact or discard customer and payment identifiers and extract only the minimum offer/price evidence necessary.

## 7.10 Legal operating gate

A retailer/source must not be activated merely because a developer places its URL into a configuration file. A person responsible for legal/source approval must check and record:

- Exact document or endpoint.
- Current terms and date checked.
- Rights holder or licensor.
- Access method.
- Commercial extraction permission or advice.
- AI processor transfer permission, if applicable.
- Display/caching/retention rights.
- Geographic and duration scope.
- Logo/image rights, if any.
- Contact for complaints or permission withdrawal.

If the answer is uncertain, the source stays `pending_review` and is not used for commercial publication.

---

# 8. Technology architecture and implementation direction

## 8.1 Do not rewrite everything before proving the data engine

The existing PWA has a useful foundation. A full rewrite before the extraction and data-quality process is proven would create extra work and new defects. The recommended sequence is:

1. Stabilise source intake and price correctness.
2. Establish an auditable page-level extraction queue.
3. Establish a reliable product/offer schema.
4. Improve the existing interface so complete results are visible.
5. Refactor the monolithic front end into manageable modules.
6. Add a production database and admin/review dashboard when the data volume justifies it.
7. Finish and test Capacitor Android after the web experience is stable.

## 8.2 Current prototype architecture

The current package is predominantly a static PWA:

- One main HTML/JavaScript interface.
- A JSON catalogue/feed.
- A Python extraction script.
- GitHub Actions for scheduled processing.
- A service worker for offline caching.
- A Capacitor 8 wrapper prepared for Android.

This is suitable for an early, low-cost pilot with a small number of authorised sources and a controlled reviewer. It is not yet an ideal long-term system for hundreds of pamphlets, thousands of pages, high-frequency source updates and a public correction workflow.

## 8.3 Recommended staged architecture

### Stage 1 — controlled pilot

- Keep the PWA/static JSON feed.
- Keep the extraction worker separate from the customer-facing app.
- Store private source files outside the public web root.
- Use GitHub Actions only as a scheduled/triggered job runner while volume remains manageable.
- Use GitHub Secrets for API credentials.
- Publish only reviewed feed snapshots.
- Keep the approved source registry in version control without embedding confidential contracts or credentials.

### Stage 2 — growing catalogue

Introduce:

- Managed PostgreSQL database for retailer, source, pamphlet, page, product, offer, review and price history.
- Private object storage for permitted source documents and page images.
- A durable job queue for page-level extraction.
- A review/admin console.
- A read API or generated public feed for the customer application.
- Background expiry and freshness jobs.
- Monitoring and alerting.

A managed PostgreSQL service such as Supabase can be considered because the original project already referenced Supabase environment variables, but the decision must compare cost, data location, operator terms, backup, access control and scale. Alternatively, a Cloudflare-oriented design using Workers, D1, R2 and Queues can be evaluated. Do not operate two competing backends without a reason.

### Stage 3 — production scale

Separate the system into clear services or modules:

- Source registry/admin.
- Document intake.
- OCR and text extraction.
- Vision/AI extraction.
- Page count audit.
- Product matching.
- Offer validation.
- Human review.
- Publication service.
- User-facing catalogue API.
- Alerts and notifications.
- Analytics and revenue reporting.

Each service should have a narrow responsibility and clear logs. The project should not turn into one oversized script with dozens of unrelated responsibilities.

## 8.4 Suggested repository structure

A maintainable future repository may use a structure such as:

```text
mzansi-smart-basket/
  apps/
    web/                    # customer web/PWA application
    android/                # Capacitor Android project after generation
    admin/                  # internal review and source management console
  services/
    ingestion/              # source imports and file validation
    extraction/             # OCR, AI extraction and page audit
    catalogue/              # identity matching and offer normalisation
    publication/            # release validation and feed publishing
    expiry/                 # scheduled offer status updates
  packages/
    schemas/                # shared product/offer JSON schemas
    pricing/                # unit price and comparison rules
    ui/                     # shared UI components
  data/
    fixtures/               # synthetic and rights-cleared test fixtures only
  docs/
    MASTER_PLAN_V1.md
    legal/
    operations/
    api/
  tests/
    unit/
    integration/
    end_to_end/
    fixtures/
  .github/workflows/
  package.json
  package-lock.json
```

This is a target structure, not a claim that all these folders exist today.

## 8.5 No secrets in the front end

Gemini keys, database service-role keys, signing keys and private feed credentials must never be placed in:

- `index.html` or bundled JavaScript.
- Public JSON files.
- The Android application package.
- A public GitHub repository.
- Screenshot/demo recordings.

Use server-side secrets and least-privilege credentials. Rotate credentials if they are accidentally exposed. The Android app should call a controlled backend endpoint rather than embed a private AI API key.

## 8.6 Build and deployment

Cloudflare Pages can host the static app. Its current documentation lists 500 builds per month on the Free plan, one concurrent build, a 20-minute build timeout, up to 20,000 files and a 25 MiB maximum asset size on that plan. This is enough for a small static site, but it does not mean the entire backend, database, AI processing or storage is free.

The plan should keep:

- A staging deployment.
- A production deployment.
- A rollback procedure.
- A versioned public feed.
- A build log and deployment ID.
- A source-map or error-reporting approach that does not leak secrets.
- Environment-specific API endpoints.

The source repository should have reproducible dependency installation and an audited lockfile.

## 8.7 Android through Capacitor

The reviewed package prepares Capacitor 8. Current Capacitor environment documentation states Node.js 22 or higher, Android Studio 2025.2.1 minimum for Capacitor 8, and Android SDK platform API 24 or higher; API 36 is currently identified as the latest stable SDK in the documentation retrieved for this plan.

Required release process:

1. Install Node.js 22+ and Android Studio.
2. Install the Android SDK and required build tools.
3. Install project dependencies from the committed lockfile.
4. Build the local web assets.
5. Add or synchronise the Android platform.
6. Review Android manifest permissions.
7. Test on multiple physical devices, including a low-cost phone and a current Android phone.
8. Test offline mode, app resume, feed updates, notification permissions and location permission denial.
9. Generate a signed Android App Bundle (AAB).
10. Store the app signing key and recovery process securely.
11. Complete Play Console declarations and testing requirements.

Do not call the Android app finished merely because `npx cap add android` works. A successful sync is not a release build, and a release build is not proof that the app behaves correctly on a real phone.

For new personal Google Play developer accounts created after 13 November 2023, Google currently requires a closed test with at least 12 testers opted in continuously for at least 14 days before the developer can apply for production access. Organisation account requirements and verification should be checked before choosing the account type.

## 8.8 Offline support and feed freshness

The PWA should allow shoppers to use previously loaded data offline, but it must mark the feed as cached and show the last successful update time. The app must calculate expiry locally using the proper timezone and must not show a stale offer as current just because the phone is offline.

A cached feed should retain its release version, `generated_at`, `verified_at`, source coverage summary and data age. The interface should distinguish:

- Online and current.
- Online but stale.
- Offline using a cached verified snapshot.
- Offline using unverified/demo data.
- No data available.

---

# 9. Review, publication and customer trust

## 9.1 AI is an extraction assistant, not an authority

The AI system is useful for reading dense pamphlet pages, identifying products and structuring price data. It can still:

- Miss a small price in a corner.
- Confuse R9.99 with R99.99.
- Attach a price to the wrong product.
- Miss a footnote or a loyalty-card condition.
- Misread a date or year.
- Merge two distinct pack sizes.
- Infer a price range as a single price.
- Return valid JSON with incomplete content.

Therefore a successful AI response is only a candidate record. It is not a verified offer.

## 9.2 Reviewer workflow

The internal review screen should display the source page (only to authorised reviewers), the candidate offer fields and the extracted region/coordinates. Reviewers should be able to:

- Confirm the offer.
- Correct product name, brand, size, price or date.
- Add or correct conditions.
- Split a wrongly merged variant.
- Merge duplicate offer identities only when justified.
- Mark an offer unreadable.
- Reject an invalid or unsupported price.
- Mark a source-rights issue.
- Escalate unclear legal questions.

Each decision must be auditable. A bulk approval feature may be added only when the source, extraction method and review protocol justify it; reviewers should not be forced to click hundreds of repetitive acknowledgements without seeing the content.

## 9.3 Publication gate

Before an offer can enter the public verified feed, the system must require:

- A source with a current, approved permission record.
- Successful extraction and required page coverage.
- Product identity review.
- Price review.
- Offer dates and timezone review.
- Conditions and region review.
- No unresolved high-severity flags.
- Reviewer identity and timestamp.

The publication script must fail closed. An unknown field should not become a verified field merely because the script has no validation rule for it.

## 9.4 Consumer correction and takedown

Provide a visible link to report:

- Wrong price.
- Expired deal.
- Wrong region.
- Wrong pack size or product.
- Missing loyalty requirement.
- Retailer says offer is not valid.
- Trademark, copyright or source concern.
- Privacy/security concern.

Every report should create a ticket with timestamp, offer ID, source ID, reporter details only if volunteered, severity and action status. High-risk price errors can automatically hide an offer while awaiting review. Copyright/rights complaints should be escalated promptly and recorded.

## 9.5 Public transparency page

A public methodology page should explain:

- How offers are sourced.
- What “verified” means.
- How often source coverage is checked.
- How dates and loyalty prices are handled.
- Why stock is not guaranteed.
- How users can report mistakes.
- How sponsored and affiliate placements are labelled.
- That the service is independent unless a retailer agreement says otherwise.

Do not expose confidential permission agreements, private source files, API keys, reviewer personal information or internal security details.

---

# 10. Feature roadmap: build what shoppers actually need

The feature list is organised by priority, not by how impressive a feature sounds.

## 10.1 Launch-critical features

- Complete authorised pamphlet inventory.
- Page-by-page extraction and count audit.
- Exact offer-level dates and end-of-day semantics.
- Clear data freshness and verification labels.
- Complete catalogue with reliable search and filters.
- Correct product matching and unit price.
- Price comparisons and savings calculations.
- Basket building and quantity editing.
- Province/region selection.
- Expiry and stale-feed handling.
- Source and methodology display.
- Report/correction function.
- POPIA-ready privacy and security baseline.
- No sample prices presented as live.

## 10.2 High-value second wave

- Product price alerts.
- Price history.
- Barcode scanning.
- Shopping-list sharing.
- Household multiple-user lists.
- Store location and travel planning.
- Local branch offer support.
- Better multilingual interface.
- Voice search, if it is reliable and accessible.
- Export/share basket.
- Personal regular-shopping templates.

## 10.3 Later options

- Meal planning based on verified specials.
- Pantry and expiry reminders.
- Budget coaching and household spend summaries.
- Retailer-sponsored coupon placement.
- Retailer dashboard for offer submission and error correction.
- Retailer feed/API integrations.
- Business analytics based on properly aggregated and lawfully processed data.

## 10.4 Features that should not be rushed

- User accounts and social profiles before they are necessary.
- Storing loyalty-card numbers centrally.
- Open public uploads without rights and moderation controls.
- Automated scraping of mobile apps or private endpoints.
- A chatbot that answers price questions from stale or unverified content.
- Paid premium tiers before users demonstrate repeat value.
- Artificial “live” claims when feeds are updated only once a day.

---

# 11. Business model and money plan

## 11.1 The revenue question

The app can earn money, but no income is guaranteed. A price-comparison platform usually needs repeated traffic and user trust before advertising or affiliate revenue becomes material. The first phase may earn nothing while the owner pays for domain, legal review, AI processing, storage, development and support.

Do not plan personal finances around projected app revenue until real usage and revenue data exist.

## 11.2 Revenue streams

### Affiliate referrals

A retailer or affiliate network may pay for qualified clicks or purchases. Each programme must be reviewed for allowed price display, comparison, link handling, attribution, data refresh and disclosure requirements. Do not assume a retailer affiliate link permits reproduction of the retailer's brochure.

### Advertising

Display ads can create revenue after users arrive. Start with non-intrusive placements. Do not let ads interrupt comparison or obscure the price. Track consent, privacy and advertising policy requirements. The ad network's use of data must be understood and disclosed.

### Sponsored placements

Retailers may pay for a campaign placement or promotional highlight. Label it clearly as sponsored. Never manipulate the ordinary cheapest-price ranking or hide competitors because a retailer paid.

### Premium features

Possible premium features include advanced price alerts, extensive price history, household shared lists or export tools. Keep basic product search and price comparison useful for free users; otherwise the app loses the audience it needs to create value.

### Retailer tools

A future business-to-business product could allow authorised retailers to submit offers, correct data, see aggregate offer performance or sponsor campaigns. This may provide a more direct revenue path than relying only on consumer ads.

## 11.3 Unit economics

Every month, track:

- Active users.
- Weekly returning users.
- Search sessions.
- Basket creation rate.
- Affiliate click-through rate.
- Confirmed affiliate commission.
- Ad revenue per thousand impressions (where available).
- Sponsored campaign revenue.
- Premium conversion and churn.
- Cost per processed source page.
- Cost per published offer.
- Hosting/database/storage cost.
- Error reports per 1,000 offers.
- Review time per 100 offers.

Monthly net contribution should be measured as:

`affiliate revenue + advertising revenue + sponsorships + subscriptions - source-processing costs - hosting/storage - payment fees - support - compliance - other operating expenses`.

The company should know the cost of processing one pamphlet and maintaining one active offer. If the cost of producing accurate data exceeds the income it can reasonably generate, the source pipeline or revenue model must change.

## 11.4 Cost categories

Budget for:

- Domain registration and renewal.
- Website hosting.
- Database and object storage.
- OCR and AI API usage.
- Backups and monitoring.
- Google Play registration and testing devices.
- Android signing and release support.
- Company registration and annual filings.
- Accountant and tax support.
- Legal advice and retailer permission agreements.
- Advertising and user acquisition.
- Customer support and correction handling.

A free hosting tier does not mean the whole service is free. The data pipeline, AI page processing and human review can become the dominant expenses.

## 11.5 Keep ranking independent

The comparison engine must be transparent. A paid retailer should not automatically be shown as cheapest. The user should be able to select “lowest total price”, “lowest unit price”, “one-store basket” or another clear criterion. Sponsored content should sit outside or clearly alongside the unbiased ranking.

---

# 12. Company, ownership and founder control

## 12.1 Decide whether to start as a sole trader or company

A sole proprietor can test an idea with less setup, but the business and the individual are not separate legal persons. A private company (Pty) Ltd can provide a separate legal entity and a clearer structure for owning the app, signing retailer agreements, opening a business bank account and bringing in shareholders later. It also brings ongoing company-law, tax and accounting duties.

The founder should not register a company only because it sounds professional. The decision should reflect liability, contracts, ownership, expected revenue and cost. A South African accountant or commercial lawyer can help decide the right timing.

## 12.2 CIPC pathway

For a private company:

1. Check the company name and possible conflicts.
2. Check trade-mark availability separately; company registration does not equal trade-mark registration.
3. Create the CIPC/BizPortal account with credentials the founder controls.
4. Select the correct private-company structure and memorandum of incorporation.
5. Complete director and shareholder details truthfully.
6. Keep registration certificates, company number, MOI and share records.
7. Submit beneficial-ownership information as required.
8. File annual returns and required accompanying information on time.
9. Keep director, address and contact details up to date.
10. Store all company and tax records securely.

CIPC currently states that company and close-corporation annual returns are tied to beneficial-ownership information and must be filed within the applicable period; its guidance refers to filing within 30 business days after the anniversary date. Reconfirm the applicable deadlines and current fees at the time of registration.

## 12.3 Asset ownership checklist

The founder or company must control:

- GitHub organisation/repository.
- Domain and DNS account.
- Cloud hosting account.
- AI provider account and billing.
- Database and private file storage.
- Google Play Console listing.
- App signing keys.
- Brand artwork and source design files.
- Website analytics and advertising accounts.
- Affiliate network accounts.
- Business bank account and billing records.

Use two-factor authentication, recovery codes, a password manager and a documented emergency recovery process.

## 12.4 Intellectual property ownership

Before relying on the project, identify who created and owns the original code. If another developer, friend or company created it, obtain a written agreement identifying the rights assigned or licensed. Payment alone should not be assumed to transfer every copyright and related right.

The assignment should identify:

- Source code and build scripts.
- UI/UX and graphics.
- Brand name and logo files created for the app.
- Database schema and original data compilations created by the business.
- Documentation and tests.
- Domain and social accounts where transferable.
- Future improvements and deliverables.
- Third-party libraries and their licences.

Retailer source content and third-party libraries remain subject to their own licences; a company cannot assign rights it does not own.

## 12.5 Tax and company administration

The company should have a separate bank account and complete records from the beginning of commercial operations. Register and file with SARS as required. Obtain advice about company income tax, provisional tax, VAT and whether a qualifying small-business or turnover-tax regime is suitable.

SARS's Budget 2026 material states that it is administering the announced VAT threshold increase to R2.3 million for compulsory registration and R120,000 for voluntary registration from 1 April 2026, while noting the relevant legislative process. These figures and their legal implementation should be rechecked with SARS or an accountant before relying on them. Turnover Tax is a separate regime with eligibility criteria; it is not automatically the best option for every company.

---

# 13. Launch and growth strategy

## 13.1 Do not launch nationally with unverified data

A credible launch should begin with a small but properly covered pilot area. The objective is not to advertise “all South African specials” before the data system can support that claim. It is to prove:

- The selected source set is authorised.
- All received source pages are accounted for.
- All price-bearing items are extracted or listed as gaps.
- Reviewers can verify offers at a reasonable cost.
- Users understand dates and conditions.
- The app remains useful on a phone and slow network.

## 13.2 Pilot launch sequence

1. Complete the source and legal register.
2. Obtain at least one authorised source route for each pilot retailer.
3. Process the full active pamphlet set for the pilot area.
4. Complete page-level extraction and human review.
5. Run the data and UI tests.
6. Invite a small group of local shoppers.
7. Collect error reports and usage feedback.
8. Correct issues and measure repeat use.
9. Expand the source inventory and geographic scope only when the process is sustainable.

## 13.3 Growth channels

Potential channels include:

- WhatsApp community sharing, without spam.
- Local Facebook groups where promotion is permitted.
- Community pages and local radio.
- Grocery-budgeting and household-saving content.
- Referral links.
- Retailer partnership announcements where agreed.
- Search-engine content such as “weekly price comparison in Mpumalanga”, backed by accurate data.

Do not send unsolicited marketing messages to phone numbers collected from groups. Obtain marketing consent where required and honour opt-outs.

## 13.4 Retailer partnership pitch

The app should approach retailers with a professional, specific offer:

- It directs shoppers to authorised retailer offer pages or stores.
- It records the product and price in a comparison interface.
- It can show exact campaign periods and regional conditions.
- It does not copy complete pamphlets or use logos without approval.
- It can label official partner offers.
- It can link directly to an authorised offer page or store locator.
- It can provide an agreed performance report if the retailer wants one.

Ask for written permission that specifically addresses data fields, update frequency, storage, commercial use, affiliate revenue, AI/OCR processing, branding, attribution, link-out requirements and termination.

---

# 14. Testing and quality assurance plan

## 14.1 Unit tests

At minimum, unit tests must cover:

- Currency and decimal parsing (R25, R25.99, R1 299.99).
- Thousands separators and OCR confusions.
- Pack size parsing (kg, g, L, ml, multipacks).
- Product identity normalisation.
- Different sizes and flavours staying separate.
- Loyalty-card price handling.
- Multi-buy maths.
- “From” and variable-weight prices.
- Regional offer handling.
- Date parsing and impossible dates.
- Time parsing and timezone conversion.
- Offer expiry at the exact end instant.
- Unknown dates blocked from verified publication.
- Duplicate offer handling.
- Multiple offers at one retailer retained.
- Previous price history kept separate from retailer “was” prices.
- Expired offer removal and stale offline feed display.
- Large catalogue sizes (3,000, 10,000 and 100,000 synthetic records where practical).
- No silent truncation.
- Rights registry fail-closed behaviour.
- External AI upload disabled unless source and transfer permission are confirmed.
- Remote URL allowlist, redirect policy and host validation.
- Partial job cannot be published as complete.

## 14.2 Extraction completeness tests

Build a rights-cleared gold test set of sample pamphlet pages. For each page, manually record the correct number of priced offers and their fields. Include difficult pages:

- Dense grocery grids.
- Meat/braai specials.
- Small corner boxes.
- Multiple prices in one product card.
- Loyalty prices.
- Multi-buy deals.
- Flyers with different dates for different items.
- Low-resolution scans.
- Rotated pages.
- Product photographs with small overlaid text.
- Gadget specifications.
- Regional fine print.

Calculate recall and precision for item detection and field accuracy separately. A model should not be declared complete from a test that only checks whether it returned valid JSON.

## 14.3 Integration tests

Test the complete path from a permitted file to a candidate offer feed:

- File registration.
- Page count.
- Source permission check.
- OCR/extraction.
- Page audit.
- Retry handling.
- Queue checkpoint.
- Candidate creation.
- Human review.
- Publication gate.
- Feed deployment.
- Client display.
- Expiry.

Use mock AI responses for deterministic integration tests and a small rights-cleared live test set for provider integration tests.

## 14.4 End-to-end tests

Use real browser automation to test:

- First app load.
- Search and filters.
- All result pages.
- Basket operations.
- Unit-price display.
- Offer detail.
- Date countdown.
- Offline feed.
- Stale cache labelling.
- User correction form.
- Language setting.
- Accessibility and keyboard navigation.
- Phone-sized viewport.
- Android WebView behaviour.

## 14.5 Security tests

Test:

- No API key in JavaScript bundle or APK.
- No direct public access to private source documents.
- Server-side validation of user input.
- Remote URL allowlists and SSRF prevention.
- Safe file type and size handling.
- No untrusted HTML rendering from offer descriptions.
- Appropriate CORS, CSP and HTTPS.
- Rate limiting and abuse handling.
- Authentication and role separation for reviewers.
- Audit log integrity.
- Backup restoration.

## 14.6 Release gate

A release must not be labelled production-ready unless the release report contains:

- Version and commit hash.
- Test suite results.
- Known issues.
- Source coverage status.
- Open page gaps.
- Offers pending review.
- Security scan status.
- Android/web build status.
- Rollback version.
- Legal/source changes since last release.

---

# 15. Monitoring and business operations

## 15.1 Daily operations dashboard

The owner/reviewer should see:

- Expected retailers and source endpoints.
- Sources checked today.
- Current pamphlets received.
- Missing expected pamphlets.
- Total pamphlet pages.
- Completed, pending, failed and gap pages.
- Expected price-bearing item counts.
- Extracted candidate count.
- Verified published offer count.
- Expired and withdrawn offers.
- Quota/runtime failures.
- Cost per source and page.
- Last successful public feed deployment.

## 15.2 Alert conditions

Generate alerts when:

- An expected source has not been checked within its freshness window.
- A new pamphlet is discovered but not queued.
- A page count is missing.
- Extraction count does not match the audit count.
- A page fails repeatedly.
- API quota is exhausted.
- A source permission record expires or is withdrawn.
- A candidate feed is partial.
- Expired offers remain in the public feed.
- A public offer receives repeated price complaints.
- A user data incident is detected.
- The public feed or app fails to load.

## 15.3 Data retention and deletion

Retain only what is needed for the business, legal compliance and audit. Source documents may have a shorter retention limit than derived factual offer records, depending on the agreement. When a permission is withdrawn, the company must assess whether it must stop future processing, remove cached source content, remove or retain derived fields under the agreement, and document the decision. A source-rights withdrawal is not merely a URL configuration change; it must trigger a review of existing records.

---

# 16. Risk register

| Risk | Likelihood before controls | Impact | Required control |
|---|---|---|---|
| Missing offers from dense pages | High | High | Page-level audit, independent counts, re-read queue, reviewer gate |
| AI misreads price | High | High | Candidate status, schema validation, price anomaly checks, human review |
| Expired offer remains visible | Medium | High | Offer-level expiry time, timezone-aware service/client checks, expiry tests |
| Retailer source use challenged | Medium | High | Source-specific permission evidence, legal review, no broad crawler |
| Third-party compilation copied | Medium | High | Independently curated data, limited fields, source/legal review |
| Retailer affiliation implied | Medium | Medium/High | Plain-text identification, no unlicensed logos, explicit non-affiliation notice |
| Stale or false stock claim | High | High | Separate ad validity from stock; no availability guarantee without feed |
| User privacy breach | Medium | High | Data minimisation, encryption, access controls, incident plan |
| API quota causes incomplete feed | High | Medium/High | Durable queue, checkpoint/retry, previous snapshot retained |
| App performance on low-cost phones | Medium | Medium | Pagination/virtualisation, small feed payload, text-first design |
| Business costs exceed revenue | High | High | Pilot budget, per-page costing, real usage and revenue metrics |
| Account lockout or developer owns keys | Medium | High | Founder-controlled accounts, 2FA, recovery records, asset register |
| Android release rejected or delayed | Medium | Medium | Play policy review, closed testing, permission minimisation |
| False sponsored ranking | Medium | High | Separate ad ranking, labels, independent price sort |

---

# 17. Implementation roadmap and acceptance gates

This roadmap prioritises correctness and trust before scale.

## Phase 0 — Project baseline and owner control

**Tasks**

- Decide the permanent repository and project version.
- Create an owner-controlled private GitHub repository.
- Confirm who owns original source code and obtain any required written assignments.
- Secure domain, DNS, Cloudflare, AI provider and Play Console accounts.
- Keep demo data visibly labelled.
- Add a changelog and release ledger.

**Acceptance gate**

The owner controls the accounts, the source code's ownership position is documented, and nobody is claiming the demo catalogue is live.

## Phase 1 — Source inventory and legal gates

**Tasks**

- Create a source register for each intended retailer and endpoint.
- Review exact source terms and permissions.
- Obtain retailer/feed permissions where required.
- Record local OCR and external AI upload permissions separately.
- Remove uncontrolled aggregator discovery.
- Draft the source takedown and permission expiry process.

**Acceptance gate**

Every enabled source has a complete permission record and evidence. The registry is not populated with guessed rights.

## Phase 2 — Exhaustive ingestion engine

**Tasks**

- Replace file-level extraction with durable page-level jobs.
- Remove all hidden PDF/image/item/prompt/list caps.
- Add page manifests and exact page counts.
- Add independent offer count audit.
- Add page-level retries and checkpoint persistence.
- Add quota wait and resumable jobs.
- Add a full coverage report.
- Add comprehensive categories and variants.
- Add dates and exact end-time fields.

**Acceptance gate**

A rights-cleared test set containing dense multi-page grocery, meat, braai, chicken, gadget and non-food pages is processed without silent loss; every page has a status; every count mismatch is visible; no partial run is published as complete.

## Phase 3 — Product and offer correctness

**Tasks**

- Separate product identity and offer records.
- Improve variant matching and duplicate detection.
- Preserve every distinct same-store offer.
- Add unit-price calculation.
- Add loyalty and multi-buy representation.
- Add regional and branch rules.
- Add offer-level expiry.

**Acceptance gate**

Gold-set tests meet an agreed precision/recall threshold, with no unresolved high-severity price or identity errors in the release candidate. Unknown dates and ambiguous products remain pending.

## Phase 4 — Catalogue UI and basket

**Tasks**

- Make total catalogue counts visible.
- Improve pagination/virtualisation without hidden content truncation.
- Add categories and synonyms.
- Add product detail with source, dates and conditions.
- Improve basket optimiser and transport costs.
- Add freshness/verification labels.
- Add correction reports.

**Acceptance gate**

A pilot shopper can find every offer in the test feed, understand conditions and build a basket without seeing sample data as current.

## Phase 5 — Pilot and operational proof

**Tasks**

- Operate a small geographic pilot.
- Measure source freshness, extraction accuracy, review time and costs.
- Gather shopper corrections.
- Improve search and category design.
- Confirm the legal and privacy pages with counsel.

**Acceptance gate**

The pilot has repeat users, measurable accuracy and a sustainable review workflow. Do not expand merely because the app can display more data.

## Phase 6 — Business launch

**Tasks**

- Complete company and IP ownership arrangements.
- Finalise terms, privacy notice and supplier identity details.
- Establish tax and accounting process.
- Apply for appropriate affiliate programmes.
- Establish advertising/sponsored content rules.

**Acceptance gate**

The business can identify who owns the app, who processes user data, how revenue is recorded, how sponsored placements are labelled, and how complaints are handled.

## Phase 7 — Android release

**Tasks**

- Finish Capacitor Android project.
- Test on physical devices.
- Review all Android permissions.
- Generate signed AAB.
- Complete Play Console declarations.
- Run any required closed test.

**Acceptance gate**

The release passes device tests, policy checks, privacy declarations and production access requirements.

## Phase 8 — Scale and retailer integration

**Tasks**

- Add more authorised retailer feeds.
- Introduce database and review console if volume requires it.
- Automate source freshness monitoring.
- Negotiate direct retailer partnerships.
- Add price alerts and history.

**Acceptance gate**

Every added source has rights and measurable quality, and the cost per active offer remains sustainable.

---

# 18. Immediate engineering backlog

The next code-improvement cycles should work through this queue. Priority may change if testing reveals a more severe blocker.

## P0 — Must fix before any public data launch

- [ ] Remove the demonstration 75-item catalogue from the production feed or keep a strict demo environment flag that can never be mistaken for live data.
- [ ] Keep the 75 sample offers only in a clearly labelled demo fixture, not a public verified feed.
- [ ] Add a real source inventory and source-permission evidence records.
- [ ] Add a page manifest for every pamphlet page.
- [ ] Add a separate page-count audit; prompt instructions alone are insufficient.
- [ ] Add exact offer-level date/time fields and `Africa/Johannesburg` timezone semantics.
- [ ] Block missing or uncertain end dates from verified publication.
- [ ] Ensure failed/quota-limited chunks remain pending and can be resumed.
- [ ] Prevent partial candidate feed from being described as complete.
- [ ] Add source/page provenance to every offer.
- [ ] Add a verified-feed banner based on a signed/validated release, not merely the existence of a timestamp.
- [ ] Make the 100-item display window transparent and improve “show all”/pagination UX.

## P1 — Required for a trustworthy pilot

- [ ] Expand retail categories and offer schema.
- [ ] Improve meat/braai/chicken and appliance-specific extraction fields.
- [ ] Add product-variant matching rules.
- [ ] Add unit-price and multi-buy calculations.
- [ ] Preserve multiple offers per store and source.
- [ ] Add a price correction workflow.
- [ ] Add a reviewer dashboard or structured review interface.
- [ ] Add current offer count and source coverage report in the app.
- [ ] Add offline stale-feed expiry handling.
- [ ] Add end-to-end browser tests.
- [ ] Add mobile accessibility tests.

## P2 — Needed as usage grows

- [ ] Move from one large `index.html` to modular files/components.
- [ ] Add managed database and page-level queue.
- [ ] Add operational monitoring and cost dashboards.
- [ ] Add alerts and price history.
- [ ] Add household list sharing and barcode scanning.
- [ ] Add additional South African language translations.
- [ ] Add retailer dashboards and partner APIs.

---

# 19. Research and source register

The following sources were checked for this plan on or around 25 November 2026. The live law, source terms and provider requirements must be checked again before launch. References below are intended for legal and engineering review; they are not a substitute for a professional opinion.

## South African law and compliance

1. [Copyright Act 98 of 1978 — South African Government](https://www.gov.za/documents/copyright-act-16-apr-2015-0942)
2. [Copyright Act definition of literary work, including tables and compilations](https://api.acts.co.za/copyright-act-1978/1_definitions.php)
3. [National Soccer League t/a Premier Soccer League v Gidani (Pty) Ltd [2014] ZAGPJHC 33](https://www.saflii.org/za/cases/ZAGPJHC/2014/33.html)
4. [Constitutional Court: Copyright Amendment Bill and Performers' Protection Amendment Bill, [2026] ZACC 26](https://www.concourt.org.za/index.php/11-former-jud%20ges/index.php/judgement/index.php/judgement/647-ex-parte-president-of-the-republic-of-south-africa-in-re-constitutionality-of-the-copyright-amendment-bill-and-the-performers-protection-amendment-bill-cct306-24)
5. [Parliament: Copyright Amendment Bill B13-2017](https://www.parliament.gov.za/bill/2291650)
6. [SA Legal Academy report, 20 November 2026: Parliamentary committee updated on status of amending legislation](https://legalacademy.co.za/news/read/intellectual-property-parliamentary-committee-updated-on-status-amending-legislation)
7. [Trade Marks Act 194 of 1993 — South African Government](https://www.gov.za/sites/default/files/gcis_document/201409/act194of1993.pdf)
8. [Consumer Protection Act 68 of 2008 — South African Government](https://www.gov.za/sites/default/files/32186_467.pdf)
9. [Consumer Protection Act section 29 — general standards for marketing](https://api.acts.co.za/consumer-protection-act-2008/29_general_standards_for_marketing_of_goods_or_services.php)
10. [Consumer Protection Act section 41 — false, misleading or deceptive representations](https://api.acts.co.za/consumer-protection-act-2008/41_false_misleading_or_deceptive_representations.php)
11. [Electronic Communications and Transactions Act 25 of 2002 — South African Government](https://www.gov.za/documents/electronic-communications-and-transactions-act)
12. [ECTA section 86 — unauthorised access/interception/interference with data](https://www.gov.za/sites/default/files/gcis_document/201409/a25-02.pdf)
13. [ECTA section 43 — information to be provided for electronic transactions](https://www.saflii.org/za/legis/consol_act/ecata2002427.pdf)
14. [POPIA section 22 guidance — Information Regulator](https://inforegulator.org.za/wp-content/uploads/2020/07/Guidelines-on-completing-a-Security-Compromise-Notification-ito-Section-22-POPIA.pdf)
15. [Information Regulator fact sheet: handling security compromises, 19 August 2025](https://inforegulator.org.za/2025/08/19/fact-sheet-handling-of-security-compromises/)
16. [Information Regulator: Information Officer registration](https://www.justice.gov.za/inforeg/)
17. [Information Regulator guidance note on direct marketing under POPIA](https://inforegulator.org.za/wp-content/uploads/2020/07/GUIDANCE-NOTE-ON-DIRECT-MARKETING-IN-TERMS-OF-THE-PROTECTION-OF-PERSONAL-INFORMATION-ACT-4-OF-2013-POPIA.pdf)
18. [CIPC: beneficial ownership filings with annual returns](https://www.cipc.co.za/?p=20728)
19. [CIPC: registration fees and self-service company registration](https://www.cipc.co.za/?page_id=3699)
20. [CIPC FAQs: annual returns and beneficial ownership](https://www.cipc.co.za/?page_id=4160)
21. [SARS: Budget 2026 VAT threshold FAQs](https://www.sars.gov.za/about/sars-tax-and-customs-system/budget/budget-2026-frequently-asked-questions/)
22. [SARS: Turnover Tax](https://www.sars.gov.za/types-of-tax/turnover-tax/)
23. [Advertising Regulatory Board: current Codes and Appendices](https://www.arb.org.za/The_Codes/)
24. [Advertising Regulatory Board: Social Media Appendix, version 2026-02](https://www.arb.org.za/code-file-downloads/Appendix_Social_Media_v2026-02.pdf)

## Technology and distribution

25. [Capacitor 8 environment setup](https://capacitorjs.com/docs/getting-started/environment-setup)
26. [Capacitor Android documentation](https://capacitorjs.com/docs/android)
27. [Google Play: testing requirements for new personal developer accounts](https://support.google.com/googleplay/android-developer/answer/14151465)
28. [Cloudflare Pages current limits](https://developers.cloudflare.com/pages/platform/limits/)

---

# 20. Working definition of “done”

Mzansi Smart Basket is not “done” when it has a nice home screen, a large amount of code, or a ZIP file that opens. It approaches a trustworthy first release only when all these are true:

1. The owner controls the critical accounts, domain, repository and app-store listing.
2. The code ownership position is documented.
3. The source registry contains only source routes with a documented permission basis.
4. Every in-scope current pamphlet has a record.
5. Every page of every in-scope pamphlet has a processing status.
6. Every page has a defensible offer-count audit.
7. Every offer has correct product identity, price, conditions, source and region or a visible unresolved status.
8. Every verified offer has a usable expiry policy and is removed/marked expired at the right time.
9. No partial run can masquerade as a complete feed.
10. No demo price can appear as a live verified price.
11. The app exposes all results, even where it paginates for performance.
12. Users understand whether an offer is verified, stale, regional, conditional or stock-unconfirmed.
13. Users can report errors and the company can correct them.
14. POPIA and other required legal/consumer documents have been completed for the actual business.
15. The public web app and Android app have been tested on real devices.
16. The company has a sustainable operational and revenue plan.

## Final direction

Keep the original idea: collect permitted retail-offer information from multiple retailers, include every in-scope offer rather than a small curated sample, compare prices properly, and help South African households plan their shopping baskets.

Change the method: replace uncontrolled pamphlet crawling and unverified AI publishing with an authorised, exhaustive, page-audited, resumable and human-reviewed data pipeline. Make source coverage visible. Separate factual offer data from protected pamphlet artwork and source compilations. Keep price ranking independent of advertising. Build the customer experience around accuracy, convenience and trust.

The next work should focus on Volume 2's legal/source-rights operating manual and Volume 3's exhaustive extraction specification, then turn those specifications into tested code. The latest reviewed ZIP is a useful safer baseline, but it is not yet a live or fully exhaustive production service.

---

# 21. Verified baseline audit — Legal Reviewed v2

This section records observations from the actual `mzansi_smart_basket_legal_reviewed_v2.zip` project inspected for this plan. It is deliberately separate from the target-state design. A feature described elsewhere in this plan is not considered implemented merely because it is specified here.

## 21.1 Baseline identity and current status

The reviewed project is a static/PWA-first web application with a single large `index.html`, a Python extraction pipeline, a manually gated publisher, a JSON offer feed, a service worker, a small set of tests, and a Capacitor 8 package configuration. The project is a safer development baseline than the original v9-style crawler because it no longer performs broad third-party catalogue crawling and it separates AI extraction from public publication.

However, the project is not yet a live retail-data service. The inspected `approved_sources.json` has an empty `sources` array. The inspected `deals.json` identifies itself as a demonstration catalogue, carries `approvalStatus: demo`, has an empty `verifiedAt`, and contains 75 sample products. Those sample offers must never be represented as confirmed retailer specials. Before a real public launch, replace the sample feed with an explicitly empty “no verified offers yet” state or a genuine reviewed feed. Do not quietly relabel examples as live data.

## 21.2 Confirmed strengths in the current baseline

1. The source registry requires an explicit record rather than discovering random pamphlet aggregators.
2. Remote source downloads are disabled by default and restricted to approved HTTPS hosts when enabled.
3. Gemini document uploads are a separately controlled action and are disabled by default.
4. The extractor writes a candidate file rather than changing the live public feed directly.
5. The publisher requires explicit human acknowledgements for offer review and source-rights review.
6. The publisher checks for a non-empty product feed, positive finite prices, validity end dates, start/end ordering and HTTPS source references.
7. The publisher rejects candidates that report unread chunks or quota exhaustion.
8. The extractor splits multi-page PDFs into small chunks, caches successful chunks and preserves candidate data separately from the public feed.
9. The UI distinguishes demonstration data from a human-reviewed feed.
10. The catalogue includes categories for meat/poultry, gadgets/appliances, clothing, household products and other offers, not only grocery staples.
11. The UI has a visible first-page rendering window of 100 items, with load-more and “Show all” controls. This is not the same as a source extraction cap, but it must remain clear to the shopper how many results exist and which are loaded.

## 21.3 Confirmed blockers and implementation defects

### A. Automated ingestion is currently switched off

The inspected GitHub Actions workflow sets both `ENABLE_APPROVED_REMOTE_DOWNLOADS` and `ENABLE_GEMINI_DOCUMENT_UPLOADS` to `false`. The extractor checks the Gemini-upload flag near the beginning of `main()` and returns before extraction when that flag is false. The source registry is empty as well. The result is that the scheduled job, as currently configured, does not read or convert new pamphlets into candidate offers. The workflow may run tests and exit successfully without updating a real price catalogue.

**Required fix:** Do not simply switch both flags on globally. First obtain and record a lawful source/processing basis for the exact source, and make separate explicit per-source controls for local OCR, external AI processing, remote download, commercial extraction, offer-data display, image/logo display and link-back. The workflow should print an explicit “NO APPROVED INPUTS — NO INGESTION OCCURRED” status and should not be described as a successful feed refresh.

### B. No independent page-level completeness proof exists yet

The extractor prompt tells the model to count priced items on every page and return all of them. That is a useful instruction, but it is not an independent audit. The extracted structured result does not currently require a per-page expected count, recognized count, omitted-item explanation, page fingerprint or review state. There is no independent computer-vision/OCR count to compare with the AI result. A model can omit a page corner offer and still return structurally valid JSON.

**Required fix:** Add a page manifest and a page-by-page ledger. Every page must move through explicit states such as `discovered`, `downloaded`, `rights_checked`, `rendered`, `text_detected`, `offers_detected`, `extracted`, `audited`, `reviewed`, `published`, `failed` or `blocked`. An empty page is not automatically complete: it needs a visible “zero offer” decision supported by the page content. Use at least two complementary detection passes for dense pages (for example, local text OCR plus visual AI extraction) and require reconciliation of their counts. Disagreement must create a review task, not be silently resolved by dropping an offer.

### C. A successful but empty AI response can be missed

In the current `run_chunk` path, chunks are flagged as failed when the provider status is not `ok`, but an `ok` response containing no rows does not enter that failure path. On a price-bearing page, this can leave the page unrepresented without incrementing the unread/failure count. The publication gate cannot detect an omission the extractor has not recorded as an omission.

**Required fix:** Treat `ok + zero offers` as incomplete unless the independent page audit has verified that the page contains no price-bearing offers. Store a zero-offer reason code and audit evidence for genuinely empty pages. If the page contains offers but extraction returns zero, split the page into smaller visual regions, retry alternate extraction, then place it in the review queue. Never cache an empty result as a completed page without an audit decision.

### D. The current expiry data is date-only

The `ExtractedDeal` schema currently stores `valid_from` and `valid_until` as date strings. `is_expired()` compares dates and treats missing or malformed end dates as not expired. The publisher later refuses publication where an offer end date is missing or invalid, which is a useful additional gate, but the pipeline cannot represent a retailer's exact end time or a short flash deal that expires at a specified hour. A date-only offer may remain visible for more of the final day than the retailer intends if the app treats the date as valid until midnight.

**Required fix:** Store `valid_from_at` and `valid_until_at` as timezone-aware instants with `Africa/Johannesburg` as the default retailer/local offer timezone, while retaining the printed date text as source evidence. Never invent an exact hour. Where only a date is printed, mark the time precision as `date_only` and apply an explicitly documented conservative display/expiry policy. Where a promotion is described as “until stocks last”, record that separately; do not convert it into a fabricated timestamp or stock guarantee. Run an expiry job independently of new pamphlet extraction.

### E. The current offline fallback has a real item limit

The browser's primary network feed is not limited to 1,500 products, but when saving the full catalogue into local storage exceeds the browser quota, the fallback sorts offers and retains only 1,500 products. The code comment states that the service worker still holds the full feed, but browser storage and service-worker cache quotas are not guaranteed and can be evicted. Therefore, the correct product statement is not “unlimited full offline catalogue”. The fallback is a deliberately reduced local catalogue.

**Required fix:** Keep the server-side catalogue complete. Make the client distinguish `online_full`, `offline_full`, and `offline_partial`. When the fallback is partial, say so, display the cached record count and last successful sync time, and never imply that the displayed cached catalogue is complete. Replace whole-feed localStorage serialization with IndexedDB or another storage design suitable for large structured data. Add explicit quota and eviction handling.

### F. Extraction resource ceilings need queue/resume semantics

The current extractor processes PDFs in two-page chunks, has a 65,536-token response ceiling, a default 45-minute runtime budget and the GitHub workflow has a 55-minute job timeout. These are operational safety ceilings, not item-count limits, but they can defer work. The current extractor tracks failed chunks and retains successful chunk cache entries, which is a good beginning; it does not yet provide a complete, durable page-level queue with run IDs, retry reasons, attempt counts, next retry times, and an explicit final coverage certificate.

**Required fix:** Do not remove practical resource limits by setting infinite timeouts. Instead, make every resource-limited run resumable. Every unprocessed page must remain queued. A run that defers work must be marked `partial`, not `complete`. Continue until the full registered in-scope source manifest is accounted for. Publish nothing from a source/run whose page ledger is incomplete.

### G. Workflow path triggers are incomplete

The current workflow watches changes under `pamphlets/**` and `pamphlet_urls.txt`, but the approved-source registry is also a material input to the workflow. Updating the source registry alone should trigger a validation/extraction preparation run, but the current path list does not include `approved_sources.json`.

**Required fix:** Add the registry, extraction scripts, lock/dependency files, schema and workflow files to appropriate CI triggers. Separate a cheap validation workflow from an authorised ingestion workflow, so a documentation or test change does not accidentally trigger paid API processing.

### H. Offer model needs stronger semantics for variants and promotions

The current extraction model stores normal price, reward price, a text `multi_buy_note`, size and category. It has room to grow, but it cannot always represent offers such as “2 for R45”, “R45 each when buying two”, “3 for R100”, “mix and match”, “limit 4”, “from price”, deposit, bundle components, or different pack sizes without ambiguity. Treating R22.50 as the whole deal price for “2 for R45” would be wrong unless the model explicitly stores the required quantity and total.

**Required fix:** Store the advertised total, qualifying quantity, effective per-unit amount, qualifying rule, maximum quantity and original printed offer text as separate fields. Store product identity separately from a price offer. Add GTIN/barcode where legally and technically available, plus brand, variant, net quantity, unit and pack-count. Do not merge two products simply because their names normalize to the same slug.

### I. No real pamphlet has been proven end to end

The 14 passing automated tests are useful unit tests. They exercise size parsing, merging, expiry rejection, source gating, publication acknowledgement, incomplete-coverage rejection and a 3,000-item synthetic merge. They do not prove that a real multi-page Shoprite, Boxer or Pick n Pay leaflet has been exhaustively extracted, that every braai pack/chicken portion/gadget was captured, or that the current data sources are legally usable.

**Required fix:** Build a permission-cleared golden test set of real source pages with a human-authored ground-truth offer inventory. The inventory must cover dense food pages, meat/butchery price boards, chicken portions, braai packs, gadgets, appliances, clothing, loyalty prices, multi-buy conditions, tiny footnotes, regional variants, and multiple promotions on one page. Measure precision, recall and exact-field accuracy per page and per offer type. A complete pass requires 100% page accounting and a defined high accuracy threshold, with every exception visible and resolved by a reviewer. The app must not use a passing synthetic unit test as a marketing claim of complete retailer coverage.

## 21.4 Exact current test status

The reviewed baseline was tested in the local project folder on 25 November 2026. The command `python -m unittest discover -s tests -v` completed with **14 tests passing**. The tests include a synthetic 3,000-item merge. This demonstrates that the merge layer can handle that synthetic input without a built-in product-count ceiling. It does not demonstrate unlimited memory, CPU, API quota or production throughput, and it does not demonstrate exhaustive pamphlet OCR.

Python compilation checks and JavaScript syntax checks were also reported as passed during the package review. A real Android APK/AAB build, physical-device QA, real pamphlet benchmark, and live source ingestion were not completed as part of this plan creation.

## 21.5 Immediate P0 work in the correct order

1. Remove or isolate the 75 demonstration offers before any public live-price launch.
2. Add a truthful app-wide status: `DEMO`, `NO VERIFIED OFFERS`, `PARTIAL COVERAGE`, `REVIEW IN PROGRESS`, `VERIFIED FEED` or `STALE FEED`.
3. Add a page/source manifest and a resumable page queue.
4. Fix zero-row `ok` responses so price-bearing pages cannot disappear from coverage accounting.
5. Add page-level audit counts and a review task for count mismatches.
6. Replace date-only expiry as the sole time model with validity instants and an explicit date-only policy.
7. Replace the 1,500-record offline fallback with IndexedDB and a visible completeness indicator.
8. Add source-rights granularity for local OCR, external AI, remote fetching, extraction, commercial display, image use and linking.
9. Correct CI triggers and make the workflow distinguish “no approved input”, “partial run” and “complete run”.
10. Create the first legally cleared golden benchmark set and test every page against it.
11. Preserve every raw source and candidate record only for the approved retention period; keep scans private and separate from public offer data.
12. Run a real-world pilot with a small declared source universe before expanding to all South African retailers.

## 21.6 Proof required before claiming complete coverage

Every ingestion run must produce a machine-readable manifest containing:

- run identifier, start/end time and operator/workflow identity;
- source ID, source version, source URL or local file name, rights-record ID and file SHA-256;
- source publication/validity window and the reason it is in scope;
- total pages, rendered pages, OCR-processed pages, AI-processed pages and audited pages;
- per-page OCR offer count, AI offer count, reconciled count and human-review status;
- duplicate decisions and links to the canonical offer IDs;
- zero-offer pages with reviewer or audit evidence;
- pages deferred, failed, blocked, unreadable or excluded with exact reason codes;
- retry attempt count and next retry status;
- total unique candidates and total published offers;
- publication approver, review timestamp and source-rights approval reference.

The run can be marked `complete` only when every page in the source manifest has a terminal, justified state. “The AI returned JSON”, “the GitHub job passed”, “the PDF was split”, or “some deals were extracted” are not definitions of completeness.

---

# 22. Product behaviour rules for difficult real-world offers

These detailed rules are included because the largest comparison errors often occur outside simple grocery products.

## 22.1 Meat, chicken and braai offers

The catalogue must preserve distinctions between whole chicken, chicken portions, IQF mixed portions, drumsticks, thighs, wings, breast fillets, braai packs, marinated products, wors, boerewors, steak packs, chops, offal and prepared meat trays. Similar labels do not mean the same product. Record cut, bone-in/bone-out, fresh/frozen, marinade, pack mass, pack count, quality/grade where stated, and any “assorted” wording. If the leaflet advertises a variable-weight product with a per-kilogram price, represent the price basis as `per_kg`, not as a false fixed pack price.

When a photograph or illustration shows a serving suggestion rather than the actual pack, do not infer the product contents from the picture. Use the printed description. Preserve exclusions such as “selected varieties”, “while stocks last”, “minimum weight”, or “participating stores only”. A braai pack that contains multiple products should have a bundle record with component text if the components are stated. Do not convert the bundle into a single generic “meat pack” and lose its contents.

## 22.2 Gadgets, appliances and electronics

Capture manufacturer, model number, exact capacity/specification, voltage/plug type where shown, warranty statement, included accessories, colour/variant, price, instalment wording and whether the item is online-only or branch-specific. A “from R…” price must remain a starting price and cannot be presented as the definite price of every variant. If the pamphlet shows a picture of one model but text describes another, create a discrepancy review. For electronics, a cheaper item with materially lower capacity or a different model must not be ranked as a direct equivalent without a clear comparability label.

## 22.3 Clothing, footwear and household products

Capture size ranges, material, pack count, dimensions, colour/variant, age band (where relevant), unit count and any mix-and-match terms. A multi-pack should not be compared to a single item without unit calculation. A displayed model wearing clothing is not evidence that every pictured garment is included in a bundle.

## 22.4 Loyalty-card and membership prices

Keep the ordinary price and the qualifying loyalty/member price separately. Record the exact programme, whether membership is free or paid if known, eligibility restrictions, account requirements and limit per card. If the card discount applies only to a selected subset of variants, link it only to those variants. Do not assume a customer has a loyalty card. A basket optimiser must show both the price available to everyone and the price available only when the user qualifies.

## 22.5 Multi-buy, bundle and quantity-limit offers

A multi-buy promotion must not be flattened into a single unit price without recording the qualifying quantity. For example, the record for “2 for R45” must preserve `advertised_total=45`, `required_quantity=2`, and `effective_unit_price=22.50`, plus the original wording and any mix-and-match rule. If the shopper adds only one item, the basket must not incorrectly charge R22.50. For “buy 2, get 1 free”, represent the qualifying quantity and free quantity explicitly. For “3 for R100 or R39.99 each”, represent both purchase paths.

## 22.6 Price comparison and price history

Compare the same item or clearly labelled equivalent variants. Calculate unit price only when a reliable quantity and unit are available. Use correct conversions (kg/g, L/ml, count, per roll, per nappy, per wash) and never compare unlike measures as though identical. Preserve a price history only with source provenance and an explicit distinction between normal shelf price, advertised price, loyalty price and observed till price. Do not invent a “was” price or savings percentage from an unknown baseline.

---

# 23. Shopper trust, support and correction operations

A price-comparison service needs a visible correction mechanism, not only a disclaimer.

## 23.1 Every offer needs an evidence drawer

An offer detail view should expose retailer, product description, pack size, advertised price, member price if any, offer conditions, region, validity, last checked time, source reference and verification state. The public app should not expose private pamphlet scans or internal source documents unless the licence expressly permits display. A source link may be a retailer's official page or an authorised document link, depending on the rights record.

## 23.2 User reports

Each offer should support a report reason such as wrong price, expired offer, wrong product, wrong size, wrong branch/region, loyalty condition missing, item unavailable, duplicate, or suspected misleading listing. Reports should be triaged by severity. A confirmed material error should immediately mark the offer as disputed or temporarily suppress it while it is checked. A report alone should not silently rewrite the price.

## 23.3 Correction service levels

Define practical internal targets, not promises that cannot be met. Example pilot objectives: urgent high-impact price errors reviewed within one business day; routine reports reviewed within three business days; all reports acknowledged automatically. Publish the actual policy and review the targets after the pilot. Record who changed the offer, when, why and which evidence supported the correction.

## 23.4 Public incident notice

If a feed-wide extraction error or source mismatch is discovered, pause affected offers, preserve the last known good feed only if its validity remains current, mark the feed stale, and show a notice where user decisions may be affected. Do not keep displaying an old feed as “live” simply because it is cached.

---

# 24. Volume 1 completion ledger

| Workstream | Status | Evidence / next action |
|---|---|---|
| Requirements captured from user notes | Complete for Volume 1 | The uploaded notes are the baseline for exhaustive pamphlet and product coverage |
| Original v15 code audit | Baseline reviewed | Old crawler had hidden source limits and sample-feed risk; see source notes in conversation |
| Legal Reviewed v2 audit | Complete for initial audit | Actual files inspected; findings recorded in Section 21 |
| South African legal research | Preliminary research complete | Must be rechecked by counsel before commercial use |
| No-arbitrary-content-cap design | Specified | Page manifest, resumable queue and full coverage proof required |
| Page-level completeness engine | Not implemented | Volume 3 / P0 implementation |
| Verified retailer source agreements | Not started | Source register currently empty |
| Real current pamphlet extraction benchmark | Not run | Need permitted source files and gold-labelled offer inventory |
| Exact expiry instants | Not implemented | Add timezone-aware validity model and expiry worker |
| Offline full-catalogue guarantee | Not implemented | Replace localStorage cap with IndexedDB + completeness state |
| 75 demo offers replaced | Not done | Must remove/replace before public production claims |
| Web production deployment | Not verified | Domain/Cloudflare owner accounts and live QA needed |
| Android signed release | Not verified | Native Android project generation, signing and physical-device test remain |
| Commercial revenue evidence | Not available | Need users, actual traffic, affiliate agreements and costs |

Volume 1 is complete as a strategic and baseline-audit document. The app itself is not complete. The next implementation cycle should start with the P0 items in Section 21.5 and should not widen the retailer source universe until source permission and page-level coverage can be demonstrated.

---

# Iteration 2 amendment — evidence-led coverage, regional offers and private processing

**Amendment date:** 25 November 2026  
**Applies to:** Volume 1 architecture, the pamphlet ingestion workflow, offer data model, trust model and release gates.

This amendment records implementation changes made after the first continuation baseline was re-audited. It does not change the product vision or relax the “every in-scope offer” requirement. It strengthens the evidence needed before a run can be described as complete.

## A. Page-level completeness is a gate, not a progress estimate

Every pamphlet PDF is enumerated into one-page units. Each page carries its source filename, one-based page number, SHA-256 fingerprint, cache status, extraction count, extraction-reported count and a separate second-pass AI count. A page is complete only when the three offer counts agree. Empty extraction is accepted only when both model passes explicitly report zero priced offer blocks.

A failed, truncated, ambiguous, count-mismatched or quota-limited page remains incomplete and must be retried. It is not converted into a successful empty page. The pipeline maintains complete-page cache entries so later runs can resume without repeating all already completed pages. The cache key changes when the source page bytes, extraction prompt/schema, extraction model or audit model changes.

**Accuracy limitation:** two AI passes are not two independent ground-truth measurements. Both may overlook the same small price block or misinterpret a multi-buy. The project must not market “100% extraction” based on matching model counts alone. A manually labelled benchmark is a release prerequisite.

## B. Offer identity and deduplication

A product card can contain several valid offers from the same retailer. Equal prices do not prove that two records are duplicates: the pamphlet, page, validity period, region, card requirement, quantity condition or campaign may differ. The merger therefore retains distinct offers and collapses only records with identical recorded commercial/source identity.

The primary store offer is selected for display, while distinct alternatives remain in `moreOffers`. At display time, the frontend evaluates each offer independently. It prefers an offer active now over one that starts later, hides expired offers by default, and preserves the shopper's explicit expired-offer view. A still-valid alternative must not disappear just because the cheapest recorded offer has expired.

## C. Region belongs to the offer, not just the product

The product-level region list is a discovery/union field. It must not be treated as proof that every retailer offer applies throughout that union. Each primary and alternative offer stores its own province scope. The publication gate checks for valid South African province values, and the interface filters individual offers for the selected province.

Further work must determine how to represent “Inland”, “Coastal”, selected provinces, participating branches, exclusions, and store-specific terms without over-expanding a promotion's geography. If the source is ambiguous, the offer must be labelled “region unclear” and held for review rather than broadened to “All”.

## D. Offer expiry and start boundaries

The app stores `validFromAt` and `validUntilAt` only when clock times are printed. A date-only end date is treated as inclusive through that date in the Africa/Johannesburg timezone and is labelled “exact time not stated”. The frontend schedules a refresh at the next offer start/end instant and refreshes on return to the foreground. The basket can look up the dates of the specific offer that was selected, including an alternate.

This describes advertised validity, not live store inventory. Retailer stock, participating branches, price overrides and till conditions can still vary. The UI must not equate an unexpired advertisement with confirmed stock.

## E. Publication checks apply to every offer row

The publication gate iterates every primary offer and every alternate under `moreOffers`. It validates prices, date ranges, exact timestamp syntax and consistency, source URL or approved local-source provenance, and province scope. An expired or unsourced alternate cannot bypass checks merely because a primary offer is valid. Private source-evidence references are removed from the public feed after the reviewer has acknowledged the source-rights basis; public source IDs/labels and page provenance can remain.

Human acknowledgements are workflow guardrails. They are not an automated legal opinion, independent price verification or proof that the operator actually inspected the source.

## F. Source-ingestion security and private workflows

Remote source files are fetched only from exact HTTPS hosts in the approved register, with redirects disabled. Downloads are streamed, actual bytes are counted against the configurable per-file byte ceiling (100 MB default), and file signatures must identify a PDF, PNG, JPEG or WebP. This ceiling is a resource/security guard on each file; it is not a cap on the number of pamphlets, pages or offers. The workflow must report a rejected large or invalid file clearly, not silently omit it.

The source-rights register can be supplied through the private `APPROVED_SOURCES_JSON` GitHub Actions secret. The repository is required to be private while source agreements, provenance records, unpublished candidates or cached extracts are processed. Workflow caches store completed-page extraction results; candidate feeds and reports are uploaded as short-lived workflow artifacts instead of committed to public source history.

Document upload to Gemini and remote downloads remain disabled by default. The owner must enable them only after confirming rights for commercial extraction and transfer to the configured AI processor. A public URL, free printed pamphlet or OCR capability alone is not treated as permission.

## G. Client-side trust labels

A locally imported JSON file cannot declare itself verified. A user-selected external feed may load, but it remains unverified even when its JSON claims `approvalStatus: verified`. The same-origin reviewed feed can show verified status only when it carries the publisher's review metadata. This is a trust distinction, not a cryptographic signature; a production release should consider signed feed manifests if feeds are hosted separately from the app origin.

## H. Verification and outstanding work

Iteration 2 passed 42 Python tests and a Node-based frontend logic suite. Syntax/configuration checks passed for Python scripts, inline app JavaScript, the web build script, JSON configuration and workflow YAML. These are synthetic/local checks; they do not prove extraction recall or price accuracy on actual pamphlets.

The P0 next step is a manually labelled, rights-cleared real-pamphlet benchmark. It must include dense grocery pages, meat and braai offers, chicken cuts/portions, gadgets/appliances, clothing, loyalty-card prices, multipacks, regional restrictions and multi-buy offers. For every page, record the human expected price-bearing block count and each expected offer record. The extractor must then be scored for recall, precision, exact price accuracy, pack-size accuracy, date accuracy, region accuracy and product-matching errors.

The next technical requirement is structured multi-buy pricing: required quantity, bundle total, single-item fallback, loyalty-card interaction and basket quantity arithmetic. “2 for R50” must not be represented as an unconditional R25 single-item price when the shopper buys one. This must be handled before promoting basket totals as accurate.

The native Android project, signed release bundle, physical-device tests, production Cloudflare deployment, real retailer permissions, live Gemini ingestion and revenue performance remain unverified or blocked. These are explicit gates, not completed features.


## I. Offline trust metadata

The browser cache uses a versioned complete-feed snapshot. Imported JSON is always unverified. A remote feed supplied by a user remains unverified even if its payload claims `approvalStatus: verified`; this status is stripped before the feed is cached. Same-origin feed fetches reject HTTP redirects so a same-origin URL cannot silently redirect to an external feed and inherit the verified status. Cache schema changes invalidate prior snapshots so old self-asserted verification fields do not survive an upgrade. This is not cryptographic feed signing; a future separated feed host should use a signed manifest verified against a public key embedded in the app.

---

# Iteration 3 amendment — SAST expiry and alternate-offer time integrity

This amendment supersedes earlier baseline findings in this document where those findings describe the previous localStorage fallback or the old device-local date handling. Historical baseline observations remain in the audit trail, but they must not be read as the state of the current source tree.

## Updated offline catalogue position

The former 1,500-product localStorage truncation has been replaced by a versioned IndexedDB complete-feed snapshot. The app no longer deliberately slices the feed to a fixed number of products for its local fallback. This does not guarantee offline persistence: browsers may deny storage, evict data, or run out of quota. The app must continue to report cache failure honestly and must not describe the complete offline catalogue as guaranteed until quota/eviction/recovery tests have passed on supported devices.

## South African calendar rules

- All date-only retail offer validity is interpreted in South African Standard Time (SAST, UTC+02:00), not the phone's configured timezone.
- A date-only offer with end date `YYYY-MM-DD` remains valid for that South African calendar date and expires at the following date boundary.
- An exact clock time may be used only when the source prints it and it has been reviewed. It must include an unambiguous offset or be explicitly interpreted as South African local time under the data contract.
- An alternate offer's own date or exact timestamp must never inherit an unrelated primary offer timestamp. Primary/product-level dates are fallback values only when the alternate contains neither its own date nor its own timestamp for that boundary.
- Automatic refresh scheduling includes primary and every alternate offer start/end boundary; this matters when an offer becomes active or expires while the app remains open.

## Verification update

Iteration 3 added frontend regression scenarios for SAST date conversion, invalid calendar dates, date-only expiry labels, alternate-offer refresh scheduling, and the precedence of an alternate's own date-only validity over the primary offer's exact timestamp. At the time of this amendment, 42 Python tests and 10 frontend logic scenarios passed, along with Python compilation, JavaScript syntax, JSON parsing and workflow YAML parsing.

## Remaining high-priority data correctness work

The next price-integrity task is structured multi-buy pricing. The text `2 for R45` must not become a universally applicable R22.50 single-unit price. The data model must distinguish bundle quantity, total bundle price, loyalty eligibility and any explicitly advertised single-unit price. Basket arithmetic must either calculate a qualifying bundle correctly or explain that the offer cannot price a smaller quantity from the available evidence. Product matching must also distinguish pack size, meat cut/grade, brand, model and pack count before declaring offers comparable.
