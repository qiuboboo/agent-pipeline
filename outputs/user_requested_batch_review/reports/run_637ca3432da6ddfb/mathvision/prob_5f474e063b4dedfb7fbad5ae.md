# MathVision / prob_5f474e063b4dedfb7fbad5ae

- source_problem_id: `17`
- source_split: `test`
- clean_decision: `reject`
- rewrite_strategy: `keep_open`
- full sample bundle JSON: `outputs/user_requested_batch_review/pipeline_runs/run_637ca3432da6ddfb/datasets/mathvision/samples/prob_5f474e063b4dedfb7fbad5ae.json`

## 1. 原始内容（处理前）

### 1.1 原始快照

```json
{
  "dataset_key": "mathvision",
  "source_problem_id": "17",
  "source_split": "test",
  "raw_question_text": "A jump of a little kangaroo is three times shorter than its mother's. How many jumps should the little kangaroo make to cover the distance equal to 7 jumps of its mother?\n<image1>",
  "raw_answer_text": "21",
  "choice_map": {},
  "image_sources": [
    "inline://pil_image"
  ],
  "metadata": {
    "row_index": 16,
    "question_field": "question",
    "answer_field": "answer",
    "image_field": "decoded_image",
    "choice_field": null
  },
  "raw_record": {
    "id": "17",
    "question": "A jump of a little kangaroo is three times shorter than its mother's. How many jumps should the little kangaroo make to cover the distance equal to 7 jumps of its mother?\n<image1>",
    "options": [],
    "image": "images/17.jpg",
    "decoded_image": "<JpegImageFile size=(414, 182) mode=RGB>",
    "answer": "21",
    "solution": null,
    "level": 2,
    "subject": "arithmetic"
  }
}
```

### 1.2 原始图片

- （无）

## 2. 处理前后对照

### 2.1 关键字段对照

| 字段 | 处理前 | 处理后 |
| --- | --- | --- |
| question_text | A jump of a little kangaroo is three times shorter than its mother's. How many jumps should the little kangaroo make to cover the distance equal to 7 jumps of its mother? <image1> | A jump of a little kangaroo is three times shorter than its mother's. How many jumps should the little kangaroo make to cover the distance equal to 7 jumps of its mother? <image1> |
| answer_text | 21 | 21 |
| answer_type | - | numeric |
| image_count | 1 | 1 |
| text_dominant | - | False |
| cleaning_path | - | multimodal_full |
| clean_decision | - | reject |
| alignment_status | - | good |
| solvability_decision_hint | - | pass |
| rewrite_strategy | - | keep_open |

### 2.2 结构化处理后结果

#### problem_main_record

```json
{
  "problem_id": "prob_5f474e063b4dedfb7fbad5ae",
  "source_dataset": "MathVision",
  "source_split": "test",
  "source_problem_id": "17",
  "ingest_batch_id": "multidataset-clean_20260324T074830Z",
  "problem_type": "multimodal_reasoning",
  "domain_tags": [
    "数学"
  ],
  "language": "en",
  "raw_question_text": "A jump of a little kangaroo is three times shorter than its mother's. How many jumps should the little kangaroo make to cover the distance equal to 7 jumps of its mother?\n<image1>",
  "normalized_question_text": "A jump of a little kangaroo is three times shorter than its mother's. How many jumps should the little kangaroo make to cover the distance equal to 7 jumps of its mother?\n<image1>",
  "raw_answer_text": "21",
  "normalized_answer_text": "21",
  "answer_type": "numeric",
  "image_count": 1,
  "has_multiple_images": false,
  "requires_image": true,
  "multimodal_strength_score": 0.9622,
  "multi_step_score": 0.3017,
  "verifiability_score": 1.0,
  "quality_risk_flags": [
    "low_resolution"
  ],
  "current_status": "clean_rejected",
  "clean_decision": "reject",
  "clean_decision_reason_codes": [
    "low_resolution"
  ],
  "review_priority": "normal",
  "annotation_ready": false,
  "qa_precheck_ready": false,
  "release_reserved": {},
  "rewrite_strategy": "keep_open",
  "open_variant_count": 1,
  "candidate_id": "cand_5f474e063b4dedfb7fbad5ae",
  "text_dominant": false,
  "cleaning_path": "multimodal_full",
  "alignment_status": "good",
  "solvability_score": 1.0,
  "solvability_decision_hint": "pass",
  "created_at": "2026-03-24T07:48:40Z",
  "updated_at": "2026-03-24T07:48:40Z",
  "initial_image_dependency_score": 0.9,
  "initial_multi_solution_score": 0.46,
  "initial_verifiability_score": 0.8726,
  "multi_solution_mining_policy": "aggressive"
}
```

#### clean_problem_record

```json
{
  "clean_problem_record_id": "cleanprob_1e0778a5fdaa41be635d4796",
  "problem_id": "prob_5f474e063b4dedfb7fbad5ae",
  "source_dataset": "MathVision",
  "source_problem_id": "17",
  "normalized_question_text": "A jump of a little kangaroo is three times shorter than its mother's. How many jumps should the little kangaroo make to cover the distance equal to 7 jumps of its mother?\n<image1>",
  "normalized_answer_text": "21",
  "image_count": 1,
  "has_multiple_images": false,
  "requires_image": true,
  "text_dominant": false,
  "cleaning_path": "multimodal_full",
  "question_type": "open",
  "open_variant_count": 1,
  "alignment_status": "good",
  "solvability_score": 1.0,
  "solvability_path_mode": "multimodal",
  "clean_decision": "reject",
  "decision_reason_codes": [
    "low_resolution"
  ],
  "created_at": "2026-03-24T07:48:40Z"
}
```

#### normalized_assets

```json
{
  "normalized_assets_id": "nassets_1e0778a5fdaa41be635d4796",
  "problem_id": "prob_5f474e063b4dedfb7fbad5ae",
  "normalized_question_text": "A jump of a little kangaroo is three times shorter than its mother's. How many jumps should the little kangaroo make to cover the distance equal to 7 jumps of its mother?\n<image1>",
  "normalized_answer_text": "21",
  "question_unit_normalization_map": [],
  "answer_unit_normalization_map": [],
  "variable_aliases": [
    {
      "original": "A",
      "canonical": "A",
      "variable_type": "symbol"
    },
    {
      "original": "jump",
      "canonical": "jump",
      "variable_type": "label"
    },
    {
      "original": "of",
      "canonical": "of",
      "variable_type": "label"
    },
    {
      "original": "a",
      "canonical": "a",
      "variable_type": "symbol"
    },
    {
      "original": "is",
      "canonical": "is",
      "variable_type": "label"
    },
    {
      "original": "than",
      "canonical": "than",
      "variable_type": "label"
    },
    {
      "original": "its",
      "canonical": "its",
      "variable_type": "label"
    },
    {
      "original": "s",
      "canonical": "s",
      "variable_type": "symbol"
    },
    {
      "original": "How",
      "canonical": "How",
      "variable_type": "label"
    },
    {
      "original": "many",
      "canonical": "many",
      "variable_type": "label"
    },
    {
      "original": "the",
      "canonical": "the",
      "variable_type": "label"
    },
    {
      "original": "make",
      "canonical": "make",
      "variable_type": "label"
    },
    {
      "original": "to",
      "canonical": "to",
      "variable_type": "label"
    }
  ],
  "sentence_segments": [
    {
      "segment_index": 1,
      "text": "A jump of a little kangaroo is three times shorter than its mother's."
    },
    {
      "segment_index": 2,
      "text": "How many jumps should the little kangaroo make to cover the distance equal to 7 jumps of its mother?"
    },
    {
      "segment_index": 3,
      "text": "<image1>"
    }
  ],
  "image_regions": [
    {
      "image_index": 1,
      "source_uri": "inline://pil_image",
      "roi_bbox": {
        "x": 24,
        "y": 16,
        "width": 368,
        "height": 143
      },
      "readability_score": 0.772,
      "contrast_score": 38.6284
    }
  ],
  "text_dominant": false,
  "cleaning_path": "multimodal_full",
  "created_at": "2026-03-24T07:48:40Z"
}
```

