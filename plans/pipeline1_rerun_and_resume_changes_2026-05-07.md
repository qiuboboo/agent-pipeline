# pipeline1 rerun / resume changes

Date: 2026-05-07

## Code changes

- `src/benchmarkallinone/pipeline.py`
  - Added `sample_offset` support through all major sampling paths.
  - Added `mm_math` preparsed cache at `outputs/repo_cache/hf_raw/mm_math/preparsed_samples_v1.jsonl`.
  - Added resume support from:
    - `--resume-from-run-dir`
    - `--resume-from-log`
  - Resume now records `resume` and `resume_from_run_dir` in pipeline summary.
  - Fixed Hugging Face sliced splits so that when a dataset row has no native `id/problem_id`, `source_problem_id` uses `slice_start + local_index` instead of restarting from `0` inside `test[START:END]`.

- `scripts/build_ready_from_outputs_content_dedup.py`
  - Updated default global `source_problem_id` dedup dataset set to match the audit conclusion.

## Rerun configs

- `configs/ai2d_rerun_1000_3000.yaml`
- `configs/geoqa_plus_rerun_2000_3000.yaml`
- `configs/multi_physics_rerun_0912_1412.yaml`
- `configs/physreason_rerun_0000_0300.yaml`
- `configs/mm_math_rerun_0300_4000.yaml`

## Verification highlights

- `ai2d` smoke verification:
  - `source_split=test[1000:3000]`
  - `source_problem_id=1000`
- `geoqa_plus` smoke verification:
  - `source_split=test[2000:3000]`
  - `source_problem_id=2000`
- `multi_physics` smoke verification:
  - `source_problem_id=912`
- `physreason` smoke verification:
  - `source_problem_id=cal_problem_00035`
- `mm_math` smoke verification:
  - `source_problem_id=53010111.png`

## Smoke-test plan

For each rerun dataset:

- Run a temporary 1-sample smoke test.
- Check:
  - `source_problem_id`
  - `problem_id`
  - `source_split`
  - `open_ended_problem_variants[].open_variant_id`

Then verify resume using:

- `--resume-from-run-dir`
- `--resume-from-log`
