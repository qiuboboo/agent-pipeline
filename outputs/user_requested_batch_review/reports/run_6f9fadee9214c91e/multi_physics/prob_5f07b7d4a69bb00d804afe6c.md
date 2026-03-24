# muti- physics / prob_5f07b7d4a69bb00d804afe6c

- source_problem_id: `9`
- source_split: `repo_discovered`
- clean_decision: `pass`
- rewrite_strategy: `keep_open`
- full sample bundle JSON: `outputs/user_requested_batch_review/pipeline_runs/run_6f9fadee9214c91e/datasets/multi_physics/samples/prob_5f07b7d4a69bb00d804afe6c.json`

## 1. 原始内容（处理前）

### 1.1 原始快照

```json
{
  "dataset_key": "multi_physics",
  "source_problem_id": "9",
  "source_split": "repo_discovered",
  "raw_question_text": "如图所示为一个质点运动的位移x随时间t变化的图象，由此可知质点在0～4s内\nA. 先沿x轴正方向运动，后沿x轴负方向运动\nB. 一直做匀变速运动\nC. t=2s时速度一定最大\nD. 速率为5m/s的时刻有两个",
  "raw_answer_text": "CD",
  "choice_map": {},
  "image_sources": [],
  "metadata": {
    "data_file": "outputs/repo_cache/multi_physics/Data/1.json",
    "question_field": "question",
    "answer_field": "answer",
    "image_field": null,
    "choice_field": null
  },
  "raw_record": {
    "category": "multi",
    "question": "如图所示为一个质点运动的位移x随时间t变化的图象，由此可知质点在0～4s内\nA. 先沿x轴正方向运动，后沿x轴负方向运动\nB. 一直做匀变速运动\nC. t=2s时速度一定最大\nD. 速率为5m/s的时刻有两个",
    "picture": [
      "../Data/1/9_0.png"
    ],
    "answer": [
      "CD"
    ],
    "analysis": "从图中可知正向位移减小，故质点一直朝着负方向运动，A错误；图像的斜率表示速度大小，故斜率先增大后减小，说明物体速率先增大后减小，做变速运动，但不能判断是不是做匀变速直线运动，t=2s时，斜率最大，速度最大，B错误C正确；因为斜率先增大后减小，并且平均速度为5m/s，故增大过程中有一刻速度为5m/s，减小过程中有一刻速度为5m/s，共有两个时刻速度大小为5m/s，D正确",
    "index": 9,
    "level": 1
  }
}
```

## 2. 处理前后对照

### 2.1 关键字段对照

| 字段 | 处理前 | 处理后 |
| --- | --- | --- |
| question_text | 如图所示为一个质点运动的位移x随时间t变化的图象，由此可知质点在0～4s内 A. 先沿x轴正方向运动，后沿x轴负方向运动 B. 一直做匀变速运动 C. t=2s时速度一定最大 D. 速率为5m/s的时刻有两个 | 如图所示为一个质点运动的位移x随时间t变化的图象,由此可知质点在0~4s内 A. 先沿x轴正方向运动,后沿x轴负方向运动 B. 一直做匀变速运动 C. t=2s时速度一定最大 D. 速率为5m/s的时刻有两个 |
| answer_text | CD | CD |
| answer_type | - | short_text |
| image_count | 0 | 0 |
| text_dominant | - | True |
| cleaning_path | - | text_lightweight |
| clean_decision | - | pass |
| alignment_status | - | good |
| solvability_decision_hint | - | pass |

### 2.2 结构化处理后结果

#### problem_main_record

```json
{
  "problem_id": "prob_5f07b7d4a69bb00d804afe6c",
  "source_dataset": "muti- physics",
  "source_split": "repo_discovered",
  "source_problem_id": "9",
  "ingest_batch_id": "multidataset-clean_20260324T063656Z",
  "problem_type": "multimodal_reasoning",
  "domain_tags": [
    "物理"
  ],
  "language": "zh",
  "raw_question_text": "如图所示为一个质点运动的位移x随时间t变化的图象，由此可知质点在0～4s内\nA. 先沿x轴正方向运动，后沿x轴负方向运动\nB. 一直做匀变速运动\nC. t=2s时速度一定最大\nD. 速率为5m/s的时刻有两个",
  "normalized_question_text": "如图所示为一个质点运动的位移x随时间t变化的图象,由此可知质点在0~4s内\nA. 先沿x轴正方向运动,后沿x轴负方向运动\nB. 一直做匀变速运动\nC. t=2s时速度一定最大\nD. 速率为5m/s的时刻有两个",
  "raw_answer_text": "CD",
  "normalized_answer_text": "CD",
  "answer_type": "short_text",
  "image_count": 0,
  "has_multiple_images": false,
  "requires_image": false,
  "multimodal_strength_score": 0.48,
  "multi_step_score": 0.4097,
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
  "rewrite_strategy": "keep_open",
  "open_variant_count": 1,
  "candidate_id": "cand_5f07b7d4a69bb00d804afe6c",
  "text_dominant": true,
  "cleaning_path": "text_lightweight",
  "alignment_status": "good",
  "solvability_score": 1.0,
  "solvability_decision_hint": "pass",
  "created_at": "2026-03-24T06:37:08Z",
  "updated_at": "2026-03-24T06:37:08Z",
  "initial_image_dependency_score": 0.2,
  "initial_multi_solution_score": 0.18,
  "initial_verifiability_score": 0.78,
  "multi_solution_mining_policy": "conservative"
}
```

#### clean_problem_record

