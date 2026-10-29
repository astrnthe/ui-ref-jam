---
name: ui-ref-jam
description: Reverse-engineer reference websites' front-end effects (scroll, hover, nav, layout, type, colour), check them against UI/UX rules, rebuild each in the user's brand as a live option board (a local HTML page in the built-in browser), then grill the user round by round, reading picks back from the page. Also: boards on an existing site from its real pages (before/after splits, zoomed crops, injected variants); overnight robustness sweeps with a morning brief; client feedback turned into a requirement ledger, with placeholder facts proven from the user's files and screenshots of where the client said it; real, recolourable product photos instead of drawn placeholders. Use when the user shares reference sites, URLs, DESIGN.md files or screenshots to learn from, 拆解 or remix; asks for a 方案板 or says "给我方案板"; asks for overnight testing; or pastes client feedback.
---

# UI ref jam

Turn a pile of reference websites into decisions the user can make by playing with them. The workflow has five steps:

1. Take each site apart and record how each effect is actually built.
2. Lay the findings out per category and check them against UI/UX rules.
3. Rebuild every candidate effect as a small live demo in the user's brand, each with a deliberate twist.
4. Put the demos on a board as numbered questions, with a recommended answer pre-selected.
5. Grill the user round by round until nothing is left open. Only then touch the real site.

The board is the product. The user judges motion by touching it, not by reading about it, and every option already wears their colours and copy. Text-only option lists got rejected; this format got "太好了".

## Three bundled methods

This skill carries everything it needs; nothing else has to be installed. Each method lives in its own folder:

| Method | Where | What it does in this workflow |
|---|---|---|
| **REA reverse engineering** (github.com/morluto/rea, MIT) | `references/reverse-engineering.md` is the working method. `references/rea/` holds the upstream README and the website-observation, script-export, module-trace and source-location docs. | Step 1. Evidence-based teardown: observe, read the shipped code, record evidence, mechanism and unknowns, then verify the rebuild against a finite checklist. |
| **UI UX Pro Max** (MIT) | `vendor/ui-ux-pro-max/`: the search tool `vendor/ui-ux-pro-max/scripts/search.py`, its CSV data (styles, palettes, fonts, UX guidelines, GSAP motion presets, landing patterns, stacks), `vendor/ui-ux-pro-max/references/quick-reference.md` (about 98 rules by priority), `vendor/ui-ux-pro-max/references/pro-rules.md`, and the upstream SKILL text in `UPSTREAM-SKILL.md`. | Brand context before Step 3; extra candidate effects beyond the references; a rules check on every option; stack-specific build notes. |
| **Grill me** (mattpocock-skills, MIT) | `references/grilling.md`, verbatim. | Steps 4–5. Map the decisions as a design tree, ask a whole frontier per round with a recommended answer, keep going until the frontier is empty. |

Run the search tool by full path, with no assumed working directory:

```bash
python3 ~/.claude/skills/ui-ref-jam/vendor/ui-ux-pro-max/scripts/search.py "<query>" --domain <ux|gsap|style|color|typography|landing|google-fonts> [-n 5]
python3 ~/.claude/skills/ui-ref-jam/vendor/ui-ux-pro-max/scripts/search.py "<product> <industry> <tone>" --design-system --motion <1-10> -p "<Project>"
python3 ~/.claude/skills/ui-ref-jam/vendor/ui-ux-pro-max/scripts/search.py "<keyword>" --stack astro   # or the stack the project uses
```

If a search returns nothing, retry once with broader words. If it still returns nothing, say the advice comes from the built-in priority table, never from data you didn't get.

## Before you start

Gather these, and look for them in the project before asking:

- **The reference URLs**, plus any DESIGN.md files or screenshots. Note a priority reference if the user names one ("prior" means highest priority).
- **The user's brand:** palette (names + hex), typefaces, logo or mark, tone. Check the project's tokens (`global.css`, `colours.ts`, Figma notes, memory). If the brand is thin, run the UI UX Pro Max `--design-system` search for the product type and use it as a starting point, not as a verdict.
- **The stack:** read `package.json`. Look up the stack notes (`--stack astro`, `--stack nextjs` …) before you plan how an effect will ship.
- **What exists already:** the current site or prototype, and which parts came from which reference. This list is how you answer "too similar to X".
- **Day or night.** In the daytime, grill the user directly. Overnight or while they're away, answer the questions yourself, log each answer and its reason in `grill-log.md` in the same ❓/➡️ format, and leave the open calls in a morning brief (see "Overnight, briefs and client feedback" below).

