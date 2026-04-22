# proofreading

A Claude Code skill for proofreading academic papers against a structured checklist covering abbreviations, math notation, math consistency, introduction structure, grammar and style, and figures and tables.

## Features

- **Report mode**: full prioritized issue report with line-level findings
- **Interactive mode**: fix issues step by step together with the agent
- **PDF annotation extraction**: when given an annotated PDF, extracts highlights, notes, and strikethrough comments from reviewers

## Requirements

Install Python dependencies with:

```bash
pip install -r requirements.txt
```

`pymupdf` is required for PDF annotation extraction (`scripts/extract-pdf-annotations.py`). It is not needed if you only work with LaTeX source files.

## Usage

```
/proofread [path] [--check <id>] [--interactive]
```

- `path` — path to the root `.tex` file or directory of `.tex` files (default: current directory). A `.pdf` file can also be provided to extract annotations.
- `--check <id>` — run only one check: `abbrev`, `math-notation`, `math-consistency`, `intro`, `grammar`, `figures`
- `--interactive` — fix issues one by one instead of producing a written report
