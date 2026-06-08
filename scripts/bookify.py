#!/usr/bin/env python3
"""Restructure the OCR'd Sarvam Markdown into a cleanly aligned book.

Structural stages only (no network): parse -> classify headings -> footnotes to
per-section endnotes -> litany tables to lists -> extract image -> dedupe running
footer -> strip chunk markers -> verses as line blocks -> build hierarchy
(book/part/work/adhyaya/pada/adhikarana) -> linked TOC -> emit clean Markdown.

Outputs the book Markdown plus side-car reports (heading decisions, footnotes,
structure) so every heuristic decision is auditable.

Usage:
    uv run python scripts/bookify.py INPUT.md OUTPUT.md [--work-dir DIR]
"""

from __future__ import annotations

import argparse
import base64
import json
import re
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path

# ---------------------------------------------------------------------------
# Patterns (calibrated to the actual file)
# ---------------------------------------------------------------------------
CHUNK_RE = re.compile(r"^<!--\s*chunk\s+\d+\s*\(pages from \d+\)\s*-->\s*$")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
FOOTNOTE_RE = re.compile(r"^\[\^\d+\]:\s*(.*)$")
IMAGE_RE = re.compile(r"^!\[[^\]]*\]\(data:image/(\w+);base64,([^)]+)\)\s*$")
OCR_CAPTION_RE = re.compile(r"^\*This image contains.*\*\s*$")
DANDA = r"[।॥]"
# A title wrapped in dandas: ## ।। X ।।  or  ## ॥ X ॥
DANDA_TITLE_RE = re.compile(rf"^{DANDA}{DANDA}?\s*(.+?)\s*{DANDA}{DANDA}?$")
# Heading text that is really a verse/sutra line (ends with a verse number)
ENDS_VERSE_RE = re.compile(rf"{DANDA}+\s*[\d०-९]+\s*{DANDA}*\s*$")
SUTRA_REF_RE = re.compile(r"\([\d०-९]+\s*[।|॥]\s*[\d०-९]+\s*[।|॥]\s*[\d०-९]+\)")
LEAD_DEVA_NUM_RE = re.compile(r"^([०-९]+)\s*(.*)$")

# Non-danda lines that are nevertheless real titles.
REAL_TITLE_ALLOW = {
    "पुष्टिस्वाध्याय समयतालिका",
    "तत्त्वार्थदीपनिबन्धे",
    "TATVARTHDIP NIBANDH",
    "ANUBHASYA",
}
LATIN_TITLE_MAP = {
    "ANUBHASYA": "श्रीमद्ब्रह्मसूत्राणुभाष्यम्",
    "TATVARTHDIP NIBANDH": "तत्त्वार्थदीपनिबन्ध",
}

# Part II structural end-markers
WORK_END_RE = re.compile(r"इति\s.*(समाप्त|सम्पूर्ण)")
# Match both "...अधिकरणम्॥N॥" and sandhi-fused "...जिज्ञासाधिकरणम्॥1॥" by keying
# on the suffix "धिकरणम्" followed by a number (avoids प्रकरणम् false-positives).
ADHIKARANA_END_RE = re.compile(rf"धिकरणम्\s*{DANDA}*\s*[\d०-९]+\s*{DANDA}*")
ANUBHASYA_HEAD = "ANUBHASYA"

# Sanskrit ordinals -> number, for parsing "प्रथमाध्याये द्वितीयपादे"
ORDINAL = {"प्रथम": 1, "द्वितीय": 2, "तृतीय": 3, "चतुर्थ": 4}
ADHYAYA_NUM_RE = re.compile(r"(प्रथम|द्वितीय|तृतीय|चतुर्थ)\S*ध्याय")
PADA_NUM_RE = re.compile(r"(प्रथम|द्वितीय|तृतीय|चतुर्थ)\S*पाद")
ADHYAYA_NAMES = {1: "प्रथमोऽध्यायः", 2: "द्वितीयोऽध्यायः",
                 3: "तृतीयोऽध्यायः", 4: "चतुर्थोऽध्यायः"}
PADA_NAMES = {1: "प्रथमः पादः", 2: "द्वितीयः पादः",
              3: "तृतीयः पादः", 4: "चतुर्थः पादः"}