#### text_structure_record

```json
{
  "text_structure_id": "text_prob_5f474e063b4dedfb7fbad5ae",
  "problem_id": "prob_5f474e063b4dedfb7fbad5ae",
  "question_type": "open",
  "conditions": [
    {
      "text": "<image1>",
      "segment_index": 3,
      "mentions_visual": false,
      "numeric_tokens": [
        "1"
      ],
      "unit_mentions": [
        "g",
        "m"
      ],
      "condition_role": "explicit"
    }
  ],
  "targets": [
    {
      "text": "How many jumps should the little kangaroo make to cover the distance equal to 7 jumps of its mother?",
      "segment_index": 2,
      "mentions_visual": false,
      "numeric_tokens": [
        "7"
      ],
      "unit_mentions": [
        "g",
        "h",
        "m",
        "s"
      ],
      "target_role": "primary"
    }
  ],
  "answer_slots": [
    {
      "slot_id": "slot_prob_5f474e063b4dedfb7fbad5ae_1",
      "variant_index": 1,
      "split_role": "single",
      "slot_type": "numeric",
      "target_text": "<image1>",
      "expected_answer_type": "numeric",
      "expected_answer": "21",
      "requires_visual_grounding": false
    }
  ],
  "entity_mentions": [
    {
      "mention": "image",
      "entity_category": "image",
      "requires_visual_grounding": true
    },
    {
      "mention": "A",
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
      "original": "jump",
      "canonical": "jump",
      "variable_type": "label"
    },
    {
      "original": "of",
      "canonical": "of",
      "variable_type": "label"
    },
    {
      "original": "a",
      "canonical": "a",
      "variable_type": "symbol"
    },
    {
      "original": "is",
      "canonical": "is",
      "variable_type": "label"
    },
    {
      "original": "than",
      "canonical": "than",
      "variable_type": "label"
    },
    {
      "original": "its",
      "canonical": "its",
      "variable_type": "label"
    },
    {
      "original": "s",
      "canonical": "s",
      "variable_type": "symbol"
    },
    {
      "original": "How",
      "canonical": "How",
      "variable_type": "label"
    },
    {
      "original": "many",
      "canonical": "many",
      "variable_type": "label"
    },
    {
      "original": "the",
      "canonical": "the",
      "variable_type": "label"
    },
    {
      "original": "make",
      "canonical": "make",
      "variable_type": "label"
    },
    {
      "original": "to",
      "canonical": "to",
      "variable_type": "label"
    }
  ],
  "unit_mentions": [
    "A",
    "g",
    "h",
    "m",
    "s"
  ],
  "sentence_segments": [
    {
      "segment_index": 1,
      "text": "A jump of a little kangaroo is three times shorter than its mother's."
    },
    {
      "segment_index": 2,
      "text": "How many jumps should the little kangaroo make to cover the distance equal to 7 jumps of its mother?"
    },
    {
      "segment_index": 3,
      "text": "<image1>"
    }
  ],
  "requires_visual_grounding": true,
  "text_structure_status": "complete",
  "parser_confidence": 0.92,
  "created_at": "2026-03-24T07:48:40Z"
}
```

#### visual_structure_records

```json
[
  {
    "visual_structure_id": "visual_prob_5f474e063b4dedfb7fbad5ae_1",
    "problem_id": "prob_5f474e063b4dedfb7fbad5ae",
    "image_index": 1,
    "image_asset_role": "primary_image",
    "global_attributes": {
      "visual_kind": "wide_diagram",
      "aspect_ratio": 2.2747,
      "dark_pixel_ratio": 0.1847,
      "readability_score": 0.772,
      "has_roi": true
    },
    "visual_entities": [
      {
        "entity_id": "canvas",
        "entity_type": "full_canvas",
        "bbox": {
          "x": 0,
          "y": 0,
          "width": 414,
          "height": 182
        },
        "salience": 1.0
      },
      {
        "entity_id": "roi",
        "entity_type": "content_region",
        "bbox": {
          "x": 24,
          "y": 16,
          "width": 368,
          "height": 143
        },
        "salience": 0.95
      },
      {
        "entity_id": "roi_top_left",
        "entity_type": "subregion",
        "bbox": {
          "x": 24,
          "y": 16,
          "width": 184,
          "height": 71
        },
        "salience": 0.4418
      },
      {
        "entity_id": "roi_top_right",
        "entity_type": "subregion",
        "bbox": {
          "x": 208,
          "y": 16,
          "width": 184,
          "height": 71
        },
        "salience": 0.8337
      },
      {
        "entity_id": "roi_bottom_left",
        "entity_type": "subregion",
        "bbox": {
          "x": 24,
          "y": 87,
          "width": 184,
          "height": 72
        },
        "salience": 0.5313
      },
      {
        "entity_id": "roi_bottom_right",
        "entity_type": "subregion",
        "bbox": {
          "x": 208,
          "y": 87,
          "width": 184,
          "height": 72
        },
        "salience": 0.6515
      }
    ],
    "visual_relations": [
      {
        "source_entity_id": "roi",
        "target_entity_id": "canvas",
        "relation": "inside"
      },
      {
        "source_entity_id": "roi_top_left",
        "target_entity_id": "canvas",
        "relation": "inside"
      },
      {
        "source_entity_id": "roi_top_right",
        "target_entity_id": "canvas",
        "relation": "inside"
      },
      {
        "source_entity_id": "roi_bottom_left",
        "target_entity_id": "canvas",
        "relation": "inside"
      },
      {
        "source_entity_id": "roi_bottom_right",
        "target_entity_id": "canvas",
        "relation": "inside"
      },
      {
        "source_entity_id": "roi",
        "target_entity_id": "roi_top_left",
        "relation": "left_of"
      },
      {
        "source_entity_id": "roi_top_left",
        "target_entity_id": "roi_top_right",
        "relation": "left_of"
      },
      {
        "source_entity_id": "roi_top_right",
        "target_entity_id": "roi_bottom_left",
        "relation": "right_of"
      },
      {
        "source_entity_id": "roi_bottom_left",
        "target_entity_id": "roi_bottom_right",
        "relation": "left_of"
      }
    ],
    "parser_confidence": 0.9088,
    "created_at": "2026-03-24T07:48:40Z"
  }
]
```

