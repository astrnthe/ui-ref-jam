# Demo recipes

Every demo below is implemented in `assets/example-board.tpl.html`. It was built for a merch studio's board (6-colour palette; Geist stands in for the brand's typeface). The brand name in it, weft.example, is fictional. Find a recipe by its id: search the CSS comment (`/* Q4 scroll demos */`), the markup (`data-demo="s1"`) or the JS block (`/* ---------- Q4 scroll demos ---------- */`). To reuse one, copy its CSS, markup and JS block, then swap the tokens and copy.

Shared helpers, at the top of the script:

- **`tick(el, fn)`:** one rAF loop; `fn(now, dt)` runs only while `el` is on screen, and `dt` is 0 while motion is paused.
- **`every(el, ms, fn)`:** a repeating cycle built on `tick`, so it pauses off-screen too.
- **`scrollbox(box, onP)`:** a scroll container that plays itself (slow cosine ping-pong) until the viewer scrolls it. Then it resumes from wherever they left it. It calls `onP(progress 0..1, box)` on every scroll. Wrap content in a tall inner div with a `.stk` sticky child to make a pinned stage.
- **`on(hex)`:** picks ink or paper text for a colour by luminance.
- **`SOFT`:** each palette colour mixed 62% with the neutral, for large areas.
- **Motion toggle:** the `#motion` button pauses CSS (`.paused`) and WAAPI animations (`document.getAnimations()`). The board animates even when the viewer's OS asks for reduced motion, because motion is what is being judged.

## Accent treatments (brand palette inside one control)

All five share a JS level `lvl` that eases toward 0 at rest and 1 on hover (`lvl += (target-lvl)*(1-exp(-dt/150))`). A phase advances faster as `lvl` rises, so speed changes never jump. On hover the label sits in a paper "woven label" chip, so any colour can run behind the text.

| id | name | mechanism |
|---|---|---|
| W1 | Dye wave | Six SVG band paths with sine top edges, rebuilt every frame. At rest they fill 17% of the height; on hover they fill everything, with bigger amplitude and more speed. |
| W2 | Dot flood | Lusion's dot × palette. At rest the dot cycles colours. On hover it emits solid rings (WAAPI scale, 1.7 s expo-out, max 7 kept). On leave the rings shrink back. |
| W3 | Selvedge stripes | Vertical hard-stop stripes. Height is `calc(5px + (100% - 5px) * var(--lvl))`; `background-position` is driven by the phase. |
| W4 | Floss twist | The same idea with 118° stripes, on a light button. |
| W5 | Weave grid | 18×4 cells; colour index = floor(phase − col·.42 + row·.8) mod 6, so a diagonal wave runs through them. |

Rest-state sub-choice: black-and-white / a little colour moving / full colour all the time.

## Signature line (Lusion U1)

The SVG path is measured with `getTotalLength`. The draw is `stroke-dasharray`, mapped from scroll as `r = (scrollTop + .55ch) / (scrollHeight − .45ch)`. Over/under at the self-crossing works like this: find the crossing by sampling 320 points and testing segment pairs. Then redraw a ±30-unit stretch of the later pass on top, with a background-coloured wider stroke under it.

| id | variant | how |
|---|---|---|
| L1 | Six-strand | Six stacked strokes of decreasing width (dark outside, light inside), round caps. |
| L2 | Space-dyed | Six segment paths, each `dasharray "0 s vis big"`, with a pen-tip circle in the current segment's colour. |
| L3 | Per-section colour | One stroke whose colour switches as the head's y passes section bounds. |
| L4 | Hairline | Thin ink line; the baseline to compare against. |

Lusion U2 tint (`.tint`): greyscale image plus a colour overlay with `mix-blend-mode: lighten`. Add `.is-real` to fade to the true image.

## Colour distribution mocks (Q3)

`MINI()` builds a mini homepage (nav, hero, product band, work, statement, footer) that auto-scrolls. Scheme classes recolour it:

| id | scheme |
|---|---|
| D1 | Neutral page, every accent in all colours |
| D2 | Section backgrounds cycle through soft colours |
| D3 | Tinted images, monochrome UI |
| D4 | Selvedge stripes as structure |
| D5 | One colour per page (three mini pages) |
| D6 | Dark ink base |

The saturation sub-choice re-tints live: full everywhere / full for small areas and soft for big ones / soft everywhere.

## Scroll library (Q4)

