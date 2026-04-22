#!/usr/bin/env python3
"""Convert a proofreading report markdown file to a formatted PDF via pandoc."""
import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

TEMPLATE = Path(__file__).parent.parent / "templates" / "report_latex.tex"

SEVERITY_COLORS = {
    "[ERROR]": r"\textcolor{errorred}{\textbf{[ERROR]}}",
    "[WARN]":  r"\textcolor{warnambер}{\textbf{[WARN]}}",
    "[INFO]":  r"\textcolor{infoblue}{\textbf{[INFO]}}",
}


def check_deps() -> bool:
    ok = True
    if not shutil.which("pandoc"):
        print("ERROR: pandoc not found. Install with: sudo apt install pandoc  OR  brew install pandoc")
        ok = False
    if not shutil.which("xelatex") and not shutil.which("pdflatex"):
        print("ERROR: no LaTeX engine found. Install texlive: sudo apt install texlive-xetex")
        ok = False
    return ok


def extract_title(md: str) -> str:
    m = re.search(r"^#\s+(.+)$", md, re.MULTILINE)
    return m.group(1).strip() if m else "Proofreading Report"


def build_pdf(md_path: Path, out_path: Path, engine: str) -> None:
    title = extract_title(md_path.read_text())
    cmd = [
        "pandoc",
        str(md_path),
        "--from", "markdown-raw_tex",
        "--to", "pdf",
        "--pdf-engine", engine,
        "--template", str(TEMPLATE),
        "--variable", f"title={title}",
        "--variable", "geometry:margin=2.5cm",
        "--table-of-contents",
        "--toc-depth=2",
        "--output", str(out_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("pandoc error:")
        print(result.stderr)
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert proofreading report markdown to PDF.")
    parser.add_argument("input", help="Path to the markdown report file")
    parser.add_argument("-o", "--output", help="Output PDF path (default: same name as input with .pdf)")
    parser.add_argument("--engine", default="pdflatex", choices=["xelatex", "pdflatex", "lualatex"],
                        help="LaTeX engine to use (default: xelatex)")
    parser.add_argument("--check-deps", action="store_true", help="Check dependencies and exit")
    args = parser.parse_args()

    if args.check_deps:
        sys.exit(0 if check_deps() else 1)

    if not check_deps():
        sys.exit(1)

    md_path = Path(args.input)
    if not md_path.exists():
        print(f"ERROR: file not found: {md_path}")
        sys.exit(1)

    out_path = Path(args.output) if args.output else md_path.with_suffix(".pdf")

    print(f"Generating PDF: {out_path}")
    build_pdf(md_path, out_path, args.engine)
    print(f"Done: {out_path}")


if __name__ == "__main__":
    main()
