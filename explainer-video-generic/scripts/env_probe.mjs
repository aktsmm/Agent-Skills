#!/usr/bin/env node
// Prints one JSON line: { playwright: bool, browser: bool, detail: string }. Used by check_env.py.
import { loadPlaywright, launchBrowser } from './_browser.mjs';

const out = { playwright: false, browser: false, detail: '' };
try {
  loadPlaywright();
  out.playwright = true;
  try { const b = await launchBrowser(); await b.close(); out.browser = true; }
  catch (e) { out.detail = e.message.split('\n')[0]; }
} catch (e) { out.detail = e.message; }
console.log(JSON.stringify(out));
