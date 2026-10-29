#!/usr/bin/env python3
"""Self-test for the skill: run it after any change, before you publish.

Checks:
  1. SKILL.md frontmatter: name matches the folder name or "ui-ref-jam", description present and at most 1024 characters.
  2. Every repo path mentioned in backticks in the Markdown files exists.
  3. Every Python file compiles; the Node script parses (if node is installed); the shell script parses.
  4. The UI UX Pro Max search runs and returns results.
  5. hover_rules.py extracts hover rules from a small stylesheet.
  6. embed_images.py builds both board templates with generated test images, leaving no %%IMG_ placeholder.
  7. The log builder turns a two-entry log into index.html.
Usage: python3 tests/selftest.py        (exit code 0 = all passed)
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fails = []


def check(name, ok, detail=''):
    print(('PASS ' if ok else 'FAIL ') + name + (f'  ({detail})' if detail else ''))
    if not ok:
        fails.append(name)


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=120, **kw)


# 1. frontmatter
skill = open(os.path.join(ROOT, 'SKILL.md'), encoding='utf-8').read()
m = re.match(r'---\n(.*?)\n---\n', skill, re.S)
check('frontmatter block', bool(m))
if m:
    fm = dict(re.findall(r'^(\w+): (.*)$', m.group(1), re.M))
    check('name set', fm.get('name') in (os.path.basename(ROOT), 'ui-ref-jam'), fm.get('name', ''))
    d = fm.get('description', '')
    check('description length <= 1024', 0 < len(d) <= 1024, f'{len(d)} chars')

# 2. referenced paths
missing = []
for dirpath, _, files in os.walk(ROOT):
    if '/vendor/' in dirpath + '/' or '/.git' in dirpath or '/references/rea' in dirpath:
        continue
    for fn in files:
        if not fn.endswith('.md'):
            continue
        text = open(os.path.join(dirpath, fn), encoding='utf-8').read()
        for ref in re.findall(r'`((?:scripts|references|assets|vendor|tests)/[^`\s<>*]+)`', text):
            ref = ref.rstrip('.,;:')
            if not os.path.exists(os.path.join(ROOT, ref)):
                missing.append(f'{fn}: {ref}')
check('referenced paths exist', not missing, '; '.join(missing[:8]))

# 3. syntax
bad = []
for dirpath, _, files in os.walk(ROOT):
    if '/.git' in dirpath:
        continue
    for fn in files:
        p = os.path.join(dirpath, fn)
        if fn.endswith('.py'):
            r = run([sys.executable, '-m', 'py_compile', p])
            if r.returncode:
                bad.append(fn)
check('python files compile', not bad, ', '.join(bad))
if shutil.which('node'):
    r = run(['node', '--check', os.path.join(ROOT, 'scripts/sweep.cjs')])
    check('sweep.cjs parses', r.returncode == 0, r.stderr.strip()[:200])
r = run(['bash', '-n', os.path.join(ROOT, 'scripts/check_board.sh')])
check('check_board.sh parses', r.returncode == 0, r.stderr.strip()[:200])

# 4. search
r = run([sys.executable, os.path.join(ROOT, 'vendor/ui-ux-pro-max/scripts/search.py'), 'scroll reveal', '--domain', 'gsap', '-n', '2'])
check('ui-ux-pro-max search', r.returncode == 0 and len(r.stdout.strip()) > 40, r.stderr.strip()[:200])

tmp = tempfile.mkdtemp(prefix='ui-ref-jam-test-')
try:
    # 5. hover rules
    css = os.path.join(tmp, 'a.css')
    open(css, 'w').write('.btn{color:red}.btn:hover{color:blue;transform:scale(1.02)}a:hover span{opacity:.5}')
    r = run([sys.executable, os.path.join(ROOT, 'scripts/hover_rules.py'), css])
    check('hover_rules extracts rules', r.returncode == 0 and ':hover' in r.stdout, r.stderr.strip()[:200])

    # 6. embed images into both templates
    try:
        from PIL import Image, ImageDraw
        def img(path, colour):
            im = Image.new('RGBA', (400, 460), (0, 0, 0, 0))
            ImageDraw.Draw(im).rounded_rectangle((60, 60, 340, 420), 40, fill=colour)
            im.save(path)
        imgs = {}
        for k, c in [('front', (30, 30, 30, 255)), ('back', (90, 90, 90, 255))]:
            imgs[k] = os.path.join(tmp, k + '.png'); img(imgs[k], c)
        for k in ['workshop', 'knit', 'spools', 'swatches', 'screenprint', 'cones', 'jeans', 'cutting', 'sketch', 'colour']:
            imgs[k] = imgs['front']
    except ImportError:
        imgs = None
        check('Pillow installed (needed for image tests)', False)
    if imgs:
        for tpl in ['assets/motion-samples.tpl.html', 'assets/example-board.tpl.html']:
            keys = sorted(set(re.findall(r'%%IMG_(\w+)%%', open(os.path.join(ROOT, tpl), encoding='utf-8').read())))
            args = []
            for k in keys:
                args += ['--img', f'{k}={imgs.get(k, imgs["front"])}']
            out = os.path.join(tmp, os.path.basename(tpl).replace('.tpl', ''))
            r = run([sys.executable, os.path.join(ROOT, 'scripts/embed_images.py'), os.path.join(ROOT, tpl), out, *args,
                     '--preview', out.replace('.html', '.preview.html')])
            left = re.findall(r'%%IMG_\w+%%', open(out, encoding='utf-8').read()) if os.path.exists(out) else ['(no output)']
            check(f'embed_images {os.path.basename(tpl)}', r.returncode == 0 and not left, (r.stderr.strip() or ' '.join(left))[:200])
            if 'motion' in tpl and os.path.exists(out):
                check('cut-outs keep transparency (webp, not jpeg)', 'data:image/webp' in open(out, encoding='utf-8').read())
        print('   previews in', tmp)

    # 7. log builder
    log = os.path.join(tmp, 'log')
    os.makedirs(log)
    for fn in ['build.py', 'viewer.tpl.html', 'append.py', 'README.md']:
        shutil.copy(os.path.join(ROOT, 'assets/log', fn), log)
    open(os.path.join(log, 'decisions.md'), 'w', encoding='utf-8').write(
        '# Decisions\n\n### D-001\n- date: 2026-01-01\n- type: board\n- private: no\n- title.zh: 测试\n- title.en: Test\n- why.zh: 未说明\n- why.en: Not stated\n')
    open(os.path.join(log, 'changes.md'), 'w', encoding='utf-8').write(
        '# Changes\n\n### C-001\n- date: 2026-01-01\n- type: deploy\n- private: no\n- title.zh: 测试\n- title.en: Test\n')
    r = run([sys.executable, os.path.join(log, 'build.py')])
    idx = os.path.join(log, 'index.html')
    ok = r.returncode == 0 and os.path.exists(idx) and 'D-001' in open(idx, encoding='utf-8').read()
    check('log build.py', ok, r.stderr.strip()[:200])
finally:
    if not fails:
        shutil.rmtree(tmp, ignore_errors=True)

print('\n' + ('ALL PASSED' if not fails else f'{len(fails)} FAILED: ' + ', '.join(fails)))
sys.exit(1 if fails else 0)
