#!/usr/bin/env python3
"""Check a booklet source against the house conventions (vallabh_vani/booklets/SPEC_*.md).

    lint_booklet.py SOURCE.md

ERROR lines must be fixed before a build is delivered; WARN lines are for the editor to look at (a standard
Hindi form can be right inside someone else's quoted words). The kind comes from `booklet:` in the YAML block.
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

DEVDIG = "०१२३४५६७८९"


def word(w: str) -> re.Pattern:
    return re.compile(r"(?<![\u0900-\u097F])" + w + r"(?![\u0900-\u097F])")


def main() -> int:
    path = Path(sys.argv[1])
    md = path.read_text()
    lines = md.splitlines()
    kind = (re.search(r"^booklet:\s*(\w+)", md, re.M) or [None, "hindi"])[1]
    errors, warns = [], []
    body = re.sub(r"<!--.*?-->", "", md, flags=re.S)

    def where(rx: re.Pattern, limit: int = 8) -> str:
        hits = [str(i) for i, l in enumerate(lines, 1) if rx.search(l)]
        return ", ".join(hits[:limit]) + (" …" if len(hits) > limit else "")

    if "\u090f\u0947" in md:
        errors.append(
            f"ए + े typed for ऐ (lines {where(re.compile(chr(0x90F) + chr(0x947)))}): type the letter ऐ"
        )
    if re.search(r"\[\d\d:\d\d:\d\d\]", body):
        errors.append("timestamps left in the text")
    if re.search(r"‹[^›]*›", body):
        errors.append(
            f"editorial flags ‹…› left in the text (lines {where(re.compile('‹'))}): resolve them before delivery"
        )

    if kind == "hindi":
        for key in ("title:", "subtitle:", "occasion:", "speaker:"):
            if not re.search(r"^" + key, md, re.M):
                errors.append(f"YAML block lacks {key}")
        for ph in ("{{अनुक्रमणिका}}", "{{उद्धृत वचन}}"):
            if ph not in md:
                warns.append(
                    f"placeholder {ph} missing (contents / index will not be generated)"
                )
        heads = re.findall(r"^# (.+)$", md, re.M)
        nums = []
        for h in heads:
            m = re.match(r"खण्ड ([" + DEVDIG + r"]+) — \S", h)
            if not m:
                errors.append(f"heading not in the form '# खण्ड N — title': {h}")
                continue
            nums.append(int("".join(str(DEVDIG.index(c)) for c in m.group(1))))
        if nums and nums != list(range(1, len(nums) + 1)):
            errors.append(f"खण्ड numbers not consecutive: {nums}")
        if re.search(r"^\*\*(Speaker|A student|Listener)", md, re.M):
            errors.append(
                "speaker labels belong to the English editions, not to the booklet"
            )
        prose = re.sub(
            r"^#.*$", "", body, flags=re.M
        )  # headings are the editor's words
        prose = re.sub(r"\*\*.*?\*\*", "", prose)  # quotations are bold
        prose = re.sub(r"^\|.*$", "", prose, flags=re.M)  # verse lines
        prose = re.sub(r'"[^"\n]{0,400}?"', "", prose)  # other people's quoted words
        for std, own in (
            ("है", "हे"),
            ("हैं", "हें"),
            ("था", "हतो"),
            ("थे", "हते"),
            ("थी", "हती"),
        ):
            n = len(word(std).findall(prose))
            if n:
                warns.append(
                    f"{n} × {std} outside quotations (the speaker's form is {own}); lines {where(word(std))}"
                )
        for nasal, cb in (("यहां", "यहाँ"), ("वहां", "वहाँ"), ("कहां", "कहाँ"), ("हूं", "हूँ")):
            if word(nasal).search(body):
                warns.append(f"{nasal} → {cb} (lines {where(word(nasal))})")
        if "।।" in body:
            warns.append(f"'।।' typed: use ॥ (lines {where(re.compile('।।'))})")
        dandas = [
            i
            for i, l in enumerate(lines, 1)
            if "।" in re.sub(r"\*\*.*?\*\*", "", l)
            and not l.startswith("|")
            and not l.startswith("<")
        ]
        if dandas:
            warns.append(
                f"daṇḍa in Hindi prose (a Hindi sentence ends with '.'): lines {', '.join(map(str, dandas[:8]))}"
            )
        cand = re.compile(r"[क-ह]़?्(?=(?:सु|कु|को|की|के|में|ने|पे|से)(?![\u0900-\u097F]))")
        n = len(cand.findall(body))
        if n:
            warns.append(
                f"{n} virama + postposition without ZWNJ (the booklet shows a visible virama in लोगन्‌कु, "
                f"ऑर्डर्‌में: add U+200C where the speaker's form needs it); lines {where(cand)}"
            )
        quotes = re.findall(
            r'\*\*\s*["“]([^"”*]+)["”]?\s*\*\*\s*["”]?\s*(\(([^()]{2,60})\))?', body
        )
        unsourced = [q for q, src, _ in quotes if not src]
        if unsourced:
            warns.append(
                f"{len(unsourced)} bold quotations without a source (not indexed): "
                + "; ".join(u[:30] for u in unsourced[:5])
            )
        srcs = Counter(
            re.sub(r"[\s" + DEVDIG + r"0-9./\-–]+$", "", s) for _, _, s in quotes if s
        )
        variants = {}
        for s in srcs:
            k = re.sub(r"[.\s]", "", s)[:5]
            variants.setdefault(k, set()).add(s)
        for k, v in variants.items():
            if len(v) > 1:
                warns.append(
                    "one source written several ways: " + " | ".join(sorted(v))
                )
        for i, l in enumerate(lines, 1):
            if not l.startswith(("|", "<", "#", "-")) and l.count('"') % 2:
                warns.append(f"line {i}: odd number of quotation marks")
    else:
        labels = Counter(
            re.findall(
                r"^(श्लोक\s*[:ः]|śloka\S*\s*:|सुबोधिन[ीि]\s*:|Subodhin\S*\s*:)\s*$",
                md,
                re.M,
            )
        )
        groups = {}
        for lab, n in labels.items():
            groups.setdefault(lab[:3], []).append(f"{lab} ×{n}")
        for g in groups.values():
            if len(g) > 1:
                warns.append("label written several ways: " + ", ".join(g))
        marks = Counter(
            re.findall(r"(\|\||॥|।।|\|)\s*[" + DEVDIG + r"0-9]+\s*(\|\||॥|।।|\|)", md)
        )
        if len(marks) > 1:
            warns.append(
                "verse numbers closed several ways: "
                + ", ".join(f"{a}N{b} ×{n}" for (a, b), n in marks.items())
            )
        colon = [
            i
            for i, ln in enumerate(lines, 1)
            if re.search(r"[\u0900-\u097F]:", ln)
            and not ln.startswith(":::")
            and not re.match(r"^\s*(श्लोक|सुबोधिन)", ln)
        ]
        if colon:
            warns.append(
                f"a colon typed for the visarga ः in Devanagari (lines {', '.join(map(str, colon[:10]))})"
            )
        if re.search(r"\bTranl?sation|\bTranslaton|\bTrnaslation", md):
            errors.append(
                f"misspelt 'Translation' (lines {where(re.compile(r'Tranl?sation|Translaton|Trnaslation'))})"
            )
        paras = [p.strip() for p in re.split(r"\n\s*\n", body) if len(p.strip()) > 120]
        seen = {}
        for p in paras:
            key = re.sub(r"\W+", " ", p.lower())[:160]
            if key in seen:
                warns.append(f"paragraph printed twice: '{p[:60]}…'")
            seen[key] = 1
        for a, b in (
            ("Nalakūbera", "Nalakūbara"),
            ("Narada", "Nārada"),
            ("Śrikṛṣṇa", "Śrīkṛṣṇa"),
            ("Mahayogī", "Mahāyogī"),
            ("Krishna", "Kṛṣṇa"),
        ):
            if re.search(r"\b" + a + r"\b", md) and re.search(r"\b" + b + r"\b", md):
                warns.append(f"both {a} and {b} occur")
    for e in errors:
        print("ERROR", e)
    for w in warns:
        print("WARN ", w)
    print(f"{path.name}: {len(errors)} errors, {len(warns)} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
