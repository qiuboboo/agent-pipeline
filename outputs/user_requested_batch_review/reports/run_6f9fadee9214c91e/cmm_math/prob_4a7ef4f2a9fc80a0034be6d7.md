# CMM-Math / prob_4a7ef4f2a9fc80a0034be6d7

- source_problem_id: `19899`
- source_split: `train`
- clean_decision: `review`
- rewrite_strategy: `split_open`
- full sample bundle JSON: `outputs/user_requested_batch_review/pipeline_runs/run_6f9fadee9214c91e/datasets/cmm_math/samples/prob_4a7ef4f2a9fc80a0034be6d7.json`

## 1. 原始内容（处理前）

### 1.1 原始快照

```json
{
  "dataset_key": "cmm_math",
  "source_problem_id": "19899",
  "source_split": "train",
  "raw_question_text": "已知 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-y \\geq 0, \\\\ x+y \\leq 2, \\\\ y \\geq 0,\\end{array}\\right.$围为 ( )",
  "raw_answer_text": "C",
  "choice_map": {
    "A": "$(-1,1)$",
    "B": "$[-1,1)$",
    "C": "$[-1,1]$",
    "D": "$(-1,1]$"
  },
  "image_sources": [],
  "metadata": {
    "row_index": 8,
    "question_field": "question",
    "answer_field": "answer",
    "image_field": "image",
    "choice_field": "options"
  },
  "raw_record": {
    "id": "19899",
    "image": "[\"9284.jpg\"]",
    "answer": "C",
    "solution": "null",
    "level": "高二",
    "question": "已知 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-y \\geq 0, \\\\ x+y \\leq 2, \\\\ y \\geq 0,\\end{array}\\right.$围为 ( )",
    "options": "A. $(-1,1)$\nB. $[-1,1)$\nC. $[-1,1]$\nD. $(-1,1]$",
    "subject": "解析几何",
    "analysis": "不等式组表示的平面区域如图所示:\n\n<ImageHere>\n\n$\\because z=a x+y$ 的最大值为 $a+1, \\therefore$ 最值是在 $(1,1)$ 处取得, $\\because y=-a x+z$,\n\n当 $-a \\geq 0$ 时, $-a \\leq 1$, 即 $-1 \\leq a \\leq 0$;\n\n当 $-a<0$ 时, 需满足 $-a \\geq-1$, 即 $0<a \\leq 1$, 故 $-1 \\leq a \\leq 1$.\n\n考点: 由线性目标函数的最值求参数范围."
  }
}
```

## 2. 处理前后对照

### 2.1 关键字段对照

