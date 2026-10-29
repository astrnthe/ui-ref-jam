"""Turn an AI product photo of a white garment on chroma green into two layers a web page can recolour live.

  shade.webp  grey shading with the garment's alpha: multiplied over a solid colour (and used as that colour's mask)
  hi.webp     highlights with the same alpha: screened on top, so folds still read on dark colours
  box.json    where the garment sits on the canvas (x, y, w, h as fractions)

Every garment is framed the same way on one canvas (default 800 x 920), so a whole range reads as one shoot.
A preview sheet shows each garment in the preview colours, the way the page will tint it.

  python garment.py --raw raw --out out hoodie t-shirt cap        # reads raw/<name>.png
  python garment.py --colours '#613F33,#1D1C1A,#F2F2F0' tote      # preview colours (default: a neutral set)

A name may carry a variant after '@' (hoodie@back); the part before '@' picks the fill below.
Needs numpy, scipy and Pillow (python3 -m venv <scratch>/imgenv && <scratch>/imgenv/bin/pip install numpy scipy pillow).
"""
import argparse, json
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage

W, H = 800, 920
# How much of the canvas each kind of piece fills, so a cap does not look as big as a hoodie.
FILL = {'hoodie': .86, 'sweatshirt': .86, 'long-sleeve': .88, 't-shirt': .84, 'cap': .74, 'tote': .70}
PREVIEW = ['#613F33', '#647058', '#9DACC1', '#BBAE8E', '#EDD05E', '#EE86C8', '#F2F2F0', '#1D1C1A']


def key(rgb):
    """Alpha and luminance of a garment shot on chroma green (float RGB 0-255)."""
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    # The backdrop is pure chroma green: almost no red, in light or in shadow, and clearly greener than it is blue or red.
    # Fabric keeps its red even where the floor bounces green onto it (the base of a tote); the near-black inside a hood
    # has little red but is not green either. Either test alone fails on one of those.
    red = r / np.maximum(g, 20)
    spill = g - np.maximum(r, b)
    bg = np.clip((.32 - red) / .2, 0, 1) * np.clip((spill - 12) / 20, 0, 1)
    a = 1 - bg
    # Keep the garment (the biggest piece) and anything big attached; drop specks.
    lab, n = ndimage.label(a > .5)
    if n:
        sizes = ndimage.sum(np.ones_like(a), lab, range(1, n + 1))
        keep = np.isin(lab, [i + 1 for i, s in enumerate(sizes) if s > sizes.max() * .02])
        a = a * ndimage.binary_dilation(keep, iterations=3)
    # Inside the outline everything is solid; only the outer couple of pixels keep the soft edge. The backdrop seen
    # through a gap (between a tote's handles) stays out.
    disk = ndimage.generate_binary_structure(2, 1)
    solid = ndimage.binary_fill_holes(ndimage.binary_closing(a > .15, disk, iterations=6)) & (bg < .5)
    a = np.minimum(a, ndimage.grey_opening(a, size=(7, 7)))  # thin contact shadow where a bag meets the floor
    a = np.maximum(a, ndimage.binary_erosion(solid, disk, iterations=2).astype(np.float32))
    g2 = np.minimum(g, np.maximum(r, b) + 4)  # take the green cast off the edges
    lum = .2126 * r + .7152 * g2 + .0722 * b
    # The shadow a bag casts where it stands on the floor: dark pixels below the lowest lit fabric in each column.
    lit = (a > .5) & (lum >= 90)
    for x in np.where(lit.any(0))[0]:
        y = np.where(lit[:, x])[0].max()
        a[y + 1:, x] *= lum[y + 1:, x] >= 90
    return a, lum


def frame(a, lum, fill, w=W, h=H):
    ys, xs = np.where(a > .05)
    a, lum = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1], lum[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    s = min(w * fill / a.shape[1], h * fill / a.shape[0])
    size = (max(1, round(a.shape[1] * s)), max(1, round(a.shape[0] * s)))
    A = np.asarray(Image.fromarray((a * 255).astype(np.uint8)).resize(size, Image.LANCZOS), dtype=np.float32) / 255
    L = np.asarray(Image.fromarray(np.clip(lum, 0, 255).astype(np.uint8)).resize(size, Image.LANCZOS), dtype=np.float32)
    ca, cl = np.zeros((h, w), np.float32), np.zeros((h, w), np.float32)
    ox, oy = (w - size[0]) // 2, (h - size[1]) // 2
    ca[oy:oy + size[1], ox:ox + size[0]] = A; cl[oy:oy + size[1], ox:ox + size[0]] = L
    return ca, cl, (ox / w, oy / h, size[0] / w, size[1] / h)


def layers(a, lum):
    """Shading normalised so lit cloth is 1 (the colour shows exactly), plus a highlight map for ridges."""
    inside = lum[a > .9]
    ref, mid, top = np.percentile(inside, 88), np.percentile(inside, 55), np.percentile(inside, 99.5)
    shade = np.clip(lum / ref, .16, 1)  # the inside of a hood or collar stays a deep shade of the colour, not black
    hi = np.clip((lum - mid) / max(1, top - mid), 0, 1) ** 1.6 * .32
    return shade, hi


def rgba(v, a):
    g = (np.clip(v, 0, 1) * 255).astype(np.uint8)
    return Image.fromarray(np.dstack([g, g, g, (a * 255).astype(np.uint8)]), 'RGBA')


def tint(shade, hi, a, hexc, bg=(242, 242, 240)):
    """What the page will show: colour x shade, highlights screened on, over a background."""
    c = np.array([int(hexc[i:i + 2], 16) for i in (1, 3, 5)], np.float32) / 255
    m = c[None, None, :] * shade[..., None]
    s = 1 - (1 - m) * (1 - hi[..., None])
    out = s * a[..., None] + np.array(bg, np.float32)[None, None, :] / 255 * (1 - a[..., None])
    return (out * 255).astype(np.uint8)


def run(name, raw, out, colours):
    kind = name.split('@')[0]
    rgb = np.asarray(Image.open(raw / f'{name}.png').convert('RGB'), dtype=np.float32)
    a, lum = key(rgb)
    a, lum, box = frame(a, lum, FILL.get(kind, .84))
    shade, hi = layers(a, lum)
    d = out / name; d.mkdir(parents=True, exist_ok=True)
    rgba(shade, a).save(d / 'shade.webp', quality=88, method=6)
    rgba(hi, a).save(d / 'hi.webp', quality=80, method=6)
    json.dump({'box': [round(v, 4) for v in box]}, open(d / 'box.json', 'w'))
    tiles = [tint(shade, hi, a, h) for h in colours]
    half = (len(tiles) + 1) // 2
    rows = [np.concatenate(tiles[:half], 1), np.concatenate(tiles[half:] + [np.full_like(tiles[0], 242)] * (half - len(tiles[half:])), 1)]
    (out / 'previews').mkdir(exist_ok=True)
    Image.fromarray(np.concatenate(rows, 0)).resize((W * half // 2, H)).save(out / 'previews' / f'{name}.jpg', quality=82)
    print(name, 'box', [round(v, 3) for v in box])


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('names', nargs='+')
    ap.add_argument('--raw', default='raw'); ap.add_argument('--out', default='out')
    ap.add_argument('--colours', default=','.join(PREVIEW))
    o = ap.parse_args()
    for n in o.names:
        run(n, Path(o.raw), Path(o.out), o.colours.split(','))
