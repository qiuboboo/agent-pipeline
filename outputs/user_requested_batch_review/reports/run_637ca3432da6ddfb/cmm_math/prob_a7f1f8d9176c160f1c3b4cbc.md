# CMM-Math / prob_a7f1f8d9176c160f1c3b4cbc

- source_problem_id: `19894`
- source_split: `train`
- clean_decision: `review`
- rewrite_strategy: `split_open`
- full sample bundle JSON: `outputs/user_requested_batch_review/pipeline_runs/run_637ca3432da6ddfb/datasets/cmm_math/samples/prob_a7f1f8d9176c160f1c3b4cbc.json`

## 1. 原始内容（处理前）

### 1.1 原始快照

```json
{
  "dataset_key": "cmm_math",
  "source_problem_id": "19894",
  "source_split": "train",
  "raw_question_text": "已知点 $(-3,-1)$ 和点 $(4,-6)$ 在直线 $3 x-2 y-a=0$ 的两侧, 则 $a$ 的取值范围为 ( )",
  "raw_answer_text": "B",
  "choice_map": {
    "A": "$(-24,7)$",
    "B": "$(-7,24)$",
    "C": "$(-\\infty,-7) \\cup(24, \\infty)$",
    "D": "$(-\\infty,-24) \\cup(7,+\\infty)$"
  },
  "image_sources": [],
  "metadata": {
    "row_index": 5,
    "question_field": "question",
    "answer_field": "answer",
    "image_field": null,
    "choice_field": "options"
  },
  "raw_record": {
    "id": "19894",
    "image": "[]",
    "answer": "B",
    "solution": "null",
    "level": "高二",
    "question": "已知点 $(-3,-1)$ 和点 $(4,-6)$ 在直线 $3 x-2 y-a=0$ 的两侧, 则 $a$ 的取值范围为 ( )",
    "options": "A. $(-24,7)$\nB. $(-7,24)$\nC. $(-\\infty,-7) \\cup(24, \\infty)$\nD. $(-\\infty,-24) \\cup(7,+\\infty)$",
    "subject": "解析几何",
    "analysis": "因为点 $(-3,-1)$ 和 $(4,-6)$ 在直线 $3 x-2 y-a=0$ 的两侧, 所以 $[3 \\times(-3)-2 \\times(-1)-a] \\times[3 \\times 4-2 \\times(-6)-a]<0$, 所以 $-7<a<24$. 故选 B."
  }
}
```

### 1.2 原始图片

- （无）

## 2. 处理前后对照

### 2.1 关键字段对照

| 字段 | 处理前 | 处理后 |
| --- | --- | --- |
| question_text | 已知点 $(-3,-1)$ 和点 $(4,-6)$ 在直线 $3 x-2 y-a=0$ 的两侧, 则 $a$ 的取值范围为 ( ) | 已知点 $(-3,-1)$ 和点 $(4,-6)$ 在直线 $3 x-2 y-a=0$ 的两侧, 则 $a$ 的取值范围为 ( ) |
| answer_text | B | B |
| answer_type | - | option |
| image_count | 0 | 0 |
| text_dominant | - | True |
| cleaning_path | - | text_lightweight |
| clean_decision | - | review |
| alignment_status | - | good |
| solvability_decision_hint | - | pass |
| rewrite_strategy | - | split_open |

### 2.2 结构化处理后结果

#### problem_main_record

