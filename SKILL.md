---
name: proofread
description: Proofread an academic paper against a structured checklist covering abbreviations, math notation, introduction structure, grammar and style, figures and tables, and statistical relevance. Two modes — report (full written report) and interactive (fix issues step by step together with the user).
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
- `--check <id>` — run only a specific check. IDs: `intro`, `math-notation`, `stats`, `figures`, `grammar`, `abbrev`. Omit to run all six.
- `--interactive` — enable interactive mode. Omit for report mode.

---

## Core Workflow

### Step 0: Collect Input Files

1. Resolve the input path. If a directory is given, find all `.tex` files recursively (`find . -name "*.tex"`).
2. Read all `.tex` files into memory. Note the root file (typically `main.tex`) for structure analysis.
3. Concatenate files in document order (follow `\input` and `\include` chains from the root) to produce a single logical document for cross-section checks.
4. If no `.tex` files are found, attempt to read a plain-text or PDF version and warn the user that line numbers will be absent.

---

### Check 1: Paper Structure

**Goal**: Verify that the abstract and introduction follow the expected structure of an academic paper: clear problem motivation, gap identification, proposed approach, quantitative results (abstract), explicit contributions, and a section roadmap. Check that the related work is discussed correctly. Check that the conclusion follows common guidelines.

#### 1.1 Check abstract structure

The abstract must follow this fixed four-part structure, in order:

1. **Motivate the problem** — why does this problem matter? Showing real-world relevance strongly recommended.
2. **Identify the gap** — what do existing approaches fail to do?
3. **State the proposed approach** — what does this paper do?
4. **Give key quantitative results** — at least one concrete number supporting the main claim.

- `[ERROR]` if any of the four parts is entirely absent. `[VIBE]`
- `[WARN]` if the parts appear but are out of order (e.g., approach stated before gap). `[VIBE]`
- `[WARN]` if no quantitative result is given (e.g., only qualitative claims like "significantly improves"). `[VIBE]`
- `[WARN]` if the abstract exceeds 150 words (typical conference limit; adjust if venue is known). `[HARD]`

#### 1.2 Check introduction structure

The introduction must contain, in roughly this order:

1. **Motivation** — a paragraph establishing why the problem is important and relevant. Showing real-world relevance strongly recommended.
2. **State of the art and gap** — a summary of related approaches and their shortcomings. The gap must be stated explicitly (e.g., "However, none of these methods...").
3. **Proposed approach** — a description of what this paper proposes and why it addresses the gap.
4. **Contribution list** — a very concrete list of explicit contributions (see 1.3). 
5. **Section roadmap** — [OPTIONAL] a final paragraph describing the structure of the paper (see 1.4).

- `[ERROR]` if the contribution list is absent. `[MIX]`
- `[INFO]` if the section roadmap is absent. `[MIX]`
- `[WARN]` if the gap is not stated explicitly (related work is described but no "However,..." or equivalent contrast is made). `[VIBE]`
- `[WARN]` if the proposed approach is not re-stated in the introduction after the related work (it should appear both in the abstract and the introduction). `[VIBE]`
- `[WARN]` if the novelty of the work is not stated explicitly (e.g., "To the best of our knowledge, this is the first work to..."). `[VIBE]`
- `[INFO]` if the introduction order deviates significantly from the structure above. `[VIBE]`

#### 1.3 Check contribution list

- `[ERROR]` if a contribution item is too encompassing. The contributions should very precisely list the new theoretical contributions to the field. These contributions must be elements that are not present in related work. New contributions should be supported by theorems, proofs, algorithms etc. `[VIBE]`
- `[ERROR]` if a contribution item is vague and not falsifiable — e.g., "We improve performance" without specifying what is improved or by how much. A good contribution names the specific claim: "We show that our method reduces collision rate by 30% compared to baseline X." `[VIBE]`
- `[ERROR]` if the word `contribut`..., e.g., contribute, contribution, is not used in the introduction. `[HARD]`
- `[WARN]` if contributions are not presented as a list (numbered or bulleted). A list is recommended, but a very clear sentence with (a), (b), and (c) or (i), (ii), and (iii) also works. `[MIX]`
- `[INFO]` if any contribution item does not begin with "We", "This work", "In this paper" etc. (e.g., "We propose...", "We show...", "We evaluate...", "We introduce...", "We demonstrate..."). `[MIX]`
- `[INFO]` if a contribution item uses passive voice instead of "We" (e.g., "A new method is proposed" → "We propose a new method"). `[MIX]`

#### 1.4 Check section roadmap

The last paragraph of the introduction should describe the structure of the remainder of the paper.

- `[WARN]` if no roadmap paragraph is present in the introduction. `[MIX]`
- `[ERROR]` if the roadmap references a section number or name that does not match the actual sections in the document (verify against `\section{}` commands). `[MIX]`
- `[WARN]` if the roadmap uses future tense ("will be presented") instead of present tense ("is presented", "presents"). `[MIX]`
- `[WARN]` if not all major sections are mentioned in the roadmap (every top-level `\section{}` except the introduction itself should appear). `[MIX]`
- `[INFO]` if the roadmap does not open with a standard linking phrase such as "The remainder of this paper is structured as follows" or "This paper is organized as follows". `[MIX]`

#### 1.5 Check problem statement

If the paper has a dedicated problem statement section or subsection:

- `[ERROR]` if the problem statement mentions the proposed solution (e.g., "we use a safety shield"). The problem statement must describe what needs to be solved, not how. `[VIBE]`
- `[WARN]` if the problem statement includes implementation details that belong in the method section. `[VIBE]`

