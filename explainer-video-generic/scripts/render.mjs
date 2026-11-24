#!/usr/bin/env node
// Drive the explainer-video HTML engine in headless Chromium: check, stills, contact sheets, and MP4 export.
//
//   node render.mjs check  <video.html> [--json timing.json]
//   node render.mjs sheet  <video.html> --out sheet.png [--times 1,5,9 | per-scene default] [--cols 3] [--subs]
//   node render.mjs still  <video.html> --t 12.5 --out frame.png [--subs] [--no-captions]
//   node render.mjs mp4    <video.html> --out video.mp4 [--from 0 --to 5] [--scale 1|2] [--bitrate 8M] [--subs] [--no-captions] [--codec libx264]
//
// Every frame is rendered deterministically ("the picture at time t") and piped to ffmpeg (H.264, fixed fps, yuv420p, faststart),
// so there are no dropped frames. Needs: node, ffmpeg (with any H.264 encoder), playwright(-core) and a Chromium-family browser.
// Run `python scripts/check_env.py` to verify the toolchain.
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { spawn, spawnSync } from 'node:child_process';
import { launchBrowser, findFfmpeg, pickH264 } from './_browser.mjs';

function args(argv) {
  const o = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith('--')) { const k = a.slice(2); const nx = argv[i + 1]; if (nx === undefined || nx.startsWith('--')) o[k] = true; else { o[k] = nx; i++; } }
    else o._.push(a);
  }
  return o;
}
const MIME = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.mjs': 'text/javascript', '.json': 'application/json', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.svg': 'image/svg+xml', '.webp': 'image/webp', '.mp4': 'video/mp4', '.webm': 'video/webm', '.mov': 'video/quicktime', '.mp3': 'audio/mpeg', '.wav': 'audio/wav' };
// Video assets are served as all-keyframe proxies so per-frame seeking is fast and exact.
const PROXY = !process.argv.includes('--no-proxy');
let FF = null;
function proxyFor(p) {
  const dir = path.join(path.dirname(p), '.xvproxy'); const out = path.join(dir, path.basename(p) + '.intra.mp4');
  if (fs.existsSync(out) && fs.statSync(out).mtimeMs >= fs.statSync(p).mtimeMs) return out;
  fs.mkdirSync(dir, { recursive: true });
  const enc = pickH264(FF, '20M');
  const r = spawnSync(FF, ['-y', '-v', 'error', '-i', p, '-an', ...enc.args, '-g', '1', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out]);
  return r.status === 0 ? out : p;
}
function serve(root) {
  return new Promise(res => {
    const srv = http.createServer((req, rsp) => {
      let p = path.join(root, decodeURIComponent(req.url.split('?')[0]));
      if (!p.startsWith(root) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { rsp.writeHead(404); return rsp.end(); }
      if (PROXY && /\.(mp4|mov|m4v|webm)$/i.test(p) && !p.includes('.xvproxy')) p = proxyFor(p);
      const size = fs.statSync(p).size, type = MIME[path.extname(p).toLowerCase()] || 'application/octet-stream';
      const range = req.headers.range;
      if (range) { // needed for video seeking
        const m = /bytes=(\d*)-(\d*)/.exec(range); const s = m[1] ? parseInt(m[1], 10) : 0; const e = m[2] ? parseInt(m[2], 10) : size - 1;
        rsp.writeHead(206, { 'Content-Type': type, 'Content-Range': `bytes ${s}-${e}/${size}`, 'Accept-Ranges': 'bytes', 'Content-Length': e - s + 1, 'Access-Control-Allow-Origin': '*' });
        fs.createReadStream(p, { start: s, end: e }).pipe(rsp);
      } else { rsp.writeHead(200, { 'Content-Type': type, 'Content-Length': size, 'Accept-Ranges': 'bytes', 'Access-Control-Allow-Origin': '*' }); fs.createReadStream(p).pipe(rsp); }
    });
    srv.listen(0, '127.0.0.1', () => res(srv));
  });
}

async function main() {
  const a = args(process.argv.slice(2));
  const [cmd, html] = a._;
  if (!cmd || !html) { console.error('Usage: node render.mjs check|sheet|still|mp4 <video.html> [options]'); process.exit(2); }
  const abs = path.resolve(html); const root = path.dirname(abs);
  if (!fs.existsSync(abs)) { console.error('Not found: ' + abs); process.exit(2); }
  if (cmd === 'mp4' || PROXY) { try { FF = findFfmpeg(); } catch (e) { if (cmd === 'mp4') throw e; } }
  const srv = await serve(root); const port = srv.address().port;
  const browser = await launchBrowser();
  const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
  const logs = [];
  page.on('pageerror', e => logs.push('pageerror: ' + e.message));
  page.on('console', m => { if (m.type() === 'error') logs.push('console: ' + m.text()); });
  let code = 0;
  try {
    await page.goto(`http://127.0.0.1:${port}/${encodeURIComponent(path.basename(abs))}?render=1`, { waitUntil: 'load' });
    await page.waitForFunction(() => window.__XV && window.__XV.ready, null, { timeout: 30000 });
    await page.evaluate(() => window.__XV.ready);
    const info = await page.evaluate(() => window.__XV.info());

    if (cmd === 'check') {
      const r = await page.evaluate(step => window.__XV.check(step), parseFloat(a.step || '0.1'));
      const timing = await page.evaluate(() => window.__XV.timing());
      if (a.json) fs.writeFileSync(a.json, JSON.stringify(timing, null, 2));
      console.log(`## ${info.title} (${info.slug}) total ${r.total.toFixed(1)}s, ${r.scenes.length} scenes${info.fit ? ', timing fitted to narration audio (FIT)' : ''}`);
      r.scenes.forEach(s => console.log(`  ${s.id.padEnd(5)} ${s.start.toFixed(1).padStart(6)}s +${s.duration.toFixed(1).padStart(5)}s  ${s.title}`));
      if (r.errors.length) { console.log('ERRORS (render)'); r.errors.forEach(e => console.log('  ' + e)); }
      if (r.warnings.length) { console.log('WARNINGS'); r.warnings.forEach(e => console.log('  ' + e)); }
      if (logs.length) { console.log('BROWSER ERRORS'); logs.slice(0, 20).forEach(e => console.log('  ' + e)); }
      if (r.ok && !logs.length) console.log('OK: no render errors, nothing outside the safe area');
      code = r.errors.length || logs.length ? 1 : 0;
    } else if (cmd === 'sheet') {
      let times;
      if (a.times && a.times !== true) times = String(a.times).split(',').map(Number);
      else times = info.scenes.flatMap(s => [s.start + Math.min(1.5, s.duration * 0.2), s.start + s.duration * 0.55, s.start + s.duration - 0.6]);
      const url = await page.evaluate(([t, c, sub]) => window.__XV.sheet(t, c, { subs: sub }), [times, parseInt(a.cols || '3', 10), !!a.subs]);
      const out = a.out || 'sheet.png'; fs.writeFileSync(out, Buffer.from(url.split(',')[1], 'base64'));
      console.log(`Saved contact sheet: ${out} (${times.length} frames)`);
    } else if (cmd === 'still') {
      const t = parseFloat(a.t || '0'); const url = (await page.evaluate(([T, sub, cap]) => window.__XV.frames(T, 1, 1, { subs: sub, captions: cap }, 'image/png'), [t, !!a.subs, !a['no-captions']]))[0];
      const out = a.out || `still_${t}.png`; fs.writeFileSync(out, Buffer.from(url.split(',')[1], 'base64')); console.log(`Saved still: ${out} (t=${t}s)`);
    } else if (cmd === 'mp4') {
      const fps = info.fps, scale = parseInt(a.scale || '1', 10), from = parseFloat(a.from || '0'), to = Math.min(parseFloat(a.to || String(info.total)), info.total);
      const out = a.out || `${info.slug}.mp4`; const br = a.bitrate || (scale === 2 ? '16M' : '8M');
      const n = Math.round((to - from) * fps); const opts = { captions: !a['no-captions'], subs: !!a.subs };
      const enc = pickH264(FF, br, a.codec && a.codec !== true ? a.codec : undefined);
      console.log(`Encoding with ${enc.name}, ${1920 * scale}x${1080 * scale} @ ${fps}fps`);
      const ff = spawn(FF, ['-y', '-hide_banner', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-',
        ...enc.args, '-g', String(fps * 2), '-r', String(fps), '-vf', 'scale=in_range=pc:out_range=tv,format=yuv420p', '-color_range', 'tv', '-movflags', '+faststart', '-an', out], { stdio: ['pipe', 'inherit', 'inherit'] });
      ff.stdin.on('error', () => {}); // ffmpeg exit is reported via the close code below
      const t0 = Date.now(); const batch = 15; let done = 0;
      for (let f = 0; f < n; f += batch) {
        const T0 = from + f / fps; const k = Math.min(batch, n - f);
        const urls = await page.evaluate(([T, k2, s, o]) => window.__XV.frames(T, k2, s, o, 'image/jpeg', 0.95), [T0, k, scale, opts]);
        for (const u of urls) { if (!ff.stdin.write(Buffer.from(u.slice(u.indexOf(',') + 1), 'base64'))) await new Promise(r => ff.stdin.once('drain', r)); }
        done += urls.length;
        if (f % (fps * 10) < batch) process.stdout.write(`\r  ${(done / fps).toFixed(0)} / ${((to - from)).toFixed(0)} s  (${((Date.now() - t0) / 1000).toFixed(0)} s elapsed)   `);
      }
      ff.stdin.end(); const rc = await new Promise(r => ff.on('close', r)); process.stdout.write('\n');
      if (rc !== 0) throw new Error('ffmpeg failed (exit code ' + rc + ')');
      const st = fs.statSync(out);
      console.log(`Wrote MP4: ${out} (${done} frames, ${(done / fps).toFixed(1)}s, ${(st.size / 1048576).toFixed(1)} MB, rendered in ${((Date.now() - t0) / 1000).toFixed(0)}s)`);
      if (logs.length) { console.log('BROWSER ERRORS'); logs.slice(0, 20).forEach(e => console.log('  ' + e)); }
    } else { console.error('Unknown command: ' + cmd); code = 2; }
  } finally { await browser.close(); srv.close(); }
  process.exit(code);
}
main().catch(e => { console.error('ERROR: ' + e.message); process.exit(1); });
