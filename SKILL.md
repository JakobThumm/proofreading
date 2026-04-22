---
name: proofread
description: Proofread an academic paper against a structured checklist covering abbreviations, math notation, introduction structure, grammar and style, and figures and tables. Two modes — report (full written report) and interactive (fix issues step by step together with the user).
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
- `--check <id>` — run only a specific check. IDs: `abbrev`, `math-notation`, `intro`, `grammar`, `figures`. Omit to run all five.
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

**Goal**: Verify that every abbreviation is introduced correctly, used consistently, has the right article, and that the abstract is self-contained.

#### 1.1 Collect all abbreviations

Scan the full document for abbreviations. An abbreviation is any sequence of 2 or more uppercase letters (optionally mixed with digits), e.g., `RL`, `MDP`, `SAC`, `HER`, `STP`, `DoF`. Also collect any terms defined via LaTeX acronym packages (`\ac{}`, `\acp{}`, `\acf{}`, `\acl{}`, `\acs{}`, `\newacronym{}`).

Build two lists:
- **Abstract abbreviations**: all abbreviations appearing in the abstract
- **Body abbreviations**: all abbreviations appearing in the main body (everything after the abstract)

#### 1.2 Check the abstract

The abstract is a standalone piece of text and must introduce its own abbreviations independently of the main body.

For each abbreviation in the abstract:
- `[ERROR]` if it is used without being introduced in the abstract itself (pattern: full term followed by abbreviation in parentheses, e.g., `reinforcement learning (RL)`)
- `[ERROR]` if it is introduced more than once in the abstract
- `[WARN]` if it is introduced in the abstract but only used once (introduction unnecessary)

#### 1.3 Check first use in the main body

For each abbreviation in the body:
- Find the first occurrence in document order (follow `\input`/`\include` chain).
- `[ERROR]` if the first occurrence is bare (e.g., `RL` appears) without a prior or inline introduction of the form `full term (ABBREV)`. This applies even if the abbreviation was introduced in the abstract — the main body must introduce it independently.
- `[ERROR]` if the abbreviation appears in a section heading before it has been introduced in body text.
- `[INFO]` if the introduction pattern deviates from `full term (ABBREV)` (e.g., abbreviation introduced before the full term).

#### 1.4 Check subsequent uses in the main body

After the introduction, the full term must not be written out again — the abbreviation must be used exclusively.

- `[WARN]` for each occurrence of the full term (case-insensitive) after the introduction point, where the abbreviation should have been used instead.
- `[ERROR]` if the abbreviation is introduced more than once in the main body (e.g., `neural network (NN)` appears a second time after the first body introduction). Note: one introduction in the abstract and one in the body is correct and expected — this error only fires for a second introduction within the body itself.

#### 1.5 Check article agreement

For each occurrence of `a ABBREV` or `an ABBREV` (case-insensitive), check whether the article matches the pronunciation of the first letter of the abbreviation as a spelled-out letter name.

Letters whose names begin with a vowel sound → require `an`:
`A` (AY), `E` (EE), `F` (EF), `H` (AY-TCH), `I` (EYE), `L` (EL), `M` (EM), `N` (EN), `O` (OH), `R` (AR), `S` (ESS), `X` (EX)

All other letters → require `a`.

**Exception**: if the abbreviation is pronounced as a word rather than spelled out (e.g., `NASA`, `LASER`), use the pronunciation of the word itself, not the first letter name. Use context and common knowledge to judge this.

- `[ERROR]` if the article does not match the rule above (e.g., `a NN` → should be `an NN`).

#### 1.6 Check plural formation

Plurals of abbreviations are formed by appending a lowercase `s` directly: `NNs`, `MLPs`, `STPs`.

- `[ERROR]` if a possessive apostrophe is used to form a plural: `NN's`, `MLP's`
- `[WARN]` if the full term is pluralized after the abbreviation has been introduced (e.g., `neural networks` instead of `NNs`)

---

### Check 2: Math Symbols and Notation

**Goal**: Verify that every math symbol is defined before first use, that equations are properly integrated into the text, and that LaTeX notation follows best practices.