#### 1.6 Check related work structure

- `[ERROR]` if related work is organized chronologically rather than thematically by approach category. Each category must open with a clear topic sentence. `[VIBE]`
- `[WARN]` if the related work section does not end with a gap statement that clearly identifies what prior methods cannot do and thus motivates the proposed work. `[VIBE]`
- `[ERROR]` if the related work section explicitly describes or evaluates the proposed method (e.g., "In contrast to prior work, our method does X"). Related work discusses others' work only. `[VIBE]`

#### 1.7 Check experiments and hypotheses

- `[WARN]` if the experiments section does not state hypotheses explicitly before presenting results (e.g., "H1: ..., H2: ..."). Explicit hypotheses are a frequently recurring professor comment. `[VIBE]`
- `[WARN]` if a conclusion generalizes a result to "all cases" or "any environment" when the experiment only covered one or two settings. `[VIBE]`

#### 1.8 Check conclusions

- `[WARN]` if the conclusion does not explain why the results are better than prior work. `[VIBE]`
- `[WARN]` if the conclusion does not reiterate the unique features of the approach. `[VIBE]`
- `[WARN]` if the conclusion does not mention at least one key quantitative result. `[VIBE]`
- `[INFO]` if the conclusion introduces new content not discussed anywhere else in the paper. `[VIBE]`

#### 1.9 Check motivation scope

Motivation — establishing why the problem matters, why existing approaches fall short, or why the task is challenging — belongs exclusively in the introduction (and, briefly, the related work gap statement). Method sections must describe *what* the approach does and *how* it works, not re-argue *why* the problem is worth solving.
Flag motivational content in the methodology section(s) and experiment/result section(s):

- `[ERROR]` if a method paragraph opens with a sentence that re-states the problem motivation from the introduction (e.g., "Ensuring safety is critical in human-robot interaction because...", "Existing methods fail to handle..."). `[VIBE]`
- `[ERROR]` if a method paragraph introduces new motivation not present in the introduction — a reason the problem is hard or important that was not established earlier (e.g., "Another challenge is that sensors are noisy, which makes..."). `[VIBE]`
- `[WARN]` if transitional sentences between subsections of the method re-introduce the gap or limitation of prior work (e.g., "Since prior methods cannot handle X, we instead..."). A single back-reference is acceptable; repeated gap re-statements across multiple method subsections are not. `[VIBE]`

---

### Check 2: Math Symbols and Notation

**Goal**: Verify that every math symbol is defined before first use, that equations are properly integrated into the text, and that LaTeX notation follows best practices.

#### 2.1 Collect all math symbols

Scan all math environments (`$...$`, `$$...$$`, `\(...\)`, `\[...\]`, `equation`, `align`, `gather`, `multline`, and their starred variants) and build a list of every distinct symbol used. A symbol is any single letter, Greek letter, calligraphic/bold/hat/dot-decorated letter, or named operator that carries semantic meaning (e.g., `x`, `\mathcal{X}`, `\boldsymbol{\theta}`, `\hat{f}`, `\dot{x}`, `J`, `\pi`).

Exclude pure syntax tokens (`=`, `+`, `-`, `\leq`, `\in`, `\forall`, etc.) — these do not require definition.

#### 2.2 Check symbol definitions

For each symbol, find its first use in document order.

- `[ERROR]` if a symbol is used in an equation or inline math before it is defined anywhere in the text. A definition is a prose statement of the form "where `X` is ..." or "let `X` denote ..." appearing in the same or an earlier paragraph, or a `where` clause immediately following the equation. `[MIX]`
- `[ERROR]` if a symbol is used in a figure caption or table caption before it has been defined in the main text at that point in reading order. `[MIX]`
- `[WARN]` if a symbol is defined but never used. `[MIX]`
- `[INFO]` if the definition appears after the equation rather than before (post-equation `where` clauses are acceptable but pre-definition is preferred). `[MIX]`

**Subscripts and superscripts:**

Treat each distinct subscript and superscript as a symbol in its own right if it carries semantic meaning (i.e., it is a variable or index, not a fixed label like `\text{max}`). Examples of semantic indices: `i` in `x_i`, `t` in `s_t`, `k` in `g^{(k)}`. Examples of non-semantic labels: `\text{max}`, `\text{ref}`, `0` as a constant initializer.

For each semantic subscript/superscript:
- `[ERROR]` if the index is used but never defined in prose (e.g., `s_t` appears but `t` is never explained as the time step index). `[MIX]`
- `[ERROR]` if a subscripted or superscripted symbol (e.g., `x_i`) is introduced without defining what the index ranges over (e.g., `i \in \{1, \ldots, N\}` or "for each joint `i`"). `[MIX]`
- `[WARN]` if an index is defined but the corresponding indexed family of symbols is only used once (indexing may be unnecessary). `[MIX]`
- `[WARN]` if the same index letter is used with different meanings in different parts of the paper (e.g., `i` denotes joint index in Section II but episode index in Section IV). Flag each such conflict with both locations. `[MIX]`

#### 2.3 Check symbol consistency

This check verifies that notation is globally coherent: the same symbol always refers to the same concept, and the same concept is always referred to by the same symbol.

**One symbol, one concept:**

Build a map from each symbol to all prose definitions found for it across the document.
- `[ERROR]` if a symbol is defined to mean two different things in different parts of the paper (e.g., `x` is defined as "state" in Section II and as "position" in Section IV). Report both definition locations. `[VIBE]`
- `[WARN]` if a symbol is used in a context that is semantically inconsistent with its definition, even if not explicitly redefined (e.g., `t` defined as a continuous time variable but used as a discrete step index elsewhere). `[VIBE]`

