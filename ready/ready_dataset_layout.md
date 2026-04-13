# Ready 数据集结构说明

这份文档说明当前 `output -> ready` 主链写出的 **flat ready dataset layout**。

| 领域 | 通过 | 总数 | 通过率 |
|---|---:|---:|---:|
| 数学 | 4383 | 7545 | 58.09% |
| 物理 | 4596 | 6781 | 67.78% |
| 化学 | 1222 | 1782 | 68.57% |
| 生物 | 283 | 494 | 57.29% |
| 地理 | 1757 | 2000 | 87.85% |
| 电子电路 | 1613 | 2316 | 69.65% |
| 六领域小计 | 13854 | 20918 | 66.23% |

图片路径相对于：
- `ready/<subject>/<dataset>/`

## 1. ready 根目录结构

`ready/` 下分6个领域 'math' 'biology' 'chemistry' 'circuit' 'geography' 'physics',其中每个数据集各自占一个目录：

```text
math/
├── summary.json                        # 本次 ready 构建的总览（跨数据集）
├── mm_math/
│   ├── summary.json                    # 单数据集摘要
│   ├── selection_manifest.json         # 样本选择与放行清单
│   ├── samples/
│   │   ├── mmmath00000.json
│   │   ├── mmmath00001.json
│   │   └── ...
│   └── artifacts/
│       ├── images/
│       │   ├── mmmath00000.png
│       │   ├── mmmath00001.png
│       │   └── ...
│       └── crops/
│           ├── mmmath00000.png
│           ├── mmmath00001.png
│           └── ...
├── scemqa_math/
│   ├── summary.json
│   ├── selection_manifest.json
│   ├── samples/
│   │   ├── scemqamath00000.json
│   │   └── ...
│   └── artifacts/
│       ├── images/
│       └── crops/
└── ...
```

## 2. 单数据集目录里有什么

以 `ready/math/mm_math/` 为例：

- `summary.json`
  - 这个 ready 数据集最终写出了多少样本
  - 经过 release gate 后的最终状态计数
  - 来自哪些 `outputs/...` 和哪些 `run_*`
  - 每个 range 的扫描/去重情况
- `selection_manifest.json`
  - 这批样本为什么被保留、为什么被丢弃
  - 哪些样本是原始 `pass`
  - 哪些样本是 `review` 后被 release gate 放进 ready
- `samples/*.json`
  - 每题一个样本 JSON
  - 文件名已经 canonical 化，例如 `mmmath00000.json`
- `artifacts/images/*`
  - 样本对应原图
- `artifacts/crops/*`
  - 样本对应裁剪图

## 3. sample JSON 的关键路径字段

每个 `samples/*.json` 里会额外写入 canonical 字段，例如：

```json
{
  "canonical_sample_id": "mmmath00000",
  "canonical_sample_index": 0,
  "canonical_dataset_key": "mm_math",
  "sample_path": "samples/mmmath00000.json",
  "image_path": "artifacts/images/mmmath00000.png",
  "crop_path": "artifacts/crops/mmmath00000.png"
}
```

这些路径字段的含义是：

- `sample_path`
- `image_path`
- `crop_path`

**都相对于当前数据集根目录**，也就是相对于：

- `ready/<subject>/<dataset>/`

举例：

- 若数据集根目录是 `ready/math/mm_math/`
- 且样本里写：
  - `image_path = "artifacts/images/mmmath00000.png"`

则该图片的完整路径就是：

- `ready/math/mm_math/artifacts/images/mmmath00000.png`

同理：

- `crop_path = "artifacts/crops/mmmath00000.png"`
- 对应完整路径：
  - `ready/math/mm_math/artifacts/crops/mmmath00000.png`

## 4. selection_manifest.json 主要内容

`selection_manifest.json` 是 **ready 选择过程的台账**。

典型结构大致如下：

```json
{
  "dataset_key": "mm_math",
  "selection_rule": "...",
  "kept_problem_ids": [...],
  "kept_source_problem_ids": [...],
  "kept_samples": [...],
  "dropped_samples": [...],
  "ranges": [...],
  "release_gate": {
    "enabled": true,
    "policy_config": "configs/review_release_policies.yaml",
    "structured_release_buckets": [...],
    "explicit_release_candidate_count": 0,
    "counts": {
      "pass_original": 0,
      "released_review": 0,
      "dropped_review": 0,
      "dropped_reject": 0,
      "dropped_other": 0
    }
  }
}
```

