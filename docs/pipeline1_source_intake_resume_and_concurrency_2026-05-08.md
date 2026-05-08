# Pipeline1 Source-Intake Resume And Concurrency

Date: 2026-05-08

## What changed

Pipeline1 now uses `runtime.sample_concurrency` in both places that can do expensive per-sample work:

- Source sampling / source-intake extraction now runs through `BaseConnector.collect_concurrently()`.
- Final sample processing still uses the same concurrency setting for `process_sample()`.
- Source-intake cache reads and appends are protected by locks, so concurrent workers can safely share the same cache file.
- `SourceIntakeAgent` initialization is locked, so concurrent workers do not race while creating the agent.

The source-intake cache is stored under:

```text
outputs/repo_cache/source_intake/<dataset_key>/<safe_split>_<locator_digest>.jsonl
```

Each cache row stores:

- `row_fingerprint`: fingerprint of dataset/source config plus the normalized raw row.
- `extracted`: extracted question, answer, choices, image fields and notes.
- `cached_at`: write time.

When a cached row is reused, the emitted source-intake record contains:

```text
source_intake_cache_hit
```

in `extraction_notes`.

## Resume behavior

`--resume` scans prior runs under the configured output root, collects completed `source_problem_id` values, and skips those samples before final processing.

`--rerun-missing-only` can also scan prior outputs or explicit reference output globs and only process source ids that are not already present.

Important distinction:

- `--resume` skips already completed samples by `source_problem_id`.
- Source-intake cache reuse is independent of `--resume`; it is keyed by row fingerprint and prevents re-running source field extraction for the same raw row.

## Dataset-specific notes

`multi_physics` source ids are now deterministic:

```text
<normalized_data_file_stem>_<zero_padded_row_index>
```

If the row has an `index` field, that value is used. Otherwise the file-local row index is used. This keeps ids stable when the full dataset is rerun.

`mm_math` raw JSONL preparsing now builds a preparsed cache with the same concurrency setting. Once built, later runs load the preparsed cache directly.

`physreason_rerun_0000_1200.yaml` replaces the earlier smaller rerun config and is set to:

```text
sample_offset: 0
sample_per_dataset: 1200
rerun_missing_only: true
rerun_reference_output_globs:
  - physreason_full_*
```

## Validation

Syntax check:

```text
python -m py_compile src\benchmarkallinone\pipeline.py
```

AI2D sample-level resume validation:

```text
conda run -n agent python -m src.benchmarkallinone.pipeline --config configs\ai2d_rerun_1000_3000.yaml --sample-per-dataset 1 --sample-concurrency 1 --disable-llm --resume
```

Observed:

- First resume test processed `source_problem_id=1000`.
- Second resume test skipped `1000` and processed `source_problem_id=1001`.
- Both runs used `0` LLM requests.

AI2D source-intake cache validation:

```text
conda run -n agent python -m src.benchmarkallinone.pipeline --config configs\ai2d_rerun_1000_3000.yaml --sample-per-dataset 1 --sample-concurrency 1 --disable-llm
```

Observed:

- Reprocessed the same first sample, `source_problem_id=1000`.
- Cache file line count stayed unchanged at `3`.
- Output source-intake record included `source_intake_cache_hit`.
- LLM request count stayed `0`.

This confirms source-intake can resume from its cache even without `--resume`.

