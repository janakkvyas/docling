#!/usr/bin/env python3
"""Tile PNG figures into one contact sheet (2 columns) for visual QA."""
import sys
from pathlib import Path
from PIL import Image
out, files = Path(sys.argv[1]), [Path(f) for f in sys.argv[2:]]
W = 900
tiles = []
for f in files:
    im = Image.open(f).convert("RGB"); im = im.resize((W, int(im.height * W / im.width)))
    tiles.append(im)
rows = [tiles[i:i+2] for i in range(0, len(tiles), 2)]
H = sum(max(t.height for t in r) for r in rows) + 10 * len(rows)
sheet = Image.new("RGB", (2 * W + 10, H), "white"); y = 0
for r in rows:
    for j, t in enumerate(r): sheet.paste(t, (j * (W + 10), y))
    y += max(t.height for t in r) + 10
sheet.save(out, quality=80); print(out, sheet.size)
