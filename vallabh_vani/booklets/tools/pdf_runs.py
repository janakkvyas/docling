#!/usr/bin/env python3
"""Print the text runs of PDF pages with font, size, weight and position (to learn an exemplar's typography).

    pdf_runs.py EXEMPLAR.pdf PAGE [PAGE ...]

One line per run: font, size in pt, "bold" when the PDF draws it with fill+stroke (Word's synthetic bold) or
the font is a bold face, x range, baseline, and the text as the PDF's text layer gives it (which may be broken
for Devanagari: judge sizes and positions here, read the words in the page image). Duplicate runs (some PDFs
draw text twice) are shown once.
"""

from __future__ import annotations

import sys

import pymupdf

doc = pymupdf.open(sys.argv[1])
for p in [int(x) for x in sys.argv[2:]]:
    print(f"===== page {p}")
    seen, rows = set(), []
    for sp in doc[p - 1].get_texttrace():
        if not sp["chars"]:
            continue
        x0, y0, x1, y1 = sp["bbox"]
        key = (round(x0, 1), round(y0, 1), tuple(c[1] for c in sp["chars"]))
        if key in seen:
            continue
        seen.add(key)
        text = "".join(chr(c[0]) if c[0] > 0 else "·" for c in sp["chars"])
        bold = (
            sp.get("type") == 2
            or "bold" in sp["font"].lower()
            or "gras" in sp["font"].lower()
        )
        base = sp["chars"][0][2][1]
        rows.append((round(base, 1), x0, sp["font"], sp["size"], bold, x1, text))
    rows.sort()
    for base, x0, font, size, bold, x1, text in rows:
        if text.strip():
            print(
                f"  {font[:20]:20} {size:5.1f}pt {'bold' if bold else '    '} x {x0:6.1f}-{x1:6.1f} base {base:6.1f} | {text[:70]}"
            )
