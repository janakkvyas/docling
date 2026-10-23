#!/usr/bin/env python3
"""List and extract the fonts embedded in a PDF (to learn an exemplar's typography).

    pdf_fonts.py EXEMPLAR.pdf OUTDIR [--patch]

For every embedded font: the real family and style (from the font's own name table; PDFs often hide them as
"CIDFont+F2"), ascent/descent, whether it is complete or a subset, and its Devanagari and Latin coverage.
The font files are written to OUTDIR. With --patch, Devanagari code points missing from a font's character
map (Microsoft Print to PDF drops ि, ई, ऐ …) are mapped again to their glyphs (named uniXXXX), so the font
can shape text for glyph_check.py. Embedded fonts keep their licences: Noto fonts are OFL; most Microsoft
fonts may not be redistributed.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pymupdf
from fontTools.ttLib import TTFont

pdf, out = sys.argv[1], Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
doc = pymupdf.open(pdf)
done = set()
for pno in range(len(doc)):
    for xref, ext, ftype, basename, *_ in doc.get_page_fonts(pno):
        if xref in done:
            continue
        done.add(xref)
        name, ext2, _, buf = doc.extract_font(xref)
        if not buf:
            print(f"{basename}: not embedded")
            continue
        path = out / f"{basename.replace('+', '_')}.{ext2 or 'bin'}"
        path.write_bytes(buf)
        try:
            f = TTFont(str(path))
        except Exception as e:  # CFF/Type1 fonts: report only
            print(f"{basename}: {ext2}, {len(buf)} bytes ({e.__class__.__name__})")
            continue
        cmap = (
            (f.getBestCmap() or {}) if "cmap" in f else {}
        )  # CID fonts embedded by InDesign often have no cmap
        upm = f["head"].unitsPerEm
        hh = f["hhea"]
        deva = sum(1 for c in cmap if 0x0900 <= c <= 0x097F)
        latin = sum(1 for c in cmap if 0x41 <= c <= 0x7A)
        added = []
        if "--patch" in sys.argv:
            names = set(f.getGlyphOrder())
            for cp in range(0x0900, 0x0980) if "cmap" in f else []:
                g = f"uni{cp:04X}"
                if cp not in cmap and g in names:
                    for t in f["cmap"].tables:
                        if t.isUnicode():
                            t.cmap[cp] = g
                    added.append(chr(cp))
            if added:
                f.save(str(path.with_name(path.stem + "_patched" + path.suffix)))
        first_page = pno + 1
        print(
            f"{basename}: {f['name'].getDebugName(4)} | {f['maxp'].numGlyphs} glyphs | ascent {hh.ascent / upm:.3f} "
            f"descent {-hh.descent / upm:.3f} em | Devanagari {deva}, Latin {latin} code points | "
            f"first used on p.{first_page}"
            + (f" | patched: {''.join(added)}" if added else "")
        )
