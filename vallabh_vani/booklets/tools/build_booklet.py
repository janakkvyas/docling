#!/usr/bin/env python3
"""Build a Vallabh Vani booklet: pandoc markdown -> .docx (house template) -> .pdf.

    build_booklet.py SOURCE.md OUTDIR [--name BASENAME]

The YAML block says which kind: `booklet: hindi` (pravachan booklet, the default) or `booklet: english`
(translation book). Page markers (<!-- p.N -->) are removed. In a Hindi booklet the placeholders
{{अनुक्रमणिका}} and {{उद्धृत वचन}} are replaced by the contents (from the `# खण्ड …` headings) and the index
of quotations (every **"…"** followed by a source in brackets), whose page numbers are read from a first
PDF build. See vallabh_vani/booklets/SPEC.md for the conventions.
"""

from __future__ import annotations

import argparse
import html
import os
import re
import subprocess
import tempfile
import unicodedata
import zipfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
DEV = str.maketrans("0123456789", "०१२३४५६७८९")
QUOTE = re.compile(
    r'\*\*\s*["“](?P<q>[^"”*]+?)["”]?\s*\*\*\s*["”]?\s*\((?P<src>[^()]{2,60})\)'
)
QUOTE2 = re.compile(r'["“]\*\*(?P<q>[^"”*]+?)\*\*["”]\s*\((?P<src>[^()]{2,60})\)')


def meta_of(md: str) -> dict[str, str]:
    m = re.match(r"---\n(.*?)\n---\n", md, re.S)
    out = {}
    if m:
        for line in m.group(1).splitlines():
            k, _, v = line.partition(":")
            if v.strip():
                out[k.strip()] = v.strip().strip('"')
    return out


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, **kw)


def xml(s: str) -> str:
    return html.escape(s, quote=False)


def contents_xml(md: str, title: str, pages: dict[str, int] | None) -> str:
    heads = re.findall(r"^# (.+?)\s*(?:\{[^}]*\})?\s*$", md, re.M)
    paras = [
        f'<w:p><w:pPr><w:pStyle w:val="ContentsHeading"/></w:pPr><w:r><w:t xml:space="preserve">'
        f"{xml('अनुक्रमणिका — ' + title)}</w:t></w:r></w:p>"
    ]
    for h in heads:
        lead, sep, rest = h.partition(" — ")
        page = ""
        if pages is not None:
            page = f"<w:r><w:tab/></w:r><w:r><w:t>{str(pages.get(h, 0)).translate(DEV) if pages.get(h) else '००'}</w:t></w:r>"
        paras.append(
            '<w:p><w:pPr><w:pStyle w:val="ContentsItem"/></w:pPr>'
            "<w:r><w:t>•</w:t></w:r><w:r><w:tab/></w:r>"
            f'<w:r><w:rPr><w:b/><w:bCs/></w:rPr><w:t xml:space="preserve">{xml(lead)}</w:t></w:r>'
            f'<w:r><w:t xml:space="preserve">{xml(sep + rest)}</w:t></w:r>{page}</w:p>'
        )
    return "\n```{=openxml}\n" + "\n".join(paras) + "\n```\n"


def quotations(md: str) -> list[tuple[str, str]]:
    body = md.split("{{उद्धृत वचन}}")[0]
    found = []
    for rx in (QUOTE, QUOTE2):
        for m in rx.finditer(body):
            found.append((m.start(), m.group("q").strip(), m.group("src").strip()))
    found.sort()
    return [(q, s) for _, q, s in found]


def opening(q: str, words: int = 5) -> str:
    return " ".join(q.split()[:words])


