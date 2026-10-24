#!/usr/bin/env python3
"""Check a lecture's markdown against the house format. Usage: lint_md.py build/sp01.md ..."""

import re
import sys
from pathlib import Path

TITLE = 'title: "श्रीकपिलगीता · Kapila Gītā"'
PREFACE = "*Reading edition of a spoken discourse in English by Dr. Dharmendra Jhala on the Kapila Gītā"
LEADS = ["**Content.**", "**Examples and Stories.**", "**Terms, Verses and Flags.**"]
for arg in sys.argv[1:]:
    md = Path(arg)
    text = md.read_text()
    lines = text.split("\n")
    issues = []
    if TITLE not in lines[:4]:
        issues.append("title line differs")
    if not any(l.startswith('subtitle: "Lecture ') for l in lines[:4]):
        issues.append("subtitle missing/odd")
    if not any(l.startswith(PREFACE) for l in lines[:12]):
        issues.append("italic preface missing")
    nums = [int(m.group(1)) for m in re.finditer(r"^# (\d+)\. \S", text, re.M)]
    if nums != list(range(nums[0], nums[0] + len(nums))):
        issues.append(f"section numbers not consecutive/unique: {nums}")
    summ = [
        i
        for i, l in enumerate(lines)
        if re.match(r"^# Brief Summary( of Part \d)?\s*$", l)
    ]
    if len(summ) != 1:
        issues.append(f"Brief Summary headings: {len(summ)}")
    else:
        paras = [l for l in lines[summ[0] + 1 :] if l.strip()]
        if [p.split(" ")[0] + " " + " ".join(p.split(" ")[1:3]) for p in paras][:0]:
            pass
        got = [next((ld for ld in LEADS if p.startswith(ld)), p[:30]) for p in paras]
        if got != LEADS:
            issues.append(f"Brief Summary paragraphs: {got}")
    body = [l for l in lines if not l.startswith(">")]
    bullets = [
        l[:50]
        for l in body
        if re.match(r"^\s*([-*+]|\d+\.)\s+\S", l) and not l.startswith("# ")
    ]
    if bullets:
        issues.append(f"{len(bullets)} list lines, e.g. {bullets[:2]}")
    figs = re.findall(
        r"^!\[Figure (\d+) · [^\]]+\]\((figs\d\d/[^)]+\.png)\)\{width=6\.2in\}\s*$",
        text,
        re.M,
    )
    allfig = re.findall(r"^!\[", text, re.M)
    fn = [int(n) for n, _ in figs]
    if fn and fn != list(range(fn[0], fn[0] + len(fn))):
        issues.append(f"figure numbers: {fn}")
    missing = [p for _, p in figs if not (md.parent / p).exists()]
    if missing:
        issues.append(f"missing figure files: {missing}")
    flags = {
        k: text.count(k) for k in ("‹श्रवणाधारित›", "‹?›", "‹…›", "characterization›")
    }
    words = len(re.sub(r"[#>*\[\]()!]", " ", text).split())
    print(
        f"{md.name}: sections {nums[0]}–{nums[-1]} ({len(nums)}), figures {len(fn)}, ~{words} words, flags {flags}"
        + ("" if not issues else "\n    ISSUES: " + " | ".join(issues))
    )
