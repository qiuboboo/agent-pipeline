# outputs 重复审计与重跑建议（2026-05-06）

## 口径说明

- 本次审计主要针对 `outputs/` 下各数据集分段目录的重复问题。
- 对于可以把 `source_problem_id` 视为题目唯一键的数据集，使用全局 `source_problem_id` 去重来评估“现有结果还能保留多少”。
- dry-run 统一通过 `conda --no-plugins run -n agent python scripts/build_ready_from_outputs_content_dedup.py --dry-run --dataset <dataset>` 执行。
- `physreason` 仍沿用脚本内的特殊策略，只看 `physreason_full_*` 体系。

## 脚本改动

- 已修改 [scripts/build_ready_from_outputs_content_dedup.py](/d:/Hallucination/workspace/agent-pipeline/scripts/build_ready_from_outputs_content_dedup.py:23)
- 对以下数据集默认启用“跨所有 outputs 目录，按 `source_problem_id` 全局去重”：
  - `ai2d`
  - `eee_bench`
  - `emma_physics`
  - `geoqa_plus`
  - `mm_math`
  - `msearth_open_ended`
  - `multi_physics`
- 新增参数：
  - `--global-source-id-dedup-dataset <dataset_key>`

## 已 dry-run 复核的数据集

### 1. ai2d

- scanned: `1901`
- unique after global source_problem_id dedup: `1000`
- duplicates: `901`
- 结论：`ai2d_1000_3000` 基本没有提供新的唯一题。

建议重跑：

- `1000:3000`

### 2. geoqa_plus

- scanned: `2245`
- unique after global source_problem_id dedup: `2000`
- duplicates: `245`
- 结论：`geoqa_plus_2000_5000` 当前已有部分没有提供新的唯一 coverage。

建议重跑：

- `2000:5000`

### 3. mm_math

- scanned: `3307`
- unique after global source_problem_id dedup: `1000`
- duplicates: `2307`
- 结论：后续多个分段存在明显重复取数，当前全局唯一 coverage 只有 `1000`。

建议重跑：

- `300:600`
- `600:900`
- `900:1500`
- `1500:2100`
- `2100:3000`
- `3000:4000`

说明：

- 现有 `mm_math` 各分段之间重复严重，不建议再信任目录名对应的 coverage。
- 更稳的做法是按你真正想要的目标区间重新切分重跑。

### 4. emma_physics

- scanned: `468`
- unique after global source_problem_id dedup: `156`
- duplicates: `312`
- 结论：当前最终只保住了 `emma_physics_300_500` 这批的唯一题。

建议重跑：

- `000:100`
- `100:300`
- `500:2788`

说明：

- `300:500` 当前可先保留。

### 5. multi_physics

- scanned: `1499`
- unique after global source_problem_id dedup: `912`
- duplicates: `587`
- 结论：现有结果可保留的唯一 coverage 大致到 `912`。

建议重跑：

- `912:1412`

说明：

- `500_1412` 目录内已有结果可以视为“实际提供了 0:912 的唯一 coverage”。
- 不建议整段废弃重跑，优先补 `912:1412` 更划算。

### 6. eee_bench

- scanned: `2916`
- unique after global source_problem_id dedup: `1716`
- duplicates: `1200`
- 结论：`eee_bench_0500_1000` 基本没有提供额外新题，当前保留下来的主要是 `000_500` 和 `1000_2860`。

建议重跑：

- `500:1000`

### 7. msearth_open_ended

- scanned: `1476`
- unique after global source_problem_id dedup: `500`
- duplicates: `976`
- 结论：当前最终保留下来的唯一题主要来自：
  - `msearth_open_ended_600_1100`
  - `msearth_open_ended_batched_ler_reasoning_chain`

建议重跑：

- `0:300`
- `300:600`

说明：

- 当前已有结果更像只保住了后半段的一部分 coverage。

### 8. physreason

- scanned: `1174`
- unique after current physreason_full rule dedup: `539`
- duplicates: `635`
- 结论：当前最终保留下来的唯一题主要来自：
  - `physreason_full_300_600`
  - `physreason_full_600_1200`

建议重跑：

- `0:300`

说明：

- `physreason` 目前仍按 `physreason_full_*` 专用规则处理。
- 当前证据更像“前段覆盖缺失”，不是简单的目录名误差。

### 9. seephys

- scanned: `2001`
- unique after selection: `2000`
- duplicates: `1`
- 结论：重复极轻，当前无需优先重跑。

建议重跑：

- 暂无

## 从现有 ready/summary 看出有重复信号，但未按新规则复核的数据集

### cmm_math

- summary duplicate_source_problem_id: `40`
- 建议：后续有时间再单独 dry-run 复核

### geosqa

- summary duplicate_source_problem_id: `885`
- 建议：优先级较高，建议单独 dry-run 复核

### mathvision

- summary duplicate_source_problem_id: `143`
- 建议：后续单独 dry-run 复核

## 当前建议的重跑优先级

### 高优先级

- `ai2d 1000:3000`
- `geoqa_plus 2000:5000`
- `eee_bench 500:1000`
- `emma_physics 000:100`
- `emma_physics 100:300`
- `emma_physics 500:2788`
- `multi_physics 912:1412`

### 中优先级

- `msearth_open_ended 0:300`
- `msearth_open_ended 300:600`
- `physreason 0:300`

### 需要整体重新规划切分

- `mm_math`

说明：

- `mm_math` 不建议继续沿用现有 outputs 目录名来推断 coverage。
- 更稳妥的做法是重新确认目标范围，再按新配置整段重跑。
