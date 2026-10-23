#!/usr/bin/env python3
"""Series-wide spelling consistency for build/sp*.md and build/make_figs*.py.

Everywhere:   Mahāprabhujī -> Mahāprabhuji (house form);  Bhagavad Gītā -> Bhagavadgītā.
English prose (not inside italic Sanskrit, not in verse lines, not in image paths):
   brahman -> Brahman, bhagavān -> Bhagavān, paramātman/paramātmā -> Paramātmā, śuddhādvaita -> Śuddhādvaita.
An italic span holding only one of those words is normalised too.
"""
import re, sys
from pathlib import Path
EVERYWHERE = [(r"Mahāprabhujī", "Mahāprabhuji"), (r"Bhagavad Gītā", "Bhagavadgītā")]
PROSE = [(r"\bbrahman\b", "Brahman"), (r"\bbhagavān\b", "Bhagavān"),
         (r"\b[pP]aramātman\b", "Paramātmā"), (r"\bparamātmā\b", "Paramātmā"), (r"\bśuddhādvaita\b", "Śuddhādvaita")]
ITAL = re.compile(r"(?<!\*)\*(?!\*)([^*\n]+?)(?<!\*)\*(?!\*)")
def sub_all(s, rules):
    n = 0
    for pat, rep in rules:
        s, k = re.subn(pat, rep, s); n += k
    return s, n
def prose_line(line):
    if re.match(r"^> ", line) and (line.startswith("> *") or re.search(r"[ऀ-ॿ]", line)):
        return line, 0                       # verse line (Devanagari or IAST)
    head, sep, tail = line.partition("](")   # keep image/link targets untouched
    out, n, pos = [], 0, 0
    for m in ITAL.finditer(head):
        seg, k = sub_all(head[pos:m.start()], PROSE); out.append(seg); n += k
        inner = m.group(1)
        if re.fullmatch(r"(brahman|bhagavān|paramātman|paramātmā|śuddhādvaita)('s)?", inner):
            inner, k = sub_all(inner, PROSE); n += k
        out.append("*" + inner + "*"); pos = m.end()
    seg, k = sub_all(head[pos:], PROSE); out.append(seg); n += k
    return "".join(out) + sep + tail, n
changed_figs = []
for md in sorted(Path("build").glob("sp[0-9][0-9]*.md")):
    text, n1 = sub_all(md.read_text(), EVERYWHERE)
    lines, n2 = [], 0
    for line in text.split("\n"):
        line, k = prose_line(line); lines.append(line); n2 += k
    new = "\n".join(lines)
    if n1 + n2: md.write_text(new)
    print(f"{md.name}: {n1} everywhere-fixes, {n2} prose-fixes")
for py in sorted(Path("build").glob("make_figs*.py")):
    text, n1 = sub_all(py.read_text(), EVERYWHERE)
    text, n2 = sub_all(text, PROSE)
    if n1 + n2:
        py.write_text(text); changed_figs.append(py.name); print(f"{py.name}: {n1 + n2} fixes")
Path("tools/qa/changed_figs.txt").write_text("\n".join(changed_figs) + "\n")
