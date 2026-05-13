# Review 原因归并分布（基于 docs/review 候选统计，2026-05-13）

说明：本统计聚合 `docs/review/*candidates*.json` 中已导出的 `reason_code_counts`、`quality_risk_flag_counts`、`excluded_counts`、`fail_counts_top`、`reason_combo_counts`、`risk_combo_counts`。同一样本可能有多个 reason/risk，因此这里统计的是**原因出现次数**，不是唯一问题样本数。

## 总体归并分布

总原因出现次数：`12324`

| 原因大类 | 出现次数 | 占比 |
| --- | ---: | ---: |
| 答案/标注冲突类 | 2452 | 19.9% |
| 视觉质量/证据类 | 2432 | 19.7% |
| alignment/grounding 类 | 1937 | 15.7% |
| 其他/零散风险类 | 1926 | 15.6% |
| rewrite 完整性/可理解性类 | 1140 | 9.3% |
| metadata/path 类 | 1134 | 9.2% |
| split/多子题类 | 1101 | 8.9% |
| 选项/选择题结构类 | 115 | 0.9% |
| 核心语义风险类 | 87 | 0.7% |

## 分文件统计

### `docs/review/geoqa_plus_rewrite_release_candidates_2026-05-10.json`

原因出现次数：`2903`

| 原因大类 | 出现次数 | 占比 |
| --- | ---: | ---: |
| 答案/标注冲突类 | 2040 | 70.3% |
| 视觉质量/证据类 | 354 | 12.2% |
| alignment/grounding 类 | 211 | 7.3% |
| rewrite 完整性/可理解性类 | 135 | 4.7% |
| 核心语义风险类 | 83 | 2.9% |
| metadata/path 类 | 40 | 1.4% |
| 选项/选择题结构类 | 24 | 0.8% |
| 其他/零散风险类 | 11 | 0.4% |
| split/多子题类 | 5 | 0.2% |

### `docs/review/mm_math_strict_rewrite_release_candidates_2026-05-10.json`

原因出现次数：`6644`

| 原因大类 | 出现次数 | 占比 |
| --- | ---: | ---: |
| 视觉质量/证据类 | 2011 | 30.3% |
| 其他/零散风险类 | 1731 | 26.1% |
| alignment/grounding 类 | 1548 | 23.3% |
| metadata/path 类 | 1055 | 15.9% |
| rewrite 完整性/可理解性类 | 277 | 4.2% |
| 选项/选择题结构类 | 11 | 0.2% |
| 答案/标注冲突类 | 7 | 0.1% |
| 核心语义风险类 | 4 | 0.1% |

### `docs/review/multi_physics_visual_grounding_rewrite_candidates_2026-05-10.json`

原因出现次数：`2777`

| 原因大类 | 出现次数 | 占比 |
| --- | ---: | ---: |
| split/多子题类 | 1096 | 39.5% |
| rewrite 完整性/可理解性类 | 728 | 26.2% |
| 答案/标注冲突类 | 405 | 14.6% |
| 其他/零散风险类 | 184 | 6.6% |
| alignment/grounding 类 | 178 | 6.4% |
| 选项/选择题结构类 | 80 | 2.9% |
| 视觉质量/证据类 | 67 | 2.4% |
| metadata/path 类 | 39 | 1.4% |

