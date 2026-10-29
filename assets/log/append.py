#!/usr/bin/env python3
"""Appends new entries to the log with the next free IDs, then rebuilds index.html.

The input file holds entries in the README format, but with bare `### D` / `### C` headings. Two extra keys:
`img.src:` copies an existing image (or SVG) into img/ as <ID>-<n>.jpg, at most 1600px wide.
`img.url:` takes a screenshot of a web page (first screen, 1440×900) into img/<ID>-u<n>.jpg. This needs PW, the playwright
module path, and optionally CHROME. Without them the URL is kept in `links` instead.
Usage: python3 log/append.py new-entries.md     (Pillow is needed to resize images, otherwise they are copied as they are)
"""
import os
import re
import shutil
import subprocess
import sys
import time

LOG = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(LOG)


def last_id(fn, kind):
    ids = [int(m) for m in re.findall(r'(?m)^### ' + kind + r'-(\d+)', open(os.path.join(LOG, fn), encoding='utf-8').read())]
    return max(ids or [0])


def copy_img(src, dst):
    try:
        from PIL import Image
        im = Image.open(src).convert('RGB')
        im.thumbnail((1600, 4000))
        im.save(dst, quality=82)
    except Exception:
        shutil.copy(src, dst)


def shoot(url, dst):
    if not os.environ.get('PW'):
        return False
    js = ("const pw=require(process.env.PW);(async()=>{const b=await pw.chromium.launch(process.env.CHROME?{executablePath:process.env.CHROME}:{});"
          "const p=await b.newPage({viewport:{width:1440,height:900}});await p.goto(process.argv[1],{waitUntil:'load',timeout:30000});"
          "await p.waitForTimeout(6500);await p.screenshot({path:process.argv[2],type:'jpeg',quality:82});await b.close();})()"
          ".catch(e=>{console.error(e.message);process.exit(1)})")
    for attempt in range(3):  # Netlify sometimes closes the connection on deploy permalinks; a retry after a pause works
        if subprocess.run(['node', '-e', js, url, dst]).returncode == 0:
            return True
        time.sleep(4)
    return False


def main(path):
    blocks, cur = [], None
    for line in open(path, encoding='utf-8'):
        line = line.rstrip('\n')
        m = re.match(r'^###\s+([DC])\b', line)
        if m:
            cur = {'k': m.group(1), 'lines': []}
            blocks.append(cur)
        elif cur is not None and line.startswith('- '):
            cur['lines'].append(line)
    nxt = {'D': last_id('decisions.md', 'D'), 'C': last_id('changes.md', 'C')}
    out = {'D': [], 'C': []}
    os.makedirs(os.path.join(LOG, 'img'), exist_ok=True)
    for b in sorted(blocks, key=lambda b: next((l for l in b['lines'] if l.startswith('- date:')), '') + next((l for l in b['lines'] if l.startswith('- time:')), '')):
        nxt[b['k']] += 1
        bid = f"{b['k']}-{nxt[b['k']]:03d}"
        imgs, links, lines, n = [], [], [], 0
        for l in b['lines']:
            m = re.match(r'^- img\.(src|url):\s?(.*)$', l)
            if not m:
                lines.append(l)
                continue
            for spec in [s.strip() for s in m.group(2).split(' · ') if s.strip()]:
                target = re.sub(r'\s*\(.*\)\s*$', '', spec).strip()
                n += 1
                if m.group(1) == 'src':
                    sp = target if os.path.isabs(target) else os.path.join(ROOT, target)
                    if not os.path.exists(sp):
                        print('missing image', bid, target)
                        continue
                    ext = '.svg' if sp.lower().endswith('.svg') else '.jpg'
                    dst = f'img/{bid}-{n}{ext}'
                    (shutil.copy if ext == '.svg' else copy_img)(sp, os.path.join(LOG, dst))
                    imgs.append(dst)
                else:
                    dst = f'img/{bid}-u{n}.jpg'
                    if shoot(target, os.path.join(LOG, dst)):
                        imgs.append(dst)
                    else:
                        links.append(target)
        if links:
            lines.append('- links: ' + ' · '.join(links))
        if imgs:
            lines.append('- img: ' + ' · '.join(imgs))
        out[b['k']].append(f'### {bid}\n' + '\n'.join(lines))
        print('added', bid)
    for k, fn in (('D', 'decisions.md'), ('C', 'changes.md')):
        if out[k]:
            with open(os.path.join(LOG, fn), 'a', encoding='utf-8') as f:
                f.write('\n' + '\n\n'.join(out[k]) + '\n')
    subprocess.run([sys.executable, os.path.join(LOG, 'build.py')])


if __name__ == '__main__':
    main(sys.argv[1])
