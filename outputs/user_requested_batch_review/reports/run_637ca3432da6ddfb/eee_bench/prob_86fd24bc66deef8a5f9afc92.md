# EEE-Bench / prob_86fd24bc66deef8a5f9afc92

- source_problem_id: `7`
- source_split: `test`
- clean_decision: `pass`
- rewrite_strategy: `blank_open`
- full sample bundle JSON: `outputs/user_requested_batch_review/pipeline_runs/run_637ca3432da6ddfb/datasets/eee_bench/samples/prob_86fd24bc66deef8a5f9afc92.json`

## 1. 原始内容（处理前）

### 1.1 原始快照

```json
{
  "dataset_key": "eee_bench",
  "source_problem_id": "7",
  "source_split": "test",
  "raw_question_text": "Hint: Please answer the question and provide the correct option letter, e.g., A, B, C, D, at the end.\nQuestion: The voltage of the three electrodes of a silicon transistor measured with a multimeter is shown in the figure. It can be determined that the transistor is operating in ( )\nChoices\nA. Amplification state\nB. Cutoff state\nC. Reverse amplification state\nD. Saturation state\n",
  "raw_answer_text": "A",
  "choice_map": {},
  "image_sources": [
    "inline://pil_image"
  ],
  "metadata": {
    "row_index": 7,
    "question_field": "problem",
    "answer_field": "solution",
    "image_field": "image",
    "choice_field": null
  },
  "raw_record": {
    "image": "<PngImageFile size=(384, 384) mode=RGB>",
    "problem": "Hint: Please answer the question and provide the correct option letter, e.g., A, B, C, D, at the end.\nQuestion: The voltage of the three electrodes of a silicon transistor measured with a multimeter is shown in the figure. It can be determined that the transistor is operating in ( )\nChoices\nA. Amplification state\nB. Cutoff state\nC. Reverse amplification state\nD. Saturation state\n",
    "solution": "A"
  }
}
```

### 1.2 原始图片

- （无）

## 2. 处理前后对照

### 2.1 关键字段对照

| 字段 | 处理前 | 处理后 |
| --- | --- | --- |
| question_text | Hint: Please answer the question and provide the correct option letter, e.g., A, B, C, D, at the end. Question: The voltage of the three electrodes of a silicon transistor measured with a multimeter is shown in the figure. It can be determined that the transistor is operating in ( ) Choices A. Amplification state B. Cutoff state C. Reverse amplification state D. Saturation state  | Question: The voltage of the three electrodes of a silicon transistor measured with a multimeter is shown in the figure. It can be determined that the transistor is operating in ( ) Choices A. Amplification state B. Cutoff state C. Reverse amplification state D. Saturation state |
| answer_text | A | A |
| answer_type | - | option |
| image_count | 1 | 1 |
| text_dominant | - | False |
| cleaning_path | - | multimodal_full |
| clean_decision | - | pass |
| alignment_status | - | good |
| solvability_decision_hint | - | pass |
| rewrite_strategy | - | blank_open |

### 2.2 结构化处理后结果

#### problem_main_record

```json
{
  "problem_id": "prob_86fd24bc66deef8a5f9afc92",
  "source_dataset": "EEE-Bench",
  "source_split": "test",
  "source_problem_id": "7",
  "ingest_batch_id": "multidataset-clean_20260324T074830Z",
  "problem_type": "multimodal_reasoning",
  "domain_tags": [
    "电气电子工程领域"
  ],
  "language": "en",
  "raw_question_text": "Hint: Please answer the question and provide the correct option letter, e.g., A, B, C, D, at the end.\nQuestion: The voltage of the three electrodes of a silicon transistor measured with a multimeter is shown in the figure. It can be determined that the transistor is operating in ( )\nChoices\nA. Amplification state\nB. Cutoff state\nC. Reverse amplification state\nD. Saturation state\n",
  "normalized_question_text": "Question: The voltage of the three electrodes of a silicon transistor measured with a multimeter is shown in the figure. It can be determined that the transistor is operating in ( )\nChoices\nA. Amplification state\nB. Cutoff state\nC. Reverse amplification state\nD. Saturation state",
  "raw_answer_text": "A",
  "normalized_answer_text": "A",
  "answer_type": "option",
  "image_count": 1,
  "has_multiple_images": false,
  "requires_image": true,
  "multimodal_strength_score": 0.971,
  "multi_step_score": 0.3697,
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
  "candidate_id": "cand_86fd24bc66deef8a5f9afc92",
  "text_dominant": false,
  "cleaning_path": "multimodal_full",
  "alignment_status": "good",
  "solvability_score": 1.0,
  "solvability_decision_hint": "pass",
  "created_at": "2026-03-24T07:48:44Z",
  "updated_at": "2026-03-24T07:48:44Z",
  "initial_image_dependency_score": 0.9,
  "initial_multi_solution_score": 0.52,
  "initial_verifiability_score": 0.8688,
  "multi_solution_mining_policy": "aggressive"
}
```

#### clean_problem_record

```json
{
  "clean_problem_record_id": "cleanprob_18b594e922bfd47ed4618256",
  "problem_id": "prob_86fd24bc66deef8a5f9afc92",
  "source_dataset": "EEE-Bench",
  "source_problem_id": "7",
  "normalized_question_text": "Question: The voltage of the three electrodes of a silicon transistor measured with a multimeter is shown in the figure. It can be determined that the transistor is operating in ( )\nChoices\nA. Amplification state\nB. Cutoff state\nC. Reverse amplification state\nD. Saturation state",
  "normalized_answer_text": "A",
  "image_count": 1,
  "has_multiple_images": false,
  "requires_image": true,
  "text_dominant": false,
  "cleaning_path": "multimodal_full",
  "question_type": "multiple_choice",
  "open_variant_count": 1,
  "alignment_status": "good",
  "solvability_score": 1.0,
  "solvability_path_mode": "multimodal",
  "clean_decision": "pass",
  "decision_reason_codes": [
    "meets_cleaning_requirements"
  ],
  "created_at": "2026-03-24T07:48:44Z"
}
```

#### normalized_assets

