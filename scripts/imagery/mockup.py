"""Put artwork onto your own studio garment photo (from garment.py's raw shots), matching existing renders.

Two kinds of artwork:
  --flatlay  a print lifted off an old mockup slide (garment flat lay on the left half, black garment): its black ground
             drops away (screen blend), so only the ink lands on the new garment, where it sat before.
  --art      a cut-out file (PNG with alpha, e.g. a logo rendered from SVG): laid over the cloth at --at cx,cy,width
             (fractions of the garment's bounding box).
Then the garment's shading and highlights go over everything, so folds and light cross the print too.

  python mockup.py --garment raw/t-shirt.png --colour '#1D1C1A' --flatlay old/02.jpg --out tee.jpg
  python mockup.py --garment raw/hoodie.png --colour '#161616' --art logo.png --at .5,.46,.36 --out hoodie.jpg
  options: --size 1800 --bg 189,189,189 --fill .76   (measure the existing renders first and match them)

Replaces mockups that sit on other brands' product or model photos. Needs numpy, scipy, Pillow; imports key() from
garment.py next to it.
"""
import argparse, sys
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage

sys.path.insert(0, str(Path(__file__).parent))
from garment import key  # noqa: E402


def garment(path, size=1800, fill=.76):
    rgb = np.asarray(Image.open(path).convert('RGB'), dtype=np.float32)
    a, lum = key(rgb)
    ys, xs = np.where(a > .05)
    a, lum = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1], lum[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    k = size * fill / max(a.shape)
    dims = (round(a.shape[1] * k), round(a.shape[0] * k))
    A = np.asarray(Image.fromarray((a * 255).astype(np.uint8)).resize(dims, Image.LANCZOS), np.float32) / 255
    L = np.asarray(Image.fromarray(np.clip(lum, 0, 255).astype(np.uint8)).resize(dims, Image.LANCZOS), np.float32)
    ca, cl = np.zeros((size, size), np.float32), np.zeros((size, size), np.float32)
    ox, oy = (size - dims[0]) // 2, (size - dims[1]) // 2 + size // 90
    ca[oy:oy + dims[1], ox:ox + dims[0]] = A; cl[oy:oy + dims[1], ox:ox + dims[0]] = L
    inside = cl[ca > .9]
    ref, mid, top = np.percentile(inside, 88), np.percentile(inside, 55), np.percentile(inside, 99.5)
    return {'a': ca, 'shade': np.clip(cl / ref, .16, 1), 'hi': np.clip((cl - mid) / max(1, top - mid), 0, 1) ** 1.6 * .32,
            'box': (ox, oy, dims[0], dims[1]), 'size': size}


def lift_print(path):
    """The print on the black flat lay in the left half of a mockup slide: its pixels, the garment's black, and where
    it sits on the garment (centre x, centre y, width; fractions of the garment's bounding box)."""
    im = np.asarray(Image.open(path).convert('RGB'), dtype=np.float32) / 255
    im = im[:, :im.shape[1] // 2]
    lum = im @ np.array([.2126, .7152, .0722], np.float32)
    dark = lum < .25
    lab, n = ndimage.label(dark)
    dark = lab == (np.argmax(ndimage.sum(dark, lab, range(1, n + 1))) + 1)
    body = ndimage.binary_fill_holes(dark)
    ink = body & ~dark
    lab, n = ndimage.label(ndimage.binary_dilation(ink, iterations=6))
    sizes = ndimage.sum(ink, lab, range(1, n + 1))
    big = np.isin(lab, [i + 1 for i, s in enumerate(sizes) if s > sizes.max() * .02])  # drops a neck label
    ys, xs = np.where(big & ink)
    y0, y1, x0, x1 = ys.min() - 8, ys.max() + 9, xs.min() - 8, xs.max() + 9
    ty, tx = np.where(body)
    tb = (tx.min(), ty.min(), tx.max() - tx.min(), ty.max() - ty.min())
    rel = ((x0 + x1) / 2 - tb[0]) / tb[2], ((y0 + y1) / 2 - tb[1]) / tb[3], (x1 - x0) / tb[2]
    return {'px': im[y0:y1, x0:x1], 'black': np.median(im[dark], axis=0), 'rel': rel}


def load_art(path, at):
    art = np.asarray(Image.open(path).convert('RGBA'), np.float32) / 255
    ys, xs = np.where(art[..., 3] > .15)  # a low threshold keeps near-invisible fringe and throws the centring off
    return {'px': art[ys.min():ys.max() + 1, xs.min():xs.max() + 1], 'rel': at}


def compose(g, colour, prints, out, bg=(189, 189, 189)):
    S = g['size']
    c = np.array([int(colour[i:i + 2], 16) for i in (1, 3, 5)], np.float32) / 255
    alb = np.broadcast_to(c, (S, S, 3)).copy()
    ox, oy, gw, gh = g['box']
    for p in prints:
        cx, cy, wr = p['rel']
        px = p['px']; w = round(gw * wr); h = round(px.shape[0] * w / px.shape[1])
        img = np.asarray(Image.fromarray((np.clip(px, 0, 1) * 255).astype(np.uint8), 'RGBA' if px.shape[2] == 4 else 'RGB').resize((w, h), Image.LANCZOS), np.float32) / 255
        x0, y0 = round(ox + gw * cx - w / 2), round(oy + gh * cy - h / 2)
        region = alb[y0:y0 + h, x0:x0 + w]
        if img.shape[2] == 4:
            al = img[..., 3:]
            region[:] = img[..., :3] * al + region * (1 - al)
        else:
            ink = np.clip((img - p['black'] - .04) / (1 - p['black'] - .04), 0, 1)
            fy = np.minimum(np.arange(h) / 12, (h - 1 - np.arange(h)) / 12).clip(0, 1)
            fx = np.minimum(np.arange(w) / 12, (w - 1 - np.arange(w)) / 12).clip(0, 1)
            ink *= np.minimum.outer(fy, fx)[..., None]
            region[:] = 1 - (1 - region) * (1 - ink)
    m = alb * g['shade'][..., None]
    m = 1 - (1 - m) * (1 - g['hi'][..., None])
    yy, xx = np.mgrid[0:S, 0:S]
    sh = np.exp(-(((xx - S / 2) / (gw * .42)) ** 2 + ((yy - (oy + gh + 4)) / (S / 80)) ** 2)) * .22
    back = np.array(bg, np.float32)[None, None, :] / 255 * (1 - sh[..., None])
    a = g['a'][..., None]
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray((np.clip(m * a + back * (1 - a), 0, 1) * 255).astype(np.uint8)).save(out, quality=90)
    print('wrote', out)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--garment', required=True); ap.add_argument('--colour', required=True); ap.add_argument('--out', required=True)
    ap.add_argument('--flatlay', action='append', default=[]); ap.add_argument('--art', action='append', default=[])
    ap.add_argument('--at', action='append', default=[], help='cx,cy,width for each --art, in order')
    ap.add_argument('--size', type=int, default=1800); ap.add_argument('--fill', type=float, default=.76)
    ap.add_argument('--bg', default='189,189,189')
    o = ap.parse_args()
    prints = [lift_print(f) for f in o.flatlay]
    prints += [load_art(f, tuple(float(v) for v in at.split(','))) for f, at in zip(o.art, o.at)]
    compose(garment(o.garment, o.size, o.fill), o.colour, prints, o.out, tuple(int(v) for v in o.bg.split(',')))
