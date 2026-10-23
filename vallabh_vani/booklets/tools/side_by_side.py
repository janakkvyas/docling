#!/usr/bin/env python3
"""Pair pages of two PDFs side by side for visual comparison.
Usage: side_by_side.py A.pdf B.pdf OUT.png a1:b1 a2:b2 ...   (page pairs; A on the left)"""

import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

a, b, out = sys.argv[1], sys.argv[2], sys.argv[3]
pairs = [tuple(int(x) for x in p.split(":")) for p in sys.argv[4:]]
with tempfile.TemporaryDirectory() as t:

    def page(pdf, n, tag):
        stem = Path(t) / f"{tag}{n}"
        subprocess.run(
            [
                "pdftoppm",
                "-r",
                "60",
                "-png",
                "-f",
                str(n),
                "-l",
                str(n),
                "-singlefile",
                pdf,
                str(stem),
            ],
            check=True,
        )
        return Image.open(f"{stem}.png").convert("RGB")

    tiles = [(page(a, x, "a"), page(b, y, "b")) for x, y in pairs]
    w, h = tiles[0][0].size
    sheet = Image.new("RGB", (len(tiles) * (2 * w + 30) + 10, h + 30), "white")
    d = ImageDraw.Draw(sheet)
    for i, (l, r) in enumerate(tiles):
        x = 10 + i * (2 * w + 30)
        sheet.paste(l, (x, 25))
        sheet.paste(r.resize(l.size), (x + w + 4, 25))
        d.rectangle([x, 25, x + w - 1, 25 + h - 1], outline="#999999")
        d.rectangle([x + w + 4, 25, x + 2 * w + 3, 25 + h - 1], outline="#C46210")
        d.text((x + 4, 6), f"exemplar p.{pairs[i][0]}", fill="black")
        d.text((x + w + 8, 6), f"rebuild p.{pairs[i][1]}", fill="#C46210")
    sheet.save(out)
print(out)
