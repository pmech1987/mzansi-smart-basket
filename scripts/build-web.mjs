import { mkdirSync, rmSync, copyFileSync, readFileSync, writeFileSync, existsSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { spawnSync } from 'node:child_process';

const root = process.cwd();
const out = resolve(root, 'www');
rmSync(out, { recursive: true, force: true });
mkdirSync(out, { recursive: true });

let html = readFileSync(resolve(root, 'index.html'), 'utf8');
html = html.replace('<script src="https://cdn.tailwindcss.com/3.4.17"></script>', '<link rel="stylesheet" href="./app.css">');
html = html.replace('<script src="https://unpkg.com/lucide@0.460.0/dist/umd/lucide.min.js"></script>', '<script src="./vendor/lucide.min.js"></script>');
html = html.replace(/\s*<link rel="preconnect" href="https:\/\/fonts\.googleapis\.com" \/>/, '');
html = html.replace(/\s*<link rel="preconnect" href="https:\/\/fonts\.gstatic\.com" crossorigin \/>/, '');
html = html.replace(/\s*<link href="https:\/\/fonts\.googleapis\.com[^>]+>/, '');
html = html.replace('font-family: \'Inter\', -apple-system, BlinkMacSystemFont, sans-serif;', 'font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;');
// Load a small native bridge before the app script; in a browser it retains browser geolocation.
html = html.replace('  <script>\n    const STORAGE_KEY', '  <script src="./native-bridge.js"></script>\n  <script>\n    const STORAGE_KEY');
const feedUrl = process.env.MZANSI_FEED_URL?.trim();
if (feedUrl) {
  if (!/^https:\/\//i.test(feedUrl)) throw new Error('MZANSI_FEED_URL must be an HTTPS URL.');
  html = html.replace("feedUrl: './deals.json',", `feedUrl: ${JSON.stringify(feedUrl)},`);
}
writeFileSync(resolve(out, 'index.html'), html);

for (const file of ['manifest.json', 'deals.json', 'icon-192.png', 'icon-512.png', 'terms.html', 'privacy.html', 'price-methodology.html']) {
  if (existsSync(resolve(root, file))) copyFileSync(resolve(root, file), resolve(out, file));
}
mkdirSync(resolve(out, 'vendor'), { recursive: true });
const lucide = resolve(root, 'node_modules/lucide/dist/umd/lucide.min.js');
if (!existsSync(lucide)) throw new Error('Lucide UMD file not found. Run npm install before building.');
copyFileSync(lucide, resolve(out, 'vendor/lucide.min.js'));

const tailwindBin = process.platform === 'win32' ? 'npx.cmd' : 'npx';
const css = spawnSync(tailwindBin, ['tailwindcss', '-c', 'tailwind.config.cjs', '-i', 'styles/tailwind.input.css', '-o', resolve(out, 'app.css'), '--minify'], { cwd: root, stdio: 'inherit' });
if (css.status !== 0) throw new Error('Tailwind CSS build failed.');

const esbuildBin = process.platform === 'win32' ? 'npx.cmd' : 'npx';
const js = spawnSync(esbuildBin, ['esbuild', 'src/native-bridge.js', '--bundle', '--minify', '--format=iife', `--outfile=${resolve(out, 'native-bridge.js')}`], { cwd: root, stdio: 'inherit' });
if (js.status !== 0) throw new Error('Native bridge build failed.');

let sw = readFileSync(resolve(root, 'sw.js'), 'utf8');
sw = sw.replace("const APP_SHELL = ['./', './index.html', './manifest.json', './icon-192.png', './icon-512.png'];",
  "const APP_SHELL = ['./', './index.html', './manifest.json', './icon-192.png', './icon-512.png', './app.css', './vendor/lucide.min.js', './native-bridge.js', './terms.html', './privacy.html', './price-methodology.html'];");
writeFileSync(resolve(out, 'sw.js'), sw);
console.log(`Built offline-ready web app in ${out}`);
