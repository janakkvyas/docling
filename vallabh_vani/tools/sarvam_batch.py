#!/usr/bin/env python3
"""Submit a folder of prepared audio files to Sarvam's batch speech-to-text and download the JSON results.

Usage: sarvam_batch.py IN_DIR OUT_DIR LANGUAGE_CODE KEYTERMS_FILE
The API key is read from the SARVAM_API_KEY environment variable; it is never written to disk.
"""
import os
import sys
from pathlib import Path

from sarvamai import SarvamAI

in_dir, out_dir, language, keyterms_file = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], Path(sys.argv[4])
keyterms = [k.strip() for k in keyterms_file.read_text().splitlines() if k.strip()][:50]
client = SarvamAI(api_subscription_key=os.environ["SARVAM_API_KEY"])
job = client.speech_to_text_job.create_job(
    model="saaras:v4", mode="verbatim", language_code=language,
    with_diarization=True, with_timestamps=True, keyterms=keyterms,
)
print("job", job.job_id, flush=True)
job.upload_files(file_paths=sorted(str(p) for p in in_dir.glob("*.mp3")))
job.start()
status = job.wait_until_complete(poll_interval=30, timeout=7100)
for detail in status.job_details or []:
    print(detail.inputs[0].file_name, detail.state, detail.error_message, flush=True)
out_dir.mkdir(parents=True, exist_ok=True)
print("downloaded", job.download_outputs(output_dir=str(out_dir)))
