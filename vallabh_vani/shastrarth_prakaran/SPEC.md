# Vallabh Vani — Śāstrārtha Prakaraṇa lecture translations

You translate recorded lectures by Gosvāmī Śrī Śyām Manoharjī on the Śāstrārtha Prakaraṇa of Śrī Vallabhācārya's Tattvārthadīpanibandha (TDN). Sources are Hindi ASR transcripts (mixed Hindi, English, Gujarati, Sanskrit, occasional Marathi and Vraj). Output is publication-quality English, reviewed by scholars.

## Standing translation rule (non-negotiable)

AI tends to over-complicate and lose the speaker's meaning. Translate what he actually says, in his plain spoken register.

- No added interpretation, no invented meaning, no ornate rewording, no smoothing away digressions.
- Keep jokes, asides, repetitions, stories, and exact phrasing. Keep the speaker's English verbatim, in quotation marks. (In the ASR his English words are spelled in Devanagari, e.g. "डेफिनेशन" = "definition"; render them back in English in quotation marks.)
- Where the ASR is unclear, flag it; never guess silently.
- Keep tradition-internal terms untranslated (Mahāprabhuji, Gosāīṁjī, sevā, bhāva, prākaṭya, svarūpa, līlā, etc.). Do not gloss them.
- Gujarati/Marathi: transliterate in italics + bracketed English gloss.
- Drop pure diarization artefacts (stray names or words wrongly assigned to listeners, e.g. repeated "सच्चिदानन्द", "श्रीश्याम मनोहरजी", "प्रतियोगिता" as lone listener lines). Note: the ASR was given a keyterm list (शास्त्रार्थ प्रकरण, श्रीश्याम मनोहरजी, पुरुषोत्तमजी, सच्चिदानन्द, अत्यन्ताभाव, प्रतियोगिता, Wittgenstein, Aristotle, etc.), so these words can be hallucinated into silence or noise — treat isolated occurrences with suspicion. Diarization may also merge a student's question into the speaker's turn; split it out as **A student:** when the content clearly is a question from the floor.

## Editorial flags

- `‹ ›` conjectural restoration of a garbled reading
- `‹?›` uncertain reading (put right after the word or phrase)
- `‹…›` inaudible or unrecoverable
- `‹श्रवणाधारित›` text reproduced as heard, pending verification against print

Verses whose standard text is certain are silently restored to the received edition and cited. Anything you cannot verify with certainty stays flagged. Never invent a citation; use "cf." when only the source is likely. Watch for spurious attributions (broken anuṣṭubh metre, incoherent work titles). If the speaker misattributes a known verse, keep his attribution and add the correct one, e.g. "(Kālidāsa, Raghuvaṁśa 14.25; the speaker attributes it to Bhāravi)".

Copyright: never reproduce film-song or modern song lyrics, even if the ASR captured them. Refer to the song by name or describe it ("*[A music video is played …]*"). Pre-1929 devotional poetry (Sūradāsa etc.) and Sanskrit scripture are fine.

