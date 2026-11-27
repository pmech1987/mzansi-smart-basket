# Android setup — Mzansi Smart Basket

This project now has a Capacitor 8 configuration and an Android-ready web build. The generated `www/` directory is the bundled app content. The Android Studio project is created on the owner's computer by Capacitor; this ZIP does not contain a signed APK/AAB or a generated `android/` folder.

## Requirements

- A computer (Windows, macOS or Linux); building a Play Store app on an Android phone alone is not a practical workflow.
- Node.js 22 or newer.
- Android Studio 2025.2.1 or newer, with Android SDK Platform 36 installed.
- A working internet connection for the first dependency install and Gradle downloads.

## Create the Android project

1. Extract the ZIP into a folder you control.
2. Open a terminal in the project folder.
3. Run `npm install`.
4. Run `npm run build:web`.
5. Run `npm run cap:add:android` once. This creates the `android/` native project.
6. Add the permissions from `docs/android-manifest-permissions.xml` inside the `<manifest>` element in `android/app/src/main/AndroidManifest.xml` (above `<application>`).
7. Run `npm run cap:sync` whenever you change the web app or install/update a Capacitor plugin.
8. Run `npm run cap:open:android` and allow Android Studio to finish Gradle sync.
9. Connect an Android phone with USB debugging enabled, or create an emulator. Select the device and press Run.

The app asks for location permission only when the user taps the location button. Location is optional; manual province selection remains available.

## Connect a live feed

The app currently defaults to its bundled `deals.json`. After you own a domain and publish a reviewed `deals.json` file over HTTPS, build the Android bundle with the hosted feed URL:

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

Replace `YOUR-DOMAIN` with the domain you actually own. Keep the feed URL HTTPS and configure the server to allow cross-origin requests only as needed. The Feed panel also allows a user to change the feed URL manually.

## Build a release bundle

1. In Android Studio choose **Build → Generate Signed Bundle / APK**.
2. Choose **Android App Bundle (AAB)** for Google Play.
3. Create a new upload key and store the keystore and passwords in a secure password manager and two protected backups. Never commit them to GitHub or include them in this ZIP.
4. Keep the same package ID (`za.co.mzansismartbasket.app`) for all future updates after first publication. Change it before first Play Store release only if you choose a different permanent ID.
5. Test the signed build on physical Android devices before upload.

## Important before Google Play

- Google currently lists a one-time US$25 registration fee for full public distribution. If you register as an organisation, Google asks for a D-U-N-S number, organisation details and a website. Apply for the D-U-N-S number directly; Google says the application is free.
- New personal developer accounts created after 13 November 2023 must complete a closed test with at least 12 testers opted in continuously for 14 days before applying for production access. An organisation account may be more suitable once your Pty Ltd and organisation details are ready.
- Complete `terms.html` and `privacy.html` placeholders with your real operator/contact details.
- Host the privacy notice on a public HTTPS page and use that exact URL in Play Console.
- Complete Play Console's Data safety form accurately, including location use and any future ad/analytics/affiliate SDKs.
- Prepare app icon, screenshots, feature graphic, app description, content rating and test track.
- The current build is a working project setup, not a Play-approved app or a finished release binary.
