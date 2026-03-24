# Candidate 200 Remote Benchmark Report

_Date: 2026-03-24_

## Run

- Config: `configs/candidate_200_remote.yaml`
- Output: `outputs/candidate_200_remote/run_6be16173d2403a7e/summary.json`
- Scope: 10 datasets × 20 samples each = 200 requested samples

## Timing

- Wall-clock time: **195 seconds**
- Requested samples: **200**
- Processed samples: **200**
- Average wall-clock per processed sample: **0.975 s/sample**

## Overall outcome

- Pass: **90**
- Review: **26**
- Reject: **84**

### Availability views

- **Strict usable (pass only):** 90 / 200 = **45.0%**
- **Lenient usable (pass + review):** 116 / 200 = **58.0%**

---

## Per-dataset results

| Dataset | Subject | Requested | Processed | Pass | Review | Reject | Strict usable | Lenient usable | Main rewrite mix |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| SCEMQA | science | 20 | 20 | 3 | 0 | 17 | 15.0% | 15.0% | `blank_open:11`, `split_open:9` |
| Geometry3K | math | 20 | 20 | 0 | 4 | 16 | 0.0% | 20.0% | `blank_open:10`, `candidate_reject:10` |
| CMM-Math | math | 20 | 20 | 13 | 6 | 1 | 65.0% | 95.0% | `blank_open:13`, `split_open:7` |
| MathVision | math | 20 | 20 | 11 | 3 | 6 | 55.0% | 70.0% | `keep_open:13`, `blank_open:6`, `split_open:1` |
| MM-Math | math | 20 | 20 | 10 | 0 | 10 | 50.0% | 50.0% | `keep_open:20` |
| SeePhys | physics | 20 | 20 | 4 | 0 | 16 | 20.0% | 20.0% | `keep_open:20` |
| Multi-Physics | physics | 20 | 20 | 11 | 0 | 9 | 55.0% | 55.0% | `keep_open:20` |
| PhysReason | physics | 20 | 20 | 15 | 0 | 5 | 75.0% | 75.0% | `keep_open:20` |
| EEE-Bench | engineering | 20 | 20 | 15 | 4 | 1 | 75.0% | 95.0% | `blank_open:8`, `keep_open:8`, `split_open:3`, `drop_image_index:1` |
| EMMA-Physics | physics | 20 | 20 | 8 | 9 | 3 | 40.0% | 85.0% | `blank_open:11`, `split_open:9` |

---

## Per-subject aggregate

| Subject | Datasets | Processed | Pass | Review | Reject | Strict usable | Lenient usable |
|---|---:|---:|---:|---:|---:|---:|---:|
| science | 1 | 20 | 3 | 0 | 17 | 15.0% | 15.0% |
| math | 4 | 80 | 34 | 13 | 33 | 42.5% | 58.75% |
| physics | 4 | 80 | 38 | 9 | 33 | 47.5% | 58.75% |
| engineering | 1 | 20 | 15 | 4 | 1 | 75.0% | 95.0% |

---

## Quick takeaways

### Strongest current datasets under this setup
By strict pass rate on this 200-sample run:
- **PhysReason**: 75.0%
- **EEE-Bench**: 75.0%
- **CMM-Math**: 65.0%
- **MathVision**: 55.0%
- **Multi-Physics**: 55.0%
- **MM-Math**: 50.0%

### Most promising by lenient usable rate (pass + review)
- **EEE-Bench**: 95.0%
- **CMM-Math**: 95.0%
- **EMMA-Physics**: 85.0%
- **PhysReason**: 75.0%
- **MathVision**: 70.0%

### Currently weakest under default thresholds
- **SCEMQA**: 15.0% strict / 15.0% lenient
- **Geometry3K**: 0.0% strict / 20.0% lenient
- **SeePhys**: 20.0% strict / 20.0% lenient

---

## Rewrite-pattern observations from this run

### Predominantly `keep_open`
- `MM-Math`
- `SeePhys`
- `Multi-Physics`
- `PhysReason`
- much of `MathVision`

These datasets behave more like naturally open or multi-step problems than standard single-target visual MCQ.

### Predominantly `blank_open`
- `EEE-Bench` (though not exclusively)
- much of `SCEMQA`
- part of `Geometry3K`
- part of `MathVision`

These are closer to standard visual-choice to open-question rewriting.

### Predominantly `split_open`
- `CMM-Math` (partial but important)
- `EMMA-Physics` (substantial share)
- part of `SCEMQA`

These often reflect structured targets or decomposable question forms.

---

## What this means right now

1. **Connector coverage is no longer the main blocker** for the currently reachable candidate set.
2. The next bottleneck is clearly **source-specific quality / thresholding** plus **rewrite-policy branching**.
3. A single rewrite path is not adequate across datasets.
4. The best current positive-control sources for continued iteration are:
   - `EEE-Bench`
   - `PhysReason`
   - `CMM-Math`
5. The datasets that most likely need threshold or source-specific handling next are:
   - `Geometry3K`
   - `SCEMQA`
   - `SeePhys`
   - parts of `MathVision`

---

## Suggested next step

Run a source-specific quality analysis focused on:
- `low_resolution`
- `low_text_completeness`
- candidate-intake reject patterns
- whether `Geometry3K`, `SCEMQA`, and `SeePhys` need threshold overrides