def index_xml(entries, pages: list[int] | None) -> str:
    paras = [
        '<w:p><w:pPr><w:pStyle w:val="IndexHeading"/></w:pPr><w:r><w:t>उद्धृत वचन</w:t></w:r></w:p>'
    ]
    for i, (q, src) in enumerate(entries, 1):
        pg = str(pages[i - 1]).translate(DEV) if pages and pages[i - 1] else "००"
        close = (
            "" if len(q.split()) > 5 else '"'
        )  # a quotation cut to its opening words keeps only the opening mark
        paras.append(
            '<w:p><w:pPr><w:pStyle w:val="IndexItem"/></w:pPr>'
            f'<w:r><w:t xml:space="preserve">{str(i).translate(DEV)}.</w:t></w:r><w:r><w:tab/></w:r>'
            f'<w:r><w:rPr><w:b/><w:bCs/></w:rPr><w:t xml:space="preserve">"{xml(opening(q))}{close}</w:t></w:r>'
            f'<w:r><w:t xml:space="preserve"> ({xml(src)})</w:t></w:r><w:r><w:tab/></w:r>'
            f'<w:r><w:t xml:space="preserve">- {pg}</w:t></w:r></w:p>'
        )
    return "\n```{=openxml}\n" + "\n".join(paras) + "\n```\n"


def runs_xml(s: str) -> str:
    """Inline markdown (only **bold**) to WordprocessingML runs."""
    out = []
    for i, part in enumerate(re.split(r"\*\*", s)):
        if part:
            rpr = "<w:rPr><w:b/><w:bCs/></w:rPr>" if i % 2 else ""
            out.append(f'<w:r>{rpr}<w:t xml:space="preserve">{xml(part)}</w:t></w:r>')
    return "".join(out)


def printed_lists(md: str) -> str:
    """`::: contents` / `::: index` divs (a contents or index typed as printed) -> styled paragraphs."""

    def contents(m):
        lines = [l.strip() for l in m.group(1).strip().splitlines() if l.strip()]
        if any(
            l.count("|") >= 3 for l in lines[1:]
        ):  # English book: N | Devanagari | IAST | page
            paras = [
                f'<w:p><w:pPr><w:pStyle w:val="ContentsHeading"/></w:pPr>{runs_xml(lines[0])}</w:p>'
            ]
            for l in lines[1:]:
                cells = [c.strip() for c in l.strip("|").split("|")]
                if len(cells) < 4 or set(l) <= set("|-: "):
                    continue
                num, deva, iast_, page = cells[:4]
                if not re.match(
                    r"^[0-9०-९]", num
                ):  # the column heads (S. No. | Subject | | P.No.)
                    small = '<w:rPr><w:sz w:val="20"/><w:szCs w:val="20"/></w:rPr>'
                    paras.append(
                        f'<w:p><w:pPr><w:pStyle w:val="ContentsItem"/></w:pPr><w:r>{small}<w:t>{xml(num)}</w:t></w:r>'
                        f"<w:r><w:tab/></w:r><w:r>{small}<w:t>{xml(deva)}</w:t></w:r><w:r><w:tab/></w:r>"
                        f"<w:r>{small}<w:t>{xml(page)}</w:t></w:r></w:p>"
                    )
                    continue
                paras.append(
                    f'<w:p><w:pPr><w:pStyle w:val="ContentsItem"/></w:pPr><w:r><w:t>{xml(num)}</w:t></w:r>'
                    f"<w:r><w:tab/></w:r>{runs_xml(deva)}<w:r><w:tab/></w:r><w:r><w:t>{xml(page)}</w:t></w:r></w:p>"
                )
                if iast_:
                    paras.append(
                        f'<w:p><w:pPr><w:pStyle w:val="ContentsIAST"/></w:pPr>{runs_xml(iast_)}</w:p>'
                    )
            return "\n```{=openxml}\n" + "\n".join(paras) + "\n```\n"
        paras = [
            f'<w:p><w:pPr><w:pStyle w:val="ContentsHeading"/></w:pPr>{runs_xml(lines[0])}</w:p>'
        ]
        for l in lines[1:]:
            item = re.sub(r"^[-*+]\s+", "", l)
            paras.append(
                '<w:p><w:pPr><w:pStyle w:val="ContentsItem"/></w:pPr><w:r><w:t>•</w:t></w:r>'
                f"<w:r><w:tab/></w:r>{runs_xml(item)}</w:p>"
            )
        return "\n```{=openxml}\n" + "\n".join(paras) + "\n```\n"

    def index(m):
        raw = [l.strip() for l in m.group(1).strip().splitlines() if l.strip()]
        items: list[str] = []
        for l in raw[
            1:
        ]:  # an item whose source or text runs onto the next line is joined to it
            if re.match(r"^(\*\*)?[०-९0-9]+\.", l) or not items:
                items.append(l)
            else:
                items[-1] += " " + l
        paras = [
            f'<w:p><w:pPr><w:pStyle w:val="IndexHeading"/></w:pPr>{runs_xml(raw[0])}</w:p>'
        ]
        for it in items:
            it = it.replace("** **", " ")
            whole = it.startswith("**") and it.endswith("**") and it.count("**") == 2
            s = it[2:-2] if whole else it
            num, _, rest = s.partition(" ")
            body, dash, page = rest.rpartition(" -")
            if not dash:
                body, page = rest, ""
            body, page = body.strip(), page.replace("*", "").strip()
            if whole:
                body = f"**{body}**"
            page_run = (
                f'<w:r><w:tab/></w:r><w:r><w:t xml:space="preserve">- {xml(page)}</w:t></w:r>'
                if dash
                else ""
            )
            paras.append(
                f'<w:p><w:pPr><w:pStyle w:val="IndexItem"/></w:pPr><w:r><w:t>{xml(num.strip("*"))}</w:t></w:r>'
                f"<w:r><w:tab/></w:r>{runs_xml(body)}{page_run}</w:p>"
            )
        return "\n```{=openxml}\n" + "\n".join(paras) + "\n```\n"

    md = re.sub(r"^::: contents\n(.*?)^:::\s*$", contents, md, flags=re.M | re.S)
    return re.sub(r"^::: index\n(.*?)^:::\s*$", index, md, flags=re.M | re.S)