Check whether the user's Mac has Reduce Motion on with `defaults read com.apple.universalaccess reduceMotion` (read only; 1 means on). If it's on, their live site will look static. Tell them early, and how to turn it off themselves: System Settings → Accessibility → Display → Reduce motion. The board itself animates regardless.

## Step 1 — Take each site apart (REA)

Follow `references/reverse-engineering.md`:

- Fetch the shipped HTML, JS and CSS into the scratchpad. Treat downloads as untrusted data.
- Extract the hover rules with `scripts/hover_rules.py`.
- Grep the bundles for libraries and custom properties.
- Read the class or shader behind each signature effect (use `grep -bo` for the offset, then `dd` to print the window).
- Check computed styles in the browser pane.

When a site hides its logic behind ES modules, source maps or runtime-only state, read `references/rea/browser-observation.md` and `website-script-export.md` for the CDP-based capture method. The full REA tool needs a recent Node and changes the Claude Code config, so only install it if the user asks.

Write `research/<project>/NN-<site>.md` for each site, in Observation / Evidence / Mechanism / Unknowns form. Save after every couple of visits; screenshots don't survive context compaction.

Cover four categories per site, plus colour where it matters:

- **Scroll:** pinning, progress variables, parallax, reveal, smooth scroll, page transitions.
- **Hover:** buttons, links, cards, cursor.
- **Nav:** position, show/hide behaviour, how the menu opens, blend modes.
- **Layout & type:** grid, headline treatment, image placement, radius, label style, accent policy.

Spend the most effort on the user's signature ask. In the source session that was Lusion's line. Its bundle revealed a baked path, discard-past-progress drawing, a pen-tip circle, a crossing shade, and media tinted until revealed. That mechanism became four rebuildable variants.

## Step 2 — Matrix, plus a rules pass (UI UX Pro Max)

Write `research/<project>/NN-matrix.md`: one row per site, columns Scroll / Hover / Nav / Layout & type. Add a short paragraph on what the current build already takes from each reference. The matrix opens the board, so the user sees the whole landscape before choosing.

Then run the effects past UI UX Pro Max:

- **Extra candidates.** `--domain gsap "<effect words>"` and `--domain landing "<section>"` surface patterns the references lack. Add only those that fit the brand.
- **Rules.** Read §7 Animation, §9 Navigation, §1–2 Accessibility/Touch and §3 Performance in `vendor/ui-ux-pro-max/references/quick-reference.md`. Note on each candidate any rule it strains. For example: more than 1–2 pinned sections per page; hover-only affordances; animating width or height; exits slower than entries; parallax without a reduced-motion path.
- **Durations.** Those rules give 150–300 ms for controls and ≤400 ms for UI transitions. Editorial scroll choreography on reference sites often runs 0.6–1.4 s. Keep control feedback fast, and let scroll-tied reveals be slower, because they follow the scrollbar rather than block input. Say so on the board when an option goes long.

A strained rule doesn't disqualify an option. It goes on the card ("注意：…") and becomes a question in a later round if the user picks it.

## Step 3 — Plan the questions (the design tree)

Read `references/grilling.md` once per session. The essentials:

- **The design tree.** Every decision branches into the decisions that hang off it.
- **Rounds by frontier.** The frontier is every decision whose prerequisites are settled. Ask the whole frontier in one round. A question whose answer depends on another question in the same round belongs to a later round.
- **A recommended answer per question**, worded so that "yes" accepts it.
- **Facts are your job, decisions are theirs.** Look things up yourself, or with a subagent; never ask the user for a fact. Don't block the round on a running lookup. Only the questions downstream of it wait.
- **Done when the frontier is empty and the user confirms.** Don't build on the real site before that.

A first round that has worked well (adapt the names and count to the project):