### 4.1 顶层关键字段

- `dataset_key`
  - 当前 ready 数据集名
- `selection_rule`
  - 这一批样本是按什么规则从 outputs 里选出来的
- `kept_problem_ids`
  - 最终进入 ready 的 problem_id 列表
- `kept_source_problem_ids`
  - 最终进入 ready 的 source_problem_id 列表
- `kept_samples`
  - 每个被保留样本的详细选择记录
- `dropped_samples`
  - 每个被丢弃样本的记录和原因
- `ranges`
  - 每个 range 的扫描/去重统计
- `release_gate`
  - review-release 放行策略的信息与计数

### 4.2 kept_samples 里常见字段

`kept_samples` 中每一项通常会包含：

- `problem_id`
- `source_problem_id`
- `range_key`
- `original_sample_filename`
- `source_output_dir`
- `source_run`
- `source_dataset_root`
- `source_sample_path`
- `source_kind`
- `source_decision`
- `source_reason_codes`
- `released_from_review`
- `release_bucket`
- `release_basis`
- `selection_notes`
- `release_mode`
- `candidate_json`
- `final_decision_for_ready`
- `canonical_sample_id`
- `canonical_sample_index`
- `sample_path`
- `image_path`
- `crop_path`
- `image_paths`
- `crop_paths`

其中最常用的是：

- 这题从哪来：
  - `source_output_dir`
  - `source_run`
  - `source_sample_path`
- 原始判定是什么：
  - `source_decision`
  - `source_reason_codes`
- 为什么能进 ready：
  - `released_from_review`
  - `release_bucket`
  - `release_basis`
  - `final_decision_for_ready`
- 最终写到哪里：
  - `canonical_sample_id`
  - `sample_path`
  - `image_path`
  - `crop_path`

### 4.3 dropped_samples 里常见字段

`dropped_samples` 基本沿用保留样本的来源字段，但会额外包含：

- `drop_reason`

例如：

- 原始 decision 是 `review`，但没有命中 release gate
- 原始 decision 是 `reject`
- 或其他不进入 ready 的情况

## 5. summary.json 主要内容

单数据集的 `summary.json` 更偏统计摘要，常见字段：

- `dataset_key`
- `dataset_root`
- `processed_samples`
- `selected_samples`
- `input_selected_samples_before_release_gate`
- `dedup_rule`
- `scanned_files`
- `duplicate_source_problem_id`
- `unique_files`
- `status_counts`
- `original_status_counts_before_release_gate`
- `release_gate`
- `source_runs`
- `source_output_dirs`
- `ranges`
- `selection_validation`
- `write_validation`

可把它理解成：

- `selection_manifest.json` = 逐样本台账
- `summary.json` = 聚合统计摘要

## 6. 图片路径到底相对什么

这是最容易混的点，单独强调：

### 在 sample JSON / selection_manifest 的路径字段里：

- `sample_path`
- `image_path`
- `crop_path`
- `image_paths`
- `crop_paths`

**全部是相对于当前 dataset root**，不是相对于仓库根目录。

也就是说：

- dataset root = `ready/<dataset>/`
- `image_path = "artifacts/images/xxx.png"`
- 实际完整路径 = `ready/<dataset>/artifacts/images/xxx.png`

### 在 review 文档里的图片 markdown
如果文档文件位于：

- `docs/review/<dataset>.md`

那它为了引用 ready 里的图片，通常会写成：

```md
![](../ready/mm_math/artifacts/crops/mmmath00000.png)
```

这里的 `..` 是相对于文档所在目录来算的，不是 sample JSON 的相对规则。

所以要区分：

- sample/manifest 里的路径：**相对 dataset root**
- markdown 文档里的路径：**相对文档文件本身**

## 7. 一句话总结

当前 ready 是 **flat dataset layout**：

- 每个数据集一个目录：`ready/<dataset>/`
- 样本 JSON 在：`samples/*.json`
- 图在：`artifacts/images/*` 和 `artifacts/crops/*`
- `selection_manifest.json` 负责记录“怎么选的”
- `summary.json` 负责记录“最后结果统计”
- 样本里的 `image_path/crop_path` 一律相对 `ready/<dataset>/`
