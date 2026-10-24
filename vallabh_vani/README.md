# Vallabh Vani — lecture transcription and translation workspace

This directory records the work done on lecture series for Vallabh Vani, the discourses of Gosvāmī Śrī Śyām
Manoharjī, so that the pipeline, the editorial conventions and the finished texts live with the code that produced them. It is
independent of the Docling package: nothing here is imported by `docling`, and the repository's hooks only
apply the line-count limit to it.

| Series | Sessions | Language of the lectures | What was produced |
|---|---|---|---|
| `shastrarth_prakaran/` — the Śāstrārtha Prakaraṇa of Vallabhācārya's Tattvārthadīpanibandha | 13 weekly sessions, 2026-07-11 → 2026-10-17 | Hindi (with Gujarati, Sanskrit, English) | Hindi ASR transcripts; 15 English translation documents (Lectures 3 and 5 in two parts; 570 pages), 104 figures; every quoted kārikā and Prakāśa sentence verified against the Bombay 1943 edition |
| `kapil_gita/` — the Kapila Gītā (Śrīmad Bhāgavata 3.25–33) by **Dr. Dharmendra Jhala**, transcribed by mistake: not part of the corpus | 15 sessions, 2022-10-30 → 2023-03-05 (revision) | English (with Sanskrit, Hindi, Gujarati) | English ASR transcripts; 15 verbatim reading editions |
| `kapil_gita_gsm/` — the Kapila Gītā (Śrīmad Bhāgavata 3.24–26) by **Gosvāmī Śrī Śyām Manoharjī** | 14 sessions, 2022-01-30 → 2022-03-03 | English (with Sanskrit, Hindi, Gujarati) | English ASR transcripts; 14 verbatim reading editions |

The owner's requirements for the translation project (2026-10-24): translations and editions are **verbatim**,
in the format of the earlier deliveries (the series briefs and `tools/build_final.py`), and the owner receives
**Word files only** (`.docx`), never PDF or markdown. They take nothing from published works: no wording,
renderings, conventions or layout from published translations or from the booklets in `booklets/`. The
`.docx` deliverables are not committed (they are built from the markdown here, see *Building*; PDFs are made
only to check the layout), nor is any audio. Private transcripts of a living teacher's classes: treat the contents of
this directory with the discretion the speaker and his students would expect.

Two published booklets the owner shared are documented in `booklets/`: the **Hindi pravachan booklet** (model
प्रतिबिम्बवाद, 2026) and the **English stuti book** (model नलकूबरमणिग्रीवकृतस्तुति). They are reference for making a
booklet when the owner asks for one, never a model for the translations. (An "English discourse booklet" that set
the lecture editions in the stuti book's style was made on 2026-10-23 and withdrawn on 2026-10-24 at the owner's
request; it is in the history of this repository only.) `booklets/README.md` lists the briefs, the speaker's
idiom, the Word templates and the build. `PROJECT_INSTRUCTIONS.md` is the text for a Claude Project that covers
all the work.

## Layout

```
vallabh_vani/
  README.md
  PROJECT_INSTRUCTIONS.md       instructions for a Claude Project covering all the work
  booklets/                     the owner's published booklets: briefs, idiom, templates, build (booklets on request only)
  tools/                         the pipeline (see below)
  shastrarth_prakaran/
    SPEC.md                      the translation brief the agents worked to, with the settled conventions
    APPLY_CONCORDANCE.md         how the verified kārikā text was applied to the finished lectures
    series.cfg                   "sp Shastrarth_Prakaran_Lecture": markdown prefix and output basename
    sources/LNN_<date>.srt       the ASR transcript, one subtitle per segment, with speaker labels
    sources/LNN_<date>_turns.txt the same condensed to one line per speaker turn (what the translators read)
    sources/charts/*.pdf         the charts the speaker shared in four sessions
    lectures/*.md, figsNN/       the finished translations (pandoc markdown) and their figures
    figure_scripts/              the matplotlib scripts that draw the figures
    karika_concordance.md        every Śāstrārtha kārikā and Prakāśa sentence quoted, verified in the 1943 scans
    Shastrarth_Prakaran_Appendix_Karikas_Prakasha_1943.md   the verified texts as a reference appendix
    Shastrarth_Prakaran_Closing_Reports.md                   one report per lecture
  kapil_gita/
    SPEC.md, series.cfg, lint_md.py
    sources/KNN_<date>.srt, KNN_<date>_turns.txt
    lectures/*.md
    Kapil_Gita_Closing_Reports.md
  kapil_gita_gsm/
    SPEC.md, series.cfg, lint_md.py
    sources/KNN_<date>.txt, .srt, _turns.txt; RECORDINGS.md
    lectures/*.md
    Kapil_Gita_GSM_Closing_Reports.md
```

## Pipeline

1. **Audio.** Recordings are downmixed to mono 16 kHz 64 kbps MP3 with ffmpeg. Sarvam's batch API
   accepts at most 7200 s per file, so longer recordings are cut at a pause near the middle
   (`silencedetect`) and the cut time is recorded in a `cuts.txt` (`<date> <seconds>`).