**One concept, one symbol:**

Identify concept clusters: groups of symbols that appear to refer to the same entity based on their prose definitions and surrounding context.
- `[WARN]` if two different symbols appear to refer to the same concept without explanation (e.g., "goal state" is written as `g` in one section and as `x_g` in another). Flag as a potential inconsistency for the author to confirm. `[VIBE]`
- `[WARN]` if a concept is sometimes referred to by its symbol and sometimes by a synonymous term that suggests a different symbol could be used (e.g., "target" and "goal" used interchangeably but only one has a symbol). `[VIBE]`

**Decoration consistency:**

Decorations (`\hat{}`, `\tilde{}`, `\bar{}`, `\boldsymbol{}`, `\mathcal{}`) should carry consistent semantic meaning throughout the paper (e.g., `\hat{x}` always means "estimated x", `\mathcal{X}` always means "set of x").
- `[WARN]` if the same decoration is applied to different base symbols with different semantic meanings (e.g., `\hat{x}` means "estimate" but `\hat{f}` means "learned function" where a different convention might be expected). `[VIBE]`
- `[WARN]` if a concept that is decorated in one equation (e.g., `\hat{x}` for estimated state) appears without decoration in another equation where the estimated value is clearly intended. `[VIBE]`

#### 2.4 Check variables in text

Single-letter variables and all math symbols appearing inline in prose must be wrapped in math mode.

- `[ERROR]` for any bare single letter used as a variable in prose without math delimiters, e.g., `the value of N` instead of `the value of $N$`. Use context to distinguish math variables from ordinary words — flag only when the letter clearly refers to a mathematical quantity. `[MIX]`
- `[ERROR]` for bare expressions like `t+1` or `x_i` outside math mode. `[HARD]`

#### 2.5 Check equation integration and punctuation

Equations must be part of the surrounding text flow and punctuated accordingly.

- `[ERROR]` if a displayed equation is not preceded by a colon, comma, or a sentence that flows into it grammatically. `[VIBE]`
- `[ERROR]` if a displayed equation is not followed by a punctuation mark (period, comma) where one is grammatically required by the surrounding sentence. `[MIX]`
- `[ERROR]` if an equation label is referenced before the equation appears in the document (forward reference to an equation). `[MIX]`

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

- `[ERROR]` if a known vector is not formatted as the convention requires (e.g., Convention A: vector `x` written as plain `$x$` instead of `$\boldsymbol{x}$`). `[MIX]`
- `[ERROR]` if a known matrix is not formatted as the convention requires (e.g., Convention A: matrix `A` written as plain `$A$` instead of `$\boldsymbol{A}$`). `[MIX]`
- `[ERROR]` if a known set is not formatted as the convention requires (e.g., Convention A: set written as `$X$` instead of `$\mathcal{X}$`). `[MIX]`
- `[WARN]` if a known scalar is formatted with bold or calligraphic style (likely a type error). `[MIX]`
- `[WARN]` if a symbol's type cannot be determined but its formatting is inconsistent with other symbols of likely the same type. `[VIBE]`

**Step 3 — Check for mixed convention usage**

- `[ERROR]` if both `\boldsymbol{}` and `\mathbf{}` are used for vectors or matrices (only one bold command should be used throughout; `\boldsymbol{}` is preferred as it also works for Greek letters). `[HARD]`
- `[WARN]` if uppercase calligraphic (`\mathcal{}`) and uppercase bold (`\boldsymbol{}` or `\mathbf{}`) are both used for sets in different places. `[MIX]`

---

#### 2.7 Check notation best practices

- `[ERROR]` if `*` is used for multiplication inside math mode (use juxtaposition or `\cdot` instead): e.g., `$a * b$` → `$a b$` or `$a \cdot b$`. `[HARD]`
- `[WARN]` if `\cdot` is used to denote a dot product between two vectors (prefer the transpose form `$\boldsymbol{c}^\top \boldsymbol{c}$` instead): e.g., `$\boldsymbol{a} \cdot \boldsymbol{b}$` → `$\boldsymbol{a}^\top \boldsymbol{b}$`. `[HARD]`
- `[ERROR]` if plain text words appear inside a formula without `\text{}` or `\mathrm{}`, causing them to render as products of letters: e.g., `$sun$` instead of `$\text{sun}$`. Flag when a sequence of 3+ lowercase letters inside math mode spells an English word. `[HARD]`
- `[ERROR]` if `\mathbf` is used for Greek letters or symbols that should use `\boldsymbol` instead (e.g., `\mathbf{\theta}` → `\boldsymbol{\theta}`). `[HARD]`
- `[ERROR]` if an accent or decoration is placed outside rather than around only the base letter: e.g., `\hat{f(x)}` → `\hat{f}(x)`. `[HARD]`
- `[WARN]` if `\frac` is used inside inline math (`$...$`) where `\tfrac` or a slash form would be more readable. `[HARD]`
- `[ERROR]` if `\mathbb` is used for anything other than the standard number sets `\mathbb{R}`, `\mathbb{N}`, `\mathbb{Z}`, `\mathbb{C}`, `\mathbb{Q}`. It must not be used for general matrices, indicator functions, or other objects. `[HARD]`
- `[WARN]` if time derivatives are written as `\frac{d x}{d t}` or `\frac{\partial x}{\partial t}` in display equations where `\dot{x}` or `\ddot{x}` would be more compact and consistent with the rest of the paper. `[MIX]`
- `[WARN]` if an equation is referenced in prose as "equation 3" or "eq. 3" instead of `\eqref{label}`, which produces `(3)` automatically and tracks renumbering. `[HARD]`
- `[WARN]` if a multi-step derivation contains `=` or `\leq` transitions with no indication of which equation or rule was used. Suggest `\overset{(X)}{}` or a brief prose annotation to make the derivation checkable. `[VIBE]`
- `[ERROR]` if `\forall` or `\exists` is followed directly by a set (e.g., `\forall \{a, b, c\}`) rather than a variable with a domain constraint (e.g., `\forall x \in \mathcal{X}`). `[HARD]`
- `[INFO]` if "zero vector" is used; prefer "vector of zeros" (`\mathbf{0}`) to avoid confusion with the zero element of a vector space. `[HARD]`

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