```json
{
  "clean_problem_record_id": "cleanprob_48328372045b3e280a87402e",
  "problem_id": "prob_5f07b7d4a69bb00d804afe6c",
  "source_dataset": "muti- physics",
  "source_problem_id": "9",
  "normalized_question_text": "如图所示为一个质点运动的位移x随时间t变化的图象,由此可知质点在0~4s内\nA. 先沿x轴正方向运动,后沿x轴负方向运动\nB. 一直做匀变速运动\nC. t=2s时速度一定最大\nD. 速率为5m/s的时刻有两个",
  "normalized_answer_text": "CD",
  "image_count": 0,
  "has_multiple_images": false,
  "requires_image": false,
  "text_dominant": true,
  "cleaning_path": "text_lightweight",
  "question_type": "open",
  "open_variant_count": 1,
  "alignment_status": "good",
  "solvability_score": 1.0,
  "solvability_path_mode": "text_only",
  "clean_decision": "pass",
  "decision_reason_codes": [
    "meets_cleaning_requirements"
  ],
  "created_at": "2026-03-24T06:37:08Z"
}
```

#### normalized_assets

```json
{
  "normalized_assets_id": "nassets_48328372045b3e280a87402e",
  "problem_id": "prob_5f07b7d4a69bb00d804afe6c",
  "normalized_question_text": "如图所示为一个质点运动的位移x随时间t变化的图象,由此可知质点在0~4s内\nA. 先沿x轴正方向运动,后沿x轴负方向运动\nB. 一直做匀变速运动\nC. t=2s时速度一定最大\nD. 速率为5m/s的时刻有两个",
  "normalized_answer_text": "CD",
  "question_unit_normalization_map": [],
  "answer_unit_normalization_map": [],
  "variable_aliases": [
    {
      "original": "A",
      "canonical": "A",
      "variable_type": "symbol"
    },
    {
      "original": "B",
      "canonical": "B",
      "variable_type": "symbol"
    },
    {
      "original": "C",
      "canonical": "C",
      "variable_type": "symbol"
    },
    {
      "original": "t",
      "canonical": "t",
      "variable_type": "symbol"
    },
    {
      "original": "D",
      "canonical": "D",
      "variable_type": "symbol"
    }
  ],
  "sentence_segments": [
    {
      "segment_index": 1,
      "text": "如图所示为一个质点运动的位移x随时间t变化的图象,由此可知质点在0~4s内"
    },
    {
      "segment_index": 2,
      "text": "A."
    },
    {
      "segment_index": 3,
      "text": "先沿x轴正方向运动,后沿x轴负方向运动"
    },
    {
      "segment_index": 4,
      "text": "B."
    },
    {
      "segment_index": 5,
      "text": "一直做匀变速运动"
    },
    {
      "segment_index": 6,
      "text": "C."
    },
    {
      "segment_index": 7,
      "text": "t=2s时速度一定最大"
    },
    {
      "segment_index": 8,
      "text": "D."
    },
    {
      "segment_index": 9,
      "text": "速率为5m/s的时刻有两个"
    }
  ],
  "image_regions": [],
  "text_dominant": true,
  "cleaning_path": "text_lightweight",
  "created_at": "2026-03-24T06:37:08Z"
}
```

#### text_structure_record

```json
{
  "text_structure_id": "text_prob_5f07b7d4a69bb00d804afe6c",
  "problem_id": "prob_5f07b7d4a69bb00d804afe6c",
  "question_type": "open",
  "conditions": [
    {
      "text": "如图所示为一个质点运动的位移x随时间t变化的图象,由此可知质点在0~4s内",
      "segment_index": 1,
      "mentions_visual": false,
      "numeric_tokens": [
        "0",
        "4"
      ],
      "unit_mentions": [
        "s"
      ],
      "condition_role": "explicit"
    },
    {
      "text": "t=2s时速度一定最大",
      "segment_index": 7,
      "mentions_visual": false,
      "numeric_tokens": [
        "2"
      ],
      "unit_mentions": [
        "s"
      ],
      "condition_role": "explicit"
    },
    {
      "text": "速率为5m/s的时刻有两个",
      "segment_index": 9,
      "mentions_visual": false,
      "numeric_tokens": [
        "5"
      ],
      "unit_mentions": [
        "m",
        "s"
      ],
      "condition_role": "explicit"
    }
  ],
  "targets": [
    {
      "text": "如图所示为一个质点运动的位移x随时间t变化的图象,由此可知质点在0~4s内\nA. 先沿x轴正方向运动,后沿x轴负方向运动\nB. 一直做匀变速运动\nC. t=2s时速度一定最大\nD. 速率为5m/s的时刻有两个",
      "segment_index": 9,
      "mentions_visual": false,
      "numeric_tokens": [
        "0",
        "4",
        "2",
        "5"
      ],
      "unit_mentions": [
        "A",
        "m",
        "s"
      ],
      "target_role": "fallback"
    }
  ],
  "answer_slots": [
    {
      "slot_id": "slot_prob_5f07b7d4a69bb00d804afe6c_1",
      "variant_index": 1,
      "split_role": "single",
      "slot_type": "short_text",
      "target_text": "速率为5m/s的时刻有两个",
      "expected_answer_type": "short_text",
      "expected_answer": "CD",
      "requires_visual_grounding": false
    }
  ],
  "entity_mentions": [
    {
      "mention": "A",
      "entity_category": "label",
      "requires_visual_grounding": true
    },
    {
      "mention": "B",
      "entity_category": "label",
      "requires_visual_grounding": true
    },
    {
      "mention": "C",
      "entity_category": "label",
      "requires_visual_grounding": true
    },
    {
      "mention": "D",
      "entity_category": "label",
      "requires_visual_grounding": true
    }
  ],
  "variable_aliases": [
    {
      "original": "A",
      "canonical": "A",
      "variable_type": "symbol"
    },
    {
      "original": "B",
      "canonical": "B",
      "variable_type": "symbol"
    },
    {
      "original": "C",
      "canonical": "C",
      "variable_type": "symbol"
    },
    {
      "original": "t",
      "canonical": "t",
      "variable_type": "symbol"
    },
    {
      "original": "D",
      "canonical": "D",
      "variable_type": "symbol"
    }
  ],
  "unit_mentions": [
    "A",
    "m",
    "s"
  ],
  "sentence_segments": [
    {
      "segment_index": 1,
      "text": "如图所示为一个质点运动的位移x随时间t变化的图象,由此可知质点在0~4s内"
    },
    {
      "segment_index": 2,
      "text": "A."
    },
    {
      "segment_index": 3,
      "text": "先沿x轴正方向运动,后沿x轴负方向运动"
    },
    {
      "segment_index": 4,
      "text": "B."
    },
    {
      "segment_index": 5,
      "text": "一直做匀变速运动"
    },
    {
      "segment_index": 6,
      "text": "C."
    },
    {
      "segment_index": 7,
      "text": "t=2s时速度一定最大"
    },
    {
      "segment_index": 8,
      "text": "D."
    },
    {
      "segment_index": 9,
      "text": "速率为5m/s的时刻有两个"
    }
  ],
  "requires_visual_grounding": true,
  "text_structure_status": "complete",
  "parser_confidence": 0.92,
  "created_at": "2026-03-24T06:37:08Z"
}
```

