# Proofreading

A Claude Code skill for proofreading academic papers against a structured checklist covering paper structure, math notation, statistical relevance, figures and tables, grammar and style, and abbreviations.

## Experience
[I](https://jakob-thumm.com) went through a hard school with [my professor](https://www.ce.cit.tum.de/en/cps/members/prof-dr-ing-matthias-althoff/) highlighting every single detail that differentiates an average paper from an outstanding scientific work.
Over the years of my Ph.D., I received feedback on my paper drafts 44 times!
I went through all of this feedback and compiled a comprehensive list of checks that regularly come up during proof reading. 
That being said, especially Check 5 (Grammar and Style) is highly subjective and should be adapted to your personal needs.

If you find this skill useful, **give it a star** and **share it with your colleagues**.
Do not hesitate to open up a pull request to extend this skill further! 

## Features

- **Report mode**: full prioritized issue report with line-level findings
- **Interactive mode**: fix issues step by step together with the agent
- **PDF annotation extraction**: when given an annotated PDF, extracts highlights, notes, and strikethrough comments from reviewers

## Checks

This skill contains over 100 checks, which we categorize into 6 groups. The following list gives a brief summary of the most important checks in each group.

**Check 1 — Paper Structure** (`intro`)
- Abstract follows the four-part structure: motivation, gap, approach, quantitative result
- Introduction contains an explicit, falsifiable contribution list
- Related work is organized thematically and ends with a gap statement

**Check 2 — Math Symbols and Notation** (`math-notation`)
- Every symbol and index is defined before first use
- Scalar/vector/matrix/set convention is detected and applied consistently
- Equations are punctuated and integrated into the surrounding text

**Check 3 — Statistical Relevance** (`stats`)
- Result figures show uncertainty (error bars, confidence bands)
- Result tables report values with standard deviation or confidence intervals
- Comparative prose claims are backed by statistical evidence or seed counts

**Check 4 — Figures and Tables** (`figures`)
- Every figure and table is referenced in the text and has a self-contained caption
- Figures use vector formats; tables use the `booktabs` package
- Result figures are assessed for axis labels, legend, line thickness, and color accessibility

**Check 5 — Grammar and Style** (`grammar`)
- First-person "we" is used consistently; passive is reserved for system properties
- Prohibited vague intensifiers and inflated vocabulary are flagged
- Compound adjectives are hyphenated; Oxford comma and `i.e.,`/`e.g.,` rules are applied

**Check 6 — Abbreviations** (`abbrev`)
- The abstract introduces its own abbreviations independently of the main body
- Every abbreviation is introduced on first use in the body with the full term
- Article agreement (`a`/`an`) and plural formation (`NNs` not `NN's`) are checked

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
- `--check <id>` — run only one check: `intro`, `math-notation`, `stats`, `figures`, `grammar`, `abbrev`
- `--interactive` — fix issues one by one instead of producing a written report

## Contribute

Propose additions or changes by opening a pull request:

1. Edit `SKILL.md` — each check is a `### Check N` section; sub-checks follow the `#### N.x` pattern.
2. Tag every rule with a severity (`[ERROR]` / `[WARN]` / `[INFO]`) and a difficulty label (`[HARD]` for tool-based checks, e.g. grub, `[MIX]` for a mix between tool-based and reasoning checks, `[VIBE]` for semantic reasoning only).
3. Keep the change focused: one logical issue per sub-check, one sub-check per rule group.
4. If you add a new check group, update the `--check` argument list in the Arguments section of `SKILL.md` and in this README.