#### alignment_record

```json
{
  "alignment_id": "align_1e0778a5fdaa41be635d4796",
  "problem_id": "prob_5f474e063b4dedfb7fbad5ae",
  "image_entity_refs": [
    "visual_prob_5f474e063b4dedfb7fbad5ae_1::roi",
    "visual_prob_5f474e063b4dedfb7fbad5ae_1::roi_top_left",
    "visual_prob_5f474e063b4dedfb7fbad5ae_1::roi_top_right",
    "visual_prob_5f474e063b4dedfb7fbad5ae_1::roi_bottom_left",
    "visual_prob_5f474e063b4dedfb7fbad5ae_1::roi_bottom_right"
  ],
  "text_span_refs": [
    "asset_prob_5f474e063b4dedfb7fbad5ae_question_text_normalized"
  ],
  "alignment_pairs": [
    {
      "text_ref": "image",
      "image_ref": "visual_prob_5f474e063b4dedfb7fbad5ae_1::roi",
      "relation": "grounds_image",
      "confidence": 0.7772
    },
    {
      "text_ref": "A",
      "image_ref": "visual_prob_5f474e063b4dedfb7fbad5ae_1::roi",
      "relation": "grounds_label",
      "confidence": 0.7772
    }
  ],
  "conflict_pairs": [
    {
      "type": "implicit_visual_dependency",
      "detail": "题目依赖图像，但题干中视觉锚点表达较弱。",
      "severity": "minor",
      "confidence": 0.61
    }
  ],
  "coverage_score": 0.9,
  "consistency_score": 0.9,
  "alignment_status": "good",
  "created_at": "2026-03-24T07:48:40Z",
  "cleaning_path": "multimodal_full",
  "text_dominant": false
}
```

#### solvability_report

```json
{
  "solvability_id": "solv_prob_5f474e063b4dedfb7fbad5ae",
  "problem_id": "prob_5f474e063b4dedfb7fbad5ae",
  "answer_verifiable": true,
  "target_clear": true,
  "rewrite_complete": true,
  "text_sufficient": true,
  "visual_grounding_available": true,
  "reasoning_path_exists": true,
  "path_mode": "multimodal",
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
  "created_at": "2026-03-24T07:48:40Z"
}
```

#### cleaning_record

```json
{
  "cleaning_id": "clean_1e0778a5fdaa41be635d4796",
  "problem_id": "prob_5f474e063b4dedfb7fbad5ae",
  "cleaning_version": "v3.0.0",
  "pipeline_run_id": "run_637ca3432da6ddfb",
  "dataset_name": "MathVision",
  "input_asset_ids": [
    "asset_22909c10067f227624b6ed94",
    "asset_747aba5221c5dd6033ef095b",
    "asset_49e3f0de96e56bcd7cbf4e92",
    "asset_339058f52c1b41de68933ca6",
    "asset_1e233ed3003a1d5b5eafb478",
    "asset_726fe65dc6c11e400eead187",
    "asset_a46478cf747ee37ece10f00d"
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
      "variable_alias_count": 13
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
      "check": "image_quality_1",
      "result": {
        "width": 414,
        "height": 182,
        "blur_score": 3526.8535,
        "contrast_score": 38.6284,
        "noise_score": 23.5401,
        "readability_score": 0.772,
        "crop_integrity_score": 1.0,
        "roi_bbox": {
          "x": 24,
          "y": 16,
          "width": 368,
          "height": 143
        },
        "perceptual_hash": "fffce0c19999fdff"
      },
      "passed": true
    }
  ],
  "alignment_summary": {
    "alignment_id": "align_1e0778a5fdaa41be635d4796",
    "coverage_score": 0.9,
    "consistency_score": 0.9,
    "alignment_status": "good",
    "conflict_count": 1
  },
  "text_structure_summary": {
    "text_structure_id": "text_prob_5f474e063b4dedfb7fbad5ae",
    "question_type": "open",
    "condition_count": 1,
    "target_count": 1,
    "answer_slot_count": 1,
    "status": "complete"
  },
  "solvability_summary": {
    "solvability_id": "solv_prob_5f474e063b4dedfb7fbad5ae",
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
  "risk_flags": [
    "low_resolution"
  ],
  "clean_score": 0.8818,
  "decision": "reject",
  "decision_reason_codes": [
    "low_resolution"
  ],
  "review_ticket_id": null,
  "operator_type": "system",
  "started_at": "2026-03-24T07:48:40Z",
  "finished_at": "2026-03-24T07:48:40Z",
  "candidate_id": "cand_5f474e063b4dedfb7fbad5ae",
  "cleaning_path": "multimodal_full",
  "text_dominant": false
}
```

## 3. 开放化改写前后

### 3.1 改写前

```json
{
  "question_text_before_rewrite": "A jump of a little kangaroo is three times shorter than its mother's. How many jumps should the little kangaroo make to cover the distance equal to 7 jumps of its mother?\n<image1>",
  "answer_text_before_rewrite": "21",
  "raw_question_text": "A jump of a little kangaroo is three times shorter than its mother's. How many jumps should the little kangaroo make to cover the distance equal to 7 jumps of its mother?\n<image1>",
  "raw_answer_text": "21"
}
```

### 3.2 改写后

```json
{
  "rewrite_report": {
    "rewrite_id": "rewrite_1e0778a5fdaa41be635d4796",
    "problem_id": "prob_5f474e063b4dedfb7fbad5ae",
    "source_problem_id": "17",
    "strategy": "keep_open",
    "rationale": "Question is already open-ended.",
    "discard_reason_codes": [],
    "variant_count": 1,
    "variants": [
      {
        "open_variant_id": "open_2f3dea16a2fce26e8e7d98f2",
        "parent_problem_id": "prob_5f474e063b4dedfb7fbad5ae",
        "variant_index": 1,
        "title": "MathVision 开放题",
        "rewritten_question_text": "A jump of a little kangaroo is three times shorter than its mother's. How many jumps should the little kangaroo make to cover the distance equal to 7 jumps of its mother?\n<image1>",
        "expected_answer_type": "numeric",
        "expected_answer": "21",
        "split_role": "single"
      }
    ],
    "created_at": "2026-03-24T07:48:40Z"
  },
  "open_ended_problem_variants": [
    {
      "open_variant_id": "open_2f3dea16a2fce26e8e7d98f2",
      "parent_problem_id": "prob_5f474e063b4dedfb7fbad5ae",
      "variant_index": 1,
      "title": "MathVision 开放题",
      "rewritten_question_text": "A jump of a little kangaroo is three times shorter than its mother's. How many jumps should the little kangaroo make to cover the distance equal to 7 jumps of its mother?\n<image1>",
      "expected_answer_type": "numeric",
      "expected_answer": "21",
      "split_role": "single"
    }
  ]
}
```

## 4. 完整 collection + cleaning 输出对象

#### candidate_problem_record

