#!/usr/bin/env python3
"""Conservative OCR proofreading pass over the structured book via Sarvam sarvam-m.

Only body text (prose paragraphs, verse lines, litany items, endnotes) is sent;
headings, the TOC, anchors and markup are never touched. Protected tokens (verse
numbers ।।N।।/॥N॥, sutra refs, manuscript sigla) are masked with placeholders so
the model cannot alter them. Every unit is validated (placeholders intact, length
within bounds, output in Devanagari, no injected markup) and reverts to the
original on any failure. All accepted edits are written to an auditable changelog.

Usage:
    SARVAM_API_KEY=... uv run python scripts/bookify_proofread.py IN.md OUT.md \
        [--lines A:B] [--concurrency 4] [--work-dir DIR]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path

from sarvamai import SarvamAI

DEFAULT_MODEL = "sarvam-105b"
DANDA = r"[।॥]"
PROTECT_RES = [
    re.compile(rf"{DANDA}+\s*[\d०-९]+\s*{DANDA}+"),     # verse numbers ।।N।।
    re.compile(r"\([\d०-९]+\s*[।|॥]\s*[\d०-९]+\s*[।|॥]\s*[\d०-९]+\)"),  # sutra refs
    re.compile(r"[क-ह][\d०-९]/[क-ह][\d०-९]"),           # manuscript sigla ख१/ग१
    re.compile(r"\{#sec-\d+\}"),                          # heading anchors (safety)
    re.compile(r"[०-९]+"),                                # any remaining Devanagari
    #                                                       digits (word indices) —
    #                                                       never let the model touch
    #                                                       numbers. ASCII placeholder
    #                                                       digits are unaffected.
]
DEVA_RE = re.compile(r"[ऀ-ॿ]")
BAD_OUT_RE = re.compile(r"[#<>]|!\[|\[\^|```")           # injected markup markers

SYSTEM_PROMPT = (
    "You are a meticulous proofreader of classical Devanagari (Sanskrit and Hindi) "
    "Vaiṣṇava scripture digitised by OCR. Fix ONLY unambiguous OCR errors: broken "
    "or wrong conjuncts, swapped/garbled characters, obvious mātrā mistakes, and "
    "clearly wrong word splits or joins. NEVER paraphrase, translate, modernise, "
    "reorder, summarise, expand, or change meaning. Preserve every placeholder of "
    "the form §§T<number>§§ EXACTLY as given. Preserve all punctuation including "
    "daṇḍas. If a passage is unclear, leave it UNCHANGED. Reply with ONLY the "
    "corrected text — no notes, no explanation, no quotes."
)


@dataclass
class Unit:
    idx: int          # position in the units list
    line_start: int   # source line index (for changelog)
    prefix: str       # markup to re-attach ("| ", "- ", "3. ", or "")
    content: str      # editable text (markup stripped)
    editable: bool
    masked: str = ""
    tokens: list[str] = field(default_factory=list)
    new_content: str = ""
    changed: bool = False
    status: str = "unchanged"


def mask(text: str) -> tuple[str, list[str]]:
    tokens: list[str] = []

    def repl(m):
        tokens.append(m.group(0))
        return f"§§T{len(tokens) - 1}§§"

    masked = text
    for rgx in PROTECT_RES:
        masked = rgx.sub(repl, masked)
    return masked, tokens


def unmask(text: str, tokens: list[str]) -> str:
    for i, tok in enumerate(tokens):
        text = text.replace(f"§§T{i}§§", tok)
    return text


def parse_units(md: str) -> list[Unit]:
    """Split the structured Markdown into editable/non-editable units."""
    lines = md.split("\n")
    units: list[Unit] = []
    in_toc = False
    i, n = 0, len(lines)
    while i < n:
        line = lines[i]
        stripped = line.strip()
        # track the TOC block (## विषयानुक्रमणिका .. next heading) as non-editable
        if stripped.startswith("## विषयानुक्रमणिका"):
            in_toc = True
            units.append(Unit(len(units), i, "", line, False))
            i += 1
            continue
        if in_toc and stripped.startswith("#"):
            in_toc = False
        if in_toc or not stripped or stripped.startswith("#"):
            units.append(Unit(len(units), i, "", line, False))
            i += 1
            continue
        if line.startswith("| "):  # verse line
            units.append(Unit(len(units), i, "| ", line[2:], True))
            i += 1
            continue
        if line.startswith("- "):  # litany item
            units.append(Unit(len(units), i, "- ", line[2:], True))
            i += 1
            continue
        em = re.match(r"^([०-९]+|•)\.\s+(.*)$", line)  # endnote
        if em:
            units.append(Unit(len(units), i, f"{em.group(1)}. ", em.group(2), True))
            i += 1
            continue
        # prose paragraph: join consecutive plain lines into one unit
        buf = [line]
        start = i
        i += 1
        while i < n and lines[i].strip() and not lines[i].startswith(("|", "-", "#")) \
                and not re.match(r"^([०-९]+|•)\.\s+", lines[i]):
            buf.append(lines[i])
            i += 1
        units.append(Unit(len(units), start, "", " ".join(s.strip() for s in buf), True))
    return units


def call_batch(client: SarvamAI, batch: list[Unit], model: str) -> dict[int, str]:
    """Send a batch; return {unit_idx: corrected_masked_text}."""
    parts = []
    for u in batch:
        parts.append(f"###{u.idx}###\n{u.masked}")
    user = (
        "Proofread each segment below. Return the SAME ###number### markers in the "
        "same order, each followed by the corrected text. Keep every §§T..§§ token "
        "verbatim. Do not merge or drop segments.\n\n" + "\n".join(parts)
    )
    resp = client.chat.completions(
        model=model, temperature=0,
        messages=[{"role": "system", "content": SYSTEM_PROMPT},
                  {"role": "user", "content": user}],
    )
    text = resp.choices[0].message.content
    if not text:
        return {}
    out: dict[int, str] = {}
    chunks = re.split(r"###(\d+)###", text)
    # chunks: ['', 'idx', 'body', 'idx', 'body', ...]
    for j in range(1, len(chunks) - 1, 2):
        try:
            out[int(chunks[j])] = chunks[j + 1].strip()
        except ValueError:
            continue
    return out


def validate(orig_masked: str, new_masked: str, tokens: list[str]) -> bool:
    if not new_masked.strip():
        return False
    # placeholders intact (same multiset)
    want = re.findall(r"§§T\d+§§", orig_masked)
    got = re.findall(r"§§T\d+§§", new_masked)
    if sorted(want) != sorted(got):
        return False
    # restored output checks
    new = unmask(new_masked, tokens)
    orig = unmask(orig_masked, tokens)
    if BAD_OUT_RE.search(new):
        return False
    if DEVA_RE.search(orig) and not DEVA_RE.search(new):
        return False
    ratio = len(new) / max(1, len(orig))
    if not (0.8 <= ratio <= 1.25):
        return False
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--lines", default="", help="A:B source-line range to limit scope")
    ap.add_argument("--batch", type=int, default=10)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--concurrency", type=int, default=4)
    ap.add_argument("--work-dir", default="/tmp/bookify_work")
    args = ap.parse_args()

    key = os.environ.get("SARVAM_API_KEY")
    if not key:
        print("ERROR: SARVAM_API_KEY not set", file=sys.stderr)
        return 2

    work = Path(args.work_dir)
    work.mkdir(parents=True, exist_ok=True)
    cache_path = work / "proofread_cache.json"
    cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}

    md = Path(args.input).read_text(encoding="utf-8")
    units = parse_units(md)

    lo, hi = 0, 10 ** 9
    if args.lines:
        a, b = args.lines.split(":")
        lo, hi = int(a), int(b)

    targets = []
    for u in units:
        if u.editable and lo <= u.line_start <= hi and len(u.content.strip()) >= 4:
            u.masked, u.tokens = mask(u.content)
            targets.append(u)

    client = SarvamAI(api_subscription_key=key)
    batches = [targets[i:i + args.batch] for i in range(0, len(targets), args.batch)]
    print(f"units total={len(units)} editable-in-scope={len(targets)} "
          f"batches={len(batches)}", flush=True)

    def process(batch):
        # serve from cache where possible
        need = [u for u in batch if hashlib.sha256(u.masked.encode()).hexdigest()
                not in cache]
        results = {}
        if need:
            try:
                results = call_batch(client, need, args.model)
            except Exception as e:
                print(f"  batch error: {e}", flush=True)
        for u in batch:
            h = hashlib.sha256(u.masked.encode()).hexdigest()
            if h in cache:
                cand = cache[h]
            else:
                cand = results.get(u.idx, "")
                if cand and validate(u.masked, cand, u.tokens):
                    cache[h] = cand
                else:
                    cand = u.masked  # fallback: unchanged
                    cache[h] = cand
            new = unmask(cand, u.tokens)
            u.new_content = new
            u.changed = new.strip() != u.content.strip()
            u.status = "changed" if u.changed else "unchanged"
        return batch

    done = 0
    with ThreadPoolExecutor(max_workers=args.concurrency) as ex:
        futs = [ex.submit(process, b) for b in batches]
        for f in as_completed(futs):
            f.result()
            done += 1
            if done % 10 == 0:
                print(f"  {done}/{len(batches)} batches", flush=True)
    cache_path.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")

    # rebuild markdown from units in order (prose paragraphs collapse to one
    # line, which is fine; blank lines and headings are preserved as units).
    rebuilt: list[str] = []
    changelog = []
    for u in units:
        if u.editable:
            text = u.new_content if u.new_content else u.content
            rebuilt.append(f"{u.prefix}{text}")
            if u.changed:
                changelog.append({"line": u.line_start, "prefix": u.prefix.strip(),
                                  "old": u.content, "new": u.new_content})
        else:
            rebuilt.append(u.content)
    out_text = "\n".join(rebuilt)
    out_text = re.sub(r"\n{3,}", "\n\n", out_text)
    Path(args.output).write_text(out_text + "\n", encoding="utf-8")

    # changelog artifacts
    (work / "changelog.json").write_text(
        json.dumps(changelog, ensure_ascii=False, indent=2), encoding="utf-8")
    cl_md = ["# प्रूफरीडिंग परिवर्तन-सूची (changelog)", "",
             f"कुल इकाइयाँ जाँची: {len(targets)} · परिवर्तित: {len(changelog)}", ""]
    for c in changelog:
        cl_md.append(f"- **पंक्ति {c['line']}**")
        cl_md.append(f"  - पूर्व: {c['old']}")
        cl_md.append(f"  - नव:  {c['new']}")
    (work / "changelog.md").write_text("\n".join(cl_md), encoding="utf-8")

    print(f"WROTE {args.output}; changed {len(changelog)}/{len(targets)} units")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
