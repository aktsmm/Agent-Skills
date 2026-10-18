// Render a deck HTML (sections with class "page", 1280x720 px) to PDF + per-page PNGs with headless Chrome.
// Usage: node render-deck.mjs <deck.html> [outDir]
// Needs playwright-core resolvable from the current directory (npm i playwright-core) and a Chrome/Edge binary
// (set CHROME_PATH or install one of the common paths). Exits 1 when any content slide overflows.
import { createRequire } from "node:module";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { resolve, basename } from "node:path";

const { chromium } = createRequire(process.cwd() + "/")("playwright-core");
const src = resolve(process.argv[2] ?? "deck.html");
const out = resolve(process.argv[3] ?? "out");
const stem = basename(src).replace(/\.html?$/i, "");
const exe = [process.env.CHROME_PATH, "/usr/bin/google-chrome", "/usr/bin/chromium", "C:/Program Files/Google/Chrome/Application/chrome.exe", "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"].find((p) => p && existsSync(p));
if (!exe) throw new Error("no Chrome found; set CHROME_PATH");
mkdirSync(out, { recursive: true });

// Evaluated as a string (a function body breaks under tsx/esbuild: "__name is not defined").
const OVERFLOW = `(() => [...document.querySelectorAll('.page.slide')].map((p, i) => {
  const ft = p.querySelector('.ft');
  const ftTop = ft ? ft.getBoundingClientRect().top : p.getBoundingClientRect().bottom;
  const cardOver = Math.max(0, ...[...p.querySelectorAll('.card')].map((c) => c.getBoundingClientRect().bottom - ftTop));
  const scrollOver = Math.max(0, ...[...p.querySelectorAll('.main, .side')].map((e) => e.scrollHeight - e.clientHeight), p.scrollHeight - p.clientHeight);
  return { page: [...document.querySelectorAll('.page')].indexOf(p) + 1, key: p.dataset.key || '', over: Math.round(Math.max(cardOver, scrollOver)) };
}))()`;

const browser = await chromium.launch({ executablePath: exe, args: ["--no-sandbox"] });
try {
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
  await page.setContent(readFileSync(src, "utf8"));
  await page.evaluate("document.fonts.ready");
  const report = await page.evaluate(OVERFLOW);
  await page.pdf({ path: `${out}/${stem}.pdf`, width: "1280px", height: "720px", printBackground: true, preferCSSPageSize: true });
  const total = await page.evaluate("document.querySelectorAll('.page').length");
  for (let i = 0; i < total; i++) {
    await page.evaluate(`document.querySelectorAll('.page').forEach((p, j) => { p.style.display = j === ${i} ? '' : 'none'; })`);
    await page.screenshot({ path: `${out}/${stem}-p${i + 1}.png`, clip: { x: 0, y: 0, width: 1280, height: 720 } });
  }
  writeFileSync(`${out}/${stem}-report.json`, JSON.stringify({ pages: total, slides: report }, null, 2));
  const bad = report.filter((r) => r.over > 0);
  console.log(`pdf: ${out}/${stem}.pdf (${total} pages)`);
  if (bad.length) {
    console.error("overflow:", JSON.stringify(bad));
    process.exitCode = 1;
  }
} finally {
  await browser.close();
}
