# ui-ref-jam

A [Claude Code](https://claude.com/claude-code) skill for designing a website through **live option boards** rather than text questions.

You give it reference sites. It takes each one apart, records how every effect is actually built, and rebuilds each candidate effect as a small live demo in your brand. The demos go on a local HTML board, with a recommended answer pre-selected on every question. Then it grills you round by round, reading your picks back from the page, until nothing is left open. Only then does it touch the real site.

It also covers the work around the boards:

- boards on a site that already exists (split before/after views, zoomed crops, CSS variants injected into the live page);
- overnight robustness sweeps with a morning brief;
- turning client feedback into a requirement ledger, with placeholder facts proven from your own files and screenshots of where the client said something;
- replacing drawn product placeholders with real, recolourable product photos;
- a bilingual (中文 / English) decision and change log for case studies.

The working language of the boards is Chinese with English terms; the method itself is written in English.

## Install

```bash
git clone https://github.com/<you>/ui-ref-jam ~/.claude/skills/ui-ref-jam
```

Claude Code picks the skill up from `~/.claude/skills/`. It triggers on things like "拆解这几个网站", "给我方案板", pasted client feedback, or a request for overnight testing. You can also ask for it by name.

## What's inside

| Path | What it is |
|---|---|
| `SKILL.md` | The workflow: take the references apart → matrix and rules pass → design tree → board → grill → change the real site |
| `references/` | Reverse-engineering method, demo recipes, grilling, hand-off (sweeps, briefs, client feedback, split sessions), product imagery |
| `assets/example-board.tpl.html` | A complete 9-question board with about 50 working demos (scroll, hover, nav, layout, smoothness, pinned scroll) |
| `assets/motion-samples.tpl.html` | Standalone samples: load-in timing, and turning a flat product photo without the "card flip" look |
| `assets/morning-brief.tpl.html` | Template for the overnight brief |
| `assets/log/` | The decision and change log: format, builder, appender, viewer |
| `scripts/` | Image embedding, board check, hover-rule extraction, a same-origin server for boards and the built site, a multi-size page sweep, garment-photo layering and mockups |
| `vendor/ui-ux-pro-max/` | UI UX Pro Max search tool and data (styles, palettes, fonts, UX rules, motion presets, stacks) |

The demo brand in the templates, **weft.example**, is fictional. Swap in your own tokens, copy and images.

## Requirements

- Claude Code with the built-in browser (boards are opened as local pages and picks are read back from `localStorage`).
- Python 3. Pillow is needed for image work. `scripts/imagery/garment.py` and `mockup.py` also need `numpy` and `scipy`.
- Node and Playwright for `scripts/sweep.cjs` (point `PW` at the playwright module).
- Google Chrome for `scripts/check_board.sh` (or set `CHROME`).

## Check it

```bash
python3 tests/selftest.py
```

It checks the frontmatter and every path the docs mention, compiles the scripts, runs the UI UX Pro Max search, builds both board templates with generated images (cut-outs must keep their transparency), and builds a sample log. Before publishing your own fork, also grep it for client names, people, paths under your home folder and deploy ids.

## Credits

This skill bundles three MIT-licensed works; their notices are kept in `THIRD_PARTY_NOTICES.md` and next to the files:

- **REA** reverse-engineering method, by morluto: `references/rea/`
- **UI UX Pro Max**, by Next Level Builder: `vendor/ui-ux-pro-max/`
- **Grilling**, from mattpocock-skills by Matt Pocock: `references/grilling.md`
