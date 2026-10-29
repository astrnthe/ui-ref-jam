#!/usr/bin/env python3
"""Embed images into a board template and write the publishable page plus a local preview.

The Artifact sandbox blocks outside image hosts, so board images travel as data: URIs.
Placeholders in the template look like %%IMG_key%%.

Usage:
  embed_images.py TEMPLATE OUT_HTML --img key=path [--img key=path ...]
                  [--width 420] [--quality 58] [--preview PREVIEW_HTML]

The preview wraps the page in the same skeleton the Artifact tool adds at publish time,
plus an error hook that writes script errors onto <body data-err="...">, so a headless
--dump-dom run (see check_board.sh) shows whether the page's script ran cleanly.
"""
import argparse, base64, io, mimetypes, re, sys

SKELETON_HEAD = (
    '<!doctype html><html><head><meta charset=utf-8>'
    '<meta name=viewport content="width=device-width,initial-scale=1,viewport-fit=cover">'
    '<style>:root{color-scheme:light}body{margin:0;font:14px system-ui}img{max-width:100%}[hidden]{display:none!important}</style>'
    '<script>addEventListener("error",e=>{document.documentElement.dataset.err=(document.documentElement.dataset.err||"")+e.message+" | "})</script>'
    '</head><body>'
)


def data_uri(path, width, quality):
    try:
        from PIL import Image  # optional: shrink so a dozen photos stay well under the size cap
        im = Image.open(path)
        buf = io.BytesIO()
        # Cut-outs keep their transparency: JPEG would fill it with black.
        if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
            im = im.convert("RGBA")
            if im.getextrema()[3][0] < 255:
                im.thumbnail((width, width))
                im.save(buf, "WEBP", quality=max(quality, 80), method=4)
                return "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode()
        im = im.convert("RGB")
        im.thumbnail((width, width))
        im.save(buf, "JPEG", quality=quality, optimize=True, progressive=True)
        return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
    except ImportError:
        mime = mimetypes.guess_type(path)[0] or "image/jpeg"
        with open(path, "rb") as f:
            return f"data:{mime};base64," + base64.b64encode(f.read()).decode()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("template")
    ap.add_argument("out")
    ap.add_argument("--img", action="append", default=[], help="key=path")
    ap.add_argument("--width", type=int, default=420)
    ap.add_argument("--quality", type=int, default=58)
    ap.add_argument("--preview")
    a = ap.parse_args()

    imgs = {}
    for spec in a.img:
        key, path = spec.split("=", 1)
        imgs[key] = data_uri(path, a.width, a.quality)

    html = open(a.template, encoding="utf-8").read()
    missing = sorted(set(re.findall(r"%%IMG_(\w+)%%", html)) - set(imgs))
    if missing:
        sys.exit("No image given for: " + ", ".join(missing))
    html = re.sub(r"%%IMG_(\w+)%%", lambda m: imgs[m.group(1)], html)

    open(a.out, "w", encoding="utf-8").write(html)
    if a.preview:
        open(a.preview, "w", encoding="utf-8").write(SKELETON_HEAD + html + "</body></html>")
    print(f"wrote {a.out} ({len(html)//1024} KB, {len(imgs)} images)")


if __name__ == "__main__":
    main()