def norm(s: str) -> str:
    s = unicodedata.normalize("NFC", s)
    s = re.sub(r"[\s‌‍\"'“”‘’.,;:!?()\[\]॥।|\-—*]", "", s)
    return s


def find_pages(pdf: Path, keys: list[str], start_after: str | None = None) -> list[int]:
    n = int(
        re.search(
            r"Pages:\s+(\d+)",
            run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout,
        ).group(1)
    )
    texts = [
        norm(
            run(
                ["pdftotext", "-f", str(i), "-l", str(i), str(pdf), "-"],
                capture_output=True,
                text=True,
            ).stdout
        )
        for i in range(1, n + 1)
    ]
    out, page, pos = [], 0, 0
    for k in keys:
        key = norm(k)[:14]
        hit = 0
        # search forward from the last hit, so repeated quotations get their own pages
        for p in range(page, n):
            j = texts[p].find(key, pos if p == page else 0)
            if j >= 0:
                hit, page, pos = p + 1, p, j + 1
                break
        out.append(hit)
    return out


def build_once(src_md: str, out_docx: Path, ref: Path, workdir: Path) -> Path:
    md_file = out_docx.with_suffix(".build.md")
    md_file.write_text(src_md)
    run(
        [
            "pandoc",
            str(md_file),
            "-f",
            "markdown+smart",
            "-t",
            "docx",
            f"--reference-doc={ref}",
            f"--lua-filter={TOOLS / 'booklet.lua'}",
            f"--resource-path={workdir}",
            "-o",
            str(out_docx),
        ]
    )
    renumber_docpr(out_docx)
    fc = out_docx.parent / "fonts.conf"
    fc.write_text("""<?xml version="1.0"?><!DOCTYPE fontconfig SYSTEM "fonts.dtd"><fontconfig>
<include ignore_missing="yes">/etc/fonts/fonts.conf</include>
<alias><family>Sanskrit Text</family><prefer><family>Noto Serif</family><family>Noto Serif Devanagari</family></prefer></alias>
<alias><family>Calibri</family><prefer><family>Carlito</family></prefer></alias>
<alias><family>Tahoma</family><prefer><family>DejaVu Sans</family></prefer></alias>
</fontconfig>""")
    env = dict(os.environ, FONTCONFIG_FILE=str(fc))
    run(
        [
            "soffice",
            "--headless",
            f"-env:UserInstallation=file:///tmp/lo_booklet_{out_docx.stem}",
            "--convert-to",
            "pdf",
            "--outdir",
            str(out_docx.parent),
            str(out_docx),
        ],
        capture_output=True,
        env=env,
    )
    md_file.unlink()
    return out_docx.with_suffix(".pdf")


