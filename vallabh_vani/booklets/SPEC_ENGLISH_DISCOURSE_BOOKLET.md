# English discourse booklets — brief and house style

A booklet of this kind prints one lecture of Gosvāmī Śrī Śyām Manoharjī in English (his own English, or a translation of a Hindi lecture) in the house style of the owner's English books. It joins the two exemplars the owner shared: it is **set like the English stuti book** (नलकूबरमणिग्रीवकृतस्तुति, rev. 1: page, type, title page, contents, verses, transliteration, capitals, spelling, sources) and **built like the Hindi pravachan booklet** (प्रतिबिम्बवाद, 2026, rev. 2: one discourse in the speaker's words, divided into sections, his quotations in bold with their sources, an index of quotations). It was first made on 2026-10-23 for the fifteen Kapila Gītā lectures, when the owner asked that every project follow the shared samples and that he receive Word files only.

## Standing rules

- **The speaker's words are kept**, as both exemplars keep them: his sentences, idiom, repetitions, asides, stories and exchanges with students. The edition rules of the series apply unchanged (`vallabh_vani/kapil_gita/SPEC.md`, `vallabh_vani/shastrarth_prakaran/SPEC.md`). The booklet changes the form, never the words.
- **The owner receives the Word file only** (`.docx`): never a PDF or a markdown file. The markdown stays in this repository as the source; the PDF made by the build is for checking the layout.
- **Nothing uncertain is hidden.** The editorial flags of the edition (`‹?›`, `‹ ›`, `‹…›`, `‹श्रवणाधारित›`, `‹the speaker's characterization›`) are not printed; each becomes a **comment in the margin of the Word file**, saying what kind of doubt it is and, for the recording, the time at which its section begins. They are settled by listening, by the printed source, or by the owner, and the comments deleted, before the booklet is printed.

## The booklet, part by part

