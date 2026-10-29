#!/usr/bin/env bash
# One headless pass over a board preview (made by embed_images.py --preview):
#   1. dump the DOM after the scripts have run and report any script error caught by the hook
#   2. take a tall desktop screenshot and cut it into viewable parts
# Usage: check_board.sh PREVIEW_HTML OUT_DIR [HEIGHT]
set -euo pipefail
PREVIEW="$1"; OUT="$2"; H="${3:-12000}"
mkdir -p "$OUT"
CH="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
[ -x "$CH" ] || { echo "Chrome not found; set CHROME=/path/to/chrome"; exit 1; }

ERR=$("$CH" --headless=new --disable-gpu --virtual-time-budget=5000 --dump-dom "file://$PREVIEW" 2>/dev/null | grep -o '<html[^>]*>' | grep -o 'data-err="[^"]*"' || true)
if [ -n "$ERR" ]; then echo "SCRIPT ERRORS: $ERR"; else echo "no script errors"; fi

"$CH" --headless=new --disable-gpu --hide-scrollbars --window-size=1440,"$H" --virtual-time-budget=7000 \
  --screenshot="$OUT/full.png" "file://$PREVIEW" >/dev/null 2>&1
python3 - "$OUT" <<'EOF' || echo "(Pillow missing: open $OUT/full.png directly)"
import sys
from PIL import Image
out = sys.argv[1]
im = Image.open(out + "/full.png").convert("RGB")
w, h = im.size
step = 3000
for i, top in enumerate(range(0, h, step)):
    c = im.crop((0, top, w, min(h, top + step)))
    c = c.resize((c.width * 45 // 100, c.height * 45 // 100))
    c.save(f"{out}/part{i}.jpg", quality=72)
    print(f"{out}/part{i}.jpg")
EOF
