#!/usr/bin/env python3
"""Check a page-marked transcription against the PDF's (lossy) text layer.

The text layer of the Print-to-PDF booklet keeps most characters exactly but drops conjunct
glyphs, the short-i sign and some vowel-sign ligatures, writes ई as इ and ऐ as ए+े, and inserts
spaces. So every character the layer DOES have must appear, in order, in a correct transcription.
This script aligns the two per page and reports
  A. layer characters with no counterpart in the transcription (almost always a transcription error),
  B. Latin letters, digits and punctuation in the transcription that the layer lacks.
Usage: check_layer.py TRANSCRIPTION.md [LAYER_DIR]   (pages are marked <!-- p.N --> / <!-- p.N cont -->)
"""

from __future__ import annotations

import difflib
import re
import sys
import unicodedata
from pathlib import Path

LAYER = (
    Path(sys.argv[2])
    if len(sys.argv) > 2
    else Path(__file__).resolve().parent.parent / "layer"
)
STRONG = re.compile(r"[A-Za-z0-9०-९.,;:?!()\-—'\"%&/]")


def norm(s: str) -> str:
    s = unicodedata.normalize("NFD", s)
    for a, b in (
        ("“", '"'),
        ("”", '"'),
        ("‘", "'"),
        ("’", "'"),
        ("ई", "इ"),
        ("ऐ", "एे"),
        ("ॐ", "ओम"),
    ):
        s = s.replace(a, b)
    s = s.replace("॥", "॥").replace(
        "।।", "॥"
    )  # treat a typed double single-daṇḍa like ॥ for alignment
    return re.sub(r"\s+", "", s)


def strip_md(s: str) -> str:
    s = re.sub(r"<!--.*?-->", " ", s, flags=re.S)
    s = re.sub(r"!\[[^\]]*\]\([^)]*\)(\{[^}]*\})?", " ", s)
    s = re.sub(r"^\s*#+\s*", "", s, flags=re.M)
    s = re.sub(r"^\s*\|\s?", "", s, flags=re.M)
    s = re.sub(r"^\s*[-*]\s+", "", s, flags=re.M)
    s = s.replace("**", "").replace("::: ", "").replace(":::", "")
    s = re.sub(r"\{[^}]*\}", " ", s)
    return s


def pages_of(md: str) -> dict[int, str]:
    parts = re.split(r"<!--\s*p\.(\d+)(?:\s+cont)?\s*-->", md)
    out: dict[int, str] = {}
    for i in range(1, len(parts), 2):
        out[int(parts[i])] = out.get(int(parts[i]), "") + parts[i + 1]
    return out


def layer_text(n: int) -> str:
    t = (LAYER / f"p-{n:02d}.txt").read_text()
    lines = [ln for ln in t.splitlines() if ln.strip()]
    if lines and re.fullmatch(r"\s*\d+\s*", lines[-1]):
        lines = lines[:-1]  # folio
    return "\n".join(lines)


def main() -> int:
    md = Path(sys.argv[1]).read_text()
    total = 0
    for n, body in sorted(pages_of(md).items()):
        lay, tra = norm(layer_text(n)), norm(strip_md(body))
        sm = difflib.SequenceMatcher(None, lay, tra, autojunk=False)
        issues = []
        for op, i1, i2, j1, j2 in sm.get_opcodes():
            if op in ("replace", "delete"):
                issues.append(
                    (
                        "A",
                        lay[max(0, i1 - 12) : i2 + 12],
                        lay[i1:i2],
                        tra[max(0, j1 - 12) : j2 + 12],
                    )
                )
            if op in ("replace", "insert"):
                extra = tra[j1:j2]
                if STRONG.search(extra):
                    issues.append(
                        (
                            "B",
                            lay[max(0, i1 - 12) : i2 + 12],
                            extra,
                            tra[max(0, j1 - 12) : j2 + 12],
                        )
                    )
        ratio = len(tra) / max(1, len(lay))
        print(
            f"p.{n}: layer {len(lay)} chars, transcription {len(tra)} chars (x{ratio:.2f}), issues {len(issues)}"
        )
        for kind, lctx, what, tctx in issues:
            print(f"   {kind} {what!r:>14}  layer …{lctx}…  |  yours …{tctx}…")
        total += len(issues)
    print("TOTAL ISSUES", total)
    return 0


if __name__ == "__main__":
    sys.exit(main())