1. **Title page** (no folio), centred: the work in Devanagari between double daṇḍas, 21 pt (`॥ श्रीकपिलगीता ॥`), and in IAST, 16 pt (`॥ Śrīkapilagītā ॥`); the lecture, 16 pt (`Lecture 1`); its themes and the chapter, 11 pt; the date of the recording; low on the page the speaker, `गोस्वामी श्याम मनोहर` (18 pt) and `Goswāmy Śyāma Manohara` (15 pt), as on the stuti book.
2. **Note on the text** (p. i), heading 16 pt like the stuti book's *Preface*: what the text is (a reading edition of the recording of that date), what editing was done (punctuation, capitalisation, spelling, paragraphs, headings, quoted verses restored to their printed text) and what the comments mark.
3. **Contents** (p. ii), heading `Contents`, 12 pt: the stuti book's three columns, `S. No.` | `Subject` | `P.No.`, one row per section, with *Synopsis* and *Quotations* unnumbered. The page numbers are Word fields (PAGEREF to a bookmark at each heading): Word recomputes them for the fonts of the computer that opens the file (Word asks to update the fields when the file opens: answer *Yes*). Front-matter folios are lower-case roman; the text is numbered from 1.
4. **Synopsis** (p. 1), heading 14 pt like the stuti book's *Summary of verses*: the edition's summary of the lecture's argument, then `Examples and stories:` (a label like the stuti book's `Synopsis:`) and the list of the lecture's examples, stories and analogies. The edition's third paragraph (terms, verses and flags) is the editor's apparatus and is not printed.
5. **The lecture**, from a new page: the numbered sections of the edition, `1. Vyāsa, the Veda and the Birth of the Bhāgavata`, 14 pt, centred, with about 48 pt above, not each on a new page (the stuti book's parts). Body 12 pt on a 20 pt line, justified, first line indented 15 mm, English hyphenation.
   - **Dialogue**: the booklet is the speaker's, so his label is dropped where he simply goes on; another voice is labelled as in the edition (`A student:`, `Listener 2:`, a name), and the speaker's label (`Speaker:`) is printed only where he answers someone. Labels are roman, like the stuti book's `Translation:`.
   - **Verses** he recites: the Devanagari centred, 12 pt, one half-verse per line, kept on the page with its transliteration; the IAST centred, 11 pt, line for line; the source on its own centred line in brackets; then the gloss as a paragraph, in square brackets because it is the editor's rendering unless the speaker gives his own.
   - **Quotations inside the text**: bold, within double quotation marks, the source after them in brackets in regular type (the pravachan booklet's rule): **"sarvaṃ khalv idaṃ brahma"** (Chāndogya Upaniṣad 3.14.1). A passage he reads out without a source (the Subodhinī, given as heard) is set the same way, with its comment, and is not indexed until its source is checked.
   - Sanskrit, Hindi and Gujarati words in the text are roman, not italic (the stuti book uses no italics); a Hindi or Gujarati sentence keeps its English rendering in square brackets.
6. **Quotations** (new page), heading 14 pt: every sourced quotation and verse in order of occurrence, numbered, its opening five words in bold within quotation marks (the closing mark only when the quotation is complete), the source, the page as a PAGEREF field.

Not printed: timestamps (they are in the comments), editorial flags, the closing apparatus paragraph, footnotes, running heads.

## Page and type

The stuti book's measured values (`SPEC_ENGLISH_STUTI_BOOK.md`), written by `tools/make_ref_booklet.py english`:

| Element | Value |
|---|---|
| Page | 5.5 × 8.5 in; margins left 36 pt, right 32 pt, top 40 pt, bottom 47 pt |
| Body | Sanskrit Text 12 pt on a fixed 20 pt line, justified, first line 42.5 pt, 4.3 pt after, hyphenation on |
| Verses | Devanagari 12 pt, IAST 11 pt, centred, 24.3 pt apart, 24 pt after the group |
| Section heading | 14 pt, centred, regular weight, 48 pt above |
| Title page | 21 / 16 pt title, 16 pt lecture, 11 pt themes and date, 18 / 15 pt speaker |
| Note heading, contents heading | 16 pt; 12 pt |
| Contents rows | 12 pt; number at 42.5 pt, subject at 72 pt, page right-aligned at 292 pt; titles wrap before the page column |
| Quotations | heading 14 pt; items 11 pt, page numbers right-aligned at the margin |
| Folio | Tahoma Bold 8 pt, centred; none on the title page, roman in the front matter, Arabic from the synopsis |
| Comments | author "Editor", one per flag |

The Word file names *Sanskrit Text* like the stuti book; it comes with Windows (in the Devanagari supplemental fonts) and must be installed where the booklet is opened, or Word substitutes another font. The check PDF is built with Noto Serif and Noto Serif Devanagari, about 5 % wider, so its pages run a little longer than Word's.

## Conventions of the text

- **Capitals for God**, as in the stuti book (*His, Him, Himself* for God throughout; *You* and *Your* in the prayers, with a few lowercase slips): *He, His, Him, Himself* when the pronoun means Bhagavān in any of His forms (Kṛṣṇa, Viṣṇu, Nārāyaṇa, Rāma, Kapila the avatāra, the vyūhas, Paramātmā, Īśvara, Brahman spoken of as a person), and *You, Your* when someone addresses Him (Kuntī, Prahlāda, Kardama and Devahūti to Kapila, a poet's prayer). Lowercase for the speaker, his students, sages and gods (Vyāsa, Nārada, Brahmā, Śiva), the ācāryas, devotees, the individual self and every example person. When the referent is in doubt, lowercase. `tools/pronoun_tags.py` tags the candidates, agents decide on them (`tools/CAPITALS_BRIEF.md`), and `pronoun_tags.py apply` checks that only the case of those words changed.
- **British spelling** (realise, analyse, visualise, centre, labour, programme, *practise* as a verb), with `tools/british_spelling.py`; misheard words keep the recogniser's spelling.
- **IAST** in the house form of the stuti book: `ṃ` for anusvāra (the series' sources write `ṁ`; the converter changes it), `’` for avagraha joined to the word before (`jajñe’gnir`), Devanagari daṇḍas `।` and `॥` in IAST verse lines, no hyphens inside verses and quotations; Sanskrit words in the running text keep the edition's spelling.
- **Sources** in the stuti book's English forms: (Bhāgavata Purāṇa 3.24.6), (Bhagavadgītā 4.8), (Kaṭha Upaniṣad 1.3.7), (Īśa Upaniṣad 7), (Śaṅkara, Brahmasūtrabhāṣya 1.1.2), (Taittirīya Saṃhitā 6.3.10.5). In running prose the speaker's own names (*Śrīmad Bhāgavata*, *Gītā*) stay.
- Every Devanagari verse line is checked against its IAST letter for letter (`tools/iast.py`). In the Kapila Gītā seven IAST lines taken from e-texts wrote a nasal or a word division where the Devanagari has anusvāra or sandhi (*prasaṅkhyānāya* for प्रसंख्यानाय, *pumān jāta* for पुमाञ्जात); they now follow the Devanagari, and all 327 Devanagari verse lines agree with their IAST.

## Making one

```bash
# the edition, made to the series brief, with the house spelling and capitals
python3 vallabh_vani/booklets/tools/british_spelling.py EDITION.md
python3 vallabh_vani/booklets/tools/pronoun_tags.py tag EDITION.md kgNN_tagged.md kgNN_tags.json   # then the agents
python3 vallabh_vani/booklets/tools/pronoun_tags.py apply EDITION.md kgNN_caps.json EDITION.md
# booklet markdown, then the Word file (and a check PDF in OUT/check/)
python3 vallabh_vani/booklets/tools/lecture_to_booklet.py EDITION.md kgNN.md --series-deva श्रीकपिलगीता --series-iast Śrīkapilagītā
python3 vallabh_vani/booklets/tools/build_booklet.py kgNN.md OUT --name Kapil_Gita_LectureNN_EN
```

The converter reports the sections, the comments by kind, the indexed quotations, any verse whose IAST and Devanagari disagree, and any flag left over (there must be none). `tools/check_booklet_text.py EDITION.md BOOKLET.docx` then compares the booklet with the edition word for word and counts its comments against the flags; it must report no difference. Look at the title page, the contents, a verse page, a dialogue page and the index in the check PDF. Deliver the `.docx`, with a short closing report in the message.

The fifteen Kapila Gītā booklets (2026-10-23) passed both checks: every word of each edition, 1,458 comments for 1,458 flags, 230 sections, 224 quotations indexed; 979 pages in the check build (Noto Serif), fewer in Word with Sanskrit Text.

## For the owner to decide

- The speaker's label in dialogue is *Speaker:*, and other voices are named as the recogniser separated them (*Listener 2*); names, or *Gosvāmījī* for the speaker, can replace them throughout.
- The synopsis is the edition's summary in the editor's words (the pravachan booklet has none; the stuti book opens with its summary): keep, shorten or drop.
- The Subodhinī passages given as heard are set as quotations without a source and are not indexed; once checked against the printed Subodhinī they can take their source and enter the index.
- The title page uses the stuti book's `Goswāmy Śyāma Manohara`; the running text has *Gosvāmī Śrī Śyām Manoharjī*.