```json
{
  "normalized_assets_id": "nassets_18b594e922bfd47ed4618256",
  "problem_id": "prob_86fd24bc66deef8a5f9afc92",
  "normalized_question_text": "Question: The voltage of the three electrodes of a silicon transistor measured with a multimeter is shown in the figure. It can be determined that the transistor is operating in ( )\nChoices\nA. Amplification state\nB. Cutoff state\nC. Reverse amplification state\nD. Saturation state",
  "normalized_answer_text": "A",
  "question_unit_normalization_map": [],
  "answer_unit_normalization_map": [],
  "variable_aliases": [
    {
      "original": "The",
      "canonical": "The",
      "variable_type": "label"
    },
    {
      "original": "of",
      "canonical": "of",
      "variable_type": "label"
    },
    {
      "original": "the",
      "canonical": "the",
      "variable_type": "label"
    },
    {
      "original": "a",
      "canonical": "a",
      "variable_type": "symbol"
    },
    {
      "original": "with",
      "canonical": "with",
      "variable_type": "label"
    },
    {
      "original": "is",
      "canonical": "is",
      "variable_type": "label"
    },
    {
      "original": "in",
      "canonical": "in",
      "variable_type": "label"
    },
    {
      "original": "It",
      "canonical": "It",
      "variable_type": "label"
    },
    {
      "original": "can",
      "canonical": "can",
      "variable_type": "label"
    },
    {
      "original": "be",
      "canonical": "be",
      "variable_type": "label"
    },
    {
      "original": "that",
      "canonical": "that",
      "variable_type": "label"
    },
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
      "original": "D",
      "canonical": "D",
      "variable_type": "symbol"
    }
  ],
  "sentence_segments": [
    {
      "segment_index": 1,
      "text": "Question: The voltage of the three electrodes of a silicon transistor measured with a multimeter is shown in the figure."
    },
    {
      "segment_index": 2,
      "text": "It can be determined that the transistor is operating in ( )"
    },
    {
      "segment_index": 3,
      "text": "Choices"
    },
    {
      "segment_index": 4,
      "text": "A."
    },
    {
      "segment_index": 5,
      "text": "Amplification state"
    },
    {
      "segment_index": 6,
      "text": "B."
    },
    {
      "segment_index": 7,
      "text": "Cutoff state"
    },
    {
      "segment_index": 8,
      "text": "C."
    },
    {
      "segment_index": 9,
      "text": "Reverse amplification state"
    },
    {
      "segment_index": 10,
      "text": "D."
    },
    {
      "segment_index": 11,
      "text": "Saturation state"
    }
  ],
  "image_regions": [
    {
      "image_index": 1,
      "source_uri": "inline://pil_image",
      "roi_bbox": {
        "x": 6,
        "y": 20,
        "width": 271,
        "height": 329
      },
      "readability_score": 0.7403,
      "contrast_score": 42.536
    }
  ],
  "text_dominant": false,
  "cleaning_path": "multimodal_full",
  "created_at": "2026-03-24T07:48:44Z"
}
```

#### text_structure_record

```json
{
  "text_structure_id": "text_prob_86fd24bc66deef8a5f9afc92",
  "problem_id": "prob_86fd24bc66deef8a5f9afc92",
  "question_type": "multiple_choice",
  "conditions": [
    {
      "text": "Question: The voltage of the three electrodes of a silicon transistor measured with a multimeter is shown in the figure.",
      "segment_index": 1,
      "mentions_visual": true,
      "numeric_tokens": [],
      "unit_mentions": [
        "g",
        "h",
        "m",
        "s"
      ],
      "condition_role": "explicit"
    }
  ],
  "targets": [
    {
      "text": "Amplification state",
      "segment_index": 5,
      "mentions_visual": false,
      "numeric_tokens": [],
      "unit_mentions": [
        "A",
        "m",
        "s"
      ],
      "target_role": "primary"
    },
    {
      "text": "Cutoff state",
      "segment_index": 7,
      "mentions_visual": false,
      "numeric_tokens": [],
      "unit_mentions": [
        "s"
      ],
      "target_role": "primary"
    },
    {
      "text": "Reverse amplification state",
      "segment_index": 9,
      "mentions_visual": false,
      "numeric_tokens": [],
      "unit_mentions": [
        "m",
        "s"
      ],
      "target_role": "primary"
    },
    {
      "text": "Saturation state",
      "segment_index": 11,
      "mentions_visual": false,
      "numeric_tokens": [],
      "unit_mentions": [
        "s"
      ],
      "target_role": "primary"
    }
  ],
  "answer_slots": [
    {
      "slot_id": "slot_prob_86fd24bc66deef8a5f9afc92_1",
      "variant_index": 1,
      "split_role": "single",
      "slot_type": "numeric",
      "target_text": "It can be determined that the transistor is operating in ( )",
      "expected_answer_type": "numeric",
      "expected_answer": "Amplification state",
      "requires_visual_grounding": true
    }
  ],
  "entity_mentions": [
    {
      "mention": "figure",
      "entity_category": "figure",
      "requires_visual_grounding": true
    },
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
      "original": "The",
      "canonical": "The",
      "variable_type": "label"
    },
    {
      "original": "of",
      "canonical": "of",
      "variable_type": "label"
    },
    {
      "original": "the",
      "canonical": "the",
      "variable_type": "label"
    },
    {
      "original": "a",
      "canonical": "a",
      "variable_type": "symbol"
    },
    {
      "original": "with",
      "canonical": "with",
      "variable_type": "label"
    },
    {
      "original": "is",
      "canonical": "is",
      "variable_type": "label"
    },
    {
      "original": "in",
      "canonical": "in",
      "variable_type": "label"
    },
    {
      "original": "It",
      "canonical": "It",
      "variable_type": "label"
    },
    {
      "original": "can",
      "canonical": "can",
      "variable_type": "label"
    },
    {
      "original": "be",
      "canonical": "be",
      "variable_type": "label"
    },
    {
      "original": "that",
      "canonical": "that",
      "variable_type": "label"
    },
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
      "original": "D",
      "canonical": "D",
      "variable_type": "symbol"
    }
  ],
  "unit_mentions": [
    "A",
    "g",
    "h",
    "m",
    "min",
    "s"
  ],
  "sentence_segments": [
    {
      "segment_index": 1,
      "text": "Question: The voltage of the three electrodes of a silicon transistor measured with a multimeter is shown in the figure."
    },
    {
      "segment_index": 2,
      "text": "It can be determined that the transistor is operating in ( )"
    },
    {
      "segment_index": 3,
      "text": "Choices"
    },
    {
      "segment_index": 4,
      "text": "A."
    },
    {
      "segment_index": 5,
      "text": "Amplification state"
    },
    {
      "segment_index": 6,
      "text": "B."
    },
    {
      "segment_index": 7,
      "text": "Cutoff state"
    },
    {
      "segment_index": 8,
      "text": "C."
    },
    {
      "segment_index": 9,
      "text": "Reverse amplification state"
    },
    {
      "segment_index": 10,
      "text": "D."
    },
    {
      "segment_index": 11,
      "text": "Saturation state"
    }
  ],
  "requires_visual_grounding": true,
  "text_structure_status": "complete",
  "parser_confidence": 0.92,
  "created_at": "2026-03-24T07:48:44Z"
}
```

#### visual_structure_records

```json
[
  {
    "visual_structure_id": "visual_prob_86fd24bc66deef8a5f9afc92_1",
    "problem_id": "prob_86fd24bc66deef8a5f9afc92",
    "image_index": 1,
    "image_asset_role": "primary_image",
    "global_attributes": {
      "visual_kind": "circuit_diagram",
      "aspect_ratio": 1.0,
      "dark_pixel_ratio": 0.0498,
      "readability_score": 0.7403,
      "has_roi": true
    },
    "visual_entities": [
      {
        "entity_id": "canvas",
        "entity_type": "full_canvas",
        "bbox": {
          "x": 0,
          "y": 0,
          "width": 384,
          "height": 384
        },
        "salience": 1.0
      },
      {
        "entity_id": "roi",
        "entity_type": "content_region",
        "bbox": {
          "x": 6,
          "y": 20,
          "width": 271,
          "height": 329
        },
        "salience": 0.95
      },
      {
        "entity_id": "roi_top_right",
        "entity_type": "subregion",
        "bbox": {
          "x": 141,
          "y": 20,
          "width": 136,
          "height": 164
        },
        "salience": 0.4581
      },
      {
        "entity_id": "roi_bottom_left",
        "entity_type": "subregion",
        "bbox": {
          "x": 6,
          "y": 184,
          "width": 135,
          "height": 165
        },
        "salience": 0.4046
      },
      {
        "entity_id": "roi_bottom_right",
        "entity_type": "subregion",
        "bbox": {
          "x": 141,
          "y": 184,
          "width": 136,
          "height": 165
        },
        "salience": 0.4902
      }
    ],
    "visual_relations": [
      {
        "source_entity_id": "roi",
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
    "parser_confidence": 0.8961,
    "created_at": "2026-03-24T07:48:44Z"
  }
]
```

