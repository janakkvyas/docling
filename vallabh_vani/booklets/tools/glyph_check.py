#!/usr/bin/env python3
"""Verify a page-marked transcription against the glyphs a PDF actually draws.

    glyph_check.py PDF TRANSCRIPTION.md FONT.ttf [--fix-zwnj OUT.md] [--font-name SUBSTR]

Each page's text (between <!-- p.N --> markers) is shaped word by word with HarfBuzz using the font the PDF
embeds (extract it with pdf_fonts.py; if the PDF's subset lost cmap entries, pdf_fonts.py --patch restores
ई ऐ ि), and the glyph ids are compared with the PDF's own glyph stream for that page (spaces ignored, curly
and straight quotes treated alike). A word that matches only when a ZERO WIDTH NON-JOINER follows one of its
viramas is printed with a visible virama; --fix-zwnj writes the transcription with those ZWNJs inserted.
Every other difference is reported with its context: it is a transcription error until shown otherwise.
"""

from __future__ import annotations

import ctypes
import difflib
import itertools
import re
import sys
from pathlib import Path

import pymupdf

hb = ctypes.CDLL("libharfbuzz.so.0")
for fn, res, args in (
    ("hb_blob_create_from_file", ctypes.c_void_p, [ctypes.c_char_p]),
    ("hb_face_create", ctypes.c_void_p, [ctypes.c_void_p, ctypes.c_uint]),
    ("hb_font_create", ctypes.c_void_p, [ctypes.c_void_p]),
    ("hb_buffer_create", ctypes.c_void_p, []),
    (
        "hb_buffer_add_utf8",
        None,
        [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_uint, ctypes.c_int],
    ),
    ("hb_buffer_guess_segment_properties", None, [ctypes.c_void_p]),
    (
        "hb_shape",
        None,
        [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint],
    ),
    ("hb_buffer_destroy", None, [ctypes.c_void_p]),
):
    getattr(hb, fn).restype = res
    getattr(hb, fn).argtypes = args


class _Info(ctypes.Structure):
    _fields_ = [
        ("codepoint", ctypes.c_uint32),
        ("mask", ctypes.c_uint32),
        ("cluster", ctypes.c_uint32),
        ("v1", ctypes.c_uint32),
        ("v2", ctypes.c_uint32),
    ]


hb.hb_buffer_get_glyph_infos.restype = ctypes.POINTER(_Info)
hb.hb_buffer_get_glyph_infos.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint)]
ZWNJ, VIRAMA = "‌", "्"


class Shaper:
    def __init__(self, font: Path):
        blob = hb.hb_blob_create_from_file(str(font).encode())
        self.font = hb.hb_font_create(hb.hb_face_create(blob, 0))
        self.cache: dict[str, tuple[int, ...]] = {}
        self.ignore = {0, self._raw(" ")[0]}
        q = [self._raw(c)[0] for c in '"“”']
        s = [self._raw(c)[0] for c in "'‘’"]
        self.canon = dict.fromkeys(q, q[0]) | dict.fromkeys(s, s[0])

    def _raw(self, text: str) -> tuple[int, ...]:
        buf = hb.hb_buffer_create()
        data = text.encode()
        hb.hb_buffer_add_utf8(buf, data, len(data), 0, len(data))
        hb.hb_buffer_guess_segment_properties(buf)
        hb.hb_shape(self.font, buf, None, 0)
        n = ctypes.c_uint()
        info = hb.hb_buffer_get_glyph_infos(buf, ctypes.byref(n))
        out = tuple(info[i].codepoint for i in range(n.value))
        hb.hb_buffer_destroy(buf)
        return out

    def word(self, w: str) -> tuple[int, ...]:
        if w not in self.cache:
            self.cache[w] = tuple(
                self.canon.get(g, g) for g in self._raw(w) if g not in self.ignore
            )
        return self.cache[w]


def pdf_glyphs(doc, page: int, font_sub: str, sh: Shaper) -> list[int]:
    seen, out, rows = set(), [], []
    for sp in doc[page - 1].get_texttrace():
        if font_sub not in sp["font"]:
            continue
        key = (
            round(sp["bbox"][0], 1),
            round(sp["bbox"][1], 1),
            tuple(c[1] for c in sp["chars"]),
        )
        if key in seen:
            continue
        seen.add(key)
        rows.append(
            (
                round(sp["chars"][0][2][1] / 3),
                sp["chars"][0][2][0],
                [c[1] for c in sp["chars"]],
            )
        )
    for _, _, gids in sorted(rows, key=lambda r: (r[0], r[1])):
        out += [sh.canon.get(g, g) for g in gids if g not in sh.ignore]
    return out


