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
