# muti- physics / prob_a9fc15484cddc66957a9bcd3

- source_problem_id: `14`
- source_split: `repo_discovered`
- clean_decision: `pass`
- rewrite_strategy: `keep_open`
- full sample bundle JSON: `outputs/user_requested_batch_review/pipeline_runs/run_6f9fadee9214c91e/datasets/multi_physics/samples/prob_a9fc15484cddc66957a9bcd3.json`

## 1. 原始内容（处理前）

### 1.1 原始快照

```json
{
  "dataset_key": "multi_physics",
  "source_problem_id": "14",
  "source_split": "repo_discovered",
  "raw_question_text": "甲、乙两车在同一条直道上行驶，它们运动的位移x随时间t变化的关系如图所示。已知乙车做匀变速直线运动，其图线与t轴相切于10 s处。则下列说法正确的是\nA．甲车的初速度为零\nB．乙车的初位置在$x_0=60 \\mathrm{m}$处[来源:学+科+网]\nC．乙车的加速度大小为$1.6\\mathrm{~m/s^2}$\nD．5 s时两车相遇，此时乙车速度较大",
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
    "question": "甲、乙两车在同一条直道上行驶，它们运动的位移x随时间t变化的关系如图所示。已知乙车做匀变速直线运动，其图线与t轴相切于10 s处。则下列说法正确的是\nA．甲车的初速度为零\nB．乙车的初位置在$x_0=60 \\mathrm{m}$处[来源:学+科+网]\nC．乙车的加速度大小为$1.6\\mathrm{~m/s^2}$\nD．5 s时两车相遇，此时乙车速度较大",
    "picture": [
      "../Data/1/14_0.png"
    ],
    "answer": [
      "CD"
    ],
    "analysis": "由位移图像可知，车做匀速直线运动，乙车做匀变速直线运动，其图线与轴相切于10s处，10s时乙车速度减小到零。根据位移图像斜率表示速度可知甲车的初速度为4ms，选项A错误；把末速度为零的乙车的运动做逆向处理，看作初速度为零匀加速直线运动，由$\\mid20=\\frac{1}{2} at_{1}^{2} , t_{1}=5s , x_{0}=\\frac{1}{2} at^{2} , t=10s ,$解得：x=80m,$a=1.6m/s^2$，。即乙车的初位置在x=80m处，乙车的加速度大小为$1.6m/s^2$，选项B错误C正确；5s时两车都处在x=20m处相遇，此时乙车速度$\\mathrm{~v=at_{1}=1.6\\times5m~s=8.0m/s}$，而甲车的速度为4m/s，乙车速度较大，选项D正确。",
    "index": 14,
    "level": 3
  }
}
```

## 2. 处理前后对照

### 2.1 关键字段对照