- `[INFO]` for any complex expression appearing **3 or more times** that has no corresponding custom command. For each, suggest a concise command name and the `\newcommand` definition: `[MIX]`
  ```
  Expression `r_{\text{hum}}^j` appears 7 times.
  Suggestion: \newcommand{\rhumj}{r_{\text{hum}}^j}
  ```
  Propose the command name by combining the meaningful parts of the expression (drop `\text`, `\boldsymbol`, braces; camelCase or abbreviate). Flag this as `[INFO]` since it is a style suggestion, not an error.

**Step 3 — Check consistent use of existing custom commands**

For each custom command defined in Step 1, search all math environments for occurrences of its expansion written out in full instead of using the command.

- `[WARN]` if a defined command's expansion appears written out manually instead of using the command: e.g., `r_{\text{hum}}^j` is written out explicitly when `\rhumj` is already defined. `[HARD]`
  ```
  [WARN] main.tex:84 — expansion of \rhumj written out manually instead of using the command.
  > $r_{\text{hum}}^j \leq d_{\text{safe}}$
  Suggestion: Replace with \rhumj.
  ```

#### 2.9 Check notation coherence

- `[ERROR]` if the paper switches between discrete and continuous time notation without explicitly explaining the relationship. For example, using `t_k` for discrete steps in one section and `t` for continuous time in another without a bridging statement. `[VIBE]`
- `[WARN]` if the same mathematical operation is written two different ways in different parts of the paper (e.g., `\| \cdot \|` vs `| \cdot |` for the same norm, or `a^\top b` vs `\langle a, b \rangle` for the same inner product). `[MIX]`
- `[WARN]` if the same quantity is denoted differently across sections or the appendix (e.g., `q_i` in the main text vs `\theta_i` in the appendix for joint angles). `[MIX]`
- `[WARN]` if subscripts and superscripts for the same concept are used inconsistently (e.g., `x_i^j` in one place and `x^j_i` or `x_{i,j}` elsewhere for the same meaning). `[MIX]`

#### 2.10 Check equation numbering discipline

- `[INFO]` if a numbered equation is never referenced anywhere in the text. An unreferenced equation number adds clutter; suggest removing the number (use the starred environment, e.g., `equation*`). `[HARD]`
- `[INFO]` if an equation `\label{}` is defined but no corresponding `\eqref{label}` or `\ref{label}` is used. `[HARD]`

#### 2.11 Check function argument consistency

- `[ERROR]` if a function is called with different numbers of arguments at different points (e.g., `f(x)` in one place and `f(x, t)` elsewhere without explanation). `[MIX]`
- `[WARN]` if a function is defined with arguments in one order but called in a different order at a later use. `[VIBE]`

---

### Check 3: Statistical Relevance

**Goal**: Verify that quantitative results are reported with appropriate statistical context — error bars, confidence intervals, standard deviations, or equivalent — wherever this is meaningful.

#### 3.1 Check result figures for uncertainty reporting

For each result figure (line plots, bar charts, scatter plots showing experimental outcomes), view the figure and check whether uncertainty is visualized.

- `[WARN]` if a bar chart shows mean values without error bars (standard deviation, standard error, or confidence interval). `[VIBE]`
- `[WARN]` if a line plot of results over trials/episodes/time shows no shaded confidence region or error band around the mean. `[VIBE]`
- `[WARN]` if a scatter plot shows point estimates with no indication of spread or confidence. `[VIBE]`

**Context**: some figures legitimately show only means — e.g., a single deterministic run, a demonstration trajectory, or a figure where uncertainty would clutter the visualization. In such cases, the text should explicitly state why uncertainty is not shown. Flag the absence of uncertainty visualization as `[WARN]` rather than `[ERROR]` and note that it requires author judgement.

#### 3.2 Check result tables for uncertainty reporting

For each results table:
- `[WARN]` if numerical results are reported as plain values (e.g., `84.3`) without an associated uncertainty (e.g., `84.3 ± 1.2`), standard deviation, or confidence interval, and the table reports results from stochastic experiments (RL training, neural network training, randomized trials). `[MIX]`
- `[INFO]` if the table caption or a table footnote explains that results are deterministic or averaged over a stated number of seeds — this is acceptable justification for omitting uncertainty. `[MIX]`

#### 3.3 Check prose claims for statistical support

- `[WARN]` if the text makes a comparative claim (e.g., "our method outperforms", "achieves higher accuracy", "converges faster") without citing a statistical test, confidence interval, or at minimum a clear description of the number of runs and variance. `[VIBE]`
- `[WARN]` if the text describes results from a single run as if they were general findings. Phrases like "the agent achieves X" without noting the number of seeds or runs should be flagged. `[VIBE]`

---

### Check 4: Figures and Tables

**Goal**: Verify that every figure and table is referenced in the text, has a self-contained caption, uses vector graphics, and is placed close to its first reference.

#### 4.1 Check that every figure and table is referenced

