#!/usr/bin/env python3
"""Build a Vallabh Vani booklet: pandoc markdown -> .docx (house template).

    build_booklet.py SOURCE.md OUTDIR [--name BASENAME]

Writes OUTDIR/BASENAME.docx, the deliverable (the owner receives Word files only), and a PDF for checking in
OUTDIR/check/. The YAML block says which kind: `booklet: hindi` (pravachan booklet, the default) or
`booklet: english` (translation book, or English discourse booklet). Page markers (<!-- p.N -->) are removed.

* Hindi booklet: the placeholders {{अनुक्रमणिका}} and {{उद्धृत वचन}} become the contents (from the `# खण्ड …`
  headings) and the index of quotations (every **"…"** followed by a source in brackets), whose page numbers are
  read from a first build.
* English discourse booklet (SPEC_ENGLISH_DISCOURSE_BOOKLET.md): a `::: toc` block (rows `N | title | bookmark`)
  and a `::: quotations` block (rows `bookmark | quotation | source`) become the contents and the index with
  Word PAGEREF fields, so Word recomputes the page numbers for the fonts of the computer that opens the file;
  the cached numbers are those of the build. `{{end title page}}` and `{{end front matter}}` end the sections
  of the title page (no folio) and of the front matter (roman folios); the text is numbered from 1.
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


ROMAN = [(10, "x"), (9, "ix"), (5, "v"), (4, "iv"), (1, "i")]


def roman(n: int) -> str:
    out = ""
    for v, s in ROMAN:
        while n >= v:
            out, n = out + s, n - v
    return out


_bm = iter(range(99001, 99999))


def bookmark(name: str) -> str:
    i = next(_bm)
    return f'<w:bookmarkStart w:id="{i}" w:name="{name}"/><w:bookmarkEnd w:id="{i}"/>'


def pageref(bm: str, pages: dict[str, str]) -> str:
    """A PAGEREF field to a bookmark, its cached result the page found in the last build."""
    return (
        f'<w:fldSimple w:instr=" PAGEREF {bm} \\h "><w:r><w:t>{xml(pages.get(bm, ""))}</w:t></w:r>'
        "</w:fldSimple>"
    )


def toc_xml(lines: list[str], pages: dict[str, str]) -> str:
    """English discourse booklet: `::: toc` (heading, then rows `N | title | bookmark`)."""
    paras = [
        f'<w:p><w:pPr><w:pStyle w:val="ContentsHeading"/></w:pPr>{bookmark("contents")}{runs_xml(lines[0])}</w:p>'
    ]
    small = '<w:rPr><w:sz w:val="20"/><w:szCs w:val="20"/></w:rPr>'
    for line in lines[1:]:
        cells = [c.strip() for c in line.split("|")]
        if len(cells) != 3:
            continue
        num, title, bm = cells
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", bm) or bm in ("P", "Page"):
            paras.append(  # the column heads, small, as in the exemplar
                f'<w:p><w:pPr><w:pStyle w:val="TocItem"/></w:pPr><w:r>{small}<w:t>{xml(num)}</w:t></w:r>'
                f"<w:r><w:tab/></w:r><w:r>{small}<w:t>{xml(title)}</w:t></w:r><w:r><w:tab/></w:r>"
                f"<w:r>{small}<w:t>{xml(bm)}</w:t></w:r></w:p>"
            )
            continue
        paras.append(
            f'<w:p><w:pPr><w:pStyle w:val="TocItem"/></w:pPr><w:r><w:t>{xml(num)}</w:t></w:r>'
            f"<w:r><w:tab/></w:r>{runs_xml(title)}<w:r><w:tab/></w:r>{pageref(bm, pages)}</w:p>"
        )
    return "\n```{=openxml}\n" + "\n".join(paras) + "\n```\n"


def quotations_xml(lines: list[str], pages: dict[str, str]) -> str:
    """English discourse booklet: `::: quotations` (heading, then rows `bookmark | quotation | source`)."""
    paras = [
        f'<w:p><w:pPr><w:pStyle w:val="IndexHeading"/></w:pPr>{bookmark("quotations")}{runs_xml(lines[0])}</w:p>'
    ]
    n = 0
    for line in lines[1:]:
        cells = [c.strip() for c in line.split("|", 2)]
        if len(cells) != 3:
            continue
        bm, quote, src = cells
        n += 1
        words = quote.split()
        shown = "“" + " ".join(words[:5]) + ("”" if len(words) <= 5 else "")
        paras.append(
            f'<w:p><w:pPr><w:pStyle w:val="IndexItem"/></w:pPr><w:r><w:t>{n}.</w:t></w:r><w:r><w:tab/></w:r>'
            f'<w:r><w:rPr><w:b/><w:bCs/></w:rPr><w:t xml:space="preserve">{xml(shown)}</w:t></w:r>'
            f'<w:r><w:t xml:space="preserve"> ({xml(src)})</w:t></w:r><w:r><w:tab/></w:r>{pageref(bm, pages)}</w:p>'
        )
    return "\n```{=openxml}\n" + "\n".join(paras) + "\n```\n"


def section_markers(md: str) -> str:
    """{{end title page}} / {{end front matter}} -> paragraphs that close a Word section (filled in later)."""
    tiny = '<w:spacing w:before="0" w:after="0" w:line="20" w:lineRule="exact"/>'
    for marker, rsid, name in (
        ("{{end title page}}", "00000001", "titlepageend"),
        ("{{end front matter}}", "00000002", "frontmatterend"),
    ):
        md = md.replace(
            marker,
            f'```{{=openxml}}\n<w:p><w:pPr>{tiny}<w:sectPr w:rsidR="{rsid}"/></w:pPr>{bookmark(name)}</w:p>\n```',
        )
    return md


def printed_lists(md: str, pages: dict[str, str] | None = None) -> str:
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

    def block_lines(m):
        return [
            line.strip() for line in m.group(1).strip().splitlines() if line.strip()
        ]

    pages = pages or {}
    md = re.sub(
        r"^::: toc\n(.*?)^:::\s*$",
        lambda m: toc_xml(block_lines(m), pages),
        md,
        flags=re.M | re.S,
    )
    md = re.sub(
        r"^::: quotations\n(.*?)^:::\s*$",
        lambda m: quotations_xml(block_lines(m), pages),
        md,
        flags=re.M | re.S,
    )
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


def build_once(
    src_md: str, out_docx: Path, ref: Path, workdir: Path, pdf_dir: Path
) -> Path:
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
    md_file.unlink()
    postprocess(out_docx)
    pdf_dir.mkdir(parents=True, exist_ok=True)
    fc = pdf_dir / "fonts.conf"
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
            'pdf:writer_pdf_Export:{"ExportBookmarksToPDFDestination":{"type":"boolean","value":"true"}}',
            "--outdir",
            str(pdf_dir),
            str(out_docx),
        ],
        capture_output=True,
        env=env,
    )
    return pdf_dir / (out_docx.stem + ".pdf")


# The order of the children of w:settings in the WordprocessingML schema (ISO/IEC 29500, CT_Settings).
SETTINGS_ORDER = """writeProtection view zoom removePersonalInformation removeDateAndTime doNotDisplayPageBoundaries
displayBackgroundShape printPostScriptOverText printFractionalCharacterWidth printFormsData embedTrueTypeFonts
embedSystemFonts saveSubsetFonts saveFormsData mirrorMargins alignBordersAndEdges bordersDoNotSurroundHeader
bordersDoNotSurroundFooter gutterAtTop hideSpellingErrors hideGrammaticalErrors activeWritingStyle proofState
formsDesign attachedTemplate linkStyles stylePaneFormatFilter stylePaneSortMethod documentType mailMerge
revisionView trackRevisions doNotTrackMoves doNotTrackFormatting documentProtection autoFormatOverride
styleLockTheme styleLockQFSet defaultTabStop autoHyphenation consecutiveHyphenLimit hyphenationZone
doNotHyphenateCaps showEnvelope summaryLength clickAndTypeStyle defaultTableStyle evenAndOddHeaders
bookFoldRevPrinting bookFoldPrinting bookFoldPrintingSheets drawingGridHorizontalSpacing
drawingGridVerticalSpacing displayHorizontalDrawingGridEvery displayVerticalDrawingGridEvery
doNotUseMarginsForDrawingGridOrigin drawingGridHorizontalOrigin drawingGridVerticalOrigin doNotShadeFormData
noPunctuationKerning characterSpacingControl printTwoOnOne strictFirstAndLastChars noLineBreaksAfter
noLineBreaksBefore savePreviewPicture doNotValidateAgainstSchema saveInvalidXml ignoreMixedContent
alwaysShowPlaceholderText doNotDemarcateInvalidXml saveXmlDataOnly useXSLTWhenSaving saveThroughXslt
showXMLTags alwaysMergeEmptyNamespace updateFields hdrShapeDefaults footnotePr endnotePr compat docVars rsids
mathPr attachedSchema themeFontLang clrSchemeMapping doNotIncludeSubdocsInStats doNotAutoCompressPictures
forceUpgrade captions readModeInkLockDown smartTagType schemaLibrary shapeDefaults doNotEmbedSmartTags
decimalSymbol listSeparator""".split()


def fix_settings(data: bytes, update_fields: bool) -> bytes:
    """Put w:settings in schema order (Word is strict where LibreOffice is not); ask Word to update fields."""
    from lxml import etree

    root = etree.fromstring(data)
    w = (
        root.nsmap.get("w")
        or "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    )
    if update_fields and root.find(f"{{{w}}}updateFields") is None:
        el = etree.SubElement(root, f"{{{w}}}updateFields")
        el.set(f"{{{w}}}val", "true")
    rank = {name: i for i, name in enumerate(SETTINGS_ORDER)}
    kids = list(root)
    for k in kids:
        root.remove(k)
    for k in sorted(kids, key=lambda e: rank.get(etree.QName(e).localname, len(rank))):
        root.append(k)
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)


# The order of the children of w:pPr and w:rPr in the schema (ISO/IEC 29500, CT_PPrBase and CT_RPr)
PPR_ORDER = """pStyle keepNext keepLines pageBreakBefore framePr widowControl numPr suppressLineNumbers pBdr shd tabs
suppressAutoHyphens kinsoku wordWrap overflowPunct topLinePunct autoSpaceDE autoSpaceDN bidi adjustRightInd
snapToGrid spacing ind contextualSpacing mirrorIndents suppressOverlap jc textDirection textAlignment
textboxTightWrap outlineLvl divId cnfStyle rPr sectPr pPrChange""".split()
RPR_ORDER = """rStyle rFonts b bCs i iCs caps smallCaps strike dstrike outline shadow emboss imprint noProof snapToGrid
vanish webHidden color spacing w kern position sz szCs highlight u effect bdr shd fitText vertAlign rtl cs em
lang eastAsianLayout specVanish oMath""".split()


def schema_order(data: bytes) -> bytes:
    """Put the children of every w:pPr and w:rPr in schema order (pandoc and python-docx do not always)."""
    from lxml import etree

    root = etree.fromstring(data)
    w = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    for tag, order in (("pPr", PPR_ORDER), ("rPr", RPR_ORDER)):
        rank = {f"{{{w}}}{n}": i for i, n in enumerate(order)}
        for el in root.iter(f"{{{w}}}{tag}"):
            kids = list(el)
            keys = [rank.get(k.tag, len(rank)) for k in kids]
            if keys == sorted(keys):
                continue
            for k in kids:
                el.remove(k)
            for k in sorted(kids, key=lambda e: rank.get(e.tag, len(rank))):
                el.append(k)
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)


def fill_sections(doc: bytes) -> bytes:
    """Complete the section breaks of the title page and the front matter from the body's section."""
    if b'w:rsidR="0000000' not in doc:
        return doc
    body = list(re.finditer(rb"<w:sectPr>(.*?)</w:sectPr>", doc, re.S))[-1]
    inner = body.group(1)
    foot = b"".join(re.findall(rb"<w:(?:footer|header)Reference[^>]*/>", inner))
    page = b"".join(re.findall(rb"<w:pg(?:Sz|Mar)[^>]*/>", inner))
    title = (
        b"<w:sectPr>" + page + b"</w:sectPr>"
    )  # no footer: the title page has no folio
    front = (
        b"<w:sectPr>"
        + foot
        + page
        + b'<w:pgNumType w:fmt="lowerRoman" w:start="1"/></w:sectPr>'
    )
    main = b"<w:sectPr>" + foot + page + b'<w:pgNumType w:start="1"/></w:sectPr>'
    doc = doc[: body.start()] + main + doc[body.end() :]
    doc = doc.replace(b'<w:sectPr w:rsidR="00000001"/>', title)
    return doc.replace(b'<w:sectPr w:rsidR="00000002"/>', front)