#### visual_structure_records

```json
[]
```

#### alignment_record

```json
{
  "alignment_id": "align_48328372045b3e280a87402e",
  "problem_id": "prob_5f07b7d4a69bb00d804afe6c",
  "image_entity_refs": [],
  "text_span_refs": [
    "asset_prob_5f07b7d4a69bb00d804afe6c_question_text_normalized"
  ],
  "alignment_pairs": [],
  "conflict_pairs": [],
  "coverage_score": 1.0,
  "consistency_score": 1.0,
  "alignment_status": "good",
  "created_at": "2026-03-24T06:37:08Z",
  "cleaning_path": "text_lightweight",
  "text_dominant": true
}
```

#### solvability_report

```json
{
  "solvability_id": "solv_prob_5f07b7d4a69bb00d804afe6c",
  "problem_id": "prob_5f07b7d4a69bb00d804afe6c",
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
  "created_at": "2026-03-24T06:37:08Z"
}
```

#### cleaning_record

```json
{
  "cleaning_id": "clean_48328372045b3e280a87402e",
  "problem_id": "prob_5f07b7d4a69bb00d804afe6c",
  "cleaning_version": "v3.0.0",
  "pipeline_run_id": "run_6f9fadee9214c91e",
  "dataset_name": "muti- physics",
  "input_asset_ids": [
    "asset_6b9f13b4d6a584c8756b6eff",
    "asset_c86802975f2d69a46852040a",
    "asset_fd87f9c42442b01bd3e819e4",
    "asset_fe182ebe37149725b311cb11",
    "asset_80bbab8880b54eeff01264aa"
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
      "variable_alias_count": 5
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
    "alignment_id": "align_48328372045b3e280a87402e",
    "coverage_score": 1.0,
    "consistency_score": 1.0,
    "alignment_status": "good",
    "conflict_count": 0
  },
  "text_structure_summary": {
    "text_structure_id": "text_prob_5f07b7d4a69bb00d804afe6c",
    "question_type": "open",
    "condition_count": 3,
    "target_count": 1,
    "answer_slot_count": 1,
    "status": "complete"
  },
  "solvability_summary": {
    "solvability_id": "solv_prob_5f07b7d4a69bb00d804afe6c",
    "solvability_score": 1.0,
    "reasoning_path_exists": true,
    "decision_hint": "pass",
    "failure_codes": []
  },
  "rewrite_summary": {
    "strategy": "keep_open",
    "variant_count": 1,
    "discard_reason_codes": []
  },
  "missing_field_summary": {
    "missing_question_text": false,
    "missing_answer_text": false,
    "missing_image_count": 0
  },
  "risk_flags": [],
  "clean_score": 0.8637,
  "decision": "pass",
  "decision_reason_codes": [
    "meets_cleaning_requirements"
  ],
  "review_ticket_id": null,
  "operator_type": "system",
  "started_at": "2026-03-24T06:37:08Z",
  "finished_at": "2026-03-24T06:37:08Z",
  "candidate_id": "cand_5f07b7d4a69bb00d804afe6c",
  "cleaning_path": "text_lightweight",
  "text_dominant": true
}
```

## 3. 开放化改写前后

### 3.1 改写前

```json
{
  "question_text_before_rewrite": "如图所示为一个质点运动的位移x随时间t变化的图象,由此可知质点在0~4s内\nA. 先沿x轴正方向运动,后沿x轴负方向运动\nB. 一直做匀变速运动\nC. t=2s时速度一定最大\nD. 速率为5m/s的时刻有两个",
  "answer_text_before_rewrite": "CD",
  "raw_question_text": "如图所示为一个质点运动的位移x随时间t变化的图象，由此可知质点在0～4s内\nA. 先沿x轴正方向运动，后沿x轴负方向运动\nB. 一直做匀变速运动\nC. t=2s时速度一定最大\nD. 速率为5m/s的时刻有两个",
  "raw_answer_text": "CD"
}
```

### 3.2 改写后

