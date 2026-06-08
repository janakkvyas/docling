# Ṣoḍaśagrantha & Aṇubhāṣya — aligned book

This directory holds a clean, book-formatted edition of the Vallabhācārya corpus
(the *Ṣoḍaśagrantha* stotras/prakaraṇa works and the *Brahmasūtra-Aṇubhāṣya*
commentary) rebuilt from an OCR of the original Devanagari scan.

## Files

| File | What it is |
|------|------------|
| `source_ocr.md` | Raw OCR Markdown from the scan (Sarvam vision OCR via docling). Input. |
| `book.md` | Structurally aligned book Markdown (the pipeline output). |
| `book.epub` | EPUB edition (embeds Noto Serif Devanagari). **Deliverable.** |
| `book.pdf` | PDF edition, 225 pp., typeset with xelatex. **Deliverable.** |
| `assets/` | The two images extracted from the scan. |

## Pipeline

Three scripts under `../scripts/` reproduce everything:

```bash
# 1. OCR the PDF -> source_ocr.md  (needs SARVAM_API_KEY)
uv run python scripts/sarvam_convert.py INPUT.pdf book/source_ocr.md

# 2. Structure: clean OCR Markdown -> book.md
uv run python scripts/bookify.py book/source_ocr.md book/book.md

# 3. Build EPUB + PDF (needs pandoc + xelatex + Noto Devanagari fonts)
uv run python scripts/bookify_build.py book/book.md book/
```

### What `bookify.py` does

- Classifies headings: only daṇḍa-wrapped titles (`।। … ।।`) and a small
  allow-list are real work titles; verse/sūtra lines that the OCR mistakenly
  marked as headings are demoted back to body text. Decisions are logged.
- Converts the OCR's footnotes into per-section endnotes (टिप्पण्यः).
- Turns the litany `<table>` blocks (the नमः epithet lists) into Markdown lists.
- Extracts the embedded base64 images to `assets/` and drops the English OCR
  captions.
- Removes the duplicated running footer and the `<!-- chunk … -->` markers.
- Strips the interleaved Hindi भावार्थ commentary, leaving the pure Sanskrit
  mūla text. This covers both the **parenthetical** glosses and the
  **standalone Hindi prose** sentences sprinkled between the verses (e.g.
  *"कृपा प्राप्त करनेका मार्ग पुष्टिमार्ग नहीं है…"*), plus the
  footnote/टिप्पण्यः blocks. Detection keys on whole-token Hindi markers
  (है, हैं, नहीं, को, चाहिये …) that never occur in the Sanskrit text, so
  scripture **citations** — `(तैत्ति.उप.2।1)`, `(भग.गीता 4।24)` — sigla,
  textual-variant notes, and the entire Sanskrit Aṇubhāṣya commentary of
  Part II are preserved untouched.
- Renders verses as Markdown line blocks so the poetry keeps its line breaks.
- Builds the two-part hierarchy: **भाग १** (stotras/prakaraṇa works) and
  **भाग २** (Aṇubhāṣya). For भाग २ it reconstructs the full
  अध्याय → पाद structure (4 × 4 = 16 sections) by parsing the adhikaraṇa-end
  markers, which name their own chapter and quarter (e.g.
  *…प्रथमाध्याये द्वितीयपादे …अधिकरणम्॥3॥*). Section order is enforced monotonic
  so stray quoted ordinals cannot misplace a heading.

A full run report is written to `bookify_report.json`.

## A note on proofreading (intentionally **not** applied)

`scripts/bookify_proofread.py` is a conservative LLM proofreading pass (Sarvam
`sarvam-105b`, numbers/sūtra-refs/sigla masked, per-unit validation, changelog).
On a representative Part I sample it changed ~21 % of text units, and inspection
showed most changes were **not** OCR fixes but alterations of the scripture —
daṇḍas turned into periods, sandhi rewritten, an epithet swapped
(श्रीकृष्णास्यं → श्रीकृष्णचरणं), and even an invented word. The Sarvam OCR was
already at the quality ceiling, so the deep pass was **deliberately skipped** to
preserve textual fidelity. The script and its safeguards are kept for reference;
run it only with careful human review of `changelog.md`.