#### 2.1 Collect all math symbols

Scan all math environments (`$...$`, `$$...$$`, `\(...\)`, `\[...\]`, `equation`, `align`, `gather`, `multline`, and their starred variants) and build a list of every distinct symbol used. A symbol is any single letter, Greek letter, calligraphic/bold/hat/dot-decorated letter, or named operator that carries semantic meaning (e.g., `x`, `\mathcal{X}`, `\boldsymbol{\theta}`, `\hat{f}`, `\dot{x}`, `J`, `\pi`).

Exclude pure syntax tokens (`=`, `+`, `-`, `\leq`, `\in`, `\forall`, etc.) — these do not require definition.

#### 2.2 Check symbol definitions

For each symbol, find its first use in document order.

- `[ERROR]` if a symbol is used in an equation or inline math before it is defined anywhere in the text. A definition is a prose statement of the form "where `X` is ..." or "let `X` denote ..." appearing in the same or an earlier paragraph, or a `where` clause immediately following the equation.
- `[ERROR]` if a symbol is used in a figure caption or table caption before it has been defined in the main text at that point in reading order.
- `[WARN]` if a symbol is defined but never used.
- `[INFO]` if the definition appears after the equation rather than before (post-equation `where` clauses are acceptable but pre-definition is preferred).

**Subscripts and superscripts:**

Treat each distinct subscript and superscript as a symbol in its own right if it carries semantic meaning (i.e., it is a variable or index, not a fixed label like `\text{max}`). Examples of semantic indices: `i` in `x_i`, `t` in `s_t`, `k` in `g^{(k)}`. Examples of non-semantic labels: `\text{max}`, `\text{ref}`, `0` as a constant initializer.

For each semantic subscript/superscript:
- `[ERROR]` if the index is used but never defined in prose (e.g., `s_t` appears but `t` is never explained as the time step index).
- `[ERROR]` if a subscripted or superscripted symbol (e.g., `x_i`) is introduced without defining what the index ranges over (e.g., `i \in \{1, \ldots, N\}` or "for each joint `i`").
- `[WARN]` if an index is defined but the corresponding indexed family of symbols is only used once (indexing may be unnecessary).
- `[WARN]` if the same index letter is used with different meanings in different parts of the paper (e.g., `i` denotes joint index in Section II but episode index in Section IV). Flag each such conflict with both locations.

#### 2.3 Check symbol consistency

This check verifies that notation is globally coherent: the same symbol always refers to the same concept, and the same concept is always referred to by the same symbol.

**One symbol, one concept:**

Build a map from each symbol to all prose definitions found for it across the document.
- `[ERROR]` if a symbol is defined to mean two different things in different parts of the paper (e.g., `x` is defined as "state" in Section II and as "position" in Section IV). Report both definition locations.
- `[WARN]` if a symbol is used in a context that is semantically inconsistent with its definition, even if not explicitly redefined (e.g., `t` defined as a continuous time variable but used as a discrete step index elsewhere).

**One concept, one symbol:**

Identify concept clusters: groups of symbols that appear to refer to the same entity based on their prose definitions and surrounding context.
- `[WARN]` if two different symbols appear to refer to the same concept without explanation (e.g., "goal state" is written as `g` in one section and as `x_g` in another). Flag as a potential inconsistency for the author to confirm.
- `[WARN]` if a concept is sometimes referred to by its symbol and sometimes by a synonymous term that suggests a different symbol could be used (e.g., "target" and "goal" used interchangeably but only one has a symbol).

**Decoration consistency:**

Decorations (`\hat{}`, `\tilde{}`, `\bar{}`, `\boldsymbol{}`, `\mathcal{}`) should carry consistent semantic meaning throughout the paper (e.g., `\hat{x}` always means "estimated x", `\mathcal{X}` always means "set of x").
- `[WARN]` if the same decoration is applied to different base symbols with different semantic meanings (e.g., `\hat{x}` means "estimate" but `\hat{f}` means "learned function" where a different convention might be expected).
- `[WARN]` if a concept that is decorated in one equation (e.g., `\hat{x}` for estimated state) appears without decoration in another equation where the estimated value is clearly intended.