```json
{
  "rewrite_report": {
    "rewrite_id": "rewrite_48328372045b3e280a87402e",
    "problem_id": "prob_5f07b7d4a69bb00d804afe6c",
    "source_problem_id": "9",
    "strategy": "keep_open",
    "rationale": "Question is already open-ended.",
    "discard_reason_codes": [],
    "variant_count": 1,
    "variants": [
      {
        "open_variant_id": "open_044e513f1390a5e07430cac7",
        "parent_problem_id": "prob_5f07b7d4a69bb00d804afe6c",
        "variant_index": 1,
        "title": "muti- physics 开放题",
        "rewritten_question_text": "如图所示为一个质点运动的位移x随时间t变化的图象,由此可知质点在0~4s内\nA. 先沿x轴正方向运动,后沿x轴负方向运动\nB. 一直做匀变速运动\nC. t=2s时速度一定最大\nD. 速率为5m/s的时刻有两个",
        "expected_answer_type": "short_text",
        "expected_answer": "CD",
        "split_role": "single"
      }
    ],
    "created_at": "2026-03-24T06:37:08Z"
  },
  "open_ended_problem_variants": [
    {
      "open_variant_id": "open_044e513f1390a5e07430cac7",
      "parent_problem_id": "prob_5f07b7d4a69bb00d804afe6c",
      "variant_index": 1,
      "title": "muti- physics 开放题",
      "rewritten_question_text": "如图所示为一个质点运动的位移x随时间t变化的图象,由此可知质点在0~4s内\nA. 先沿x轴正方向运动,后沿x轴负方向运动\nB. 一直做匀变速运动\nC. t=2s时速度一定最大\nD. 速率为5m/s的时刻有两个",
      "expected_answer_type": "short_text",
      "expected_answer": "CD",
      "split_role": "single"
    }
  ]
}
```

## 4. 完整 collection + cleaning 输出对象

#### candidate_problem_record

```json
{
  "candidate_id": "cand_5f07b7d4a69bb00d804afe6c",
  "source_dataset": "muti- physics",
  "source_split": "repo_discovered",
  "source_problem_id": "9",
  "subject": "物理",
  "raw_question_text": "如图所示为一个质点运动的位移x随时间t变化的图象，由此可知质点在0～4s内\nA. 先沿x轴正方向运动，后沿x轴负方向运动\nB. 一直做匀变速运动\nC. t=2s时速度一定最大\nD. 速率为5m/s的时刻有两个",
  "raw_answer_text": "CD",
  "has_image": false,
  "image_count": 0,
  "requires_image": false,
  "text_dominant": true,
  "recommended_cleaning_path": "text_lightweight",
  "initial_image_dependency_score": 0.2,
  "initial_multi_solution_score": 0.18,
  "initial_verifiability_score": 0.78,
  "multi_solution_mining_policy": "conservative",
  "should_push_multi_solution_agent": false,
  "multi_solution_policy_rationale": "该数据集更可能以单解题为主，不强推多解 agent，只保留基础可验证性与可标注性检查。",
  "metadata": {
    "data_file": "outputs/repo_cache/multi_physics/Data/1.json",
    "question_field": "question",
    "answer_field": "answer",
    "image_field": null,
    "choice_field": null
  },
  "created_at": "2026-03-24T06:37:08Z"
}
```

#### raw_asset_bundle

```json
{
  "raw_asset_bundle_id": "bundle_aeac7750e159725191240edf",
  "candidate_id": "cand_5f07b7d4a69bb00d804afe6c",
  "source_dataset": "muti- physics",
  "source_problem_id": "9",
  "assets": [
    {
      "asset_role": "question_text_raw",
      "storage_uri": "inline://prob_5f07b7d4a69bb00d804afe6c/question_source",
      "is_present": true
    },
    {
      "asset_role": "answer_text_raw",
      "storage_uri": "inline://prob_5f07b7d4a69bb00d804afe6c/answer_source",
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
    "initial_image_dependency_score": 0.2,
    "initial_multi_solution_score": 0.18,
    "initial_verifiability_score": 0.78
  },
  "created_at": "2026-03-24T06:37:08Z"
}
```

#### candidate_pool_entry

```json
{
  "candidate_pool_entry_id": "cpool_05fa47b9734a14b3472e240e",
  "candidate_id": "cand_5f07b7d4a69bb00d804afe6c",
  "source_dataset": "muti- physics",
  "source_problem_id": "9",
  "candidate_status": "ready_for_cleaning",
  "priority_score": 0.368,
  "priority_tier": "normal",
  "recommended_cleaning_path": "text_lightweight",
  "multi_solution_mining_policy": "conservative",
  "initial_scores": {
    "initial_image_dependency_score": 0.2,
    "initial_multi_solution_score": 0.18,
    "initial_verifiability_score": 0.78
  },
  "created_at": "2026-03-24T06:37:08Z"
}
```

#### clean_pool_entries

```json
[
  {
    "clean_pool_entry_id": "cleanpool_48328372045b3e280a87402e",
    "candidate_id": "cand_5f07b7d4a69bb00d804afe6c",
    "problem_id": "prob_5f07b7d4a69bb00d804afe6c",
    "dataset_name": "muti- physics",
    "pool_status": "ready_for_annotation",
    "clean_decision": "pass",
    "review_required": false,
    "rewrite_strategy": "keep_open",
    "open_variant_count": 1,
    "text_dominant": true,
    "cleaning_path": "text_lightweight",
    "created_at": "2026-03-24T06:37:08Z"
  }
]
```

#### rewrite_reports