2. **Transcription.** `tools/sarvam_batch.py IN_DIR OUT_DIR LANGUAGE_CODE KEYTERMS_FILE` submits a
   folder to Sarvam AI (`saaras:v4`, verbatim mode, speaker diarization, word timestamps, up to 50
   key terms that bias recognition). The API key is read from `SARVAM_API_KEY`. Language codes used:
   `unknown` (auto-detect; the Hindi lectures came back as `hi-IN`) and `en-IN`. Key-term lists:
   `tools/keyterms_shastrarth.txt`, `tools/keyterms_kapil_gita.txt`. A key term can be hallucinated
   into noise or silence; the briefs tell the editors to treat isolated occurrences with suspicion.
3. **Transcripts.** `tools/transcript_from_json.py JSON_DIR OUT_DIR PREFIX "Main speaker" [cuts.txt]`
   turns the JSON results into three files per date: a review transcript with one `[hh:mm:ss]` line per
   segment, an `.srt`, and a condensed one-line-per-turn file. The speaker with the most airtime is the
   main speaker; others are numbered listeners. Recordings processed in two halves are re-joined with
   the recorded offset. (`tools/condense.py` is the earlier condenser kept for reference; an early
   version of it dropped continuation lines, which is why the briefs mention recovered lines.)
4. **Editing / translation.** One agent per lecture worked to the brief in `SPEC.md`: read the whole
   transcript, map the argument, write pandoc markdown in chunks with heading checks after each append,
   draw the figures (Śāstrārtha only), build, verify. The non-negotiable rule in both briefs is
   fidelity to the speaker's own words.
5. **Verification against print (Śāstrārtha).** Every Tattvārthadīpanibandha kārikā and Prakāśa sentence
   the speaker quotes was located and read in the page images of the Bombay 1943 edition
   (ed. Harishankar Shastri, archive.org `jhzf-tattvartha-deepa-nibandha-shastrartha-prakarana-pr`),
   cross-checked with the 1904 Gyan Sagar edition; `karika_concordance.md` records each one with page
   and leaf, and `APPLY_CONCORDANCE.md` is the rule set under which the lectures were conformed to it.
6. **Build.** `tools/make_ref.py` writes the house `ref.docx` (Noto Serif / Noto Serif Devanagari,
   maroon headings, A4, page numbers). `tools/build_final.py OUTDIR [KEY …]` runs pandoc with it and
   `tools/verse_breaks.lua` (so each half-line of a verse prints on its own line), renumbers Word's
   `wp:docPr` ids (duplicates make Word hide images), converts to PDF with LibreOffice for checking, and copies
   the `.docx` to the output folder (Word files only). `tools/lint_md.py` checks the house format (title, preface,
   consecutive numbered sections, figure numbering and files, the three-paragraph Brief Summary, no lists).
   `tools/normalize.py` enforces series-wide spellings; `tools/contact_sheet.py` tiles figures for review;
   `tools/package.sh` zips deliverables under the 30 MB upload limit.

### Building the documents

```bash
sudo apt-get install -y fonts-noto-core pandoc libreoffice-writer poppler-utils
pip install python-docx matplotlib pillow sarvamai
cd vallabh_vani/shastrarth_prakaran            # or kapil_gita
mkdir -p build && cp lectures/*.md build/ && cp -r lectures/figs* build/ 2>/dev/null
python3 ../tools/make_ref.py build/ref.docx    # run from a directory containing tools/ and build/ … see below
```

`build_final.py` expects a project directory with `tools/` (the scripts and `series.cfg`), `build/`
(the `spNN.md` / `kgNN.md` sources, figures and `ref.docx`) and writes to `outputs/`. The committed
lecture files are named by their output basenames; to rebuild, copy them to `build/` as
`sp01.md`, `sp03_part1.md`, … (`kg01.md`, …) alongside their `figsNN/` folders.

## Editorial conventions (both series)

- Editorial flags: `‹ ›` conjectural restoration, `‹?›` uncertain reading, `‹…›` inaudible,
  `‹श्रवणाधारित›` given as heard, pending verification against print.
- Verses whose standard text is certain are silently restored to the received edition and cited;
  anything unverifiable stays flagged; a misattribution by the speaker is kept and the correct source added.
- Sensitive remarks are kept as spoken with the marker ‹the speaker's characterization›.
- Film-song lyrics are never reproduced; pre-1929 devotional poetry and scripture are.
- Spellings: Mahāprabhuji, Gosāīṁjī, Puruṣottamajī, Brahman, Paramātmā, Bhagavān, Śuddhādvaita,
  Bhagavadgītā; tradition-internal terms are left untranslated and unglossed.
- Śāstrārtha kārikās are cited by the 1943 numbering; a block that joins the second half of one kārikā to
  the first half of the next (as the 1943 commentary prints kārikās 25–30) is cited `26cd–27ab` etc.

## Status

Both series are complete. Śāstrārtha Prakaraṇa: 13 sessions, 15 documents, 570 pages, 219 sections, 104 figures; every one of the 22 kārikās and 93 Prakāśa sentences the speaker quotes was read in the 1943 page images. Kapila Gītā (Dr. Dharmendra Jhala, transcribed by mistake): 15 sessions, 15 verbatim editions, 230 sections; Bhāgavata, Gītā and Upaniṣad verses were restored from e-texts, while the Subodhinī passages the speaker reads aloud remain ‹श्रवणाधारित› because no reliable e-text exists. The two closing-reports files say, lecture by lecture, what was restored and what remains flagged for checking against print or the audio.
