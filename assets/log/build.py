#!/usr/bin/env python3
"""Builds log/index.html, the viewer for decisions.md and changes.md (format in README.md).

The page is self-contained: the entries are embedded as JSON, images are linked from img/. It switches the whole log
between Chinese and English, filters decisions / changes / types, and has a case-study mode that hides private entries.
Usage: python3 log/build.py
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REPEAT = {'quote', 'img', 'links'}


def parse(path, kind):
    if not os.path.exists(path):
        return []
    entries, cur = [], None
    for raw in open(path, encoding='utf-8'):
        line = raw.rstrip('\n')
        m = re.match(r'^###\s+([DC]-\d+)\s*$', line)
        if m:
            cur = {'id': m.group(1), 'kind': kind}
            entries.append(cur)
            continue
        m = re.match(r'^- ([a-z.]+):\s?(.*)$', line)
        if cur is not None and m:
            k, v = m.group(1), m.group(2).strip()
            if k in REPEAT:
                parts = [p.strip() for p in v.split(' · ')] if k in ('img', 'links') else [v]
                cur.setdefault(k, []).extend(p for p in parts if p)
            else:
                cur[k] = v
    return entries


def main():
    data = parse(os.path.join(HERE, 'decisions.md'), 'decision') + parse(os.path.join(HERE, 'changes.md'), 'change')
    data.sort(key=lambda e: (e.get('date', ''), e.get('time', '99:99'), e['id']))
    tpl = open(os.path.join(HERE, 'viewer.tpl.html'), encoding='utf-8').read()
    out = tpl.replace('/*%%DATA%%*/[]', json.dumps(data, ensure_ascii=False))
    open(os.path.join(HERE, 'index.html'), 'w', encoding='utf-8').write(out)
    d = sum(e['kind'] == 'decision' for e in data)
    print(f'index.html: {d} decisions, {len(data) - d} changes, {sum(e.get("private") == "yes" for e in data)} private')


if __name__ == '__main__':
    main()