#### alignment_record

```json
{
  "alignment_id": "align_18b594e922bfd47ed4618256",
  "problem_id": "prob_86fd24bc66deef8a5f9afc92",
  "image_entity_refs": [
    "visual_prob_86fd24bc66deef8a5f9afc92_1::roi",
    "visual_prob_86fd24bc66deef8a5f9afc92_1::roi_top_right",
    "visual_prob_86fd24bc66deef8a5f9afc92_1::roi_bottom_left",
    "visual_prob_86fd24bc66deef8a5f9afc92_1::roi_bottom_right"
  ],
  "text_span_refs": [
    "asset_prob_86fd24bc66deef8a5f9afc92_question_text_normalized"
  ],
  "alignment_pairs": [
    {
      "text_ref": "figure",
      "image_ref": "visual_prob_86fd24bc66deef8a5f9afc92_1::roi",
      "relation": "grounds_figure",
      "confidence": 0.774
    },
    {
      "text_ref": "A",
      "image_ref": "visual_prob_86fd24bc66deef8a5f9afc92_1::roi",
      "relation": "grounds_label",
      "confidence": 0.774
    },
    {
      "text_ref": "B",
      "image_ref": "visual_prob_86fd24bc66deef8a5f9afc92_1::roi",
      "relation": "grounds_label",
      "confidence": 0.774
    },
    {
      "text_ref": "C",
      "image_ref": "visual_prob_86fd24bc66deef8a5f9afc92_1::roi",
      "relation": "grounds_label",
      "confidence": 0.774
    },
    {
      "text_ref": "D",
      "image_ref": "visual_prob_86fd24bc66deef8a5f9afc92_1::roi",
      "relation": "grounds_label",
      "confidence": 0.774
    },
    {
      "text_ref": "slot_prob_86fd24bc66deef8a5f9afc92_1",
      "image_ref": "visual_prob_86fd24bc66deef8a5f9afc92_1::roi",
      "relation": "slot_grounding",
      "confidence": 0.7771
    }
  ],
  "conflict_pairs": [],
  "coverage_score": 0.9,
  "consistency_score": 0.98,
  "alignment_status": "good",
  "created_at": "2026-03-24T07:48:44Z",
  "cleaning_path": "multimodal_full",
  "text_dominant": false
}
```

#### solvability_report

```json
{
  "solvability_id": "solv_prob_86fd24bc66deef8a5f9afc92",
  "problem_id": "prob_86fd24bc66deef8a5f9afc92",
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
  "created_at": "2026-03-24T07:48:44Z"
}
```

#### cleaning_record

```json
{
  "cleaning_id": "clean_18b594e922bfd47ed4618256",
  "problem_id": "prob_86fd24bc66deef8a5f9afc92",
  "cleaning_version": "v3.0.0",
  "pipeline_run_id": "run_637ca3432da6ddfb",
  "dataset_name": "EEE-Bench",
  "input_asset_ids": [
    "asset_9db7ec578d798fe2b4bd2afd",
    "asset_1dc145316d573be86a396fc1",
    "asset_3a6cc05b46f802fcf1e50b8b",
    "asset_36c897cb4058fc2701393ac5",
    "asset_88ca31e80caa0d4251396692",
    "asset_76813c7b7667c1e0d75398ad",
    "asset_9c9ba22e3bfc238097248360"
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
      "variable_alias_count": 15
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
        "width": 384,
        "height": 384,
        "blur_score": 239.4151,
        "contrast_score": 42.536,
        "noise_score": 17.1402,
        "readability_score": 0.7403,
        "crop_integrity_score": 1.0,
        "roi_bbox": {
          "x": 6,
          "y": 20,
          "width": 271,
          "height": 329
        },
        "perceptual_hash": "f7f7e70f87e7f3f3"
      },
      "passed": true
    }
  ],
  "alignment_summary": {
    "alignment_id": "align_18b594e922bfd47ed4618256",
    "coverage_score": 0.9,
    "consistency_score": 0.98,
    "alignment_status": "good",
    "conflict_count": 0
  },
  "text_structure_summary": {
    "text_structure_id": "text_prob_86fd24bc66deef8a5f9afc92",
    "question_type": "multiple_choice",
    "condition_count": 1,
    "target_count": 4,
    "answer_slot_count": 1,
    "status": "complete"
  },
  "solvability_summary": {
    "solvability_id": "solv_prob_86fd24bc66deef8a5f9afc92",
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
  "clean_score": 0.9192,
  "decision": "pass",
  "decision_reason_codes": [
    "meets_cleaning_requirements"
  ],
  "review_ticket_id": null,
  "operator_type": "system",
  "started_at": "2026-03-24T07:48:44Z",
  "finished_at": "2026-03-24T07:48:44Z",
  "candidate_id": "cand_86fd24bc66deef8a5f9afc92",
  "cleaning_path": "multimodal_full",
  "text_dominant": false
}
```

## 3. 开放化改写前后

### 3.1 改写前

```json
{
  "question_text_before_rewrite": "Question: The voltage of the three electrodes of a silicon transistor measured with a multimeter is shown in the figure. It can be determined that the transistor is operating in ( )\nChoices\nA. Amplification state\nB. Cutoff state\nC. Reverse amplification state\nD. Saturation state",
  "answer_text_before_rewrite": "A",
  "raw_question_text": "Hint: Please answer the question and provide the correct option letter, e.g., A, B, C, D, at the end.\nQuestion: The voltage of the three electrodes of a silicon transistor measured with a multimeter is shown in the figure. It can be determined that the transistor is operating in ( )\nChoices\nA. Amplification state\nB. Cutoff state\nC. Reverse amplification state\nD. Saturation state\n",
  "raw_answer_text": "A"
}
```

### 3.2 改写后

