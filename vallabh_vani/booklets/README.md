# Booklets: Hindi pravachan booklets and English stuti books

What the owner's published booklets look like, written down so that a new booklet can be made the same way when the owner asks for one, and the tools that make them. **They are not a model for the translation project**: translations and editions stay verbatim, in the format of the series briefs, and take nothing from published works (see `../README.md`).

| File | What it is |
|---|---|
| `SPEC_HINDI_BOOKLET.md` | brief and house style of the Hindi pravachan booklet, learned from प्रतिबिम्बवाद (2026, rev. 2) |
| `SPEC_ENGLISH_STUTI_BOOK.md` | brief and house style of the English stuti book, learned from नलकूबरमणिग्रीवकृतस्तुति (rev. 1) |
| `IDIOM.md` | the speaker's idiom as the Hindi booklet prints it, every form counted, with examples |
| `samples/` | the opening pages of both exemplars in the house markdown: the build test |
| `templates/` | Word templates with the house styles (`Booklet_HI_template.docx`, `Booklet_EN_template.docx`) |
| `fonts/` | Noto Sans Medium, the Hindi booklet's typeface (SIL Open Font License, `OFL.txt`) |
| `tools/` | template, build, checks, and the tools for studying a new exemplar (below) |

The project instructions for a Claude Project, covering these and the lecture series, are `../PROJECT_INSTRUCTIONS.md`. **The owner receives Word files only**: the build writes the `.docx` to the output folder and a PDF for checking to `check/` inside it; never send the PDF or the markdown. The full clean copies of the two exemplars are kept with the owner (they are published booklets; this repository is public).

## Setup

```bash
sudo apt-get install -y pandoc libreoffice-writer poppler-utils fonts-noto-core fonts-crosextra-carlito
pip install python-docx pymupdf fonttools pillow
mkdir -p ~/.local/share/fonts && cp vallabh_vani/booklets/fonts/NotoSans-Medium.ttf ~/.local/share/fonts/ && fc-cache -f
```

Calibri (the Hindi booklet's folio) is replaced by the metric-compatible Carlito and "Sanskrit Text" (the English book's font, part of Windows) by Noto Serif and Noto Serif Devanagari: `build_booklet.py` sets these substitutions for LibreOffice itself.

## Making a booklet

```bash
cd vallabh_vani/booklets
python3 tools/lint_booklet.py samples/pratibimbavada_opening.md          # house conventions
python3 tools/build_booklet.py samples/pratibimbavada_opening.md out/    # out/*.docx, check PDF in out/check/
python3 tools/build_booklet.py samples/nalakubara_opening.md out/
```

`build_booklet.py` reads `booklet: hindi|english` from the YAML block, writes the reference template (`make_ref_booklet.py`), runs pandoc with `booklet.lua` (classes → paragraph styles, `* * *` → new page, bold → the 13 pt quotation style), converts with LibreOffice, and, for a Hindi booklet, generates the contents and the index of quotations, finding each quotation's page in a first build and writing the numbers in a second. The build can also write a contents and an index as Word PAGEREF fields (`::: toc`, `::: quotations`) and a title page and front matter as their own sections (`{{end title page}}`, `{{end front matter}}`), and it puts the template's style properties and settings in the order of the WordprocessingML schema, which Word requires. `iast.py` gives the house transliteration of a Devanagari line.

The template was checked against the exemplar by rebuilding the clean copy of प्रतिबिम्बवाद with it: built with LibreOffice from the clean copy, the booklet comes to 92 pages like the original, and 60 of the 85 printed pages that begin with running text begin on the same page of the rebuild. The other 25, in sections 6, 7 and 9, begin one page earlier, because the template opens every section like p. 10 while the original's openings were placed by hand lower on the page (copying the original's openings into a test build brings 78 of the 85 onto the same page). Within a page LibreOffice and Word fill lines slightly differently, a word or so per line, which no style setting removes; in Word the template carries the original's own settings and should lay the text out as the original (not verified here, as Word is not available in this environment).

## Studying a new exemplar

When the owner shares another finished booklet, learn it the way these two were learned, and update the brief only with the owner's agreement:

1. **Fonts**: `python3 tools/pdf_fonts.py NEW.pdf fonts_new/ --patch` names the real typefaces (PDFs hide them as "CIDFont+F2"), their metrics and coverage, and extracts them.
2. **Sizes and positions**: `python3 tools/pdf_runs.py NEW.pdf 1 3 10` lists every text run with font, size, weight and baseline; `python3 tools/measure_pages.py NEW.pdf:10 …` gives line positions and spacing. A Word "Print to PDF" file draws at 0.75 scale, which `pdf_runs.py` already allows for.
3. **Text**: if the PDF's text layer is broken (look for "त ब बवाद" for प्रतिबिम्बवाद), ask for the `.docx`. Otherwise transcribe from the page images: OCR with Tesseract (`-l hin+eng --psm 6`, one thread per process) as a draft, then one agent per ten pages working to `tools/TRANSCRIPTION_BRIEF.md`. Check every page with `tools/check_layer.py` (against the text layer: what it keeps is exact) and `tools/glyph_check.py` (each word shaped with the PDF's own font and compared with the glyphs the PDF draws: this also proves where the print has a visible virama and inserts the ZWNJ).
4. **Compare**: rebuild with the template and set pages side by side (`tools/side_by_side.py EXEMPLAR.pdf REBUILD.pdf out.png 1:1 10:10`); write down what the new booklet confirms, what it changes and its inconsistencies.
