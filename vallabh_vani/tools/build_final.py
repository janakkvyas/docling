#!/usr/bin/env python3
"""Build the deliverables of a lecture series from the markdown sources in build/.

For each lecture key (e.g. "01", "03_part1"): pandoc with the house reference document and the verse
line-break filter -> renumber wp:docPr ids (Word hides images when they repeat) -> LibreOffice PDF (kept in
build/ for checking) -> copy the .docx into the output directory. The owner receives Word files only.

The markdown prefix and the output basename come from tools/series.cfg next to this script, one line:
    sp Shastrarth_Prakaran_Lecture
so that build/sp03_part1.md becomes Shastrarth_Prakaran_Lecture03_Part1_EN.docx.

Usage: build_final.py [OUTDIR] [KEY ...]      default: all keys found in build/.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
PREFIX, BASENAME = (ROOT / "tools" / "series.cfg").read_text().split()


def renumber_docpr(docx: Path) -> int:
    """Give every wp:docPr a unique id; return the number of duplicates left (must be 0)."""
    tmp = docx.with_suffix(".tmp.docx")
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
    xml = zipfile.ZipFile(docx).read("word/document.xml").decode()
    ids = re.findall(r'<wp:docPr\b[^>]*?\bid="(\d+)"', xml)
    return len(ids) - len(set(ids))


def build(key: str, out: Path) -> None:
    nn, _, part = key.partition("_")
    base = f"{BASENAME}{nn}_{part.capitalize()}_EN" if part else f"{BASENAME}{nn}_EN"
    md = BUILD / f"{PREFIX}{key}.md"
    docx = BUILD / f"{base}.docx"
    subprocess.run(
        [
            "pandoc",
            md.name,
            "-o",
            docx.name,
            "--reference-doc=ref.docx",
            "-f",
            "markdown+smart",
            f"--lua-filter={ROOT / 'tools' / 'verse_breaks.lua'}",
        ],
        cwd=BUILD,
        check=True,
    )
    dups = renumber_docpr(docx)
    subprocess.run(
        [
            "soffice",
            "--headless",
            f"-env:UserInstallation=file:///tmp/lo_final_{PREFIX}{key}",
            "--convert-to",
            "pdf",
            "--outdir",
            str(BUILD),
            str(docx),
        ],
        check=True,
        capture_output=True,
    )
    pdf = docx.with_suffix(".pdf")
    info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
    pages = re.search(r"Pages:\s+(\d+)", info).group(1)
    images = len(
        [n for n in zipfile.ZipFile(docx).namelist() if n.startswith("word/media/")]
    )
    figures = len(re.findall(r"^!\[Figure", md.read_text(), re.M))
    shutil.copyfile(
        docx, out / docx.name
    )  # Word only: the PDF stays in build/ for checking
    print(
        f"{base}: {pages} pages, {figures} figure refs, {images} images in docx, duplicate docPr ids {dups}"
    )


def main(argv: list[str]) -> None:
    out = Path(argv[1]) if len(argv) > 1 else ROOT / "outputs"
    keys = argv[2:] or sorted(
        p.stem[len(PREFIX) :] for p in BUILD.glob(f"{PREFIX}[0-9][0-9]*.md")
    )
    out.mkdir(parents=True, exist_ok=True)
    for key in keys:
        build(key, out)


if __name__ == "__main__":
    main(sys.argv)
