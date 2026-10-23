#!/usr/bin/env python3
"""Make the markdown of an English discourse booklet from a lecture edition.

    lecture_to_booklet.py EDITION.md OUT.md --series-deva श्रीकपिलगीता --series-iast Śrīkapilagītā

The edition is the pandoc markdown of the lecture series (vallabh_vani/kapil_gita/SPEC.md): a YAML title and
subtitle, an italic note, numbered sections with their timestamps, dialogue labels, verse blocks, Sanskrit in
italics, editorial flags and a closing Brief Summary. The booklet follows
vallabh_vani/booklets/SPEC_ENGLISH_DISCOURSE_BOOKLET.md: a title page, a note on the text, the contents, a
synopsis, the sections and an index of quotations. The speaker's words are kept as they are; the flags become
Word comments in the margin; Sanskrit quotations are set in bold within quotation marks with their source;
IAST and sources take the house forms. Build the result with build_booklet.py.
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from iast import iast

DEVA = re.compile(r"[\u0900-\u097F]")
ITALIC = re.compile(r"(?<!\*)\*(?!\*)([^*\n]+?)\*(?!\*)")
LABEL = re.compile(r"^\*\*([^*]{1,40}?):\*\*\s*")
TIMESTAMP = re.compile(r"^\*\[(\d\d:\d\d:\d\d)\]\*\s*$")
SOURCE = r"\((?:cf\. )?[A-ZĀĪŪṚṜḶŚṢṬḌṆṄÑ][^()]*?\d[^()]*\)"
QUOTE = re.compile(
    r"(?<!\*)\*(?!\*)(?P<q>[^*\n]+?)\*(?!\*)(?P<unc>‹\?›)?"
    r"(?:(?P<sp>\s*)(?P<src>" + SOURCE + r")|\s*(?P<heard>‹श्रवणाधारित›))"
)
AS_HEARD = "Given as heard: not yet checked against a printed edition."
MESSAGES = {
    "?": "Uncertain reading: given as transcribed from the recording{ts}.",
    "…": "Inaudible or unrecoverable in the recording{ts}.",
    "conj": "Conjectural restoration of a garbled passage of the recording{ts}.",
    "heard": AS_HEARD,
    "char": "Kept as spoken: the speaker's characterisation.",
}
WORKS = [  # house forms of the English citations (SPEC_ENGLISH_STUTI_BOOK.md, Citations)
    (r"Śrīmad Bhāgavata(?=\s+\d)", "Bhāgavata Purāṇa"),
    (r"Bhagavad[- ]?[Gg]ītā", "Bhagavadgītā"),
    (r"(?<=\()Gītā(?=\s+\d)", "Bhagavadgītā"),
    (r"Kaṭhopaniṣad", "Kaṭha Upaniṣad"),
    (r"Īśā Upaniṣad", "Īśa Upaniṣad"),
    (r"Brahmasūtra-bhāṣya", "Brahmasūtrabhāṣya"),
]


class Ctx:
    def __init__(self) -> None:
        self.comment = 0
        self.quote = 0
        self.timestamp = ""
        self.index: list[tuple[str, str, str]] = []  # bookmark, quotation, source
        self.iast_mismatch: list[tuple[str, str, str]] = []
        self.flags = {"?": 0, "…": 0, "conj": 0, "heard": 0, "char": 0}

    def note(self, kind: str, anchor: str) -> str:
        """A Word comment (pandoc comment span) on `anchor`."""
        self.comment += 1
        self.flags[kind] += 1
        ts = (
            f" (section from {self.timestamp})"
            if self.timestamp and kind in ("?", "…", "conj")
            else ""
        )
        text = MESSAGES[kind].format(ts=ts)
        i = self.comment
        return f'[{text}]{{.comment-start id="{i}" author="Editor"}}{anchor}[]{{.comment-end id="{i}"}}'

    def bookmark(self) -> str:
        self.quote += 1
        return f"q{self.quote:03d}"


def anusvara(s: str) -> str:
    return s.replace("ṁ", "ṃ").replace("Ṁ", "Ṃ")


def sources(s: str) -> str:
    def fix(m):
        inner = m.group(0)
        for rx, rep in WORKS:
            inner = re.sub(rx, rep, inner)
        return inner

    return re.sub(r"\([^()]*\)", fix, s)


def avagraha(s: str) -> str:
    """Sanskrit in the running text: the avagraha as ’ joined to the word before (the house form)."""
    return re.sub(r"\s+'(?=\w)", "’", s).replace("'", "’")


def sanskrit(s: str) -> str:
    """IAST of a quotation or verse line in the house form: ṃ, ’ for avagraha, no hyphens, daṇḍas."""
    s = anusvara(s)
    s = re.sub(r"\s+'", "’", s).replace("'", "’")
    s = re.sub(r"(?<=[\w›])-(?=\w)", "", s)
    return s.replace("||", "॥").replace("|", "।")


def flags(s: str, ctx: Ctx) -> str:
    """Editorial flags -> Word comments."""
    s = re.sub(
        r"\s*‹the speaker's characteri[sz]ation›", lambda m: ctx.note("char", ""), s
    )
    s = re.sub(r"\s*‹श्रवणाधारित›", lambda m: ctx.note("heard", ""), s)
    s = re.sub(r"‹…›", lambda m: ctx.note("…", "…"), s)
    s = re.sub(r"([^\s‹›\[\](){}*\"“”]*)‹\?›", lambda m: ctx.note("?", m.group(1)), s)
    return re.sub(r"‹([^›]+)›", lambda m: ctx.note("conj", m.group(1)), s)


def plain(s: str) -> str:
    """A quotation without its flags (a conjectural restoration keeps its text)."""
    s = re.sub(r"‹(?:\?|…|श्रवणाधारित)›", "", s)
    return re.sub(r"‹([^›]*)›", r"\1", s)


def quote(m: re.Match, ctx: Ctx) -> str:
    q = sanskrit(m.group("q").strip())
    body = f'**"{q}"**'
    if m.group("unc"):
        body = ctx.note("?", body)
    if m.group("heard"):
        return ctx.note("heard", body)
    src = sources(anusvara(m.group("src")))
    bm = ctx.bookmark()
    ctx.index.append((bm, plain(q), src[1:-1]))
    return f"[]{{#{bm}}}{body} {src}"


def prose(s: str, ctx: Ctx) -> str:
    s = QUOTE.sub(lambda m: quote(m, ctx), s)
    s = ITALIC.sub(lambda m: avagraha(m.group(1)), s)
    s = flags(s, ctx)
    return sources(anusvara(s))


def verse_block(block: str, ctx: Ctx) -> list[str]:
    lines = [re.sub(r"^>\s?", "", line).rstrip() for line in block.splitlines()]
    groups, cur = [], []
    for line in lines:
        if line.strip():
            cur.append(line.strip())
        elif cur:
            groups.append(cur)
            cur = []
    if cur:
        groups.append(cur)
    out: list[str] = []
    deva: list[str] | None = None
    for g in groups:
        if all(DEVA.search(x) and not x.startswith("*") for x in g):
            deva = g
            continue
        if all(x.startswith("*") for x in g):
            last = g[-1]
            m = re.search(r"\s*(\([^()]*\))\s*$", last)
            src = m.group(1) if m else ""
            if m:
                g = [*g[:-1], last[: m.start()]]
            ia = [sanskrit(x.strip().strip("*").strip()) for x in g]
            heard = "‹श्रवणाधारित›" in src
            src = re.sub(r";?\s*‹श्रवणाधारित›", "", src)
            src = sources(anusvara(src)) if src else ""
            bm = ""
            if src:
                bm = ctx.bookmark()
                first = re.sub(r"[।॥\d]", "", plain(ia[0])).strip()
                ctx.index.append((bm, first, src[1:-1]))
            if deva:
                for d, i_line in zip(
                    deva, ia
                ):  # check the IAST against the Devanagari, letter for letter
                    a = re.sub(r"[^a-zāīūṛṝḷṃḥṅñṭḍṇśṣ’]", "", iast(d).lower()).replace(
                        "’", ""
                    )
                    b = re.sub(r"[^a-zāīūṛṝḷṃḥṅñṭḍṇśṣ’]", "", i_line.lower()).replace(
                        "’", ""
                    )
                    if a != b:
                        ctx.iast_mismatch.append((ctx.timestamp, d, i_line))
                out.append(
                    "::: verse\n"
                    + "\n".join(
                        f"| {'[]{#' + bm + '}' if k == 0 and bm else ''}{flags(d, ctx)}"
                        for k, d in enumerate(deva)
                    )
                    + "\n:::"
                )
            iast_lines = [
                f"| {'[]{#' + bm + '}' if k == 0 and bm and not deva else ''}{flags(x, ctx)}"
                for k, x in enumerate(ia)
            ]
            if src:
                iast_lines.append("| " + (ctx.note("heard", src) if heard else src))
            elif heard:
                iast_lines[-1] += ctx.note("heard", "")
            out.append("::: verse-iast\n" + "\n".join(iast_lines) + "\n:::")
            deva = None
            continue
        out.append(
            prose(" ".join(g), ctx)
        )  # the gloss, in square brackets as in the edition
    return out


def split_sections(body: str):
    parts = re.split(r"^# (.+)$", body, flags=re.M)
    return [(parts[i].strip(), parts[i + 1]) for i in range(1, len(parts), 2)]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("edition")
    ap.add_argument("out")
    ap.add_argument("--series-deva", required=True)
    ap.add_argument("--series-iast", required=True)
    ap.add_argument("--author-deva", default="गोस्वामी श्याम मनोहर")
    ap.add_argument("--author-iast", default="Goswāmy Śyāma Manohara")
    a = ap.parse_args()
    text = unicodedata.normalize("NFC", Path(a.edition).read_text(encoding="utf-8"))
    ym = re.match(r"---\n(.*?)\n---\n", text, re.S)
    yaml = dict(re.findall(r'^(\w+): "(.*)"$', ym.group(1), re.M))
    rest = text[ym.end() :].strip()
    note_raw, _, body = rest.partition("\n\n")
    assert note_raw.startswith("*Reading edition"), note_raw[:60]
    ctx = Ctx()

    # title page
    lec, _, themes = yaml["subtitle"].partition(" — ")
    themes = prose(themes, ctx)
    date = re.search(r"recording of (\d{1,2} \w+ \d{4})", note_raw).group(1)

    # note on the text
    note = note_raw.strip().strip("*")
    note = re.sub(r"\s*Editorial flags:.*$", "", note, flags=re.S)
    note = note.replace(
        "editing is limited to punctuation, paragraphing",
        "editing is limited to punctuation, capitalisation, spelling, paragraphing",
    )
    note = prose(note, ctx) + (
        " Comments in the margin mark what is still to be settled before printing: uncertain readings,"
        " conjectural restorations, inaudible passages, and quotations given as heard and not yet checked"
        " against a printed edition. A comment on the recording gives the time at which its section begins."
    )

    sections = split_sections(body)
    summary = dict(sections).get("Brief Summary", "")
    sections = [(h, b) for h, b in sections if h != "Brief Summary"]
    syn = re.findall(
        r"\*\*(Content|Examples and Stories)\.\*\*\s*(.+?)(?=\n\n\*\*|\Z)",
        summary,
        re.S,
    )
    syn = dict(syn)

    out = [
        "---",
        "booklet: english",
        f'title: "{a.series_iast} — {lec}"',
        "---",
        "",
        "::: title",
        f"॥ {a.series_deva} ॥",
        "",
        f"॥ {a.series_iast} ॥",
        ":::",
        "",
        "::: book-subtitle",
        lec,
        ":::",
        "",
        "::: title-note",
        themes,
        "",
        date,
        ":::",
        "",
        "::: lecture-author",
        a.author_deva,
        "",
        a.author_iast,
        ":::",
        "",
        "{{end title page}}",
        "",
        "::: front-heading",
        "Note on the text",
        ":::",
        "",
        note,
        "",
        "* * *",
        "",
        "TOC_PLACEHOLDER",
        "",
        "{{end front matter}}",
        "",
        "# Synopsis {#synopsis}",
        "",
    ]
    if syn.get("Content"):
        out += [prose(syn["Content"].strip(), ctx), ""]
    if syn.get("Examples and Stories"):
        out += [
            "::: label-left",
            "Examples and stories:",
            ":::",
            "",
            prose(syn["Examples and Stories"].strip(), ctx),
            "",
        ]
    out += ["* * *", ""]

    toc = [
        "::: toc",
        "Contents",
        "",
        "S. No. | Subject | P.No.",
        " | Synopsis | synopsis",
    ]
    voice = "Speaker"  # the booklet is the speaker's: his label is shown only when he answers someone
    for n, (head, sec) in enumerate(sections, 1):
        hm = re.match(r"(\d+)\.\s+(.*)", head)
        num, title = hm.group(1), hm.group(2)
        sid = f"s{int(num):02d}"
        ctx.timestamp = ""
        blocks = [b for b in re.split(r"\n\s*\n", sec.strip()) if b.strip()]
        if blocks and TIMESTAMP.match(blocks[0].strip()):
            ctx.timestamp = TIMESTAMP.match(blocks.pop(0).strip()).group(1)
        title_md = prose(title, ctx)
        toc_title = re.sub(r"\[[^\]]*\]\{[^}]*\}", "", title_md)  # without the comments
        toc.append(f"{num} | {toc_title} | {sid}")
        out += [f"# {num}. {title_md} {{#{sid}}}", ""]
        for b in blocks:
            b = b.strip()
            if b.startswith(">"):
                out += [x + "\n" for x in verse_block(b, ctx)]
                continue
            label = ""
            lm = LABEL.match(b)
            if lm:
                who = lm.group(1)
                b = b[lm.end() :]
                if not (who == "Speaker" and voice == "Speaker"):
                    label = f"{who}: "
                voice = who
            out += [label + prose(b, ctx), ""]
    if ctx.index:
        toc.append(" | Quotations | quotations")
    toc.append(":::")
    if ctx.index:
        out += ["* * *", "", "::: quotations", "Quotations"]
        out += [f"{bm} | {q} | {src}" for bm, q, src in ctx.index]
        out += [":::", ""]
    md = "\n".join(out).replace("TOC_PLACEHOLDER", "\n".join(toc))
    md = re.sub(r"\n{3,}", "\n\n", md)
    Path(a.out).write_text(md, encoding="utf-8")
    left = re.findall(r"‹[^›]*›", md)
    print(
        f"{Path(a.edition).name}: {len(sections)} sections, {ctx.comment} comments {ctx.flags}, "
        f"{len(ctx.index)} indexed quotations, {len(ctx.iast_mismatch)} IAST/Devanagari differences, "
        f"{len(left)} flags left"
    )
    for ts, d, i_line in ctx.iast_mismatch:
        print(f"  IAST? [{ts}] {d}  |  {i_line}")


if __name__ == "__main__":
    main()
