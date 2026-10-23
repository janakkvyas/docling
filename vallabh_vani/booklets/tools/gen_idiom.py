#!/usr/bin/env python3
"""Write IDIOM.md: the speaker's idiom as an exemplar booklet prints it, with counts and examples.

    gen_idiom.py EXEMPLAR.md OUT.md

Counts whole words in the running text (bold quotations, verse lines, comments and the YAML block excluded).
The list of forms is curated below; the English-in-Devanagari table is found automatically.
"""

from __future__ import annotations

import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

FORMS = [
    (
        "Copula and tense",
        [
            ("हे", "है"),
            ("हें", "हैं"),
            ("हतो", "था"),
            ("हती", "थी"),
            ("हते", "थे"),
            ("होय", "हो"),
            ("होवे", "होता है / हो"),
            ("होवें", "होते हैं"),
            ("होयगो", "होगा"),
            ("होइगो", "होगा"),
            ("होयगी", "होगी"),
            ("जायगो", "जाएगा"),
            ("जाएगो", "जाएगा"),
            ("आयगो", "आएगा"),
            ("पड़ेगो", "पड़ेगा"),
            ("रहेगो", "रहेगा"),
            ("करेगो", "करेगा"),
            ("आवे", "आता है / आए"),
            ("जावे", "जाता है / जाए"),
            ("रहवे", "रहता है"),
            ("करवे", "करता है"),
            ("लगे", "लगता है"),
        ],
    ),
    (
        "Pronouns and their oblique forms",
        [
            ("मोकु", "मुझे / मुझको"),
            ("मोसु", "मुझसे"),
            ("मेरो", "मेरा"),
            ("तोकु", "तुझे"),
            ("तेरो", "तेरा"),
            ("तुमकु", "तुम्हें"),
            ("आपकु", "आपको"),
            ("अपन्", "हम"),
            ("अपन्ने", "हमने"),
            ("अपनेकु", "हमें"),
            ("अपनो", "हमारा"),
            ("अपने", "हमारे / अपने"),
            ("वाको", "उसका"),
            ("वाकी", "उसकी"),
            ("वाके", "उसके"),
            ("वाकु", "उसको"),
            ("वासु", "उससे"),
            ("वामें", "उसमें"),
            ("याको", "इसका"),
            ("याकी", "इसकी"),
            ("याके", "इसके / इसलिए"),
            ("याकु", "इसको"),
            ("यासु", "इससे"),
            ("यामें", "इसमें"),
            ("जाको", "जिसका"),
            ("जाकु", "जिसको"),
            ("जामें", "जिसमें"),
            ("उनने", "उन्होंने"),
            ("वाने", "उसने"),
            ("याने", "इसने"),
            ("वा", "वह / उस"),
            ("या", "यह / इस"),
            ("जा", "जो / जिस"),
        ],
    ),
    (
        "Verb forms",
        [
            ("कियो", "किया"),
            ("भयो", "हुआ"),
            ("भई", "हुई"),
            ("भये", "हुए"),
            ("गयो", "गया"),
            ("रह्यो", "रहा"),
            ("कह्यो", "कहा"),
            ("आयो", "आया"),
            ("लियो", "लिया"),
            ("दियो", "दिया"),
            ("बतायो", "बताया"),
            ("समझायो", "समझाया"),
            ("मान्यो", "माना"),
            ("लिख्यो", "लिखा"),
            ("सोच्यो", "सोचा"),
            ("पूछी", "पूछा"),
            ("कही", "कहा"),
            ("करनो", "करना"),
            ("समझनो", "समझना"),
            ("होनो", "होना"),
            ("करवेको", "करने का"),
            ("होवेके", "होने के"),
            ("करूँ", "करूँ / करता हूँ"),
        ],
    ),
    (
        "Postpositions and particles",
        [
            ("सु", "से"),
            ("कु", "को"),
            ("पे", "पर"),
            ("के", "कि (also genitive के)"),
            ("ना", "ना (tag: न?)"),
            ("बखत", "वक्त"),
            ("तरहसु", "तरह से"),
            ("सबसु", "सबसे"),
            ("खाली", "केवल"),
            ("नहीं", "नहीं"),
        ],
    ),
    (
        "Gujarati and Vraj words",
        [
            ("छेल्ले", "आखिर में (Guj.)"),
            ("आखु", "पूरा (Guj.)"),
            ("पण", "पर (Guj.)"),
            ("पाछो", "फिर से / पीछे"),
            ("लफड़ा", "झंझट"),
            ("ख्याल", "ध्यान / समझ"),
            ("मजेदार", "मज़ेदार"),
            ("भाई", "भाई (address)"),
            ("अरे", "अरे"),
            ("खुलासा", "स्पष्ट"),
        ],
    ),
]
DEVA = r"[ऀ-ॿ‌]"


