#!/usr/bin/env python3
"""Devanagari -> IAST in the house style of the English translation books (SPEC_ENGLISH_STUTI_BOOK.md).

    iast.py "कृष्णकी सर्वरूपता"        -> kṛṣṇakī sarvarūpatā
    iast.py --file verses.txt            (one line in, one line out)

Letter for letter, inherent vowel always written (Hindi titles too: अप्रकट -> aprakaṭa), anusvāra and
chandrabindu -> ṃ, visarga -> ḥ, avagraha -> ’, daṇḍas kept as printed, Devanagari digits -> Arabic.
Check every line by eye: the script cannot know sandhi spacing the print may want.
"""

from __future__ import annotations

import sys
from pathlib import Path

VOWELS = {
    "अ": "a",
    "आ": "ā",
    "इ": "i",
    "ई": "ī",
    "उ": "u",
    "ऊ": "ū",
    "ऋ": "ṛ",
    "ॠ": "ṝ",
    "ऌ": "ḷ",
    "ॡ": "ḹ",
    "ए": "e",
    "ऐ": "ai",
    "ओ": "o",
    "औ": "au",
    "ऑ": "ŏ",
    "ॲ": "ĕ",
}
SIGNS = {
    "ा": "ā",
    "ि": "i",
    "ी": "ī",
    "ु": "u",
    "ू": "ū",
    "ृ": "ṛ",
    "ॄ": "ṝ",
    "ॢ": "ḷ",
    "ॣ": "ḹ",
    "े": "e",
    "ै": "ai",
    "ो": "o",
    "ौ": "au",
    "ॉ": "ŏ",
    "ॅ": "ĕ",
}
CONS = {
    "क": "k",
    "ख": "kh",
    "ग": "g",
    "घ": "gh",
    "ङ": "ṅ",
    "च": "c",
    "छ": "ch",
    "ज": "j",
    "झ": "jh",
    "ञ": "ñ",
    "ट": "ṭ",
    "ठ": "ṭh",
    "ड": "ḍ",
    "ढ": "ḍh",
    "ण": "ṇ",
    "त": "t",
    "थ": "th",
    "द": "d",
    "ध": "dh",
    "न": "n",
    "प": "p",
    "फ": "ph",
    "ब": "b",
    "भ": "bh",
    "म": "m",
    "य": "y",
    "र": "r",
    "ल": "l",
    "ळ": "ḷ",
    "व": "v",
    "श": "ś",
    "ष": "ṣ",
    "स": "s",
    "ह": "h",
    "क़": "q",
    "ख़": "x",
    "ग़": "ġ",
    "ज़": "z",
    "ड़": "ṛ",
    "ढ़": "ṛh",
    "फ़": "f",
    "य़": "ẏ",
}
NUKTA_BASE = {
    "क": "क़",
    "ख": "ख़",
    "ग": "ग़",
    "ज": "ज़",
    "ड": "ड़",
    "ढ": "ढ़",
    "फ": "फ़",
    "य": "य़",
}
OTHER = {"ं": "ṃ", "ँ": "ṃ", "ः": "ḥ", "ऽ": "’", "ॐ": "oṃ", "‌": "", "‍": ""}
DIGITS = str.maketrans("०१२३४५६७८९", "0123456789")


def iast(text: str) -> str:
    out, i, n = [], 0, len(text)
    while i < n:
        ch = text[i]
        if ch in NUKTA_BASE and i + 1 < n and text[i + 1] == "़":
            ch, i = NUKTA_BASE[ch], i + 1
        if ch in CONS:
            out.append(CONS[ch])
            nxt = text[i + 1] if i + 1 < n else ""
            if nxt == "्":
                i += 2
                continue
            if nxt in SIGNS:
                out.append(SIGNS[nxt])
                i += 2
                continue
            out.append("a")
            i += 1
            continue
        out.append(VOWELS.get(ch) or OTHER.get(ch, ch))
        i += 1
    return "".join(out).translate(DIGITS)


if __name__ == "__main__":
    if sys.argv[1:2] == ["--file"]:
        for line in Path(sys.argv[2]).read_text().splitlines():
            print(iast(line))
    else:
        print(iast(" ".join(sys.argv[1:])))