#### 2.4 Check variables in text

Single-letter variables and all math symbols appearing inline in prose must be wrapped in math mode.

- `[ERROR]` for any bare single letter used as a variable in prose without math delimiters, e.g., `the value of N` instead of `the value of $N$`. Use context to distinguish math variables from ordinary words — flag only when the letter clearly refers to a mathematical quantity.
- `[ERROR]` for bare expressions like `t+1` or `x_i` outside math mode.

#### 2.5 Check equation integration and punctuation

Equations must be part of the surrounding text flow and punctuated accordingly.

- `[ERROR]` if a displayed equation is not preceded by a colon, comma, or a sentence that flows into it grammatically.
- `[ERROR]` if a displayed equation is not followed by a punctuation mark (period, comma) where one is grammatically required by the surrounding sentence.
- `[ERROR]` if an equation label is referenced before the equation appears in the document (forward reference to an equation).

#### 2.6 Check scalar, vector, matrix, and set notation

**Goal**: Identify the notation convention the paper uses for mathematical types, then verify it is applied consistently to every symbol.

**Step 1 — Infer the convention**

Scan the document for symbols whose type can be determined unambiguously from context. Use the following signals:

| Signal | Type inferred |
|--------|--------------|
| `$x \in \mathbb{R}$` (no exponent) | scalar |
| `$x \in \mathbb{R}^n$` (single exponent) | vector |
| `$x \in \mathbb{R}^{m \times n}$` (product exponent) | matrix |
| `$x = \{...\}$`, `$x \subset ...$`, `$x \subseteq ...$` | set |
| Subscripted with two indices: `$A_{ij}$` | likely matrix |
| Subscripted with one index: `$x_i$` | likely vector element or scalar |
| `\mathcal{X}` | likely set (strong signal for Convention A) |
| `\boldsymbol{x}` lowercase | likely vector (strong signal for Convention A) |
| `\boldsymbol{X}` uppercase | likely matrix (Convention A) or set (Convention B) |
| `\mathbf{x}` | likely vector (Convention C) |

From these signals, determine which of the following conventions the paper most likely follows. Choose the convention with the most matching evidence:

| Convention | Scalar | Vector | Matrix | Set |
|------------|--------|--------|--------|-----|
| **A** (default) | `$x$` | `$\boldsymbol{x}$` | `$\boldsymbol{X}$` | `$\mathcal{X}$` |
| **B** | `$x$` | `$x$` (no bold) | `$X$` | `$\boldsymbol{X}$` |
| **C** (ML common) | `$x$` | `$\mathbf{x}$` | `$\mathbf{X}$` | `$\mathcal{X}$` |

Report the detected convention at the top of Check 2's findings: `Detected notation convention: A/B/C (or unknown)`.

If the evidence is mixed and no single convention dominates, report `[WARN] Notation convention could not be determined reliably — mixed signals found` and list the conflicting examples. Still proceed with the checks below using the plurality convention.

**Step 2 — Check all typed symbols**

For each symbol whose type is known (from Step 1 signals or prose definitions), verify its formatting matches the detected convention:

- `[ERROR]` if a known vector is not formatted as the convention requires (e.g., Convention A: vector `x` written as plain `$x$` instead of `$\boldsymbol{x}$`).
- `[ERROR]` if a known matrix is not formatted as the convention requires (e.g., Convention A: matrix `A` written as plain `$A$` instead of `$\boldsymbol{A}$`).
- `[ERROR]` if a known set is not formatted as the convention requires (e.g., Convention A: set written as `$X$` instead of `$\mathcal{X}$`).
- `[WARN]` if a known scalar is formatted with bold or calligraphic style (likely a type error).
- `[WARN]` if a symbol's type cannot be determined but its formatting is inconsistent with other symbols of likely the same type.

**Step 3 — Check for mixed convention usage**

- `[ERROR]` if both `\boldsymbol{}` and `\mathbf{}` are used for vectors or matrices (only one bold command should be used throughout; `\boldsymbol{}` is preferred as it also works for Greek letters).
- `[WARN]` if uppercase calligraphic (`\mathcal{}`) and uppercase bold (`\boldsymbol{}` or `\mathbf{}`) are both used for sets in different places.

