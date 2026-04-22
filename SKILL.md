---
name: proofread
description: Proofread an academic paper against a structured checklist covering abbreviations, math notation, math consistency, introduction structure, grammar and style, and figures and tables. Two modes — report (full written report) and interactive (fix issues step by step together with the user).
allowed-tools: Read Bash Edit
license: MIT license
metadata:
    skill-author: Jakob Thumm
---

# Paper Proofreading

## Overview

Systematically proofread an academic paper against six structured checks. Each check scans the full paper and collects concrete, line-level findings.

Two modes are available:
- **Report mode** (default): produces a single prioritized written report organized by check, with a summary scorecard at the top.
- **Interactive mode**: presents issues one at a time, lets the user decide how to resolve each one, and applies edits directly to the source files.

This skill targets **LaTeX source files** as primary input. Plain-text and PDF inputs are supported but yield less precise findings (line numbers will be approximate or absent).

## When to Use This Skill

Use this skill when:
- Finishing a draft and want a full systematic review before submission — use **report mode**
- Sitting down to actively fix a paper issue by issue — use **interactive mode**
- Returning to a paper after a break and want to catch consistency issues
- Preparing a revision and need to verify all issues flagged by reviewers are resolved

## Arguments

```
/proofread [path] [--check <id>] [--interactive]
```

- `path` — path to the paper's root `.tex` file or directory containing `.tex` files. Defaults to the current directory.
- `--check <id>` — run only a specific check. IDs: `abbrev`, `math-notation`, `math-consistency`, `intro`, `grammar`, `figures`. Omit to run all six.
- `--interactive` — enable interactive mode. Omit for report mode.

---

## Core Workflow

### Step 0: Collect Input Files

1. Resolve the input path. If a directory is given, find all `.tex` files recursively (`find . -name "*.tex"`).
2. Read all `.tex` files into memory. Note the root file (typically `main.tex`) for structure analysis.
3. Concatenate files in document order (follow `\input` and `\include` chains from the root) to produce a single logical document for cross-section checks.
4. If no `.tex` files are found, attempt to read a plain-text or PDF version and warn the user that line numbers will be absent.

---

### Check 1: Abbreviations

<!-- To be filled in -->

---

### Check 2: Math Symbols and Notation

<!-- To be filled in -->

---

### Check 3: Math Consistency

<!-- To be filled in -->

---

### Check 4: Introduction Structure

<!-- To be filled in -->

---

### Check 5: Grammar and Style

<!-- To be filled in -->

---

### Check 6: Figures and Tables

<!-- To be filled in -->

---

## Mode A: Report Mode (default)

After all checks are complete, produce a single report with the following structure (see **Output Format** below). Do not edit any source files.

---

## Mode B: Interactive Mode (`--interactive`)

In interactive mode, all checks still run first to collect the full issue list. Then present issues to the user one at a time and allow them to resolve each before moving on.

### Interactive Loop

For each issue (ordered by check, then severity ERRORs first, then line number):

1. **Present the issue** in a compact block:
   ```
   Issue 3 of 17 — [ERROR] abbrev — intro.tex:42
   > we use a NN to classify
   Abbreviation "NN" used before introduction.
   Suggestion: Change to "a neural network (NN)" on first use.
   ```

2. **Offer the user four options:**
   ```
   How would you like to proceed?
     [A] Apply suggestion
     [E] Edit manually — tell me what to write
     [S] Skip this issue
     [Q] Quit and show remaining issues as a report
   ```

3. **Handle the response:**
   - `A` — apply the suggested fix directly to the source file using the Edit tool, confirm the change, then move to the next issue.
   - `E` — ask the user for the desired text, apply it, confirm, then move to the next issue.
   - `S` — mark the issue as skipped and move to the next issue.
   - `Q` — stop the interactive loop and output the remaining unresolved issues as a standard report (see **Output Format**).

4. After every applied edit, briefly confirm: `✓ Fixed in intro.tex:42. Moving to next issue.`

5. After all issues are resolved or skipped, show a short closing summary:
   ```
   Interactive session complete.
   Fixed: 12 | Skipped: 3 | Remaining: 2 (see report below)
   ```
   Then output any skipped issues as a report.

### Important Rules for Interactive Mode

- Re-read the relevant file section before applying each edit to ensure the file has not drifted from the collected finding (earlier edits may shift line numbers).
- Never apply an edit without confirming the target text still matches. If it does not, re-present the finding with the updated context and ask the user again.
- Do not batch-apply multiple edits without user confirmation between each one.

---

## Output Format

After all checks are complete, produce a single report with the following structure:

```
# Proofreading Report — <paper title or filename>
Date: <today>

## Scorecard
| # | Check                    | Issues |
|---|--------------------------|--------|
| 1 | Abbreviations            | n      |
| 2 | Math Symbols & Notation  | n      |
| 3 | Math Consistency         | n      |
| 4 | Introduction Structure   | n      |
| 5 | Grammar & Style          | n      |
| 6 | Figures & Tables         | n      |
|   | **Total**                | **n**  |

---

## 1. Abbreviations
<findings or "No issues found.">

## 2. Math Symbols & Notation
<findings or "No issues found.">

## 3. Math Consistency
<findings or "No issues found.">

## 4. Introduction Structure
<findings or "No issues found.">

## 5. Grammar & Style
<findings or "No issues found.">

## 6. Figures & Tables
<findings or "No issues found.">
```

### Finding Format

Each individual finding follows this format:

```
- [SEVERITY] file.tex:LINE — <concise description of the issue>
  > <offending snippet (≤ 80 chars)>
  Suggestion: <concrete fix>
```

Severity levels:
- `[ERROR]` — clear rule violation (e.g., abbreviation never introduced, undefined math symbol)
- `[WARN]` — likely issue that needs human judgement (e.g., possible inconsistency)
- `[INFO]` — minor style note or suggestion

Sort findings within each section by severity (ERRORs first), then by line number.