```json
{
  "candidate_id": "cand_5f474e063b4dedfb7fbad5ae",
  "source_dataset": "MathVision",
  "source_split": "test",
  "source_problem_id": "17",
  "subject": "数学",
  "raw_question_text": "A jump of a little kangaroo is three times shorter than its mother's. How many jumps should the little kangaroo make to cover the distance equal to 7 jumps of its mother?\n<image1>",
  "raw_answer_text": "21",
  "has_image": true,
  "image_count": 1,
  "requires_image": true,
  "text_dominant": false,
  "recommended_cleaning_path": "multimodal_full",
  "initial_image_dependency_score": 0.9,
  "initial_multi_solution_score": 0.46,
  "initial_verifiability_score": 0.8726,
  "multi_solution_mining_policy": "aggressive",
  "should_push_multi_solution_agent": true,
  "multi_solution_policy_rationale": "该数据集被视为具备较稳定的多解潜力，可进入更强的多解挖掘链路。",
  "metadata": {
    "row_index": 16,
    "question_field": "question",
    "answer_field": "answer",
    "image_field": "decoded_image",
    "choice_field": null
  },
  "created_at": "2026-03-24T07:48:40Z"
}
```

#### raw_asset_bundle

```json
{
  "raw_asset_bundle_id": "bundle_400c8d032c7bede367ab95b2",
  "candidate_id": "cand_5f474e063b4dedfb7fbad5ae",
  "source_dataset": "MathVision",
  "source_problem_id": "17",
  "assets": [
    {
      "asset_role": "question_text_raw",
      "storage_uri": "inline://prob_5f474e063b4dedfb7fbad5ae/question_source",
      "is_present": true
    },
    {
      "asset_role": "answer_text_raw",
      "storage_uri": "inline://prob_5f474e063b4dedfb7fbad5ae/answer_source",
      "is_present": true
    },
    {
      "asset_role": "image_raw",
      "storage_uri": "inline://pil_image",
      "is_present": true,
      "width": 414,
      "height": 182
    }
  ],
  "core_asset_completeness": {
    "has_question_text": true,
    "has_answer_text": true,
    "image_count": 1,
    "has_multiple_images": false
  },
  "initial_scores": {
    "initial_image_dependency_score": 0.9,
    "initial_multi_solution_score": 0.46,
    "initial_verifiability_score": 0.8726
  },
  "created_at": "2026-03-24T07:48:40Z"
}
```

#### candidate_pool_entry

```json
{
  "candidate_pool_entry_id": "cpool_df5a2044fa8b283e2cc94350",
  "candidate_id": "cand_5f474e063b4dedfb7fbad5ae",
  "source_dataset": "MathVision",
  "source_problem_id": "17",
  "candidate_status": "ready_for_cleaning",
  "priority_score": 0.7598,
  "priority_tier": "high",
  "recommended_cleaning_path": "multimodal_full",
  "multi_solution_mining_policy": "aggressive",
  "initial_scores": {
    "initial_image_dependency_score": 0.9,
    "initial_multi_solution_score": 0.46,
    "initial_verifiability_score": 0.8726
  },
  "created_at": "2026-03-24T07:48:40Z"
}
```

#### clean_pool_entries

```json
[]
```

#### rewrite_reports

```json
[
  {
    "rewrite_id": "rewrite_1e0778a5fdaa41be635d4796",
    "problem_id": "prob_5f474e063b4dedfb7fbad5ae",
    "source_problem_id": "17",
    "strategy": "keep_open",
    "rationale": "Question is already open-ended.",
    "discard_reason_codes": [],
    "variant_count": 1,
    "variants": [
      {
        "open_variant_id": "open_2f3dea16a2fce26e8e7d98f2",
        "parent_problem_id": "prob_5f474e063b4dedfb7fbad5ae",
        "variant_index": 1,
        "title": "MathVision 开放题",
        "rewritten_question_text": "A jump of a little kangaroo is three times shorter than its mother's. How many jumps should the little kangaroo make to cover the distance equal to 7 jumps of its mother?\n<image1>",
        "expected_answer_type": "numeric",
        "expected_answer": "21",
        "split_role": "single"
      }
    ],
    "created_at": "2026-03-24T07:48:40Z"
  }
]
```

#### open_ended_problem_variants

```json
[
  {
    "open_variant_id": "open_2f3dea16a2fce26e8e7d98f2",
    "parent_problem_id": "prob_5f474e063b4dedfb7fbad5ae",
    "variant_index": 1,
    "title": "MathVision 开放题",
    "rewritten_question_text": "A jump of a little kangaroo is three times shorter than its mother's. How many jumps should the little kangaroo make to cover the distance equal to 7 jumps of its mother?\n<image1>",
    "expected_answer_type": "numeric",
    "expected_answer": "21",
    "split_role": "single"
  }
]
```

#### asset_records