```json
{
  "rewrite_report": {
    "rewrite_id": "rewrite_18b594e922bfd47ed4618256",
    "problem_id": "prob_86fd24bc66deef8a5f9afc92",
    "source_problem_id": "7",
    "strategy": "blank_open",
    "rationale": "Converted multiple choice into blank-style open-ended question.",
    "discard_reason_codes": [],
    "variant_count": 1,
    "variants": [
      {
        "open_variant_id": "open_8dcc411fa71586308e937522",
        "parent_problem_id": "prob_86fd24bc66deef8a5f9afc92",
        "variant_index": 1,
        "title": "EEE-Bench 开放题",
        "rewritten_question_text": "Question: The voltage of the three electrodes of a silicon transistor measured with a multimeter is shown in the figure. It can be determined that the transistor is operating in ( )",
        "expected_answer_type": "numeric",
        "expected_answer": "Amplification state",
        "split_role": "single"
      }
    ],
    "created_at": "2026-03-24T07:48:44Z"
  },
  "open_ended_problem_variants": [
    {
      "open_variant_id": "open_8dcc411fa71586308e937522",
      "parent_problem_id": "prob_86fd24bc66deef8a5f9afc92",
      "variant_index": 1,
      "title": "EEE-Bench 开放题",
      "rewritten_question_text": "Question: The voltage of the three electrodes of a silicon transistor measured with a multimeter is shown in the figure. It can be determined that the transistor is operating in ( )",
      "expected_answer_type": "numeric",
      "expected_answer": "Amplification state",
      "split_role": "single"
    }
  ]
}
```

## 4. 完整 collection + cleaning 输出对象

#### candidate_problem_record

```json
{
  "candidate_id": "cand_86fd24bc66deef8a5f9afc92",
  "source_dataset": "EEE-Bench",
  "source_split": "test",
  "source_problem_id": "7",
  "subject": "电气电子工程领域",
  "raw_question_text": "Hint: Please answer the question and provide the correct option letter, e.g., A, B, C, D, at the end.\nQuestion: The voltage of the three electrodes of a silicon transistor measured with a multimeter is shown in the figure. It can be determined that the transistor is operating in ( )\nChoices\nA. Amplification state\nB. Cutoff state\nC. Reverse amplification state\nD. Saturation state\n",
  "raw_answer_text": "A",
  "has_image": true,
  "image_count": 1,
  "requires_image": true,
  "text_dominant": false,
  "recommended_cleaning_path": "multimodal_full",
  "initial_image_dependency_score": 0.9,
  "initial_multi_solution_score": 0.52,
  "initial_verifiability_score": 0.8688,
  "multi_solution_mining_policy": "aggressive",
  "should_push_multi_solution_agent": true,
  "multi_solution_policy_rationale": "该数据集被视为具备较稳定的多解潜力，可进入更强的多解挖掘链路。",
  "metadata": {
    "row_index": 7,
    "question_field": "problem",
    "answer_field": "solution",
    "image_field": "image",
    "choice_field": null
  },
  "created_at": "2026-03-24T07:48:44Z"
}
```

#### raw_asset_bundle

```json
{
  "raw_asset_bundle_id": "bundle_8b39d6e94f564742ac02bd5c",
  "candidate_id": "cand_86fd24bc66deef8a5f9afc92",
  "source_dataset": "EEE-Bench",
  "source_problem_id": "7",
  "assets": [
    {
      "asset_role": "question_text_raw",
      "storage_uri": "inline://prob_86fd24bc66deef8a5f9afc92/question_source",
      "is_present": true
    },
    {
      "asset_role": "answer_text_raw",
      "storage_uri": "inline://prob_86fd24bc66deef8a5f9afc92/answer_source",
      "is_present": true
    },
    {
      "asset_role": "image_raw",
      "storage_uri": "inline://pil_image",
      "is_present": true,
      "width": 384,
      "height": 384
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
    "initial_multi_solution_score": 0.52,
    "initial_verifiability_score": 0.8688
  },
  "created_at": "2026-03-24T07:48:44Z"
}
```

#### candidate_pool_entry

```json
{
  "candidate_pool_entry_id": "cpool_afbef14543dcf4e6d8b1cafd",
  "candidate_id": "cand_86fd24bc66deef8a5f9afc92",
  "source_dataset": "EEE-Bench",
  "source_problem_id": "7",
  "candidate_status": "ready_for_cleaning",
  "priority_score": 0.7766,
  "priority_tier": "high",
  "recommended_cleaning_path": "multimodal_full",
  "multi_solution_mining_policy": "aggressive",
  "initial_scores": {
    "initial_image_dependency_score": 0.9,
    "initial_multi_solution_score": 0.52,
    "initial_verifiability_score": 0.8688
  },
  "created_at": "2026-03-24T07:48:44Z"
}
```

#### clean_pool_entries

```json
[
  {
    "clean_pool_entry_id": "cleanpool_18b594e922bfd47ed4618256",
    "candidate_id": "cand_86fd24bc66deef8a5f9afc92",
    "problem_id": "prob_86fd24bc66deef8a5f9afc92",
    "dataset_name": "EEE-Bench",
    "pool_status": "ready_for_annotation",
    "clean_decision": "pass",
    "review_required": false,
    "rewrite_strategy": "blank_open",
    "open_variant_count": 1,
    "text_dominant": false,
    "cleaning_path": "multimodal_full",
    "created_at": "2026-03-24T07:48:44Z"
  }
]
```

#### rewrite_reports

```json
[
  {
    "rewrite_id": "rewrite_18b594e922bfd47ed4618256",
    "problem_id": "prob_86fd24bc66deef8a5f9afc92",
    "source_problem_id": "7",
    "strategy": "blank_open",
    "rationale": "Converted multiple choice into blank-style open-ended question.",
    "discard_reason_codes": [],
    "variant_count": 1,
    "variants": [
      {
        "open_variant_id": "open_8dcc411fa71586308e937522",
        "parent_problem_id": "prob_86fd24bc66deef8a5f9afc92",
        "variant_index": 1,
        "title": "EEE-Bench 开放题",
        "rewritten_question_text": "Question: The voltage of the three electrodes of a silicon transistor measured with a multimeter is shown in the figure. It can be determined that the transistor is operating in ( )",
        "expected_answer_type": "numeric",
        "expected_answer": "Amplification state",
        "split_role": "single"
      }
    ],
    "created_at": "2026-03-24T07:48:44Z"
  }
]
```

#### open_ended_problem_variants

```json
[
  {
    "open_variant_id": "open_8dcc411fa71586308e937522",
    "parent_problem_id": "prob_86fd24bc66deef8a5f9afc92",
    "variant_index": 1,
    "title": "EEE-Bench 开放题",
    "rewritten_question_text": "Question: The voltage of the three electrodes of a silicon transistor measured with a multimeter is shown in the figure. It can be determined that the transistor is operating in ( )",
    "expected_answer_type": "numeric",
    "expected_answer": "Amplification state",
    "split_role": "single"
  }
]
```

#### asset_records

