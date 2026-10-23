#!/usr/bin/env python3
"""Turn Sarvam batch JSON results into dated transcripts.

For every recording date found in JSON_DIR (files `<date>.mp3.json`, or `<date>_p1.mp3.json` and
`<date>_p2.mp3.json` for a recording that was split at the time given in CUTS_FILE as "<date> <seconds>"),
write into OUT_DIR:

  <prefix>_<date>.txt         speaker blocks with one [hh:mm:ss] line per ASR segment (the review format)
  <prefix>_<date>.srt         the same segments as subtitles, for checking against the audio
  <prefix>_<date>_turns.txt   one line per speaker turn, "S:"/"Ln:" with the turn's start time (the working format)

The speaker with the most airtime in each piece is labelled as the main speaker; others are numbered
listeners, numbered within the day only.

Usage: transcript_from_json.py JSON_DIR OUT_DIR PREFIX "Main speaker label" [CUTS_FILE] [--title TITLE]
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

LISTENER = "श्रोता {n} (Listener {n})"
SEP = "=" * 60


@dataclass
class Segment:
    start: float
    end: float
    speaker: str
    text: str


def hms(seconds: float) -> str:
    t = int(seconds)
    return f"{t // 3600:02d}:{t % 3600 // 60:02d}:{t % 60:02d}"


def srt_time(seconds: float) -> str:
    ms = int(round(seconds * 1000))
    return f"{ms // 3600000:02d}:{ms % 3600000 // 60000:02d}:{ms % 60000 // 1000:02d},{ms % 1000:03d}"


def load_pieces(json_dir: Path, cuts: dict[str, float]) -> dict[str, list[tuple[Path, float]]]:
    days: dict[str, list[tuple[Path, float]]] = {}
    for path in sorted(json_dir.glob("*.mp3.json")):
        stem = path.name[: -len(".mp3.json")]
        if stem.endswith("_p1") or stem.endswith("_p2"):
            day, part = stem[:-3], stem[-2:]
            offset = 0.0 if part == "p1" else cuts[day]
        else:
            day, offset = stem, 0.0
        days.setdefault(day, []).append((path, offset))
    return days


def read_segments(pieces: list[tuple[Path, float]], main_label: str) -> list[Segment]:
    segments: list[Segment] = []
    listeners: dict[tuple[int, str], str] = {}
    for index, (path, offset) in enumerate(pieces):
        entries = json.loads(path.read_text())["diarized_transcript"]["entries"]
        airtime: Counter[str] = Counter()
        for entry in entries:
            airtime[entry["speaker_id"]] += entry["end_time_seconds"] - entry["start_time_seconds"]
        main = airtime.most_common(1)[0][0]
        for entry in entries:
            text = entry["transcript"].strip()
            if not text:
                continue
            speaker_id = entry["speaker_id"]
            if speaker_id == main:
                label = main_label
            else:
                key = (index, speaker_id)
                if key not in listeners:
                    listeners[key] = LISTENER.format(n=len(listeners) + 1)
                label = listeners[key]
            segments.append(
                Segment(entry["start_time_seconds"] + offset, entry["end_time_seconds"] + offset, label, text)
            )
    return segments


def write_day(out_dir: Path, prefix: str, day: str, segments: list[Segment], title: str, main_label: str) -> None:
    duration = segments[-1].end if segments else 0.0
    header = [
        title,
        f"Date: {day}    Duration: {hms(duration)}",
        "",
        "Verbatim transcript (Sarvam AI saaras:v4, verbatim mode, speaker diarization).",
        f"Main speaker = {main_label}. Listener numbers identify short interjections within this day only.",
        "Machine transcription: names, verses and technical terms may contain errors; verify against the audio.",
        "",
        SEP,
    ]
    review, turns, srt = list(header), [], []
    current = None
    turn_text: list[str] = []
    turn_start = 0.0

    def flush_turn() -> None:
        if turn_text:
            who = "S:" if current == main_label else f"L{current.split('(Listener ')[1].rstrip(')')}:"
            turns.append(f"{who} [{hms(turn_start)}] " + " ".join(turn_text))

    for n, seg in enumerate(segments, 1):
        if seg.speaker != current:
            flush_turn()
            turn_text, turn_start, current = [], seg.start, seg.speaker
            review += ["", f"{seg.speaker}:"]
        review.append(f"[{hms(seg.start)}] {seg.text}")
        turn_text.append(seg.text)
        srt.append(f"{n}\n{srt_time(seg.start)} --> {srt_time(seg.end)}\n{seg.speaker}: {seg.text}\n")
    flush_turn()
    (out_dir / f"{prefix}_{day}.txt").write_text("\n".join(review) + "\n")
    (out_dir / f"{prefix}_{day}.srt").write_text("\n".join(srt))
    (out_dir / f"{prefix}_{day}_turns.txt").write_text("\n".join(turns) + "\n")
    words = sum(len(s.text.split()) for s in segments)
    print(f"{prefix}_{day}: {hms(duration)}, {len(segments)} segments, {len(turns)} turns, {words} words")


def main(argv: list[str]) -> None:
    title = "Transcript"
    if "--title" in argv:
        i = argv.index("--title")
        title = argv[i + 1]
        argv = argv[:i] + argv[i + 2 :]
    json_dir, out_dir, prefix, main_label = Path(argv[1]), Path(argv[2]), argv[3], argv[4]
    cuts: dict[str, float] = {}
    if len(argv) > 5 and Path(argv[5]).exists():
        for line in Path(argv[5]).read_text().split("\n"):
            if line.strip():
                day, seconds = line.split()
                cuts[day] = float(seconds)
    out_dir.mkdir(parents=True, exist_ok=True)
    for day, pieces in sorted(load_pieces(json_dir, cuts).items()):
        write_day(out_dir, prefix, day, read_segments(pieces, main_label), title, main_label)


if __name__ == "__main__":
    main(sys.argv)
