"""Tag the pronouns that may need capitals (He/His/Him/Himself, You/Your for God) in a lecture edition.

    pronoun_tags.py tag   EDITION.md TAGGED.md TAGS.json
    pronoun_tags.py apply EDITION.md CAPS.json OUT.md

Tags: every lowercase he/his/him/himself outside italics (h1, h2, ...), and every lowercase
you/your/yours/yourself outside italics in a paragraph that names God (y1, y2, ...). `apply`
capitalises the tagged words listed in CAPS.json ({"capitalise": [{"id": "h12", ...}, ...]}) and
checks that nothing but the case of those words changed.
"""

import json
import re
import sys
from pathlib import Path

HE = re.compile(r"\b(he|his|him|himself)\b")
YOU = re.compile(r"\b(you|your|yours|yourself)\b")
ITAL = re.compile(r"(?<!\*)\*(?!\*)[^*\n]+?\*(?!\*)")
GOD = re.compile(
    r"Bhagavān|Bhagavan|Kṛṣṇa|Krishna|Lord|God|Prabhu|Kapila|Viṣṇu|Hari\b|Nārāyaṇa|Ṭhākurjī|"
    r"Puruṣottama|Vāsudeva|Saṅkarṣaṇa|Pradyumna|Aniruddha|Rāma|Paramātmā|Īśvara|Brahman|Antaryāmī"
)


def spans(text):
    """(start, end, word, kind) of every taggable pronoun, in order."""
    italic = [(m.start(), m.end()) for m in ITAL.finditer(text)]

    def in_italic(i):
        return any(a <= i < b for a, b in italic)

    out = []
    for m in HE.finditer(text):
        if not in_italic(m.start()):
            out.append((m.start(), m.end(), m.group(1), "h"))
    pos = 0
    for para in re.split(r"(\n\s*\n)", text):
        if GOD.search(para):
            for m in YOU.finditer(para):
                i = pos + m.start()
                if not in_italic(i):
                    out.append((i, pos + m.end(), m.group(1), "y"))
        pos += len(para)
    out.sort()
    counters = {"h": 0, "y": 0}
    tagged = []
    for a, b, w, k in out:
        counters[k] += 1
        tagged.append({"id": f"{k}{counters[k]}", "start": a, "end": b, "word": w})
    return tagged


def main():
    mode = sys.argv[1]
    text = Path(sys.argv[2]).read_text(encoding="utf-8")
    tags = spans(text)
    if mode == "tag":
        parts, last = [], 0
        for t in tags:
            parts.append(text[last : t["end"]] + f"⟦{t['id']}⟧")
            last = t["end"]
        parts.append(text[last:])
        Path(sys.argv[3]).write_text("".join(parts), encoding="utf-8")
        Path(sys.argv[4]).write_text(
            json.dumps(tags, ensure_ascii=False), encoding="utf-8"
        )
        print(
            f"{sys.argv[2]}: {sum(t['id'][0] == 'h' for t in tags)} he-forms, {sum(t['id'][0] == 'y' for t in tags)} you-forms"
        )
    else:
        caps = {
            c["id"]
            for c in json.loads(Path(sys.argv[3]).read_text(encoding="utf-8"))[
                "capitalise"
            ]
        }
        known = {t["id"] for t in tags}
        unknown = caps - known
        if unknown:
            sys.exit(f"unknown ids: {sorted(unknown)[:10]}")
        chars = list(text)
        for t in tags:
            if t["id"] in caps:
                chars[t["start"]] = chars[t["start"]].upper()
        new = "".join(chars)
        assert new.lower() == text.lower() and len(new) == len(text)
        Path(sys.argv[4]).write_text(new, encoding="utf-8")
        print(f"{sys.argv[2]}: capitalised {len(caps)} of {len(tags)} tagged pronouns")


if __name__ == "__main__":
    main()