```json
[
  {
    "rewrite_id": "rewrite_48328372045b3e280a87402e",
    "problem_id": "prob_5f07b7d4a69bb00d804afe6c",
    "source_problem_id": "9",
    "strategy": "keep_open",
    "rationale": "Question is already open-ended.",
    "discard_reason_codes": [],
    "variant_count": 1,
    "variants": [
      {
        "open_variant_id": "open_044e513f1390a5e07430cac7",
        "parent_problem_id": "prob_5f07b7d4a69bb00d804afe6c",
        "variant_index": 1,
        "title": "muti- physics 开放题",
        "rewritten_question_text": "如图所示为一个质点运动的位移x随时间t变化的图象,由此可知质点在0~4s内\nA. 先沿x轴正方向运动,后沿x轴负方向运动\nB. 一直做匀变速运动\nC. t=2s时速度一定最大\nD. 速率为5m/s的时刻有两个",
        "expected_answer_type": "short_text",
        "expected_answer": "CD",
        "split_role": "single"
      }
    ],
    "created_at": "2026-03-24T06:37:08Z"
  }
]
```

#### open_ended_problem_variants

```json
[
  {
    "open_variant_id": "open_044e513f1390a5e07430cac7",
    "parent_problem_id": "prob_5f07b7d4a69bb00d804afe6c",
    "variant_index": 1,
    "title": "muti- physics 开放题",
    "rewritten_question_text": "如图所示为一个质点运动的位移x随时间t变化的图象,由此可知质点在0~4s内\nA. 先沿x轴正方向运动,后沿x轴负方向运动\nB. 一直做匀变速运动\nC. t=2s时速度一定最大\nD. 速率为5m/s的时刻有两个",
    "expected_answer_type": "short_text",
    "expected_answer": "CD",
    "split_role": "single"
  }
]
```

#### asset_records