```json
{
  "problem_id": "prob_a7f1f8d9176c160f1c3b4cbc",
  "source_dataset": "CMM-Math",
  "source_split": "train",
  "source_problem_id": "19894",
  "ingest_batch_id": "multidataset-clean_20260324T074830Z",
  "problem_type": "multimodal_reasoning",
  "domain_tags": [
    "数学"
  ],
  "language": "zh",
  "raw_question_text": "已知点 $(-3,-1)$ 和点 $(4,-6)$ 在直线 $3 x-2 y-a=0$ 的两侧, 则 $a$ 的取值范围为 ( )",
  "normalized_question_text": "已知点 $(-3,-1)$ 和点 $(4,-6)$ 在直线 $3 x-2 y-a=0$ 的两侧, 则 $a$ 的取值范围为 ( )",
  "raw_answer_text": "B",
  "normalized_answer_text": "B",
  "answer_type": "option",
  "image_count": 0,
  "has_multiple_images": false,
  "requires_image": false,
  "multimodal_strength_score": 0.33,
  "multi_step_score": 0.4097,
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
  "candidate_id": "cand_a7f1f8d9176c160f1c3b4cbc",
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
  "clean_problem_record_id": "cleanprob_2965b7389d7a049750c99354",
  "problem_id": "prob_a7f1f8d9176c160f1c3b4cbc",
  "source_dataset": "CMM-Math",
  "source_problem_id": "19894",
  "normalized_question_text": "已知点 $(-3,-1)$ 和点 $(4,-6)$ 在直线 $3 x-2 y-a=0$ 的两侧, 则 $a$ 的取值范围为 ( )",
  "normalized_answer_text": "B",
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
  "created_at": "2026-03-24T07:48:35Z"
}
```

#### normalized_assets

```json
{
  "normalized_assets_id": "nassets_2965b7389d7a049750c99354",
  "problem_id": "prob_a7f1f8d9176c160f1c3b4cbc",
  "normalized_question_text": "已知点 $(-3,-1)$ 和点 $(4,-6)$ 在直线 $3 x-2 y-a=0$ 的两侧, 则 $a$ 的取值范围为 ( )",
  "normalized_answer_text": "B",
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
      "original": "a",
      "canonical": "a",
      "variable_type": "symbol"
    }
  ],
  "sentence_segments": [
    {
      "segment_index": 1,
      "text": "已知点 $(-3,-1)$ 和点 $(4,-6)$ 在直线 $3 x-2 y-a=0$ 的两侧, 则 $a$ 的取值范围为 ( )"
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
  "text_structure_id": "text_prob_a7f1f8d9176c160f1c3b4cbc",
  "problem_id": "prob_a7f1f8d9176c160f1c3b4cbc",
  "question_type": "multiple_choice",
  "conditions": [
    {
      "text": "已知点 $(-3,-1)$ 和点 $(4,-6)$ 在直线 $3 x-2 y-a=0$ 的两侧, 则 $a$ 的取值范围为 ( )",
      "segment_index": 1,
      "mentions_visual": false,
      "numeric_tokens": [
        "-3",
        "-1",
        "4",
        "-6",
        "3",
        "-2",
        "0"
      ],
      "unit_mentions": [],
      "condition_role": "explicit"
    }
  ],
  "targets": [
    {
      "text": "已知点 $(-3,-1)$ 和点 $(4,-6)$ 在直线 $3 x-2 y-a=0$ 的两侧, 则 $a$ 的取值范围为 ( )",
      "segment_index": 1,
      "mentions_visual": false,
      "numeric_tokens": [
        "-3",
        "-1",
        "4",
        "-6",
        "3",
        "-2",
        "0"
      ],
      "unit_mentions": [],
      "target_role": "fallback"
    }
  ],
  "answer_slots": [
    {
      "slot_id": "slot_prob_a7f1f8d9176c160f1c3b4cbc_1",
      "variant_index": 1,
      "split_role": "part_1",
      "slot_type": "short_text",
      "target_text": "请只回答第 1 个目标量。",
      "expected_answer_type": "short_text",
      "expected_answer": "$(-7,24)$",
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
      "original": "a",
      "canonical": "a",
      "variable_type": "symbol"
    }
  ],
  "unit_mentions": [],
  "sentence_segments": [
    {
      "segment_index": 1,
      "text": "已知点 $(-3,-1)$ 和点 $(4,-6)$ 在直线 $3 x-2 y-a=0$ 的两侧, 则 $a$ 的取值范围为 ( )"
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
  "alignment_id": "align_2965b7389d7a049750c99354",
  "problem_id": "prob_a7f1f8d9176c160f1c3b4cbc",
  "image_entity_refs": [],
  "text_span_refs": [
    "asset_prob_a7f1f8d9176c160f1c3b4cbc_question_text_normalized"
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
  "solvability_id": "solv_prob_a7f1f8d9176c160f1c3b4cbc",
  "problem_id": "prob_a7f1f8d9176c160f1c3b4cbc",
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
  "cleaning_id": "clean_2965b7389d7a049750c99354",
  "problem_id": "prob_a7f1f8d9176c160f1c3b4cbc",
  "cleaning_version": "v3.0.0",
  "pipeline_run_id": "run_637ca3432da6ddfb",
  "dataset_name": "CMM-Math",
  "input_asset_ids": [
    "asset_7dd8039e14430cef9044e852",
    "asset_ed9b1e76daee9c63cf77782d",
    "asset_150e5bcd82f83d0d39c9833b",
    "asset_1af7b0307ea25bf84304007e",
    "asset_b2b4d2da4171c27765c25420"
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
      "variable_alias_count": 3
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
    "alignment_id": "align_2965b7389d7a049750c99354",
    "coverage_score": 1.0,
    "consistency_score": 1.0,
    "alignment_status": "good",
    "conflict_count": 0
  },
  "text_structure_summary": {
    "text_structure_id": "text_prob_a7f1f8d9176c160f1c3b4cbc",
    "question_type": "multiple_choice",
    "condition_count": 1,
    "target_count": 1,
    "answer_slot_count": 1,
    "status": "complete"
  },
  "solvability_summary": {
    "solvability_id": "solv_prob_a7f1f8d9176c160f1c3b4cbc",
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
  "clean_score": 0.8401,
  "decision": "review",
  "decision_reason_codes": [
    "split_variant_needs_review"
  ],
  "review_ticket_id": "review_prob_a7f1f8d9176c160f1c3b4cbc",
  "operator_type": "system",
  "started_at": "2026-03-24T07:48:35Z",
  "finished_at": "2026-03-24T07:48:35Z",
  "candidate_id": "cand_a7f1f8d9176c160f1c3b4cbc",
  "cleaning_path": "text_lightweight",
  "text_dominant": true
}
```

