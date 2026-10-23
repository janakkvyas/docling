#!/usr/bin/env python3
"""British spelling in the English of a lecture edition (the house style of the English books).

    british_spelling.py EDITION.md [...]     (rewrites the files; prints the changes)

Only the words and phrases below change. Left alone: Sanskrit in italics, words in a phrase flagged as
uncertain (the three words before ‹?›: a misheard phrase stays as transcribed), and the closing
"Terms, Verses and Flags" paragraph, which quotes what the recogniser heard.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

WORDS = {
    "realize": "realise",
    "realizes": "realises",
    "realized": "realised",
    "realizing": "realising",
    "realization": "realisation",
    "visualize": "visualise",
    "visualized": "visualised",
    "visualizes": "visualises",
    "visualizing": "visualising",
    "visualization": "visualisation",
    "analyze": "analyse",
    "analyzed": "analysed",
    "analyzes": "analyses",
    "analyzing": "analysing",
    "synchronized": "synchronised",
    "synchronization": "synchronisation",
    "globalization": "globalisation",
    "specialized": "specialised",
    "recognize": "recognise",
    "recognizes": "recognises",
    "recognized": "recognised",
    "demoralized": "demoralised",
    "systematize": "systematise",
    "systematized": "systematised",
    "organization": "organisation",
    "dichotomized": "dichotomised",
    "commercialized": "commercialised",
    "stabilizing": "stabilising",
    "synthesizing": "synthesising",
    "utilize": "utilise",
    "materialized": "materialised",
    "catalyze": "catalyse",
    "characterization": "characterisation",
    "center": "centre",
    "centers": "centres",
    "labor": "labour",
    "practiced": "practised",
    "color": "colour",
    "behavior": "behaviour",
    "favor": "favour",
    "honor": "honour",
    "fulfill": "fulfil",
}
PHRASES = [  # spelling that depends on the sense (practise as a verb, programme of an event)
    (r"\byou practice it\b", "you practise it"),
    (r"\bentertainment program\b(?!me)", "entertainment programme"),
    (r"\bor program was there\b", "or programme was there"),
]
ITALIC = re.compile(r"(?<!\*)\*(?!\*)[^*\n]+?\*(?!\*)")


def fix(text: str) -> tuple[str, list[str]]:
    keep = [(m.start(), m.end()) for m in ITALIC.finditer(text)]
    keep += [(m.start(), m.end()) for m in re.finditer(r"(?:\S+\s+){0,3}\S*‹\?›", text)]
    keep += [
        (m.start(), m.end())
        for m in re.finditer(r"\*\*Terms, Verses and Flags\.\*\*.*", text, re.S)
    ]
    changes: list[str] = []

    def word(m):
        w = m.group(0)
        if any(a <= m.start() < b for a, b in keep):
            return w
        new = WORDS[w.lower()]
        new = new.capitalize() if w[0].isupper() else new
        changes.append(f"{w} -> {new}")
        return new

    text = re.sub(r"\b(" + "|".join(WORDS) + r")\b", word, text, flags=re.I)
    for rx, rep in PHRASES:
        text, n = re.subn(rx, rep, text)
        changes += [rep] * n
    return text, changes


if __name__ == "__main__":
    for f in sys.argv[1:]:
        p = Path(f)
        old = p.read_text(encoding="utf-8")
        new, changes = fix(old)
        assert len(old.split()) == len(new.split())  # no word added or lost
        p.write_text(new, encoding="utf-8")
        print(f"{p.name}: {len(changes)} changes {sorted(set(changes))}")
