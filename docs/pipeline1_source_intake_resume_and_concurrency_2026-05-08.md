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

`mm_math` raw JSONL preparsing now supports range-targeted incremental cache build:

- For `sample_strategy=head`, target row indices are exactly `[sample_offset, sample_offset + sample_per_dataset)`.
- Existing row indices in preparsed cache are reused.
- Only missing row indices are parsed and appended.
- Window gaps are allowed (for example, running `300:320`, then `400:420` does not require building `320:400`).

This is tracked by per-entry `row_index`, and cache selection is by row index, not by contiguous blocks.

`HuggingFaceConnector` now includes a local Arrow fast path:

- It first checks local HuggingFace dataset cache directories and matching split Arrow shards.
- If local Arrow files exist, it loads from local Arrow (`Dataset.from_file` + concat) and applies split slicing locally.
- It falls back to `load_dataset()` only if local Arrow cache is not found/usable.

This avoids long stalls in builder/metadata/network phases when local cache is already complete.

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

MM-Math overlap/gap cache validation (`--disable-llm`, isolated temporary cache root):

- Run A: offset `300`, count `20` -> `built=20`.
- Run B: offset `310`, count `20` -> `built=10` (overlap reused, only `320:329` built).
- Run C: offset `400`, count `20` -> `built=20` (gap `330:399` not required and not built).

AI2D / GeoQA+ local Arrow integrity check:

- AI2D local arrow rows: `2844 + 244 = 3088`, matching `dataset_info.splits.test.num_examples=3088`.
- GeoQA+ local arrow rows: `train=18081`, `test=3040`, matching `dataset_info`.

AI2D / GeoQA+ 1-sample full run validation with local fast path (`--disable-llm`):

- AI2D (`test[1000:3000]`, 1 sample) completed in `~0.27s`.
- GeoQA+ (`test[2000:3000]`, 1 sample) completed in `~0.15s`.

Both runs passed source intake + sample processing end-to-end and did not stall in `load_dataset()`.
