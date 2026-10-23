# Kapila Gītā — verbatim English editions of the lectures

You prepare the reading edition of one lecture by Gosvāmī Śrī Śyām Manoharjī on the Kapila Gītā (Śrīmad Bhāgavata, Skandha 3, adhyāyas 25–33: Kapila's teaching to Devahūti). The lectures were delivered **in English** (Indian English, with Sanskrit, Hindi and Gujarati terms, verses and asides), so this is not a translation: it is the speaker's own English, transcribed by ASR, set out as a document. Output is publication quality, reviewed by scholars. Series: Lecture 1 = 2022-10-30 … Lecture 14 = 2023-02-26; Lecture 15 = 2023-03-05 (Revision).

## Standing rule (non-negotiable): keep the speaker's words

The owner of this project asked that the speaker's vocabulary — the words he actually uses — be kept, all of it. So:

- Keep his sentences as he spoke them: his word choices, Indian-English idiom, repetitions for emphasis, asides, jokes, stories, questions to the audience, and the students' questions and answers. Do not paraphrase, do not "improve" grammar, do not substitute synonyms, do not shorten, do not reorder, do not smooth away digressions.
- You may add punctuation, sentence and paragraph breaks, section headings, and capitalisation. You may drop only ASR noise and pure disfluencies: stammered syllables, a word restarted and immediately completed, "uh/um". A phrase he repeats whole stays.
- Where the ASR has plainly mis-heard an English word, restore it only when the context makes the word certain; otherwise keep the ASR word and flag it ‹?›. Never guess silently.
- Sanskrit, Hindi and Gujarati terms he uses stay as his terms, spelled consistently in IAST in italics on the pattern of the series (*ātmā*, *prakṛti*, *puruṣa*, *mahat*, *ahaṅkāra*, *jīva*, *bhakti*, *vairāgya*, *saṁsāra*, *māyā*, *sattva/rajas/tamas*, *satsaṅga*, *sevā*, *līlā*, *svarūpa*). Tradition-internal terms are not glossed (Mahāprabhuji, Gosāīṁjī, Ṭhākurjī, Puṣṭimārga, sevā, bhāva…). A Hindi or Gujarati sentence is transliterated in italics with a bracketed English gloss.
- Verses: when he recites a Bhāgavata verse (or part of one) whose text you can verify against a reliable e-text (GRETIL, vedabase/bhagavata e-texts), restore it to the received reading in a verse block and cite it (Śrīmad Bhāgavata 3.26.3 etc.); what you cannot verify stays ‹श्रवणाधारित›. Watch for ASR keyterm hallucinations (the recogniser was given a list of names such as Kapila, Devahūti, Kardama, Mahāprabhuji, Vallabhācārya, Śaṅkarācārya, Subodhinī — an isolated, out-of-context occurrence of one of these is suspect).
- Diarization: the main speaker is Goswamiji; label him **Speaker:**. Others are **A student:** / **Listener 2:** or a name if spoken. The recogniser sometimes folds a short question from the floor into the speaker's turn; split it out when it is plainly a question from the audience. Drop lone keyterm words wrongly assigned to listeners.
- Sensitive remarks (about another religion, politics, named persons): keep as spoken; add ‹the speaker's characterization›. Never reproduce film-song lyrics; name or describe the song.

## Editorial flags

`‹ ›` conjectural restoration · `‹?›` uncertain reading (right after the word) · `‹…›` inaudible/unrecoverable · `‹श्रवणाधारित›` text given as heard, pending verification against print.

## Markdown structure (pandoc source)

```markdown
---
title: "श्रीकपिलगीता · Kapila Gītā"
subtitle: "Lecture N — <three or four main themes>"
---

*Reading edition of a spoken discourse in English by Gosvāmī Śrī Śyām Manoharjī on the Kapila Gītā (Śrīmad Bhāgavata, Skandha 3, adhyāyas 25–33), prepared from an ASR transcript of the recording of <date>. The speaker's own words, vocabulary, repetitions, asides, humour, code-switching and exchanges with students are kept; editing is limited to punctuation, paragraphing, section headings and the restoration of quoted verses to their received text. Editorial flags: ‹ › conjectural restoration of a garbled reading; ‹?› uncertain reading; ‹…› inaudible or unrecoverable passage; ‹श्रवणाधारित› text given as heard, pending verification against a printed edition.*

# 1. Section Title

*[00:00:00]*

**Speaker:** …
```

- Numbered H1 sections, `# N. Title`, about 10–16 per lecture at real turns of the argument; titles name the point and, where there is one, the memorable example. The first line under each heading is the start timestamp of that section in italics, `*[hh:mm:ss]*`, taken from the transcript.
- Body is flowing prose in the speaker's words. No bullets, no lists, minimal bold. Dialogue labels in bold.
- Verse blocks exactly as in the series:

```markdown
> देवनागरी पङ्क्ति १ ।  
> देवनागरी पङ्क्ति २ ॥  
>
> *iast line one |*  
> *iast line two ||* (Śrīmad Bhāgavata 3.26.3)
>
> [English gloss — the speaker's own rendering if he gives one, in his words.]
```

(two trailing spaces end every non-final verse line.)

- No figures.
- Final unnumbered `# Brief Summary` with exactly three bold-led paragraphs: `**Content.**` (the lecture's argument in prose, in the editor's words), `**Examples and Stories.**` (every example, story and analogy, semicolon-separated), `**Terms, Verses and Flags.**` (Sanskrit terms as he uses them, verses with references, flags carried over).

## Workflow

1. Read the whole condensed transcript `build/KNN_<date>_turns.txt` (one line per turn: `S:` = Goswamiji, `L1:`… = others, each with its start timestamp) in overlapping chunks before writing. The per-segment source with timestamps is `sources/KNN_<date>.txt`.
2. Map the argument, choose section breaks.
3. Write `build/kgNN.md` in chunks via `cat >> file << 'CHUNK_n'`; after every append check `grep -c "^# N\."` for each new heading (exactly 1); cut any duplicate tail with Python.
4. Build and verify from the project root (/tmp/claude-0/-home-user-docling/52cfa96e-0437-507f-b456-a63b9493e8f7/scratchpad/kapil_gita): `python3 tools/build_final.py outputs NN` then `python3 tools/lint_md.py build/kgNN.md`. View the title page (`pdftoppm -jpeg -r 60 -f 1 -l 1 …`) and one interior page with a verse. Outputs: `outputs/Kapil_Gita_LectureNN_EN.{docx,pdf,md}`.

The edition must be COMPLETE: the whole session, start to end, every sentence of content. Expect roughly 10,000–18,000 words.

## Closing report

Two or three short prose paragraphs, no lists: page count, section count; which verses were restored (with references); which items remain ‹श्रवणाधारित› or ‹?›; any passage where the ASR was too garbled to recover. No offers or questions at the end.