```json
[
  {
    "asset_id": "asset_6b9f13b4d6a584c8756b6eff",
    "problem_id": "prob_5f07b7d4a69bb00d804afe6c",
    "asset_type": "text",
    "asset_role": "question_text_source",
    "source_uri": "source://multi_physics/repo_discovered/9/question",
    "storage_uri": "inline://prob_5f07b7d4a69bb00d804afe6c/question_source",
    "file_format": "txt",
    "file_size_bytes": 250,
    "width": null,
    "height": null,
    "sha256": "497069ec3f9facd34b11525631d6065ef5a86c4740f659a299ea35e5113a023b",
    "perceptual_hash": null,
    "source_text_snapshot": "如图所示为一个质点运动的位移x随时间t变化的图象，由此可知质点在0～4s内\nA. 先沿x轴正方向运动，后沿x轴负方向运动\nB. 一直做匀变速运动\nC. t=2s时速度一定最大\nD. 速率为5m/s的时刻有两个",
    "normalized_text_snapshot": null,
    "text_completeness_score": 0.6429,
    "blur_score": null,
    "readability_score": null,
    "noise_score": null,
    "cropped_from_asset_id": null,
    "roi_bbox": null,
    "unit_normalization_map": [],
    "variable_aliases": [
      {
        "original": "A",
        "canonical": "A",
        "variable_type": "symbol"
      },
      {
        "original": "B",
        "canonical": "B",
        "variable_type": "symbol"
      },
      {
        "original": "C",
        "canonical": "C",
        "variable_type": "symbol"
      },
      {
        "original": "t",
        "canonical": "t",
        "variable_type": "symbol"
      },
      {
        "original": "D",
        "canonical": "D",
        "variable_type": "symbol"
      }
    ],
    "asset_quality_flags": [],
    "is_usable": true,
    "discard_reason_codes": [],
    "created_at": "2026-03-24T06:37:08Z",
    "updated_at": "2026-03-24T06:37:08Z"
  },
  {
    "asset_id": "asset_c86802975f2d69a46852040a",
    "problem_id": "prob_5f07b7d4a69bb00d804afe6c",
    "asset_type": "text",
    "asset_role": "question_text_normalized",
    "source_uri": null,
    "storage_uri": "inline://prob_5f07b7d4a69bb00d804afe6c/question_normalized",
    "file_format": "txt",
    "file_size_bytes": 244,
    "width": null,
    "height": null,
    "sha256": "ea389db05fca84e1be009afed9407a016966e5a16631a71bfbe442108c380cfa",
    "perceptual_hash": null,
    "source_text_snapshot": "如图所示为一个质点运动的位移x随时间t变化的图象，由此可知质点在0～4s内\nA. 先沿x轴正方向运动，后沿x轴负方向运动\nB. 一直做匀变速运动\nC. t=2s时速度一定最大\nD. 速率为5m/s的时刻有两个",
    "normalized_text_snapshot": "如图所示为一个质点运动的位移x随时间t变化的图象,由此可知质点在0~4s内\nA. 先沿x轴正方向运动,后沿x轴负方向运动\nB. 一直做匀变速运动\nC. t=2s时速度一定最大\nD. 速率为5m/s的时刻有两个",
    "text_completeness_score": 0.6429,
    "blur_score": null,
    "readability_score": null,
    "noise_score": null,
    "cropped_from_asset_id": null,
    "roi_bbox": null,
    "unit_normalization_map": [],
    "variable_aliases": [
      {
        "original": "A",
        "canonical": "A",
        "variable_type": "symbol"
      },
      {
        "original": "B",
        "canonical": "B",
        "variable_type": "symbol"
      },
      {
        "original": "C",
        "canonical": "C",
        "variable_type": "symbol"
      },
      {
        "original": "t",
        "canonical": "t",
        "variable_type": "symbol"
      },
      {
        "original": "D",
        "canonical": "D",
        "variable_type": "symbol"
      }
    ],
    "asset_quality_flags": [],
    "is_usable": true,
    "discard_reason_codes": [],
    "created_at": "2026-03-24T06:37:08Z",
    "updated_at": "2026-03-24T06:37:08Z"
  },
  {
    "asset_id": "asset_fd87f9c42442b01bd3e819e4",
    "problem_id": "prob_5f07b7d4a69bb00d804afe6c",
    "asset_type": "answer",
    "asset_role": "answer_raw",
    "source_uri": "source://multi_physics/repo_discovered/9/answer",
    "storage_uri": "inline://prob_5f07b7d4a69bb00d804afe6c/answer_raw",
    "file_format": "txt",
    "file_size_bytes": 2,
    "width": null,
    "height": null,
    "sha256": "90ec58127ec472ffb7e3f90c3ee320f8bb1dc6bc64a48143e6d91f7d9a6de236",
    "perceptual_hash": null,
    "source_text_snapshot": "CD",
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
        "original": "CD",
        "canonical": "CD",
        "variable_type": "label"
      }
    ],
    "asset_quality_flags": [],
    "is_usable": true,
    "discard_reason_codes": [],
    "created_at": "2026-03-24T06:37:08Z",
    "updated_at": "2026-03-24T06:37:08Z"
  },
  {
    "asset_id": "asset_fe182ebe37149725b311cb11",
    "problem_id": "prob_5f07b7d4a69bb00d804afe6c",
    "asset_type": "answer",
    "asset_role": "answer_normalized",
    "source_uri": null,
    "storage_uri": "inline://prob_5f07b7d4a69bb00d804afe6c/answer_normalized",
    "file_format": "txt",
    "file_size_bytes": 2,
    "width": null,
    "height": null,
    "sha256": "90ec58127ec472ffb7e3f90c3ee320f8bb1dc6bc64a48143e6d91f7d9a6de236",
    "perceptual_hash": null,
    "source_text_snapshot": "CD",
    "normalized_text_snapshot": "CD",
    "text_completeness_score": 1.0,
    "blur_score": null,
    "readability_score": null,
    "noise_score": null,
    "cropped_from_asset_id": null,
    "roi_bbox": null,
    "unit_normalization_map": [],
    "variable_aliases": [
      {
        "original": "CD",
        "canonical": "CD",
        "variable_type": "label"
      }
    ],
    "asset_quality_flags": [],
    "is_usable": true,
    "discard_reason_codes": [],
    "created_at": "2026-03-24T06:37:08Z",
    "updated_at": "2026-03-24T06:37:08Z"
  },
  {
    "asset_id": "asset_80bbab8880b54eeff01264aa",
    "problem_id": "prob_5f07b7d4a69bb00d804afe6c",
    "asset_type": "text",
    "asset_role": "question_text_open_variant",
    "source_uri": null,
    "storage_uri": "inline://open_044e513f1390a5e07430cac7",
    "file_format": "txt",
    "file_size_bytes": 244,
    "width": null,
    "height": null,
    "sha256": "ea389db05fca84e1be009afed9407a016966e5a16631a71bfbe442108c380cfa",
    "perceptual_hash": null,
    "source_text_snapshot": "如图所示为一个质点运动的位移x随时间t变化的图象，由此可知质点在0～4s内\nA. 先沿x轴正方向运动，后沿x轴负方向运动\nB. 一直做匀变速运动\nC. t=2s时速度一定最大\nD. 速率为5m/s的时刻有两个",
    "normalized_text_snapshot": "如图所示为一个质点运动的位移x随时间t变化的图象,由此可知质点在0~4s内\nA. 先沿x轴正方向运动,后沿x轴负方向运动\nB. 一直做匀变速运动\nC. t=2s时速度一定最大\nD. 速率为5m/s的时刻有两个",
    "text_completeness_score": 0.6429,
    "blur_score": null,
    "readability_score": null,
    "noise_score": null,
    "cropped_from_asset_id": null,
    "roi_bbox": null,
    "unit_normalization_map": [],
    "variable_aliases": [
      {
        "original": "A",
        "canonical": "A",
        "variable_type": "symbol"
      },
      {
        "original": "B",
        "canonical": "B",
        "variable_type": "symbol"
      },
      {
        "original": "C",
        "canonical": "C",
        "variable_type": "symbol"
      },
      {
        "original": "t",
        "canonical": "t",
        "variable_type": "symbol"
      },
      {
        "original": "D",
        "canonical": "D",
        "variable_type": "symbol"
      }
    ],
    "asset_quality_flags": [],
    "is_usable": true,
    "discard_reason_codes": [],
    "created_at": "2026-03-24T06:37:08Z",
    "updated_at": "2026-03-24T06:37:08Z"
  }
]
```

#### node_records

