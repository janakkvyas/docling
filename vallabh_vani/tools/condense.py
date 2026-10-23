#!/usr/bin/env python3
"""Condense a diarized transcript into one-line S:/Ln: turns with the starting timestamp.

Speaker headers are exactly "गोस्वामी श्रीश्याम मनोहरजी:" or "श्रोता N (Listener N):". Any other line
without a [hh:mm:ss] stamp is a continuation of the previous segment (the ASR text contained a newline)
and is appended to the current turn.
"""
import re, sys
from pathlib import Path
HDR = re.compile(r"(गोस्वामी श्रीश्याम मनोहरजी|श्रोता (\d+) \(Listener \d+\)):")
TS = re.compile(r"\[(\d\d:\d\d:\d\d)\] ?(.*)")
src, dst = Path(sys.argv[1]), Path(sys.argv[2])
lines = src.read_text().split("\n")
body = lines[lines.index("=" * 60) + 1:]
turns = []; who = None; buf = []; ts = None
def flush():
    if buf: turns.append(f"{who} [{ts}] " + " ".join(buf))
for ln in body:
    ln = ln.strip()
    if not ln: continue
    h = HDR.fullmatch(ln)
    if h:
        flush(); buf = []; ts = None
        who = "S:" if h.group(2) is None else f"L{h.group(2)}:"
        continue
    m = TS.match(ln)
    if m:
        if ts is None: ts = m.group(1)
        buf.append(m.group(2))
    else:
        buf.append(ln)
flush()
dst.write_text("\n".join(turns) + "\n")
print(dst.name, len(turns), "turns", len("".join(turns)), "chars")