```json
[
  {
    "asset_id": "asset_22909c10067f227624b6ed94",
    "problem_id": "prob_5f474e063b4dedfb7fbad5ae",
    "asset_type": "text",
    "asset_role": "question_text_source",
    "source_uri": "source://mathvision/test/17/question",
    "storage_uri": "inline://prob_5f474e063b4dedfb7fbad5ae/question_source",
    "file_format": "txt",
    "file_size_bytes": 179,
    "width": null,
    "height": null,
    "sha256": "eb66881190e12bac841b3687c48fdb6aa4651e0ae1e523ad359ce185bcb04be1",
    "perceptual_hash": null,
    "source_text_snapshot": "A jump of a little kangaroo is three times shorter than its mother's. How many jumps should the little kangaroo make to cover the distance equal to 7 jumps of its mother?\n<image1>",
    "normalized_text_snapshot": null,
    "text_completeness_score": 0.7098,
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
        "original": "jump",
        "canonical": "jump",
        "variable_type": "label"
      },
      {
        "original": "of",
        "canonical": "of",
        "variable_type": "label"
      },
      {
        "original": "a",
        "canonical": "a",
        "variable_type": "symbol"
      },
      {
        "original": "is",
        "canonical": "is",
        "variable_type": "label"
      },
      {
        "original": "than",
        "canonical": "than",
        "variable_type": "label"
      },
      {
        "original": "its",
        "canonical": "its",
        "variable_type": "label"
      },
      {
        "original": "s",
        "canonical": "s",
        "variable_type": "symbol"
      },
      {
        "original": "How",
        "canonical": "How",
        "variable_type": "label"
      },
      {
        "original": "many",
        "canonical": "many",
        "variable_type": "label"
      },
      {
        "original": "the",
        "canonical": "the",
        "variable_type": "label"
      },
      {
        "original": "make",
        "canonical": "make",
        "variable_type": "label"
      },
      {
        "original": "to",
        "canonical": "to",
        "variable_type": "label"
      }
    ],
    "asset_quality_flags": [],
    "is_usable": true,
    "discard_reason_codes": [],
    "created_at": "2026-03-24T07:48:40Z",
    "updated_at": "2026-03-24T07:48:40Z"
  },
  {
    "asset_id": "asset_747aba5221c5dd6033ef095b",
    "problem_id": "prob_5f474e063b4dedfb7fbad5ae",
    "asset_type": "text",
    "asset_role": "question_text_normalized",
    "source_uri": null,
    "storage_uri": "inline://prob_5f474e063b4dedfb7fbad5ae/question_normalized",
    "file_format": "txt",
    "file_size_bytes": 179,
    "width": null,
    "height": null,
    "sha256": "eb66881190e12bac841b3687c48fdb6aa4651e0ae1e523ad359ce185bcb04be1",
    "perceptual_hash": null,
    "source_text_snapshot": "A jump of a little kangaroo is three times shorter than its mother's. How many jumps should the little kangaroo make to cover the distance equal to 7 jumps of its mother?\n<image1>",
    "normalized_text_snapshot": "A jump of a little kangaroo is three times shorter than its mother's. How many jumps should the little kangaroo make to cover the distance equal to 7 jumps of its mother?\n<image1>",
    "text_completeness_score": 0.7098,
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
        "original": "jump",
        "canonical": "jump",
        "variable_type": "label"
      },
      {
        "original": "of",
        "canonical": "of",
        "variable_type": "label"
      },
      {
        "original": "a",
        "canonical": "a",
        "variable_type": "symbol"
      },
      {
        "original": "is",
        "canonical": "is",
        "variable_type": "label"
      },
      {
        "original": "than",
        "canonical": "than",
        "variable_type": "label"
      },
      {
        "original": "its",
        "canonical": "its",
        "variable_type": "label"
      },
      {
        "original": "s",
        "canonical": "s",
        "variable_type": "symbol"
      },
      {
        "original": "How",
        "canonical": "How",
        "variable_type": "label"
      },
      {
        "original": "many",
        "canonical": "many",
        "variable_type": "label"
      },
      {
        "original": "the",
        "canonical": "the",
        "variable_type": "label"
      },
      {
        "original": "make",
        "canonical": "make",
        "variable_type": "label"
      },
      {
        "original": "to",
        "canonical": "to",
        "variable_type": "label"
      }
    ],
    "asset_quality_flags": [],
    "is_usable": true,
    "discard_reason_codes": [],
    "created_at": "2026-03-24T07:48:40Z",
    "updated_at": "2026-03-24T07:48:40Z"
  },
  {
    "asset_id": "asset_49e3f0de96e56bcd7cbf4e92",
    "problem_id": "prob_5f474e063b4dedfb7fbad5ae",
    "asset_type": "answer",
    "asset_role": "answer_raw",
    "source_uri": "source://mathvision/test/17/answer",
    "storage_uri": "inline://prob_5f474e063b4dedfb7fbad5ae/answer_raw",
    "file_format": "txt",
    "file_size_bytes": 2,
    "width": null,
    "height": null,
    "sha256": "6f4b6612125fb3a0daecd2799dfd6c9c299424fd920f9b308110a2c1fbd8f443",
    "perceptual_hash": null,
    "source_text_snapshot": "21",
    "normalized_text_snapshot": null,
    "text_completeness_score": 1.0,
    "blur_score": null,
    "readability_score": null,
    "noise_score": null,
    "cropped_from_asset_id": null,
    "roi_bbox": null,
    "unit_normalization_map": [],
    "variable_aliases": [],
    "asset_quality_flags": [],
    "is_usable": true,
    "discard_reason_codes": [],
    "created_at": "2026-03-24T07:48:40Z",
    "updated_at": "2026-03-24T07:48:40Z"
  },
  {
    "asset_id": "asset_339058f52c1b41de68933ca6",
    "problem_id": "prob_5f474e063b4dedfb7fbad5ae",
    "asset_type": "answer",
    "asset_role": "answer_normalized",
    "source_uri": null,
    "storage_uri": "inline://prob_5f474e063b4dedfb7fbad5ae/answer_normalized",
    "file_format": "txt",
    "file_size_bytes": 2,
    "width": null,
    "height": null,
    "sha256": "6f4b6612125fb3a0daecd2799dfd6c9c299424fd920f9b308110a2c1fbd8f443",
    "perceptual_hash": null,
    "source_text_snapshot": "21",
    "normalized_text_snapshot": "21",
    "text_completeness_score": 1.0,
    "blur_score": null,
    "readability_score": null,
    "noise_score": null,
    "cropped_from_asset_id": null,
    "roi_bbox": null,
    "unit_normalization_map": [],
    "variable_aliases": [],
    "asset_quality_flags": [],
    "is_usable": true,
    "discard_reason_codes": [],
    "created_at": "2026-03-24T07:48:40Z",
    "updated_at": "2026-03-24T07:48:40Z"
  },
  {
    "asset_id": "asset_1e233ed3003a1d5b5eafb478",
    "problem_id": "prob_5f474e063b4dedfb7fbad5ae",
    "asset_type": "image",
    "asset_role": "primary_image",
    "source_uri": "inline://pil_image",
    "storage_uri": "outputs/user_requested_batch_review/pipeline_runs/run_637ca3432da6ddfb/datasets/mathvision/artifacts/images/prob_5f474e063b4dedfb7fbad5ae_primary.png",
    "file_format": "png",
    "file_size_bytes": 34778,
    "width": 414,
    "height": 182,
    "sha256": "773bfe0f61d9cabc6815958477f79d7fbee97630bcd81a9d5bc0333a02e536e7",
    "perceptual_hash": "fffce0c19999fdff",
    "source_text_snapshot": null,
    "normalized_text_snapshot": null,
    "text_completeness_score": null,
    "blur_score": 3526.8535,
    "readability_score": 0.772,
    "noise_score": 23.5401,
    "cropped_from_asset_id": null,
    "roi_bbox": {
      "x": 24,
      "y": 16,
      "width": 368,
      "height": 143
    },
    "unit_normalization_map": [],
    "variable_aliases": [],
    "asset_quality_flags": [
      "low_resolution"
    ],
    "is_usable": true,
    "discard_reason_codes": [],
    "created_at": "2026-03-24T07:48:40Z",
    "updated_at": "2026-03-24T07:48:40Z"
  },
  {
    "asset_id": "asset_726fe65dc6c11e400eead187",
    "problem_id": "prob_5f474e063b4dedfb7fbad5ae",
    "asset_type": "crop",
    "asset_role": "region_crop",
    "source_uri": null,
    "storage_uri": "outputs/user_requested_batch_review/pipeline_runs/run_637ca3432da6ddfb/datasets/mathvision/artifacts/crops/prob_5f474e063b4dedfb7fbad5ae_primary_roi.png",
    "file_format": "png",
    "file_size_bytes": 33900,
    "width": 368,
    "height": 143,
    "sha256": "2d35d16d961ebe9c1b809cd4db5c6a50d3f2fca901c636072fbd7bcad7397476",
    "perceptual_hash": "fff8e0e119b9f8fc",
    "source_text_snapshot": null,
    "normalized_text_snapshot": null,
    "text_completeness_score": null,
    "blur_score": 3526.8535,
    "readability_score": 0.772,
    "noise_score": 23.5401,
    "cropped_from_asset_id": "asset_1e233ed3003a1d5b5eafb478",
    "roi_bbox": {
      "x": 24,
      "y": 16,
      "width": 368,
      "height": 143
    },
    "asset_quality_flags": [],
    "is_usable": true,
    "discard_reason_codes": [],
    "created_at": "2026-03-24T07:48:40Z",
    "updated_at": "2026-03-24T07:48:40Z"
  },
  {
    "asset_id": "asset_a46478cf747ee37ece10f00d",
    "problem_id": "prob_5f474e063b4dedfb7fbad5ae",
    "asset_type": "text",
    "asset_role": "question_text_open_variant",
    "source_uri": null,
    "storage_uri": "inline://open_2f3dea16a2fce26e8e7d98f2",
    "file_format": "txt",
    "file_size_bytes": 179,
    "width": null,
    "height": null,
    "sha256": "eb66881190e12bac841b3687c48fdb6aa4651e0ae1e523ad359ce185bcb04be1",
    "perceptual_hash": null,
    "source_text_snapshot": "A jump of a little kangaroo is three times shorter than its mother's. How many jumps should the little kangaroo make to cover the distance equal to 7 jumps of its mother?\n<image1>",
    "normalized_text_snapshot": "A jump of a little kangaroo is three times shorter than its mother's. How many jumps should the little kangaroo make to cover the distance equal to 7 jumps of its mother?\n<image1>",
    "text_completeness_score": 0.7098,
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
        "original": "jump",
        "canonical": "jump",
        "variable_type": "label"
      },
      {
        "original": "of",
        "canonical": "of",
        "variable_type": "label"
      },
      {
        "original": "a",
        "canonical": "a",
        "variable_type": "symbol"
      },
      {
        "original": "is",
        "canonical": "is",
        "variable_type": "label"
      },
      {
        "original": "than",
        "canonical": "than",
        "variable_type": "label"
      },
      {
        "original": "its",
        "canonical": "its",
        "variable_type": "label"
      },
      {
        "original": "s",
        "canonical": "s",
        "variable_type": "symbol"
      },
      {
        "original": "How",
        "canonical": "How",
        "variable_type": "label"
      },
      {
        "original": "many",
        "canonical": "many",
        "variable_type": "label"
      },
      {
        "original": "the",
        "canonical": "the",
        "variable_type": "label"
      },
      {
        "original": "make",
        "canonical": "make",
        "variable_type": "label"
      },
      {
        "original": "to",
        "canonical": "to",
        "variable_type": "label"
      }
    ],
    "asset_quality_flags": [],
    "is_usable": true,
    "discard_reason_codes": [],
    "created_at": "2026-03-24T07:48:40Z",
    "updated_at": "2026-03-24T07:48:40Z"
  }
]
```

