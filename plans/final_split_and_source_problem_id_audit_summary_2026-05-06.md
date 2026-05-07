# split / source_problem_id 审计最终整理

日期：2026-05-06

## 审计目标

这轮审计的目标是给出一个尽量高置信的结论，用来决定哪些数据集需要重跑、哪些现有 `ready` 会受到影响。

主要检查两类问题：

- `source_problem_id` 能不能作为跨输出目录的判同 / 去重依据
- 某些 split 是否实际重复跑到了前面的题，导致 coverage 错位

本结论综合了以下证据：

- 代码里 `source_problem_id` 的生成逻辑
- 现有 `outputs/` 的全量重复 id 统计
- 重复 id 组的题面内容比对
- 对冲突组的随机复核

相关原始记录：

- [source_problem_id_audit_2026-05-06.json](/d:/Hallucination/workspace/agent-pipeline/plans/source_problem_id_audit_2026-05-06.json)
- [source_problem_id_relaxed_audit_2026-05-06.json](/d:/Hallucination/workspace/agent-pipeline/plans/source_problem_id_relaxed_audit_2026-05-06.json)
- [random_conflict_resample_2026-05-06.json](/d:/Hallucination/workspace/agent-pipeline/plans/random_conflict_resample_2026-05-06.json)
- [ready_impact_from_split_and_source_id_audit_2026-05-06.md](/d:/Hallucination/workspace/agent-pipeline/plans/ready_impact_from_split_and_source_id_audit_2026-05-06.md)

## 一、哪些数据集可以按 source_problem_id 判同

这里的“可以”指的是：

- 对当前这批 `outputs` 来说，可把同一个 `source_problem_id` 视为同一道题
- 这个结论不自动等于“以后长期都安全”

### 可以

- `ai2d`
- `geoqa_plus`
- `multi_physics`
- `physreason`
- `mathvision`
- `mm_math`

说明：

- `geoqa_plus`、`multi_physics`、`mathvision` 里，表面不同的重复题大多是 `<image>`、`Question:`、尾部选项拼接等包装差异。
- `mm_math` 里有少量表面差异，实际主要是 LaTeX 转义写法不同，题面内容未变。
- `mm_math` 仍然只建议作为“这批现有 outputs 可用”，不建议把它上升成永久稳定规则。

### 不可以

- `eee_bench`
- `seephys`
- `emma_physics`
- `msearth_open_ended`

说明：

- 这些数据集里，重复 `source_problem_id` 对应的题面不是“包装不同”，而是真不同题。
- `eee_bench`、`seephys`、`emma_physics` 还做了随机复核，结论仍然成立。

## 二、随机复核后的高置信结论

以下三个数据集，已经可以高置信认定：

- `eee_bench`
- `seephys`
- `emma_physics`

结论：

- 跨输出目录出现的重复 `source_problem_id`，确实会对应不同题
- 因此不能把 `source_problem_id` 当这些数据集的全局唯一键来合并目录

随机复核结果：

- `eee_bench`：从 500 个冲突 id 组里随机抽 10 组，均为明显不同题
- `seephys`：从 300 个冲突 id 组里随机抽 10 组，均为明显不同题
- `emma_physics`：在去除 `<image_1>` 等伪差异后，仍有 56 个冲突 id 组；随机抽 10 组，均为明显不同题

## 三、建议重跑区间

这里只列出本轮已经可以给出较明确建议的数据集。

### 可按 source_problem_id 判同的数据集

- `ai2d`：重跑 `1000:3000`
- `geoqa_plus`：重跑 `2000:5000`
- `multi_physics`：重跑 `912:1412`
- `physreason`：重跑 `0:300`
- `mm_math`：建议重跑 `300:4000`
- `mathvision`：本轮不需要因这个问题重跑

说明：

- `multi_physics` 不是整段 `500:1412` 都坏，而是现有结果只稳定覆盖到前 `912` 个唯一题，缺的是后段。
- `mm_math` 的问题核心是 split / coverage 错位，不是简单的 id 冲突。

### 不能按 source_problem_id 判同的数据集

这类数据集不能直接用“全局按 id 去重”的方式给出完整重跑区间，只能先给出保守结论。

#### eee_bench

- 可单独保留前缀块：`000:500`
- 后续情况：
  - `0500:1000` 基本是重复前段
  - `1000:2860` 是“新题 + 冲突题”混合
  - `2660:2860` 没带来新唯一块

#### seephys

- 可单独保留前缀块：`000:300`
- 后续情况：
  - `300:600` 基本是重复前段
  - `600:2000` 是“新题 + 冲突题”混合

#### emma_physics

- 可单独保留前缀块：`000:100`
- 后续情况：
  - `100:300` 基本是重复前段
  - `300:500` 是“少量新题 + 冲突题”混合
  - `500:2788` 基本没有新增唯一覆盖

## 四、现有 ready 的受影响范围

按本轮发现的问题，现有 `D:\Hallucination\workspace\ready` 中明确受影响的有：

- `ready/circuit/eee_bench`
- `ready/physics/emma_physics`
- `ready/math/mm_math`
- `ready/physics/multi_physics`
- `ready/physics/physreason`
- `ready/physics/seephys`

原因概括：

- `eee_bench`、`emma_physics`、`seephys`：重复 `source_problem_id` 真冲突
- `mm_math`、`multi_physics`、`physreason`：主要是 split / coverage 错位，现有 ready 继承了这个问题

本轮未发现同类阻塞问题的现有 ready 有：

- `ready/math/mathvision`

以下现有 ready 不在这轮问题命中范围内，因此不列入“本轮受影响名单”：

- `ready/biology/scemqa_biology`
- `ready/biology/sciverse_biology`
- `ready/chemistry/emma_chemistry`
- `ready/chemistry/scemqa_chemistry`
- `ready/chemistry/sciverse_chemistry`
- `ready/geography/geosqa`
- `ready/math/cmm_math`
- `ready/math/geometry3k`
- `ready/math/scemqa_math`
- `ready/physics/phyx`
- `ready/physics/sciverse_physics`

## 五、面向 pipeline2 的保守建议

如果只根据这轮 split / `source_problem_id` 审计来判断：

### 可以继续进入 pipeline2

- `mathvision`

### 建议暂缓，等修复 / 重跑 / 重建 ready 后再进入 pipeline2

- `eee_bench`
- `emma_physics`
- `mm_math`
- `multi_physics`
- `physreason`
- `seephys`

### 其余现有 ready

- 本轮没有新增证据表明它们被这类问题击中
- 但这不等于完成了全部质量审计

## 六、最终一句话版

- 能按 `source_problem_id` 判同：`ai2d`、`geoqa_plus`、`multi_physics`、`physreason`、`mathvision`、`mm_math`
- 不能按 `source_problem_id` 判同：`eee_bench`、`seephys`、`emma_physics`、`msearth_open_ended`
- 需要优先处理并影响现有 `ready` 的：`eee_bench`、`emma_physics`、`mm_math`、`multi_physics`、`physreason`、`seephys`
