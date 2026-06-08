#!/usr/bin/env python3
"""Convert a large PDF to Markdown using Sarvam AI Document Intelligence.

Sarvam caps each Document Intelligence job at 10 pages, so this splits the PDF
into <=10-page chunks, runs each as its own job (in parallel, with retries),
downloads the Markdown, and concatenates everything back in page order.

Prereqs:
    uv pip install sarvamai pypdf
    export SARVAM_API_KEY=...            # required

Usage:
    uv run python scripts/sarvam_convert.py INPUT.pdf OUTPUT.md \
        [--language hi-IN] [--chunk-size 10] [--concurrency 4]

Language hints (BCP-47): hi-IN (Hindi/Devanagari, default), sa-IN (Sanskrit),
en-IN, bn-IN, ta-IN, te-IN, mr-IN, gu-IN, kn-IN, ml-IN, pa-IN, or-IN, ur-IN, ...
"""

from __future__ import annotations

import argparse
import io
import os
import sys
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from sarvamai import SarvamAI

MAX_RETRIES = 4


def split_pdf(src: Path, out_dir: Path, chunk_size: int) -> list[Path]:
    """Split src into <=chunk_size-page PDFs; return chunk paths in order."""
    reader = PdfReader(str(src))
    n = len(reader.pages)
    out_dir.mkdir(parents=True, exist_ok=True)
    chunks: list[Path] = []
    for idx, start in enumerate(range(0, n, chunk_size)):
        writer = PdfWriter()
        for p in range(start, min(start + chunk_size, n)):
            writer.add_page(reader.pages[p])
        chunk_path = out_dir / f"chunk_{idx:03d}.pdf"
        with chunk_path.open("wb") as f:
            writer.write(f)
        chunks.append(chunk_path)
    return chunks


def _markdown_from_download(path: Path) -> str:
    """A job output may be a zip of .md files or a bare .md; return its text."""
    data = path.read_bytes()
    if zipfile.is_zipfile(io.BytesIO(data)):
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            md_names = sorted(n for n in z.namelist() if n.lower().endswith(".md"))
            return "\n\n".join(z.read(n).decode("utf-8", "replace") for n in md_names)
    return data.decode("utf-8", "replace")


def process_chunk(client: SarvamAI, chunk: Path, language: str,
                  work_dir: Path) -> str:
    """Run one chunk through a Document Intelligence job; return its Markdown."""
    last_err: Exception | None = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            job = client.document_intelligence.create_job(
                language=language, output_format="md")
            job.upload_file(str(chunk))
            job.start()
            status = job.wait_until_complete(poll_interval=3.0, timeout=900)
            if status.job_state == "Failed":
                raise RuntimeError(f"job failed: {status.job_state}")
            dl = work_dir / f"{chunk.stem}.out"
            job.download_output(str(dl))
            return _markdown_from_download(dl)
        except Exception as e:  # network / 429 / job errors -> backoff & retry
            last_err = e
            wait = 2 ** attempt
            print(f"  [{chunk.name}] attempt {attempt} failed: {e} "
                  f"(retry in {wait}s)", flush=True)
            time.sleep(wait)
    raise RuntimeError(f"{chunk.name} failed after {MAX_RETRIES} attempts: {last_err}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--language", default="hi-IN")
    ap.add_argument("--chunk-size", type=int, default=10)
    ap.add_argument("--concurrency", type=int, default=4)
    args = ap.parse_args()

    key = os.environ.get("SARVAM_API_KEY")
    if not key:
        print("ERROR: SARVAM_API_KEY is not set", file=sys.stderr)
        return 2

    src = Path(args.input)
    out = Path(args.output)
    work = Path("/tmp/sarvam_work")
    chunks = split_pdf(src, work / "chunks", args.chunk_size)
    print(f"split into {len(chunks)} chunks of <= {args.chunk_size} pages",
          flush=True)

    client = SarvamAI(api_subscription_key=key)
    results: dict[int, str] = {}
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=args.concurrency) as ex:
        futs = {ex.submit(process_chunk, client, c, args.language, work): i
                for i, c in enumerate(chunks)}
        done = 0
        for fut in as_completed(futs):
            i = futs[fut]
            results[i] = fut.result()  # raises if a chunk exhausted retries
            done += 1
            print(f"completed {done}/{len(chunks)} (chunk {i})", flush=True)

    md_parts = []
    for i in range(len(chunks)):
        start_page = i * args.chunk_size + 1
        md_parts.append(f"<!-- chunk {i} (pages from {start_page}) -->\n\n"
                        + results[i].strip())
    out.write_text("\n\n".join(md_parts) + "\n", encoding="utf-8")
    print(f"WROTE {out} ({out.stat().st_size/1e6:.2f} MB) in "
          f"{time.time()-t0:.0f}s", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