@dataclass
class Block:
    kind: str            # heading|para|table|footnote_def|image|hr|comment
    lines: list[str]
    chunk_id: int = 0
    level: int = 0       # for headings
    text: str = ""       # single-line text for headings
    role: str = ""       # book|part|work|adhyaya|pada|adhikarana
    anchor: str = ""
    section_id: int = -1  # which work/section this block belongs to
    meta: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Stage 1: parse
# ---------------------------------------------------------------------------
def parse(raw: str) -> list[Block]:
    lines = raw.split("\n")
    blocks: list[Block] = []
    chunk = 0
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        if CHUNK_RE.match(line):
            m = re.search(r"chunk\s+(\d+)", line)
            chunk = int(m.group(1)) if m else chunk
            blocks.append(Block("comment", [line], chunk))
            i += 1
            continue
        if not line.strip():
            i += 1
            continue
        if line.strip() == "---":
            blocks.append(Block("hr", [line], chunk))
            i += 1
            continue
        hm = HEADING_RE.match(line)
        if hm:
            blocks.append(Block("heading", [line], chunk,
                                level=len(hm.group(1)), text=hm.group(2)))
            i += 1
            continue
        if IMAGE_RE.match(line):
            blocks.append(Block("image", [line], chunk))
            i += 1
            continue
        fm = FOOTNOTE_RE.match(line)
        if fm:
            buf = [line]
            i += 1
            while i < n and lines[i].strip() and not HEADING_RE.match(lines[i]) \
                    and not FOOTNOTE_RE.match(lines[i]) and lines[i].strip() != "---":
                buf.append(lines[i])
                i += 1
            blocks.append(Block("footnote_def", buf, chunk))
            continue
        if line.lstrip().startswith("<table"):
            buf = [line]
            i += 1
            while i < n and "</table>" not in lines[i - 1]:
                buf.append(lines[i])
                i += 1
            blocks.append(Block("table", buf, chunk))
            continue
        # paragraph: gather consecutive non-blank, non-special lines
        buf = [line]
        i += 1
        while i < n and lines[i].strip() and not CHUNK_RE.match(lines[i]) \
                and not HEADING_RE.match(lines[i]) and lines[i].strip() != "---" \
                and not FOOTNOTE_RE.match(lines[i]) \
                and not lines[i].lstrip().startswith("<table"):
            buf.append(lines[i])
            i += 1
        blocks.append(Block("para", buf, chunk))
    return blocks


# ---------------------------------------------------------------------------
# Stage 2: classify headings
# ---------------------------------------------------------------------------
def classify_headings(blocks: list[Block], log: dict) -> None:
    decisions = []
    for b in blocks:
        if b.kind != "heading":
            continue
        text = b.text.strip()
        bare = text
        dm = DANDA_TITLE_RE.match(text)
        if dm:
            bare = dm.group(1).strip()
        is_real = False
        reason = ""
        if text in REAL_TITLE_ALLOW or bare in REAL_TITLE_ALLOW:
            is_real, reason = True, "allow-list"
        elif SUTRA_REF_RE.search(text) or ENDS_VERSE_RE.search(text):
            is_real, reason = False, "verse/sutra-line"
        elif dm and bare and not ENDS_VERSE_RE.search(bare):
            is_real, reason = True, "danda-wrapped"
        else:
            is_real, reason = False, "ambiguous->demote"
        b.meta["is_real_title"] = is_real
        b.meta["title"] = LATIN_TITLE_MAP.get(bare, bare)
        decisions.append({"text": text, "real": is_real, "reason": reason})
        if not is_real:
            # demote to body paragraph (keep the verse text)
            b.kind = "para"
            b.lines = [text]
    log["heading_decisions"] = decisions
    log["real_titles"] = [d["text"] for d in decisions if d["real"]]