def postprocess(docx: Path) -> None:
    """Renumber drawing ids (duplicates make Word hide images), complete the sections, fix the settings."""
    tmp = docx.with_suffix(".tmp")
    with zipfile.ZipFile(docx) as zin:
        has_fields = b"PAGEREF" in zin.read("word/document.xml")
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename == "word/document.xml":
                    counter = iter(range(1, 100000))
                    data = re.sub(
                        rb'(<wp:docPr\b[^>]*?\bid=")\d+(")',
                        lambda m: m.group(1) + str(next(counter)).encode() + m.group(2),
                        data,
                    )
                    data = schema_order(fill_sections(data))
                elif item.filename == "word/styles.xml":
                    data = schema_order(data)
                elif item.filename == "word/settings.xml":
                    data = fix_settings(data, has_fields)
                zout.writestr(item, data)
    tmp.replace(docx)


def dest_pages(pdf: Path) -> dict[str, str]:
    """Bookmark -> printed folio, from the PDF's named destinations (LibreOffice exports the bookmarks; it
    writes "_" in a name as "5F", so the build's own bookmark names have no underscore)."""
    import pymupdf

    doc = pymupdf.open(str(pdf))
    names = {
        k: v["page"] for k, v in doc.resolve_names().items() if v.get("page", -1) >= 0
    }
    first_main = names["frontmatterend"] + 1 if "frontmatterend" in names else 0
    first_front = names["titlepageend"] + 1 if "titlepageend" in names else 0
    out = {}
    for k, i in names.items():
        out[k] = (
            str(i - first_main + 1) if i >= first_main else roman(i - first_front + 1)
        )
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("outdir")
    ap.add_argument("--name")
    a = ap.parse_args()
    src = Path(a.source).resolve()
    out = Path(a.outdir).resolve()
    out.mkdir(parents=True, exist_ok=True)
    check = out / "check"
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
        fields = "::: toc" in md or "::: quotations" in md

        def render(cpages, ipages, dpages=None):
            text = section_markers(printed_lists(md, dpages))
            if "{{अनुक्रमणिका}}" in text:
                text = text.replace(
                    "{{अनुक्रमणिका}}", contents_xml(md, meta.get("title", ""), cpages)
                )
            if "{{उद्धृत वचन}}" in text:
                text = text.replace("{{उद्धृत वचन}}", index_xml(entries, ipages))
            return text

        pdf = build_once(
            render({} if with_pages else None, None), docx, ref, src.parent, check
        )
        if (
            fields
        ):  # cache the page numbers of this layout in the fields (Word recomputes them)
            dpages = dest_pages(pdf)
            pdf = build_once(render(None, None, dpages), docx, ref, src.parent, check)
            if dest_pages(pdf) != dpages:
                print("warning: pages moved on the second pass; build again")
        if entries or with_pages:
            ipages = find_pages(pdf, [q for q, _ in entries]) if entries else None
            cpages = dict(zip(heads, find_pages(pdf, heads))) if with_pages else None
            pdf = build_once(render(cpages, ipages), docx, ref, src.parent, check)
            if entries:
                again = find_pages(pdf, [q for q, _ in entries])
                if again != ipages:
                    print("warning: index pages moved on the second pass; build again")
                missing = [q for (q, _), p in zip(entries, ipages) if not p]
                if missing:
                    print("warning: quotations not found in the PDF:", missing)
        info = run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
        npages = re.search(r"Pages:\s+(\d+)", info).group(1)
        nq = len(entries) if entries else len(re.findall(r"^q\d+ \|", md, re.M))
        print(
            f"{name}: {npages} pages, {len(heads)} headings, {nq} indexed quotations -> {docx} (check PDF: {pdf})"
        )


if __name__ == "__main__":
    main()