def body_text(md: str) -> str:
    md = re.sub(r"^---\n.*?\n---\n", "", md, flags=re.S)
    md = re.sub(r"<!--.*?-->", " ", md, flags=re.S)
    md = re.sub(r"!\[[^\]]*\]\([^)]*\)(\{[^}]*\})?", " ", md)  # figures
    md = re.sub(r"\*\*.*?\*\*", " ", md, flags=re.S)
    md = re.sub(r"^\|.*$", " ", md, flags=re.M)
    md = re.sub(r"^(:::|#).*$", " ", md, flags=re.M)
    return md.replace("‌", "")


def main() -> None:
    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    text = body_text(unicodedata.normalize("NFC", src.read_text()))
    words = re.findall(DEVA + r"+|[A-Za-z']+", text)
    counts = Counter(words)
    lines = [
        "# The speaker's idiom as the booklet prints it",
        "",
        f"Counted in `{src.name}` (running text only: quotations in bold, verse lines, headings and comments "
        "excluded). Standard forms in the right-hand column are given for understanding only: the booklet "
        "never uses them in the speaker's own sentences (see `SPEC_HINDI_BOOKLET.md`).",
        "",
    ]
    for title, forms in FORMS:
        lines += [
            f"## {title}",
            "",
            "| Form | Standard Hindi | Count | Example |",
            "|---|---|---|---|",
        ]
        for form, std in forms:
            form = unicodedata.normalize("NFC", form)
            n = counts.get(form, 0)
            m = re.search(
                r"(?:\S+\s+){0,4}\S*(?<![\u0900-\u097F])"
                + re.escape(form)
                + r"(?![\u0900-\u097F])\S*(?:\s+\S+){0,4}",
                text,
            )
            ex = " ".join(m.group(0).split()) if m else ""
            lines.append(f"| {form} | {std} | {n} | {ex} |")
        lines.append("")
    std = {
        w: counts.get(w, 0)
        for w in ("है", "हैं", "था", "थी", "थे", "किया", "हुआ", "गया", "मुझे", "उसका")
    }
    lines += [
        "## Standard forms in the running text",
        "",
        "They occur only in other people's quoted words, a few headings and set phrases: "
        + ", ".join(f"{w} {n}" for w, n in std.items())
        + ".",
        "",
    ]
    lines += ["## Postpositions joined to the word", ""]
    for suf, std_ in (("सु", "से"), ("कु", "को"), ("को", "का"), ("में", "में"), ("पे", "पर")):
        joined = Counter(w for w in words if w.endswith(suf) and len(w) > len(suf) + 1)
        lines.append(
            f"- **-{suf}** ({std_}): {sum(joined.values())} words, e.g. "
            + ", ".join(f"{w} {n}" for w, n in joined.most_common(12))
        )
    lines.append("")
    eng = Counter(w for w in words if re.fullmatch(DEVA + r"+्", w) and len(w) > 2)
    lines += [
        "## English words written in Devanagari with a final virama (most frequent)",
        "",
        ", ".join(f"{w} {n}" for w, n in eng.most_common(80)),
        "",
    ]
    latin = re.findall(r"[A-Za-z][A-Za-z ,'?!.-]{12,}", text)
    lines += [
        "## English sentences kept in Latin letters",
        "",
        f"{len(latin)} runs, for example: "
        + "; ".join(f"“{l.strip()}”" for l in latin[:12]),
        "",
    ]
    out.write_text("\n".join(lines))
    print("wrote", out, "from", len(words), "words")


if __name__ == "__main__":
    main()
