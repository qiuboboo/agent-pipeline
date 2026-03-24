# CMM-Math / prob_b1cb15b0aa1053ab2cf788ec

- source_problem_id: `18925`
- source_split: `train`
- clean_decision: `pass`
- rewrite_strategy: `blank_open`
- full sample bundle JSON: `outputs/user_requested_batch_review/pipeline_runs/run_637ca3432da6ddfb/datasets/cmm_math/samples/prob_b1cb15b0aa1053ab2cf788ec.json`

## 1. 原始内容（处理前）

### 1.1 原始快照

```json
{
  "dataset_key": "cmm_math",
  "source_problem_id": "18925",
  "source_split": "train",
  "raw_question_text": "若实数 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-3 y+4 \\geq 0 \\\\ 3 x-y-4 \\leq 0 \\\\ x+y \\geq 0\\end{array}\\right.$, 则 $z=3 x+2 y$ 的最大值是",
  "raw_answer_text": "C",
  "choice_map": {
    "A": "-1",
    "B": "1",
    "C": "10",
    "D": "12"
  },
  "image_sources": [],
  "metadata": {
    "row_index": 13,
    "question_field": "question",
    "answer_field": "answer",
    "image_field": null,
    "choice_field": "options"
  },
  "raw_record": {
    "id": "18925",
    "image": "[]",
    "answer": "C",
    "solution": "null",
    "level": "高二",
    "question": "若实数 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-3 y+4 \\geq 0 \\\\ 3 x-y-4 \\leq 0 \\\\ x+y \\geq 0\\end{array}\\right.$, 则 $z=3 x+2 y$ 的最大值是",
    "options": "A. -1\nB. 1\nC. 10\nD. 12",
    "subject": "解析几何",
    "analysis": "画出满足约束条件的可行域如图中阴影部分所示。\n\n![](https://cdn.mathpix.com/cropped/2024_04_19_8a964f9ccd87371be6e0g-113、.jpg?height=819&width=873&top_left_y=573&top_left_x=503)\n\n因为 $z=3 x+2 y$, 所以 $y=-\\frac{3}{2} x+\\frac{1}{2} z$.\n\n平移直线 $y=-\\frac{3}{2} x+\\frac{1}{2} z$ 可知, 当该直线经过点 $A$ 时, $z$ 取得最大值.\n\n联立两直线方程可得 $\\left\\{\\begin{array}{l}x-3 y+4=0 \\\\ 3 x-y-4=0\\end{array}\\right.$, 解得 $\\left\\{\\begin{array}{l}x=2 \\\\ y=2\\end{array}\\right.$.\n\n即点 $A$ 坐标为 $A(2,2)$, 所以 $z_{\\text {max }}=3 \\times 2+2 \\times 2=10$. 故选 C."
  }
}
```

### 1.2 原始图片

- （无）

## 2. 处理前后对照

### 2.1 关键字段对照