```json
[
  {
    "asset_id": "asset_9db7ec578d798fe2b4bd2afd",
    "problem_id": "prob_86fd24bc66deef8a5f9afc92",
    "asset_type": "text",
    "asset_role": "question_text_source",
    "source_uri": "source://eee_bench/test/7/question",
    "storage_uri": "inline://prob_86fd24bc66deef8a5f9afc92/question_source",
    "file_format": "txt",
    "file_size_bytes": 382,
    "width": null,
    "height": null,
    "sha256": "f76f30e2b0f5b470fc55f11484644274b0becc04d11d0dd8bf9c9573a3c732d4",
    "perceptual_hash": null,
    "source_text_snapshot": "Hint: Please answer the question and provide the correct option letter, e.g., A, B, C, D, at the end.\nQuestion: The voltage of the three electrodes of a silicon transistor measured with a multimeter is shown in the figure. It can be determined that the transistor is operating in ( )\nChoices\nA. Amplification state\nB. Cutoff state\nC. Reverse amplification state\nD. Saturation state\n",
    "normalized_text_snapshot": null,
    "text_completeness_score": 0.8991,
    "blur_score": null,
    "readability_score": null,
    "noise_score": null,
    "cropped_from_asset_id": null,
    "roi_bbox": null,
    "unit_normalization_map": [],
    "variable_aliases": [
      {
        "original": "The",
        "canonical": "The",
        "variable_type": "label"
      },
      {
        "original": "of",
        "canonical": "of",
        "variable_type": "label"
      },
      {
        "original": "the",
        "canonical": "the",
        "variable_type": "label"
      },
      {
        "original": "a",
        "canonical": "a",
        "variable_type": "symbol"
      },
      {
        "original": "with",
        "canonical": "with",
        "variable_type": "label"
      },
      {
        "original": "is",
        "canonical": "is",
        "variable_type": "label"
      },
      {
        "original": "in",
        "canonical": "in",
        "variable_type": "label"
      },
      {
        "original": "It",
        "canonical": "It",
        "variable_type": "label"
      },
      {
        "original": "can",
        "canonical": "can",
        "variable_type": "label"
      },
      {
        "original": "be",
        "canonical": "be",
        "variable_type": "label"
      },
      {
        "original": "that",
        "canonical": "that",
        "variable_type": "label"
      },
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
        "original": "D",
        "canonical": "D",
        "variable_type": "symbol"
      }
    ],
    "asset_quality_flags": [],
    "is_usable": true,
    "discard_reason_codes": [],
    "created_at": "2026-03-24T07:48:44Z",
    "updated_at": "2026-03-24T07:48:44Z"
  },
  {
    "asset_id": "asset_1dc145316d573be86a396fc1",
    "problem_id": "prob_86fd24bc66deef8a5f9afc92",
    "asset_type": "text",
    "asset_role": "question_text_normalized",
    "source_uri": null,
    "storage_uri": "inline://prob_86fd24bc66deef8a5f9afc92/question_normalized",
    "file_format": "txt",
    "file_size_bytes": 279,
    "width": null,
    "height": null,
    "sha256": "0533e29832f2a2fdf434233d94e41f23ac9b6b5c24d02559e844907fb5f9fa71",
    "perceptual_hash": null,
    "source_text_snapshot": "Hint: Please answer the question and provide the correct option letter, e.g., A, B, C, D, at the end.\nQuestion: The voltage of the three electrodes of a silicon transistor measured with a multimeter is shown in the figure. It can be determined that the transistor is operating in ( )\nChoices\nA. Amplification state\nB. Cutoff state\nC. Reverse amplification state\nD. Saturation state\n",
    "normalized_text_snapshot": "Question: The voltage of the three electrodes of a silicon transistor measured with a multimeter is shown in the figure. It can be determined that the transistor is operating in ( )\nChoices\nA. Amplification state\nB. Cutoff state\nC. Reverse amplification state\nD. Saturation state",
    "text_completeness_score": 0.8991,
    "blur_score": null,
    "readability_score": null,
    "noise_score": null,
    "cropped_from_asset_id": null,
    "roi_bbox": null,
    "unit_normalization_map": [],
    "variable_aliases": [
      {
        "original": "The",
        "canonical": "The",
        "variable_type": "label"
      },
      {
        "original": "of",
        "canonical": "of",
        "variable_type": "label"
      },
      {
        "original": "the",
        "canonical": "the",
        "variable_type": "label"
      },
      {
        "original": "a",
        "canonical": "a",
        "variable_type": "symbol"
      },
      {
        "original": "with",
        "canonical": "with",
        "variable_type": "label"
      },
      {
        "original": "is",
        "canonical": "is",
        "variable_type": "label"
      },
      {
        "original": "in",
        "canonical": "in",
        "variable_type": "label"
      },
      {
        "original": "It",
        "canonical": "It",
        "variable_type": "label"
      },
      {
        "original": "can",
        "canonical": "can",
        "variable_type": "label"
      },
      {
        "original": "be",
        "canonical": "be",
        "variable_type": "label"
      },
      {
        "original": "that",
        "canonical": "that",
        "variable_type": "label"
      },
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
        "original": "D",
        "canonical": "D",
        "variable_type": "symbol"
      }
    ],
    "asset_quality_flags": [],
    "is_usable": true,
    "discard_reason_codes": [],
    "created_at": "2026-03-24T07:48:44Z",
    "updated_at": "2026-03-24T07:48:44Z"
  },
  {
    "asset_id": "asset_3a6cc05b46f802fcf1e50b8b",
    "problem_id": "prob_86fd24bc66deef8a5f9afc92",
    "asset_type": "answer",
    "asset_role": "answer_raw",
    "source_uri": "source://eee_bench/test/7/answer",
    "storage_uri": "inline://prob_86fd24bc66deef8a5f9afc92/answer_raw",
    "file_format": "txt",
    "file_size_bytes": 1,
    "width": null,
    "height": null,
    "sha256": "559aead08264d5795d3909718cdd05abd49572e84fe55590eef31a88a08fdffd",
    "perceptual_hash": null,
    "source_text_snapshot": "A",
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
        "original": "A",
        "canonical": "A",
        "variable_type": "symbol"
      }
    ],
    "asset_quality_flags": [],
    "is_usable": true,
    "discard_reason_codes": [],
    "created_at": "2026-03-24T07:48:44Z",
    "updated_at": "2026-03-24T07:48:44Z"
  },
  {
    "asset_id": "asset_36c897cb4058fc2701393ac5",
    "problem_id": "prob_86fd24bc66deef8a5f9afc92",
    "asset_type": "answer",
    "asset_role": "answer_normalized",
    "source_uri": null,
    "storage_uri": "inline://prob_86fd24bc66deef8a5f9afc92/answer_normalized",
    "file_format": "txt",
    "file_size_bytes": 1,
    "width": null,
    "height": null,
    "sha256": "559aead08264d5795d3909718cdd05abd49572e84fe55590eef31a88a08fdffd",
    "perceptual_hash": null,
    "source_text_snapshot": "A",
    "normalized_text_snapshot": "A",
    "text_completeness_score": 1.0,
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
      }
    ],
    "asset_quality_flags": [],
    "is_usable": true,
    "discard_reason_codes": [],
    "created_at": "2026-03-24T07:48:44Z",
    "updated_at": "2026-03-24T07:48:44Z"
  },
  {
    "asset_id": "asset_88ca31e80caa0d4251396692",
    "problem_id": "prob_86fd24bc66deef8a5f9afc92",
    "asset_type": "image",
    "asset_role": "primary_image",
    "source_uri": "inline://pil_image",
    "storage_uri": "outputs/user_requested_batch_review/pipeline_runs/run_637ca3432da6ddfb/datasets/eee_bench/artifacts/images/prob_86fd24bc66deef8a5f9afc92_primary.png",
    "file_format": "png",
    "file_size_bytes": 23575,
    "width": 384,
    "height": 384,
    "sha256": "b0fe713d338f3aa290128f1ff16a257ffeea11957dd6764b8cc5606c3d4609a7",
    "perceptual_hash": "f7f7e70f87e7f3f3",
    "source_text_snapshot": null,
    "normalized_text_snapshot": null,
    "text_completeness_score": null,
    "blur_score": 239.4151,
    "readability_score": 0.7403,
    "noise_score": 17.1402,
    "cropped_from_asset_id": null,
    "roi_bbox": {
      "x": 6,
      "y": 20,
      "width": 271,
      "height": 329
    },
    "unit_normalization_map": [],
    "variable_aliases": [],
    "asset_quality_flags": [],
    "is_usable": true,
    "discard_reason_codes": [],
    "created_at": "2026-03-24T07:48:44Z",
    "updated_at": "2026-03-24T07:48:44Z"
  },
  {
    "asset_id": "asset_76813c7b7667c1e0d75398ad",
    "problem_id": "prob_86fd24bc66deef8a5f9afc92",
    "asset_type": "crop",
    "asset_role": "region_crop",
    "source_uri": null,
    "storage_uri": "outputs/user_requested_batch_review/pipeline_runs/run_637ca3432da6ddfb/datasets/eee_bench/artifacts/crops/prob_86fd24bc66deef8a5f9afc92_primary_roi.png",
    "file_format": "png",
    "file_size_bytes": 21999,
    "width": 271,
    "height": 329,
    "sha256": "8660e9faa1be27d04d827806e10134f89b3ebbbaf2f99549b53face0a794dc54",
    "perceptual_hash": "f9fbfb8383f3fbf8",
    "source_text_snapshot": null,
    "normalized_text_snapshot": null,
    "text_completeness_score": null,
    "blur_score": 239.4151,
    "readability_score": 0.7403,
    "noise_score": 17.1402,
    "cropped_from_asset_id": "asset_88ca31e80caa0d4251396692",
    "roi_bbox": {
      "x": 6,
      "y": 20,
      "width": 271,
      "height": 329
    },
    "asset_quality_flags": [],
    "is_usable": true,
    "discard_reason_codes": [],
    "created_at": "2026-03-24T07:48:44Z",
    "updated_at": "2026-03-24T07:48:44Z"
  },
  {
    "asset_id": "asset_9c9ba22e3bfc238097248360",
    "problem_id": "prob_86fd24bc66deef8a5f9afc92",
    "asset_type": "text",
    "asset_role": "question_text_open_variant",
    "source_uri": null,
    "storage_uri": "inline://open_8dcc411fa71586308e937522",
    "file_format": "txt",
    "file_size_bytes": 181,
    "width": null,
    "height": null,
    "sha256": "ea28bdc313753fa8196be3d498238de45060e7c449eba34712f4dd234175b851",
    "perceptual_hash": null,
    "source_text_snapshot": "Hint: Please answer the question and provide the correct option letter, e.g., A, B, C, D, at the end.\nQuestion: The voltage of the three electrodes of a silicon transistor measured with a multimeter is shown in the figure. It can be determined that the transistor is operating in ( )\nChoices\nA. Amplification state\nB. Cutoff state\nC. Reverse amplification state\nD. Saturation state\n",
    "normalized_text_snapshot": "Question: The voltage of the three electrodes of a silicon transistor measured with a multimeter is shown in the figure. It can be determined that the transistor is operating in ( )",
    "text_completeness_score": 0.8991,
    "blur_score": null,
    "readability_score": null,
    "noise_score": null,
    "cropped_from_asset_id": null,
    "roi_bbox": null,
    "unit_normalization_map": [],
    "variable_aliases": [
      {
        "original": "The",
        "canonical": "The",
        "variable_type": "label"
      },
      {
        "original": "of",
        "canonical": "of",
        "variable_type": "label"
      },
      {
        "original": "the",
        "canonical": "the",
        "variable_type": "label"
      },
      {
        "original": "a",
        "canonical": "a",
        "variable_type": "symbol"
      },
      {
        "original": "with",
        "canonical": "with",
        "variable_type": "label"
      },
      {
        "original": "is",
        "canonical": "is",
        "variable_type": "label"
      },
      {
        "original": "in",
        "canonical": "in",
        "variable_type": "label"
      },
      {
        "original": "It",
        "canonical": "It",
        "variable_type": "label"
      },
      {
        "original": "can",
        "canonical": "can",
        "variable_type": "label"
      },
      {
        "original": "be",
        "canonical": "be",
        "variable_type": "label"
      },
      {
        "original": "that",
        "canonical": "that",
        "variable_type": "label"
      },
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
        "original": "D",
        "canonical": "D",
        "variable_type": "symbol"
      }
    ],
    "asset_quality_flags": [],
    "is_usable": true,
    "discard_reason_codes": [],
    "created_at": "2026-03-24T07:48:44Z",
    "updated_at": "2026-03-24T07:48:44Z"
  }
]
```

