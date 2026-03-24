# agent-pipeline

Remote-first pipeline for downloading multimodal datasets online, extracting unified samples, and producing cleaning / rewrite / review records.

## Current status (2026-03-24)

This repo has now moved beyond basic remote-only setup and into a more complete **all-candidate remote intake** stage.

### What is now working

- Default workflow is remote-first
- Hugging Face access works through the local proxy on this machine
- GitHub source ingestion works
- The following previously broken candidate connectors have now been fixed:
  - `MathVision` image materialization (`decoded_image` now becomes a real image asset)
  - `Multi-Physics` GitHub JSON layout (`example[]` support)
  - `MM-Math` raw-file fallback (`MM_Math.jsonl + MM_Math.zip`)
  - `PhysReason` raw-zip fallback (`PhysReason-mini.zip` / `PhysReason-full.zip` + `problem.json` extraction)

### Full candidate smoke status

The all-candidate remote smoke config is:

- `configs/all_candidates_remote.yaml`

A full smoke run was completed after the connector fixes.

Latest archived run summary:
- `tmp/agent-pipeline_run_archive_2026-03-24_1023/outputs/all_candidates_remote_smoke/run_34f55dd2baab488b/summary.json`

Current small-sample outcome snapshot:

- `SCEMQA` → available, but current samples reject
- `Geometry3K` → available, mixed review / reject
- `CMM-Math` → available, review-heavy, often `split_open`
- `MathVision` → available, mixed review / reject, connector fixed
- `MM-Math` → available, current small samples pass
- `SeePhys` → available, mixed pass / reject
- `Multi-Physics` → available, mixed pass / reject
- `PhysReason` → available, mixed pass / reject
- `EEE-Bench` → available, current small samples pass
- `EMMA-Math` → available, current small samples pass
- `EMMA-Physics` → available, current small samples pass

### 200-sample cross-subject benchmark

A larger cross-subject benchmark was also completed.

- Config: `configs/candidate_200_remote.yaml`
- Report: `docs/candidate_200_benchmark_report.md`
- Output summary: `outputs/candidate_200_remote/run_6be16173d2403a7e/summary.json`

Headline numbers:
- 200 / 200 processed
- wall-clock time: **195s**
- average throughput: **0.975 s/sample**
- strict usable (`pass`): **90 / 200 = 45.0%**
- lenient usable (`pass + review`): **116 / 200 = 58.0%**

Best current performers in this setup:
- `EEE-Bench`
- `PhysReason`
- `CMM-Math`

Most likely to need source-specific threshold tuning next:
- `Geometry3K`
- `SCEMQA`
- `SeePhys`
- parts of `MathVision`

### High-level rewrite pattern snapshot

Observed from current smoke samples:

- `blank_open`
  - common in `EEE-Bench`, `EMMA-*`, `Geometry3K`, parts of `MathVision`, `SCEMQA`
- `keep_open`
  - common in `MM-Math`, `PhysReason`, `SeePhys`, `Multi-Physics`, parts of `MathVision`
- `split_open`
  - common in `CMM-Math`

This means the current bottleneck is no longer connector availability for most candidate datasets. The focus has shifted to:
- source-specific quality thresholds
- rewrite-policy alignment by question type
- better handling of mixed open-ended vs option-style multimodal questions

## Current default mode

This repo now uses a **remote-only default workflow**.

The shipped multi-dataset config is:

- `configs/multi_dataset_iter.yaml`

It pulls datasets online from:
- GitHub
- Hugging Face

## Proxy requirement on this machine

GitHub is reachable directly, but Hugging Face currently needs the local proxy:

```bash
export http_proxy=http://127.0.0.1:20171
export https_proxy=http://127.0.0.1:20171
```

Then run:

```bash
python3 benchmark/src/multidataset_cleaning_pipeline.py --config configs/multi_dataset_iter.yaml
```

## Main entrypoints

### Default remote iteration config

```bash
python3 benchmark/src/multidataset_cleaning_pipeline.py --config configs/multi_dataset_iter.yaml
```

### All-candidate remote smoke config

```bash
python3 benchmark/src/multidataset_cleaning_pipeline.py --config configs/all_candidates_remote.yaml
```

## Current default dataset set

The default remote iteration config currently includes:

- `EEE-Bench`
- `CMM-Math`
- `Geometry3K`
- `MathVision`

## Outputs

Representative summaries are retained under:

- `docs/run_summaries/`

Larger experimental outputs are written under `outputs/` during runs, and temporary/archived runs may be moved under:

- `tmp/agent-pipeline_run_archive_*`

## Notes

- The code still contains local-file support internally, but the repo’s default workflow and retained configs are now remote-first.
- If Hugging Face requests start failing, first check whether the local proxy at `127.0.0.1:20171` is still available.
- Cache directories under `outputs/repo_cache/` are not part of the intended committed source-of-truth.
