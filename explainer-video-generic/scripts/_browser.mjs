// Shared helpers for the Node scripts: locate Playwright, a Chromium-family browser and ffmpeg on any OS.
import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const IS_WIN = process.platform === 'win32';

function tryRequire(name, base) {
  try { return (base ? createRequire(path.join(base, 'x.js')) : require)(name); } catch (e) { return null; }
}

/** playwright-core / playwright from: XV_PLAYWRIGHT, local node_modules, the global npm root, NODE_PATH. */
export function loadPlaywright() {
  const bases = [];
  if (process.env.XV_PLAYWRIGHT) bases.push(process.env.XV_PLAYWRIGHT);
  bases.push(process.cwd());
  const g = spawnSync(IS_WIN ? 'npm.cmd' : 'npm', ['root', '-g'], { encoding: 'utf8', shell: IS_WIN });
  if (g.status === 0 && g.stdout.trim()) bases.push(path.join(g.stdout.trim(), 'x'));
  for (const p of (process.env.NODE_PATH || '').split(path.delimiter).filter(Boolean)) bases.push(path.join(p, 'x'));
  for (const name of ['playwright-core', 'playwright']) {
    const direct = tryRequire(name);
    if (direct && direct.chromium) return direct;
    for (const b of bases) {
      const m = tryRequire(name, b) || tryRequire(path.join(b, '..', name));
      if (m && m.chromium) return m;
      const m2 = tryRequire(path.join(b, 'node_modules', name));
      if (m2 && m2.chromium) return m2;
    }
  }
  throw new Error('Playwright not found. Run `npm i -g playwright` (then `npx playwright install chromium`), or set XV_PLAYWRIGHT to the folder containing node_modules.');
}

function systemBrowsers() {
  const pf = process.env['ProgramFiles'] || 'C:\\Program Files', pf86 = process.env['ProgramFiles(x86)'] || 'C:\\Program Files (x86)', la = process.env.LOCALAPPDATA || '';
  return IS_WIN ? [
    path.join(pf, 'Google/Chrome/Application/chrome.exe'), path.join(pf86, 'Google/Chrome/Application/chrome.exe'), path.join(la, 'Google/Chrome/Application/chrome.exe'),
    path.join(pf86, 'Microsoft/Edge/Application/msedge.exe'), path.join(pf, 'Microsoft/Edge/Application/msedge.exe'),
  ] : process.platform === 'darwin' ? [
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge', '/Applications/Chromium.app/Contents/MacOS/Chromium',
  ] : ['/usr/bin/google-chrome', '/usr/bin/google-chrome-stable', '/usr/bin/chromium', '/usr/bin/chromium-browser', '/usr/bin/microsoft-edge'];
}

/** Launch headless Chromium: XV_CHROME > Playwright-managed browser > installed Chrome/Edge. */
export async function launchBrowser(extraArgs = []) {
  const { chromium } = loadPlaywright();
  const args = ['--autoplay-policy=no-user-gesture-required', '--disable-dev-shm-usage', '--allow-file-access-from-files', ...extraArgs];
  if (process.platform === 'linux') args.push('--no-sandbox');
  const tries = [];
  if (process.env.XV_CHROME) tries.push({ executablePath: process.env.XV_CHROME });
  tries.push({});
  for (const p of systemBrowsers()) if (fs.existsSync(p)) tries.push({ executablePath: p });
  let last;
  for (const t of tries) {
    try { return await chromium.launch({ headless: true, args, ...t }); } catch (e) { last = e; }
  }
  throw new Error('No usable browser. Run `npx playwright install chromium`, or set XV_CHROME to a Chrome/Edge executable.\n' + (last ? last.message.split('\n')[0] : ''));
}

function works(cmd) { const r = spawnSync(cmd, ['-version'], { encoding: 'utf8' }); return r.status === 0; }

/** FFMPEG env > ffmpeg on PATH > imageio_ffmpeg (Python) bundled binary. */
export function findFfmpeg() {
  if (process.env.FFMPEG && fs.existsSync(process.env.FFMPEG)) return process.env.FFMPEG;
  if (works('ffmpeg')) return 'ffmpeg';
  for (const py of IS_WIN ? ['python', 'py'] : ['python3', 'python']) {
    const r = spawnSync(py, ['-c', 'import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())'], { encoding: 'utf8' });
    if (r.status === 0 && fs.existsSync(r.stdout.trim())) return r.stdout.trim();
  }
  throw new Error('ffmpeg not found. Install ffmpeg, `pip install imageio-ffmpeg`, or set FFMPEG to the binary path.');
}

/** Pick an H.264 encoder that this ffmpeg build actually has. */
export function pickH264(ff, bitrate, preferred) {
  const out = spawnSync(ff, ['-hide_banner', '-encoders'], { encoding: 'utf8' }).stdout || '';
  const have = new Set([...out.matchAll(/^\s*V\S+\s+(\S+)/gm)].map(m => m[1]));
  const order = preferred ? [preferred] : ['libx264', 'libopenh264', 'h264_nvenc', 'h264_qsv', 'h264_amf', 'h264_videotoolbox', 'h264_mf'];
  const name = order.find(n => have.has(n));
  if (!name) throw new Error('This ffmpeg has no H.264 encoder (tried ' + order.join(', ') + ').');
  const br = ['-b:v', bitrate, '-maxrate', bitrate];
  if (name === 'libx264') return { name, args: ['-c:v', name, '-preset', 'medium', '-crf', '17', '-profile:v', 'high'] };
  if (name === 'libopenh264') return { name, args: ['-c:v', name, '-profile:v', 'high', ...br] };
  return { name, args: ['-c:v', name, ...br] };
}

export { IS_WIN };