#### node_records

```json
[
  {
    "node_id": "node_8e529039d9a8a19e9174c548",
    "problem_id": "prob_86fd24bc66deef8a5f9afc92",
    "node_type": "text_fact",
    "canonical_value": "Question: The voltage of the three electrodes of a silicon transistor measured with a multimeter is shown in the figure.",
    "surface_forms": [
      "Question: The voltage of the three electrodes of a silicon transistor measured with a multimeter is shown in the figure."
    ],
    "origin_kind": "text",
    "cognitive_level": "objective",
    "source_refs": [
      "asset_1dc145316d573be86a396fc1"
    ],
    "evidence_refs": [
      "asset_1dc145316d573be86a396fc1"
    ],
    "upstream_node_ids": [],
    "value_type": "condition",
    "normalized_value": {
      "text": "Question: The voltage of the three electrodes of a silicon transistor measured with a multimeter is shown in the figure.",
      "segment_index": 1,
      "mentions_visual": true,
      "numeric_tokens": [],
      "unit_mentions": [
        "g",
        "h",
        "m",
        "s"
      ],
      "condition_role": "explicit"
    },
    "unit": "g,h,m,s",
    "confidence": 0.92,
    "verifiability": "high",
    "ambiguity_level": "low",
    "is_direct_from_source": true,
    "is_generated_by_system": false,
    "is_reviewed_by_human": false,
    "stage_created": "cleaning",
    "status": "active",
    "version": 1,
    "created_at": "2026-03-24T07:48:44Z",
    "updated_at": "2026-03-24T07:48:44Z"
  },
  {
    "node_id": "node_c71e12daecf7937f8a07b8fc",
    "problem_id": "prob_86fd24bc66deef8a5f9afc92",
    "node_type": "target_slot",
    "canonical_value": "It can be determined that the transistor is operating in ( )",
    "surface_forms": [
      "It can be determined that the transistor is operating in ( )"
    ],
    "origin_kind": "text_structure",
    "cognitive_level": "computed",
    "source_refs": [
      "asset_1dc145316d573be86a396fc1"
    ],
    "evidence_refs": [
      "asset_1dc145316d573be86a396fc1"
    ],
    "upstream_node_ids": [],
    "value_type": "numeric",
    "normalized_value": {
      "slot_id": "slot_prob_86fd24bc66deef8a5f9afc92_1",
      "variant_index": 1,
      "split_role": "single",
      "slot_type": "numeric",
      "target_text": "It can be determined that the transistor is operating in ( )",
      "expected_answer_type": "numeric",
      "expected_answer": "Amplification state",
      "requires_visual_grounding": true
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
    "created_at": "2026-03-24T07:48:44Z",
    "updated_at": "2026-03-24T07:48:44Z"
  },
  {
    "node_id": "node_660e885c49683aad8c7c979b",
    "problem_id": "prob_86fd24bc66deef8a5f9afc92",
    "node_type": "answer_claim",
    "canonical_value": "A",
    "surface_forms": [
      "A"
    ],
    "origin_kind": "text",
    "cognitive_level": "objective",
    "source_refs": [
      "asset_36c897cb4058fc2701393ac5"
    ],
    "evidence_refs": [
      "asset_36c897cb4058fc2701393ac5"
    ],
    "upstream_node_ids": [],
    "value_type": "option",
    "normalized_value": {
      "answer": "A"
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
    "created_at": "2026-03-24T07:48:44Z",
    "updated_at": "2026-03-24T07:48:44Z"
  },
  {
    "node_id": "node_6ce1e23a1740f651525b8e91",
    "problem_id": "prob_86fd24bc66deef8a5f9afc92",
    "node_type": "perception_fact",
    "canonical_value": "primary_image::full_canvas::canvas",
    "surface_forms": [
      "canvas"
    ],
    "origin_kind": "vision",
    "cognitive_level": "objective",
    "source_refs": [
      "visual_prob_86fd24bc66deef8a5f9afc92_1"
    ],
    "evidence_refs": [
      "visual_prob_86fd24bc66deef8a5f9afc92_1"
    ],
    "upstream_node_ids": [],
    "value_type": "full_canvas",
    "normalized_value": {
      "entity_id": "canvas",
      "entity_type": "full_canvas",
      "bbox": {
        "x": 0,
        "y": 0,
        "width": 384,
        "height": 384
      },
      "salience": 1.0
    },
    "unit": null,
    "confidence": 0.8961,
    "verifiability": "medium",
    "ambiguity_level": "low",
    "is_direct_from_source": false,
    "is_generated_by_system": true,
    "is_reviewed_by_human": false,
    "stage_created": "cleaning",
    "status": "active",
    "version": 1,
    "created_at": "2026-03-24T07:48:44Z",
    "updated_at": "2026-03-24T07:48:44Z"
  },
  {
    "node_id": "node_3ad6a22da446744d6669ff0a",
    "problem_id": "prob_86fd24bc66deef8a5f9afc92",
    "node_type": "perception_fact",
    "canonical_value": "primary_image::content_region::roi",
    "surface_forms": [
      "roi"
    ],
    "origin_kind": "vision",
    "cognitive_level": "objective",
    "source_refs": [
      "visual_prob_86fd24bc66deef8a5f9afc92_1"
    ],
    "evidence_refs": [
      "visual_prob_86fd24bc66deef8a5f9afc92_1"
    ],
    "upstream_node_ids": [],
    "value_type": "content_region",
    "normalized_value": {
      "entity_id": "roi",
      "entity_type": "content_region",
      "bbox": {
        "x": 6,
        "y": 20,
        "width": 271,
        "height": 329
      },
      "salience": 0.95
    },
    "unit": null,
    "confidence": 0.8961,
    "verifiability": "medium",
    "ambiguity_level": "low",
    "is_direct_from_source": false,
    "is_generated_by_system": true,
    "is_reviewed_by_human": false,
    "stage_created": "cleaning",
    "status": "active",
    "version": 1,
    "created_at": "2026-03-24T07:48:44Z",
    "updated_at": "2026-03-24T07:48:44Z"
  },
  {
    "node_id": "node_7bcfcca9ebf329af1f82f667",
    "problem_id": "prob_86fd24bc66deef8a5f9afc92",
    "node_type": "perception_fact",
    "canonical_value": "primary_image::subregion::roi_top_right",
    "surface_forms": [
      "roi_top_right"
    ],
    "origin_kind": "vision",
    "cognitive_level": "objective",
    "source_refs": [
      "visual_prob_86fd24bc66deef8a5f9afc92_1"
    ],
    "evidence_refs": [
      "visual_prob_86fd24bc66deef8a5f9afc92_1"
    ],
    "upstream_node_ids": [],
    "value_type": "subregion",
    "normalized_value": {
      "entity_id": "roi_top_right",
      "entity_type": "subregion",
      "bbox": {
        "x": 141,
        "y": 20,
        "width": 136,
        "height": 164
      },
      "salience": 0.4581
    },
    "unit": null,
    "confidence": 0.8961,
    "verifiability": "medium",
    "ambiguity_level": "low",
    "is_direct_from_source": false,
    "is_generated_by_system": true,
    "is_reviewed_by_human": false,
    "stage_created": "cleaning",
    "status": "active",
    "version": 1,
    "created_at": "2026-03-24T07:48:44Z",
    "updated_at": "2026-03-24T07:48:44Z"
  },
  {
    "node_id": "node_33823bcdd555189a2a91b321",
    "problem_id": "prob_86fd24bc66deef8a5f9afc92",
    "node_type": "perception_fact",
    "canonical_value": "primary_image::subregion::roi_bottom_left",
    "surface_forms": [
      "roi_bottom_left"
    ],
    "origin_kind": "vision",
    "cognitive_level": "objective",
    "source_refs": [
      "visual_prob_86fd24bc66deef8a5f9afc92_1"
    ],
    "evidence_refs": [
      "visual_prob_86fd24bc66deef8a5f9afc92_1"
    ],
    "upstream_node_ids": [],
    "value_type": "subregion",
    "normalized_value": {
      "entity_id": "roi_bottom_left",
      "entity_type": "subregion",
      "bbox": {
        "x": 6,
        "y": 184,
        "width": 135,
        "height": 165
      },
      "salience": 0.4046
    },
    "unit": null,
    "confidence": 0.8961,
    "verifiability": "medium",
    "ambiguity_level": "low",
    "is_direct_from_source": false,
    "is_generated_by_system": true,
    "is_reviewed_by_human": false,
    "stage_created": "cleaning",
    "status": "active",
    "version": 1,
    "created_at": "2026-03-24T07:48:44Z",
    "updated_at": "2026-03-24T07:48:44Z"
  },
  {
    "node_id": "node_48d4a57ea77250d6daded617",
    "problem_id": "prob_86fd24bc66deef8a5f9afc92",
    "node_type": "perception_fact",
    "canonical_value": "primary_image::subregion::roi_bottom_right",
    "surface_forms": [
      "roi_bottom_right"
    ],
    "origin_kind": "vision",
    "cognitive_level": "objective",
    "source_refs": [
      "visual_prob_86fd24bc66deef8a5f9afc92_1"
    ],
    "evidence_refs": [
      "visual_prob_86fd24bc66deef8a5f9afc92_1"
    ],
    "upstream_node_ids": [],
    "value_type": "subregion",
    "normalized_value": {
      "entity_id": "roi_bottom_right",
      "entity_type": "subregion",
      "bbox": {
        "x": 141,
        "y": 184,
        "width": 136,
        "height": 165
      },
      "salience": 0.4902
    },
    "unit": null,
    "confidence": 0.8961,
    "verifiability": "medium",
    "ambiguity_level": "low",
    "is_direct_from_source": false,
    "is_generated_by_system": true,
    "is_reviewed_by_human": false,
    "stage_created": "cleaning",
    "status": "active",
    "version": 1,
    "created_at": "2026-03-24T07:48:44Z",
    "updated_at": "2026-03-24T07:48:44Z"
  },
  {
    "node_id": "node_6f4e3a013742c9d1d89fd122",
    "problem_id": "prob_86fd24bc66deef8a5f9afc92",
    "node_type": "text_fact",
    "canonical_value": "Question: The voltage of the three electrodes of a silicon transistor measured with a multimeter is shown in the figure. It can be determined that the transistor is operating in ( )",
    "surface_forms": [
      "Question: The voltage of the three electrodes of a silicon transistor measured with a multimeter is shown in the figure. It can be determined that the transistor is operating in ( )"
    ],
    "origin_kind": "reasoning",
    "cognitive_level": "computed",
    "source_refs": [
      "asset_9c9ba22e3bfc238097248360"
    ],
    "evidence_refs": [
      "asset_9c9ba22e3bfc238097248360"
    ],
    "upstream_node_ids": [],
    "value_type": "text",
    "normalized_value": {
      "open_variant_id": "open_8dcc411fa71586308e937522",
      "parent_problem_id": "prob_86fd24bc66deef8a5f9afc92",
      "variant_index": 1,
      "title": "EEE-Bench 开放题",
      "rewritten_question_text": "Question: The voltage of the three electrodes of a silicon transistor measured with a multimeter is shown in the figure. It can be determined that the transistor is operating in ( )",
      "expected_answer_type": "numeric",
      "expected_answer": "Amplification state",
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
    "created_at": "2026-03-24T07:48:44Z",
    "updated_at": "2026-03-24T07:48:44Z"
  },
  {
    "node_id": "node_33954312245b8cf5b7826230",
    "problem_id": "prob_86fd24bc66deef8a5f9afc92",
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
      "solvability_id": "solv_prob_86fd24bc66deef8a5f9afc92",
      "problem_id": "prob_86fd24bc66deef8a5f9afc92",
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
      "created_at": "2026-03-24T07:48:44Z"
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
    "created_at": "2026-03-24T07:48:44Z",
    "updated_at": "2026-03-24T07:48:44Z"
  },
  {
    "node_id": "node_ab1cd9a584985026a2e4a35f",
    "problem_id": "prob_86fd24bc66deef8a5f9afc92",
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
    "created_at": "2026-03-24T07:48:44Z",
    "updated_at": "2026-03-24T07:48:44Z"
  }
]
```

