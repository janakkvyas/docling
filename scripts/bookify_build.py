#!/usr/bin/env python3
"""Build EPUB and PDF from the structured book Markdown via pandoc.

EPUB embeds Noto Serif Devanagari; PDF is produced with xelatex using a
Devanagari main font and a Latin fallback so the rare Latin glyph still renders.

Usage:
    uv run python scripts/bookify_build.py BOOK.md OUTDIR \
        [--title T] [--author A]
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path

DEVA_SERIF = "/usr/share/fonts/truetype/noto/NotoSerifDevanagari-Regular.ttf"

# xelatex preamble: Devanagari main font + Latin fallback family.
HEADER_TEX = r"""
\usepackage{fontspec}
\setmainfont{Noto Serif Devanagari}
\newfontfamily\latinfallback{Noto Serif}
\usepackage{newunicodechar}
\newunicodechar{•}{\textbullet}
\setlength{\emergencystretch}{3em}
"""


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd[:6]), "...", flush=True)
    subprocess.run(cmd, check=True)


def build_epub(book: Path, out: Path, title: str, author: str) -> None:
    run([
        "pandoc", str(book), "-o", str(out),
        "--toc", "--toc-depth=4", "--split-level=2",
        "--metadata", f"title={title}",
        "--metadata", f"author={author}",
        "--metadata", "lang=hi",
        f"--epub-embed-font={DEVA_SERIF}",
        "--resource-path", f"{book.parent}:{book.parent}/assets",
    ])


def build_pdf(book: Path, out: Path, title: str, author: str, work: Path) -> None:
    header = work / "header.tex"
    header.write_text(HEADER_TEX, encoding="utf-8")
    run([
        "pandoc", str(book), "-o", str(out),
        "--pdf-engine=xelatex",
        "--toc", "--toc-depth=3",
        "-V", "documentclass=report",
        "-V", "geometry:margin=2cm",
        "-V", f"title={title}",
        "-V", f"author={author}",
        "-V", "mainfont=Noto Serif Devanagari",
        "-H", str(header),
        "--resource-path", f"{book.parent}:{book.parent}/assets",
    ])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("book")
    ap.add_argument("outdir")
    ap.add_argument("--title", default="षोडशग्रन्थ व अणुभाष्य संग्रह")
    ap.add_argument("--author", default="श्रीवल्लभाचार्य")
    ap.add_argument("--work-dir", default="/tmp/bookify_work")
    ap.add_argument("--skip-pdf", action="store_true")
    args = ap.parse_args()

    if not shutil.which("pandoc"):
        print("ERROR: pandoc not installed")
        return 2
    book = Path(args.book)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    work = Path(args.work_dir)

    build_epub(book, outdir / "book.epub", args.title, args.author)
    print(f"EPUB: {(outdir/'book.epub').stat().st_size/1e6:.2f} MB")
    if not args.skip_pdf and shutil.which("xelatex"):
        build_pdf(book, outdir / "book.pdf", args.title, args.author, work)
        print(f"PDF:  {(outdir/'book.pdf').stat().st_size/1e6:.2f} MB")
    elif not args.skip_pdf:
        print("WARNING: xelatex not found; skipped PDF")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