## 3. 开放化改写前后

### 3.1 改写前

```json
{
  "question_text_before_rewrite": "已知点 $(-3,-1)$ 和点 $(4,-6)$ 在直线 $3 x-2 y-a=0$ 的两侧, 则 $a$ 的取值范围为 ( )",
  "answer_text_before_rewrite": "B",
  "raw_question_text": "已知点 $(-3,-1)$ 和点 $(4,-6)$ 在直线 $3 x-2 y-a=0$ 的两侧, 则 $a$ 的取值范围为 ( )",
  "raw_answer_text": "B"
}
```

### 3.2 改写后

```json
{
  "rewrite_report": {
    "rewrite_id": "rewrite_2965b7389d7a049750c99354",
    "problem_id": "prob_a7f1f8d9176c160f1c3b4cbc",
    "source_problem_id": "19894",
    "strategy": "split_open",
    "rationale": "Compound choice answer was split into multiple open-ended targets.",
    "discard_reason_codes": [],
    "variant_count": 1,
    "variants": [
      {
        "open_variant_id": "open_9d138880ce4d9b7809098da8",
        "parent_problem_id": "prob_a7f1f8d9176c160f1c3b4cbc",
        "variant_index": 1,
        "title": "CMM-Math 子题 1",
        "rewritten_question_text": "已知点 $(-3,-1)$ 和点 $(4,-6)$ 在直线 $3 x-2 y-a=0$ 的两侧, 则 $a$ 的取值范围为 ( )\n请只回答第 1 个目标量。",
        "expected_answer_type": "short_text",
        "expected_answer": "$(-7,24)$",
        "split_role": "part_1"
      }
    ],
    "created_at": "2026-03-24T07:48:35Z"
  },
  "open_ended_problem_variants": [
    {
      "open_variant_id": "open_9d138880ce4d9b7809098da8",
      "parent_problem_id": "prob_a7f1f8d9176c160f1c3b4cbc",
      "variant_index": 1,
      "title": "CMM-Math 子题 1",
      "rewritten_question_text": "已知点 $(-3,-1)$ 和点 $(4,-6)$ 在直线 $3 x-2 y-a=0$ 的两侧, 则 $a$ 的取值范围为 ( )\n请只回答第 1 个目标量。",
      "expected_answer_type": "short_text",
      "expected_answer": "$(-7,24)$",
      "split_role": "part_1"
    }
  ]
}
```

