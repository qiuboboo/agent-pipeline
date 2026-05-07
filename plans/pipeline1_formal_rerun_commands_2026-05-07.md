# pipeline1 formal rerun commands

Date: 2026-05-07

## Environment

- conda env: `agent`
- base_url: `https://www.msutools.cn/v1`
- model: `gpt-5.4`

## Recommended run commands

Set API key first in PowerShell:

```powershell
$env:OPENAI_API_KEY="YOUR_KEY"
```

### ai2d

```powershell
conda run -n agent python -m src.benchmarkallinone.pipeline --config configs/ai2d_rerun_1000_3000.yaml
```

### geoqa_plus

```powershell
conda run -n agent python -m src.benchmarkallinone.pipeline --config configs/geoqa_plus_rerun_2000_3000.yaml
```

### multi_physics

```powershell
conda run -n agent python -m src.benchmarkallinone.pipeline --config configs/multi_physics_rerun_0912_1412.yaml
```

### physreason

```powershell
conda run -n agent python -m src.benchmarkallinone.pipeline --config configs/physreason_rerun_0000_0300.yaml
```

### mm_math

```powershell
conda run -n agent python -m src.benchmarkallinone.pipeline --config configs/mm_math_rerun_0300_4000.yaml
```

## Resume commands

### Resume from a known run dir

```powershell
conda run -n agent python -m src.benchmarkallinone.pipeline --config CONFIG_PATH --resume-from-run-dir OUTPUT_ROOT/run_xxx
```

### Resume from a previous log

```powershell
conda run -n agent python -m src.benchmarkallinone.pipeline --config CONFIG_PATH --resume-from-log PATH_TO_LOG
```

## Notes

- `ai2d` uses `test[1000:3000]`
- `geoqa_plus` uses `test[2000:3000]`
- `multi_physics`, `physreason`, `mm_math` rely on `sample_offset`
- `mm_math` now has a preparsed cache under `outputs/repo_cache/hf_raw/mm_math/preparsed_samples_v1.jsonl`
