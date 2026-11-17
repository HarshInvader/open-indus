// Screenshots of the explore pages with headless Chromium over the DevTools protocol.
// No server, no installs: Node's built-in WebSocket talks to a headless shell that is
// killed at the end. Usage: node shots/shoot.mjs a b c wordmark index
// Writes shots/<page>-<width>-<theme>.png (full page, capped at 6000 px tall).
import { spawn } from 'node:child_process';
import { writeFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { homedir } from 'node:os';

const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(here, '..');
const BIN = process.env.CHROME || `${homedir()}/Library/Caches/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-mac-arm64/chrome-headless-shell`;
const pages = process.argv.slice(2);
// CLIP=x,y,w,h captures one region at 2x for close-ups (1440 wide only), named <page>-detail-<theme>.png
const CLIP = process.env.CLIP ? process.env.CLIP.split(',').map(Number) : null;
const port = 9333 + Math.floor(Math.random() * 400);
const proc = spawn(BIN, [`--remote-debugging-port=${port}`, '--hide-scrollbars', '--allow-file-access-from-files', 'about:blank'], { stdio: 'ignore' });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function target() {
  for (let i = 0; i < 50; i++) {
    try { const r = await fetch(`http://127.0.0.1:${port}/json/list`); const j = await r.json(); const p = j.find((t) => t.type === 'page'); if (p) return p.webSocketDebuggerUrl; } catch {}
    await sleep(150);
  }
  throw new Error('no browser');
}

try {
  const ws = new WebSocket(await target());
  await new Promise((r) => ws.addEventListener('open', r, { once: true }));
  let id = 0; const waits = new Map();
  ws.addEventListener('message', (e) => { const m = JSON.parse(e.data); if (m.id && waits.has(m.id)) { waits.get(m.id)(m); waits.delete(m.id); } });
  const send = (method, params = {}) => new Promise((r) => { const i = ++id; waits.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
  await send('Page.enable');
  for (const p of pages) {
    for (const width of CLIP ? [1440] : [1440, 390]) {
      for (const theme of ['light', 'dark']) {
        await send('Emulation.setDeviceMetricsOverride', { width, height: width === 390 ? 844 : 900, deviceScaleFactor: 1, mobile: width === 390 });
        await send('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-color-scheme', value: theme }] });
        await send('Page.navigate', { url: `file://${root}/${p}.html?theme=${theme}` });
        await sleep(3200); // fonts, images and entrance animations
        const m = await send('Runtime.evaluate', { expression: 'JSON.stringify([document.documentElement.scrollWidth, document.documentElement.scrollHeight])', returnByValue: true });
        const [sw, sh] = JSON.parse(m.result.result.value);
        const h = Math.min(sh, 6000);
        await send('Emulation.setDeviceMetricsOverride', { width, height: h, deviceScaleFactor: 1, mobile: width === 390 });
        await sleep(500);
        const shot = await send('Page.captureScreenshot', CLIP ? { format: 'png', clip: { x: CLIP[0], y: CLIP[1], width: CLIP[2], height: CLIP[3], scale: 1 } } : { format: 'png', captureBeyondViewport: false });
        const out = CLIP ? `${here}/${p}-detail-${theme}.png` : `${here}/${p}-${width}-${theme}.png`;
        writeFileSync(out, Buffer.from(shot.result.data, 'base64'));
        console.log(out.replace(root + '/', ''), `scrollWidth=${sw}`, `height=${sh}`);
      }
    }
  }
  ws.close();
} finally {
  proc.kill('SIGTERM');
}