## 4. 完整 collection + cleaning 输出对象

#### candidate_problem_record

```json
{
  "candidate_id": "cand_a7f1f8d9176c160f1c3b4cbc",
  "source_dataset": "CMM-Math",
  "source_split": "train",
  "source_problem_id": "19894",
  "subject": "数学",
  "raw_question_text": "已知点 $(-3,-1)$ 和点 $(4,-6)$ 在直线 $3 x-2 y-a=0$ 的两侧, 则 $a$ 的取值范围为 ( )",
  "raw_answer_text": "B",
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
    "row_index": 5,
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
  "raw_asset_bundle_id": "bundle_c2be09e1e6c9606415ceb525",
  "candidate_id": "cand_a7f1f8d9176c160f1c3b4cbc",
  "source_dataset": "CMM-Math",
  "source_problem_id": "19894",
  "assets": [
    {
      "asset_role": "question_text_raw",
      "storage_uri": "inline://prob_a7f1f8d9176c160f1c3b4cbc/question_source",
      "is_present": true
    },
    {
      "asset_role": "answer_text_raw",
      "storage_uri": "inline://prob_a7f1f8d9176c160f1c3b4cbc/answer_source",
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
  "candidate_pool_entry_id": "cpool_58fcb13d8312ae565b6c51a3",
  "candidate_id": "cand_a7f1f8d9176c160f1c3b4cbc",
  "source_dataset": "CMM-Math",
  "source_problem_id": "19894",
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
    "clean_pool_entry_id": "cleanpool_2965b7389d7a049750c99354",
    "candidate_id": "cand_a7f1f8d9176c160f1c3b4cbc",
    "problem_id": "prob_a7f1f8d9176c160f1c3b4cbc",
    "dataset_name": "CMM-Math",
    "pool_status": "manual_review",
    "clean_decision": "review",
    "review_required": true,
    "rewrite_strategy": "split_open",
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
    "rewrite_id": "rewrite_2965b7389d7a049750c99354",
    "problem_id": "prob_a7f1f8d9176c160f1c3b4cbc",
    "source_problem_id": "19894",
    "strategy": "split_open",
    "rationale": "Compound choice answer was split into multiple open-ended targets.",
    "discard_reason_codes": [],
    "variant_count": 1,
    "variants": [
      {
        "open_variant_id": "open_9d138880ce4d9b7809098da8",
        "parent_problem_id": "prob_a7f1f8d9176c160f1c3b4cbc",
        "variant_index": 1,
        "title": "CMM-Math 子题 1",
        "rewritten_question_text": "已知点 $(-3,-1)$ 和点 $(4,-6)$ 在直线 $3 x-2 y-a=0$ 的两侧, 则 $a$ 的取值范围为 ( )\n请只回答第 1 个目标量。",
        "expected_answer_type": "short_text",
        "expected_answer": "$(-7,24)$",
        "split_role": "part_1"
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
    "open_variant_id": "open_9d138880ce4d9b7809098da8",
    "parent_problem_id": "prob_a7f1f8d9176c160f1c3b4cbc",
    "variant_index": 1,
    "title": "CMM-Math 子题 1",
    "rewritten_question_text": "已知点 $(-3,-1)$ 和点 $(4,-6)$ 在直线 $3 x-2 y-a=0$ 的两侧, 则 $a$ 的取值范围为 ( )\n请只回答第 1 个目标量。",
    "expected_answer_type": "short_text",
    "expected_answer": "$(-7,24)$",
    "split_role": "part_1"
  }
]
```

#### asset_records