---

#### 2.7 Check notation best practices

- `[ERROR]` if `*` is used for multiplication inside math mode (use juxtaposition or `\cdot` instead): e.g., `$a * b$` → `$a b$` or `$a \cdot b$`.
- `[WARN]` if `\cdot` is used to denote a dot product between two vectors (prefer the transpose form `$\boldsymbol{c}^\top \boldsymbol{c}$` instead): e.g., `$\boldsymbol{a} \cdot \boldsymbol{b}$` → `$\boldsymbol{a}^\top \boldsymbol{b}$`.
- `[ERROR]` if plain text words appear inside a formula without `\text{}` or `\mathrm{}`, causing them to render as products of letters: e.g., `$sun$` instead of `$\text{sun}$`. Flag when a sequence of 3+ lowercase letters inside math mode spells an English word.
- `[ERROR]` if `\mathbf` is used for Greek letters or symbols that should use `\boldsymbol` instead (e.g., `\mathbf{\theta}` → `\boldsymbol{\theta}`).
- `[ERROR]` if an accent or decoration is placed outside rather than around only the base letter: e.g., `\hat{f(x)}` → `\hat{f}(x)`.
- `[WARN]` if `\frac` is used inside inline math (`$...$`) where `\tfrac` or a slash form would be more readable.

#### 2.8 Check repeated math expressions and custom command usage

**Step 1 — Collect existing custom commands**

Scan the preamble and any `\input`-ted style or macro files for all custom math command definitions:
- `\newcommand`, `\renewcommand`, `\providecommand`
- `\DeclareMathOperator`, `\DeclarePairedDelimiter`

For each defined command, record its name and its expansion (the replacement text). Build a map: `expansion → command name`.

**Step 2 — Detect repeated complex expressions**

Scan all math environments and collect every sub-expression that is:
- Non-trivial: contains at least one subscript or superscript plus at least one `\text{}`, `\mathrm{}`, or decoration (`\hat`, `\boldsymbol`, etc.) — e.g., `r_{\text{hum}}^j`, `\hat{x}_{t+1|t}`, `\boldsymbol{\theta}_{\text{ref}}`
- Not already covered by a custom command from Step 1

Count occurrences of each such expression across the full document (inline and displayed math).

- `[INFO]` for any complex expression appearing **3 or more times** that has no corresponding custom command. For each, suggest a concise command name and the `\newcommand` definition:
  ```
  Expression `r_{\text{hum}}^j` appears 7 times.
  Suggestion: \newcommand{\rhumj}{r_{\text{hum}}^j}
  ```
  Propose the command name by combining the meaningful parts of the expression (drop `\text`, `\boldsymbol`, braces; camelCase or abbreviate). Flag this as `[INFO]` since it is a style suggestion, not an error.

**Step 3 — Check consistent use of existing custom commands**

For each custom command defined in Step 1, search all math environments for occurrences of its expansion written out in full instead of using the command.

- `[WARN]` if a defined command's expansion appears written out manually instead of using the command: e.g., `r_{\text{hum}}^j` is written out explicitly when `\rhumj` is already defined.
  ```
  [WARN] main.tex:84 — expansion of \rhumj written out manually instead of using the command.
  > $r_{\text{hum}}^j \leq d_{\text{safe}}$
  Suggestion: Replace with \rhumj.
  ```

---

### Check 3: Introduction Structure

<!-- To be filled in -->

---

### Check 4: Grammar and Style

<!-- To be filled in -->

---

### Check 5: Figures and Tables

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
| 3 | Introduction Structure   | n      |
| 4 | Grammar & Style          | n      |
| 5 | Figures & Tables         | n      |
|   | **Total**                | **n**  |

---

## 1. Abbreviations
<findings or "No issues found.">

## 2. Math Symbols & Notation
<findings or "No issues found.">

## 3. Introduction Structure
<findings or "No issues found.">

## 4. Grammar & Style
<findings or "No issues found.">

## 5. Figures & Tables
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