Collect all figure and table labels from `\label{}` commands inside `figure` and `table` environments. Collect all references to figures and tables from `\ref{}`, `\cref{}`, `\autoref{}`, and `\Cref{}` commands in the body text.

- `[ERROR]` if a figure or table has a `\label{}` but is never referenced in the body text. `[HARD]`
- `[ERROR]` if a figure or table is referenced but has no `\label{}` (hardcoded number used directly). `[HARD]`
- `[ERROR]` if a figure or table is referenced only in its own caption (self-referential, not referenced from body text). `[MIX]`
- `[WARN]` if a figure is referenced only after its position in the document (i.e., the first `\ref{}`/`\autoref{}` to that figure appears textually after the `\begin{figure}`). Figures should be mentioned before or at the point where the reader encounters them. `[MIX]`
- `[INFO]` if a figure is referenced only once in the entire document; verify the call-out is early enough. `[MIX]`

#### 4.2 Check that every reference points to an existing label

- `[ERROR]` if a `\ref{}`, `\cref{}`, or similar command references a label that does not exist in the document (dangling reference). `[HARD]`

#### 4.3 Check caption quality

Every figure and table caption must be self-contained: a reader should understand what is shown without reading the surrounding text.

- `[ERROR]` if a caption is a single word or fragment (e.g., `\caption{Results.}`) — captions should describe what is shown. `[MIX]`
- `[ERROR]` if a figure uses visual elements (line styles, colors, arrow styles, shading) that are not explained in the caption or a legend within the figure. For example, if both solid and dashed lines appear, the caption must state what each represents. `[VIBE]`
- `[WARN]` if a caption says only "Results of experiment X" without describing what the axes, curves, or visual elements represent. `[VIBE]`
- `[WARN]` if a caption uses an abbreviation that is not introduced either within the caption itself or in the document before the figure/table appears in reading order. `[MIX]`
- `[WARN]` if a caption uses a math symbol that is not defined within the caption and has not been defined in the main text before this point. `[MIX]`
- `[ERROR]` if a caption ends without a period. `[HARD]`

#### 4.4 Check that figures are referenced before they appear

Figures and tables should appear close to and after their first reference in the text.

- `[WARN]` if a figure or table appears in the document more than one page before its first in-text reference (forward float that readers encounter before the motivation). `[MIX]`
- `[INFO]` if a figure or table appears more than two pages after its first reference (may have drifted too far). `[MIX]`

#### 4.5 Check figure format

- `[WARN]` if a figure is included using a raster format (`.png`, `.jpg`, `.jpeg`, `.bmp`, `.gif`) — prefer vector formats (`.pdf`, `.eps`, `.svg`). Raster figures lose quality when scaled and are generally not accepted by IEEE/ACM venues for line art and diagrams. `[HARD]`
- `[INFO]` if a figure file cannot be located on disk (broken include path). `[HARD]`

#### 4.6 Check float placement options

Figures and tables should be placed at the top of a page (`[t]` or `[!t]`). Bottom placement and forced `[h]`/`[H]` options interrupt reading flow and are generally discouraged.

- `[WARN]` if a `figure` or `table` environment uses `[b]` (bottom placement). `[HARD]`
- `[WARN]` if a `figure` or `table` environment uses `[h]` or `[H]` (here placement) — prefer `[t]` to let LaTeX choose the best top-of-page slot. `[HARD]`
- `[INFO]` if a `figure` or `table` environment has no placement option specified (LaTeX default may not match intended behaviour). `[HARD]`

#### 4.7 Check table formatting

Tables must use the `booktabs` package (`\toprule`, `\midrule`, `\bottomrule`) instead of `\hline`.

- `[ERROR]` if `\hline` is used inside a `tabular` or `tabularx` environment — replace with `\toprule` (top), `\midrule` (between header and body), and `\bottomrule` (bottom).
- `[ERROR]` if `booktabs` rules are used but `\usepackage{booktabs}` is absent from the preamble. `[HARD]`
- `[WARN]` if a table has no top or bottom rule at all (neither `\hline` nor `\toprule`/`\bottomrule`). `[HARD]`
- `[WARN]` if vertical lines (`|` in the column spec, e.g., `\begin{tabular}{|l|c|}`) are used — booktabs style avoids vertical rules. `[HARD]`
- `[WARN]` if the first column of a table is not left-aligned (`l`) — the first column should be `l`, all remaining columns `c`. `[HARD]`
- `[WARN]` if any column other than the first is left-aligned (`l`) without a clear reason — prefer `c` for data columns. `[HARD]`

#### 4.8 Check that figures are explained in the text

Every figure and table should be discussed in the surrounding text, not just referenced.

- `[WARN]` if a figure or table reference appears in the text but the surrounding paragraph contains no sentence that describes or interprets what the figure/table shows (i.e., the reference is a bare parenthetical like "(see Fig. 3)" with no accompanying explanation). `[VIBE]`

#### 4.9 Check result figure visual quality

For each figure file included in the paper, view it directly (use the Read tool on PDF/image files) and assess the following visual properties. Apply these checks only to result and data figures (plots, graphs, bar charts, line plots) — skip diagrams, schematics, and architecture figures.

**Axis labels:**
- `[ERROR]` if any axis (x or y) of a plot has no label. `[VIBE]`
- `[WARN]` if an axis label is present but has no unit where a unit is expected (e.g., "Time" without "(s)", "Distance" without "(m)"). `[VIBE]`

**Y-axis limits:**
- `[WARN]` if multiple similar plots (same metric, same experiment type) have different y-axis limits, making visual comparison misleading. Flag the specific figures and their differing limits. `[VIBE]`

