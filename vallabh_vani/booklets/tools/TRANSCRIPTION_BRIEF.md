# Transcribing pages of an exemplar booklet (brief for one agent per ten pages)

Folder: `PRB`, prepared with `pdftoppm -r 300 -png` (hi300/), `tesseract … -l hin+eng --psm 6` (ocr/), `pdftotext -layout` per page (layer/), and the tools of `vallabh_vani/booklets/tools/` (tools/).

Written for प्रतिबिम्बवाद (2026, rev. 2), a discourse typed in Word and printed to PDF; adapt the page-specific notes for another booklet. Its text is Hindi in the speaker's own Vraj- and Gujarati-coloured idiom, with English words written in Devanagari, English sentences in Latin letters, and Sanskrit quotations. We need an **exact diplomatic transcription** in Unicode: the PDF's own text layer is broken, so this transcription will become the reference copy that later editors learn the house style from. Exactness matters more than speed.

## Inputs for each page N (two-digit file numbers: p-05, p-17, …)

- `PRB/hi300/p-NN.png`: the page image at 300 dpi. **This is the authority.** Read it with the Read tool. To read a line closely, run `python3 PRB/tools/zoom.py N TOP BOTTOM` (points from the top of the 612-pt page; body lines are 22 pt apart, the first starts at 54) and Read the PNG it prints.
- `PRB/ocr/p-NN.txt`: Tesseract OCR. A useful draft, with many errors: English garbage where conjuncts were hard ("Yall" for रह्यो, "catch" for क्योंके), है where the print has हे, missing viramas, wrong vowel signs, invisible joiners (U+200C/U+200D: remove them all), line breaks.
- `PRB/layer/p-NN.txt`: the PDF's own text layer. Every character it contains is correct and in order, but it silently drops conjunct glyphs (प्र, क्य, च्छ, ह्य …), the short-i sign ि, the sign ैं, some ी, and it writes ई as इ and ऐ as ए+े, and inserts spaces. Use it to confirm vowel signs, हे vs है, punctuation, digits and English.

## What to write

One file, `PRB/trans/pFIRST-LAST.md` (e.g. `p10-20.md`), covering your pages in order.

- Before each page's text, a marker on its own line: `<!-- p.N -->`. If the page begins in the middle of a paragraph (its first line is not indented and the previous page did not end the paragraph; look at the previous page image if needed), write `<!-- p.N cont -->` instead, with **no blank line before or after it**, so the paragraph continues across the marker.
- One paragraph per line (join the printed lines; no hard wraps). A blank line between paragraphs. A printed line-end hyphen that belongs to a compound stays, with no space after it (ज्ञान-भक्ति-तारतम्य).
- Section headings: `# खण्ड N — title` exactly as printed (one line, even if printed on two).
- Bold exactly where printed: `**…**` (mostly Sanskrit quotations and a few terms). Underline is not marked.
- Quotation marks: write straight `"` and `'` whatever the print shows.
- Everything else **exactly as printed**: spelling, the speaker's dialect forms (हे, हें, हतो, हती, हते, मोकु, आपकु, कियो, भयो, रह्यो, सु, कु, बखत, अपन् …; never "correct" them to standard Hindi), the editor's inconsistencies (यहाँ and यहां both occur; हूँ and हूं), English words in Devanagari with or without the final virama as printed (ऑर्डर्, टेबल), nukta, chandrabindu versus anusvāra (zoom in to decide), Devanagari versus Arabic digits, punctuation (Hindi sentences end with a Latin full stop `.`; `।`/`॥` and the typed pair `।।` only in Sanskrit — keep whichever is printed), dashes (— em dash), dots (`...`, `....`: count them), the English as printed including its errors.
- Write ऐ as the single letter ऐ. Do not type invisible joiners (ZWNJ/ZWJ); a visible virama inside a word such as लोगन्‌कु is restored afterwards by `glyph_check.py --fix-zwnj`, so simply write लोगन्कु.
- Verse lines (the śloka pages, the badhāī pada lines if they are one block) as a line block, one printed line per line, each starting with `| `. Prose stays prose.
- The two chart pages: on p.17 write `![](charts/chart_1.png)` and, below it, an HTML comment `<!-- chart_1: … -->` containing the chart's labels as an indented outline (keep the letters a–f and their legend). On p.18 do the same for the tree at the top with `![](charts/chart_2.png)` and `<!-- chart_2: … -->`, then the text.
- Index pages (उद्धृत वचन): heading `## उद्धृत वचन`, then one item per line exactly as printed, e.g. `१. **"प्रकाशाश्रयवद्वा तेजस्त्वात्॥"** (ब्र.सू.३.२.२८) - २७` (bold where printed; an empty item stays empty: `५.`).
- If, after zooming, a reading is still uncertain, keep your best reading and add `<!-- ? note -->` right after it. Do not add any other notes.

## Check before you finish

Run `python3 PRB/tools/check_layer.py PRB/trans/pFIRST-LAST.md`. It aligns each page with the text layer and lists **A** (a layer character missing from your text) and **B** (a Latin letter, digit or punctuation mark in your text that the layer lacks). Each one is almost always a transcription error: zoom in, fix, rerun, until the report is empty or every remaining item is one you have verified in the image (for example the layer's own ई→इ). Then run `python3 PRB/tools/glyph_check.py PDF YOURFILE.md FONT_patched.ttf` (the font from `pdf_fonts.py --patch`): every word is shaped with the PDF's own font and compared with the glyphs the page draws. Differences it pairs as mark-order moves are not errors; every other difference is, until the image shows otherwise. Then read your file once from top to bottom against the images.

## Reply

Two or three lines: pages done, the remaining checker items and why they stand, and any `<!-- ? -->` notes. Do not paste the transcription.
