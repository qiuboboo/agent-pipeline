# Pipeline Overview

This document outlines the current state of the pipeline implemented based on `multidataset_cleaning_pipeline.py`.

---

## Key Features

1. **Modular Record Layering**
   - Record types implemented:
     - `problem_main_record`: Summarizes the main details of each processed problem, including question text, multimodal scores, and decision outcomes (`pass`, `review`, `reject`).
     - `asset_record`: Captures asset-level references like associated images.
     - `alignment_record`: Tracks basic alignment details for image-text consistency.
     - `rewrite_report`: Details the rewrite strategy applied to each problem.
     - `open_ended_problem_variants`: Generates new open-ended variants, if applicable.
     - `cleaning_record`: Consolidates decisions, rewrite summaries, and alignment outcomes.
     - `field_audit_record`: Logs transformation steps.
     - `summary.json`: Provides a summary with distribution counts (decision, rewrite).

2. **Rewrite Strategies**
   - Rewrite strategies (`rewrite_strategy`):
     - `blank_open`: Converts multiple-choice questions into blank-style open-ended questions.
     - `drop_image_index`: Rejects pure image-index choice questions.
     - `keep_open`: Directly accepts questions as open-ended.
     - `split_open`: Splits compound answers into multiple open-ended components.

3. **Input Format Compatibility**
   - Compatible with both `.json` and `.jsonl` formats, maintaining consistent outputs.

4. **Decision Gates**
   - Pass/review/reject decisions based on:
     - `multimodal_necessity`
     - `node_decomposability`
     - `answer_stability`
     - Rewrite strategy and alignment quality.

---

## Pipeline Outputs

### Record Files

- `problem_main_records.jsonl`
- `asset_records.jsonl`
- `alignment_records.jsonl`
- `rewrite_reports.jsonl`
- `open_ended_problem_variants.jsonl`
- `cleaning_records.jsonl`
- `field_audit_records.jsonl`
- `summary.json`: Example `summary.json`:

```json
{
  "pipeline_run_id": "candidate-clean_<TIMESTAMP>",
  "input_path": "<INPUT_PATH>",
  "processed_samples": 10,
  "decision_counts": {
    "pass": 4,
    "review": 1,
    "reject": 5
  },
  "rewrite_strategy_counts": {
    "blank_open": 5,
    "drop_image_index": 5
  }
}
```

---

## Next Steps

1. Run full `mini_test` dataset (35 samples) to:
   - Validate `pass`, `review`, `reject` distributions.
   - Inspect correctness of `rewrite_strategy` and edge-case handling.

2. Refine gate thresholds and alignment logic based on validation results.