| 字段 | 处理前 | 处理后 |
| --- | --- | --- |
| question_text | 已知 $x, y$ 满足约束条件 $\left\{\begin{array}{l}x-y \geq 0, \\ x+y \leq 2, \\ y \geq 0,\end{array}\right.$围为 ( ) | 已知 $x, y$ 满足约束条件 $\left\{\begin{array}{l}x-y \geq 0, \\ x+y \leq 2, \\ y \geq 0,\end{array}\right.$围为 ( ) |
| answer_text | C | C |
| answer_type | - | option |
| image_count | 0 | 0 |
| text_dominant | - | True |
| cleaning_path | - | text_lightweight |
| clean_decision | - | review |
| alignment_status | - | good |
| solvability_decision_hint | - | pass |

### 2.2 结构化处理后结果

#### problem_main_record

```json
{
  "problem_id": "prob_4a7ef4f2a9fc80a0034be6d7",
  "source_dataset": "CMM-Math",
  "source_split": "train",
  "source_problem_id": "19899",
  "ingest_batch_id": "multidataset-clean_20260324T063656Z",
  "problem_type": "multimodal_reasoning",
  "domain_tags": [
    "数学"
  ],
  "language": "zh",
  "raw_question_text": "已知 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-y \\geq 0, \\\\ x+y \\leq 2, \\\\ y \\geq 0,\\end{array}\\right.$围为 ( )",
  "normalized_question_text": "已知 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-y \\geq 0, \\\\ x+y \\leq 2, \\\\ y \\geq 0,\\end{array}\\right.$围为 ( )",
  "raw_answer_text": "C",
  "normalized_answer_text": "C",
  "answer_type": "option",
  "image_count": 0,
  "has_multiple_images": false,
  "requires_image": false,
  "multimodal_strength_score": 0.33,
  "multi_step_score": 0.3377,
  "verifiability_score": 1.0,
  "quality_risk_flags": [],
  "current_status": "cleaning_review",
  "clean_decision": "review",
  "clean_decision_reason_codes": [
    "split_variant_needs_review"
  ],
  "review_priority": "normal",
  "annotation_ready": false,
  "qa_precheck_ready": true,
  "release_reserved": {},
  "rewrite_strategy": "split_open",
  "open_variant_count": 1,
  "candidate_id": "cand_4a7ef4f2a9fc80a0034be6d7",
  "text_dominant": true,
  "cleaning_path": "text_lightweight",
  "alignment_status": "good",
  "solvability_score": 1.0,
  "solvability_decision_hint": "pass",
  "created_at": "2026-03-24T06:37:02Z",
  "updated_at": "2026-03-24T06:37:02Z",
  "initial_image_dependency_score": 0.28,
  "initial_multi_solution_score": 0.46,
  "initial_verifiability_score": 0.78,
  "multi_solution_mining_policy": "aggressive"
}
```

#### clean_problem_record

```json
{
  "clean_problem_record_id": "cleanprob_209c59cdbe556c9d3d815cec",
  "problem_id": "prob_4a7ef4f2a9fc80a0034be6d7",
  "source_dataset": "CMM-Math",
  "source_problem_id": "19899",
  "normalized_question_text": "已知 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-y \\geq 0, \\\\ x+y \\leq 2, \\\\ y \\geq 0,\\end{array}\\right.$围为 ( )",
  "normalized_answer_text": "C",
  "image_count": 0,
  "has_multiple_images": false,
  "requires_image": false,
  "text_dominant": true,
  "cleaning_path": "text_lightweight",
  "question_type": "multiple_choice",
  "open_variant_count": 1,
  "alignment_status": "good",
  "solvability_score": 1.0,
  "solvability_path_mode": "text_only",
  "clean_decision": "review",
  "decision_reason_codes": [
    "split_variant_needs_review"
  ],
  "created_at": "2026-03-24T06:37:02Z"
}
```

#### normalized_assets

```json
{
  "normalized_assets_id": "nassets_209c59cdbe556c9d3d815cec",
  "problem_id": "prob_4a7ef4f2a9fc80a0034be6d7",
  "normalized_question_text": "已知 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-y \\geq 0, \\\\ x+y \\leq 2, \\\\ y \\geq 0,\\end{array}\\right.$围为 ( )",
  "normalized_answer_text": "C",
  "question_unit_normalization_map": [],
  "answer_unit_normalization_map": [],
  "variable_aliases": [
    {
      "original": "x",
      "canonical": "x",
      "variable_type": "symbol"
    },
    {
      "original": "y",
      "canonical": "y",
      "variable_type": "symbol"
    },
    {
      "original": "left",
      "canonical": "left",
      "variable_type": "label"
    },
    {
      "original": "l",
      "canonical": "l",
      "variable_type": "symbol"
    },
    {
      "original": "geq",
      "canonical": "geq",
      "variable_type": "label"
    },
    {
      "original": "leq",
      "canonical": "leq",
      "variable_type": "label"
    },
    {
      "original": "end",
      "canonical": "end",
      "variable_type": "label"
    }
  ],
  "sentence_segments": [
    {
      "segment_index": 1,
      "text": "已知 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-y \\geq 0, \\\\ x+y \\leq 2, \\\\ y \\geq 0,\\end{array}\\right.$围为 ( )"
    }
  ],
  "image_regions": [],
  "text_dominant": true,
  "cleaning_path": "text_lightweight",
  "created_at": "2026-03-24T06:37:02Z"
}
```

#### text_structure_record

```json
{
  "text_structure_id": "text_prob_4a7ef4f2a9fc80a0034be6d7",
  "problem_id": "prob_4a7ef4f2a9fc80a0034be6d7",
  "question_type": "multiple_choice",
  "conditions": [
    {
      "text": "已知 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-y \\geq 0, \\\\ x+y \\leq 2, \\\\ y \\geq 0,\\end{array}\\right.$围为 ( )",
      "segment_index": 1,
      "mentions_visual": false,
      "numeric_tokens": [
        "0",
        "2",
        "0"
      ],
      "unit_mentions": [
        "g",
        "h"
      ],
      "condition_role": "explicit"
    }
  ],
  "targets": [
    {
      "text": "已知 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-y \\geq 0, \\\\ x+y \\leq 2, \\\\ y \\geq 0,\\end{array}\\right.$围为 ( )",
      "segment_index": 1,
      "mentions_visual": false,
      "numeric_tokens": [
        "0",
        "2",
        "0"
      ],
      "unit_mentions": [
        "g",
        "h"
      ],
      "target_role": "fallback"
    }
  ],
  "answer_slots": [
    {
      "slot_id": "slot_prob_4a7ef4f2a9fc80a0034be6d7_1",
      "variant_index": 1,
      "split_role": "part_1",
      "slot_type": "short_text",
      "target_text": "请只回答第 1 个目标量。",
      "expected_answer_type": "short_text",
      "expected_answer": "$[-1,1]$",
      "requires_visual_grounding": false
    }
  ],
  "entity_mentions": [],
  "variable_aliases": [
    {
      "original": "x",
      "canonical": "x",
      "variable_type": "symbol"
    },
    {
      "original": "y",
      "canonical": "y",
      "variable_type": "symbol"
    },
    {
      "original": "left",
      "canonical": "left",
      "variable_type": "label"
    },
    {
      "original": "l",
      "canonical": "l",
      "variable_type": "symbol"
    },
    {
      "original": "geq",
      "canonical": "geq",
      "variable_type": "label"
    },
    {
      "original": "leq",
      "canonical": "leq",
      "variable_type": "label"
    },
    {
      "original": "end",
      "canonical": "end",
      "variable_type": "label"
    }
  ],
  "unit_mentions": [
    "g",
    "h"
  ],
  "sentence_segments": [
    {
      "segment_index": 1,
      "text": "已知 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-y \\geq 0, \\\\ x+y \\leq 2, \\\\ y \\geq 0,\\end{array}\\right.$围为 ( )"
    }
  ],
  "requires_visual_grounding": false,
  "text_structure_status": "complete",
  "parser_confidence": 0.92,
  "created_at": "2026-03-24T06:37:02Z"
}
```

#### visual_structure_records

```json
[]
```

#### alignment_record

```json
{
  "alignment_id": "align_209c59cdbe556c9d3d815cec",
  "problem_id": "prob_4a7ef4f2a9fc80a0034be6d7",
  "image_entity_refs": [],
  "text_span_refs": [
    "asset_prob_4a7ef4f2a9fc80a0034be6d7_question_text_normalized"
  ],
  "alignment_pairs": [],
  "conflict_pairs": [],
  "coverage_score": 1.0,
  "consistency_score": 1.0,
  "alignment_status": "good",
  "created_at": "2026-03-24T06:37:02Z",
  "cleaning_path": "text_lightweight",
  "text_dominant": true
}
```

#### solvability_report

```json
{
  "solvability_id": "solv_prob_4a7ef4f2a9fc80a0034be6d7",
  "problem_id": "prob_4a7ef4f2a9fc80a0034be6d7",
  "answer_verifiable": true,
  "target_clear": true,
  "rewrite_complete": true,
  "text_sufficient": true,
  "visual_grounding_available": true,
  "reasoning_path_exists": true,
  "path_mode": "text_only",
  "failure_codes": [],
  "score_breakdown": {
    "answer_verifiable": 1.0,
    "target_clear": 1.0,
    "rewrite_complete": 1.0,
    "text_sufficient": 1.0,
    "visual_grounding": 1.0
  },
  "solvability_score": 1.0,
  "decision_hint": "pass",
  "created_at": "2026-03-24T06:37:02Z"
}
```

#### cleaning_record

```json
{
  "cleaning_id": "clean_209c59cdbe556c9d3d815cec",
  "problem_id": "prob_4a7ef4f2a9fc80a0034be6d7",
  "cleaning_version": "v3.0.0",
  "pipeline_run_id": "run_6f9fadee9214c91e",
  "dataset_name": "CMM-Math",
  "input_asset_ids": [
    "asset_aa79cc9078a9b7b73874a8ec",
    "asset_fe7071f92a673f804c479da9",
    "asset_b8a1c3e7c3305f1f5d4988bc",
    "asset_cf2db0021dcec1089a11ca32",
    "asset_46c5401a16ec8870f2cc8567"
  ],
  "normalization_actions": [
    {
      "action_type": "text_normalized",
      "trigger": "NormalizationAgent",
      "confidence": 1.0,
      "human_confirmed": false
    },
    {
      "action_type": "answer_canonicalized",
      "trigger": "NormalizationAgent",
      "confidence": 0.98,
      "human_confirmed": false
    },
    {
      "action_type": "unit_normalized",
      "trigger": "NormalizationAgent",
      "confidence": 0.92,
      "human_confirmed": false,
      "question_unit_count": 0,
      "answer_unit_count": 0
    },
    {
      "action_type": "variable_canonicalized",
      "trigger": "NormalizationAgent",
      "confidence": 0.88,
      "human_confirmed": false,
      "variable_alias_count": 7
    },
    {
      "action_type": "question_rewritten",
      "trigger": "QuestionRewriteAgent",
      "confidence": 0.85,
      "human_confirmed": false
    }
  ],
  "quality_checks": [
    {
      "check": "image_quality",
      "result": null,
      "passed": true
    }
  ],
  "alignment_summary": {
    "alignment_id": "align_209c59cdbe556c9d3d815cec",
    "coverage_score": 1.0,
    "consistency_score": 1.0,
    "alignment_status": "good",
    "conflict_count": 0
  },
  "text_structure_summary": {
    "text_structure_id": "text_prob_4a7ef4f2a9fc80a0034be6d7",
    "question_type": "multiple_choice",
    "condition_count": 1,
    "target_count": 1,
    "answer_slot_count": 1,
    "status": "complete"
  },
  "solvability_summary": {
    "solvability_id": "solv_prob_4a7ef4f2a9fc80a0034be6d7",
    "solvability_score": 1.0,
    "reasoning_path_exists": true,
    "decision_hint": "pass",
    "failure_codes": []
  },
  "rewrite_summary": {
    "strategy": "split_open",
    "variant_count": 1,
    "discard_reason_codes": []
  },
  "missing_field_summary": {
    "missing_question_text": false,
    "missing_answer_text": false,
    "missing_image_count": 0
  },
  "risk_flags": [],
  "clean_score": 0.8458,
  "decision": "review",
  "decision_reason_codes": [
    "split_variant_needs_review"
  ],
  "review_ticket_id": "review_prob_4a7ef4f2a9fc80a0034be6d7",
  "operator_type": "system",
  "started_at": "2026-03-24T06:37:02Z",
  "finished_at": "2026-03-24T06:37:02Z",
  "candidate_id": "cand_4a7ef4f2a9fc80a0034be6d7",
  "cleaning_path": "text_lightweight",
  "text_dominant": true
}
```

## 3. 开放化改写前后

### 3.1 改写前

```json
{
  "question_text_before_rewrite": "已知 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-y \\geq 0, \\\\ x+y \\leq 2, \\\\ y \\geq 0,\\end{array}\\right.$围为 ( )",
  "answer_text_before_rewrite": "C",
  "raw_question_text": "已知 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-y \\geq 0, \\\\ x+y \\leq 2, \\\\ y \\geq 0,\\end{array}\\right.$围为 ( )",
  "raw_answer_text": "C"
}
```

### 3.2 改写后

```json
{
  "rewrite_report": {
    "rewrite_id": "rewrite_209c59cdbe556c9d3d815cec",
    "problem_id": "prob_4a7ef4f2a9fc80a0034be6d7",
    "source_problem_id": "19899",
    "strategy": "split_open",
    "rationale": "Compound choice answer was split into multiple open-ended targets.",
    "discard_reason_codes": [],
    "variant_count": 1,
    "variants": [
      {
        "open_variant_id": "open_1ce8c0eceb79589c1187bcd2",
        "parent_problem_id": "prob_4a7ef4f2a9fc80a0034be6d7",
        "variant_index": 1,
        "title": "CMM-Math 子题 1",
        "rewritten_question_text": "已知 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-y \\geq 0, \\\\ x+y \\leq 2, \\\\ y \\geq 0,\\end{array}\\right.$围为 ( )\n请只回答第 1 个目标量。",
        "expected_answer_type": "short_text",
        "expected_answer": "$[-1,1]$",
        "split_role": "part_1"
      }
    ],
    "created_at": "2026-03-24T06:37:02Z"
  },
  "open_ended_problem_variants": [
    {
      "open_variant_id": "open_1ce8c0eceb79589c1187bcd2",
      "parent_problem_id": "prob_4a7ef4f2a9fc80a0034be6d7",
      "variant_index": 1,
      "title": "CMM-Math 子题 1",
      "rewritten_question_text": "已知 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-y \\geq 0, \\\\ x+y \\leq 2, \\\\ y \\geq 0,\\end{array}\\right.$围为 ( )\n请只回答第 1 个目标量。",
      "expected_answer_type": "short_text",
      "expected_answer": "$[-1,1]$",
      "split_role": "part_1"
    }
  ]
}
```

## 4. 完整 collection + cleaning 输出对象

#### candidate_problem_record

```json
{
  "candidate_id": "cand_4a7ef4f2a9fc80a0034be6d7",
  "source_dataset": "CMM-Math",
  "source_split": "train",
  "source_problem_id": "19899",
  "subject": "数学",
  "raw_question_text": "已知 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-y \\geq 0, \\\\ x+y \\leq 2, \\\\ y \\geq 0,\\end{array}\\right.$围为 ( )",
  "raw_answer_text": "C",
  "has_image": false,
  "image_count": 0,
  "requires_image": false,
  "text_dominant": true,
  "recommended_cleaning_path": "text_lightweight",
  "initial_image_dependency_score": 0.28,
  "initial_multi_solution_score": 0.46,
  "initial_verifiability_score": 0.78,
  "multi_solution_mining_policy": "aggressive",
  "should_push_multi_solution_agent": true,
  "multi_solution_policy_rationale": "该数据集被视为具备较稳定的多解潜力，可进入更强的多解挖掘链路。",
  "metadata": {
    "row_index": 8,
    "question_field": "question",
    "answer_field": "answer",
    "image_field": "image",
    "choice_field": "options"
  },
  "created_at": "2026-03-24T06:37:02Z"
}
```

#### raw_asset_bundle

```json
{
  "raw_asset_bundle_id": "bundle_ce490b8f13509af2c84e3333",
  "candidate_id": "cand_4a7ef4f2a9fc80a0034be6d7",
  "source_dataset": "CMM-Math",
  "source_problem_id": "19899",
  "assets": [
    {
      "asset_role": "question_text_raw",
      "storage_uri": "inline://prob_4a7ef4f2a9fc80a0034be6d7/question_source",
      "is_present": true
    },
    {
      "asset_role": "answer_text_raw",
      "storage_uri": "inline://prob_4a7ef4f2a9fc80a0034be6d7/answer_source",
      "is_present": true
    }
  ],
  "core_asset_completeness": {
    "has_question_text": true,
    "has_answer_text": true,
    "image_count": 0,
    "has_multiple_images": false
  },
  "initial_scores": {
    "initial_image_dependency_score": 0.28,
    "initial_multi_solution_score": 0.46,
    "initial_verifiability_score": 0.78
  },
  "created_at": "2026-03-24T06:37:02Z"
}
```

#### candidate_pool_entry

```json
{
  "candidate_pool_entry_id": "cpool_8ffb94fa8a00934e89d69539",
  "candidate_id": "cand_4a7ef4f2a9fc80a0034be6d7",
  "source_dataset": "CMM-Math",
  "source_problem_id": "19899",
  "candidate_status": "ready_for_cleaning",
  "priority_score": 0.484,
  "priority_tier": "normal",
  "recommended_cleaning_path": "text_lightweight",
  "multi_solution_mining_policy": "aggressive",
  "initial_scores": {
    "initial_image_dependency_score": 0.28,
    "initial_multi_solution_score": 0.46,
    "initial_verifiability_score": 0.78
  },
  "created_at": "2026-03-24T06:37:02Z"
}
```

#### clean_pool_entries

```json
[
  {
    "clean_pool_entry_id": "cleanpool_209c59cdbe556c9d3d815cec",
    "candidate_id": "cand_4a7ef4f2a9fc80a0034be6d7",
    "problem_id": "prob_4a7ef4f2a9fc80a0034be6d7",
    "dataset_name": "CMM-Math",
    "pool_status": "manual_review",
    "clean_decision": "review",
    "review_required": true,
    "rewrite_strategy": "split_open",
    "open_variant_count": 1,
    "text_dominant": true,
    "cleaning_path": "text_lightweight",
    "created_at": "2026-03-24T06:37:02Z"
  }
]
```

#### rewrite_reports

```json
[
  {
    "rewrite_id": "rewrite_209c59cdbe556c9d3d815cec",
    "problem_id": "prob_4a7ef4f2a9fc80a0034be6d7",
    "source_problem_id": "19899",
    "strategy": "split_open",
    "rationale": "Compound choice answer was split into multiple open-ended targets.",
    "discard_reason_codes": [],
    "variant_count": 1,
    "variants": [
      {
        "open_variant_id": "open_1ce8c0eceb79589c1187bcd2",
        "parent_problem_id": "prob_4a7ef4f2a9fc80a0034be6d7",
        "variant_index": 1,
        "title": "CMM-Math 子题 1",
        "rewritten_question_text": "已知 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-y \\geq 0, \\\\ x+y \\leq 2, \\\\ y \\geq 0,\\end{array}\\right.$围为 ( )\n请只回答第 1 个目标量。",
        "expected_answer_type": "short_text",
        "expected_answer": "$[-1,1]$",
        "split_role": "part_1"
      }
    ],
    "created_at": "2026-03-24T06:37:02Z"
  }
]
```

#### open_ended_problem_variants

```json
[
  {
    "open_variant_id": "open_1ce8c0eceb79589c1187bcd2",
    "parent_problem_id": "prob_4a7ef4f2a9fc80a0034be6d7",
    "variant_index": 1,
    "title": "CMM-Math 子题 1",
    "rewritten_question_text": "已知 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-y \\geq 0, \\\\ x+y \\leq 2, \\\\ y \\geq 0,\\end{array}\\right.$围为 ( )\n请只回答第 1 个目标量。",
    "expected_answer_type": "short_text",
    "expected_answer": "$[-1,1]$",
    "split_role": "part_1"
  }
]
```

#### asset_records

```json
[
  {
    "asset_id": "asset_aa79cc9078a9b7b73874a8ec",
    "problem_id": "prob_4a7ef4f2a9fc80a0034be6d7",
    "asset_type": "text",
    "asset_role": "question_text_source",
    "source_uri": "source://cmm_math/train/19899/question",
    "storage_uri": "inline://prob_4a7ef4f2a9fc80a0034be6d7/question_source",
    "file_format": "txt",
    "file_size_bytes": 125,
    "width": null,
    "height": null,
    "sha256": "79ef2c35f09f2d81a66fec4b351cb1bcc30014efff8965a19a57454aa1432b3d",
    "perceptual_hash": null,
    "source_text_snapshot": "已知 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-y \\geq 0, \\\\ x+y \\leq 2, \\\\ y \\geq 0,\\end{array}\\right.$围为 ( )",
    "normalized_text_snapshot": null,
    "text_completeness_score": 0.6438,
    "blur_score": null,
    "readability_score": null,
    "noise_score": null,
    "cropped_from_asset_id": null,
    "roi_bbox": null,
    "unit_normalization_map": [],
    "variable_aliases": [
      {
        "original": "x",
        "canonical": "x",
        "variable_type": "symbol"
      },
      {
        "original": "y",
        "canonical": "y",
        "variable_type": "symbol"
      },
      {
        "original": "left",
        "canonical": "left",
        "variable_type": "label"
      },
      {
        "original": "l",
        "canonical": "l",
        "variable_type": "symbol"
      },
      {
        "original": "geq",
        "canonical": "geq",
        "variable_type": "label"
      },
      {
        "original": "leq",
        "canonical": "leq",
        "variable_type": "label"
      },
      {
        "original": "end",
        "canonical": "end",
        "variable_type": "label"
      }
    ],
    "asset_quality_flags": [],
    "is_usable": true,
    "discard_reason_codes": [],
    "created_at": "2026-03-24T06:37:02Z",
    "updated_at": "2026-03-24T06:37:02Z"
  },
  {
    "asset_id": "asset_fe7071f92a673f804c479da9",
    "problem_id": "prob_4a7ef4f2a9fc80a0034be6d7",
    "asset_type": "text",
    "asset_role": "question_text_normalized",
    "source_uri": null,
    "storage_uri": "inline://prob_4a7ef4f2a9fc80a0034be6d7/question_normalized",
    "file_format": "txt",
    "file_size_bytes": 125,
    "width": null,
    "height": null,
    "sha256": "79ef2c35f09f2d81a66fec4b351cb1bcc30014efff8965a19a57454aa1432b3d",
    "perceptual_hash": null,
    "source_text_snapshot": "已知 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-y \\geq 0, \\\\ x+y \\leq 2, \\\\ y \\geq 0,\\end{array}\\right.$围为 ( )",
    "normalized_text_snapshot": "已知 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-y \\geq 0, \\\\ x+y \\leq 2, \\\\ y \\geq 0,\\end{array}\\right.$围为 ( )",
    "text_completeness_score": 0.6438,
    "blur_score": null,
    "readability_score": null,
    "noise_score": null,
    "cropped_from_asset_id": null,
    "roi_bbox": null,
    "unit_normalization_map": [],
    "variable_aliases": [
      {
        "original": "x",
        "canonical": "x",
        "variable_type": "symbol"
      },
      {
        "original": "y",
        "canonical": "y",
        "variable_type": "symbol"
      },
      {
        "original": "left",
        "canonical": "left",
        "variable_type": "label"
      },
      {
        "original": "l",
        "canonical": "l",
        "variable_type": "symbol"
      },
      {
        "original": "geq",
        "canonical": "geq",
        "variable_type": "label"
      },
      {
        "original": "leq",
        "canonical": "leq",
        "variable_type": "label"
      },
      {
        "original": "end",
        "canonical": "end",
        "variable_type": "label"
      }
    ],
    "asset_quality_flags": [],
    "is_usable": true,
    "discard_reason_codes": [],
    "created_at": "2026-03-24T06:37:02Z",
    "updated_at": "2026-03-24T06:37:02Z"
  },
  {
    "asset_id": "asset_b8a1c3e7c3305f1f5d4988bc",
    "problem_id": "prob_4a7ef4f2a9fc80a0034be6d7",
    "asset_type": "answer",
    "asset_role": "answer_raw",
    "source_uri": "source://cmm_math/train/19899/answer",
    "storage_uri": "inline://prob_4a7ef4f2a9fc80a0034be6d7/answer_raw",
    "file_format": "txt",
    "file_size_bytes": 1,
    "width": null,
    "height": null,
    "sha256": "6b23c0d5f35d1b11f9b683f0b0a617355deb11277d91ae091d399c655b87940d",
    "perceptual_hash": null,
    "source_text_snapshot": "C",
    "normalized_text_snapshot": null,
    "text_completeness_score": 1.0,
    "blur_score": null,
    "readability_score": null,
    "noise_score": null,
    "cropped_from_asset_id": null,
    "roi_bbox": null,
    "unit_normalization_map": [],
    "variable_aliases": [
      {
        "original": "C",
        "canonical": "C",
        "variable_type": "symbol"
      }
    ],
    "asset_quality_flags": [],
    "is_usable": true,
    "discard_reason_codes": [],
    "created_at": "2026-03-24T06:37:02Z",
    "updated_at": "2026-03-24T06:37:02Z"
  },
  {
    "asset_id": "asset_cf2db0021dcec1089a11ca32",
    "problem_id": "prob_4a7ef4f2a9fc80a0034be6d7",
    "asset_type": "answer",
    "asset_role": "answer_normalized",
    "source_uri": null,
    "storage_uri": "inline://prob_4a7ef4f2a9fc80a0034be6d7/answer_normalized",
    "file_format": "txt",
    "file_size_bytes": 1,
    "width": null,
    "height": null,
    "sha256": "6b23c0d5f35d1b11f9b683f0b0a617355deb11277d91ae091d399c655b87940d",
    "perceptual_hash": null,
    "source_text_snapshot": "C",
    "normalized_text_snapshot": "C",
    "text_completeness_score": 1.0,
    "blur_score": null,
    "readability_score": null,
    "noise_score": null,
    "cropped_from_asset_id": null,
    "roi_bbox": null,
    "unit_normalization_map": [],
    "variable_aliases": [
      {
        "original": "C",
        "canonical": "C",
        "variable_type": "symbol"
      }
    ],
    "asset_quality_flags": [],
    "is_usable": true,
    "discard_reason_codes": [],
    "created_at": "2026-03-24T06:37:02Z",
    "updated_at": "2026-03-24T06:37:02Z"
  },
  {
    "asset_id": "asset_46c5401a16ec8870f2cc8567",
    "problem_id": "prob_4a7ef4f2a9fc80a0034be6d7",
    "asset_type": "text",
    "asset_role": "question_text_open_variant",
    "source_uri": null,
    "storage_uri": "inline://open_1ce8c0eceb79589c1187bcd2",
    "file_format": "txt",
    "file_size_bytes": 159,
    "width": null,
    "height": null,
    "sha256": "476d6af02800a3ebc6ef94d5f2191aa7595e1c805abde8dc76d4cb7f0dd68335",
    "perceptual_hash": null,
    "source_text_snapshot": "已知 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-y \\geq 0, \\\\ x+y \\leq 2, \\\\ y \\geq 0,\\end{array}\\right.$围为 ( )",
    "normalized_text_snapshot": "已知 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-y \\geq 0, \\\\ x+y \\leq 2, \\\\ y \\geq 0,\\end{array}\\right.$围为 ( )\n请只回答第 1 个目标量。",
    "text_completeness_score": 0.6438,
    "blur_score": null,
    "readability_score": null,
    "noise_score": null,
    "cropped_from_asset_id": null,
    "roi_bbox": null,
    "unit_normalization_map": [],
    "variable_aliases": [
      {
        "original": "x",
        "canonical": "x",
        "variable_type": "symbol"
      },
      {
        "original": "y",
        "canonical": "y",
        "variable_type": "symbol"
      },
      {
        "original": "left",
        "canonical": "left",
        "variable_type": "label"
      },
      {
        "original": "l",
        "canonical": "l",
        "variable_type": "symbol"
      },
      {
        "original": "geq",
        "canonical": "geq",
        "variable_type": "label"
      },
      {
        "original": "leq",
        "canonical": "leq",
        "variable_type": "label"
      },
      {
        "original": "end",
        "canonical": "end",
        "variable_type": "label"
      }
    ],
    "asset_quality_flags": [],
    "is_usable": true,
    "discard_reason_codes": [],
    "created_at": "2026-03-24T06:37:02Z",
    "updated_at": "2026-03-24T06:37:02Z"
  }
]
```

#### node_records

```json
[
  {
    "node_id": "node_1f78912ff5015fa682e4c0c6",
    "problem_id": "prob_4a7ef4f2a9fc80a0034be6d7",
    "node_type": "text_fact",
    "canonical_value": "已知 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-y \\geq 0, \\\\ x+y \\leq 2, \\\\ y \\geq 0,\\end{array}\\right.$围为 ( )",
    "surface_forms": [
      "已知 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-y \\geq 0, \\\\ x+y \\leq 2, \\\\ y \\geq 0,\\end{array}\\right.$围为 ( )"
    ],
    "origin_kind": "text",
    "cognitive_level": "objective",
    "source_refs": [
      "asset_fe7071f92a673f804c479da9"
    ],
    "evidence_refs": [
      "asset_fe7071f92a673f804c479da9"
    ],
    "upstream_node_ids": [],
    "value_type": "condition",
    "normalized_value": {
      "text": "已知 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-y \\geq 0, \\\\ x+y \\leq 2, \\\\ y \\geq 0,\\end{array}\\right.$围为 ( )",
      "segment_index": 1,
      "mentions_visual": false,
      "numeric_tokens": [
        "0",
        "2",
        "0"
      ],
      "unit_mentions": [
        "g",
        "h"
      ],
      "condition_role": "explicit"
    },
    "unit": "g,h",
    "confidence": 0.92,
    "verifiability": "high",
    "ambiguity_level": "low",
    "is_direct_from_source": true,
    "is_generated_by_system": false,
    "is_reviewed_by_human": false,
    "stage_created": "cleaning",
    "status": "active",
    "version": 1,
    "created_at": "2026-03-24T06:37:02Z",
    "updated_at": "2026-03-24T06:37:02Z"
  },
  {
    "node_id": "node_7583bb8bb3458beb6de24af0",
    "problem_id": "prob_4a7ef4f2a9fc80a0034be6d7",
    "node_type": "target_slot",
    "canonical_value": "请只回答第 1 个目标量。",
    "surface_forms": [
      "请只回答第 1 个目标量。"
    ],
    "origin_kind": "text_structure",
    "cognitive_level": "computed",
    "source_refs": [
      "asset_fe7071f92a673f804c479da9"
    ],
    "evidence_refs": [
      "asset_fe7071f92a673f804c479da9"
    ],
    "upstream_node_ids": [],
    "value_type": "short_text",
    "normalized_value": {
      "slot_id": "slot_prob_4a7ef4f2a9fc80a0034be6d7_1",
      "variant_index": 1,
      "split_role": "part_1",
      "slot_type": "short_text",
      "target_text": "请只回答第 1 个目标量。",
      "expected_answer_type": "short_text",
      "expected_answer": "$[-1,1]$",
      "requires_visual_grounding": false
    },
    "unit": null,
    "confidence": 0.92,
    "verifiability": "high",
    "ambiguity_level": "low",
    "is_direct_from_source": false,
    "is_generated_by_system": true,
    "is_reviewed_by_human": false,
    "stage_created": "cleaning",
    "status": "active",
    "version": 1,
    "created_at": "2026-03-24T06:37:02Z",
    "updated_at": "2026-03-24T06:37:02Z"
  },
  {
    "node_id": "node_25d8ef10907d73d1b62cca03",
    "problem_id": "prob_4a7ef4f2a9fc80a0034be6d7",
    "node_type": "answer_claim",
    "canonical_value": "C",
    "surface_forms": [
      "C"
    ],
    "origin_kind": "text",
    "cognitive_level": "objective",
    "source_refs": [
      "asset_cf2db0021dcec1089a11ca32"
    ],
    "evidence_refs": [
      "asset_cf2db0021dcec1089a11ca32"
    ],
    "upstream_node_ids": [],
    "value_type": "option",
    "normalized_value": {
      "answer": "C"
    },
    "unit": null,
    "confidence": 0.98,
    "verifiability": "high",
    "ambiguity_level": "none",
    "is_direct_from_source": true,
    "is_generated_by_system": false,
    "is_reviewed_by_human": false,
    "stage_created": "cleaning",
    "status": "active",
    "version": 1,
    "created_at": "2026-03-24T06:37:02Z",
    "updated_at": "2026-03-24T06:37:02Z"
  },
  {
    "node_id": "node_bc1ec547960878f6f9a76726",
    "problem_id": "prob_4a7ef4f2a9fc80a0034be6d7",
    "node_type": "text_fact",
    "canonical_value": "已知 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-y \\geq 0, \\\\ x+y \\leq 2, \\\\ y \\geq 0,\\end{array}\\right.$围为 ( )\n请只回答第 1 个目标量。",
    "surface_forms": [
      "已知 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-y \\geq 0, \\\\ x+y \\leq 2, \\\\ y \\geq 0,\\end{array}\\right.$围为 ( )\n请只回答第 1 个目标量。"
    ],
    "origin_kind": "reasoning",
    "cognitive_level": "computed",
    "source_refs": [
      "asset_46c5401a16ec8870f2cc8567"
    ],
    "evidence_refs": [
      "asset_46c5401a16ec8870f2cc8567"
    ],
    "upstream_node_ids": [],
    "value_type": "text",
    "normalized_value": {
      "open_variant_id": "open_1ce8c0eceb79589c1187bcd2",
      "parent_problem_id": "prob_4a7ef4f2a9fc80a0034be6d7",
      "variant_index": 1,
      "title": "CMM-Math 子题 1",
      "rewritten_question_text": "已知 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-y \\geq 0, \\\\ x+y \\leq 2, \\\\ y \\geq 0,\\end{array}\\right.$围为 ( )\n请只回答第 1 个目标量。",
      "expected_answer_type": "short_text",
      "expected_answer": "$[-1,1]$",
      "split_role": "part_1"
    },
    "unit": null,
    "confidence": 0.88,
    "verifiability": "medium",
    "ambiguity_level": "low",
    "is_direct_from_source": false,
    "is_generated_by_system": true,
    "is_reviewed_by_human": false,
    "stage_created": "cleaning",
    "status": "active",
    "version": 1,
    "created_at": "2026-03-24T06:37:02Z",
    "updated_at": "2026-03-24T06:37:02Z"
  },
  {
    "node_id": "node_43efa4d0483c844b5a44c5de",
    "problem_id": "prob_4a7ef4f2a9fc80a0034be6d7",
    "node_type": "quality_signal",
    "canonical_value": "solvability=pass",
    "surface_forms": [
      "pass"
    ],
    "origin_kind": "system_quality",
    "cognitive_level": "computed",
    "source_refs": [],
    "evidence_refs": [],
    "upstream_node_ids": [],
    "value_type": "text",
    "normalized_value": {
      "solvability_id": "solv_prob_4a7ef4f2a9fc80a0034be6d7",
      "problem_id": "prob_4a7ef4f2a9fc80a0034be6d7",
      "answer_verifiable": true,
      "target_clear": true,
      "rewrite_complete": true,
      "text_sufficient": true,
      "visual_grounding_available": true,
      "reasoning_path_exists": true,
      "path_mode": "text_only",
      "failure_codes": [],
      "score_breakdown": {
        "answer_verifiable": 1.0,
        "target_clear": 1.0,
        "rewrite_complete": 1.0,
        "text_sufficient": 1.0,
        "visual_grounding": 1.0
      },
      "solvability_score": 1.0,
      "decision_hint": "pass",
      "created_at": "2026-03-24T06:37:02Z"
    },
    "unit": null,
    "confidence": 1.0,
    "verifiability": "high",
    "ambiguity_level": "none",
    "is_direct_from_source": false,
    "is_generated_by_system": true,
    "is_reviewed_by_human": false,
    "stage_created": "cleaning",
    "status": "active",
    "version": 1,
    "created_at": "2026-03-24T06:37:02Z",
    "updated_at": "2026-03-24T06:37:02Z"
  },
  {
    "node_id": "node_4d27cd5fc1b4da02d10ad302",
    "problem_id": "prob_4a7ef4f2a9fc80a0034be6d7",
    "node_type": "quality_signal",
    "canonical_value": "clean_decision=review",
    "surface_forms": [
      "review"
    ],
    "origin_kind": "system_quality",
    "cognitive_level": "computed",
    "source_refs": [],
    "evidence_refs": [],
    "upstream_node_ids": [],
    "value_type": "text",
    "normalized_value": {
      "decision": "review",
      "reasons": [
        "split_variant_needs_review"
      ]
    },
    "unit": null,
    "confidence": 1.0,
    "verifiability": "high",
    "ambiguity_level": "none",
    "is_direct_from_source": false,
    "is_generated_by_system": true,
    "is_reviewed_by_human": false,
    "stage_created": "cleaning",
    "status": "active",
    "version": 1,
    "created_at": "2026-03-24T06:37:02Z",
    "updated_at": "2026-03-24T06:37:02Z"
  }
]
```

#### field_audit_records

```json
[
  {
    "audit_id": "audit_5bffdcca6e79f4dc1b694ed0",
    "problem_id": "prob_4a7ef4f2a9fc80a0034be6d7",
    "record_type": "problem_main_record",
    "field_name": "normalized_question_text",
    "before_value": "已知 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-y \\geq 0, \\\\ x+y \\leq 2, \\\\ y \\geq 0,\\end{array}\\right.$围为 ( )",
    "after_value": "已知 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-y \\geq 0, \\\\ x+y \\leq 2, \\\\ y \\geq 0,\\end{array}\\right.$围为 ( )",
    "change_type": "text_normalized",
    "trigger": "NormalizationAgent",
    "operator_type": "system",
    "created_at": "2026-03-24T06:37:02Z"
  },
  {
    "audit_id": "audit_8e6659bd980a50eb80a11ac1",
    "problem_id": "prob_4a7ef4f2a9fc80a0034be6d7",
    "record_type": "problem_main_record",
    "field_name": "normalized_answer_text",
    "before_value": "C",
    "after_value": "C",
    "change_type": "answer_canonicalized",
    "trigger": "NormalizationAgent",
    "operator_type": "system",
    "created_at": "2026-03-24T06:37:02Z"
  },
  {
    "audit_id": "audit_26f11d76a596ede17162b050",
    "problem_id": "prob_4a7ef4f2a9fc80a0034be6d7",
    "record_type": "rewrite_report",
    "field_name": "rewrite_strategy",
    "before_value": null,
    "after_value": "split_open",
    "change_type": "question_rewritten",
    "trigger": "QuestionRewriteAgent",
    "operator_type": "system",
    "created_at": "2026-03-24T06:37:02Z"
  },
  {
    "audit_id": "audit_4d27cd5fc1b4da02d10ad302",
    "problem_id": "prob_4a7ef4f2a9fc80a0034be6d7",
    "record_type": "cleaning_record",
    "field_name": "decision",
    "before_value": null,
    "after_value": "review",
    "change_type": "gate_decision",
    "trigger": "CleanGateAgent",
    "operator_type": "system",
    "created_at": "2026-03-24T06:37:02Z"
  },
  {
    "audit_id": "audit_3081d10e6ad7091e9c33e2a1",
    "problem_id": "prob_4a7ef4f2a9fc80a0034be6d7",
    "record_type": "normalized_assets",
    "field_name": "variable_aliases",
    "before_value": null,
    "after_value": [
      {
        "original": "x",
        "canonical": "x",
        "variable_type": "symbol"
      },
      {
        "original": "y",
        "canonical": "y",
        "variable_type": "symbol"
      },
      {
        "original": "left",
        "canonical": "left",
        "variable_type": "label"
      },
      {
        "original": "l",
        "canonical": "l",
        "variable_type": "symbol"
      },
      {
        "original": "geq",
        "canonical": "geq",
        "variable_type": "label"
      },
      {
        "original": "leq",
        "canonical": "leq",
        "variable_type": "label"
      },
      {
        "original": "end",
        "canonical": "end",
        "variable_type": "label"
      }
    ],
    "change_type": "variable_canonicalized",
    "trigger": "NormalizationAgent",
    "operator_type": "system",
    "created_at": "2026-03-24T06:37:02Z"
  }
]
```

#### reject_records

```json
[]
```

### 4.1 完整 sample bundle 原文件

- `outputs/user_requested_batch_review/pipeline_runs/run_6f9fadee9214c91e/datasets/cmm_math/samples/prob_4a7ef4f2a9fc80a0034be6d7.json`