| id | source | mechanism |
|---|---|---|
| S1 | Telescope split zoom | `--p1 = p/.3`, `--p2 = ease((p−.12)/.62)`. The halves move `46cqw·p2·dir`. The frame grows from a 14px dot (radius `max(0, (1−1.25p2)·400px)`), cycling palette colours, and the image fades in with a counter-scale of 1.5→1. |
| S2 | Telescope/Cosmos depth layers | Three layers, `translateY(p·k)` and `scale(d·(1+.3p))`. |
| S3 | Laura Monin char rise | Chars in `overflow:hidden` spans. Out: −105%, 800 ms, 8 ms stagger, power4-in. In at 640 ms: from 105%, power4-out. Photos fade with an 80 ms stagger and the background crossfades. Cancel the old WAAPI fills before re-animating. |
| S4 | Alet linear ↔ random | Tiles with transitions on left/top/width (1.1 s ease-in-out); background-color transitions over 4 s; seeded random layout; outline pill toggle. |
| S5 | Cosmos rotating noun | Phrases stacked in one grid cell. The active one has opacity 1, blur 0, transform none. Inactive ones have rotateX(±75°) and blur(8px). Two tilted colour chips sit beside the word. |
| S6 | Cosmos tile cloud | CSS 3D: `translate3d(x, y, z + p·900)` with `opacity: clamp(0, (300 − (z + p·900)) / 160, 1)`. |
| S7 | Lusion tint reveal | `.tint` cards get `.is-real` once 40% of the card passes 62% of the box height. |
| S8 | Telescope footer reveal | Main is relative with z 1 and a background; the footer is `position: sticky; bottom: 0; z-index: 0`. |
| S9 | Telescope word stagger | `.w` transitions with an 85 ms index delay, toggled in and out on a cycle. |
| S10 | Laura random scatter | Re-randomise every cycle; fade out and in with an 80 ms stagger; the title uses a difference blend. |

## Hover library (Q5)

| id | source | mechanism |
|---|---|---|
| H1 | Telescope per-char roll | `.c > span` with `::after` holding a copy; `translateY(−100%)` with a 14 ms index delay; the background takes the next palette colour. |
| H2 | Lusion dot flood | The dot moves `translateX(3.2em) scale(36)`; text shifts; an arrow slides in. |
| H3 | Lusion text roll + clone | Inline grid with two copies; first goes −105%, clone goes 105% → 0. A solid colour background scales in. |
| H4 | Laura underline wipe | `::after` with `scaleX(0)` and origin right; on hover `scaleX(1)` and origin left. The bar is the palette stripe. |
| H5 | Telescope accordion | `flex-grow` .9 s expo; the container's hover shrinks the others. |
| H6 | Laura lagging ring cursor | Lerp follow. Six-colour conic ring with a radial mask. Over a target, the individual `scale` property grows it (don't fight the rotation animation's `transform`) and an "Explore" label shows. |
| H7 | Telescope arrow cursor slider | The cursor disc shows ←/→ by half; click advances; slide keyframes go 1.22 → 1.1. |
| H8 | Cosmos card | Image scale 1.07 plus saturate, .9 s; caption nudges. |
| H9 | Lusion MENU dots | Six dots on a circle, only 2 visible at rest. On hover the group rotates 270° and all six scale in, in palette colours. |
| H10 | Lusion tint → colour on hover | — |
| H11 | Cosmos row expand | `grid-template-rows: 0fr → 1fr`. |

## Nav mocks (Q6)

| id | source | design |
|---|---|---|
| N1 | Telescope | Bottom bar with difference-blend side labels. |
| N2 | Lusion | Top-right pills. Menu opens six full-width colour bands, sliding in with a 45 ms stagger. |
| N3 | Cosmos / Agronomy | Top bar with centred logo; hides on scroll down and shows on scroll up. |
| N4 | Alet | Corner labels with a difference blend. |
| N5 | Laura Monin | Header with a difference blend. |

## Layout mocks (Q7)

| id | source | layout |
|---|---|---|
| Y1 | Lusion | Giant left-aligned headline, paragraph in the right column, line behind the type. |
| Y2 | Telescope | Centred headline with a scatter. |
| Y3 | Alet | Contact sheet. |
| Y4 | Agronomy | Index rows. |
| Y5 | Laura Monin | Giant title in a difference blend over a scatter. |

The corner sub-choice sets `--rad-img` and `--rad-btn`.

## Smoothness (Q8)

| id | what it shows |
|---|---|
| G1 | Lenis-style smooth scroll: wheel → target, lerp `(1−exp(−dt/120))`. |
| G2 | Page transition: six bands `scaleX` in from the left with a 45 ms stagger, the content swaps, then they scale out to the right. |
| G3 | Side-by-side comparison: hard (no transition) vs soft (expo-out). |
| G4 | Intro sequence: word stagger, then tiles. |

The reduced-motion policy sub-choice: respect fully / keep the gentle effects / ignore.

## Pinned scroll and parallax (Q9)

| id | effect | mechanism |
|---|---|---|
| P1 | Step-by-step process | Pinned stage. `idx = floor(p·6)`. Circles fill with step colours. The connecting track fills between circle centres, measured every frame, with gradient stops at those centres. The big number rises; the image crossfades; the active step's text expands (grid rows). |
| P2 | Horizontal pin | The track moves `−ease(p)·(scrollWidth − clientWidth)`. Inside each card the image shifts by its distance from centre. Six progress bars fill. |
| P3 | Stacked cards | `position: sticky; top: 10px + i·10px`. Each card scales down by how much the next one covers it. |
| P4 | Parallax | The image is 130% of its frame and translates by its distance from the box centre; palette dots drift at their own speeds. |
| P5 | Pinned word reveal | Words go from .16 to 1 opacity; key phrases get a solid palette chip once lit. |
| P6 | Sticky side headings | The left heading is `position: sticky` inside a 2-column section. |