**Text size:**
- `[WARN]` if any text in the figure (axis labels, tick labels, legend text) appears noticeably smaller than the caption footnote size. A slightly smaller size is acceptable; tiny or unreadable text is not.
- `[ERROR]` if any text is so small it would be unreadable in print. `[VIBE]`

**Line thickness:**
- `[WARN]` if plotted lines appear thin (hairline weight). Lines in result figures should be thick enough to be clearly readable in print and when the figure is scaled down. `[VIBE]`

**Caption placement:**
- `[ERROR]` if the figure has a title rendered inside the plot area (as a Matplotlib/plot title above the axes) — this duplicates the LaTeX caption and should be removed. `[VIBE]`

**Legend:**
- `[WARN]` if a figure with multiple lines, bars, or series has no legend. `[VIBE]`
- `[WARN]` if the legend overlaps with data or is placed in a location that obscures results. `[VIBE]`
- `[WARN]` if legend text is too small to read comfortably. `[VIBE]`

**Color and accessibility:**
- `[WARN]` if the figure relies solely on color to distinguish series with no additional differentiator (different line styles: solid/dashed/dotted, or different markers: circle/square/triangle). Color-only figures are inaccessible to colorblind readers and unreadable in greyscale print. `[VIBE]`
- `[WARN]` if a red-green color pair is used as the primary distinguishing colors (most common form of colorblind inaccessibility). `[VIBE]`

**Consistency across figures:**
- `[WARN]` if the same method or condition is represented by different colors or markers in different figures of the paper. Consistent color/marker assignment across all figures is strongly preferred. `[VIBE]`

**Chartjunk:**
- `[WARN]` if the figure uses 3D effects, gradient fills, or drop shadows on 2D data — these add visual noise without information. `[VIBE]`

**Grid lines:**
- `[INFO]` if a result plot has no background grid lines. Light grid lines generally improve readability. `[VIBE]`

#### 4.10 Check cross-figure connections

- `[WARN]` if two figures use the same symbol, trajectory, or visual element where a connection between them would help the reader, but no explicit cross-reference exists in the text or captions. For example, if Fig. 4 shows a trajectory that was first introduced in Fig. 3, the caption of Fig. 4 should say so. `[VIBE]`

#### 4.12 Check LaTeX caption package conflicts

- `[WARN]` if the document uses an IEEE conference class (`IEEEtran.cls` or similar) and also includes `\usepackage{caption}` or `\usepackage{subcaption}`. These packages corrupt caption font sizes in IEEE templates and must be removed. `[HARD]`

#### 4.13 Check algorithm environments

- `[INFO]` if the paper contains `\begin{algorithm}` environments and the surrounding text refers to the algorithm by name only, never referencing specific line numbers. Note that `\label` can be placed inside algorithm environments to reference specific lines. `[MIX]`
- `[INFO]` if an algorithm uses variables in its body that are neither declared as inputs nor initialized within the algorithm. These "variables that fall from the sky" should either be added to the inputs or initialized explicitly. Assess which ones are genuinely missing versus which are duplicates or implicit from context. `[VIBE]`

---

### Check 5: Grammar and Style

**Goal**: Verify that the paper follows consistent grammatical conventions, uses the correct voice and tense, applies English punctuation rules correctly, and avoids known stylistic anti-patterns.

#### 5.1 Voice and person

- `[ERROR]` if first-person singular "I" is used anywhere (use "we" or passive voice instead). `[HARD]`
- `[WARN]` if passive voice is used in a context where "we" would work naturally (e.g., "It is shown that..." → "We show that..."). Passive is acceptable only when describing system or environmental properties (e.g., "The robot is mounted on a table"). `[VIBE]`
- `[INFO]` if "we" is used to describe a system or environment property where passive would be more appropriate (e.g., "We mount the robot on a table" when describing a fixed experimental setup). `[VIBE]`

#### 5.2 Tense consistency

**Main body**: use present tense throughout.
- `[WARN]` if past tense is used in the main body outside of the related work section (e.g., "We proposed a method" → "We propose a method"). `[MIX]`

**Figures and tables**: always referenced in present tense.
- `[ERROR]` if a figure or table is referenced in past or future tense (e.g., "Fig. 3 showed..." → "Fig. 3 shows...", "Table 1 will present..." → "Table 1 presents..."). `[MIX]`

**Related work section**: tense depends on intent.
- Simple past for describing results of a published work: "Smith [1] found that..."
- Present for author's own evaluation of the literature: "This approach, however, fails to..."
- Present perfect for recent or ongoing relevance: "Recent work has shown [7]..."
- `[WARN]` if only one tense is used throughout the entire related work section (likely indicates mechanical rather than intentional tense choice). `[VIBE]`

#### 5.3 English variant consistency

Detect the dominant English variant used in the paper (American or British) by scanning for known variant-specific spellings:

| Feature | American | British |
|---------|----------|---------|
| `-or` / `-our` | behavior | behaviour |
| `-er` / `-re` | center | centre |
| `-ize` / `-ise` | analyze | analyse |
| Double consonant | modeled | modelled |

- `[ERROR]` if both variants are used (e.g., "behaviour" and "center" in the same paper). Report all deviations from the dominant variant. `[HARD]`
- `[INFO]` state which variant was detected at the top of the Check 5 findings. `[HARD]`

#### 5.4 Punctuation

**Oxford comma**: use a comma before the final conjunction in a list of three or more items.
- `[ERROR]` if a list of three or more items is missing the Oxford comma (e.g., "We present results, discussion and conclusion" → "... discussion, and conclusion"). `[VIBE]`

