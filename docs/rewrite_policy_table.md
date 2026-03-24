# Rewrite Policy Table (working draft)

_Last updated: 2026-03-24_

This is a practical, current-state summary derived from the all-candidate remote smoke run after connector fixes. It is not the final policy, but it is strong enough to guide the next round of rewrite alignment.

## Core principle

Do **not** route all multiple-choice-looking questions through one rewrite path.

Instead, prefer:
- `blank_open` for standard visual choice questions with a single clear target
- `keep_open` for naturally open-ended, multi-step, or already-open problem forms
- `split_open` for structured mathematical targets that naturally decompose

---

## Dataset-level table

| Dataset | Typical current form | Image dependence | Common answer form | Current dominant rewrite | Current outcome snapshot | Suggested policy |
|---|---|---:|---|---|---|---|
| SCEMQA | visual science/math question, short prompt | high | numeric | `blank_open` | reject-heavy in current small smoke | keep `blank_open`, but inspect threshold/quality and whether some samples are already open-style |
| Geometry3K | short geometry prompt like “Find x” | high | numeric | `blank_open` | mixed review/reject | keep `blank_open`, but likely needs source-specific quality relaxation |
| CMM-Math | text math, set/range/structured targets | low | set / range | `split_open` | review-heavy | keep `split_open`; this is currently the clearest split-open dataset |
| MathVision | mixed visual numeric + visual option questions | high | numeric / option | mixed `keep_open` + `blank_open` | mixed review/reject | branch by answer form and question style; do not force one rewrite path |
| MM-Math | diagram-grounded math solution problems | high | open solution / set | `keep_open` | pass-heavy in current small smoke | keep `keep_open`; avoid forcing into blank-open style |
| SeePhys | physics open questions with figures | high | short_text / numeric | `keep_open` | mixed pass/reject | keep `keep_open`; quality threshold still matters |
| Multi-Physics | physics questions with options but reasoning-heavy text | high | option | `keep_open` | mixed pass/reject | currently safer as `keep_open`; revisit after more examples |
| PhysReason | long context + multi-subquestion physics reasoning | high | short_text / set | `keep_open` | mixed pass/reject | keep `keep_open`; this is structurally multi-subquestion |
| EEE-Bench | standard engineering MCQ with figure | high | option | `blank_open` | pass-heavy | keep `blank_open`; strong positive-control dataset |
| EMMA-Math | visual choice / spatial/math figure tasks | high | option | `blank_open` | pass-heavy | keep `blank_open` |
| EMMA-Physics | visual physics choice / ray/path tasks | high | short_text / option-like answer target | `blank_open` | pass-heavy | keep `blank_open` |

---

## Current rule sketch by question type

### 1. Standard visual choice question
**Use:** `blank_open`

Typical signs:
- one image or one figure
- one target quantity / one choice target
- classic MCQ wording
- options are distractors, not true subproblems

Examples:
- EEE-Bench
- EMMA-Math
- EMMA-Physics
- some Geometry3K / MathVision samples

---

### 2. Naturally open numeric or derivation problem
**Use:** `keep_open`

Typical signs:
- already asks for a numeric result or derivation
- option letters are absent or not semantically central
- forcing a blank-open transform adds little value

Examples:
- MM-Math
- some MathVision numeric items
- some SeePhys items

---

### 3. Multi-subquestion structured reasoning
**Use:** `keep_open`

Typical signs:
- explicit sub-question list
- one context with multiple targets
- answer is a list/tuple/set of results
- strong multi-step dependency across subparts

Examples:
- PhysReason

---

### 4. Structured mathematical target decomposition
**Use:** `split_open`

Typical signs:
- range / set / interval answers
- composite algebraic target
- one multiple-choice shell but multiple internal target components
- splitting makes annotation and verification easier

Examples:
- CMM-Math

---

## Current operational cautions

### Do not blindly trust “looks like MCQ”
Some datasets contain question bodies that look like MCQ, but semantically behave like open problems.

### Do not treat image presence as enough reason for `blank_open`
Some image-grounded problems are still better preserved as open-ended questions.

### Quality gate is still a confounder
Some datasets are underperforming not because the rewrite strategy is wrong, but because samples are being rejected due to:
- `low_resolution`
- `low_text_completeness`

Most affected right now:
- SCEMQA
- Geometry3K
- MathVision
- parts of PhysReason / SeePhys / Multi-Physics

---

## Immediate next policy tasks

1. Add source-specific threshold overrides for low-resolution-heavy sources.
2. Build a small answer-type + question-form classifier before rewrite.
3. Separate these classes explicitly before rewrite:
   - option-style visual MCQ
   - open numeric visual question
   - multi-subquestion reasoning problem
   - structured set/range math problem
4. Re-run all-candidate smoke after threshold tuning and compare rewrite distribution shifts.

---

## Proposed rewrite-policy changes (documented, not yet implemented)

This section records the current recommended rewrite-policy adjustments before code changes are made.

### Why change the current policy

The main issue is **not** that the rewrite prompt is too weak.
The bigger issue is that the current routing is too coarse.

At the moment, the fallback logic is still roughly:
- no choices -> `keep_open`
- pure image-index choice -> `drop_image_index`
- compound answer -> `split_open`
- otherwise with choices -> default to `blank_open`

