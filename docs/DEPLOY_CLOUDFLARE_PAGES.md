# Publish the web app with Cloudflare Pages

This guide assumes you control the GitHub repository and domain. Keep the repository private while it contains pamphlet files, AI candidates or any material not cleared for public distribution.

## 1. Put the project in your GitHub account

1. Create or sign in to your own GitHub account and enable two-factor authentication.
2. Create a **private** repository, for example `mzansi-smart-basket`.
3. Upload the contents of this project folder to the repository root (not the outer ZIP folder).
4. Check that `.env`, API keys, Android keystores and private source pamphlets are not committed.
5. Open the repository's **Settings → Secrets and variables → Actions → New repository secret**. Add `GEMINI_API_KEY` with your own Gemini API key. Do not put it in `index.html`, `deals.json`, `MZANSI_FEED_URL` or the Android app.

## 2. Connect Cloudflare Pages

1. Create a Cloudflare account using an email address you control and enable two-factor authentication. The basic static Pages hosting tier can start on the Free plan; Cloudflare currently lists up to 500 builds per month and free static-asset requests on that plan. Limits and paid products can change, so check Cloudflare's [current Pages limits](https://developers.cloudflare.com/pages/platform/limits/) and [pricing](https://www.cloudflare.com/plans/) before launch. Your domain, API usage, legal/accounting advice and marketing are separate costs.
2. Open **Workers & Pages → Create → Pages → Connect to Git**.
3. Select your GitHub account and the private `mzansi-smart-basket` repository. Authorise access only to that repository if the option is offered.
4. Set the production branch to `main` (or the branch you actually use).
5. Set **Build command** to `npm run build:web` and **Build output directory** to `www`.
6. Leave the root/build directory at the repository root. The project uses `package.json` there.
7. Start the first deployment and open the generated `*.pages.dev` address. Test the home screen, basket, province selection, source links, privacy page and terms page.

Cloudflare Pages' Git integration should rebuild after you push a reviewed `deals.json` update. The included scheduled GitHub Action only generates a pending review candidate; it does not publish live prices automatically.

## 3. Add your own domain

1. Buy/register a domain using an account and email address you own. Check name availability and trade-mark conflicts first.
2. In the Pages project, open **Custom domains → Set up a custom domain** and enter the domain you control.
3. Follow Cloudflare's DNS instructions exactly. Wait until Cloudflare reports the domain as active and HTTPS is working.
4. Test `https://YOUR-DOMAIN/`, `https://YOUR-DOMAIN/privacy.html` and `https://YOUR-DOMAIN/deals.json`.
5. Keep domain renewal, DNS and Cloudflare account recovery details under your control.

## 4. Connect Android to your live feed

The browser version can use the relative `./deals.json` file hosted on the same Pages domain. For the Android bundle, set the HTTPS feed URL before building:

**Windows PowerShell**

```powershell
$env:MZANSI_FEED_URL = "https://YOUR-DOMAIN/deals.json"
npm run build:web
npx cap sync android
```

**macOS / Linux**

```bash
MZANSI_FEED_URL="https://YOUR-DOMAIN/deals.json" npm run build:web
npx cap sync android
```

Use the exact HTTPS URL that you tested in a browser. Do not point the app at a local computer path or an API key-bearing endpoint.

## 5. First deployment checklist

- Replace every `[INSERT ...]` placeholder in `terms.html` and `privacy.html`.
- Do not treat the current 75-item demo prices as live offers.
- Only process pamphlet/source material that you are legally allowed to access and use.
- Human-check every price, pack size, date, region and loyalty condition before publishing `deals.json` as verified.
- Keep a public correction/rights contact address on the site.
- Do not add analytics, advertising or affiliate tracking until the privacy notice and consent/notice flows have been updated and reviewed.
