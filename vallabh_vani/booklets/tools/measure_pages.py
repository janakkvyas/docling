#!/usr/bin/env python3
"""Print the vertical positions of text lines (yMin of each line box, pt) on given pages of one or more PDFs.
Usage: measure_pages.py PDF:PAGE [PDF:PAGE ...]"""

import re
import subprocess
import sys
from itertools import pairwise

for arg in sys.argv[1:]:
    pdf, page = arg.rsplit(":", 1)
    h = subprocess.run(
        ["pdftotext", "-f", page, "-l", page, "-bbox-layout", pdf, "-"],
        capture_output=True,
        text=True,
    ).stdout
    rows = []
    for l in re.findall(
        r'<line xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</line>',
        h,
        re.S,
    ):
        words = " ".join(re.findall(r">([^<]+)</word>", l[4]))
        rows.append((float(l[1]), float(l[0]), float(l[2]), words))
    rows.sort()
    merged = []
    for r in rows:
        if merged and abs(merged[-1][0] - r[0]) < 2:
            continue
        merged.append(r)
    ys = [r[0] for r in merged]
    gaps = [round(b - a, 1) for a, b in pairwise(ys)]
    print(
        f"{pdf.split('/')[-1]} p.{page}: {len(merged)} lines; first y {ys[0]:.1f}, last y {ys[-1]:.1f}; gaps {gaps}"
    )
