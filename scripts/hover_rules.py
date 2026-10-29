#!/usr/bin/env python3
"""List the :hover / :focus-visible rules in shipped stylesheets — the fastest way to learn a site's hover effects.

Usage: hover_rules.py file.css [more.css ...] [--max 60]
Prints one line per rule: selector tail { declarations }. Read the transition/transform values,
then the matching base rule (grep the selector without :hover) for durations and easing.
"""
import re, sys

args = [a for a in sys.argv[1:] if not a.startswith("--")]
limit = 60
if "--max" in sys.argv:
    limit = int(sys.argv[sys.argv.index("--max") + 1])
    args = [a for a in args if a != str(limit)]

for path in args:
    css = open(path, encoding="utf-8", errors="ignore").read()
    rules = re.findall(r"([^{}]*:(?:hover|focus-visible)[^{}]*)\{([^{}]*)\}", css)
    print(f"===== {path}: {len(rules)} rules")
    for sel, body in rules[:limit]:
        print(sel.strip()[-120:], "{", body.strip()[:200], "}")