def strip_md(s: str) -> str:
    s = re.sub(r"<!--.*?-->", " ", s, flags=re.S)
    s = re.sub(r"!\[[^\]]*\]\([^)]*\)(\{[^}]*\})?", " ", s)
    s = re.sub(r"^:::.*$", " ", s, flags=re.M)
    s = re.sub(r"^\s*#+\s*", "", s, flags=re.M)
    s = re.sub(r"^\s*\|\s?", "", s, flags=re.M)
    s = re.sub(r"^\s*[-*+]\s+", "", s, flags=re.M)  # list markers
    s = re.sub(r"\{[#.][^}]*\}", " ", s)
    return s.replace("**", "").replace("&zwnj;", ZWNJ)


def pages_of(md: str) -> list[tuple[int, int, int]]:
    marks = [
        (m.start(), m.end(), int(m.group(1)))
        for m in re.finditer(r"<!--\s*p\.(\d+)[^>]*-->", md)
    ]
    return [
        (n, e, marks[i + 1][0] if i + 1 < len(marks) else len(md))
        for i, (s, e, n) in enumerate(marks)
    ]


def zwnj_variants(w: str):
    spots = [m.end() for m in re.finditer(VIRAMA + r"(?=[क-हक़-य़])", w)]
    for k in range(1, min(len(spots), 3) + 1):
        for combo in itertools.combinations(spots, k):
            v = w
            for pos in sorted(combo, reverse=True):
                v = v[:pos] + ZWNJ + v[pos:]
            yield v


def contains(hay: list[int], needle: tuple[int, ...]) -> bool:
    n = len(needle)
    return n > 0 and any(
        hay[i : i + n] == list(needle) for i in range(len(hay) - n + 1)
    )


def main() -> int:
    pdf, md_path, font = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    font_sub = (
        sys.argv[sys.argv.index("--font-name") + 1]
        if "--font-name" in sys.argv
        else "F2"
    )
    fix_out = (
        Path(sys.argv[sys.argv.index("--fix-zwnj") + 1])
        if "--fix-zwnj" in sys.argv
        else None
    )
    doc, sh, md = pymupdf.open(pdf), Shaper(font), md_path.read_text()
    edits: list[tuple[int, int, str]] = []
    total = 0
    for page, start, end in pages_of(md):
        want = pdf_glyphs(doc, page, font_sub, sh)
        region = md[start:end]
        text_words = strip_md(region).split()
        # ZWNJ: a word that is not in the PDF as shaped, but is with a ZWNJ after a virama
        for w in set(text_words):
            if VIRAMA in w and not contains(want, sh.word(w)):
                for v in zwnj_variants(w):
                    if contains(want, sh.word(v)):
                        # whole tokens only: a token may touch markdown (** or a line-block bar), never letters
                        for m in re.finditer(
                            r"(?<![^\s*|])" + re.escape(w) + r"(?![^\s*])", region
                        ):
                            edits.append((start + m.start(), start + m.end(), v))
                        text_words = [v if t == w else t for t in text_words]
                        break
        got, owner = [], []
        for i, w in enumerate(text_words):
            g = sh.word(w)
            got += g
            owner += [i] * len(g)
        sm = difflib.SequenceMatcher(None, want, got, autojunk=False)
        ops = [o for o in sm.get_opcodes() if o[0] != "equal"]
        # the same glyph a position or two earlier in one stream than the other is a difference in how two
        # shaping engines order a mark (reph, anusvara), not in the text: pair such moves and drop them
        moved = set()
        for a, (op1, i1, i2, j1, j2) in enumerate(ops):
            for b, (op2, k1, k2, l1, l2) in enumerate(ops):
                if (
                    a < b
                    and a not in moved
                    and b not in moved
                    and {op1, op2} == {"insert", "delete"}
                ):
                    g1 = got[j1:j2] if op1 == "insert" else want[i1:i2]
                    g2 = got[l1:l2] if op2 == "insert" else want[k1:k2]
                    if g1 == g2 and abs(i1 - k1) <= 30:
                        moved |= {a, b}
        problems = []
        for n, (op, i1, i2, j1, j2) in enumerate(ops):
            if n in moved:
                continue
            lo = owner[j1] if j1 < len(owner) else len(text_words) - 1
            hi = owner[j2 - 1] if 0 < j2 <= len(owner) and j2 > j1 else lo
            ctx = " ".join(text_words[max(0, lo - 2) : hi + 3])
            problems.append(
                f"   {op:7} pdf glyphs {want[i1:i2][:8]} vs text glyphs {got[j1:j2][:8]} near: {ctx}"
            )
        print(
            f"p.{page}: {len(want)} glyphs in the PDF, {len(got)} from the text, {len(problems)} differences"
            f" ({len(moved) // 2} mark-order moves ignored)"
        )
        for p in problems:
            print(p)
        total += len(problems)
    if fix_out:
        out, last = md, len(md) + 1
        for s, e, v in sorted(set(edits), reverse=True):
            if e > last:  # never apply two edits to overlapping text
                continue
            out = out[:s] + v + out[e:]
            last = s
        fix_out.write_text(out)
        print(f"wrote {fix_out} with {len(set(edits))} ZWNJ insertions")
    print("TOTAL DIFFERENCES", total)
    return 0


if __name__ == "__main__":
    sys.exit(main())
