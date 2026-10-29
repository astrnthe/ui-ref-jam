# Real product imagery

Use this when a board option or the site shows products (garments, merch, bags, caps) and the visuals are drawings,
placeholders, or mockups built on someone else's photos. The user's rule, after seeing drawn technical flats on a live
site: replace every illustration with a product image, real photography or AI-generated, never a drawing
("全部换成产品图而不是插画图"). The client asked for the same thing in their own words: real content, and one
consistent theme across the range (same lighting, background, framing, styling).

## 1. One shoot for the whole range

Generate one white garment per product type, all with the same prompt skeleton, so they read as one studio shoot:

> Professional e-commerce ghost-mannequin product photograph of a plain white heavyweight cotton **<garment and its
> details>**, front view, perfectly centred and symmetrical, the whole garment visible with generous empty margin on all
> sides, natural soft fabric folds. Soft diffused studio light from the upper left, realistic **<fabric>** texture. No
> logo, no print, no text, no labels, no hanger, no mannequin visible. Isolated on a perfectly flat, uniform pure
> chroma-key green background (#00B140) with no shadow, no gradient and no floor.

- **White on chroma green.** White takes any colour later; green keys cleanly. Ask for a back view as its own image
  when a design prints on the back (the neckline differs; don't reuse the front).
- **Caps and bags:** a three-quarter view for the cap ("curved peak pointing forward-right, button on top"); the tote
  standing upright with both handles up. Models add a floor anyway sometimes; the keyer handles it.
- **Supporting shots** (fabric swatches with matching thread, a desk, packaging) use the same light words, in the
  brand's colours by hex, "no text, no labels, no colour cards, no hands".

**Tool.** Figma's `generate_image` (via the Figma connector) worked well with `gemini-3.1-flash-image`, 896 × 1152 for
garments and 1024² for caps. It spends the user's Figma AI credits: say so once, generate one image per need, and look
at each before generating more. It drops a frame onto the file's first page, which is usually the user's working page.
Afterwards, load the figma-use skill and move the frames onto their own page (e.g. "Web — AI product photos"), named
"AI · <garment>". The download URL expires in 7 days: `curl -f -L -o raw/<name>.png <url>` straight away, into the
project (e.g. `<project>/imagery/ai-products/raw/`).

## 2. Split into tintable layers: `scripts/imagery/garment.py`

```bash
python3 -m venv <scratch>/imgenv && <scratch>/imgenv/bin/pip install numpy scipy pillow   # system Python lacks numpy
<scratch>/imgenv/bin/python ~/.claude/skills/ui-ref-jam/scripts/imagery/garment.py --raw raw --out out hoodie t-shirt cap tote
```

Per garment it writes `shade.webp` (grey shading, garment alpha), `hi.webp` (highlights, same alpha) and `box.json`
(where it sits), on one canvas (800 × 920) with per-type fill so a cap is not as big as a hoodie, plus
`previews/<name>.jpg` in eight colours. Look at every preview, dark colours included, before using it.

Keying mistakes already made and fixed in the script, so you recognise them if a new image misbehaves:

| Symptom | Cause | Fix in the script |
|---|---|---|
| Light speckles along a cap's peak, a see-through band at a tote's base | green bounced onto the fabric near the floor keys as background | solid interior: fill the outline, keep only a 2px soft edge |
| The gap between tote handles filled in grey | hole filling also filled real backdrop | never fill pixels that are strongly backdrop |
| Noise inside a hood | near-black has almost no red, so a red-only test calls it backdrop | backdrop = low red **and** clear green spill |
| Ragged dark fringe under a bag | the contact shadow on the floor | trim dark pixels below the lowest lit fabric in each column |
| Black hole inside a hood or collar on every colour | shading hits 0 there | shading floor of 0.16: a deep shade of the colour, not black |

## 3. Recolour live on the page

Keep the old component's API (props, the CSS variable the swatches set, class names the scripts query) and change
only what it draws, so no caller has to change. In SVG:

```html
<svg viewBox="0 0 800 920" style="--g:#613F33">
  <defs><mask id="m" style="mask-type:alpha"><image href="shade.webp" width="800" height="920"/></mask></defs>
  <ellipse … fill="url(#soft-floor-shadow)"/>                       <!-- optional, under the garment -->
  <g style="isolation:isolate">
    <rect width="800" height="920" mask="url(#m)" style="fill:var(--g)"/>
    <g class="mark" transform="…">…</g>                              <!-- under the shading: folds cross it -->
    <image href="shade.webp" width="800" height="920" style="mix-blend-mode:multiply"/>
    <image href="hi.webp" width="800" height="920" style="mix-blend-mode:screen"/>
  </g>
</svg>
```

On a canvas: fill the colour, `multiply` the shade, `screen` the highlights, then `destination-in` the shade to cut it
out. Draw each colour once into an offscreen canvas and reuse it.

**Marks and logos** go where they would really be: left chest, clear of a hoodie's drawstrings; the front panel of a
cap (not the side); large and centred on a tote. Place them by eye on a screenshot, per garment type.

## 4. Client artwork on your own photos: `scripts/imagery/mockup.py`

For work images, match what is already there: measure the existing renders first (size, background grey), e.g.
1800 × 1800 on grey 189. Then:

- **A print from an old mockup slide** (flat lay on the left half, garment black): `--flatlay old.jpg`. The script finds
  the print inside the garment's outline, keeps where it sat, makes the old black ground drop away (screen), and lays
  the new garment's folds and light over it.
- **A logo file:** render the SVG with Playwright on a transparent page with room around it (a viewport the size of the
  SVG can clip the last letter), recolour its fills, then `--art logo.png --at cx,cy,width`.

Use it to replace mockups that sit on other brands' product or model photos: same artwork, safe base.

## 5. Brands and honesty

- Look for a client's logo in the project folders first, then online. If it can't be found, don't draw one: list
  the brand as waiting for the client's logo files. An invented logo on a real brand misrepresents both.
- Label the client's own (in-house) brands as such on the work pages, and don't word them as outside clients ("the
  client chose…"). Testimonials written for in-house brands must not be shown as independent client quotes.
- Keep a snapshot of `src` before swapping imagery site-wide, and say which images are AI-generated when asked.

## 6. Cutting out an existing render (no numpy needed)

Garment renders on a flat grey studio background, like garment-software (CLO-style) renders at 3840², can be cut out with
PIL alone for a board sample. Key out by colour band, not by flood fill. A flood fill from the edges misses the grey
pockets enclosed between the arms and the body. Instead, make a pixel transparent when it is near-neutral
(`max − min < 12`) and inside the background's value range (about 150–218 for a 189–197 backdrop), and give a soft
edge between 120 and 150. Then run a 3×3 median filter, crop to the bounding box, and place the result on the site's
800 × 920 garment frame with the foot at 0.93 of the height. White prints above about 220 survive the key. Preview the
result on the board's paper colour before using it.