```json
[
  {
    "asset_id": "asset_7dd8039e14430cef9044e852",
    "problem_id": "prob_a7f1f8d9176c160f1c3b4cbc",
    "asset_type": "text",
    "asset_role": "question_text_source",
    "source_uri": "source://cmm_math/train/19894/question",
    "storage_uri": "inline://prob_a7f1f8d9176c160f1c3b4cbc/question_source",
    "file_format": "txt",
    "file_size_bytes": 101,
    "width": null,
    "height": null,
    "sha256": "72a05fa01e0da2fb5a4b00743d0055e6ba0190b9dd9a61bf12afa0957aebd26a",
    "perceptual_hash": null,
    "source_text_snapshot": "已知点 $(-3,-1)$ 和点 $(4,-6)$ 在直线 $3 x-2 y-a=0$ 的两侧, 则 $a$ 的取值范围为 ( )",
    "normalized_text_snapshot": null,
    "text_completeness_score": 0.608,
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
        "original": "a",
        "canonical": "a",
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
    "asset_id": "asset_ed9b1e76daee9c63cf77782d",
    "problem_id": "prob_a7f1f8d9176c160f1c3b4cbc",
    "asset_type": "text",
    "asset_role": "question_text_normalized",
    "source_uri": null,
    "storage_uri": "inline://prob_a7f1f8d9176c160f1c3b4cbc/question_normalized",
    "file_format": "txt",
    "file_size_bytes": 101,
    "width": null,
    "height": null,
    "sha256": "72a05fa01e0da2fb5a4b00743d0055e6ba0190b9dd9a61bf12afa0957aebd26a",
    "perceptual_hash": null,
    "source_text_snapshot": "已知点 $(-3,-1)$ 和点 $(4,-6)$ 在直线 $3 x-2 y-a=0$ 的两侧, 则 $a$ 的取值范围为 ( )",
    "normalized_text_snapshot": "已知点 $(-3,-1)$ 和点 $(4,-6)$ 在直线 $3 x-2 y-a=0$ 的两侧, 则 $a$ 的取值范围为 ( )",
    "text_completeness_score": 0.608,
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
        "original": "a",
        "canonical": "a",
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
    "asset_id": "asset_150e5bcd82f83d0d39c9833b",
    "problem_id": "prob_a7f1f8d9176c160f1c3b4cbc",
    "asset_type": "answer",
    "asset_role": "answer_raw",
    "source_uri": "source://cmm_math/train/19894/answer",
    "storage_uri": "inline://prob_a7f1f8d9176c160f1c3b4cbc/answer_raw",
    "file_format": "txt",
    "file_size_bytes": 1,
    "width": null,
    "height": null,
    "sha256": "df7e70e5021544f4834bbee64a9e3789febc4be81470df629cad6ddb03320a5c",
    "perceptual_hash": null,
    "source_text_snapshot": "B",
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
        "original": "B",
        "canonical": "B",
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
    "asset_id": "asset_1af7b0307ea25bf84304007e",
    "problem_id": "prob_a7f1f8d9176c160f1c3b4cbc",
    "asset_type": "answer",
    "asset_role": "answer_normalized",
    "source_uri": null,
    "storage_uri": "inline://prob_a7f1f8d9176c160f1c3b4cbc/answer_normalized",
    "file_format": "txt",
    "file_size_bytes": 1,
    "width": null,
    "height": null,
    "sha256": "df7e70e5021544f4834bbee64a9e3789febc4be81470df629cad6ddb03320a5c",
    "perceptual_hash": null,
    "source_text_snapshot": "B",
    "normalized_text_snapshot": "B",
    "text_completeness_score": 1.0,
    "blur_score": null,
    "readability_score": null,
    "noise_score": null,
    "cropped_from_asset_id": null,
    "roi_bbox": null,
    "unit_normalization_map": [],
    "variable_aliases": [
      {
        "original": "B",
        "canonical": "B",
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
    "asset_id": "asset_b2b4d2da4171c27765c25420",
    "problem_id": "prob_a7f1f8d9176c160f1c3b4cbc",
    "asset_type": "text",
    "asset_role": "question_text_open_variant",
    "source_uri": null,
    "storage_uri": "inline://open_9d138880ce4d9b7809098da8",
    "file_format": "txt",
    "file_size_bytes": 135,
    "width": null,
    "height": null,
    "sha256": "ca2d37abc49178494fa8f7b44eb73e74404ad4ad2d8eacd84347f104c686a069",
    "perceptual_hash": null,
    "source_text_snapshot": "已知点 $(-3,-1)$ 和点 $(4,-6)$ 在直线 $3 x-2 y-a=0$ 的两侧, 则 $a$ 的取值范围为 ( )",
    "normalized_text_snapshot": "已知点 $(-3,-1)$ 和点 $(4,-6)$ 在直线 $3 x-2 y-a=0$ 的两侧, 则 $a$ 的取值范围为 ( )\n请只回答第 1 个目标量。",
    "text_completeness_score": 0.608,
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
        "original": "a",
        "canonical": "a",
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
    "node_id": "node_b79b02088d977550c5ad21e0",
    "problem_id": "prob_a7f1f8d9176c160f1c3b4cbc",
    "node_type": "text_fact",
    "canonical_value": "已知点 $(-3,-1)$ 和点 $(4,-6)$ 在直线 $3 x-2 y-a=0$ 的两侧, 则 $a$ 的取值范围为 ( )",
    "surface_forms": [
      "已知点 $(-3,-1)$ 和点 $(4,-6)$ 在直线 $3 x-2 y-a=0$ 的两侧, 则 $a$ 的取值范围为 ( )"
    ],
    "origin_kind": "text",
    "cognitive_level": "objective",
    "source_refs": [
      "asset_ed9b1e76daee9c63cf77782d"
    ],
    "evidence_refs": [
      "asset_ed9b1e76daee9c63cf77782d"
    ],
    "upstream_node_ids": [],
    "value_type": "condition",
    "normalized_value": {
      "text": "已知点 $(-3,-1)$ 和点 $(4,-6)$ 在直线 $3 x-2 y-a=0$ 的两侧, 则 $a$ 的取值范围为 ( )",
      "segment_index": 1,
      "mentions_visual": false,
      "numeric_tokens": [
        "-3",
        "-1",
        "4",
        "-6",
        "3",
        "-2",
        "0"
      ],
      "unit_mentions": [],
      "condition_role": "explicit"
    },
    "unit": null,
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
    "node_id": "node_47371ed465ffaaa0dc7e6c70",
    "problem_id": "prob_a7f1f8d9176c160f1c3b4cbc",
    "node_type": "target_slot",
    "canonical_value": "请只回答第 1 个目标量。",
    "surface_forms": [
      "请只回答第 1 个目标量。"
    ],
    "origin_kind": "text_structure",
    "cognitive_level": "computed",
    "source_refs": [
      "asset_ed9b1e76daee9c63cf77782d"
    ],
    "evidence_refs": [
      "asset_ed9b1e76daee9c63cf77782d"
    ],
    "upstream_node_ids": [],
    "value_type": "short_text",
    "normalized_value": {
      "slot_id": "slot_prob_a7f1f8d9176c160f1c3b4cbc_1",
      "variant_index": 1,
      "split_role": "part_1",
      "slot_type": "short_text",
      "target_text": "请只回答第 1 个目标量。",
      "expected_answer_type": "short_text",
      "expected_answer": "$(-7,24)$",
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
    "node_id": "node_e4d74106306f35fd31cf22d5",
    "problem_id": "prob_a7f1f8d9176c160f1c3b4cbc",
    "node_type": "answer_claim",
    "canonical_value": "B",
    "surface_forms": [
      "B"
    ],
    "origin_kind": "text",
    "cognitive_level": "objective",
    "source_refs": [
      "asset_1af7b0307ea25bf84304007e"
    ],
    "evidence_refs": [
      "asset_1af7b0307ea25bf84304007e"
    ],
    "upstream_node_ids": [],
    "value_type": "option",
    "normalized_value": {
      "answer": "B"
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
    "node_id": "node_df208ee7db64562c4b91a1b9",
    "problem_id": "prob_a7f1f8d9176c160f1c3b4cbc",
    "node_type": "text_fact",
    "canonical_value": "已知点 $(-3,-1)$ 和点 $(4,-6)$ 在直线 $3 x-2 y-a=0$ 的两侧, 则 $a$ 的取值范围为 ( )\n请只回答第 1 个目标量。",
    "surface_forms": [
      "已知点 $(-3,-1)$ 和点 $(4,-6)$ 在直线 $3 x-2 y-a=0$ 的两侧, 则 $a$ 的取值范围为 ( )\n请只回答第 1 个目标量。"
    ],
    "origin_kind": "reasoning",
    "cognitive_level": "computed",
    "source_refs": [
      "asset_b2b4d2da4171c27765c25420"
    ],
    "evidence_refs": [
      "asset_b2b4d2da4171c27765c25420"
    ],
    "upstream_node_ids": [],
    "value_type": "text",
    "normalized_value": {
      "open_variant_id": "open_9d138880ce4d9b7809098da8",
      "parent_problem_id": "prob_a7f1f8d9176c160f1c3b4cbc",
      "variant_index": 1,
      "title": "CMM-Math 子题 1",
      "rewritten_question_text": "已知点 $(-3,-1)$ 和点 $(4,-6)$ 在直线 $3 x-2 y-a=0$ 的两侧, 则 $a$ 的取值范围为 ( )\n请只回答第 1 个目标量。",
      "expected_answer_type": "short_text",
      "expected_answer": "$(-7,24)$",
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
    "created_at": "2026-03-24T07:48:35Z",
    "updated_at": "2026-03-24T07:48:35Z"
  },
  {
    "node_id": "node_cb2d22826cd24561c3f2fe5c",
    "problem_id": "prob_a7f1f8d9176c160f1c3b4cbc",
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
      "solvability_id": "solv_prob_a7f1f8d9176c160f1c3b4cbc",
      "problem_id": "prob_a7f1f8d9176c160f1c3b4cbc",
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
    "node_id": "node_e5147d52610e857a0e01e5a9",
    "problem_id": "prob_a7f1f8d9176c160f1c3b4cbc",
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
    "created_at": "2026-03-24T07:48:35Z",
    "updated_at": "2026-03-24T07:48:35Z"
  }
]
```