#### node_records

```json
[
  {
    "node_id": "node_a072e4bd2bc10239d2220380",
    "problem_id": "prob_5f474e063b4dedfb7fbad5ae",
    "node_type": "text_fact",
    "canonical_value": "<image1>",
    "surface_forms": [
      "<image1>"
    ],
    "origin_kind": "text",
    "cognitive_level": "objective",
    "source_refs": [
      "asset_747aba5221c5dd6033ef095b"
    ],
    "evidence_refs": [
      "asset_747aba5221c5dd6033ef095b"
    ],
    "upstream_node_ids": [],
    "value_type": "condition",
    "normalized_value": {
      "text": "<image1>",
      "segment_index": 3,
      "mentions_visual": false,
      "numeric_tokens": [
        "1"
      ],
      "unit_mentions": [
        "g",
        "m"
      ],
      "condition_role": "explicit"
    },
    "unit": "g,m",
    "confidence": 0.92,
    "verifiability": "high",
    "ambiguity_level": "low",
    "is_direct_from_source": true,
    "is_generated_by_system": false,
    "is_reviewed_by_human": false,
    "stage_created": "cleaning",
    "status": "active",
    "version": 1,
    "created_at": "2026-03-24T07:48:40Z",
    "updated_at": "2026-03-24T07:48:40Z"
  },
  {
    "node_id": "node_12f3b5c43cb7833f423930de",
    "problem_id": "prob_5f474e063b4dedfb7fbad5ae",
    "node_type": "target_slot",
    "canonical_value": "<image1>",
    "surface_forms": [
      "<image1>"
    ],
    "origin_kind": "text_structure",
    "cognitive_level": "computed",
    "source_refs": [
      "asset_747aba5221c5dd6033ef095b"
    ],
    "evidence_refs": [
      "asset_747aba5221c5dd6033ef095b"
    ],
    "upstream_node_ids": [],
    "value_type": "numeric",
    "normalized_value": {
      "slot_id": "slot_prob_5f474e063b4dedfb7fbad5ae_1",
      "variant_index": 1,
      "split_role": "single",
      "slot_type": "numeric",
      "target_text": "<image1>",
      "expected_answer_type": "numeric",
      "expected_answer": "21",
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
    "created_at": "2026-03-24T07:48:40Z",
    "updated_at": "2026-03-24T07:48:40Z"
  },
  {
    "node_id": "node_1faf14409d81a07aac3d01aa",
    "problem_id": "prob_5f474e063b4dedfb7fbad5ae",
    "node_type": "answer_claim",
    "canonical_value": "21",
    "surface_forms": [
      "21"
    ],
    "origin_kind": "text",
    "cognitive_level": "objective",
    "source_refs": [
      "asset_339058f52c1b41de68933ca6"
    ],
    "evidence_refs": [
      "asset_339058f52c1b41de68933ca6"
    ],
    "upstream_node_ids": [],
    "value_type": "numeric",
    "normalized_value": {
      "answer": "21"
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
    "created_at": "2026-03-24T07:48:40Z",
    "updated_at": "2026-03-24T07:48:40Z"
  },
  {
    "node_id": "node_37aa0bc5e82f56e9ddfee465",
    "problem_id": "prob_5f474e063b4dedfb7fbad5ae",
    "node_type": "perception_fact",
    "canonical_value": "primary_image::full_canvas::canvas",
    "surface_forms": [
      "canvas"
    ],
    "origin_kind": "vision",
    "cognitive_level": "objective",
    "source_refs": [
      "visual_prob_5f474e063b4dedfb7fbad5ae_1"
    ],
    "evidence_refs": [
      "visual_prob_5f474e063b4dedfb7fbad5ae_1"
    ],
    "upstream_node_ids": [],
    "value_type": "full_canvas",
    "normalized_value": {
      "entity_id": "canvas",
      "entity_type": "full_canvas",
      "bbox": {
        "x": 0,
        "y": 0,
        "width": 414,
        "height": 182
      },
      "salience": 1.0
    },
    "unit": null,
    "confidence": 0.9088,
    "verifiability": "medium",
    "ambiguity_level": "low",
    "is_direct_from_source": false,
    "is_generated_by_system": true,
    "is_reviewed_by_human": false,
    "stage_created": "cleaning",
    "status": "active",
    "version": 1,
    "created_at": "2026-03-24T07:48:40Z",
    "updated_at": "2026-03-24T07:48:40Z"
  },
  {
    "node_id": "node_6f4de98e1cc31fd870ff7e45",
    "problem_id": "prob_5f474e063b4dedfb7fbad5ae",
    "node_type": "perception_fact",
    "canonical_value": "primary_image::content_region::roi",
    "surface_forms": [
      "roi"
    ],
    "origin_kind": "vision",
    "cognitive_level": "objective",
    "source_refs": [
      "visual_prob_5f474e063b4dedfb7fbad5ae_1"
    ],
    "evidence_refs": [
      "visual_prob_5f474e063b4dedfb7fbad5ae_1"
    ],
    "upstream_node_ids": [],
    "value_type": "content_region",
    "normalized_value": {
      "entity_id": "roi",
      "entity_type": "content_region",
      "bbox": {
        "x": 24,
        "y": 16,
        "width": 368,
        "height": 143
      },
      "salience": 0.95
    },
    "unit": null,
    "confidence": 0.9088,
    "verifiability": "medium",
    "ambiguity_level": "low",
    "is_direct_from_source": false,
    "is_generated_by_system": true,
    "is_reviewed_by_human": false,
    "stage_created": "cleaning",
    "status": "active",
    "version": 1,
    "created_at": "2026-03-24T07:48:40Z",
    "updated_at": "2026-03-24T07:48:40Z"
  },
  {
    "node_id": "node_66244d01c3dc135a464c2fdd",
    "problem_id": "prob_5f474e063b4dedfb7fbad5ae",
    "node_type": "perception_fact",
    "canonical_value": "primary_image::subregion::roi_top_left",
    "surface_forms": [
      "roi_top_left"
    ],
    "origin_kind": "vision",
    "cognitive_level": "objective",
    "source_refs": [
      "visual_prob_5f474e063b4dedfb7fbad5ae_1"
    ],
    "evidence_refs": [
      "visual_prob_5f474e063b4dedfb7fbad5ae_1"
    ],
    "upstream_node_ids": [],
    "value_type": "subregion",
    "normalized_value": {
      "entity_id": "roi_top_left",
      "entity_type": "subregion",
      "bbox": {
        "x": 24,
        "y": 16,
        "width": 184,
        "height": 71
      },
      "salience": 0.4418
    },
    "unit": null,
    "confidence": 0.9088,
    "verifiability": "medium",
    "ambiguity_level": "low",
    "is_direct_from_source": false,
    "is_generated_by_system": true,
    "is_reviewed_by_human": false,
    "stage_created": "cleaning",
    "status": "active",
    "version": 1,
    "created_at": "2026-03-24T07:48:40Z",
    "updated_at": "2026-03-24T07:48:40Z"
  },
  {
    "node_id": "node_09cf4d76c3870d301e63b69f",
    "problem_id": "prob_5f474e063b4dedfb7fbad5ae",
    "node_type": "perception_fact",
    "canonical_value": "primary_image::subregion::roi_top_right",
    "surface_forms": [
      "roi_top_right"
    ],
    "origin_kind": "vision",
    "cognitive_level": "objective",
    "source_refs": [
      "visual_prob_5f474e063b4dedfb7fbad5ae_1"
    ],
    "evidence_refs": [
      "visual_prob_5f474e063b4dedfb7fbad5ae_1"
    ],
    "upstream_node_ids": [],
    "value_type": "subregion",
    "normalized_value": {
      "entity_id": "roi_top_right",
      "entity_type": "subregion",
      "bbox": {
        "x": 208,
        "y": 16,
        "width": 184,
        "height": 71
      },
      "salience": 0.8337
    },
    "unit": null,
    "confidence": 0.9088,
    "verifiability": "medium",
    "ambiguity_level": "low",
    "is_direct_from_source": false,
    "is_generated_by_system": true,
    "is_reviewed_by_human": false,
    "stage_created": "cleaning",
    "status": "active",
    "version": 1,
    "created_at": "2026-03-24T07:48:40Z",
    "updated_at": "2026-03-24T07:48:40Z"
  },
  {
    "node_id": "node_54337e6a14913f3620c3a3fc",
    "problem_id": "prob_5f474e063b4dedfb7fbad5ae",
    "node_type": "perception_fact",
    "canonical_value": "primary_image::subregion::roi_bottom_left",
    "surface_forms": [
      "roi_bottom_left"
    ],
    "origin_kind": "vision",
    "cognitive_level": "objective",
    "source_refs": [
      "visual_prob_5f474e063b4dedfb7fbad5ae_1"
    ],
    "evidence_refs": [
      "visual_prob_5f474e063b4dedfb7fbad5ae_1"
    ],
    "upstream_node_ids": [],
    "value_type": "subregion",
    "normalized_value": {
      "entity_id": "roi_bottom_left",
      "entity_type": "subregion",
      "bbox": {
        "x": 24,
        "y": 87,
        "width": 184,
        "height": 72
      },
      "salience": 0.5313
    },
    "unit": null,
    "confidence": 0.9088,
    "verifiability": "medium",
    "ambiguity_level": "low",
    "is_direct_from_source": false,
    "is_generated_by_system": true,
    "is_reviewed_by_human": false,
    "stage_created": "cleaning",
    "status": "active",
    "version": 1,
    "created_at": "2026-03-24T07:48:40Z",
    "updated_at": "2026-03-24T07:48:40Z"
  },
  {
    "node_id": "node_d32b27ea028b74c7c9b85fd8",
    "problem_id": "prob_5f474e063b4dedfb7fbad5ae",
    "node_type": "perception_fact",
    "canonical_value": "primary_image::subregion::roi_bottom_right",
    "surface_forms": [
      "roi_bottom_right"
    ],
    "origin_kind": "vision",
    "cognitive_level": "objective",
    "source_refs": [
      "visual_prob_5f474e063b4dedfb7fbad5ae_1"
    ],
    "evidence_refs": [
      "visual_prob_5f474e063b4dedfb7fbad5ae_1"
    ],
    "upstream_node_ids": [],
    "value_type": "subregion",
    "normalized_value": {
      "entity_id": "roi_bottom_right",
      "entity_type": "subregion",
      "bbox": {
        "x": 208,
        "y": 87,
        "width": 184,
        "height": 72
      },
      "salience": 0.6515
    },
    "unit": null,
    "confidence": 0.9088,
    "verifiability": "medium",
    "ambiguity_level": "low",
    "is_direct_from_source": false,
    "is_generated_by_system": true,
    "is_reviewed_by_human": false,
    "stage_created": "cleaning",
    "status": "active",
    "version": 1,
    "created_at": "2026-03-24T07:48:40Z",
    "updated_at": "2026-03-24T07:48:40Z"
  },
  {
    "node_id": "node_1f6d0d5a1ba857977b2bf29f",
    "problem_id": "prob_5f474e063b4dedfb7fbad5ae",
    "node_type": "text_fact",
    "canonical_value": "A jump of a little kangaroo is three times shorter than its mother's. How many jumps should the little kangaroo make to cover the distance equal to 7 jumps of its mother?\n<image1>",
    "surface_forms": [
      "A jump of a little kangaroo is three times shorter than its mother's. How many jumps should the little kangaroo make to cover the distance equal to 7 jumps of its mother?\n<image1>"
    ],
    "origin_kind": "reasoning",
    "cognitive_level": "computed",
    "source_refs": [
      "asset_a46478cf747ee37ece10f00d"
    ],
    "evidence_refs": [
      "asset_a46478cf747ee37ece10f00d"
    ],
    "upstream_node_ids": [],
    "value_type": "text",
    "normalized_value": {
      "open_variant_id": "open_2f3dea16a2fce26e8e7d98f2",
      "parent_problem_id": "prob_5f474e063b4dedfb7fbad5ae",
      "variant_index": 1,
      "title": "MathVision 开放题",
      "rewritten_question_text": "A jump of a little kangaroo is three times shorter than its mother's. How many jumps should the little kangaroo make to cover the distance equal to 7 jumps of its mother?\n<image1>",
      "expected_answer_type": "numeric",
      "expected_answer": "21",
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
    "created_at": "2026-03-24T07:48:40Z",
    "updated_at": "2026-03-24T07:48:40Z"
  },
  {
    "node_id": "node_1c7d97cd95b8cee16e313a2b",
    "problem_id": "prob_5f474e063b4dedfb7fbad5ae",
    "node_type": "quality_signal",
    "canonical_value": "low_resolution",
    "surface_forms": [
      "low_resolution"
    ],
    "origin_kind": "system_quality",
    "cognitive_level": "computed",
    "source_refs": [],
    "evidence_refs": [],
    "upstream_node_ids": [],
    "value_type": "text",
    "normalized_value": {
      "flag": "low_resolution"
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
    "created_at": "2026-03-24T07:48:40Z",
    "updated_at": "2026-03-24T07:48:40Z"
  },
  {
    "node_id": "node_f8a7586598aa1a8e6cbd2b88",
    "problem_id": "prob_5f474e063b4dedfb7fbad5ae",
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
      "solvability_id": "solv_prob_5f474e063b4dedfb7fbad5ae",
      "problem_id": "prob_5f474e063b4dedfb7fbad5ae",
      "answer_verifiable": true,
      "target_clear": true,
      "rewrite_complete": true,
      "text_sufficient": true,
      "visual_grounding_available": true,
      "reasoning_path_exists": true,
      "path_mode": "multimodal",
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
      "created_at": "2026-03-24T07:48:40Z"
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
    "created_at": "2026-03-24T07:48:40Z",
    "updated_at": "2026-03-24T07:48:40Z"
  },
  {
    "node_id": "node_178078fb6a195f3e8c615cc8",
    "problem_id": "prob_5f474e063b4dedfb7fbad5ae",
    "node_type": "quality_signal",
    "canonical_value": "clean_decision=reject",
    "surface_forms": [
      "reject"
    ],
    "origin_kind": "system_quality",
    "cognitive_level": "computed",
    "source_refs": [],
    "evidence_refs": [],
    "upstream_node_ids": [],
    "value_type": "text",
    "normalized_value": {
      "decision": "reject",
      "reasons": [
        "low_resolution"
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
    "created_at": "2026-03-24T07:48:40Z",
    "updated_at": "2026-03-24T07:48:40Z"
  }
]
```