**Comma after i.e. and e.g.**:
- `[ERROR]` if "i.e." or "e.g." is not followed by a comma (e.g., "i.e. the result" → "i.e., the result"). `[HARD]`

**Em-dashes**: avoid em-dashes (`---`, `\textemdash`, `—`). Use a comma or split the sentence instead.
- `[WARN]` for every em-dash found. Suggest a comma or sentence split as the fix. `[HARD]`

**Comma with "which"**: use a comma before "which" when the clause is non-restrictive (i.e., the sentence is understandable without it); omit the comma when the clause is restrictive (identifies which specific thing is meant).
- `[INFO]` flag each "which" clause for author review, noting whether a comma is present and whether it seems non-restrictive or restrictive. Do not auto-classify as error — this requires human judgement. `[VIBE]`

#### 5.5 Prohibited words and phrases

Flag the following as `[WARN]`:

**Vague intensifiers** — never use these; emphasize through a shorter sentence or a quantitative qualifier instead:
`very`, `quite`, `rather`

**Overused or inflated vocabulary** — replace with simpler alternatives:
`utilize` (→ use), `emerges`, `pioneered`, `encompass`, `poised to become`, `paramount`, `harbor`, `foster`

**Imprecise word choices** — flag the following specific substitutions as `[WARN]`:
- `calculation` in a mathematical or algorithmic context → prefer `computation`. "Calculation" implies arithmetic; "computation" covers algorithmic processing.
- `given` as an adjective meaning "provided" (e.g., "the given trajectory") → prefer `provided`. ("Given an initial state, ..." as a conditional is acceptable.)
- `gives` meaning "produces" or "provides" (e.g., "this gives us X") → prefer `provides` or `yields`.
- `dynamic` as a filler adjective for anything that changes over time (e.g., "dynamic human motion") → be specific; prefer "arbitrary", "time-varying", or "changing".
- `verifiable safety` → prefer `formal safety guarantees` or `provably safe`.
- `re-define` when extending rather than replacing (e.g., "we re-define the cost function") → prefer `extend` or `incorporate`.
- `use-case` (hyphenated) as a standalone noun → prefer `use case` (two words, no hyphen).
- `computationally intensive` → prefer `computationally expensive`.

**Possessive form**: prefer "of" over "'s" when referring to inanimate objects or concepts (e.g., "the speed of the robot" not "the robot's speed"). Exception: proper human names (e.g., "Lyapunov's stability theorem").
- `[WARN]` for `TERM's NOUN` where TERM is a technical concept, algorithm name, or entity (e.g., "the agent's action" → "the action of the agent"). `[MIX]`
- `[INFO]` flag each `'s` possessive applied to a non-person noun for author review. `[MIX]`

#### 5.6 Quantitative claims

A quantitative result stated in prose must be immediately supported by a number in the same sentence.
- `[WARN]` if a comparative or superlative claim appears without an accompanying number in the same sentence: e.g., "our method significantly outperforms the baseline" without a percentage, ratio, or absolute value following it. `[VIBE]`
- `[WARN]` if "state-of-the-art" is claimed without a citation or numeric comparison. `[MIX]`

#### 5.7 Compound adjectives

Compound adjectives before a noun must be hyphenated.
- `[WARN]` for common unhyphenated compound adjectives before a noun, e.g.: `safety critical` → `safety-critical`, `real world` → `real-world`, `long horizon` → `long-horizon`, `state of the art` → `state-of-the-art`, `high frequency` → `high-frequency`, `data driven` → `data-driven`, `end to end` → `end-to-end`, `high dimensional` → `high-dimensional`, `long term` → `long-term`, `short term` → `short-term`. `[MIX]`
- `[WARN]` if "soft-actor-critic" or similar algorithm names are hyphenated when standing alone as a noun rather than as a compound modifier before another noun. `[MIX]`
- `[INFO]` if a compound noun standing alone (not before another noun) is hyphenated unnecessarily (e.g., "use-case" as a standalone noun). `[MIX]`

#### 5.8 Overused sentence openers

- `[INFO]` if "Note that" is used more than once per section. It should be reserved for genuinely non-obvious implications — flag each use for author review. `[HARD]`
- `[INFO]` if a paragraph ends with a boilerplate closing sentence that adds no content (e.g., "This concludes our discussion of X.", "In summary, we have shown..."). These are rarely needed and often pad length. `[VIBE]`

#### 5.9 Redundancy

- `[WARN]` if the same information is conveyed twice in adjacent sentences or consecutive paragraphs without adding new detail. `[VIBE]`
- `[WARN]` if a figure caption repeats verbatim something already stated in the immediately preceding paragraph. `[VIBE]`
- `[WARN]` if numbers from a table are repeated verbatim in the text narrative that directly follows the table. `[VIBE]`

#### 5.10 Strong claims and unsupported statements

- `[WARN]` if a claim uses "prove", "guarantee", "ensure", or "verify" without a formal proof, theorem, or direct citation. Flag each occurrence and note the missing backing. `[HARD]`
- `[WARN]` if the paper states that something "cannot" be done or "is impossible" without a citation or proof. `[HARD]`
- `[WARN]` if a conclusion or result is stated as general ("in any environment", "for all cases") when the experiments only covered one or two specific settings. `[VIBE]`
- `[INFO]` if a result that is mathematically trivial is presented as a significant finding without qualification. `[VIBE]`

#### 5.11 Parameter values in method sections

