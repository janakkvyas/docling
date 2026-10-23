#!/usr/bin/env python3
"""Check that an English discourse booklet (.docx) holds every word of its lecture edition, and a comment
for every editorial flag.

    check_booklet_text.py EDITION.md BOOKLET.docx

The edition's sections (headings and text, without timestamps) are compared word for word with the booklet's
text from the first section heading to the index of quotations. Only the changes the booklet makes by rule
are allowed for: dialogue labels, the flags (which become comments), italics and bold, IAST forms (ṃ, ’,
daṇḍas, hyphens inside Sanskrit), quotation marks and the English forms of the sources. The flags of the note
and of the summary's apparatus paragraph (not printed) are not counted. Exit status 1 on any difference.
"""

from __future__ import annotations

import difflib
import re
import sys
import unicodedata
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lecture_to_booklet import WORKS

LABELS = r"(?:Speaker|A student|Another student|Listener \d+)"  # completed from the edition in main()
FLAG = re.compile(r"‹[^›]*›")


def normalise(s: str) -> list[str]:
    s = unicodedata.normalize("NFC", s).replace("ṁ", "ṃ").replace("Ṁ", "Ṃ")
    s = re.sub(r"‹(?:\?|श्रवणाधारित|the speaker's characteri[sz]ation)›", "", s)
    s = s.replace("‹…›", "…")
    s = re.sub(r"‹([^›]*)›", r"\1", s)
    s = re.sub(
        r"(?m)^\s*(?:>\s?)?(?:\*\*)?" + LABELS + r":(?:\*\*)?\s", " ", s
    )  # dialogue labels
    s = s.replace("*", "")
    s = re.sub(r"(?<=[\w\u0900-\u097F])-(?=[\w\u0900-\u097F])", "", s)
    s = re.sub("[‘’']", "’", s).replace("||", "॥").replace("|", "।")
    s = re.sub(r"\s+’(?=\w)", "’", s)
    return [w.lower() for w in re.findall(r"[\w\u0900-\u097F’]+", s)]


def sources(s: str) -> str:
    def fix(m):
        inner = m.group(0)
        for rx, rep in WORKS:
            inner = re.sub(rx, rep, inner)
        return inner

    return re.sub(r"\([^()]*\)", fix, s)


def edition_text(md: str) -> tuple[str, int]:
    body = md.split("# Brief Summary")[0]
    body = body[body.index("\n# 1.") :]
    body = re.sub(r"(?m)^\*\[\d\d:\d\d:\d\d\]\*\s*$", "", body)  # timestamps
    body = re.sub(r"(?m)^#\s+", "", body)
    summary = md.split("# Brief Summary", 1)[1]
    printed = re.findall(
        r"\*\*(?:Content|Examples and Stories)\.\*\*(.*?)(?=\n\n\*\*|\Z)", summary, re.S
    )
    flags = len(FLAG.findall(body)) + sum(len(FLAG.findall(p)) for p in printed)
    return sources(body), flags


def booklet_text(docx: Path) -> tuple[str, int]:
    from docx import Document

    paras = [p.text for p in Document(str(docx)).paragraphs]
    start = next(i for i, p in enumerate(paras) if re.match(r"1\.\s", p))
    end = max(
        (i for i, p in enumerate(paras) if p.strip() == "Quotations"),
        default=len(paras),
    )
    comments = 0
    with zipfile.ZipFile(docx) as z:
        if "word/comments.xml" in z.namelist():
            comments = z.read("word/comments.xml").count(b"<w:comment ")
    return "\n".join(paras[start:end]), comments


def main() -> int:
    global LABELS
    md = Path(sys.argv[1]).read_text(encoding="utf-8")
    names = set(re.findall(r"(?m)^\*\*([^*]{1,40}?):\*\*", md))
    LABELS = (
        "(?:"
        + "|".join(re.escape(n) for n in sorted(names, key=len, reverse=True))
        + ")"
    )
    ed, flags = edition_text(md)
    bk, comments = booklet_text(Path(sys.argv[2]))
    a, b = normalise(ed), normalise(bk)
    ops = [
        op
        for op in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes()
        if op[0] != "equal"
    ]
    name = Path(sys.argv[2]).name
    print(
        f"{name}: {len(a)} words in the edition, {len(b)} in the booklet, {len(ops)} differences; "
        f"{flags} flags, {comments} comments"
    )
    for tag, i1, i2, j1, j2 in ops[:20]:
        print(
            f"  {tag}: edition «{' '.join(a[max(0, i1 - 3) : i2 + 3])}» / booklet «{' '.join(b[max(0, j1 - 3) : j2 + 3])}»"
        )
    return 1 if ops or flags > comments else 0


if __name__ == "__main__":
    sys.exit(main())