1. **Accent treatment in the brand palette:** how the brand's colours live inside buttons and other accents, with a rest-state sub-choice. With a multi-colour brand, don't copy a reference's single accent; show ways to put the whole palette inside one control as solid colour that moves, stronger on hover.
2. **Signature motif from the references:** for example a scroll-drawn line in 3–4 brand variants, plus the current version for comparison.
3. **Colour distribution:** 5–6 schemes as auto-scrolling mini homepages, plus a saturation-by-area rule.
4. **Scroll library** (multi-select).
5. **Hover library** (multi-select).
6. **Navigation:** 4–5 mocks with live behaviour.
7. **Layout of the main page**, plus a corner-radius sub-choice.
8. **Smoothness** (multi-select): smooth scroll, page transitions, consistent easing on every state change, intro sequence. Add a reduced-motion policy sub-choice.
9. **Pinned scroll and parallax** (multi-select): step-by-step process, horizontal pin, stacked cards, image parallax, pinned word reveal, sticky side headings. Each card says where on the site it would go.

Round 2 usually covers what round 1 unlocked:

- a storyboard per key page, saying which effect goes in which section and in what order;
- the colour assigned to each section;
- details of the signature motif (thickness, path, where it runs);
- the button family: primary, secondary, link;
- nav details and the mobile menu;
- where alternative layouts the user wants to try would live;
- hero copy;
- pacing: pin lengths, intro once or always.

Resolve conflicts flagged in Step 2 here (for example "you picked six pinned effects; UI UX Pro Max advises 1–2 pins per page; which pages get which?").

Give every option:

- a live demo;
- a source line, "Reference effect → brand twist";
- where it would be used;
- a one-sentence description;
- any rule it strains.

Mark the recommendation and pre-select it. Flag options that are a straight copy of one reference: they stay for comparison but aren't the default.

The differentiation rule is: keep the mechanism, change the material. Each borrowed effect gets one change rooted in the brand: its mark, palette, product or process, or copy. A remix that only swaps colours still reads as a copy.

## Step 4 — Build the board

Start from `assets/example-board.tpl.html`, a complete board with 9 questions and about 50 working demos. `references/demo-recipes.md` indexes every demo, the shared helpers and the gotchas already solved. For round 2+, start a new page from the same skeleton: the head CSS up to `/* Q1 …`, the picks-bar CSS, and the helper and picks JS. Then copy in only the demos you need.

- Swap the `:root` tokens: brand palette, `--s-*` site colours, fonts from Google Fonts with a fallback stack.
- Use the user's real copy and content. No lorem ipsum, no invented client claims.
- Keep, drop or add demos to match what the references actually contain.
- Keep the shared machinery:
  - header with motion toggle and reduced-motion note;
  - matrix;
  - question bands with sub-choice chips;
  - option cards;
  - picks bar with Copy and Save;
  - the `tick`, `every` and `scrollbox` helpers.
