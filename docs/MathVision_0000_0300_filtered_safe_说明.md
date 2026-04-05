# MathVision 0000:0300 filtered safe 子集说明

## 最终结论

MathVision `0000:0300` 不适合整包直接进入 ready，但可以基于保守筛选规则提取一个较安全的子集。

本次生成的 filtered ready 包位于：

- `ready/mathvision/run_filtered_mathvision_000_300_safe`

对应导出的统一 problem JSON 位于：

- `ready_problem_exports/run_filtered_mathvision_000_300_safe__mathvision.json`

该 filtered 包当前已经完成本地结构校验与导出校验。

---

## 背景

源数据来自：

- `outputs/mathvision_000_300/run_8d24366e519d1ecf`

原始数据集 summary：

- `requested_samples = 300`
- `processed_samples = 300`
- `pass = 145`
- `review = 153`
- `reject = 2`

rewrite 策略分布：

- `keep_open = 190`
- `blank_open = 42`
- `drop_image_index = 62`
- `split_open = 6`

虽然该 run 已完整结束，但整体 review 占比偏高，不能直接按“整包 ready”处理。

---

## 为什么不直接整包进入 ready

进一步检查后，MathVision 的主要问题不是缺题干、缺答案或缺图片，而是 **visual grounding** 和 **题型改写稳定性** 不够理想。

关键现象：

- `alignment_status.good = 217`
- `alignment_status.risky = 11`
- `alignment_status.bad = 72`

主要 reason codes：

- `alignment_requires_review = 80`
- `missing_grounded_visual_path = 52`
- `rewrite_unusable = 21`
- `pure_image_choice_task = 23`

这意味着较多样本存在以下问题：

1. 图像虽然存在，但题干-答案-图像之间的 grounding 没有稳定落地；
2. 一部分题本质上仍是纯图像选项题，不适合直接改写成当前 ready 需要的开放题；
3. 少量样本保留了 `answer_label_only`、占位图数量不一致、多图占位与单图资产不匹配等结构风险。

因此不建议把 `300` 条原 run 全量作为 ready 包提交。

---

## 筛选原则

本次构建的是一个 **保守 filtered safe 子集**，筛选规则为：

### 基础门槛

只保留同时满足以下条件的样本：

- `clean_decision = pass`
- `alignment_status = good`
- `annotation_ready = true`

### 额外排除条件

进一步排除带有以下明显风险的样本：

- `text_only_without_visual_need`
- `metadata_inconsistency`
- `answer_label_only`
- `answer_is_choice_label_only`
- `placeholder_image_count_mismatch`
- `image_placeholder_count_mismatch`
- `options_embedded_in_image`
- `option_text_missing_but_visual_options_present`
- `options_not_textual_in_metadata`
- `option_text_not_in_metadata`
- `multi_placeholder_single_image`

同时排除 clean decision reason 中包含以下高风险语义的样本：

- `missing_grounded_visual_path`
- `alignment_requires_review`
- `pure_image*`
- `rewrite_unusable`
- `rewrite_variant_invalid`
- `rewrite_not_recoverable`
- `rewrite_not_convertible`
- `rewrite_unavailable`
- `rewrite_missing_usable_variant`

筛选后的样本 ID 列表记录在：

- `plans/mathvision_filtered_candidate_ids.json`

---

## 最终 filtered 子集结果

filtered ready 包位置：

- `ready/mathvision/run_filtered_mathvision_000_300_safe`

最终保留样本数：

- `selected_samples = 116`

summary 统计：

- `requested_samples = 116`
- `processed_samples = 116`
- `pass = 116`
- `review = 0`
- `reject = 0`

rewrite 策略：

- `keep_open = 94`
- `blank_open = 22`

说明这个子集是一个完全由 `pass` 样本组成的保守子集。

---

## 文件完整性校验

对 filtered ready 包做了文件计数校验，结果如下：

- `sample_count = 116`
- `problem_main_records = 116`
- `clean_pool_entries = 116`
- `rewrite_reports = 116`
- `image_count = 116`
- `crop_count = 116`

说明该 filtered 包内部 records / samples / artifacts 数量是对齐的。

---

## 导出结果

导出命令使用包级 ready root：

```bash
python scripts/export_ready_to_problem_json.py \
  --ready-root ready/mathvision \
  --dataset run_filtered_mathvision_000_300_safe
```

导出文件：

- `ready_problem_exports/run_filtered_mathvision_000_300_safe__mathvision.json`

导出结果：

- `problem_count = 116`

导出校验：

- `missing_question_text = 0`
- `missing_standard_answer = 0`
- `missing_images = 0`
- `images_gt_2 = 0`

说明该 filtered 包导出后结构完整，可供后续统一消费。

---

## 代表性判断

本次 filtered safe 方案的核心思路不是“修复全部 MathVision”，而是：

- 承认整包 `300` 条里存在较多 grounding / rewrite 风险；
- 优先提取一批当前结构已比较稳定、可导出、可消费的样本；
- 用一个保守子集先进入 ready，而不是为了覆盖率牺牲质量。

因此，这个包更适合作为：

- **当前可用安全子集**

而不是：

- **MathVision 0000:0300 的完整最终口径**

如果后续需要扩充覆盖面，建议另做人工抽检或更精细的规则放宽，而不是直接把剩余 review 样本并入。