## Motion questions in a later round

Round-2 questions are often text options, but a motion choice still needs a sample. Both are in
`assets/motion-samples.tpl.html`, a standalone page (build it with `scripts/embed_images.py`, passing `--img front=… --img back=…`). On a board, give a
text option a fifth field and render the matching stage function (`ldStage(key)` or `rtStage(key)`) as its stage.

### Load-in timing (`ldStage`, Q22)

The chosen hero (headline words plus six product cut-outs) with the signature line behind it. Each option is one
parameter set:

| id | stagger | each item | thread draw | total | note |
|---|---|---|---|---|---|
| a | 80 ms | 600 ms, rise ≈ 1.4cqw, `cubic-bezier(.16,1,.3,1)` | 1000 ms | ≈ 1.2 s | meets "about a second" with no fast step |
| b | 50 ms | 300 ms | 500 ms | ≈ 0.65 s | literal "quick"; the kind the user bans |
| c | 140 ms | 1000 ms | 1800 ms | ≈ 2 s | picked once over a client's "about a second"; record such a departure (see handoff) |

- WAAPI on `.ldw` (words) and `.ldp` (product wrappers), with `fill: 'backwards'`. Once the animation ends, the stage
  is complete at rest.
- The thread animates `strokeDashoffset 1 → 0` on a path with `pathLength="1"`.
- A ↻ replay button sits in the stage, and each stage plays once when it comes into view. The page's click handler
  must ignore `.replay`, or replaying also selects the card.

### Turning a flat product photo (`rtStage`, Q25)

The user's reaction to the autonomous turn on the live hero: "现在的问题是，这些都是面片，旋转起来很奇怪" ("these are all
flat cards; turning them looks weird"). Squashing one cut-out with `scaleX(cos a)` and swapping the image at the
midpoint reads as a card flipping, whatever images you have. The samples use one real front and back pair (a past
project's hoodie renders, cut out):

| id | what it does | verdict |
|---|---|---|
| x | `scaleX(abs(cos a))`, swapping faces at the midpoint | the rejected current state; keep it only for comparison |
| a | hold 3 s; crossfade over 1.2 s with ±3% slide | safe, but reads as a slideshow |
| b | the same, with the old face going 0 → −28° `rotateY` and the new one +28° → 0, `perspective: 900px` | recommended for autonomous motion |
| h | **hover only**: a visible card flip (≈ 0.8 s); the hoodie flips to its back, the cap steps through 4 angles; static on touch | **picked** as the interim: "那可以先做2d面片的hover翻转" |
| c | a 24–36-frame turntable rendered from a 3D source | needs a .blend, .zprj or .glb; none existed |
| d | a glb in three.js (auto-turn, drag, recolour by material) | truest; needs models (garment-software export, or image-to-3D via Figma Weave, which needs the user's account linked) |

Rule: never auto-rotate a single flat cut-out. With no 3D source, either swap real angle photos (a, b) or make the
flip something the visitor triggers (h). Before promising rotation, search the work folders for
`.blend/.zprj/.glb/.obj/.fbx` and turntable videos. Check a video's frames before trusting its name: a client folder's
dated videos turned out to be car promos.

A pane that is hidden throttles `requestAnimationFrame`, so a screenshot taken there can show the wrong moment. To
check a mid-transition frame, call the frame function with a fixed time (`rtTick(3.55)`), or show the pane first.

## Gotchas already paid for

- **Text split up in grid or flex.** A `<p>` with `display: grid` or `flex` makes every text run and inline link its own item, so the sentence breaks apart. Wrap the sentence in one `<span>`.
- **Stale WAAPI fills.** `fill: 'forwards'` from an old animation reasserts itself after a newer one ends. Call `.getAnimations().forEach(a => a.cancel())` first.
- **`mix-blend-mode` doesn't blend.** It does nothing inside an isolated or stacking-context parent. Make the blended label its own fixed or absolute element.
- **Dashes in screen pixels.** `vector-effect: non-scaling-stroke` measures dashes in screen px and ignores `pathLength`. Use a large px dasharray.
- **SVG capped at full width.** A global `svg { max-width: 100% }` stops an SVG from overshooting its box; add `max-width: none` where it should overshoot.
- **Never hide content waiting for an observer.** Previews must be complete at rest; a pane that throttles IntersectionObserver leaves it invisible.
- **Container units.** Previews use `container-type: inline-size` on `.stage`, so `cqw` scales the mini sites to any card width.
- **Fixed colours.** Stages use fixed site colours (`--s-paper`, `--s-ink`) so the previews look like the real site in both light and dark board themes.
