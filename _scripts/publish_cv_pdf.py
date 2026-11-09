"""Publish the CV PDF rendered from cv.qmd (Typst) as files/CV_Rodrigo_Gomez_Fell.pdf.

Runs automatically after every `quarto render` (see `post-render` in _quarto.yml), so
the web CV and the PDF always come from the same source and cannot drift apart.
The PDF is copied to files/ (tracked in git) and to _site/files/ (published).

Privacy guard: if pdftotext is available (PDFTOTEXT env var or on PATH), the PDF
text is checked and the build fails if it contains a phone number, a postal
address or a date of birth. With REQUIRE_PDFTOTEXT=1 (set in the GitHub Actions
workflow) a missing pdftotext fails the build instead of skipping the check.
"""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "_site"
RENDERED = SITE / "cv-public.pdf"            # output-file set in cv.qmd
NAME = "CV_Rodrigo_Gomez_Fell.pdf"
FORBIDDEN = re.compile(r"mobile|phone|\+63|\+64|\b0?20\s?4\d{7}\b|private bag|date of birth|\bDOB\b", re.I)


def main():
    if not RENDERED.exists():                 # cv.qmd was not part of this render
        return
    pdftotext = os.environ.get("PDFTOTEXT") or shutil.which("pdftotext")
    if pdftotext:
        text = subprocess.run([pdftotext, str(RENDERED), "-"], capture_output=True,
                              text=True, check=True).stdout
        hit = FORBIDDEN.search(text)
        if hit:
            RENDERED.unlink()
            sys.exit(f"publish_cv_pdf: private detail found in CV PDF ({hit.group(0)!r}); not published")
        print(f"publish_cv_pdf: privacy check passed ({len(text)} characters of PDF text, "
              "no phone number, postal address or date of birth)")
    elif os.environ.get("REQUIRE_PDFTOTEXT") == "1":
        RENDERED.unlink()
        sys.exit("publish_cv_pdf: pdftotext not found but REQUIRE_PDFTOTEXT=1; CV not published")
    else:
        print("publish_cv_pdf: pdftotext not found; privacy check skipped")

    for dest in (ROOT / "files" / NAME, SITE / "files" / NAME):
        dest.parent.mkdir(exist_ok=True)
        shutil.copyfile(RENDERED, dest)
    RENDERED.unlink()
    print(f"publish_cv_pdf: files/{NAME} updated")


if __name__ == "__main__":
    main()