# ---------------------------------------------------------------------------
# Stage 3: assign sections (by real title) + footnotes -> per-section endnotes
# ---------------------------------------------------------------------------
def assign_sections_and_footnotes(blocks: list[Block], log: dict) -> dict:
    section_id = -1
    endnotes: dict[int, list[tuple[str, str]]] = {}
    report = []
    for b in blocks:
        if b.kind == "heading" and b.meta.get("is_real_title"):
            section_id += 1
            b.section_id = section_id
            endnotes.setdefault(section_id, [])
        else:
            b.section_id = section_id
        if b.kind == "footnote_def":
            body = FOOTNOTE_RE.match(b.lines[0]).group(1)
            if len(b.lines) > 1:
                body = body + " " + " ".join(l.strip() for l in b.lines[1:])
            lm = LEAD_DEVA_NUM_RE.match(body.strip())
            num = lm.group(1) if lm else ""
            txt = lm.group(2).strip() if lm else body.strip()
            endnotes.setdefault(section_id, []).append((num, txt))
            report.append({"section": section_id, "num": num, "text": txt[:60]})
            b.kind = "drop"  # remove from inline flow
    log["footnotes"] = report
    return endnotes


# ---------------------------------------------------------------------------
# Stage 4: litany tables -> markdown lists
# ---------------------------------------------------------------------------
class _Cells(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cells: list[str] = []
        self._in = False
        self._buf = ""

    def handle_starttag(self, tag, attrs):
        if tag == "td":
            self._in, self._buf = True, ""

    def handle_endtag(self, tag):
        if tag == "td":
            self.cells.append(self._buf.strip())
            self._in = False

    def handle_data(self, data):
        if self._in:
            self._buf += data


def tables_to_lists(blocks: list[Block], log: dict) -> None:
    count = 0
    mojibake = 0
    for b in blocks:
        if b.kind != "table":
            continue
        p = _Cells()
        p.feed("\n".join(b.lines))
        items = []
        for c in p.cells:
            if not c:
                continue
            if "�" in c:
                mojibake += 1
            items.append(f"- {c}")
        b.kind = "para"
        b.lines = items if items else ["- (खाली तालिका)"]
        b.meta["from_table"] = True
        count += 1
    log["tables_converted"] = count
    log["table_mojibake_cells"] = mojibake


# ---------------------------------------------------------------------------
# Stage 5: extract image
# ---------------------------------------------------------------------------
def extract_images(blocks: list[Block], assets: Path, log: dict) -> None:
    assets.mkdir(parents=True, exist_ok=True)
    n = 0
    for idx, b in enumerate(blocks):
        if b.kind != "image":
            continue
        m = IMAGE_RE.match(b.lines[0])
        if not m:
            b.kind = "drop"
            continue
        ext, data = m.group(1), m.group(2)
        n += 1
        out = assets / f"img_{n}.{ext}"
        try:
            out.write_bytes(base64.b64decode(data))
            b.lines = [f"![]({out.relative_to(assets.parent)})"]
            b.kind = "para"
        except Exception:
            b.kind = "drop"
    # drop English OCR captions
    for b in blocks:
        if b.kind == "para" and len(b.lines) == 1 and OCR_CAPTION_RE.match(b.lines[0]):
            b.kind = "drop"
    log["images_extracted"] = n


# ---------------------------------------------------------------------------
# Stage 6: dedupe running footer + strip chunk markers/hr
# ---------------------------------------------------------------------------
def cleanup(blocks: list[Block], log: dict) -> None:
    removed = 0
    prev_text = None
    for b in blocks:
        if b.kind == "para":
            t = "\n".join(b.lines).strip()
            if t == prev_text:  # adjacent exact duplicate
                b.kind = "drop"
                removed += 1
                continue
            prev_text = t
        elif b.kind not in ("comment", "hr", "drop"):
            prev_text = None
    # drop chunk-marker comments and any hr (chunk glue)
    for b in blocks:
        if b.kind == "comment" and CHUNK_RE.match(b.lines[0]):
            b.kind = "drop"
        if b.kind == "hr":
            b.kind = "drop"
    log["dup_lines_removed"] = removed


# ---------------------------------------------------------------------------
# Stage 7: build hierarchy (book/part/work/adhyaya/pada/adhikarana)
# ---------------------------------------------------------------------------
def build_hierarchy(blocks: list[Block], title: str, author: str, log: dict) -> list[Block]:
    # find Part II start (the ANUBHASYA heading)
    part2_idx = None
    for i, b in enumerate(blocks):
        if b.kind == "heading" and b.meta.get("title") == LATIN_TITLE_MAP[ANUBHASYA_HEAD]:
            part2_idx = i
            break

    # assign levels: every real title currently level 2 (##); refine in Part II
    for b in blocks:
        if b.kind == "heading" and b.meta.get("is_real_title"):
            b.role = "work"
            b.level = 2
            b.text = b.meta["title"]
            b.lines = [f"## {b.text}"]

    # Part II: reconstruct adhyaya/pada from the adhikarana-end markers, which
    # embed their chapter+section (e.g. "...प्रथमाध्याये द्वितीयपादे ...अधिकरणम्॥3॥").
    # Each marker ENDS an adhikarana, so a new pada/adhyaya actually begins right
    # after the *previous* marker -> we back-fill headings at those positions.
    structure_report = {"adhyaya_headings": [], "pada_headings": [], "adhikarana_ends": 0}
    pada_inserts: dict[int, list[Block]] = {}  # block-index -> headings to insert before
    if part2_idx is not None:
        raw_markers = []  # (block_index, adhyaya|None, pada|None)
        for i in range(part2_idx, len(blocks)):
            b = blocks[i]
            if b.kind != "para":
                continue
            for line in b.lines:
                if not ADHIKARANA_END_RE.search(line):
                    continue
                am = ADHYAYA_NUM_RE.search(line)
                pm = PADA_NUM_RE.search(line)
                # a real end-marker either opens with इति or names its adhyaya/pada
                if not (am or pm or line.strip().startswith("इति")):
                    continue
                structure_report["adhikarana_ends"] += 1
                raw_markers.append((i, ORDINAL[am.group(1)] if am else None,
                                    ORDINAL[pm.group(1)] if pm else None))
                break

        # forward-fill missing adh/pada, then enforce monotonic (adh,pada) so
        # stray quoted ordinals can't flip the section backwards.
        markers = []
        cur_adh, cur_pada = 1, 1
        last = (0, 0)
        for (mi, a, p) in raw_markers:
            if a:
                cur_adh = a
            if p:
                cur_pada = p
            if (cur_adh, cur_pada) >= last:
                markers.append((mi, cur_adh, cur_pada))
                last = (cur_adh, cur_pada)

        prev_adh = prev_pada = None
        # first pada/adhyaya heading goes right after the Part II heading
        first_pos = part2_idx + 1
        for k, (mi, adh, pada) in enumerate(markers):
            pos = (markers[k - 1][0] + 1) if k > 0 else first_pos
            inserts = []
            if adh != prev_adh:
                h = Block("heading", [f"## {ADHYAYA_NAMES[adh]}"], level=2,
                          text=ADHYAYA_NAMES[adh], role="adhyaya")
                inserts.append(h)
                structure_report["adhyaya_headings"].append(ADHYAYA_NAMES[adh])
                prev_pada = None  # force pada heading at chapter start
            if pada != prev_pada:
                h = Block("heading", [f"### {PADA_NAMES[pada]}"], level=3,
                          text=PADA_NAMES[pada], role="pada")
                inserts.append(h)
                structure_report["pada_headings"].append(
                    f"{ADHYAYA_NAMES[adh]} / {PADA_NAMES[pada]}")
            if inserts:
                pada_inserts.setdefault(pos, []).extend(inserts)
            prev_adh, prev_pada = adh, pada
    log["structure"] = structure_report

    # assign Part II works (तत्त्वार्थदीपनिबन्धे etc.) and the ANUBHASYA itself
    # remain as ## works; the synthesized adhyaya headings are also ##.

    # Insert top-level book + part headings, plus back-filled Part II headings
    out: list[Block] = []
    book = Block("heading", [f"# {title}"], level=1, text=title, role="book")
    sub = Block("para", [f"*{author}*"])
    part1 = Block("heading", ["# भाग १ — स्तोत्र एवं प्रकरण-ग्रन्थसंग्रह"], level=1,
                  text="भाग १ — स्तोत्र एवं प्रकरण-ग्रन्थसंग्रह", role="part")
    out.extend([book, sub, part1])
    for i, b in enumerate(blocks):
        if i in pada_inserts:
            out.extend(pada_inserts[i])
        if part2_idx is not None and i == part2_idx:
            part2 = Block("heading", ["# भाग २ — श्रीमद्ब्रह्मसूत्राणुभाष्यम्"], level=1,
                          text="भाग २ — श्रीमद्ब्रह्मसूत्राणुभाष्यम्", role="part")
            out.append(part2)
            b.kind = "drop"  # the ANUBHASYA heading replaced by the part heading
        out.append(b)
    return [b for b in out if b.kind != "drop"]


# ---------------------------------------------------------------------------
# Stage 8: (no inline TOC / anchors) — pandoc generates a page-numbered,
# bookmarked TOC at build time, which keeps the Markdown clean for GitHub and
# avoids a duplicate table of contents in the rendered book.
# ---------------------------------------------------------------------------
def add_anchors_and_toc(blocks: list[Block]) -> list[Block]:
    return blocks


# ---------------------------------------------------------------------------
# Stage 9: verses -> line blocks  +  emit
# ---------------------------------------------------------------------------
def is_verse(b: Block) -> bool:
    if b.kind != "para" or b.meta.get("from_table"):
        return False
    joined = "\n".join(b.lines)
    return bool(re.search(rf"{DANDA}+\s*[\d०-९]+\s*{DANDA}+", joined))


def emit(blocks: list[Block], endnotes: dict, title: str) -> str:
    out: list[str] = []
    # group blocks by section to append endnotes at each section end
    cur_section = -1

    def flush_endnotes(sid: int):
        notes = endnotes.get(sid)
        if notes:
            out.append("")
            out.append("#### टिप्पण्यः")
            out.append("")
            for num, txt in notes:
                label = num if num else "॰"
                out.append(f"{label}. {txt}")
            out.append("")

    n = len(blocks)
    for i, b in enumerate(blocks):
        # detect section change to flush endnotes of previous section
        if b.kind == "heading" and b.role == "work":
            if cur_section != -1:
                flush_endnotes(cur_section)
            cur_section = b.section_id
        if b.kind == "heading":
            out.append("")
            out.extend(b.lines)
            out.append("")
        elif b.kind == "para":
            if is_verse(b):
                for ln in b.lines:
                    out.append(f"| {ln.strip()}")
                out.append("")
            else:
                out.extend(b.lines)
                out.append("")
    flush_endnotes(cur_section)
    text = "\n".join(out)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--title", default="षोडशग्रन्थ व अणुभाष्य संग्रह")
    ap.add_argument("--author", default="श्रीवल्लभाचार्य")
    ap.add_argument("--work-dir", default="/tmp/bookify_work")
    args = ap.parse_args()

    work = Path(args.work_dir)
    work.mkdir(parents=True, exist_ok=True)
    log: dict = {}

    raw = Path(args.input).read_text(encoding="utf-8")
    blocks = parse(raw)
    classify_headings(blocks, log)
    endnotes = assign_sections_and_footnotes(blocks, log)
    tables_to_lists(blocks, log)
    extract_images(blocks, work / "assets", log)
    cleanup(blocks, log)
    blocks = [b for b in blocks if b.kind != "drop"]
    blocks = build_hierarchy(blocks, args.title, args.author, log)
    blocks = add_anchors_and_toc(blocks)
    md = emit(blocks, endnotes, args.title)

    Path(args.output).write_text(md, encoding="utf-8")
    (work / "bookify_report.json").write_text(
        json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"WROTE {args.output} ({len(md)/1e6:.2f} MB)")
    print(f"real titles: {len(log['real_titles'])}  "
          f"footnotes: {len(log['footnotes'])}  "
          f"tables->lists: {log['tables_converted']}  "
          f"images: {log['images_extracted']}  "
          f"dup-lines removed: {log['dup_lines_removed']}")
    print(f"Part II: adhyaya-headings={len(log['structure']['adhyaya_headings'])} "
          f"pada-headings={len(log['structure']['pada_headings'])} "
          f"adhikarana-ends={log['structure']['adhikarana_ends']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
