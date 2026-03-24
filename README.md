# agent-pipeline

Remote-first pipeline for downloading multimodal datasets online, extracting unified samples, and producing cleaning / rewrite / review records.

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

## Current default dataset set

The default remote iteration config currently includes:

- `EEE-Bench` — strongest remote positive-control dataset right now
- `CMM-Math` — stable enough for remote iteration
- `Geometry3K` — downloadable and usable, but often quality-gated by `low_resolution`

## Why MathVision is not in the default config

MathVision was tested online and the source data **does include image fields**:
- `image`
- `decoded_image`

But in the current pipeline path, those images are **not being materialized into output image assets** reliably, which leads to:
- `image_count = 0`
- `missing_core_image`
- cleaning-stage reject

So MathVision is currently treated as a connector / asset-materialization issue, not a source-availability issue.

## Main entrypoint

Use the benchmark YAML runner for multi-dataset execution:

```bash
python3 benchmark/src/multidataset_cleaning_pipeline.py --config configs/multi_dataset_iter.yaml
```

## Outputs

Representative summaries are retained under:

- `docs/run_summaries/`

Larger experimental outputs are written under `outputs/` during runs.

## Notes

- The code still contains local-file support internally, but the repo’s default workflow and retained configs are now remote-first.
- If Hugging Face requests start failing, first check whether the local proxy at `127.0.0.1:20171` is still available.
