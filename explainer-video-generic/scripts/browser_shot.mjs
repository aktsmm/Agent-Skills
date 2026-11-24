#!/usr/bin/env node
// Screenshot an HTML file (or URL) with headless Chromium. Used by icons.py to build icon contact sheets.
//   node browser_shot.mjs <file.html|url> <out.png> [--width 1200] [--height 600]
import path from 'node:path';
import fs from 'node:fs';
import { pathToFileURL } from 'node:url';
import { launchBrowser } from './_browser.mjs';

const [src, out, ...rest] = process.argv.slice(2);
if (!src || !out) { console.error('Usage: node browser_shot.mjs <file.html|url> <out.png> [--width N] [--height N]'); process.exit(2); }
const opt = k => { const i = rest.indexOf('--' + k); return i >= 0 ? parseInt(rest[i + 1], 10) : undefined; };
const url = /^https?:|^file:/.test(src) ? src : pathToFileURL(path.resolve(src)).href;
const browser = await launchBrowser();
try {
  const page = await browser.newPage({ viewport: { width: opt('width') || 1200, height: opt('height') || 600 } });
  await page.goto(url, { waitUntil: 'load' });
  await page.waitForTimeout(600);
  await page.screenshot({ path: path.resolve(out), fullPage: true });
  console.log('Saved ' + path.resolve(out) + ' (' + fs.statSync(out).size + ' bytes)');
} finally { await browser.close(); }