#### field_audit_records

```json
[
  {
    "audit_id": "audit_e37879d759f65838593c88a0",
    "problem_id": "prob_5f474e063b4dedfb7fbad5ae",
    "record_type": "problem_main_record",
    "field_name": "normalized_question_text",
    "before_value": "A jump of a little kangaroo is three times shorter than its mother's. How many jumps should the little kangaroo make to cover the distance equal to 7 jumps of its mother?\n<image1>",
    "after_value": "A jump of a little kangaroo is three times shorter than its mother's. How many jumps should the little kangaroo make to cover the distance equal to 7 jumps of its mother?\n<image1>",
    "change_type": "text_normalized",
    "trigger": "NormalizationAgent",
    "operator_type": "system",
    "created_at": "2026-03-24T07:48:40Z"
  },
  {
    "audit_id": "audit_ee682d4458701cb12db8197f",
    "problem_id": "prob_5f474e063b4dedfb7fbad5ae",
    "record_type": "problem_main_record",
    "field_name": "normalized_answer_text",
    "before_value": "21",
    "after_value": "21",
    "change_type": "answer_canonicalized",
    "trigger": "NormalizationAgent",
    "operator_type": "system",
    "created_at": "2026-03-24T07:48:40Z"
  },
  {
    "audit_id": "audit_05635802e8056c4e824ac0e3",
    "problem_id": "prob_5f474e063b4dedfb7fbad5ae",
    "record_type": "rewrite_report",
    "field_name": "rewrite_strategy",
    "before_value": null,
    "after_value": "keep_open",
    "change_type": "question_rewritten",
    "trigger": "QuestionRewriteAgent",
    "operator_type": "system",
    "created_at": "2026-03-24T07:48:40Z"
  },
  {
    "audit_id": "audit_178078fb6a195f3e8c615cc8",
    "problem_id": "prob_5f474e063b4dedfb7fbad5ae",
    "record_type": "cleaning_record",
    "field_name": "decision",
    "before_value": null,
    "after_value": "reject",
    "change_type": "gate_decision",
    "trigger": "CleanGateAgent",
    "operator_type": "system",
    "created_at": "2026-03-24T07:48:40Z"
  },
  {
    "audit_id": "audit_771e31a4167a3caf268b8d28",
    "problem_id": "prob_5f474e063b4dedfb7fbad5ae",
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
        "original": "jump",
        "canonical": "jump",
        "variable_type": "label"
      },
      {
        "original": "of",
        "canonical": "of",
        "variable_type": "label"
      },
      {
        "original": "a",
        "canonical": "a",
        "variable_type": "symbol"
      },
      {
        "original": "is",
        "canonical": "is",
        "variable_type": "label"
      },
      {
        "original": "than",
        "canonical": "than",
        "variable_type": "label"
      },
      {
        "original": "its",
        "canonical": "its",
        "variable_type": "label"
      },
      {
        "original": "s",
        "canonical": "s",
        "variable_type": "symbol"
      },
      {
        "original": "How",
        "canonical": "How",
        "variable_type": "label"
      },
      {
        "original": "many",
        "canonical": "many",
        "variable_type": "label"
      },
      {
        "original": "the",
        "canonical": "the",
        "variable_type": "label"
      },
      {
        "original": "make",
        "canonical": "make",
        "variable_type": "label"
      },
      {
        "original": "to",
        "canonical": "to",
        "variable_type": "label"
      }
    ],
    "change_type": "variable_canonicalized",
    "trigger": "NormalizationAgent",
    "operator_type": "system",
    "created_at": "2026-03-24T07:48:40Z"
  }
]
```

#### reject_records

```json
[
  {
    "reject_id": "reject_1e0778a5fdaa41be635d4796",
    "problem_id": "prob_5f474e063b4dedfb7fbad5ae",
    "stage": "cleaning",
    "reject_level": "problem",
    "reject_reason_codes": [
      "low_resolution"
    ],
    "reject_reason_detail": "Question is already open-ended.",
    "blocking_fields": [
      "low_resolution"
    ],
    "evidence_refs": [
      "align_1e0778a5fdaa41be635d4796",
      "solv_prob_5f474e063b4dedfb7fbad5ae"
    ],
    "recoverable": false,
    "recommended_action": "drop",
    "reviewed_by": null,
    "created_at": "2026-03-24T07:48:40Z"
  }
]
```

### 4.1 完整 sample bundle 原文件

- `outputs/user_requested_batch_review/pipeline_runs/run_637ca3432da6ddfb/datasets/mathvision/samples/prob_5f474e063b4dedfb7fbad5ae.json`