That last default is too aggressive. It pushes many questions that only *look* like MCQ into the same `blank_open` path, even when they are semantically closer to naturally open-ended, multi-step, or structured-target problems.

---

## Proposed rewrite classes

### 1. Standard visual choice question
**Recommended strategy:** `blank_open`

Typical signs:
- one image or one figure
- one target quantity or one target concept
- classic MCQ wording
- options act as distractors rather than true subproblems

Typical datasets:
- `EEE-Bench`
- `EMMA-Math`
- `EMMA-Physics`
- part of `Geometry3K`
- part of `MathVision`

---

### 2. Naturally open numeric / derivation problem
**Recommended strategy:** `keep_open`

Typical signs:
- already asks for a value, derivation, or conclusion directly
- even if choices exist in the source, the real semantic target is still open-ended
- converting to blank-open adds little value compared with preserving the original structure

Typical datasets:
- `MM-Math`
- part of `MathVision`
- part of `SeePhys`
- part of `Multi-Physics`

---

### 3. Multi-subquestion structured reasoning problem
**Recommended strategy:** `keep_open`

Typical signs:
- explicit sub-question list
- one shared context with multiple targets
- answer is naturally a list / tuple / multi-line result
- strong dependency between subparts

Typical datasets:
- `PhysReason`

Notes:
- do not force these into `blank_open`
- do not split into separate problems by default unless later workflow explicitly wants subproblem extraction

---

### 4. Structured mathematical target decomposition
**Recommended strategy:** `split_open`

Typical signs:
- set / interval / range answers
- one shell question but multiple target components internally
- splitting improves annotation and verification

Typical datasets:
- `CMM-Math`
- part of `SCEMQA`

---

### 5. Pure image-index choice
**Recommended strategy:** `drop_image_index`

Typical signs:
- question depends on picking one image / figure index
- option semantics are not meaningfully textualized
- rewrite would be brittle or degenerate

---

## Proposed dataset priors

These priors are meant to be **weak routing preferences**, not hard-coded irreversible rules.

### Prefer `blank_open`
- `EEE-Bench`
- `EMMA-Math`
- `EMMA-Physics`
- `Geometry3K` (default preference, but allow exceptions)

### Prefer `keep_open`
- `MM-Math`
- `SeePhys`
- `Multi-Physics`
- `PhysReason`

### Prefer `split_open`
- `CMM-Math`

### Must branch by question form
- `MathVision`
- `SCEMQA`

---

## Proposed high-priority dataset-specific changes

### MathVision
Current observation:
- visual numeric questions often behave better as `keep_open`
- standard visual option questions often behave better as `blank_open`

Suggested branch:
- if the question looks like "how many", "which number", "what value", "calculate", "determine" and the answer is numeric / expression -> `keep_open`
- if the question is a standard object / figure discrimination question -> `blank_open`

### SCEMQA
Current observation:
- current smoke shows a mix of `blank_open` and `split_open`
- many current samples still reject, so rewrite and quality remain confounded

Suggested branch:
- numeric single-target items -> `blank_open`
- set / range / structured-target items -> `split_open`
- do not default all SCEMQA items to the same path

### Geometry3K
Current observation:
- many items still look like short visual numeric targets such as "Find x"
- current weakness seems more related to thresholding / quality than rewrite itself

Suggested policy:
- keep `blank_open` as the main default
- do **not** make large rewrite-policy changes yet
- prioritize threshold / quality analysis first

---

## Proposed lightweight classifier functions

Before rewrite, the pipeline should ideally classify a sample using a few explicit checks.

### `is_multi_subquestion(question_text)`
Detects:
- `1. 2. 3.` style subparts
- `sub-question` wording
- `(1)(2)(3)` style decomposition

Suggested action:
- route to `keep_open`

### `is_set_or_range_target(answer_text, answer_type)`
Detects:
- intervals / ranges / unions / set-style outputs
- common mathematical solution-set patterns

Suggested action:
- route to `split_open`

### `is_visual_numeric_open(question_text, answer_type, choices)`
Detects:
- `how many`
- `which number`
- `what value`
- `calculate`
- `determine`
- numeric or expression-style target

Suggested action:
- route to `keep_open`

### `is_standard_visual_mcq(question_text, choices, answer_type)`
Detects:
- standard single-target visual MCQ form
- options are textual distractors rather than multiple internal objectives

Suggested action:
- route to `blank_open`

### `dataset_prior(dataset_name)`
Provides a weak prior preference by dataset family.

Suggested action:
- use only as a tie-breaker, not as a hard override against obvious question-form evidence

---

## Proposed rewrite decision order

1. pure image-index choice -> `drop_image_index`
2. multi-subquestion structure -> `keep_open`
3. set / range / structured target -> `split_open`
4. visual numeric open-style question -> `keep_open`
5. strong dataset prior toward `keep_open` and no clear standard-MCQ evidence -> `keep_open`
6. standard visual MCQ -> `blank_open`
7. fallback default -> `blank_open`

---

## Proposed first implementation targets

If only a few changes are made first, the highest-value ones appear to be:

1. remove the overly broad rule that effectively means "has choices -> default `blank_open`"
2. add explicit handling for:
   - `PhysReason` -> `keep_open`
   - `CMM-Math` -> `split_open`
3. add mixed-form routing for `MathVision`

These changes are **recommended next**, but are intentionally only documented here for now.