#### field_audit_records

```json
[
  {
    "audit_id": "audit_51f980c274574de1ccfa6234",
    "problem_id": "prob_a7f1f8d9176c160f1c3b4cbc",
    "record_type": "problem_main_record",
    "field_name": "normalized_question_text",
    "before_value": "已知点 $(-3,-1)$ 和点 $(4,-6)$ 在直线 $3 x-2 y-a=0$ 的两侧, 则 $a$ 的取值范围为 ( )",
    "after_value": "已知点 $(-3,-1)$ 和点 $(4,-6)$ 在直线 $3 x-2 y-a=0$ 的两侧, 则 $a$ 的取值范围为 ( )",
    "change_type": "text_normalized",
    "trigger": "NormalizationAgent",
    "operator_type": "system",
    "created_at": "2026-03-24T07:48:35Z"
  },
  {
    "audit_id": "audit_f24713970ecdbe6990b2aecd",
    "problem_id": "prob_a7f1f8d9176c160f1c3b4cbc",
    "record_type": "problem_main_record",
    "field_name": "normalized_answer_text",
    "before_value": "B",
    "after_value": "B",
    "change_type": "answer_canonicalized",
    "trigger": "NormalizationAgent",
    "operator_type": "system",
    "created_at": "2026-03-24T07:48:35Z"
  },
  {
    "audit_id": "audit_37132af0be61d57a14285779",
    "problem_id": "prob_a7f1f8d9176c160f1c3b4cbc",
    "record_type": "rewrite_report",
    "field_name": "rewrite_strategy",
    "before_value": null,
    "after_value": "split_open",
    "change_type": "question_rewritten",
    "trigger": "QuestionRewriteAgent",
    "operator_type": "system",
    "created_at": "2026-03-24T07:48:35Z"
  },
  {
    "audit_id": "audit_e5147d52610e857a0e01e5a9",
    "problem_id": "prob_a7f1f8d9176c160f1c3b4cbc",
    "record_type": "cleaning_record",
    "field_name": "decision",
    "before_value": null,
    "after_value": "review",
    "change_type": "gate_decision",
    "trigger": "CleanGateAgent",
    "operator_type": "system",
    "created_at": "2026-03-24T07:48:35Z"
  },
  {
    "audit_id": "audit_1fe4adda8b9d557485e7a0c2",
    "problem_id": "prob_a7f1f8d9176c160f1c3b4cbc",
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
        "original": "a",
        "canonical": "a",
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

- `outputs/user_requested_batch_review/pipeline_runs/run_637ca3432da6ddfb/datasets/cmm_math/samples/prob_a7f1f8d9176c160f1c3b4cbc.json`
