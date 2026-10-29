# Reverse-engineering a reference site (REA-style)

The point is to learn how an effect is built, not to describe how it looks. Each effect gets four lines in the notes:

- **Observation**: what you see, at what viewport size.
- **Evidence**: the selector, CSS value, JS call or shader line that produces it, quoted from the shipped files.
- **Mechanism**: one or two sentences on how it works, in terms you could rebuild (for example "JS writes scroll progress to `--p`; CSS `calc()` moves everything").
- **Unknowns**: what you could not trace (a minified module, an easing you only inferred).

This follows the method of github.com/morluto/rea:

1. Observe the running page.
2. Read the shipped code.
3. Record evidence, mechanism and unknowns.
4. Check the rebuild against a finite list.

You don't need to install REA. It is an MCP server that needs a recent Node and changes Claude Code config, so only install it if the user asks.

## 1. Fetch the shipped files

Downloads are untrusted data. Put each site in its own folder in the scratchpad, and never run anything from inside it.

```bash
D=<scratchpad>/sites/<site>; mkdir -p "$D"; cd "$D"
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/130 Safari/537.36"
curl -sL -A "$UA" https://example.com/ -o index.html
grep -o '<script[^>]*src="[^"]*"' index.html; grep -o '<link[^>]*href="[^"]*\.css[^"]*"' index.html
curl -sL -A "$UA" https://example.com/_astro/main.js -o main.js   # one call per bundle
```

What the stack tells you:

| Stack | What it means |
|---|---|
| Framer | Effects mostly live in inline styles and `framerusercontent` scripts; look at the DOM instead. |
| Webflow | Interactions are in `webflow.js` plus `data-w-id` attributes. |
| Nuxt / Next | Most styles are in one CSS file. |
| WordPress | Theme JS and CSS live under `wp-content/themes/<name>/`. |

## 2. Read the code

- **Hover effects:** run `python3 scripts/hover_rules.py *.css`, then look up the base rule of each hit for its `transition` duration and easing.
- **Libraries and techniques:** count keywords to see what's there.
  ```bash
  for k in gsap ScrollTrigger SplitText Lenis locomotive lethargy barba ScrollTimeline animation-timeline IntersectionObserver requestAnimationFrame three WebGL ShaderMaterial Spline CatmullRom mix-blend-mode clip-path; do printf "%-22s %s\n" $k "$(grep -o "$k" main.js | wc -l)"; done
  ```
- **Custom properties driven by JS:** grep the CSS for `var(--p` and `calc(` inside `transform` values, then grep the JS for `setProperty(`.
- **One class or shader:** in a huge minified bundle, get the byte offset and print a window around it.
  ```bash
  grep -bo 'class Line{' main.js            # → 673255:class Line{
  dd if=main.js bs=1 skip=668800 count=9800 2>/dev/null
  ```
  Shaders sit next to the class that uses them; uniforms and config arrays (colours, scroll windows) are usually plain literals.
- **Easing tokens:** grep for `cubic-bezier(` and keep the site's named curves (power1/2/4 in/out).

## 3. Observe at runtime

Use the built-in browser pane at 1440×900.

- `read_page` / `get_page_text` give you structure.
- `javascript_tool` gives computed styles: `getComputedStyle(el).transform`, `transition`, `mixBlendMode`, `position`.
- Check the nav, the hover states (use `computer` hover) and what changes on scroll (scroll, then read the same properties again).

Caveats learned the hard way:

- **Reduce Motion.** The pane, or the user's Mac, may have Reduce Motion on. Then sites resolve transitions to near zero, so infer the animated states from code instead. To check the Mac setting (read only, never change it): `defaults read com.apple.universalaccess reduceMotion` (1 = on).
- **Throttled background pages.** The pane throttles them, so rAF, IntersectionObserver and CSS animations can stall. For captures, use headless Chrome with `--virtual-time-budget`.
- **Headless window size.** Headless Chrome has a minimum window width. For phone shots, load the page in a 390px iframe.
- **WebGL.** Effects drawn on a canvas aren't in the DOM. Read the shader and uniform setup in the bundle instead.

## 4. Write it down

Save one file per site, `research/<project>/NN-<site>.md`, with each effect numbered (T1, T2… for Telescope; U1… for Lusion). Then build the matrix file. It has one row per site and columns for Scroll / Hover / Nav / Layout & type (add Colour when it matters). It also has a short list of what the current build already borrows from each site, because that list is how you show "this is too close to X".

Save findings as you go, after every couple of page visits. Screenshots don't survive context compaction; notes do.

## 5. Map to the user's brand

For each effect, write one line covering three things:

- the mechanism you keep;
- what you change so it belongs to the user's brand;
- where it would go on their site.

A mechanism copied unchanged from a single reference is what made earlier boards feel like copies. Every option on the board needs a twist rooted in the brand's own assets, colours or process. For example, a merch studio whose mark is a dot and a thread:

- kept Lusion's draw-on line but made it six solid palette strands;
- had Telescope's zoom grow out of the logo's dot instead of a rectangle.