```json
[
  {
    "node_id": "node_da4f71d648640a87d53f8bae",
    "problem_id": "prob_5f07b7d4a69bb00d804afe6c",
    "node_type": "text_fact",
    "canonical_value": "如图所示为一个质点运动的位移x随时间t变化的图象,由此可知质点在0~4s内",
    "surface_forms": [
      "如图所示为一个质点运动的位移x随时间t变化的图象,由此可知质点在0~4s内"
    ],
    "origin_kind": "text",
    "cognitive_level": "objective",
    "source_refs": [
      "asset_c86802975f2d69a46852040a"
    ],
    "evidence_refs": [
      "asset_c86802975f2d69a46852040a"
    ],
    "upstream_node_ids": [],
    "value_type": "condition",
    "normalized_value": {
      "text": "如图所示为一个质点运动的位移x随时间t变化的图象,由此可知质点在0~4s内",
      "segment_index": 1,
      "mentions_visual": false,
      "numeric_tokens": [
        "0",
        "4"
      ],
      "unit_mentions": [
        "s"
      ],
      "condition_role": "explicit"
    },
    "unit": "s",
    "confidence": 0.92,
    "verifiability": "high",
    "ambiguity_level": "low",
    "is_direct_from_source": true,
    "is_generated_by_system": false,
    "is_reviewed_by_human": false,
    "stage_created": "cleaning",
    "status": "active",
    "version": 1,
    "created_at": "2026-03-24T06:37:08Z",
    "updated_at": "2026-03-24T06:37:08Z"
  },
  {
    "node_id": "node_bfbca503e1e1c42b6f80e55f",
    "problem_id": "prob_5f07b7d4a69bb00d804afe6c",
    "node_type": "text_fact",
    "canonical_value": "t=2s时速度一定最大",
    "surface_forms": [
      "t=2s时速度一定最大"
    ],
    "origin_kind": "text",
    "cognitive_level": "objective",
    "source_refs": [
      "asset_c86802975f2d69a46852040a"
    ],
    "evidence_refs": [
      "asset_c86802975f2d69a46852040a"
    ],
    "upstream_node_ids": [],
    "value_type": "condition",
    "normalized_value": {
      "text": "t=2s时速度一定最大",
      "segment_index": 7,
      "mentions_visual": false,
      "numeric_tokens": [
        "2"
      ],
      "unit_mentions": [
        "s"
      ],
      "condition_role": "explicit"
    },
    "unit": "s",
    "confidence": 0.92,
    "verifiability": "high",
    "ambiguity_level": "low",
    "is_direct_from_source": true,
    "is_generated_by_system": false,
    "is_reviewed_by_human": false,
    "stage_created": "cleaning",
    "status": "active",
    "version": 1,
    "created_at": "2026-03-24T06:37:08Z",
    "updated_at": "2026-03-24T06:37:08Z"
  },
  {
    "node_id": "node_45c07575717a060885d57cc9",
    "problem_id": "prob_5f07b7d4a69bb00d804afe6c",
    "node_type": "text_fact",
    "canonical_value": "速率为5m/s的时刻有两个",
    "surface_forms": [
      "速率为5m/s的时刻有两个"
    ],
    "origin_kind": "text",
    "cognitive_level": "objective",
    "source_refs": [
      "asset_c86802975f2d69a46852040a"
    ],
    "evidence_refs": [
      "asset_c86802975f2d69a46852040a"
    ],
    "upstream_node_ids": [],
    "value_type": "condition",
    "normalized_value": {
      "text": "速率为5m/s的时刻有两个",
      "segment_index": 9,
      "mentions_visual": false,
      "numeric_tokens": [
        "5"
      ],
      "unit_mentions": [
        "m",
        "s"
      ],
      "condition_role": "explicit"
    },
    "unit": "m,s",
    "confidence": 0.92,
    "verifiability": "high",
    "ambiguity_level": "low",
    "is_direct_from_source": true,
    "is_generated_by_system": false,
    "is_reviewed_by_human": false,
    "stage_created": "cleaning",
    "status": "active",
    "version": 1,
    "created_at": "2026-03-24T06:37:08Z",
    "updated_at": "2026-03-24T06:37:08Z"
  },
  {
    "node_id": "node_4ab6a2cae257338186b925ad",
    "problem_id": "prob_5f07b7d4a69bb00d804afe6c",
    "node_type": "target_slot",
    "canonical_value": "速率为5m/s的时刻有两个",
    "surface_forms": [
      "速率为5m/s的时刻有两个"
    ],
    "origin_kind": "text_structure",
    "cognitive_level": "computed",
    "source_refs": [
      "asset_c86802975f2d69a46852040a"
    ],
    "evidence_refs": [
      "asset_c86802975f2d69a46852040a"
    ],
    "upstream_node_ids": [],
    "value_type": "short_text",
    "normalized_value": {
      "slot_id": "slot_prob_5f07b7d4a69bb00d804afe6c_1",
      "variant_index": 1,
      "split_role": "single",
      "slot_type": "short_text",
      "target_text": "速率为5m/s的时刻有两个",
      "expected_answer_type": "short_text",
      "expected_answer": "CD",
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
    "created_at": "2026-03-24T06:37:08Z",
    "updated_at": "2026-03-24T06:37:08Z"
  },
  {
    "node_id": "node_9b2025f74ac9867495de5d63",
    "problem_id": "prob_5f07b7d4a69bb00d804afe6c",
    "node_type": "answer_claim",
    "canonical_value": "CD",
    "surface_forms": [
      "CD"
    ],
    "origin_kind": "text",
    "cognitive_level": "objective",
    "source_refs": [
      "asset_fe182ebe37149725b311cb11"
    ],
    "evidence_refs": [
      "asset_fe182ebe37149725b311cb11"
    ],
    "upstream_node_ids": [],
    "value_type": "short_text",
    "normalized_value": {
      "answer": "CD"
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
    "created_at": "2026-03-24T06:37:08Z",
    "updated_at": "2026-03-24T06:37:08Z"
  },
  {
    "node_id": "node_f960dc391c8acfcf194a044f",
    "problem_id": "prob_5f07b7d4a69bb00d804afe6c",
    "node_type": "text_fact",
    "canonical_value": "如图所示为一个质点运动的位移x随时间t变化的图象,由此可知质点在0~4s内\nA. 先沿x轴正方向运动,后沿x轴负方向运动\nB. 一直做匀变速运动\nC. t=2s时速度一定最大\nD. 速率为5m/s的时刻有两个",
    "surface_forms": [
      "如图所示为一个质点运动的位移x随时间t变化的图象,由此可知质点在0~4s内\nA. 先沿x轴正方向运动,后沿x轴负方向运动\nB. 一直做匀变速运动\nC. t=2s时速度一定最大\nD. 速率为5m/s的时刻有两个"
    ],
    "origin_kind": "reasoning",
    "cognitive_level": "computed",
    "source_refs": [
      "asset_80bbab8880b54eeff01264aa"
    ],
    "evidence_refs": [
      "asset_80bbab8880b54eeff01264aa"
    ],
    "upstream_node_ids": [],
    "value_type": "text",
    "normalized_value": {
      "open_variant_id": "open_044e513f1390a5e07430cac7",
      "parent_problem_id": "prob_5f07b7d4a69bb00d804afe6c",
      "variant_index": 1,
      "title": "muti- physics 开放题",
      "rewritten_question_text": "如图所示为一个质点运动的位移x随时间t变化的图象,由此可知质点在0~4s内\nA. 先沿x轴正方向运动,后沿x轴负方向运动\nB. 一直做匀变速运动\nC. t=2s时速度一定最大\nD. 速率为5m/s的时刻有两个",
      "expected_answer_type": "short_text",
      "expected_answer": "CD",
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
    "created_at": "2026-03-24T06:37:08Z",
    "updated_at": "2026-03-24T06:37:08Z"
  },
  {
    "node_id": "node_36f1cc0ef3a58b48b678f7a1",
    "problem_id": "prob_5f07b7d4a69bb00d804afe6c",
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
      "solvability_id": "solv_prob_5f07b7d4a69bb00d804afe6c",
      "problem_id": "prob_5f07b7d4a69bb00d804afe6c",
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
      "created_at": "2026-03-24T06:37:08Z"
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
    "created_at": "2026-03-24T06:37:08Z",
    "updated_at": "2026-03-24T06:37:08Z"
  },
  {
    "node_id": "node_4601cb187678210ace4da65d",
    "problem_id": "prob_5f07b7d4a69bb00d804afe6c",
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
    "created_at": "2026-03-24T06:37:08Z",
    "updated_at": "2026-03-24T06:37:08Z"
  }
]
```