def renumber_docpr(docx: Path) -> None:
    tmp = docx.with_suffix(".tmp")
    with (
        zipfile.ZipFile(docx) as zin,
        zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout,
    ):
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "word/document.xml":
                counter = iter(range(1, 100000))
                data = re.sub(
                    rb'(<wp:docPr\b[^>]*?\bid=")\d+(")',
                    lambda m: m.group(1) + str(next(counter)).encode() + m.group(2),
                    data,
                )
            zout.writestr(item, data)
    tmp.replace(docx)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("outdir")
    ap.add_argument("--name")
    a = ap.parse_args()
    src = Path(a.source).resolve()
    out = Path(a.outdir).resolve()
    out.mkdir(parents=True, exist_ok=True)
    md = src.read_text()
    meta = meta_of(md)
    kind = meta.get("booklet", "hindi")
    name = a.name or src.stem
    md = re.sub(
        r"^[ \t]*<!--\s*p\.[^>]*-->[ \t]*\n", "", md, flags=re.M
    )  # page markers
    with tempfile.TemporaryDirectory() as tmpd:
        ref = Path(tmpd) / f"ref_{kind}.docx"
        run(
            ["python3", "-I", str(TOOLS / "make_ref_booklet.py"), kind, str(ref)],
            capture_output=True,
        )
        docx = out / f"{name}.docx"
        with_pages = meta.get("contents-pages", "false").lower() == "true"
        entries = quotations(md) if "{{उद्धृत वचन}}" in md else []
        heads = re.findall(r"^# (.+?)\s*(?:\{[^}]*\})?\s*$", md, re.M)

        def render(cpages, ipages):
            text = printed_lists(md)
            if "{{अनुक्रमणिका}}" in text:
                text = text.replace(
                    "{{अनुक्रमणिका}}", contents_xml(md, meta.get("title", ""), cpages)
                )
            if "{{उद्धृत वचन}}" in text:
                text = text.replace("{{उद्धृत वचन}}", index_xml(entries, ipages))
            return text

        pdf = build_once(
            render({} if with_pages else None, None), docx, ref, src.parent
        )
        if entries or with_pages:
            ipages = find_pages(pdf, [q for q, _ in entries]) if entries else None
            cpages = dict(zip(heads, find_pages(pdf, heads))) if with_pages else None
            pdf = build_once(render(cpages, ipages), docx, ref, src.parent)
            if entries:
                check = find_pages(pdf, [q for q, _ in entries])
                if check != ipages:
                    print("warning: index pages moved on the second pass; build again")
                missing = [q for (q, _), p in zip(entries, ipages) if not p]
                if missing:
                    print("warning: quotations not found in the PDF:", missing)
        info = run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
        npages = re.search(r"Pages:\s+(\d+)", info).group(1)
        print(
            f"{name}: {npages} pages, {len(heads)} sections, {len(entries)} indexed quotations -> {docx} and {pdf}"
        )


if __name__ == "__main__":
    main()