- `[WARN]` if a specific numerical value (e.g., `200 ms`, `250 Hz`, `0.4 rad`) appears in the method description section rather than in the experimental setup section or a parameter table. Method sections should use symbolic parameter names (e.g., `\Delta T`, `f_{\text{shield}}`); concrete values belong in the experiments section. `[MIX]`
- `[WARN]` if the `siunitx` package is not used, e.g., \SI{200}{\milli \second}. `[HARD]`

#### 5.12 Enumeration markers

- `[WARN]` if "First, ...", "Second, ...", "Third, ..." enumeration markers are used when the corresponding items are more than one paragraph apart. When items are spread across multiple paragraphs, readers lose the thread — use subsections or an itemize list instead. `[MIX]`

---

### Check 6: Abbreviations

**Goal**: Verify that every abbreviation is introduced correctly, used consistently, has the right article, and that the abstract is self-contained.

#### 6.1 Collect all abbreviations

Scan the full document for abbreviations. An abbreviation is any sequence of 2 or more uppercase letters (optionally mixed with digits), e.g., `RL`, `MDP`, `SAC`, `HER`, `STP`, `DoF`. Also collect any terms defined via LaTeX acronym packages (`\ac{}`, `\acp{}`, `\acf{}`, `\acl{}`, `\acs{}`, `\newacronym{}`).

Build two lists:
- **Abstract abbreviations**: all abbreviations appearing in the abstract
- **Body abbreviations**: all abbreviations appearing in the main body (everything after the abstract)

#### 6.2 Check the abstract

The abstract is a standalone piece of text and must introduce its own abbreviations independently of the main body.

For each abbreviation in the abstract:
- `[ERROR]` if it is used without being introduced in the abstract itself (pattern: full term followed by abbreviation in parentheses, e.g., `reinforcement learning (RL)`) `[MIX]`
- `[ERROR]` if it is introduced more than once in the abstract `[HARD]`
- `[WARN]` if it is introduced in the abstract but only used once (introduction unnecessary) `[MIX]`

#### 6.3 Check first use in the main body

For each abbreviation in the body:
- Find the first occurrence in document order (follow `\input`/`\include` chain).
- `[ERROR]` if the first occurrence is bare (e.g., `RL` appears) without a prior or inline introduction of the form `full term (ABBREV)`. This applies even if the abbreviation was introduced in the abstract — the main body must introduce it independently. `[MIX]`
- `[ERROR]` if the abbreviation appears in a section heading before it has been introduced in body text. `[HARD]`
- `[INFO]` if the introduction pattern deviates from `full term (ABBREV)` (e.g., abbreviation introduced before the full term). `[MIX]`

#### 6.4 Check subsequent uses in the main body

After the introduction, the full term must not be written out again — the abbreviation must be used exclusively.

- `[WARN]` for each occurrence of the full term (case-insensitive) after the introduction point, where the abbreviation should have been used instead. `[MIX]`
- `[ERROR]` if the abbreviation is introduced more than once in the main body (e.g., `neural network (NN)` appears a second time after the first body introduction). Note: one introduction in the abstract and one in the body is correct and expected — this error only fires for a second introduction within the body itself. `[HARD]`

#### 6.5 Check article agreement

For each occurrence of `a ABBREV` or `an ABBREV` (case-insensitive), check whether the article matches the pronunciation of the first letter of the abbreviation as a spelled-out letter name.

Letters whose names begin with a vowel sound → require `an`:
`A` (AY), `E` (EE), `F` (EF), `H` (AY-TCH), `I` (EYE), `L` (EL), `M` (EM), `N` (EN), `O` (OH), `R` (AR), `S` (ESS), `X` (EX)

All other letters → require `a`.

**Exception**: if the abbreviation is pronounced as a word rather than spelled out (e.g., `NASA`, `LASER`), use the pronunciation of the word itself, not the first letter name. Use context and common knowledge to judge this.

- `[ERROR]` if the article does not match the rule above (e.g., `a NN` → should be `an NN`). `[MIX]`

#### 6.6 Check plural formation

Plurals of abbreviations are formed by appending a lowercase `s` directly: `NNs`, `MLPs`, `STPs`.

- `[ERROR]` if a possessive apostrophe is used to form a plural: `NN's`, `MLP's` `[HARD]`
- `[WARN]` if the full term is pluralized after the abbreviation has been introduced (e.g., `neural networks` instead of `NNs`) `[MIX]`

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

After all checks are complete, produce a single Markdown report. Follow the structure defined in `templates/output_template.md` exactly — use it as the skeleton and fill in every placeholder.

### Report structure summary

1. **Header**: paper title, date, source path.
2. **Scorecard**: one row per check with separate Errors / Warnings / Info / Total columns.
3. **Overall Assessment** (immediately after the scorecard):
   - A 2–4 sentence paragraph on the overall quality: strongest areas and most critical weaknesses.
   - A **Top Issues to Address** list of the 3–6 most impactful issues across all checks, ordered by impact. Format: `[SEVERITY] Check N.x — description`. This gives the author a quick action list before reading the full details.
4. **Per-check sections** (one per check):
   - **Summary**: 1–2 sentences on the key findings for that check (e.g., "All abbreviations are correctly introduced. However, three `a NN` article errors and one double introduction were found.").
   - **Findings**: individual findings in finding format (see below). Write "No issues found." if the check is clean.

### Finding Format

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

### PDF generation

After writing the Markdown report, automatically convert it to PDF by running:

```bash
python ~/.claude/skills/proofreading/scripts/generate_report_pdf.py <report.md>
```

Run this as the final step of report mode. If the script fails (missing `pandoc` or LaTeX), print the error and note that the Markdown report is still complete and readable. The LaTeX template is at `~/.claude/skills/proofreading/templates/report_latex.tex`.
