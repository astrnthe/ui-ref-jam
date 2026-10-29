#!/usr/bin/env node
// Robustness sweep: every page at every screen size, headless. Run it before handing work over (overnight, before a
// deploy) and again on the deployed draft. Prints one line per page and size, then the problems; exits 1 if any.
//
//   PW=<path to playwright module> node sweep.cjs --base http://127.0.0.1:4411 --pages index,products,work/example,404 \
//     [--ext .html] [--sizes 320x640,390x844,1440x900] [--checks ./site-checks.cjs] [--skip '.track, .carousel'] [--wait 2600]
//
// Built-in checks: script errors, a page wider than the screen (the browser then zooms the whole page out on phones),
// sideways scroll, and text past the screen edge. Content meant to sit off screen (a horizontal track, a carousel) is
// skipped when it is inside a sideways-scrolling box; otherwise mark it data-sweep-skip or list it with --skip.
// Site rules go in a --checks module:
//   module.exports = async (page, { w, h, pg }) => ['problem text', ...]   // return [] when fine
// The module runs after the built-in checks, with the page loaded and scrolled to the top. Good candidates: the rule
// just set (baselines on the grid), anything a script positions against something else checked at several scroll
// positions and after a reload halfway down, and what shows through clear strips at the very top.
// A single failure that passes when rerun alone is a timing fluke (an image arriving late); rerun before reporting it.
const path = require('path');
const arg = (k, d) => { const i = process.argv.indexOf(`--${k}`); return i > 0 ? process.argv[i + 1] : d; };
let pw; try { pw = require(process.env.PW || 'playwright'); } catch { console.error('Set PW to the playwright module path (e.g. the playwright-skill node_modules/playwright).'); process.exit(2); }
const BASE = arg('base', 'http://127.0.0.1:4411').replace(/\/$/, '');
const EXT = arg('ext', '');
const PAGES = arg('pages', 'index').split(',');
const SIZES = arg('sizes', '320x640,375x667,390x844,430x932,768x1024,1024x768,1280x800,1440x900,1920x1080').split(',').map((s) => s.split('x').map(Number));
const WAIT = +arg('wait', 2600);
const extra = arg('checks') ? require(path.resolve(arg('checks'))) : null;
const SKIP = ['[aria-hidden="true"]', '.sr-only', '[data-sweep-skip]', arg('skip')].filter(Boolean).join(', ');

(async () => {
  const b = await pw.chromium.launch(process.env.CHROME ? { executablePath: process.env.CHROME } : {});
  const problems = [];
  for (const [w, h] of SIZES) for (const pg of PAGES) {
    const mob = w < 700;
    const p = await b.newPage({ viewport: { width: w, height: h }, isMobile: mob, hasTouch: mob });
    const errs = [];
    p.on('pageerror', (e) => errs.push(e.message));
    p.on('console', (m) => m.type() === 'error' && !/favicon|net::/.test(m.text()) && errs.push(m.text().slice(0, 100)));
    const url = `${BASE}/${pg === 'index' && !EXT ? '' : pg + EXT}`;
    const bad = [];
    try {
      await p.goto(url, { waitUntil: 'load' }); await p.waitForTimeout(WAIT);
      const r = await p.evaluate((skip) => {
        const out = { iw: innerWidth };
        const inScroller = (e) => { for (let p = e.parentElement; p && p !== document.body; p = p.parentElement) if (/auto|scroll/.test(getComputedStyle(p).overflowX)) return true; return false; };
        scrollTo(150, 0); out.sx = scrollX; scrollTo(0, 0);
        out.wide = [...document.querySelectorAll('h1, h2, h3, h4, p, li, a, span, dt, dd, figcaption, button, label')]
          .filter((e) => { const q = e.getBoundingClientRect(); return q.width > 0 && (q.right > innerWidth + 1 || q.left < -1) && !e.closest(skip) && !inScroller(e); })
          .slice(0, 3).map((e) => `${(e.className && String(e.className).split(' ')[0]) || e.tagName}:"${(e.textContent || '').trim().slice(0, 14)}"`);
        return out;
      }, SKIP);
      if (r.iw !== w) bad.push(`page wider than screen (${r.iw})`);
      if (r.sx) bad.push(`scrolls sideways ${r.sx}`);
      if (r.wide.length) bad.push('text past edge ' + r.wide.join(' '));
      if (extra) bad.push(...(await extra(p, { w, h, pg })));
    } catch (e) { bad.push('failed: ' + e.message.split('\n')[0]); }
    if (errs.length) bad.unshift('errors ' + JSON.stringify(errs.slice(0, 2)));
    const line = `${w}x${h} ${pg.padEnd(22)} ${bad.length ? 'PROBLEM ' + bad.join(' | ') : 'ok'}`;
    console.log(line); if (bad.length) problems.push(line);
    await p.close();
  }
  console.log(`\n== ${SIZES.length * PAGES.length} checked, problems: ${problems.length}`); problems.forEach((x) => console.log(x));
  await b.close();
  process.exit(problems.length ? 1 : 0);
})();