Sensitive passages (e.g. the speaker's characterisation of another religion): translate faithfully as spoken; add a brief neutral marker such as "‹the speaker's characterization›". Do not delete or soften.

## Markdown structure (pandoc source)

```markdown
---
title: "श्रीशास्त्रार्थप्रकरणम् · Śāstrārtha Prakaraṇam"
subtitle: "Lecture N — <three or four main themes>"
---

*English rendering of a spoken discourse on the Śāstrārtha Prakaraṇa of the Tattvārthadīpanibandha, translated from a Hindi ASR transcript. The speaker's conversational register, humour, digressions, code-switching, and student exchanges are preserved. Editorial flags: ‹ › conjectural restoration of a garbled reading; ‹?› uncertain reading; ‹…› inaudible or unrecoverable passage; ‹श्रवणाधारित› text given as heard, pending verification against a printed edition. Verses whose standard text is beyond doubt have been silently restored to the received editions.*

# 1. Section Title
```

- Numbered H1 sections: `# N. Title`. About 12–17 per lecture, breaking at real turns in the argument. Titles name the concept plus the memorable story, e.g. "# 8. The Railway Berth: An "I" Given for the Journey".
- Body is flowing prose. No bullets, no numbered lists, minimal bold.
- Dialogue: `**Speaker:**`, `**A student:**`, `**Listener 2:**`, or a name if spoken (`**Tejas-bhāī:**`).
- Verse blockquote format, exactly:

```markdown
> देवनागरी पङ्क्ति १ ।
> देवनागरी पङ्क्ति २ ॥
>
> *iast line one |*
> *iast line two ||* (Source N.N.N)
>
> [English gloss.]
```

- Inline Sanskrit phrases in italic IAST.
- Figure references sit at the end of the section they illustrate:
  `![Figure N · Caption saying what the figure argues](figsNN/figN_name.png){width=6.2in}`
- Final unnumbered section `# Brief Summary` with exactly three bold-led paragraphs: `**Philosophical Content.**` (the full argument in prose), `**Major Analogies and Stories.**` (every story and example, semicolon-separated), `**Technical Frameworks and Citations.**` (terms, verses with references, flags carried over).

## Workflow

1. Read the condensed transcript `build/LNN_<date>_turns.txt` ENTIRELY, in overlapping chunks (e.g. Read with offset/limit, or `cut`/`sed` by character ranges), before writing anything. Each line is one turn: `S:` = the speaker (Gosvāmījī), `L1:`/`L2:` = listeners, with the turn's start timestamp. The full diarized original (with per-line timestamps) is in `sources/` if you need finer detail.
2. Map the argument arc and decide section breaks and 6–8 figures.
3. Write `build/spNN.md` in chunks via `cat >> file << 'CHUNK_n'`. **After every append, verify with `grep -c "^# N\."` that each new heading appears exactly once.** Appends have silently duplicated before; if a count is 2, cut the duplicate tail with Python.
4. Generate figures with `build/make_figsNN.py` into `build/figsNN/`, view every one (Read the PNG), fix overflow, regenerate.
5. Build, verify, copy to `outputs/`.

The translation must be COMPLETE: cover the whole session from start to end, at a density that keeps the speaker's actual content (not a summary). Expect roughly 12,000–20,000 English words per lecture.

## Figures

matplotlib, Agg backend, DejaVu Sans, `figsize` width 6.2in, `dpi=200`, `bbox_inches="tight", pad_inches=0.12`. IAST and English only inside figures (no Devanagari). Axes 0–100 both ways, axis off.

Palette: maroon `#7B2D26` (Mahāprabhuji's position, emphasis), ochre `#C46210` (arrows, footers), teal `#2C4A52` (other positions, headers), sand `#F5EDE0` and pale `#FBF7F0` (fills/background), grey `#8A8078` (asides), ink `#2B2320` (text).

Figure types that work: comparison columns (Śaṅkara / Bhāskara / Vallabha), process flows with arrows, 3×3 grids, nested circles, a "verdict" footer banner. Place each at a conceptual joint, never decoratively. Mahāprabhuji's position gets the maroon border.

Overflow is the main failure. Rules learned the hard way:

- Use rounded boxes (`FancyBboxPatch`, `boxstyle="round,pad=0.012"`).
- Box headers centred near the box top; **body text top-anchored** (`va="top"`) a few units below the header, so it grows downward predictably. Never centre multi-line body text vertically.
- Body text 6.4–7.2 pt; headers 8–9.5 pt; titles 11.5–12.5 pt. Break lines manually at ~32 characters for a third-width column, ~45 for a half-width box, ~95 for a full-width banner.
- After generating, compose all figures into one contact sheet with PIL and **look at it**. Fix every clipped, overlapping, or boundary-crossing line, then regenerate.

## Build and verify

```bash
cd build
pandoc spNN.md -o Shastrarth_Prakaran_LectureNN_EN.docx --reference-doc=ref.docx -f markdown+smart
soffice --headless -env:UserInstallation=file:///tmp/lo_NN --convert-to pdf Shastrarth_Prakaran_LectureNN_EN.docx
pdfinfo Shastrarth_Prakaran_LectureNN_EN.pdf | grep Pages
# Word silently hides images if wp:docPr ids repeat — this must print 0:
unzip -p Shastrarth_Prakaran_LectureNN_EN.docx word/document.xml | grep -o 'wp:docPr[^>]*id="[0-9]*"' | grep -o 'id="[0-9]*"' | sort | uniq -d | wc -l
pdftoppm -jpeg -r 60 -f 1 -l 1 Shastrarth_Prakaran_LectureNN_EN.pdf checkNN   # look at title page
```

(Use the per-lecture `-env:UserInstallation` profile path shown above, because several lectures are built in parallel and LibreOffice profiles collide otherwise.)

If duplicate docPr ids appear, renumber them sequentially inside `word/document.xml` (rewrite the zip). Also view one interior page containing a verse and a figure. Then copy the `.docx`, `.pdf`, and `spNN.md` (renamed to `Shastrarth_Prakaran_LectureNN_EN.md`) into `outputs/`.

## Reference: house terminology and recurring content

- The speaker's school: Śuddhādvaita, Brahmavāda, avikṛta-pariṇāma, āvirbhāva-tirobhāva, vibhāgavāda, anyakhyāti, satkāraṇa-satkāryavāda.
- Contrasts he draws: Śaṅkara (māyā, vivarta, Vivaraṇa/Bhāmatī/Vārttika prasthānas), Bhāskara (bhedābheda, śakti-pariṇāma), Rāmānuja, Madhva, Buddha (śūnya, pratītya-samutpāda), Abrahamic creation ex nihilo.
- He often cites Puruṣottamajī's Prakāśa commentary and "Gosāīṁjī's" additions; keep the attribution as he gives it.
- Recurring kārikās in this series (keep wording consistent wherever they are quoted): *vedāḥ śrīkṛṣṇavākyāni vyāsasūtrāṇi caiva hi | samādhibhāṣā vyāsasya pramāṇaṁ tac catuṣṭayam ||*; *uttaraṁ pūrva-sandeha-vārakaṁ …*; *anantamūrti tad brahma avibhaktaṁ vibhaktimat …*; *tad-icchā-mātratas tasmād …*; *sac-cid-ānanda-rūpeṣu pūrvayor anya-līnatā …*. The series runs Lecture 1 (2026-07-11) … Lecture 12 (2026-10-03), Lecture 13 (2026-10-17), one lecture per recorded weekly session; do not claim in which earlier lecture a kārikā was first discussed unless the speaker says so.

## The speaker's own charts

For four sessions the speaker shared a chart; they are in `sources/charts/` as PDF and PNG (view the PNGs): 2026-07-18 (Lecture 2), 2026-07-25 (Lecture 3), 2026-08-08 (Lecture 5, two pages), 2026-08-15 (Lecture 6, two pages). If your lecture has one, view it before mapping the argument: it gives the correct spelling of terms the ASR garbles, and the structure the speaker is explaining. Your figures may follow the chart's structure (rendered in IAST/English, in the house palette), and where the speaker says "as in the chart" you may write *[refers to the chart]* in the text. The chart text extracted into the header of the `sources/` transcript is a rough retyping; the PNG is authoritative.

## Lectures split into two parts

Lectures 3 and 5 exceed ~80,000 characters and are split into Part 1 and Part 2, each translated by a separate agent in parallel. Fixed coordination so the parts join cleanly:
- Part 1 has exactly 8 numbered sections (`# 1.` … `# 8.`) and exactly 4 figures, numbered Figure 1–4. Part 2 starts at `# 9.` (6–9 sections) and has exactly 4 figures, numbered Figure 5–8.
- Both parts write figures into `build/figsNN/` (filenames start with their figure number, so they never collide), with scripts `build/make_figsNN_part1.py` / `build/make_figsNN_part2.py`, markdown `build/spNN_part1.md` / `build/spNN_part2.md`.
- Subtitle: `"Lecture N, Part 1 — <themes>"` / `"Lecture N, Part 2 — <themes>"`. Each part ends with `# Brief Summary of Part 1` / `# Brief Summary of Part 2` (same three bold-led paragraphs).
- Outputs: `Shastrarth_Prakaran_LectureNN_Part1_EN.{docx,pdf,md}` and `..._Part2_EN.*`.
- The Part 2 agent should read the last ~20 turns of the Part 1 transcript for context only (do not translate them), and open Part 2 without re-introducing the lecture.

## Series conventions settled in Lectures 1–12 (binding for new lectures)

- **Spellings** (outside italic Sanskrit): Mahāprabhuji, Gosāīṁjī, Puruṣottamajī, Brahman, Paramātmā, Bhagavān, Śuddhādvaita, Bhagavadgītā (in citations), Prakāśa.
- **Verse blocks**: end every non-final verse line (Devanagari and IAST) with two trailing spaces (a markdown hard break); the final build also applies `tools/verse_breaks.lua`, so each half-line prints on its own line.
- **Śāstrārtha Prakaraṇa kārikās and Prakāśa sentences** are verified against the Bombay 1943 edition (ed. Harishankar Shastri), archive.org item `jhzf-tattvartha-deepa-nibandha-shastrartha-prakarana-pr`; page images at `https://archive.org/download/jhzf-tattvartha-deepa-nibandha-shastrartha-prakarana-pr/page/n<leaf>.jpg`. The red mūla pages (all 104 kārikās) are leaves 103–109; the Prakāśa commentary runs from leaf 110 (printed commentary page = leaf − 109; the Prakāśa on kārikā 30 is on p. ७१, leaf 180, so kārikā 31 onward follows on leaf 180+). Cached images: `/tmp/claude-0/-home-user-docling/52cfa96e-0437-507f-b456-a63b9493e8f7/scratchpad/conc/pages43/` and `.../conc/*.jpg`. `tools/karika_concordance.md` gives the verified text of kārikās 1–4, 6–12, 23, 26–30, 42, 44, 104 and the Prakāśa on many of them. Read any kārikā or Prakāśa sentence the speaker quotes in the page image itself (not only OCR); if it is legible, give it as printed and cite `(Tattvārthadīpanibandha, Śāstrārtha Prakaraṇa N)` / `(Prakāśa on Śāstrārtha Prakaraṇa N)` by the 1943 number. From kārikā 25 to 30 the 1943 commentary prints second-line + next-first-line units; a block quoting such a unit is cited e.g. `26cd–27ab`. If the speaker's explanation depends on the reading he actually said, keep his words and add `[The 1943 edition reads … .]`. Unverifiable items stay ‹श्रवणाधारित›.
- **Brief Summary**: the Technical Frameworks paragraph ends its citation list with: "Kārikā numbers and the text of the Śāstrārtha Prakaraṇa and its Prakāśa follow the Bombay 1943 edition (ed. Harishankar Shastri)."
- **Build** with `python3 tools/build_final.py outputs NN` from the project root (pandoc + ref.docx + verse breaks + docPr renumbering + LibreOffice PDF + copy to outputs), then check with `python3 tools/lint_md.py build/spNN.md`.
- `tools/condense.py` now keeps continuation lines; no transcript text is lost.