#### field_audit_records

```json
[
  {
    "audit_id": "audit_03162cd9a298cbff977ceb88",
    "problem_id": "prob_86fd24bc66deef8a5f9afc92",
    "record_type": "problem_main_record",
    "field_name": "normalized_question_text",
    "before_value": "Hint: Please answer the question and provide the correct option letter, e.g., A, B, C, D, at the end.\nQuestion: The voltage of the three electrodes of a silicon transistor measured with a multimeter is shown in the figure. It can be determined that the transistor is operating in ( )\nChoices\nA. Amplification state\nB. Cutoff state\nC. Reverse amplification state\nD. Saturation state\n",
    "after_value": "Question: The voltage of the three electrodes of a silicon transistor measured with a multimeter is shown in the figure. It can be determined that the transistor is operating in ( )\nChoices\nA. Amplification state\nB. Cutoff state\nC. Reverse amplification state\nD. Saturation state",
    "change_type": "text_normalized",
    "trigger": "NormalizationAgent",
    "operator_type": "system",
    "created_at": "2026-03-24T07:48:44Z"
  },
  {
    "audit_id": "audit_3dbf74c98bccf9520c000fec",
    "problem_id": "prob_86fd24bc66deef8a5f9afc92",
    "record_type": "problem_main_record",
    "field_name": "normalized_answer_text",
    "before_value": "A",
    "after_value": "A",
    "change_type": "answer_canonicalized",
    "trigger": "NormalizationAgent",
    "operator_type": "system",
    "created_at": "2026-03-24T07:48:44Z"
  },
  {
    "audit_id": "audit_1a42879df6aa30481ced329c",
    "problem_id": "prob_86fd24bc66deef8a5f9afc92",
    "record_type": "rewrite_report",
    "field_name": "rewrite_strategy",
    "before_value": null,
    "after_value": "blank_open",
    "change_type": "question_rewritten",
    "trigger": "QuestionRewriteAgent",
    "operator_type": "system",
    "created_at": "2026-03-24T07:48:44Z"
  },
  {
    "audit_id": "audit_ab1cd9a584985026a2e4a35f",
    "problem_id": "prob_86fd24bc66deef8a5f9afc92",
    "record_type": "cleaning_record",
    "field_name": "decision",
    "before_value": null,
    "after_value": "pass",
    "change_type": "gate_decision",
    "trigger": "CleanGateAgent",
    "operator_type": "system",
    "created_at": "2026-03-24T07:48:44Z"
  },
  {
    "audit_id": "audit_30bc73bcba9907f95f8b6552",
    "problem_id": "prob_86fd24bc66deef8a5f9afc92",
    "record_type": "normalized_assets",
    "field_name": "variable_aliases",
    "before_value": null,
    "after_value": [
      {
        "original": "The",
        "canonical": "The",
        "variable_type": "label"
      },
      {
        "original": "of",
        "canonical": "of",
        "variable_type": "label"
      },
      {
        "original": "the",
        "canonical": "the",
        "variable_type": "label"
      },
      {
        "original": "a",
        "canonical": "a",
        "variable_type": "symbol"
      },
      {
        "original": "with",
        "canonical": "with",
        "variable_type": "label"
      },
      {
        "original": "is",
        "canonical": "is",
        "variable_type": "label"
      },
      {
        "original": "in",
        "canonical": "in",
        "variable_type": "label"
      },
      {
        "original": "It",
        "canonical": "It",
        "variable_type": "label"
      },
      {
        "original": "can",
        "canonical": "can",
        "variable_type": "label"
      },
      {
        "original": "be",
        "canonical": "be",
        "variable_type": "label"
      },
      {
        "original": "that",
        "canonical": "that",
        "variable_type": "label"
      },
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
        "original": "D",
        "canonical": "D",
        "variable_type": "symbol"
      }
    ],
    "change_type": "variable_canonicalized",
    "trigger": "NormalizationAgent",
    "operator_type": "system",
    "created_at": "2026-03-24T07:48:44Z"
  }
]
```

#### reject_records

```json
[]
```

### 4.1 完整 sample bundle 原文件

- `outputs/user_requested_batch_review/pipeline_runs/run_637ca3432da6ddfb/datasets/eee_bench/samples/prob_86fd24bc66deef8a5f9afc92.json`