- Use only safe images (the user's own, or licensed stock already in the project) through `%%IMG_key%%` placeholders. When an option needs product shots the project doesn't have, generate them rather than drawing them (`references/product-imagery.md`).

Build and check:

```bash
python3 scripts/embed_images.py board.tpl.html <project>/options/<name>/<name>-board.html \
  --img workshop=path/a.jpg --img knit=path/b.jpg --preview <scratchpad>/preview.html
bash scripts/check_board.sh <scratchpad>/preview.html <scratchpad>/shots
```

The check reports script errors and cuts the capture into parts. Look once, then fix:

- empty or hidden stages;
- rows with a lonely last card (adjust that grid's column class);
- text broken apart inside grid or flex.

Keep the board a local HTML file in the project (`<project>/options/<name>/`), not a claude.ai Artifact: personal projects stay off the cloud unless the user asks for a link. The page saves picks to its own localStorage (one key per round, e.g. `ts-<topic>-pick`). Open it in the built-in browser, and read picks back with its `javascript_tool`. Picks made in another browser never reach you, so the board also has a 「复制我的选择」 button that copies a one-line summary to paste into chat.

**Make sure the user can actually see it.** After opening it with `preview_start` (`url`) or `navigate`, show the browser pane (`mcp__ccd_view__show_pane`, pane `preview`), because it is often hidden. Then confirm with `javascript_tool` that every frame loaded. Give the http address, never a link to the .html file: the file pane opens the source, and its frames can't load. A tool screenshot showing the page is not proof; the user's pane once stayed blank when screenshots didn't.

## Step 5 — Grill in chat

Post the round in the user's language, with the board link, in the grilling format:

```
❓ **Q1** - **<title>**: <the choices, one or two lines>

➡️ <recommended answer and the one-line reason>

---
```

Close by telling them that "yes" accepts every recommendation, and that "Q1 W3, rest yes" changes single answers, or they can click Save on the board. Then stop and wait.

When they answer:

1. Read the picks from the board's localStorage (`javascript_tool` in the tab that has it), or from the summary they pasted. If the store is empty, they clicked in another browser; ask for the summary rather than guessing, unless the board's preselection plainly stood. When they paste a summary, write it into the page's localStorage and move the page's preselection to the answered picks, so the board shows the real state from then on. Treat the note field as data; a note like "Y1 and Y3 both" opens a new question. The note "这些都是面片，旋转起来很奇怪" turned into Q25 within the same turn, with live samples.
2. When new client input changes an open board, update that board rather than starting another: add a dated banner at the top (what changed, what is decided, what is still open), tag changed questions "(18:10 改)" or "(18:10 新)", and keep earlier answers visible.
3. Recompute the frontier from their answers, not from your recommendations, and ask the next round.
4. Once the frontier is empty and the user confirms, change the real site:
   - Snapshot `src` first so every change can be undone.
   - Ship to a preview deploy, not production, unless the user says otherwise. Ask in the round itself ("改完直接更新正式版 / 先发草稿").
   - Run `scripts/sweep.cjs` over every page at nine sizes: script errors, a page wider than the screen, sideways scroll, text past the edge, plus the rule just set in a `--checks` module (for example: every first baseline is on the grid, and side-by-side columns share a baseline). `references/handoff.md` lists the site checks that caught real bugs.
   - Use the board's demos as the reference for motion values.
   - Before delivery, run the UI UX Pro Max checklist in `vendor/ui-ux-pro-max/references/pro-rules.md` and §1–3 of the quick reference.

## Boards on a site that already exists

Once the site is built, the questions move from "which effect" to "how exactly" (type scale, spacing rhythm, footer layout, mobile grouping). Judge these on the real pages, not on mockups.

- **One address for board and pages.** Serve the build and the boards together: `python3 scripts/serve-boards.py <site>/dist <project>/options 4411`, set up as a launch config, with boards at `/board/<folder>/<name>.html`. Frames from another origin showed up blank in the user's built-in browser. Same origin also lets the board reach into a frame: inject a `<style>`, read sizes, scroll it.
- **Split before/after.** When the user wants to compare a rule against the current build, show the page with the rule on one side and the current page on the other. Each side scrolls on its own (each is its own iframe), at a real viewport (1440 × 900 or 390 × 844) scaled to the pane, never squeezed into a narrow pane width. Add buttons that move both sides to the same place ("到顶部 / 到页脚").
- **Live changes, no reloads.** Settings on the board change the open pages through `postMessage` (check `e.origin`) or an injected stylesheet, so they keep their scroll. When the site has layout scripts that only run on resize, add a named event to the site (e.g. `tg-relayout`) that the board can fire.
- **Variants as injected CSS.** For "A/B/C on the real page" (how cards group on mobile, title sizes), each option is a stylesheet the board lays over the same live page, shown on the pages it affects.
- **Measured values.** A table of the real numbers each side reports back: size, line-height, x-height, how far off the grid. It turns "looks bigger" into "54 → 63px".
- **Zoomed crops for details.** For edges and alignment, add two more copies of the page at full scale, translated so one element fills a window: one with the refinement off, one with it on, plus guide lines. Jump with `scrollTo({behavior: 'instant'})`, because sites often smooth-scroll and a crop measured mid-scroll lands in the wrong place. Turn off scroll-linked reveals in those copies (a URL flag), or they slice what you crop.
- **Guides the user expects to see.** If the board draws a grid, the text must visibly sit on it. A "grid" that is only a decoration, with baselines between its lines, got rejected ("只加了一层基线视觉，没改排版"). Changing the unit must visibly change the type.
- **Read the user's own source documents.** When they hand over a spec (a DESIGN.md, a typography guideline), read it, adopt what it settles, and turn the differences into board questions.
- **Effects that follow the scroll must hold at every point of it.** A line drawn to a heading, a lifted section, a pinned footer: check them at several scroll positions and after a reload halfway down, not only at rest. `references/handoff.md` has the cases that broke.

## Real product imagery

When the board or the site shows products, show them as product photos, never as drawn flats or placeholders. The user asked for every illustration to become a product image, photographed or AI-generated, and a client asked for one consistent look across the range. `references/product-imagery.md` has the whole method:

- one shared prompt, so the range reads as one studio shoot;
- white garments on chroma green, generated with Figma's `generate_image` (paid credits: say so, and move the frames off the user's working page afterwards);
- `scripts/imagery/garment.py` splits each one into shading and highlight layers that the page tints live in any palette colour, behind the component's existing API;
- `scripts/imagery/mockup.py` puts client artwork onto these photos, replacing mockups built on other brands' photos.

Never draw a logo for a real brand you couldn't find; list it as waiting for the client's files.

## Overnight, briefs and client feedback

`references/handoff.md` covers the work around the boards:

- **Overnight:** decide the open calls yourself, keep each one reversible, deploy drafts only.
- **The sweep** (`scripts/sweep.cjs`): every page at nine sizes, on the local build and on the deployed draft, with a module for the site's own rules.
- **The morning brief** (`assets/morning-brief.tpl.html`): the outcome, their reports as problem / cause / now, what testing found, what only a real phone can show, the decisions you made, and the one reply that moves things on.
- **Client feedback:** an ask / exists / missing / who-supplies table before building; flag anything that would mislead visitors; turn the design asks in it into board questions.
- **A requirement ledger** per client (R-rows in the client's words, a superseded table, open decisions, non-web tasks). Re-check the tracker for anything new before each update. Trackers and client docs are read-only.
- **Client docs the connector can't see:** open them in the built-in browser, read the `/mobilebasic` view, and keep a verbatim local copy.
- **Placeholders in client copy** ("[square brackets] = facts to confirm"): a provenance table, filled only from the user's own files (tech packs, renders, logo SVGs, chat lines), with "no proof → drop" everywhere else. Check every claim in the copy against the image beside it.
- **"Where did the client say that?"** Quote the passages, then screenshot each one in the tracker, using a temporary overlay outline and never touching the editor. Save the shots to `evidence/`.
- **Split sessions:** the board session hands settled picks with exact words to development and every decision to the log session. It never edits site code.
- **Production** only on the user's words, and each go-ahead covers one batch.
- **Log it:** every pick, rejection, overnight call, client round, go-ahead, deploy and snapshot goes into `log/` (see below).

## Decision and change log

Every project keeps `log/`, a bilingual record of every big change and every key decision, for later review and case studies. Start a project's log from `assets/log/` (README.md has the format, build.py builds the viewer from viewer.tpl.html). Log each board round at the moment it is answered, using the picks read back from the page, the user's note and a screenshot of the board. Log each rejection with the user's exact words. `why` records only the reasons someone actually gave.

## Things that keep the board good

- **Complete at rest.** Every stage shows something meaningful in its first frame. Scroll demos play themselves until touched.
- **Motion is the point.** Demos animate even under Reduce Motion, with a visible pause toggle. The production policy is a question on the board, not a silent default.
- **Previews look like the site.** Stages use the site's own light colours in both board themes.
- **Real content only.** Products appear as photographs (real or generated), never as drawings. Questions that make claims about the business (turnaround, guarantees, what the studio keeps) need the user's confirmation before they reach the real site.
- **Mobile.** Grids collapse to one column, hover demos toggle on tap, and pinned demos stay as scrollable boxes.
- **Choices are visible chips, never dropdowns.** Mark each question 必选 / 可跳过 and each note field 选填. Pre-select the recommendation.
- **No dead space.** Fill the width (2–4 option columns), keep the controls compact, and put the numbers or the remaining questions under the live views rather than leaving the lower half empty.
- **Board over prose.** When the user asks for one ("给我方案板"), put the open questions on a board: every option as a live or rendered specimen they can click. Don't list them in chat again.
- **Motion questions get motion samples, even in a text round.** Show timing as the chosen hero with a replay button; show rotation with real angle photos. Never auto-rotate a single flat cut-out: squashing it with `scaleX` reads as a card flip, and got rejected. `references/demo-recipes.md` has both recipes and `assets/motion-samples.tpl.html` runs them.