| 字段 | 处理前 | 处理后 |
| --- | --- | --- |
| question_text | 甲、乙两车在同一条直道上行驶，它们运动的位移x随时间t变化的关系如图所示。已知乙车做匀变速直线运动，其图线与t轴相切于10 s处。则下列说法正确的是 A．甲车的初速度为零 B．乙车的初位置在$x_0=60 \mathrm{m}$处[来源:学+科+网] C．乙车的加速度大小为$1.6\mathrm{~m/s^2}$ D．5 s时两车相遇，此时乙车速度较大 | 甲、乙两车在同一条直道上行驶,它们运动的位移x随时间t变化的关系如图所示。已知乙车做匀变速直线运动,其图线与t轴相切于10 s处。则下列说法正确的是 A.甲车的初速度为零 B.乙车的初位置在$x_0=60 \mathrm{m}$处[来源:学+科+网] C.乙车的加速度大小为$1.6\mathrm{~m/s^2}$ D.5 s时两车相遇,此时乙车速度较大 |
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
  "problem_id": "prob_a9fc15484cddc66957a9bcd3",
  "source_dataset": "muti- physics",
  "source_split": "repo_discovered",
  "source_problem_id": "14",
  "ingest_batch_id": "multidataset-clean_20260324T063656Z",
  "problem_type": "multimodal_reasoning",
  "domain_tags": [
    "物理"
  ],
  "language": "zh",
  "raw_question_text": "甲、乙两车在同一条直道上行驶，它们运动的位移x随时间t变化的关系如图所示。已知乙车做匀变速直线运动，其图线与t轴相切于10 s处。则下列说法正确的是\nA．甲车的初速度为零\nB．乙车的初位置在$x_0=60 \\mathrm{m}$处[来源:学+科+网]\nC．乙车的加速度大小为$1.6\\mathrm{~m/s^2}$\nD．5 s时两车相遇，此时乙车速度较大",
  "normalized_question_text": "甲、乙两车在同一条直道上行驶,它们运动的位移x随时间t变化的关系如图所示。已知乙车做匀变速直线运动,其图线与t轴相切于10 s处。则下列说法正确的是\nA.甲车的初速度为零\nB.乙车的初位置在$x_0=60 \\mathrm{m}$处[来源:学+科+网]\nC.乙车的加速度大小为$1.6\\mathrm{~m/s^2}$\nD.5 s时两车相遇,此时乙车速度较大",
  "raw_answer_text": "CD",
  "normalized_answer_text": "CD",
  "answer_type": "short_text",
  "image_count": 0,
  "has_multiple_images": false,
  "requires_image": false,
  "multimodal_strength_score": 0.48,
  "multi_step_score": 0.4817,
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
  "candidate_id": "cand_a9fc15484cddc66957a9bcd3",
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
  "clean_problem_record_id": "cleanprob_29a6c1f29e3752ae41dccf48",
  "problem_id": "prob_a9fc15484cddc66957a9bcd3",
  "source_dataset": "muti- physics",
  "source_problem_id": "14",
  "normalized_question_text": "甲、乙两车在同一条直道上行驶,它们运动的位移x随时间t变化的关系如图所示。已知乙车做匀变速直线运动,其图线与t轴相切于10 s处。则下列说法正确的是\nA.甲车的初速度为零\nB.乙车的初位置在$x_0=60 \\mathrm{m}$处[来源:学+科+网]\nC.乙车的加速度大小为$1.6\\mathrm{~m/s^2}$\nD.5 s时两车相遇,此时乙车速度较大",
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
  "normalized_assets_id": "nassets_29a6c1f29e3752ae41dccf48",
  "problem_id": "prob_a9fc15484cddc66957a9bcd3",
  "normalized_question_text": "甲、乙两车在同一条直道上行驶,它们运动的位移x随时间t变化的关系如图所示。已知乙车做匀变速直线运动,其图线与t轴相切于10 s处。则下列说法正确的是\nA.甲车的初速度为零\nB.乙车的初位置在$x_0=60 \\mathrm{m}$处[来源:学+科+网]\nC.乙车的加速度大小为$1.6\\mathrm{~m/s^2}$\nD.5 s时两车相遇,此时乙车速度较大",
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
      "original": "m",
      "canonical": "m",
      "variable_type": "symbol"
    },
    {
      "original": "C",
      "canonical": "C",
      "variable_type": "symbol"
    },
    {
      "original": "s",
      "canonical": "s",
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
      "text": "甲、乙两车在同一条直道上行驶,它们运动的位移x随时间t变化的关系如图所示。已知乙车做匀变速直线运动,其图线与t轴相切于10 s处。则下列说法正确的是"
    },
    {
      "segment_index": 2,
      "text": "A.甲车的初速度为零"
    },
    {
      "segment_index": 3,
      "text": "B.乙车的初位置在$x_0=60 \\mathrm{m}$处[来源:学+科+网]"
    },
    {
      "segment_index": 4,
      "text": "C.乙车的加速度大小为$1.6\\mathrm{~m/s^2}$"
    },
    {
      "segment_index": 5,
      "text": "D.5 s时两车相遇,此时乙车速度较大"
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
  "text_structure_id": "text_prob_a9fc15484cddc66957a9bcd3",
  "problem_id": "prob_a9fc15484cddc66957a9bcd3",
  "question_type": "open",
  "conditions": [
    {
      "text": "甲、乙两车在同一条直道上行驶,它们运动的位移x随时间t变化的关系如图所示。已知乙车做匀变速直线运动,其图线与t轴相切于10 s处。则下列说法正确的是",
      "segment_index": 1,
      "mentions_visual": false,
      "numeric_tokens": [
        "10"
      ],
      "unit_mentions": [
        "s"
      ],
      "condition_role": "explicit"
    },
    {
      "text": "B.乙车的初位置在$x_0=60 \\mathrm{m}$处[来源:学+科+网]",
      "segment_index": 3,
      "mentions_visual": false,
      "numeric_tokens": [
        "0",
        "60"
      ],
      "unit_mentions": [
        "h",
        "m"
      ],
      "condition_role": "explicit"
    },
    {
      "text": "C.乙车的加速度大小为$1.6\\mathrm{~m/s^2}$",
      "segment_index": 4,
      "mentions_visual": false,
      "numeric_tokens": [
        "1.6",
        "2"
      ],
      "unit_mentions": [
        "h",
        "m",
        "s"
      ],
      "condition_role": "explicit"
    },
    {
      "text": "D.5 s时两车相遇,此时乙车速度较大",
      "segment_index": 5,
      "mentions_visual": false,
      "numeric_tokens": [
        ".5"
      ],
      "unit_mentions": [
        "s"
      ],
      "condition_role": "explicit"
    }
  ],
  "targets": [
    {
      "text": "甲、乙两车在同一条直道上行驶,它们运动的位移x随时间t变化的关系如图所示。已知乙车做匀变速直线运动,其图线与t轴相切于10 s处。则下列说法正确的是\nA.甲车的初速度为零\nB.乙车的初位置在$x_0=60 \\mathrm{m}$处[来源:学+科+网]\nC.乙车的加速度大小为$1.6\\mathrm{~m/s^2}$\nD.5 s时两车相遇,此时乙车速度较大",
      "segment_index": 5,
      "mentions_visual": false,
      "numeric_tokens": [
        "10",
        "0",
        "60",
        "1.6",
        "2",
        ".5"
      ],
      "unit_mentions": [
        "A",
        "h",
        "m",
        "s"
      ],
      "target_role": "fallback"
    }
  ],
  "answer_slots": [
    {
      "slot_id": "slot_prob_a9fc15484cddc66957a9bcd3_1",
      "variant_index": 1,
      "split_role": "single",
      "slot_type": "short_text",
      "target_text": "D.5 s时两车相遇,此时乙车速度较大",
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
      "original": "m",
      "canonical": "m",
      "variable_type": "symbol"
    },
    {
      "original": "C",
      "canonical": "C",
      "variable_type": "symbol"
    },
    {
      "original": "s",
      "canonical": "s",
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
    "h",
    "m",
    "s"
  ],
  "sentence_segments": [
    {
      "segment_index": 1,
      "text": "甲、乙两车在同一条直道上行驶,它们运动的位移x随时间t变化的关系如图所示。已知乙车做匀变速直线运动,其图线与t轴相切于10 s处。则下列说法正确的是"
    },
    {
      "segment_index": 2,
      "text": "A.甲车的初速度为零"
    },
    {
      "segment_index": 3,
      "text": "B.乙车的初位置在$x_0=60 \\mathrm{m}$处[来源:学+科+网]"
    },
    {
      "segment_index": 4,
      "text": "C.乙车的加速度大小为$1.6\\mathrm{~m/s^2}$"
    },
    {
      "segment_index": 5,
      "text": "D.5 s时两车相遇,此时乙车速度较大"
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
  "alignment_id": "align_29a6c1f29e3752ae41dccf48",
  "problem_id": "prob_a9fc15484cddc66957a9bcd3",
  "image_entity_refs": [],
  "text_span_refs": [
    "asset_prob_a9fc15484cddc66957a9bcd3_question_text_normalized"
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
  "solvability_id": "solv_prob_a9fc15484cddc66957a9bcd3",
  "problem_id": "prob_a9fc15484cddc66957a9bcd3",
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
  "cleaning_id": "clean_29a6c1f29e3752ae41dccf48",
  "problem_id": "prob_a9fc15484cddc66957a9bcd3",
  "cleaning_version": "v3.0.0",
  "pipeline_run_id": "run_6f9fadee9214c91e",
  "dataset_name": "muti- physics",
  "input_asset_ids": [
    "asset_fe776797a35aef3c76655f36",
    "asset_e45ae5f848dad5405bdbe0ca",
    "asset_10888dea23e568e70c72b542",
    "asset_1f6ed984e95a75c1307d8acd",
    "asset_aae11ebeb4d026bdeb1cc99c"
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
      "variable_alias_count": 6
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
    "alignment_id": "align_29a6c1f29e3752ae41dccf48",
    "coverage_score": 1.0,
    "consistency_score": 1.0,
    "alignment_status": "good",
    "conflict_count": 0
  },
  "text_structure_summary": {
    "text_structure_id": "text_prob_a9fc15484cddc66957a9bcd3",
    "question_type": "open",
    "condition_count": 4,
    "target_count": 1,
    "answer_slot_count": 1,
    "status": "complete"
  },
  "solvability_summary": {
    "solvability_id": "solv_prob_a9fc15484cddc66957a9bcd3",
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
  "clean_score": 0.8741,
  "decision": "pass",
  "decision_reason_codes": [
    "meets_cleaning_requirements"
  ],
  "review_ticket_id": null,
  "operator_type": "system",
  "started_at": "2026-03-24T06:37:08Z",
  "finished_at": "2026-03-24T06:37:08Z",
  "candidate_id": "cand_a9fc15484cddc66957a9bcd3",
  "cleaning_path": "text_lightweight",
  "text_dominant": true
}
```

## 3. 开放化改写前后

### 3.1 改写前

```json
{
  "question_text_before_rewrite": "甲、乙两车在同一条直道上行驶,它们运动的位移x随时间t变化的关系如图所示。已知乙车做匀变速直线运动,其图线与t轴相切于10 s处。则下列说法正确的是\nA.甲车的初速度为零\nB.乙车的初位置在$x_0=60 \\mathrm{m}$处[来源:学+科+网]\nC.乙车的加速度大小为$1.6\\mathrm{~m/s^2}$\nD.5 s时两车相遇,此时乙车速度较大",
  "answer_text_before_rewrite": "CD",
  "raw_question_text": "甲、乙两车在同一条直道上行驶，它们运动的位移x随时间t变化的关系如图所示。已知乙车做匀变速直线运动，其图线与t轴相切于10 s处。则下列说法正确的是\nA．甲车的初速度为零\nB．乙车的初位置在$x_0=60 \\mathrm{m}$处[来源:学+科+网]\nC．乙车的加速度大小为$1.6\\mathrm{~m/s^2}$\nD．5 s时两车相遇，此时乙车速度较大",
  "raw_answer_text": "CD"
}
```

### 3.2 改写后

```json
{
  "rewrite_report": {
    "rewrite_id": "rewrite_29a6c1f29e3752ae41dccf48",
    "problem_id": "prob_a9fc15484cddc66957a9bcd3",
    "source_problem_id": "14",
    "strategy": "keep_open",
    "rationale": "Question is already open-ended.",
    "discard_reason_codes": [],
    "variant_count": 1,
    "variants": [
      {
        "open_variant_id": "open_3fe6d185934008286e3742f5",
        "parent_problem_id": "prob_a9fc15484cddc66957a9bcd3",
        "variant_index": 1,
        "title": "muti- physics 开放题",
        "rewritten_question_text": "甲、乙两车在同一条直道上行驶,它们运动的位移x随时间t变化的关系如图所示。已知乙车做匀变速直线运动,其图线与t轴相切于10 s处。则下列说法正确的是\nA.甲车的初速度为零\nB.乙车的初位置在$x_0=60 \\mathrm{m}$处[来源:学+科+网]\nC.乙车的加速度大小为$1.6\\mathrm{~m/s^2}$\nD.5 s时两车相遇,此时乙车速度较大",
        "expected_answer_type": "short_text",
        "expected_answer": "CD",
        "split_role": "single"
      }
    ],
    "created_at": "2026-03-24T06:37:08Z"
  },
  "open_ended_problem_variants": [
    {
      "open_variant_id": "open_3fe6d185934008286e3742f5",
      "parent_problem_id": "prob_a9fc15484cddc66957a9bcd3",
      "variant_index": 1,
      "title": "muti- physics 开放题",
      "rewritten_question_text": "甲、乙两车在同一条直道上行驶,它们运动的位移x随时间t变化的关系如图所示。已知乙车做匀变速直线运动,其图线与t轴相切于10 s处。则下列说法正确的是\nA.甲车的初速度为零\nB.乙车的初位置在$x_0=60 \\mathrm{m}$处[来源:学+科+网]\nC.乙车的加速度大小为$1.6\\mathrm{~m/s^2}$\nD.5 s时两车相遇,此时乙车速度较大",
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
  "candidate_id": "cand_a9fc15484cddc66957a9bcd3",
  "source_dataset": "muti- physics",
  "source_split": "repo_discovered",
  "source_problem_id": "14",
  "subject": "物理",
  "raw_question_text": "甲、乙两车在同一条直道上行驶，它们运动的位移x随时间t变化的关系如图所示。已知乙车做匀变速直线运动，其图线与t轴相切于10 s处。则下列说法正确的是\nA．甲车的初速度为零\nB．乙车的初位置在$x_0=60 \\mathrm{m}$处[来源:学+科+网]\nC．乙车的加速度大小为$1.6\\mathrm{~m/s^2}$\nD．5 s时两车相遇，此时乙车速度较大",
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
  "raw_asset_bundle_id": "bundle_270153d3233a5409eb6f54d7",
  "candidate_id": "cand_a9fc15484cddc66957a9bcd3",
  "source_dataset": "muti- physics",
  "source_problem_id": "14",
  "assets": [
    {
      "asset_role": "question_text_raw",
      "storage_uri": "inline://prob_a9fc15484cddc66957a9bcd3/question_source",
      "is_present": true
    },
    {
      "asset_role": "answer_text_raw",
      "storage_uri": "inline://prob_a9fc15484cddc66957a9bcd3/answer_source",
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
  "candidate_pool_entry_id": "cpool_c770a820de16f15e8aadaaad",
  "candidate_id": "cand_a9fc15484cddc66957a9bcd3",
  "source_dataset": "muti- physics",
  "source_problem_id": "14",
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
    "clean_pool_entry_id": "cleanpool_29a6c1f29e3752ae41dccf48",
    "candidate_id": "cand_a9fc15484cddc66957a9bcd3",
    "problem_id": "prob_a9fc15484cddc66957a9bcd3",
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
    "rewrite_id": "rewrite_29a6c1f29e3752ae41dccf48",
    "problem_id": "prob_a9fc15484cddc66957a9bcd3",
    "source_problem_id": "14",
    "strategy": "keep_open",
    "rationale": "Question is already open-ended.",
    "discard_reason_codes": [],
    "variant_count": 1,
    "variants": [
      {
        "open_variant_id": "open_3fe6d185934008286e3742f5",
        "parent_problem_id": "prob_a9fc15484cddc66957a9bcd3",
        "variant_index": 1,
        "title": "muti- physics 开放题",
        "rewritten_question_text": "甲、乙两车在同一条直道上行驶,它们运动的位移x随时间t变化的关系如图所示。已知乙车做匀变速直线运动,其图线与t轴相切于10 s处。则下列说法正确的是\nA.甲车的初速度为零\nB.乙车的初位置在$x_0=60 \\mathrm{m}$处[来源:学+科+网]\nC.乙车的加速度大小为$1.6\\mathrm{~m/s^2}$\nD.5 s时两车相遇,此时乙车速度较大",
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
    "open_variant_id": "open_3fe6d185934008286e3742f5",
    "parent_problem_id": "prob_a9fc15484cddc66957a9bcd3",
    "variant_index": 1,
    "title": "muti- physics 开放题",
    "rewritten_question_text": "甲、乙两车在同一条直道上行驶,它们运动的位移x随时间t变化的关系如图所示。已知乙车做匀变速直线运动,其图线与t轴相切于10 s处。则下列说法正确的是\nA.甲车的初速度为零\nB.乙车的初位置在$x_0=60 \\mathrm{m}$处[来源:学+科+网]\nC.乙车的加速度大小为$1.6\\mathrm{~m/s^2}$\nD.5 s时两车相遇,此时乙车速度较大",
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
    "asset_id": "asset_fe776797a35aef3c76655f36",
    "problem_id": "prob_a9fc15484cddc66957a9bcd3",
    "asset_type": "text",
    "asset_role": "question_text_source",
    "source_uri": "source://multi_physics/repo_discovered/14/question",
    "storage_uri": "inline://prob_a9fc15484cddc66957a9bcd3/question_source",
    "file_format": "txt",
    "file_size_bytes": 407,
    "width": null,
    "height": null,
    "sha256": "5e918854fba2afb8268372e77af4f8ec2a170fc35ff84f43dfa1dc075484d62c",
    "perceptual_hash": null,
    "source_text_snapshot": "甲、乙两车在同一条直道上行驶，它们运动的位移x随时间t变化的关系如图所示。已知乙车做匀变速直线运动，其图线与t轴相切于10 s处。则下列说法正确的是\nA．甲车的初速度为零\nB．乙车的初位置在$x_0=60 \\mathrm{m}$处[来源:学+科+网]\nC．乙车的加速度大小为$1.6\\mathrm{~m/s^2}$\nD．5 s时两车相遇，此时乙车速度较大",
    "normalized_text_snapshot": null,
    "text_completeness_score": 0.708,
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
        "original": "m",
        "canonical": "m",
        "variable_type": "symbol"
      },
      {
        "original": "C",
        "canonical": "C",
        "variable_type": "symbol"
      },
      {
        "original": "s",
        "canonical": "s",
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
    "asset_id": "asset_e45ae5f848dad5405bdbe0ca",
    "problem_id": "prob_a9fc15484cddc66957a9bcd3",
    "asset_type": "text",
    "asset_role": "question_text_normalized",
    "source_uri": null,
    "storage_uri": "inline://prob_a9fc15484cddc66957a9bcd3/question_normalized",
    "file_format": "txt",
    "file_size_bytes": 393,
    "width": null,
    "height": null,
    "sha256": "2f8a14083ea2b9bc4573700a76bf75918adac766b44712809b3ab5ca7f108fc6",
    "perceptual_hash": null,
    "source_text_snapshot": "甲、乙两车在同一条直道上行驶，它们运动的位移x随时间t变化的关系如图所示。已知乙车做匀变速直线运动，其图线与t轴相切于10 s处。则下列说法正确的是\nA．甲车的初速度为零\nB．乙车的初位置在$x_0=60 \\mathrm{m}$处[来源:学+科+网]\nC．乙车的加速度大小为$1.6\\mathrm{~m/s^2}$\nD．5 s时两车相遇，此时乙车速度较大",
    "normalized_text_snapshot": "甲、乙两车在同一条直道上行驶,它们运动的位移x随时间t变化的关系如图所示。已知乙车做匀变速直线运动,其图线与t轴相切于10 s处。则下列说法正确的是\nA.甲车的初速度为零\nB.乙车的初位置在$x_0=60 \\mathrm{m}$处[来源:学+科+网]\nC.乙车的加速度大小为$1.6\\mathrm{~m/s^2}$\nD.5 s时两车相遇,此时乙车速度较大",
    "text_completeness_score": 0.708,
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
        "original": "m",
        "canonical": "m",
        "variable_type": "symbol"
      },
      {
        "original": "C",
        "canonical": "C",
        "variable_type": "symbol"
      },
      {
        "original": "s",
        "canonical": "s",
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
    "asset_id": "asset_10888dea23e568e70c72b542",
    "problem_id": "prob_a9fc15484cddc66957a9bcd3",
    "asset_type": "answer",
    "asset_role": "answer_raw",
    "source_uri": "source://multi_physics/repo_discovered/14/answer",
    "storage_uri": "inline://prob_a9fc15484cddc66957a9bcd3/answer_raw",
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
    "asset_id": "asset_1f6ed984e95a75c1307d8acd",
    "problem_id": "prob_a9fc15484cddc66957a9bcd3",
    "asset_type": "answer",
    "asset_role": "answer_normalized",
    "source_uri": null,
    "storage_uri": "inline://prob_a9fc15484cddc66957a9bcd3/answer_normalized",
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
    "asset_id": "asset_aae11ebeb4d026bdeb1cc99c",
    "problem_id": "prob_a9fc15484cddc66957a9bcd3",
    "asset_type": "text",
    "asset_role": "question_text_open_variant",
    "source_uri": null,
    "storage_uri": "inline://open_3fe6d185934008286e3742f5",
    "file_format": "txt",
    "file_size_bytes": 393,
    "width": null,
    "height": null,
    "sha256": "2f8a14083ea2b9bc4573700a76bf75918adac766b44712809b3ab5ca7f108fc6",
    "perceptual_hash": null,
    "source_text_snapshot": "甲、乙两车在同一条直道上行驶，它们运动的位移x随时间t变化的关系如图所示。已知乙车做匀变速直线运动，其图线与t轴相切于10 s处。则下列说法正确的是\nA．甲车的初速度为零\nB．乙车的初位置在$x_0=60 \\mathrm{m}$处[来源:学+科+网]\nC．乙车的加速度大小为$1.6\\mathrm{~m/s^2}$\nD．5 s时两车相遇，此时乙车速度较大",
    "normalized_text_snapshot": "甲、乙两车在同一条直道上行驶,它们运动的位移x随时间t变化的关系如图所示。已知乙车做匀变速直线运动,其图线与t轴相切于10 s处。则下列说法正确的是\nA.甲车的初速度为零\nB.乙车的初位置在$x_0=60 \\mathrm{m}$处[来源:学+科+网]\nC.乙车的加速度大小为$1.6\\mathrm{~m/s^2}$\nD.5 s时两车相遇,此时乙车速度较大",
    "text_completeness_score": 0.708,
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
        "original": "m",
        "canonical": "m",
        "variable_type": "symbol"
      },
      {
        "original": "C",
        "canonical": "C",
        "variable_type": "symbol"
      },
      {
        "original": "s",
        "canonical": "s",
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
    "node_id": "node_815316fa1eab85d02fc9b095",
    "problem_id": "prob_a9fc15484cddc66957a9bcd3",
    "node_type": "text_fact",
    "canonical_value": "甲、乙两车在同一条直道上行驶,它们运动的位移x随时间t变化的关系如图所示。已知乙车做匀变速直线运动,其图线与t轴相切于10 s处。则下列说法正确的是",
    "surface_forms": [
      "甲、乙两车在同一条直道上行驶,它们运动的位移x随时间t变化的关系如图所示。已知乙车做匀变速直线运动,其图线与t轴相切于10 s处。则下列说法正确的是"
    ],
    "origin_kind": "text",
    "cognitive_level": "objective",
    "source_refs": [
      "asset_e45ae5f848dad5405bdbe0ca"
    ],
    "evidence_refs": [
      "asset_e45ae5f848dad5405bdbe0ca"
    ],
    "upstream_node_ids": [],
    "value_type": "condition",
    "normalized_value": {
      "text": "甲、乙两车在同一条直道上行驶,它们运动的位移x随时间t变化的关系如图所示。已知乙车做匀变速直线运动,其图线与t轴相切于10 s处。则下列说法正确的是",
      "segment_index": 1,
      "mentions_visual": false,
      "numeric_tokens": [
        "10"
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
    "node_id": "node_da3073d00abe4380241864cc",
    "problem_id": "prob_a9fc15484cddc66957a9bcd3",
    "node_type": "text_fact",
    "canonical_value": "B.乙车的初位置在$x_0=60 \\mathrm{m}$处[来源:学+科+网]",
    "surface_forms": [
      "B.乙车的初位置在$x_0=60 \\mathrm{m}$处[来源:学+科+网]"
    ],
    "origin_kind": "text",
    "cognitive_level": "objective",
    "source_refs": [
      "asset_e45ae5f848dad5405bdbe0ca"
    ],
    "evidence_refs": [
      "asset_e45ae5f848dad5405bdbe0ca"
    ],
    "upstream_node_ids": [],
    "value_type": "condition",
    "normalized_value": {
      "text": "B.乙车的初位置在$x_0=60 \\mathrm{m}$处[来源:学+科+网]",
      "segment_index": 3,
      "mentions_visual": false,
      "numeric_tokens": [
        "0",
        "60"
      ],
      "unit_mentions": [
        "h",
        "m"
      ],
      "condition_role": "explicit"
    },
    "unit": "h,m",
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
    "node_id": "node_41847f64ea02992c276e6883",
    "problem_id": "prob_a9fc15484cddc66957a9bcd3",
    "node_type": "text_fact",
    "canonical_value": "C.乙车的加速度大小为$1.6\\mathrm{~m/s^2}$",
    "surface_forms": [
      "C.乙车的加速度大小为$1.6\\mathrm{~m/s^2}$"
    ],
    "origin_kind": "text",
    "cognitive_level": "objective",
    "source_refs": [
      "asset_e45ae5f848dad5405bdbe0ca"
    ],
    "evidence_refs": [
      "asset_e45ae5f848dad5405bdbe0ca"
    ],
    "upstream_node_ids": [],
    "value_type": "condition",
    "normalized_value": {
      "text": "C.乙车的加速度大小为$1.6\\mathrm{~m/s^2}$",
      "segment_index": 4,
      "mentions_visual": false,
      "numeric_tokens": [
        "1.6",
        "2"
      ],
      "unit_mentions": [
        "h",
        "m",
        "s"
      ],
      "condition_role": "explicit"
    },
    "unit": "h,m,s",
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
    "node_id": "node_8ed9dab7367fd61cc081ae8d",
    "problem_id": "prob_a9fc15484cddc66957a9bcd3",
    "node_type": "text_fact",
    "canonical_value": "D.5 s时两车相遇,此时乙车速度较大",
    "surface_forms": [
      "D.5 s时两车相遇,此时乙车速度较大"
    ],
    "origin_kind": "text",
    "cognitive_level": "objective",
    "source_refs": [
      "asset_e45ae5f848dad5405bdbe0ca"
    ],
    "evidence_refs": [
      "asset_e45ae5f848dad5405bdbe0ca"
    ],
    "upstream_node_ids": [],
    "value_type": "condition",
    "normalized_value": {
      "text": "D.5 s时两车相遇,此时乙车速度较大",
      "segment_index": 5,
      "mentions_visual": false,
      "numeric_tokens": [
        ".5"
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
    "node_id": "node_1a8c79c09d15a5274085ded3",
    "problem_id": "prob_a9fc15484cddc66957a9bcd3",
    "node_type": "target_slot",
    "canonical_value": "D.5 s时两车相遇,此时乙车速度较大",
    "surface_forms": [
      "D.5 s时两车相遇,此时乙车速度较大"
    ],
    "origin_kind": "text_structure",
    "cognitive_level": "computed",
    "source_refs": [
      "asset_e45ae5f848dad5405bdbe0ca"
    ],
    "evidence_refs": [
      "asset_e45ae5f848dad5405bdbe0ca"
    ],
    "upstream_node_ids": [],
    "value_type": "short_text",
    "normalized_value": {
      "slot_id": "slot_prob_a9fc15484cddc66957a9bcd3_1",
      "variant_index": 1,
      "split_role": "single",
      "slot_type": "short_text",
      "target_text": "D.5 s时两车相遇,此时乙车速度较大",
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
    "node_id": "node_5931b04bfe6d14f9151fe69b",
    "problem_id": "prob_a9fc15484cddc66957a9bcd3",
    "node_type": "answer_claim",
    "canonical_value": "CD",
    "surface_forms": [
      "CD"
    ],
    "origin_kind": "text",
    "cognitive_level": "objective",
    "source_refs": [
      "asset_1f6ed984e95a75c1307d8acd"
    ],
    "evidence_refs": [
      "asset_1f6ed984e95a75c1307d8acd"
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
    "node_id": "node_5d0836f9958c27609b4cb635",
    "problem_id": "prob_a9fc15484cddc66957a9bcd3",
    "node_type": "text_fact",
    "canonical_value": "甲、乙两车在同一条直道上行驶,它们运动的位移x随时间t变化的关系如图所示。已知乙车做匀变速直线运动,其图线与t轴相切于10 s处。则下列说法正确的是\nA.甲车的初速度为零\nB.乙车的初位置在$x_0=60 \\mathrm{m}$处[来源:学+科+网]\nC.乙车的加速度大小为$1.6\\mathrm{~m/s^2}$\nD.5 s时两车相遇,此时乙车速度较大",
    "surface_forms": [
      "甲、乙两车在同一条直道上行驶,它们运动的位移x随时间t变化的关系如图所示。已知乙车做匀变速直线运动,其图线与t轴相切于10 s处。则下列说法正确的是\nA.甲车的初速度为零\nB.乙车的初位置在$x_0=60 \\mathrm{m}$处[来源:学+科+网]\nC.乙车的加速度大小为$1.6\\mathrm{~m/s^2}$\nD.5 s时两车相遇,此时乙车速度较大"
    ],
    "origin_kind": "reasoning",
    "cognitive_level": "computed",
    "source_refs": [
      "asset_aae11ebeb4d026bdeb1cc99c"
    ],
    "evidence_refs": [
      "asset_aae11ebeb4d026bdeb1cc99c"
    ],
    "upstream_node_ids": [],
    "value_type": "text",
    "normalized_value": {
      "open_variant_id": "open_3fe6d185934008286e3742f5",
      "parent_problem_id": "prob_a9fc15484cddc66957a9bcd3",
      "variant_index": 1,
      "title": "muti- physics 开放题",
      "rewritten_question_text": "甲、乙两车在同一条直道上行驶,它们运动的位移x随时间t变化的关系如图所示。已知乙车做匀变速直线运动,其图线与t轴相切于10 s处。则下列说法正确的是\nA.甲车的初速度为零\nB.乙车的初位置在$x_0=60 \\mathrm{m}$处[来源:学+科+网]\nC.乙车的加速度大小为$1.6\\mathrm{~m/s^2}$\nD.5 s时两车相遇,此时乙车速度较大",
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
    "node_id": "node_3a0a12ce0c1f2d021b4cbf7f",
    "problem_id": "prob_a9fc15484cddc66957a9bcd3",
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
      "solvability_id": "solv_prob_a9fc15484cddc66957a9bcd3",
      "problem_id": "prob_a9fc15484cddc66957a9bcd3",
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
    "node_id": "node_abc954185150c24bd2bdbdb2",
    "problem_id": "prob_a9fc15484cddc66957a9bcd3",
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
    "audit_id": "audit_cfb386f98287928892a2dc8a",
    "problem_id": "prob_a9fc15484cddc66957a9bcd3",
    "record_type": "problem_main_record",
    "field_name": "normalized_question_text",
    "before_value": "甲、乙两车在同一条直道上行驶，它们运动的位移x随时间t变化的关系如图所示。已知乙车做匀变速直线运动，其图线与t轴相切于10 s处。则下列说法正确的是\nA．甲车的初速度为零\nB．乙车的初位置在$x_0=60 \\mathrm{m}$处[来源:学+科+网]\nC．乙车的加速度大小为$1.6\\mathrm{~m/s^2}$\nD．5 s时两车相遇，此时乙车速度较大",
    "after_value": "甲、乙两车在同一条直道上行驶,它们运动的位移x随时间t变化的关系如图所示。已知乙车做匀变速直线运动,其图线与t轴相切于10 s处。则下列说法正确的是\nA.甲车的初速度为零\nB.乙车的初位置在$x_0=60 \\mathrm{m}$处[来源:学+科+网]\nC.乙车的加速度大小为$1.6\\mathrm{~m/s^2}$\nD.5 s时两车相遇,此时乙车速度较大",
    "change_type": "text_normalized",
    "trigger": "NormalizationAgent",
    "operator_type": "system",
    "created_at": "2026-03-24T06:37:08Z"
  },
  {
    "audit_id": "audit_1495a510646bc4039257f42d",
    "problem_id": "prob_a9fc15484cddc66957a9bcd3",
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
    "audit_id": "audit_e9c61be38644683ad8a34a66",
    "problem_id": "prob_a9fc15484cddc66957a9bcd3",
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
    "audit_id": "audit_abc954185150c24bd2bdbdb2",
    "problem_id": "prob_a9fc15484cddc66957a9bcd3",
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
    "audit_id": "audit_3f970aea7587d29520494743",
    "problem_id": "prob_a9fc15484cddc66957a9bcd3",
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
        "original": "m",
        "canonical": "m",
        "variable_type": "symbol"
      },
      {
        "original": "C",
        "canonical": "C",
        "variable_type": "symbol"
      },
      {
        "original": "s",
        "canonical": "s",
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

- `outputs/user_requested_batch_review/pipeline_runs/run_6f9fadee9214c91e/datasets/multi_physics/samples/prob_a9fc15484cddc66957a9bcd3.json`