| 字段 | 处理前 | 处理后 |
| --- | --- | --- |
| question_text | 若实数 $x, y$ 满足约束条件 $\left\{\begin{array}{l}x-3 y+4 \geq 0 \\ 3 x-y-4 \leq 0 \\ x+y \geq 0\end{array}\right.$, 则 $z=3 x+2 y$ 的最大值是 | 若实数 $x, y$ 满足约束条件 $\left\{\begin{array}{l}x-3 y+4 \geq 0 \\ 3 x-y-4 \leq 0 \\ x+y \geq 0\end{array}\right.$, 则 $z=3 x+2 y$ 的最大值是 |
| answer_text | C | C |
| answer_type | - | option |
| image_count | 0 | 0 |
| text_dominant | - | True |
| cleaning_path | - | text_lightweight |
| clean_decision | - | pass |
| alignment_status | - | good |
| solvability_decision_hint | - | pass |
| rewrite_strategy | - | blank_open |

### 2.2 结构化处理后结果

#### problem_main_record

```json
{
  "problem_id": "prob_b1cb15b0aa1053ab2cf788ec",
  "source_dataset": "CMM-Math",
  "source_split": "train",
  "source_problem_id": "18925",
  "ingest_batch_id": "multidataset-clean_20260324T074830Z",
  "problem_type": "multimodal_reasoning",
  "domain_tags": [
    "数学"
  ],
  "language": "zh",
  "raw_question_text": "若实数 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-3 y+4 \\geq 0 \\\\ 3 x-y-4 \\leq 0 \\\\ x+y \\geq 0\\end{array}\\right.$, 则 $z=3 x+2 y$ 的最大值是",
  "normalized_question_text": "若实数 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-3 y+4 \\geq 0 \\\\ 3 x-y-4 \\leq 0 \\\\ x+y \\geq 0\\end{array}\\right.$, 则 $z=3 x+2 y$ 的最大值是",
  "raw_answer_text": "C",
  "normalized_answer_text": "C",
  "answer_type": "option",
  "image_count": 0,
  "has_multiple_images": false,
  "requires_image": false,
  "multimodal_strength_score": 0.33,
  "multi_step_score": 0.3647,
  "verifiability_score": 1.0,
  "quality_risk_flags": [],
  "current_status": "clean_passed",
  "clean_decision": "pass",
  "clean_decision_reason_codes": [
    "meets_cleaning_requirements"
  ],
  "review_priority": "normal",
  "annotation_ready": true,
  "qa_precheck_ready": true,
  "release_reserved": {},
  "rewrite_strategy": "blank_open",
  "open_variant_count": 1,
  "candidate_id": "cand_b1cb15b0aa1053ab2cf788ec",
  "text_dominant": true,
  "cleaning_path": "text_lightweight",
  "alignment_status": "good",
  "solvability_score": 1.0,
  "solvability_decision_hint": "pass",
  "created_at": "2026-03-24T07:48:35Z",
  "updated_at": "2026-03-24T07:48:35Z",
  "initial_image_dependency_score": 0.28,
  "initial_multi_solution_score": 0.46,
  "initial_verifiability_score": 0.78,
  "multi_solution_mining_policy": "aggressive"
}
```

#### clean_problem_record

```json
{
  "clean_problem_record_id": "cleanprob_e9180ecbf2d9d7dc5ff3b143",
  "problem_id": "prob_b1cb15b0aa1053ab2cf788ec",
  "source_dataset": "CMM-Math",
  "source_problem_id": "18925",
  "normalized_question_text": "若实数 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-3 y+4 \\geq 0 \\\\ 3 x-y-4 \\leq 0 \\\\ x+y \\geq 0\\end{array}\\right.$, 则 $z=3 x+2 y$ 的最大值是",
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
  "clean_decision": "pass",
  "decision_reason_codes": [
    "meets_cleaning_requirements"
  ],
  "created_at": "2026-03-24T07:48:35Z"
}
```

#### normalized_assets

```json
{
  "normalized_assets_id": "nassets_e9180ecbf2d9d7dc5ff3b143",
  "problem_id": "prob_b1cb15b0aa1053ab2cf788ec",
  "normalized_question_text": "若实数 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-3 y+4 \\geq 0 \\\\ 3 x-y-4 \\leq 0 \\\\ x+y \\geq 0\\end{array}\\right.$, 则 $z=3 x+2 y$ 的最大值是",
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
    },
    {
      "original": "z",
      "canonical": "z",
      "variable_type": "symbol"
    }
  ],
  "sentence_segments": [
    {
      "segment_index": 1,
      "text": "若实数 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-3 y+4 \\geq 0 \\\\ 3 x-y-4 \\leq 0 \\\\ x+y \\geq 0\\end{array}\\right.$, 则 $z=3 x+2 y$ 的最大值是"
    }
  ],
  "image_regions": [],
  "text_dominant": true,
  "cleaning_path": "text_lightweight",
  "created_at": "2026-03-24T07:48:35Z"
}
```

#### text_structure_record

```json
{
  "text_structure_id": "text_prob_b1cb15b0aa1053ab2cf788ec",
  "problem_id": "prob_b1cb15b0aa1053ab2cf788ec",
  "question_type": "multiple_choice",
  "conditions": [
    {
      "text": "若实数 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-3 y+4 \\geq 0 \\\\ 3 x-y-4 \\leq 0 \\\\ x+y \\geq 0\\end{array}\\right.$, 则 $z=3 x+2 y$ 的最大值是",
      "segment_index": 1,
      "mentions_visual": false,
      "numeric_tokens": [
        "-3",
        "+4",
        "0",
        "3",
        "-4",
        "0",
        "0",
        "3",
        "+2"
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
      "text": "若实数 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-3 y+4 \\geq 0 \\\\ 3 x-y-4 \\leq 0 \\\\ x+y \\geq 0\\end{array}\\right.$, 则 $z=3 x+2 y$ 的最大值是",
      "segment_index": 1,
      "mentions_visual": false,
      "numeric_tokens": [
        "-3",
        "+4",
        "0",
        "3",
        "-4",
        "0",
        "0",
        "3",
        "+2"
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
      "slot_id": "slot_prob_b1cb15b0aa1053ab2cf788ec_1",
      "variant_index": 1,
      "split_role": "single",
      "slot_type": "numeric",
      "target_text": "若实数 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-3 y+4 \\geq 0 \\\\ 3 x-y-4 \\leq 0 \\\\ x+y \\geq 0\\end{array}\\right.$, 则 $z=3 x+2 y$ 的最大值是",
      "expected_answer_type": "numeric",
      "expected_answer": "10",
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
    },
    {
      "original": "z",
      "canonical": "z",
      "variable_type": "symbol"
    }
  ],
  "unit_mentions": [
    "g",
    "h"
  ],
  "sentence_segments": [
    {
      "segment_index": 1,
      "text": "若实数 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-3 y+4 \\geq 0 \\\\ 3 x-y-4 \\leq 0 \\\\ x+y \\geq 0\\end{array}\\right.$, 则 $z=3 x+2 y$ 的最大值是"
    }
  ],
  "requires_visual_grounding": false,
  "text_structure_status": "complete",
  "parser_confidence": 0.92,
  "created_at": "2026-03-24T07:48:35Z"
}
```

#### visual_structure_records

```json
[]
```

#### alignment_record

```json
{
  "alignment_id": "align_e9180ecbf2d9d7dc5ff3b143",
  "problem_id": "prob_b1cb15b0aa1053ab2cf788ec",
  "image_entity_refs": [],
  "text_span_refs": [
    "asset_prob_b1cb15b0aa1053ab2cf788ec_question_text_normalized"
  ],
  "alignment_pairs": [],
  "conflict_pairs": [],
  "coverage_score": 1.0,
  "consistency_score": 1.0,
  "alignment_status": "good",
  "created_at": "2026-03-24T07:48:35Z",
  "cleaning_path": "text_lightweight",
  "text_dominant": true
}
```

#### solvability_report

```json
{
  "solvability_id": "solv_prob_b1cb15b0aa1053ab2cf788ec",
  "problem_id": "prob_b1cb15b0aa1053ab2cf788ec",
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
  "created_at": "2026-03-24T07:48:35Z"
}
```

#### cleaning_record

```json
{
  "cleaning_id": "clean_e9180ecbf2d9d7dc5ff3b143",
  "problem_id": "prob_b1cb15b0aa1053ab2cf788ec",
  "cleaning_version": "v3.0.0",
  "pipeline_run_id": "run_637ca3432da6ddfb",
  "dataset_name": "CMM-Math",
  "input_asset_ids": [
    "asset_69c52bb22f78a8fd7b938f54",
    "asset_e76e1237ba23812836375aab",
    "asset_5ed186c15bb56296d08ec5e0",
    "asset_e0df9c8cc62b01ef82b7c57e",
    "asset_b7c848f3e958a70063418da3"
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
      "variable_alias_count": 8
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
    "alignment_id": "align_e9180ecbf2d9d7dc5ff3b143",
    "coverage_score": 1.0,
    "consistency_score": 1.0,
    "alignment_status": "good",
    "conflict_count": 0
  },
  "text_structure_summary": {
    "text_structure_id": "text_prob_b1cb15b0aa1053ab2cf788ec",
    "question_type": "multiple_choice",
    "condition_count": 1,
    "target_count": 1,
    "answer_slot_count": 1,
    "status": "complete"
  },
  "solvability_summary": {
    "solvability_id": "solv_prob_b1cb15b0aa1053ab2cf788ec",
    "solvability_score": 1.0,
    "reasoning_path_exists": true,
    "decision_hint": "pass",
    "failure_codes": []
  },
  "rewrite_summary": {
    "strategy": "blank_open",
    "variant_count": 1,
    "discard_reason_codes": []
  },
  "missing_field_summary": {
    "missing_question_text": false,
    "missing_answer_text": false,
    "missing_image_count": 0
  },
  "risk_flags": [],
  "clean_score": 0.8491,
  "decision": "pass",
  "decision_reason_codes": [
    "meets_cleaning_requirements"
  ],
  "review_ticket_id": null,
  "operator_type": "system",
  "started_at": "2026-03-24T07:48:35Z",
  "finished_at": "2026-03-24T07:48:35Z",
  "candidate_id": "cand_b1cb15b0aa1053ab2cf788ec",
  "cleaning_path": "text_lightweight",
  "text_dominant": true
}
```

## 3. 开放化改写前后

### 3.1 改写前

```json
{
  "question_text_before_rewrite": "若实数 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-3 y+4 \\geq 0 \\\\ 3 x-y-4 \\leq 0 \\\\ x+y \\geq 0\\end{array}\\right.$, 则 $z=3 x+2 y$ 的最大值是",
  "answer_text_before_rewrite": "C",
  "raw_question_text": "若实数 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-3 y+4 \\geq 0 \\\\ 3 x-y-4 \\leq 0 \\\\ x+y \\geq 0\\end{array}\\right.$, 则 $z=3 x+2 y$ 的最大值是",
  "raw_answer_text": "C"
}
```

### 3.2 改写后

```json
{
  "rewrite_report": {
    "rewrite_id": "rewrite_e9180ecbf2d9d7dc5ff3b143",
    "problem_id": "prob_b1cb15b0aa1053ab2cf788ec",
    "source_problem_id": "18925",
    "strategy": "blank_open",
    "rationale": "Converted multiple choice into blank-style open-ended question.",
    "discard_reason_codes": [],
    "variant_count": 1,
    "variants": [
      {
        "open_variant_id": "open_dcbc11bd21a58a1af0cea02d",
        "parent_problem_id": "prob_b1cb15b0aa1053ab2cf788ec",
        "variant_index": 1,
        "title": "CMM-Math 开放题",
        "rewritten_question_text": "若实数 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-3 y+4 \\geq 0 \\\\ 3 x-y-4 \\leq 0 \\\\ x+y \\geq 0\\end{array}\\right.$, 则 $z=3 x+2 y$ 的最大值是",
        "expected_answer_type": "numeric",
        "expected_answer": "10",
        "split_role": "single"
      }
    ],
    "created_at": "2026-03-24T07:48:35Z"
  },
  "open_ended_problem_variants": [
    {
      "open_variant_id": "open_dcbc11bd21a58a1af0cea02d",
      "parent_problem_id": "prob_b1cb15b0aa1053ab2cf788ec",
      "variant_index": 1,
      "title": "CMM-Math 开放题",
      "rewritten_question_text": "若实数 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-3 y+4 \\geq 0 \\\\ 3 x-y-4 \\leq 0 \\\\ x+y \\geq 0\\end{array}\\right.$, 则 $z=3 x+2 y$ 的最大值是",
      "expected_answer_type": "numeric",
      "expected_answer": "10",
      "split_role": "single"
    }
  ]
}
```

## 4. 完整 collection + cleaning 输出对象

#### candidate_problem_record

```json
{
  "candidate_id": "cand_b1cb15b0aa1053ab2cf788ec",
  "source_dataset": "CMM-Math",
  "source_split": "train",
  "source_problem_id": "18925",
  "subject": "数学",
  "raw_question_text": "若实数 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-3 y+4 \\geq 0 \\\\ 3 x-y-4 \\leq 0 \\\\ x+y \\geq 0\\end{array}\\right.$, 则 $z=3 x+2 y$ 的最大值是",
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
    "row_index": 13,
    "question_field": "question",
    "answer_field": "answer",
    "image_field": null,
    "choice_field": "options"
  },
  "created_at": "2026-03-24T07:48:35Z"
}
```

#### raw_asset_bundle

```json
{
  "raw_asset_bundle_id": "bundle_e49f225a17c5045bdebafaad",
  "candidate_id": "cand_b1cb15b0aa1053ab2cf788ec",
  "source_dataset": "CMM-Math",
  "source_problem_id": "18925",
  "assets": [
    {
      "asset_role": "question_text_raw",
      "storage_uri": "inline://prob_b1cb15b0aa1053ab2cf788ec/question_source",
      "is_present": true
    },
    {
      "asset_role": "answer_text_raw",
      "storage_uri": "inline://prob_b1cb15b0aa1053ab2cf788ec/answer_source",
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
  "created_at": "2026-03-24T07:48:35Z"
}
```

#### candidate_pool_entry

```json
{
  "candidate_pool_entry_id": "cpool_3bf0cd5185c4ac81daeb0fdd",
  "candidate_id": "cand_b1cb15b0aa1053ab2cf788ec",
  "source_dataset": "CMM-Math",
  "source_problem_id": "18925",
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
  "created_at": "2026-03-24T07:48:35Z"
}
```

#### clean_pool_entries

```json
[
  {
    "clean_pool_entry_id": "cleanpool_e9180ecbf2d9d7dc5ff3b143",
    "candidate_id": "cand_b1cb15b0aa1053ab2cf788ec",
    "problem_id": "prob_b1cb15b0aa1053ab2cf788ec",
    "dataset_name": "CMM-Math",
    "pool_status": "ready_for_annotation",
    "clean_decision": "pass",
    "review_required": false,
    "rewrite_strategy": "blank_open",
    "open_variant_count": 1,
    "text_dominant": true,
    "cleaning_path": "text_lightweight",
    "created_at": "2026-03-24T07:48:35Z"
  }
]
```

#### rewrite_reports

```json
[
  {
    "rewrite_id": "rewrite_e9180ecbf2d9d7dc5ff3b143",
    "problem_id": "prob_b1cb15b0aa1053ab2cf788ec",
    "source_problem_id": "18925",
    "strategy": "blank_open",
    "rationale": "Converted multiple choice into blank-style open-ended question.",
    "discard_reason_codes": [],
    "variant_count": 1,
    "variants": [
      {
        "open_variant_id": "open_dcbc11bd21a58a1af0cea02d",
        "parent_problem_id": "prob_b1cb15b0aa1053ab2cf788ec",
        "variant_index": 1,
        "title": "CMM-Math 开放题",
        "rewritten_question_text": "若实数 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-3 y+4 \\geq 0 \\\\ 3 x-y-4 \\leq 0 \\\\ x+y \\geq 0\\end{array}\\right.$, 则 $z=3 x+2 y$ 的最大值是",
        "expected_answer_type": "numeric",
        "expected_answer": "10",
        "split_role": "single"
      }
    ],
    "created_at": "2026-03-24T07:48:35Z"
  }
]
```

#### open_ended_problem_variants

```json
[
  {
    "open_variant_id": "open_dcbc11bd21a58a1af0cea02d",
    "parent_problem_id": "prob_b1cb15b0aa1053ab2cf788ec",
    "variant_index": 1,
    "title": "CMM-Math 开放题",
    "rewritten_question_text": "若实数 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-3 y+4 \\geq 0 \\\\ 3 x-y-4 \\leq 0 \\\\ x+y \\geq 0\\end{array}\\right.$, 则 $z=3 x+2 y$ 的最大值是",
    "expected_answer_type": "numeric",
    "expected_answer": "10",
    "split_role": "single"
  }
]
```

#### asset_records

```json
[
  {
    "asset_id": "asset_69c52bb22f78a8fd7b938f54",
    "problem_id": "prob_b1cb15b0aa1053ab2cf788ec",
    "asset_type": "text",
    "asset_role": "question_text_source",
    "source_uri": "source://cmm_math/train/18925/question",
    "storage_uri": "inline://prob_b1cb15b0aa1053ab2cf788ec/question_source",
    "file_format": "txt",
    "file_size_bytes": 158,
    "width": null,
    "height": null,
    "sha256": "97f714c0e2a1f6347578189ba7576c30f4f1d1a50c3f54f22d8ee418c72be674",
    "perceptual_hash": null,
    "source_text_snapshot": "若实数 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-3 y+4 \\geq 0 \\\\ 3 x-y-4 \\leq 0 \\\\ x+y \\geq 0\\end{array}\\right.$, 则 $z=3 x+2 y$ 的最大值是",
    "normalized_text_snapshot": null,
    "text_completeness_score": 0.6643,
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
      },
      {
        "original": "z",
        "canonical": "z",
        "variable_type": "symbol"
      }
    ],
    "asset_quality_flags": [],
    "is_usable": true,
    "discard_reason_codes": [],
    "created_at": "2026-03-24T07:48:35Z",
    "updated_at": "2026-03-24T07:48:35Z"
  },
  {
    "asset_id": "asset_e76e1237ba23812836375aab",
    "problem_id": "prob_b1cb15b0aa1053ab2cf788ec",
    "asset_type": "text",
    "asset_role": "question_text_normalized",
    "source_uri": null,
    "storage_uri": "inline://prob_b1cb15b0aa1053ab2cf788ec/question_normalized",
    "file_format": "txt",
    "file_size_bytes": 158,
    "width": null,
    "height": null,
    "sha256": "97f714c0e2a1f6347578189ba7576c30f4f1d1a50c3f54f22d8ee418c72be674",
    "perceptual_hash": null,
    "source_text_snapshot": "若实数 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-3 y+4 \\geq 0 \\\\ 3 x-y-4 \\leq 0 \\\\ x+y \\geq 0\\end{array}\\right.$, 则 $z=3 x+2 y$ 的最大值是",
    "normalized_text_snapshot": "若实数 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-3 y+4 \\geq 0 \\\\ 3 x-y-4 \\leq 0 \\\\ x+y \\geq 0\\end{array}\\right.$, 则 $z=3 x+2 y$ 的最大值是",
    "text_completeness_score": 0.6643,
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
      },
      {
        "original": "z",
        "canonical": "z",
        "variable_type": "symbol"
      }
    ],
    "asset_quality_flags": [],
    "is_usable": true,
    "discard_reason_codes": [],
    "created_at": "2026-03-24T07:48:35Z",
    "updated_at": "2026-03-24T07:48:35Z"
  },
  {
    "asset_id": "asset_5ed186c15bb56296d08ec5e0",
    "problem_id": "prob_b1cb15b0aa1053ab2cf788ec",
    "asset_type": "answer",
    "asset_role": "answer_raw",
    "source_uri": "source://cmm_math/train/18925/answer",
    "storage_uri": "inline://prob_b1cb15b0aa1053ab2cf788ec/answer_raw",
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
    "created_at": "2026-03-24T07:48:35Z",
    "updated_at": "2026-03-24T07:48:35Z"
  },
  {
    "asset_id": "asset_e0df9c8cc62b01ef82b7c57e",
    "problem_id": "prob_b1cb15b0aa1053ab2cf788ec",
    "asset_type": "answer",
    "asset_role": "answer_normalized",
    "source_uri": null,
    "storage_uri": "inline://prob_b1cb15b0aa1053ab2cf788ec/answer_normalized",
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
    "created_at": "2026-03-24T07:48:35Z",
    "updated_at": "2026-03-24T07:48:35Z"
  },
  {
    "asset_id": "asset_b7c848f3e958a70063418da3",
    "problem_id": "prob_b1cb15b0aa1053ab2cf788ec",
    "asset_type": "text",
    "asset_role": "question_text_open_variant",
    "source_uri": null,
    "storage_uri": "inline://open_dcbc11bd21a58a1af0cea02d",
    "file_format": "txt",
    "file_size_bytes": 158,
    "width": null,
    "height": null,
    "sha256": "97f714c0e2a1f6347578189ba7576c30f4f1d1a50c3f54f22d8ee418c72be674",
    "perceptual_hash": null,
    "source_text_snapshot": "若实数 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-3 y+4 \\geq 0 \\\\ 3 x-y-4 \\leq 0 \\\\ x+y \\geq 0\\end{array}\\right.$, 则 $z=3 x+2 y$ 的最大值是",
    "normalized_text_snapshot": "若实数 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-3 y+4 \\geq 0 \\\\ 3 x-y-4 \\leq 0 \\\\ x+y \\geq 0\\end{array}\\right.$, 则 $z=3 x+2 y$ 的最大值是",
    "text_completeness_score": 0.6643,
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
      },
      {
        "original": "z",
        "canonical": "z",
        "variable_type": "symbol"
      }
    ],
    "asset_quality_flags": [],
    "is_usable": true,
    "discard_reason_codes": [],
    "created_at": "2026-03-24T07:48:35Z",
    "updated_at": "2026-03-24T07:48:35Z"
  }
]
```

#### node_records

```json
[
  {
    "node_id": "node_d7f9b32dc6efc61d6d0e8545",
    "problem_id": "prob_b1cb15b0aa1053ab2cf788ec",
    "node_type": "text_fact",
    "canonical_value": "若实数 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-3 y+4 \\geq 0 \\\\ 3 x-y-4 \\leq 0 \\\\ x+y \\geq 0\\end{array}\\right.$, 则 $z=3 x+2 y$ 的最大值是",
    "surface_forms": [
      "若实数 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-3 y+4 \\geq 0 \\\\ 3 x-y-4 \\leq 0 \\\\ x+y \\geq 0\\end{array}\\right.$, 则 $z=3 x+2 y$ 的最大值是"
    ],
    "origin_kind": "text",
    "cognitive_level": "objective",
    "source_refs": [
      "asset_e76e1237ba23812836375aab"
    ],
    "evidence_refs": [
      "asset_e76e1237ba23812836375aab"
    ],
    "upstream_node_ids": [],
    "value_type": "condition",
    "normalized_value": {
      "text": "若实数 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-3 y+4 \\geq 0 \\\\ 3 x-y-4 \\leq 0 \\\\ x+y \\geq 0\\end{array}\\right.$, 则 $z=3 x+2 y$ 的最大值是",
      "segment_index": 1,
      "mentions_visual": false,
      "numeric_tokens": [
        "-3",
        "+4",
        "0",
        "3",
        "-4",
        "0",
        "0",
        "3",
        "+2"
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
    "created_at": "2026-03-24T07:48:35Z",
    "updated_at": "2026-03-24T07:48:35Z"
  },
  {
    "node_id": "node_bd379272a34230ff92602545",
    "problem_id": "prob_b1cb15b0aa1053ab2cf788ec",
    "node_type": "target_slot",
    "canonical_value": "若实数 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-3 y+4 \\geq 0 \\\\ 3 x-y-4 \\leq 0 \\\\ x+y \\geq 0\\end{array}\\right.$, 则 $z=3 x+2 y$ 的最大值是",
    "surface_forms": [
      "若实数 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-3 y+4 \\geq 0 \\\\ 3 x-y-4 \\leq 0 \\\\ x+y \\geq 0\\end{array}\\right.$, 则 $z=3 x+2 y$ 的最大值是"
    ],
    "origin_kind": "text_structure",
    "cognitive_level": "computed",
    "source_refs": [
      "asset_e76e1237ba23812836375aab"
    ],
    "evidence_refs": [
      "asset_e76e1237ba23812836375aab"
    ],
    "upstream_node_ids": [],
    "value_type": "numeric",
    "normalized_value": {
      "slot_id": "slot_prob_b1cb15b0aa1053ab2cf788ec_1",
      "variant_index": 1,
      "split_role": "single",
      "slot_type": "numeric",
      "target_text": "若实数 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-3 y+4 \\geq 0 \\\\ 3 x-y-4 \\leq 0 \\\\ x+y \\geq 0\\end{array}\\right.$, 则 $z=3 x+2 y$ 的最大值是",
      "expected_answer_type": "numeric",
      "expected_answer": "10",
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
    "created_at": "2026-03-24T07:48:35Z",
    "updated_at": "2026-03-24T07:48:35Z"
  },
  {
    "node_id": "node_3ae3b7b83e67b6178fee6835",
    "problem_id": "prob_b1cb15b0aa1053ab2cf788ec",
    "node_type": "answer_claim",
    "canonical_value": "C",
    "surface_forms": [
      "C"
    ],
    "origin_kind": "text",
    "cognitive_level": "objective",
    "source_refs": [
      "asset_e0df9c8cc62b01ef82b7c57e"
    ],
    "evidence_refs": [
      "asset_e0df9c8cc62b01ef82b7c57e"
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
    "created_at": "2026-03-24T07:48:35Z",
    "updated_at": "2026-03-24T07:48:35Z"
  },
  {
    "node_id": "node_4d573460e7c44ca96b59ec43",
    "problem_id": "prob_b1cb15b0aa1053ab2cf788ec",
    "node_type": "text_fact",
    "canonical_value": "若实数 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-3 y+4 \\geq 0 \\\\ 3 x-y-4 \\leq 0 \\\\ x+y \\geq 0\\end{array}\\right.$, 则 $z=3 x+2 y$ 的最大值是",
    "surface_forms": [
      "若实数 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-3 y+4 \\geq 0 \\\\ 3 x-y-4 \\leq 0 \\\\ x+y \\geq 0\\end{array}\\right.$, 则 $z=3 x+2 y$ 的最大值是"
    ],
    "origin_kind": "reasoning",
    "cognitive_level": "computed",
    "source_refs": [
      "asset_b7c848f3e958a70063418da3"
    ],
    "evidence_refs": [
      "asset_b7c848f3e958a70063418da3"
    ],
    "upstream_node_ids": [],
    "value_type": "text",
    "normalized_value": {
      "open_variant_id": "open_dcbc11bd21a58a1af0cea02d",
      "parent_problem_id": "prob_b1cb15b0aa1053ab2cf788ec",
      "variant_index": 1,
      "title": "CMM-Math 开放题",
      "rewritten_question_text": "若实数 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-3 y+4 \\geq 0 \\\\ 3 x-y-4 \\leq 0 \\\\ x+y \\geq 0\\end{array}\\right.$, 则 $z=3 x+2 y$ 的最大值是",
      "expected_answer_type": "numeric",
      "expected_answer": "10",
      "split_role": "single"
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
    "created_at": "2026-03-24T07:48:35Z",
    "updated_at": "2026-03-24T07:48:35Z"
  },
  {
    "node_id": "node_b8c891937c212d1785da03cb",
    "problem_id": "prob_b1cb15b0aa1053ab2cf788ec",
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
      "solvability_id": "solv_prob_b1cb15b0aa1053ab2cf788ec",
      "problem_id": "prob_b1cb15b0aa1053ab2cf788ec",
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
      "created_at": "2026-03-24T07:48:35Z"
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
    "created_at": "2026-03-24T07:48:35Z",
    "updated_at": "2026-03-24T07:48:35Z"
  },
  {
    "node_id": "node_69ea4d3f5fa664aab41fb445",
    "problem_id": "prob_b1cb15b0aa1053ab2cf788ec",
    "node_type": "quality_signal",
    "canonical_value": "clean_decision=pass",
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
      "decision": "pass",
      "reasons": [
        "meets_cleaning_requirements"
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
    "created_at": "2026-03-24T07:48:35Z",
    "updated_at": "2026-03-24T07:48:35Z"
  }
]
```

#### field_audit_records

```json
[
  {
    "audit_id": "audit_884841adba3b9d39e0ad3390",
    "problem_id": "prob_b1cb15b0aa1053ab2cf788ec",
    "record_type": "problem_main_record",
    "field_name": "normalized_question_text",
    "before_value": "若实数 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-3 y+4 \\geq 0 \\\\ 3 x-y-4 \\leq 0 \\\\ x+y \\geq 0\\end{array}\\right.$, 则 $z=3 x+2 y$ 的最大值是",
    "after_value": "若实数 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-3 y+4 \\geq 0 \\\\ 3 x-y-4 \\leq 0 \\\\ x+y \\geq 0\\end{array}\\right.$, 则 $z=3 x+2 y$ 的最大值是",
    "change_type": "text_normalized",
    "trigger": "NormalizationAgent",
    "operator_type": "system",
    "created_at": "2026-03-24T07:48:35Z"
  },
  {
    "audit_id": "audit_c58bc66dddf61d8b08ed8bd0",
    "problem_id": "prob_b1cb15b0aa1053ab2cf788ec",
    "record_type": "problem_main_record",
    "field_name": "normalized_answer_text",
    "before_value": "C",
    "after_value": "C",
    "change_type": "answer_canonicalized",
    "trigger": "NormalizationAgent",
    "operator_type": "system",
    "created_at": "2026-03-24T07:48:35Z"
  },
  {
    "audit_id": "audit_24e5b8d3ffbd94530ae80381",
    "problem_id": "prob_b1cb15b0aa1053ab2cf788ec",
    "record_type": "rewrite_report",
    "field_name": "rewrite_strategy",
    "before_value": null,
    "after_value": "blank_open",
    "change_type": "question_rewritten",
    "trigger": "QuestionRewriteAgent",
    "operator_type": "system",
    "created_at": "2026-03-24T07:48:35Z"
  },
  {
    "audit_id": "audit_69ea4d3f5fa664aab41fb445",
    "problem_id": "prob_b1cb15b0aa1053ab2cf788ec",
    "record_type": "cleaning_record",
    "field_name": "decision",
    "before_value": null,
    "after_value": "pass",
    "change_type": "gate_decision",
    "trigger": "CleanGateAgent",
    "operator_type": "system",
    "created_at": "2026-03-24T07:48:35Z"
  },
  {
    "audit_id": "audit_e1d2769ed2a707f7ddc7ecd5",
    "problem_id": "prob_b1cb15b0aa1053ab2cf788ec",
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
      },
      {
        "original": "z",
        "canonical": "z",
        "variable_type": "symbol"
      }
    ],
    "change_type": "variable_canonicalized",
    "trigger": "NormalizationAgent",
    "operator_type": "system",
    "created_at": "2026-03-24T07:48:35Z"
  }
]
```

#### reject_records

```json
[]
```

### 4.1 完整 sample bundle 原文件

- `outputs/user_requested_batch_review/pipeline_runs/run_637ca3432da6ddfb/datasets/cmm_math/samples/prob_b1cb15b0aa1053ab2cf788ec.json`
