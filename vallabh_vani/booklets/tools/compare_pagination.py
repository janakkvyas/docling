#!/usr/bin/env python3
"""Where does each printed page of the exemplar begin in a rebuild?

    compare_pagination.py EXEMPLAR_COPY.md REBUILD.pdf

Takes the first words after every <!-- p.N --> marker of the clean copy, finds them in the rebuilt PDF's text,
and prints, per page, the page on which they fall in the rebuild (= means the same page as the original).
"""

import re
import subprocess
import sys
import unicodedata

md, pdf = open(sys.argv[1]).read(), sys.argv[2]


def norm(s: str) -> str:
    s = unicodedata.normalize("NFC", s)
    return re.sub(r"[\s‌‍\"'“”‘’*|#:-]", "", s)


n = int(
    re.search(
        r"Pages:\s+(\d+)",
        subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout,
    ).group(1)
)
pages = [
    norm(
        subprocess.run(
            ["pdftotext", "-f", str(i), "-l", str(i), pdf, "-"],
            capture_output=True,
            text=True,
        ).stdout
    )
    for i in range(1, n + 1)
]
same, diff, rows = 0, 0, []
for m in re.finditer(r"<!--\s*p\.(\d+)[^>]*-->\s*(.*?)(?=<!--|$)", md, re.S):
    p, body = int(m.group(1)), m.group(2)
    body = re.sub(
        r"<!--.*?-->|!\[[^\]]*\]\([^)]*\)(\{[^}]*\})?|^:::.*$|^\* \* \*$|^#.*$",
        " ",
        body,
        flags=re.M,
    )
    key = norm(body)[:18]
    if len(key) < 8:
        continue
    hit = next((i + 1 for i, t in enumerate(pages) if key in t), None)
    mark = "=" if hit == p else ("?" if hit is None else f"{hit - p:+d}")
    same += hit == p
    diff += hit is not None and hit != p
    rows.append(f"p.{p}:{hit if hit else '-'}{'' if hit == p else ' (' + mark + ')'}")
print(" ".join(rows))
print(
    f"{same} pages begin on the same page as in the original, {diff} elsewhere, rebuild has {n} pages"
)
