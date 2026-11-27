# Review of the supplied AI Mode research

Checked: 25 November 2026

## Overall conclusion

The supplied AI Mode research is directionally useful: an independent comparison app can be built around factual offer fields and its own layout, without reposting entire retailer pamphlets. However, the statement that every product price/name can always be commercially reused without permission is too absolute under South African law. Individual facts are different from original expression, but an original table, price list or compilation can itself qualify for copyright. Repeatedly copying the whole selection or a substantial part of a retailer's or catalogue publisher's curated dataset can therefore present a separate issue even when each price is a fact.

The lower-risk product design is to independently compile and verify each offer, store it in Mzansi Smart Basket's own schema, publish only the fields needed for comparison, use plain-text retailer names to identify the offer, retain source/date/region/conditions, and avoid third-party photography, logos, artwork, page layouts and substantial copied compilations. This reduces risk but does not guarantee legality for every dataset or extraction method.

## Statement-by-statement assessment

| Supplied claim | Assessment |
|---|---|
| Retailer pamphlets are copyrighted as publications/artwork | Generally right. Photographs/artistic work and the original text/layout/edition may be protected. The rights in individual elements may belong to different parties. |
| Product names and prices are facts | Generally right when considered individually; not a blanket permission to copy a curated selection or database. |
| A new layout and original graphics are safer | Right. Do not copy protected photographs, logos, price-tag artwork, distinctive design or substantial selection/arrangement. |
| Plain-text store names may identify the source | Generally possible as good-faith identification, provided use is not misleading or likely to suggest affiliation/approval. |
| Credit the retailer and date prices | Good transparency practice, but attribution does not itself create a copyright licence or cure an unauthorised copy. |
| OCR makes automation legal because it uses a PDF rather than a website | Incorrect. OCR is a technical process; it does not change the rights in the source or the legal basis for commercial extraction. |
| Public website scraping is always unlawful | Too broad. It depends on the exact terms, authorisation, access controls, method, volume and applicable law. Do not bypass restrictions or automate against terms that prohibit it. |
| User-uploaded pamphlet images are safe to process | Not automatically. A user upload does not prove that the user has authority to grant commercial processing rights. |
| Affiliate feeds/APIs are preferable | Correct, provided the agreement actually grants the fields, use, display, retention and monetisation rights needed. |

## Main South African legal principles for this product

1. The Copyright Act 98 of 1978 includes written tables and compilations within the definition of literary works, and copyright in literary works includes exclusive rights to reproduce the work or a substantial part. The originality requirement and the amount/quality taken matter.
2. South African case law has recognised copyright in compilations such as price lists/directories where the collection effort and compilation satisfy the originality threshold. Do not bulk-copy a competitor catalogue or another publisher's offer database merely because each individual number is factual.
3. The Trade Marks Act contains a bona fide descriptive-use provision. That supports cautious plain-text identification in suitable circumstances; it does not authorise logos or misleading branding.
4. The Consumer Protection Act addresses misleading marketing, bait marketing and representations about price/availability. The app should not promise stock or a price that cannot be supported, and should disclose region, dates, loyalty conditions and limitations.
5. ECTA section 86 addresses intentional access to data without authority or permission. It does not mean every ordinary webpage request or every scraper automatically commits an offence; access restrictions and authorisation matter.
6. Copyright Amendment Bill B13-2017 is not treated as an enacted general fair-use permission in this project. The Constitutional Court's June 2026 judgment did not itself enact the Bill; November 2026 reporting says Parliament still must revise provisions declared unconstitutional. Re-check the official bill status before launch.

## Practical source workflow

- **Printed pamphlet in hand:** record the source, issue dates and exact offer fields. Before using the extraction pipeline for a commercial service, have counsel review whether the volume and manner of taking the offers could reproduce a substantial part of a protected compilation. Do not assume free handout equals commercial extraction permission.
- **Retailer's public PDF:** check the terms and licence for that exact page/document. Public viewing/downloading is not automatically a right to upload it to a third-party AI processor or commercially reuse an extracted compilation.
- **Retailer e-commerce/Sixty60 website or app:** check current platform terms and technical restrictions first. Do not use bots or scripts where the terms prohibit automated access or reuse without written consent. Do not bypass authentication, CAPTCHAs, paywalls, rate limits or other controls.
- **Third-party catalogue portal:** its compilation and website terms may create an additional layer of rights. Prefer not to copy or scrape another aggregator's curated data.
- **User uploads:** require a clear user warranty that the uploader has authority and a limited processing licence, but do not treat that promise as a complete answer. Keep source images private, do not republish them, and provide moderation/removal procedures.
- **Official feed or affiliate programme:** use only within the written contract/API terms; check whether commercial comparison, storage, display, caching, AI processing and paid placements are allowed.

## Changes made to this project

- Removed automated crawling of third-party catalogue directories.
- Remote downloads remain disabled unless the source host is explicitly recorded in `approved_sources.json` and the workflow flag is enabled.
- Gemini document uploads are disabled by default. The current extractor uploads source PDFs/images to Gemini for extraction, so the source record must explicitly permit AI processing and the operator must check the AI provider's current terms.
- Exact local source filenames must be listed in the approved-source registry before processing.
- Publishing now requires two separate human acknowledgements: every offer was checked, and the source/access/commercial-use basis was checked.
- The public app continues to display independently structured deal facts; it does not display the source pamphlet pages.

These checks are product safeguards, not a substitute for a South African IP lawyer's written advice on the exact source material and business model.

## Reference links

- [Copyright Act 98 of 1978 — South African Government](https://www.gov.za/documents/copyright-act-16-apr-2015-0942)
- [National Soccer League t/a Premier Soccer League v Gidani (Pty) Ltd (2014)](https://www.saflii.org/za/cases/ZAGPJHC/2014/33.html)
- [DTIC/WIPO guide on creative expression and database compilations](https://www.thedtic.gov.za/wp-content/uploads/publication-CCRD_Creative_Expressions.pdf)
- [Trade Marks Act 194 of 1993 — South African Government](https://www.gov.za/sites/default/files/gcis_document/201409/act194of1993.pdf)
- [Consumer Protection Act 68 of 2008 — South African Government](https://www.gov.za/sites/default/files/32186_467.pdf)
- [Electronic Communications and Transactions Act 25 of 2002 — South African Government](https://www.gov.za/documents/electronic-communications-and-transactions-act)
- [Constitutional Court judgment, [2026] ZACC 26](https://www.concourt.org.za/index.php/11-former-jud%20ges/index.php/judgement/index.php/judgement/647-ex-parte-president-of-the-republic-of-south-africa-in-re-constitutionality-of-the-copyright-amendment-bill-and-the-performers-protection-amendment-bill-cct306-24)
- [Parliament: Copyright Amendment Bill B13-2017](https://www.parliament.gov.za/bill/2291650)
- [SA Legal Academy report, 20 November 2026](https://legalacademy.co.za/news/read/intellectual-property-parliamentary-committee-updated-on-status-of-amending-legislation)
- [Shoprite Checkers Sixty60 promotional-rules PDF](https://www.termsconditions.co.za/content/dam/ShopriteGroup/Terms/PDFS/Checkers-Sixty60-Spot-Shop-And-Win.pdf) — promotion-specific clauses, not general terms for every Shoprite document or platform.
