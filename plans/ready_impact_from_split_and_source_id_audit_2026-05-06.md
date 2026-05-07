# 本轮 split / source_problem_id 审计对现有 ready 的影响

日期：2026-05-06

## 审计范围

本轮重点检查了以下问题：

- `source_problem_id` 是否可以作为跨输出目录去重依据
- 某些数据集是否存在 split 错切分 / 实际重复跑前段题目
- 这些问题是否已经传导到 `D:\Hallucination\workspace\ready`

本轮直接审计过、并且在现有 `ready/` 中有对应数据集的有：

- `eee_bench`
- `emma_physics`
- `mm_math`
- `multi_physics`
- `physreason`
- `seephys`
- `mathvision`

不在当前 `ready/` 下、因此不构成“现有 ready 受影响”的有：

- `ai2d`
- `geoqa_plus`
- `msearth_open_ended`

## 结论

### 明确受影响，不建议直接视为稳定 ready

- `ready/circuit/eee_bench`
  - 原因：`source_problem_id` 不能安全去重；重复 id 抽样显示是真不同题。
- `ready/physics/emma_physics`
  - 原因：`source_problem_id` 不稳定；存在不同题共用同 id。
- `ready/math/mm_math`
  - 原因：本轮更主要的问题不是 id 冲突，而是上游 split / 覆盖区间明显有误，现有 ready 继承了这类覆盖问题。
- `ready/physics/multi_physics`
  - 原因：现有输出存在“后段目录实际重复前段题目”的问题；虽然当前样本里同 id 基本仍对应同题，但 ready 覆盖范围已经受影响。
- `ready/physics/physreason`
  - 原因：`source_problem_id` 本身可用，但现有输出覆盖存在前段缺口，本轮建议补跑 `0:300` 后再统一更新 ready。
- `ready/physics/seephys`
  - 原因：`source_problem_id` 不能安全去重；重复 id 抽样显示是真不同题。

### 本轮未发现会阻止继续使用的同类问题

- `ready/math/mathvision`
  - 原因：重复 `source_problem_id` 在宽松归一化后可视为同题，本轮未发现需要因该问题重跑的区间。

## 暂不纳入本轮影响名单

以下 ready 数据集不在本轮重点问题命中范围内；不能据此说它们“绝对没问题”，只能说“本轮没有新增证据表明它们被这类问题击中”：

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

## 面向 pipeline2 的保守建议

如果只按本轮发现的 split / `source_problem_id` 问题来判断：

- 可以继续进入 `pipeline2`：`mathvision`
- 暂缓，等修复 / 重跑 / 重建 ready 后再进：`eee_bench`、`emma_physics`、`mm_math`、`multi_physics`、`physreason`、`seephys`
- 其余现有 ready：本轮未命中，不在这份问题单的阻塞名单里