#### field_audit_records

```json
[
  {
    "audit_id": "audit_5a6cc182ab9a2dc06964d166",
    "problem_id": "prob_5f07b7d4a69bb00d804afe6c",
    "record_type": "problem_main_record",
    "field_name": "normalized_question_text",
    "before_value": "如图所示为一个质点运动的位移x随时间t变化的图象，由此可知质点在0～4s内\nA. 先沿x轴正方向运动，后沿x轴负方向运动\nB. 一直做匀变速运动\nC. t=2s时速度一定最大\nD. 速率为5m/s的时刻有两个",
    "after_value": "如图所示为一个质点运动的位移x随时间t变化的图象,由此可知质点在0~4s内\nA. 先沿x轴正方向运动,后沿x轴负方向运动\nB. 一直做匀变速运动\nC. t=2s时速度一定最大\nD. 速率为5m/s的时刻有两个",
    "change_type": "text_normalized",
    "trigger": "NormalizationAgent",
    "operator_type": "system",
    "created_at": "2026-03-24T06:37:08Z"
  },
  {
    "audit_id": "audit_3ae8e732bfc124395b04197a",
    "problem_id": "prob_5f07b7d4a69bb00d804afe6c",
    "record_type": "problem_main_record",
    "field_name": "normalized_answer_text",
    "before_value": "CD",
    "after_value": "CD",
    "change_type": "answer_canonicalized",
    "trigger": "NormalizationAgent",
    "operator_type": "system",
    "created_at": "2026-03-24T06:37:08Z"
  },
  {
    "audit_id": "audit_2efd092f3dfb5709e63a0966",
    "problem_id": "prob_5f07b7d4a69bb00d804afe6c",
    "record_type": "rewrite_report",
    "field_name": "rewrite_strategy",
    "before_value": null,
    "after_value": "keep_open",
    "change_type": "question_rewritten",
    "trigger": "QuestionRewriteAgent",
    "operator_type": "system",
    "created_at": "2026-03-24T06:37:08Z"
  },
  {
    "audit_id": "audit_4601cb187678210ace4da65d",
    "problem_id": "prob_5f07b7d4a69bb00d804afe6c",
    "record_type": "cleaning_record",
    "field_name": "decision",
    "before_value": null,
    "after_value": "pass",
    "change_type": "gate_decision",
    "trigger": "CleanGateAgent",
    "operator_type": "system",
    "created_at": "2026-03-24T06:37:08Z"
  },
  {
    "audit_id": "audit_4defe0f4235384ba8a65bdc7",
    "problem_id": "prob_5f07b7d4a69bb00d804afe6c",
    "record_type": "normalized_assets",
    "field_name": "variable_aliases",
    "before_value": null,
    "after_value": [
      {
        "original": "A",
        "canonical": "A",
        "variable_type": "symbol"
      },
      {
        "original": "B",
        "canonical": "B",
        "variable_type": "symbol"
      },
      {
        "original": "C",
        "canonical": "C",
        "variable_type": "symbol"
      },
      {
        "original": "t",
        "canonical": "t",
        "variable_type": "symbol"
      },
      {
        "original": "D",
        "canonical": "D",
        "variable_type": "symbol"
      }
    ],
    "change_type": "variable_canonicalized",
    "trigger": "NormalizationAgent",
    "operator_type": "system",
    "created_at": "2026-03-24T06:37:08Z"
  }
]
```

#### reject_records

```json
[]
```

### 4.1 完整 sample bundle 原文件

- `outputs/user_requested_batch_review/pipeline_runs/run_6f9fadee9214c91e/datasets/multi_physics/samples/prob_5f07b7d4a69bb00d804afe6c.json`
