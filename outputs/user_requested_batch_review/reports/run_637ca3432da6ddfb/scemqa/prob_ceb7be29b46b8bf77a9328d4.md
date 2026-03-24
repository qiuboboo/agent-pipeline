# SCEMQA / prob_ceb7be29b46b8bf77a9328d4

- source_problem_id: `19`
- source_split: `repo_discovered`
- clean_decision: `reject`
- rewrite_strategy: `keep_open`
- full sample bundle JSON: `outputs/user_requested_batch_review/pipeline_runs/run_637ca3432da6ddfb/datasets/scemqa/samples/prob_ceb7be29b46b8bf77a9328d4.json`

## 1. 原始内容（处理前）

### 1.1 原始快照

```json
{
  "dataset_key": "scemqa",
  "source_problem_id": "19",
  "source_split": "repo_discovered",
  "raw_question_text": "In a recent survey taken about the major channels on TV, it was found that channels 2, 3, 4, and 5 captured 30%, 25%, 20%, and 25% of the audience, respectively. During the first week of the new season, 500 viewers were interviewed. Suppose that the actual observed numbers are as follows. Are the differences significant? (Yes or No)",
  "raw_answer_text": "\\answer{No} We note that the expected values (150,125,100,125) are all > 5.\n\nH0: The TV audience is distributed over Channels 2, 3, 4, and 5 with percentages 30%, 25%, 20%, and 25%, respectively.\n\nHa: the audience distribution is not 30%, 25, 20%, and 25%, respectively\n\nWe calculate the chi-square = 5.167. To use the chi-square at a 10% significance level with df = 3, the critical chi-square-value is 6.25. Since 5.167 < 6.25, there is not significant evidence to reject H0.",
  "choice_map": {},
  "image_sources": [
    "outputs/repo_cache/scemqa/Free_Response/Math_Free_Response/14.jpg"
  ],
  "metadata": {
    "data_file": "outputs/repo_cache/scemqa/Free_Response/free_response.json",
    "question_field": "Question",
    "answer_field": "Answer (final answer highlighted)",
    "image_field": "ImagePath",
    "choice_field": null
  },
  "raw_record": {
    "Question": "In a recent survey taken about the major channels on TV, it was found that channels 2, 3, 4, and 5 captured 30%, 25%, 20%, and 25% of the audience, respectively. During the first week of the new season, 500 viewers were interviewed. Suppose that the actual observed numbers are as follows. Are the differences significant? (Yes or No)",
    "Answer (final answer highlighted)": "\\answer{No} We note that the expected values (150,125,100,125) are all > 5.\n\nH0: The TV audience is distributed over Channels 2, 3, 4, and 5 with percentages 30%, 25%, 20%, and 25%, respectively.\n\nHa: the audience distribution is not 30%, 25, 20%, and 25%, respectively\n\nWe calculate the chi-square = 5.167. To use the chi-square at a 10% significance level with df = 3, the critical chi-square-value is 6.25. Since 5.167 < 6.25, there is not significant evidence to reject H0.",
    "ImagePath": "Math_Free_Response/14",
    "category": "Math_Free_Response"
  }
}
```

### 1.2 原始图片

- [`14.jpg`](outputs/repo_cache/scemqa/Free_Response/Math_Free_Response/14.jpg)

## 2. 处理前后对照

### 2.1 关键字段对照

| 字段 | 处理前 | 处理后 |
| --- | --- | --- |
| question_text | In a recent survey taken about the major channels on TV, it was found that channels 2, 3, 4, and 5 captured 30%, 25%, 20%, and 25% of the audience, respectively. During the first week of the new season, 500 viewers were interviewed. Suppose that the actual observed numbers are as follows. Are the differences significant? (Yes or No) | In a recent survey taken about the major channels on TV, it was found that channels 2, 3, 4, and 5 captured 30%, 25%, 20%, and 25% of the audience, respectively. During the first week of the new season, 500 viewers were interviewed. Suppose that the actual observed numbers are as follows. Are the differences significant? (Yes or No) |
| answer_text | \answer{No} We note that the expected values (150,125,100,125) are all > 5.  H0: The TV audience is distributed over Channels 2, 3, 4, and 5 with percentages 30%, 25%, 20%, and 25%, respectively.  Ha: the audience distribution is not 30%, 25, 20%, and 25%, respectively  We calculate the chi-square = 5.167. To use the chi-square at a 10% significance level with df = 3, the critical chi-square-value is 6.25. Since 5.167 < 6.25, there is not significant evidence to reject H0. | \answer{No} We note that the expected values (150,125,100,125) are all > 5.  H0: The TV audience is distributed over Channels 2, 3, 4, and 5 with percentages 30%, 25%, 20%, and 25%, respectively.  Ha: the audience distribution is not 30%, 25, 20%, and 25%, respectively  We calculate the chi-square = 5.167. To use the chi-square at a 10% significance level with df = 3, the critical chi-square-value is 6.25. Since 5.167 < 6.25, there is not significant evidence to reject H0 |
| answer_type | - | set |
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
  "problem_id": "prob_ceb7be29b46b8bf77a9328d4",
  "source_dataset": "SCEMQA",
  "source_split": "repo_discovered",
  "source_problem_id": "19",
  "ingest_batch_id": "multidataset-clean_20260324T074830Z",
  "problem_type": "multimodal_reasoning",
  "domain_tags": [
    "数学、物理、生物、化学"
  ],
  "language": "en",
  "raw_question_text": "In a recent survey taken about the major channels on TV, it was found that channels 2, 3, 4, and 5 captured 30%, 25%, 20%, and 25% of the audience, respectively. During the first week of the new season, 500 viewers were interviewed. Suppose that the actual observed numbers are as follows. Are the differences significant? (Yes or No)",
  "normalized_question_text": "In a recent survey taken about the major channels on TV, it was found that channels 2, 3, 4, and 5 captured 30%, 25%, 20%, and 25% of the audience, respectively. During the first week of the new season, 500 viewers were interviewed. Suppose that the actual observed numbers are as follows. Are the differences significant? (Yes or No)",
  "raw_answer_text": "\\answer{No} We note that the expected values (150,125,100,125) are all > 5.\n\nH0: The TV audience is distributed over Channels 2, 3, 4, and 5 with percentages 30%, 25%, 20%, and 25%, respectively.\n\nHa: the audience distribution is not 30%, 25, 20%, and 25%, respectively\n\nWe calculate the chi-square = 5.167. To use the chi-square at a 10% significance level with df = 3, the critical chi-square-value is 6.25. Since 5.167 < 6.25, there is not significant evidence to reject H0.",
  "normalized_answer_text": "\\answer{No} We note that the expected values (150,125,100,125) are all > 5.\n\nH0: The TV audience is distributed over Channels 2, 3, 4, and 5 with percentages 30%, 25%, 20%, and 25%, respectively.\n\nHa: the audience distribution is not 30%, 25, 20%, and 25%, respectively\n\nWe calculate the chi-square = 5.167. To use the chi-square at a 10% significance level with df = 3, the critical chi-square-value is 6.25. Since 5.167 < 6.25, there is not significant evidence to reject H0",
  "answer_type": "set",
  "image_count": 1,
  "has_multiple_images": false,
  "requires_image": true,
  "multimodal_strength_score": 0.9506,
  "multi_step_score": 0.3647,
  "verifiability_score": 0.986,
  "quality_risk_flags": [
    "low_resolution",
    "severe_crop_loss"
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
  "candidate_id": "cand_ceb7be29b46b8bf77a9328d4",
  "text_dominant": false,
  "cleaning_path": "multimodal_full",
  "alignment_status": "good",
  "solvability_score": 1.0,
  "solvability_decision_hint": "pass",
  "created_at": "2026-03-24T07:48:30Z",
  "updated_at": "2026-03-24T07:48:30Z",
  "initial_image_dependency_score": 0.9,
  "initial_multi_solution_score": 0.18,
  "initial_verifiability_score": 0.6987,
  "multi_solution_mining_policy": "conservative"
}
```

#### clean_problem_record

```json
{
  "clean_problem_record_id": "cleanprob_812a3fe7191f5a31abcda0a1",
  "problem_id": "prob_ceb7be29b46b8bf77a9328d4",
  "source_dataset": "SCEMQA",
  "source_problem_id": "19",
  "normalized_question_text": "In a recent survey taken about the major channels on TV, it was found that channels 2, 3, 4, and 5 captured 30%, 25%, 20%, and 25% of the audience, respectively. During the first week of the new season, 500 viewers were interviewed. Suppose that the actual observed numbers are as follows. Are the differences significant? (Yes or No)",
  "normalized_answer_text": "\\answer{No} We note that the expected values (150,125,100,125) are all > 5.\n\nH0: The TV audience is distributed over Channels 2, 3, 4, and 5 with percentages 30%, 25%, 20%, and 25%, respectively.\n\nHa: the audience distribution is not 30%, 25, 20%, and 25%, respectively\n\nWe calculate the chi-square = 5.167. To use the chi-square at a 10% significance level with df = 3, the critical chi-square-value is 6.25. Since 5.167 < 6.25, there is not significant evidence to reject H0",
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
  "created_at": "2026-03-24T07:48:30Z"
}
```

#### normalized_assets

```json
{
  "normalized_assets_id": "nassets_812a3fe7191f5a31abcda0a1",
  "problem_id": "prob_ceb7be29b46b8bf77a9328d4",
  "normalized_question_text": "In a recent survey taken about the major channels on TV, it was found that channels 2, 3, 4, and 5 captured 30%, 25%, 20%, and 25% of the audience, respectively. During the first week of the new season, 500 viewers were interviewed. Suppose that the actual observed numbers are as follows. Are the differences significant? (Yes or No)",
  "normalized_answer_text": "\\answer{No} We note that the expected values (150,125,100,125) are all > 5.\n\nH0: The TV audience is distributed over Channels 2, 3, 4, and 5 with percentages 30%, 25%, 20%, and 25%, respectively.\n\nHa: the audience distribution is not 30%, 25, 20%, and 25%, respectively\n\nWe calculate the chi-square = 5.167. To use the chi-square at a 10% significance level with df = 3, the critical chi-square-value is 6.25. Since 5.167 < 6.25, there is not significant evidence to reject H0",
  "question_unit_normalization_map": [],
  "answer_unit_normalization_map": [],
  "variable_aliases": [
    {
      "original": "In",
      "canonical": "In",
      "variable_type": "label"
    },
    {
      "original": "a",
      "canonical": "a",
      "variable_type": "symbol"
    },
    {
      "original": "the",
      "canonical": "the",
      "variable_type": "label"
    },
    {
      "original": "on",
      "canonical": "on",
      "variable_type": "label"
    },
    {
      "original": "TV",
      "canonical": "TV",
      "variable_type": "label"
    },
    {
      "original": "it",
      "canonical": "it",
      "variable_type": "label"
    },
    {
      "original": "was",
      "canonical": "was",
      "variable_type": "label"
    },
    {
      "original": "that",
      "canonical": "that",
      "variable_type": "label"
    },
    {
      "original": "and",
      "canonical": "and",
      "variable_type": "label"
    },
    {
      "original": "of",
      "canonical": "of",
      "variable_type": "label"
    },
    {
      "original": "week",
      "canonical": "week",
      "variable_type": "label"
    },
    {
      "original": "new",
      "canonical": "new",
      "variable_type": "label"
    },
    {
      "original": "were",
      "canonical": "were",
      "variable_type": "label"
    },
    {
      "original": "are",
      "canonical": "are",
      "variable_type": "label"
    },
    {
      "original": "as",
      "canonical": "as",
      "variable_type": "label"
    },
    {
      "original": "Are",
      "canonical": "Are",
      "variable_type": "label"
    },
    {
      "original": "Yes",
      "canonical": "Yes",
      "variable_type": "label"
    },
    {
      "original": "or",
      "canonical": "or",
      "variable_type": "label"
    },
    {
      "original": "No",
      "canonical": "No",
      "variable_type": "label"
    }
  ],
  "sentence_segments": [
    {
      "segment_index": 1,
      "text": "In a recent survey taken about the major channels on TV, it was found that channels 2, 3, 4, and 5 captured 30%, 25%, 20%, and 25% of the audience, respectively."
    },
    {
      "segment_index": 2,
      "text": "During the first week of the new season, 500 viewers were interviewed."
    },
    {
      "segment_index": 3,
      "text": "Suppose that the actual observed numbers are as follows."
    },
    {
      "segment_index": 4,
      "text": "Are the differences significant?"
    },
    {
      "segment_index": 5,
      "text": "(Yes or No)"
    }
  ],
  "image_regions": [
    {
      "image_index": 1,
      "source_uri": "outputs/repo_cache/scemqa/Free_Response/Math_Free_Response/14.jpg",
      "roi_bbox": {
        "x": 0,
        "y": 0,
        "width": 688,
        "height": 98
      },
      "readability_score": 0.6557,
      "contrast_score": 51.0388
    }
  ],
  "text_dominant": false,
  "cleaning_path": "multimodal_full",
  "created_at": "2026-03-24T07:48:30Z"
}
```

#### text_structure_record

```json
{
  "text_structure_id": "text_prob_ceb7be29b46b8bf77a9328d4",
  "problem_id": "prob_ceb7be29b46b8bf77a9328d4",
  "question_type": "open",
  "conditions": [
    {
      "text": "In a recent survey taken about the major channels on TV, it was found that channels 2, 3, 4, and 5 captured 30%, 25%, 20%, and 25% of the audience, respectively.",
      "segment_index": 1,
      "mentions_visual": false,
      "numeric_tokens": [
        "2",
        "3",
        "4",
        "5",
        "30",
        "25",
        "20",
        "25"
      ],
      "unit_mentions": [
        "V",
        "h",
        "m",
        "s"
      ],
      "condition_role": "explicit"
    },
    {
      "text": "During the first week of the new season, 500 viewers were interviewed.",
      "segment_index": 2,
      "mentions_visual": false,
      "numeric_tokens": [
        "500"
      ],
      "unit_mentions": [
        "g",
        "h",
        "s"
      ],
      "condition_role": "explicit"
    }
  ],
  "targets": [
    {
      "text": "Are the differences significant?",
      "segment_index": 4,
      "mentions_visual": false,
      "numeric_tokens": [],
      "unit_mentions": [
        "A",
        "g",
        "h",
        "s"
      ],
      "target_role": "primary"
    }
  ],
  "answer_slots": [
    {
      "slot_id": "slot_prob_ceb7be29b46b8bf77a9328d4_1",
      "variant_index": 1,
      "split_role": "single",
      "slot_type": "set",
      "target_text": "(Yes or No)",
      "expected_answer_type": "set",
      "expected_answer": "\\answer{No} We note that the expected values (150,125,100,125) are all > 5.\n\nH0: The TV audience is distributed over Channels 2, 3, 4, and 5 with percentages 30%, 25%, 20%, and 25%, respectively.\n\nHa: the audience distribution is not 30%, 25, 20%, and 25%, respectively\n\nWe calculate the chi-square = 5.167. To use the chi-square at a 10% significance level with df = 3, the critical chi-square-value is 6.25. Since 5.167 < 6.25, there is not significant evidence to reject H0",
      "requires_visual_grounding": false
    }
  ],
  "entity_mentions": [
    {
      "mention": "TV",
      "entity_category": "label",
      "requires_visual_grounding": true
    }
  ],
  "variable_aliases": [
    {
      "original": "In",
      "canonical": "In",
      "variable_type": "label"
    },
    {
      "original": "a",
      "canonical": "a",
      "variable_type": "symbol"
    },
    {
      "original": "the",
      "canonical": "the",
      "variable_type": "label"
    },
    {
      "original": "on",
      "canonical": "on",
      "variable_type": "label"
    },
    {
      "original": "TV",
      "canonical": "TV",
      "variable_type": "label"
    },
    {
      "original": "it",
      "canonical": "it",
      "variable_type": "label"
    },
    {
      "original": "was",
      "canonical": "was",
      "variable_type": "label"
    },
    {
      "original": "that",
      "canonical": "that",
      "variable_type": "label"
    },
    {
      "original": "and",
      "canonical": "and",
      "variable_type": "label"
    },
    {
      "original": "of",
      "canonical": "of",
      "variable_type": "label"
    },
    {
      "original": "week",
      "canonical": "week",
      "variable_type": "label"
    },
    {
      "original": "new",
      "canonical": "new",
      "variable_type": "label"
    },
    {
      "original": "were",
      "canonical": "were",
      "variable_type": "label"
    },
    {
      "original": "are",
      "canonical": "are",
      "variable_type": "label"
    },
    {
      "original": "as",
      "canonical": "as",
      "variable_type": "label"
    },
    {
      "original": "Are",
      "canonical": "Are",
      "variable_type": "label"
    },
    {
      "original": "Yes",
      "canonical": "Yes",
      "variable_type": "label"
    },
    {
      "original": "or",
      "canonical": "or",
      "variable_type": "label"
    },
    {
      "original": "No",
      "canonical": "No",
      "variable_type": "label"
    }
  ],
  "unit_mentions": [
    "A",
    "N",
    "V",
    "W",
    "g",
    "h",
    "m",
    "s"
  ],
  "sentence_segments": [
    {
      "segment_index": 1,
      "text": "In a recent survey taken about the major channels on TV, it was found that channels 2, 3, 4, and 5 captured 30%, 25%, 20%, and 25% of the audience, respectively."
    },
    {
      "segment_index": 2,
      "text": "During the first week of the new season, 500 viewers were interviewed."
    },
    {
      "segment_index": 3,
      "text": "Suppose that the actual observed numbers are as follows."
    },
    {
      "segment_index": 4,
      "text": "Are the differences significant?"
    },
    {
      "segment_index": 5,
      "text": "(Yes or No)"
    }
  ],
  "requires_visual_grounding": true,
  "text_structure_status": "complete",
  "parser_confidence": 0.92,
  "created_at": "2026-03-24T07:48:30Z"
}
```

#### visual_structure_records

```json
[
  {
    "visual_structure_id": "visual_prob_ceb7be29b46b8bf77a9328d4_1",
    "problem_id": "prob_ceb7be29b46b8bf77a9328d4",
    "image_index": 1,
    "image_asset_role": "primary_image",
    "global_attributes": {
      "visual_kind": "wide_diagram",
      "aspect_ratio": 7.0204,
      "dark_pixel_ratio": 0.129,
      "readability_score": 0.6557,
      "has_roi": true
    },
    "visual_entities": [
      {
        "entity_id": "canvas",
        "entity_type": "full_canvas",
        "bbox": {
          "x": 0,
          "y": 0,
          "width": 688,
          "height": 98
        },
        "salience": 1.0
      },
      {
        "entity_id": "roi",
        "entity_type": "content_region",
        "bbox": {
          "x": 0,
          "y": 0,
          "width": 688,
          "height": 98
        },
        "salience": 0.95
      },
      {
        "entity_id": "roi_top_left",
        "entity_type": "subregion",
        "bbox": {
          "x": 0,
          "y": 0,
          "width": 344,
          "height": 49
        },
        "salience": 0.4344
      },
      {
        "entity_id": "roi_top_right",
        "entity_type": "subregion",
        "bbox": {
          "x": 344,
          "y": 0,
          "width": 344,
          "height": 49
        },
        "salience": 0.4705
      },
      {
        "entity_id": "roi_bottom_left",
        "entity_type": "subregion",
        "bbox": {
          "x": 0,
          "y": 49,
          "width": 344,
          "height": 49
        },
        "salience": 0.5219
      },
      {
        "entity_id": "roi_bottom_right",
        "entity_type": "subregion",
        "bbox": {
          "x": 344,
          "y": 49,
          "width": 344,
          "height": 49
        },
        "salience": 0.4891
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
    "parser_confidence": 0.8623,
    "created_at": "2026-03-24T07:48:30Z"
  }
]
```

#### alignment_record

```json
{
  "alignment_id": "align_812a3fe7191f5a31abcda0a1",
  "problem_id": "prob_ceb7be29b46b8bf77a9328d4",
  "image_entity_refs": [
    "visual_prob_ceb7be29b46b8bf77a9328d4_1::roi",
    "visual_prob_ceb7be29b46b8bf77a9328d4_1::roi_top_left",
    "visual_prob_ceb7be29b46b8bf77a9328d4_1::roi_top_right",
    "visual_prob_ceb7be29b46b8bf77a9328d4_1::roi_bottom_left",
    "visual_prob_ceb7be29b46b8bf77a9328d4_1::roi_bottom_right"
  ],
  "text_span_refs": [
    "asset_prob_ceb7be29b46b8bf77a9328d4_question_text_normalized"
  ],
  "alignment_pairs": [
    {
      "text_ref": "TV",
      "image_ref": "visual_prob_ceb7be29b46b8bf77a9328d4_1::roi",
      "relation": "grounds_label",
      "confidence": 0.7656
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
  "created_at": "2026-03-24T07:48:30Z",
  "cleaning_path": "multimodal_full",
  "text_dominant": false
}
```

#### solvability_report

```json
{
  "solvability_id": "solv_prob_ceb7be29b46b8bf77a9328d4",
  "problem_id": "prob_ceb7be29b46b8bf77a9328d4",
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
  "created_at": "2026-03-24T07:48:30Z"
}
```

#### cleaning_record

```json
{
  "cleaning_id": "clean_812a3fe7191f5a31abcda0a1",
  "problem_id": "prob_ceb7be29b46b8bf77a9328d4",
  "cleaning_version": "v3.0.0",
  "pipeline_run_id": "run_637ca3432da6ddfb",
  "dataset_name": "SCEMQA",
  "input_asset_ids": [
    "asset_0091388d43b7b8d4e86032ba",
    "asset_44c3a2a8295c666b3dd2caeb",
    "asset_ecdf09acec71695bfd3da086",
    "asset_d26b7576256b1d993bb3c818",
    "asset_68607c7e4bdc12fa5c17a0ef",
    "asset_4bf02841d0ccf37c552851a4"
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
      "variable_alias_count": 19
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
        "width": 688,
        "height": 98,
        "blur_score": 5957.6152,
        "contrast_score": 51.0388,
        "noise_score": 41.146,
        "readability_score": 0.6557,
        "crop_integrity_score": 0.12,
        "roi_bbox": {
          "x": 0,
          "y": 0,
          "width": 688,
          "height": 98
        },
        "perceptual_hash": "00fb00ffff003f00"
      },
      "passed": true
    }
  ],
  "alignment_summary": {
    "alignment_id": "align_812a3fe7191f5a31abcda0a1",
    "coverage_score": 0.9,
    "consistency_score": 0.9,
    "alignment_status": "good",
    "conflict_count": 1
  },
  "text_structure_summary": {
    "text_structure_id": "text_prob_ceb7be29b46b8bf77a9328d4",
    "question_type": "open",
    "condition_count": 2,
    "target_count": 1,
    "answer_slot_count": 1,
    "status": "complete"
  },
  "solvability_summary": {
    "solvability_id": "solv_prob_ceb7be29b46b8bf77a9328d4",
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
    "low_resolution",
    "severe_crop_loss"
  ],
  "clean_score": 0.8745,
  "decision": "reject",
  "decision_reason_codes": [
    "low_resolution"
  ],
  "review_ticket_id": null,
  "operator_type": "system",
  "started_at": "2026-03-24T07:48:30Z",
  "finished_at": "2026-03-24T07:48:30Z",
  "candidate_id": "cand_ceb7be29b46b8bf77a9328d4",
  "cleaning_path": "multimodal_full",
  "text_dominant": false
}
```

## 3. 开放化改写前后

### 3.1 改写前

```json
{
  "question_text_before_rewrite": "In a recent survey taken about the major channels on TV, it was found that channels 2, 3, 4, and 5 captured 30%, 25%, 20%, and 25% of the audience, respectively. During the first week of the new season, 500 viewers were interviewed. Suppose that the actual observed numbers are as follows. Are the differences significant? (Yes or No)",
  "answer_text_before_rewrite": "\\answer{No} We note that the expected values (150,125,100,125) are all > 5.\n\nH0: The TV audience is distributed over Channels 2, 3, 4, and 5 with percentages 30%, 25%, 20%, and 25%, respectively.\n\nHa: the audience distribution is not 30%, 25, 20%, and 25%, respectively\n\nWe calculate the chi-square = 5.167. To use the chi-square at a 10% significance level with df = 3, the critical chi-square-value is 6.25. Since 5.167 < 6.25, there is not significant evidence to reject H0",
  "raw_question_text": "In a recent survey taken about the major channels on TV, it was found that channels 2, 3, 4, and 5 captured 30%, 25%, 20%, and 25% of the audience, respectively. During the first week of the new season, 500 viewers were interviewed. Suppose that the actual observed numbers are as follows. Are the differences significant? (Yes or No)",
  "raw_answer_text": "\\answer{No} We note that the expected values (150,125,100,125) are all > 5.\n\nH0: The TV audience is distributed over Channels 2, 3, 4, and 5 with percentages 30%, 25%, 20%, and 25%, respectively.\n\nHa: the audience distribution is not 30%, 25, 20%, and 25%, respectively\n\nWe calculate the chi-square = 5.167. To use the chi-square at a 10% significance level with df = 3, the critical chi-square-value is 6.25. Since 5.167 < 6.25, there is not significant evidence to reject H0."
}
```

### 3.2 改写后

```json
{
  "rewrite_report": {
    "rewrite_id": "rewrite_812a3fe7191f5a31abcda0a1",
    "problem_id": "prob_ceb7be29b46b8bf77a9328d4",
    "source_problem_id": "19",
    "strategy": "keep_open",
    "rationale": "Question is already open-ended.",
    "discard_reason_codes": [],
    "variant_count": 1,
    "variants": [
      {
        "open_variant_id": "open_c08f8756373b8cbaf21fa68b",
        "parent_problem_id": "prob_ceb7be29b46b8bf77a9328d4",
        "variant_index": 1,
        "title": "SCEMQA 开放题",
        "rewritten_question_text": "In a recent survey taken about the major channels on TV, it was found that channels 2, 3, 4, and 5 captured 30%, 25%, 20%, and 25% of the audience, respectively. During the first week of the new season, 500 viewers were interviewed. Suppose that the actual observed numbers are as follows. Are the differences significant? (Yes or No)",
        "expected_answer_type": "set",
        "expected_answer": "\\answer{No} We note that the expected values (150,125,100,125) are all > 5.\n\nH0: The TV audience is distributed over Channels 2, 3, 4, and 5 with percentages 30%, 25%, 20%, and 25%, respectively.\n\nHa: the audience distribution is not 30%, 25, 20%, and 25%, respectively\n\nWe calculate the chi-square = 5.167. To use the chi-square at a 10% significance level with df = 3, the critical chi-square-value is 6.25. Since 5.167 < 6.25, there is not significant evidence to reject H0",
        "split_role": "single"
      }
    ],
    "created_at": "2026-03-24T07:48:30Z"
  },
  "open_ended_problem_variants": [
    {
      "open_variant_id": "open_c08f8756373b8cbaf21fa68b",
      "parent_problem_id": "prob_ceb7be29b46b8bf77a9328d4",
      "variant_index": 1,
      "title": "SCEMQA 开放题",
      "rewritten_question_text": "In a recent survey taken about the major channels on TV, it was found that channels 2, 3, 4, and 5 captured 30%, 25%, 20%, and 25% of the audience, respectively. During the first week of the new season, 500 viewers were interviewed. Suppose that the actual observed numbers are as follows. Are the differences significant? (Yes or No)",
      "expected_answer_type": "set",
      "expected_answer": "\\answer{No} We note that the expected values (150,125,100,125) are all > 5.\n\nH0: The TV audience is distributed over Channels 2, 3, 4, and 5 with percentages 30%, 25%, 20%, and 25%, respectively.\n\nHa: the audience distribution is not 30%, 25, 20%, and 25%, respectively\n\nWe calculate the chi-square = 5.167. To use the chi-square at a 10% significance level with df = 3, the critical chi-square-value is 6.25. Since 5.167 < 6.25, there is not significant evidence to reject H0",
      "split_role": "single"
    }
  ]
}
```

## 4. 完整 collection + cleaning 输出对象

#### candidate_problem_record

```json
{
  "candidate_id": "cand_ceb7be29b46b8bf77a9328d4",
  "source_dataset": "SCEMQA",
  "source_split": "repo_discovered",
  "source_problem_id": "19",
  "subject": "数学、物理、生物、化学",
  "raw_question_text": "In a recent survey taken about the major channels on TV, it was found that channels 2, 3, 4, and 5 captured 30%, 25%, 20%, and 25% of the audience, respectively. During the first week of the new season, 500 viewers were interviewed. Suppose that the actual observed numbers are as follows. Are the differences significant? (Yes or No)",
  "raw_answer_text": "\\answer{No} We note that the expected values (150,125,100,125) are all > 5.\n\nH0: The TV audience is distributed over Channels 2, 3, 4, and 5 with percentages 30%, 25%, 20%, and 25%, respectively.\n\nHa: the audience distribution is not 30%, 25, 20%, and 25%, respectively\n\nWe calculate the chi-square = 5.167. To use the chi-square at a 10% significance level with df = 3, the critical chi-square-value is 6.25. Since 5.167 < 6.25, there is not significant evidence to reject H0.",
  "has_image": true,
  "image_count": 1,
  "requires_image": true,
  "text_dominant": false,
  "recommended_cleaning_path": "multimodal_full",
  "initial_image_dependency_score": 0.9,
  "initial_multi_solution_score": 0.18,
  "initial_verifiability_score": 0.6987,
  "multi_solution_mining_policy": "conservative",
  "should_push_multi_solution_agent": false,
  "multi_solution_policy_rationale": "该数据集更可能以单解题为主，不强推多解 agent，只保留基础可验证性与可标注性检查。",
  "metadata": {
    "data_file": "outputs/repo_cache/scemqa/Free_Response/free_response.json",
    "question_field": "Question",
    "answer_field": "Answer (final answer highlighted)",
    "image_field": "ImagePath",
    "choice_field": null
  },
  "created_at": "2026-03-24T07:48:30Z"
}
```

#### raw_asset_bundle

```json
{
  "raw_asset_bundle_id": "bundle_0160a0d42367257f68a95185",
  "candidate_id": "cand_ceb7be29b46b8bf77a9328d4",
  "source_dataset": "SCEMQA",
  "source_problem_id": "19",
  "assets": [
    {
      "asset_role": "question_text_raw",
      "storage_uri": "inline://prob_ceb7be29b46b8bf77a9328d4/question_source",
      "is_present": true
    },
    {
      "asset_role": "answer_text_raw",
      "storage_uri": "inline://prob_ceb7be29b46b8bf77a9328d4/answer_source",
      "is_present": true
    },
    {
      "asset_role": "image_raw",
      "storage_uri": "outputs/repo_cache/scemqa/Free_Response/Math_Free_Response/14.jpg",
      "is_present": true,
      "width": 688,
      "height": 98
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
    "initial_multi_solution_score": 0.18,
    "initial_verifiability_score": 0.6987
  },
  "created_at": "2026-03-24T07:48:30Z"
}
```

#### candidate_pool_entry

```json
{
  "candidate_pool_entry_id": "cpool_e245983bf496e4ff1368a594",
  "candidate_id": "cand_ceb7be29b46b8bf77a9328d4",
  "source_dataset": "SCEMQA",
  "source_problem_id": "19",
  "candidate_status": "ready_for_cleaning",
  "priority_score": 0.6236,
  "priority_tier": "normal",
  "recommended_cleaning_path": "multimodal_full",
  "multi_solution_mining_policy": "conservative",
  "initial_scores": {
    "initial_image_dependency_score": 0.9,
    "initial_multi_solution_score": 0.18,
    "initial_verifiability_score": 0.6987
  },
  "created_at": "2026-03-24T07:48:30Z"
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
    "rewrite_id": "rewrite_812a3fe7191f5a31abcda0a1",
    "problem_id": "prob_ceb7be29b46b8bf77a9328d4",
    "source_problem_id": "19",
    "strategy": "keep_open",
    "rationale": "Question is already open-ended.",
    "discard_reason_codes": [],
    "variant_count": 1,
    "variants": [
      {
        "open_variant_id": "open_c08f8756373b8cbaf21fa68b",
        "parent_problem_id": "prob_ceb7be29b46b8bf77a9328d4",
        "variant_index": 1,
        "title": "SCEMQA 开放题",
        "rewritten_question_text": "In a recent survey taken about the major channels on TV, it was found that channels 2, 3, 4, and 5 captured 30%, 25%, 20%, and 25% of the audience, respectively. During the first week of the new season, 500 viewers were interviewed. Suppose that the actual observed numbers are as follows. Are the differences significant? (Yes or No)",
        "expected_answer_type": "set",
        "expected_answer": "\\answer{No} We note that the expected values (150,125,100,125) are all > 5.\n\nH0: The TV audience is distributed over Channels 2, 3, 4, and 5 with percentages 30%, 25%, 20%, and 25%, respectively.\n\nHa: the audience distribution is not 30%, 25, 20%, and 25%, respectively\n\nWe calculate the chi-square = 5.167. To use the chi-square at a 10% significance level with df = 3, the critical chi-square-value is 6.25. Since 5.167 < 6.25, there is not significant evidence to reject H0",
        "split_role": "single"
      }
    ],
    "created_at": "2026-03-24T07:48:30Z"
  }
]
```

#### open_ended_problem_variants

```json
[
  {
    "open_variant_id": "open_c08f8756373b8cbaf21fa68b",
    "parent_problem_id": "prob_ceb7be29b46b8bf77a9328d4",
    "variant_index": 1,
    "title": "SCEMQA 开放题",
    "rewritten_question_text": "In a recent survey taken about the major channels on TV, it was found that channels 2, 3, 4, and 5 captured 30%, 25%, 20%, and 25% of the audience, respectively. During the first week of the new season, 500 viewers were interviewed. Suppose that the actual observed numbers are as follows. Are the differences significant? (Yes or No)",
    "expected_answer_type": "set",
    "expected_answer": "\\answer{No} We note that the expected values (150,125,100,125) are all > 5.\n\nH0: The TV audience is distributed over Channels 2, 3, 4, and 5 with percentages 30%, 25%, 20%, and 25%, respectively.\n\nHa: the audience distribution is not 30%, 25, 20%, and 25%, respectively\n\nWe calculate the chi-square = 5.167. To use the chi-square at a 10% significance level with df = 3, the critical chi-square-value is 6.25. Since 5.167 < 6.25, there is not significant evidence to reject H0",
    "split_role": "single"
  }
]
```

#### asset_records

```json
[
  {
    "asset_id": "asset_0091388d43b7b8d4e86032ba",
    "problem_id": "prob_ceb7be29b46b8bf77a9328d4",
    "asset_type": "text",
    "asset_role": "question_text_source",
    "source_uri": "source://scemqa/repo_discovered/19/question",
    "storage_uri": "inline://prob_ceb7be29b46b8bf77a9328d4/question_source",
    "file_format": "txt",
    "file_size_bytes": 334,
    "width": null,
    "height": null,
    "sha256": "1de4abc367fe676f8bdec4e603e05fb0e7df423a113aca7a730e71a6982819b9",
    "perceptual_hash": null,
    "source_text_snapshot": "In a recent survey taken about the major channels on TV, it was found that channels 2, 3, 4, and 5 captured 30%, 25%, 20%, and 25% of the audience, respectively. During the first week of the new season, 500 viewers were interviewed. Suppose that the actual observed numbers are as follows. Are the differences significant? (Yes or No)",
    "normalized_text_snapshot": null,
    "text_completeness_score": 0.8,
    "blur_score": null,
    "readability_score": null,
    "noise_score": null,
    "cropped_from_asset_id": null,
    "roi_bbox": null,
    "unit_normalization_map": [],
    "variable_aliases": [
      {
        "original": "In",
        "canonical": "In",
        "variable_type": "label"
      },
      {
        "original": "a",
        "canonical": "a",
        "variable_type": "symbol"
      },
      {
        "original": "the",
        "canonical": "the",
        "variable_type": "label"
      },
      {
        "original": "on",
        "canonical": "on",
        "variable_type": "label"
      },
      {
        "original": "TV",
        "canonical": "TV",
        "variable_type": "label"
      },
      {
        "original": "it",
        "canonical": "it",
        "variable_type": "label"
      },
      {
        "original": "was",
        "canonical": "was",
        "variable_type": "label"
      },
      {
        "original": "that",
        "canonical": "that",
        "variable_type": "label"
      },
      {
        "original": "and",
        "canonical": "and",
        "variable_type": "label"
      },
      {
        "original": "of",
        "canonical": "of",
        "variable_type": "label"
      },
      {
        "original": "week",
        "canonical": "week",
        "variable_type": "label"
      },
      {
        "original": "new",
        "canonical": "new",
        "variable_type": "label"
      },
      {
        "original": "were",
        "canonical": "were",
        "variable_type": "label"
      },
      {
        "original": "are",
        "canonical": "are",
        "variable_type": "label"
      },
      {
        "original": "as",
        "canonical": "as",
        "variable_type": "label"
      },
      {
        "original": "Are",
        "canonical": "Are",
        "variable_type": "label"
      },
      {
        "original": "Yes",
        "canonical": "Yes",
        "variable_type": "label"
      },
      {
        "original": "or",
        "canonical": "or",
        "variable_type": "label"
      },
      {
        "original": "No",
        "canonical": "No",
        "variable_type": "label"
      }
    ],
    "asset_quality_flags": [],
    "is_usable": true,
    "discard_reason_codes": [],
    "created_at": "2026-03-24T07:48:30Z",
    "updated_at": "2026-03-24T07:48:30Z"
  },
  {
    "asset_id": "asset_44c3a2a8295c666b3dd2caeb",
    "problem_id": "prob_ceb7be29b46b8bf77a9328d4",
    "asset_type": "text",
    "asset_role": "question_text_normalized",
    "source_uri": null,
    "storage_uri": "inline://prob_ceb7be29b46b8bf77a9328d4/question_normalized",
    "file_format": "txt",
    "file_size_bytes": 334,
    "width": null,
    "height": null,
    "sha256": "1de4abc367fe676f8bdec4e603e05fb0e7df423a113aca7a730e71a6982819b9",
    "perceptual_hash": null,
    "source_text_snapshot": "In a recent survey taken about the major channels on TV, it was found that channels 2, 3, 4, and 5 captured 30%, 25%, 20%, and 25% of the audience, respectively. During the first week of the new season, 500 viewers were interviewed. Suppose that the actual observed numbers are as follows. Are the differences significant? (Yes or No)",
    "normalized_text_snapshot": "In a recent survey taken about the major channels on TV, it was found that channels 2, 3, 4, and 5 captured 30%, 25%, 20%, and 25% of the audience, respectively. During the first week of the new season, 500 viewers were interviewed. Suppose that the actual observed numbers are as follows. Are the differences significant? (Yes or No)",
    "text_completeness_score": 0.8,
    "blur_score": null,
    "readability_score": null,
    "noise_score": null,
    "cropped_from_asset_id": null,
    "roi_bbox": null,
    "unit_normalization_map": [],
    "variable_aliases": [
      {
        "original": "In",
        "canonical": "In",
        "variable_type": "label"
      },
      {
        "original": "a",
        "canonical": "a",
        "variable_type": "symbol"
      },
      {
        "original": "the",
        "canonical": "the",
        "variable_type": "label"
      },
      {
        "original": "on",
        "canonical": "on",
        "variable_type": "label"
      },
      {
        "original": "TV",
        "canonical": "TV",
        "variable_type": "label"
      },
      {
        "original": "it",
        "canonical": "it",
        "variable_type": "label"
      },
      {
        "original": "was",
        "canonical": "was",
        "variable_type": "label"
      },
      {
        "original": "that",
        "canonical": "that",
        "variable_type": "label"
      },
      {
        "original": "and",
        "canonical": "and",
        "variable_type": "label"
      },
      {
        "original": "of",
        "canonical": "of",
        "variable_type": "label"
      },
      {
        "original": "week",
        "canonical": "week",
        "variable_type": "label"
      },
      {
        "original": "new",
        "canonical": "new",
        "variable_type": "label"
      },
      {
        "original": "were",
        "canonical": "were",
        "variable_type": "label"
      },
      {
        "original": "are",
        "canonical": "are",
        "variable_type": "label"
      },
      {
        "original": "as",
        "canonical": "as",
        "variable_type": "label"
      },
      {
        "original": "Are",
        "canonical": "Are",
        "variable_type": "label"
      },
      {
        "original": "Yes",
        "canonical": "Yes",
        "variable_type": "label"
      },
      {
        "original": "or",
        "canonical": "or",
        "variable_type": "label"
      },
      {
        "original": "No",
        "canonical": "No",
        "variable_type": "label"
      }
    ],
    "asset_quality_flags": [],
    "is_usable": true,
    "discard_reason_codes": [],
    "created_at": "2026-03-24T07:48:30Z",
    "updated_at": "2026-03-24T07:48:30Z"
  },
  {
    "asset_id": "asset_ecdf09acec71695bfd3da086",
    "problem_id": "prob_ceb7be29b46b8bf77a9328d4",
    "asset_type": "answer",
    "asset_role": "answer_raw",
    "source_uri": "source://scemqa/repo_discovered/19/answer",
    "storage_uri": "inline://prob_ceb7be29b46b8bf77a9328d4/answer_raw",
    "file_format": "txt",
    "file_size_bytes": 477,
    "width": null,
    "height": null,
    "sha256": "1043c6472c42eb0678123671d9674c1897c9884ebeb9ce30db1fbce83351d32c",
    "perceptual_hash": null,
    "source_text_snapshot": "\\answer{No} We note that the expected values (150,125,100,125) are all > 5.\n\nH0: The TV audience is distributed over Channels 2, 3, 4, and 5 with percentages 30%, 25%, 20%, and 25%, respectively.\n\nHa: the audience distribution is not 30%, 25, 20%, and 25%, respectively\n\nWe calculate the chi-square = 5.167. To use the chi-square at a 10% significance level with df = 3, the critical chi-square-value is 6.25. Since 5.167 < 6.25, there is not significant evidence to reject H0.",
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
        "original": "No",
        "canonical": "No",
        "variable_type": "label"
      },
      {
        "original": "We",
        "canonical": "We",
        "variable_type": "label"
      },
      {
        "original": "note",
        "canonical": "note",
        "variable_type": "label"
      },
      {
        "original": "that",
        "canonical": "that",
        "variable_type": "label"
      },
      {
        "original": "the",
        "canonical": "the",
        "variable_type": "label"
      },
      {
        "original": "are",
        "canonical": "are",
        "variable_type": "label"
      },
      {
        "original": "all",
        "canonical": "all",
        "variable_type": "label"
      },
      {
        "original": "H0",
        "canonical": "H0",
        "variable_type": "label"
      },
      {
        "original": "The",
        "canonical": "The",
        "variable_type": "label"
      },
      {
        "original": "TV",
        "canonical": "TV",
        "variable_type": "label"
      },
      {
        "original": "is",
        "canonical": "is",
        "variable_type": "label"
      },
      {
        "original": "over",
        "canonical": "over",
        "variable_type": "label"
      },
      {
        "original": "and",
        "canonical": "and",
        "variable_type": "label"
      },
      {
        "original": "with",
        "canonical": "with",
        "variable_type": "label"
      },
      {
        "original": "Ha",
        "canonical": "Ha",
        "variable_type": "label"
      },
      {
        "original": "not",
        "canonical": "not",
        "variable_type": "label"
      },
      {
        "original": "chi",
        "canonical": "chi",
        "variable_type": "label"
      },
      {
        "original": "To",
        "canonical": "To",
        "variable_type": "label"
      },
      {
        "original": "use",
        "canonical": "use",
        "variable_type": "label"
      },
      {
        "original": "at",
        "canonical": "at",
        "variable_type": "label"
      },
      {
        "original": "a",
        "canonical": "a",
        "variable_type": "symbol"
      },
      {
        "original": "df",
        "canonical": "df",
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
    "created_at": "2026-03-24T07:48:30Z",
    "updated_at": "2026-03-24T07:48:30Z"
  },
  {
    "asset_id": "asset_d26b7576256b1d993bb3c818",
    "problem_id": "prob_ceb7be29b46b8bf77a9328d4",
    "asset_type": "answer",
    "asset_role": "answer_normalized",
    "source_uri": null,
    "storage_uri": "inline://prob_ceb7be29b46b8bf77a9328d4/answer_normalized",
    "file_format": "txt",
    "file_size_bytes": 476,
    "width": null,
    "height": null,
    "sha256": "1f62d04e4e807855a2387d5fbbb4eae44176ad3bf3ba8d5f4c9df32a226e51bb",
    "perceptual_hash": null,
    "source_text_snapshot": "\\answer{No} We note that the expected values (150,125,100,125) are all > 5.\n\nH0: The TV audience is distributed over Channels 2, 3, 4, and 5 with percentages 30%, 25%, 20%, and 25%, respectively.\n\nHa: the audience distribution is not 30%, 25, 20%, and 25%, respectively\n\nWe calculate the chi-square = 5.167. To use the chi-square at a 10% significance level with df = 3, the critical chi-square-value is 6.25. Since 5.167 < 6.25, there is not significant evidence to reject H0.",
    "normalized_text_snapshot": "\\answer{No} We note that the expected values (150,125,100,125) are all > 5.\n\nH0: The TV audience is distributed over Channels 2, 3, 4, and 5 with percentages 30%, 25%, 20%, and 25%, respectively.\n\nHa: the audience distribution is not 30%, 25, 20%, and 25%, respectively\n\nWe calculate the chi-square = 5.167. To use the chi-square at a 10% significance level with df = 3, the critical chi-square-value is 6.25. Since 5.167 < 6.25, there is not significant evidence to reject H0",
    "text_completeness_score": 1.0,
    "blur_score": null,
    "readability_score": null,
    "noise_score": null,
    "cropped_from_asset_id": null,
    "roi_bbox": null,
    "unit_normalization_map": [],
    "variable_aliases": [
      {
        "original": "No",
        "canonical": "No",
        "variable_type": "label"
      },
      {
        "original": "We",
        "canonical": "We",
        "variable_type": "label"
      },
      {
        "original": "note",
        "canonical": "note",
        "variable_type": "label"
      },
      {
        "original": "that",
        "canonical": "that",
        "variable_type": "label"
      },
      {
        "original": "the",
        "canonical": "the",
        "variable_type": "label"
      },
      {
        "original": "are",
        "canonical": "are",
        "variable_type": "label"
      },
      {
        "original": "all",
        "canonical": "all",
        "variable_type": "label"
      },
      {
        "original": "H0",
        "canonical": "H0",
        "variable_type": "label"
      },
      {
        "original": "The",
        "canonical": "The",
        "variable_type": "label"
      },
      {
        "original": "TV",
        "canonical": "TV",
        "variable_type": "label"
      },
      {
        "original": "is",
        "canonical": "is",
        "variable_type": "label"
      },
      {
        "original": "over",
        "canonical": "over",
        "variable_type": "label"
      },
      {
        "original": "and",
        "canonical": "and",
        "variable_type": "label"
      },
      {
        "original": "with",
        "canonical": "with",
        "variable_type": "label"
      },
      {
        "original": "Ha",
        "canonical": "Ha",
        "variable_type": "label"
      },
      {
        "original": "not",
        "canonical": "not",
        "variable_type": "label"
      },
      {
        "original": "chi",
        "canonical": "chi",
        "variable_type": "label"
      },
      {
        "original": "To",
        "canonical": "To",
        "variable_type": "label"
      },
      {
        "original": "use",
        "canonical": "use",
        "variable_type": "label"
      },
      {
        "original": "at",
        "canonical": "at",
        "variable_type": "label"
      },
      {
        "original": "a",
        "canonical": "a",
        "variable_type": "symbol"
      },
      {
        "original": "df",
        "canonical": "df",
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
    "created_at": "2026-03-24T07:48:30Z",
    "updated_at": "2026-03-24T07:48:30Z"
  },
  {
    "asset_id": "asset_68607c7e4bdc12fa5c17a0ef",
    "problem_id": "prob_ceb7be29b46b8bf77a9328d4",
    "asset_type": "image",
    "asset_role": "primary_image",
    "source_uri": "outputs/repo_cache/scemqa/Free_Response/Math_Free_Response/14.jpg",
    "storage_uri": "outputs/user_requested_batch_review/pipeline_runs/run_637ca3432da6ddfb/datasets/scemqa/artifacts/images/prob_ceb7be29b46b8bf77a9328d4_primary.png",
    "file_format": "png",
    "file_size_bytes": 14704,
    "width": 688,
    "height": 98,
    "sha256": "b8649c4b91edd66ae23a6788bb8e3c3806ee7846a0795258904c9ef6093facf4",
    "perceptual_hash": "00fb00ffff003f00",
    "source_text_snapshot": null,
    "normalized_text_snapshot": null,
    "text_completeness_score": null,
    "blur_score": 5957.6152,
    "readability_score": 0.6557,
    "noise_score": 41.146,
    "cropped_from_asset_id": null,
    "roi_bbox": {
      "x": 0,
      "y": 0,
      "width": 688,
      "height": 98
    },
    "unit_normalization_map": [],
    "variable_aliases": [],
    "asset_quality_flags": [
      "low_resolution",
      "severe_crop_loss"
    ],
    "is_usable": true,
    "discard_reason_codes": [],
    "created_at": "2026-03-24T07:48:30Z",
    "updated_at": "2026-03-24T07:48:30Z"
  },
  {
    "asset_id": "asset_4bf02841d0ccf37c552851a4",
    "problem_id": "prob_ceb7be29b46b8bf77a9328d4",
    "asset_type": "text",
    "asset_role": "question_text_open_variant",
    "source_uri": null,
    "storage_uri": "inline://open_c08f8756373b8cbaf21fa68b",
    "file_format": "txt",
    "file_size_bytes": 334,
    "width": null,
    "height": null,
    "sha256": "1de4abc367fe676f8bdec4e603e05fb0e7df423a113aca7a730e71a6982819b9",
    "perceptual_hash": null,
    "source_text_snapshot": "In a recent survey taken about the major channels on TV, it was found that channels 2, 3, 4, and 5 captured 30%, 25%, 20%, and 25% of the audience, respectively. During the first week of the new season, 500 viewers were interviewed. Suppose that the actual observed numbers are as follows. Are the differences significant? (Yes or No)",
    "normalized_text_snapshot": "In a recent survey taken about the major channels on TV, it was found that channels 2, 3, 4, and 5 captured 30%, 25%, 20%, and 25% of the audience, respectively. During the first week of the new season, 500 viewers were interviewed. Suppose that the actual observed numbers are as follows. Are the differences significant? (Yes or No)",
    "text_completeness_score": 0.8,
    "blur_score": null,
    "readability_score": null,
    "noise_score": null,
    "cropped_from_asset_id": null,
    "roi_bbox": null,
    "unit_normalization_map": [],
    "variable_aliases": [
      {
        "original": "In",
        "canonical": "In",
        "variable_type": "label"
      },
      {
        "original": "a",
        "canonical": "a",
        "variable_type": "symbol"
      },
      {
        "original": "the",
        "canonical": "the",
        "variable_type": "label"
      },
      {
        "original": "on",
        "canonical": "on",
        "variable_type": "label"
      },
      {
        "original": "TV",
        "canonical": "TV",
        "variable_type": "label"
      },
      {
        "original": "it",
        "canonical": "it",
        "variable_type": "label"
      },
      {
        "original": "was",
        "canonical": "was",
        "variable_type": "label"
      },
      {
        "original": "that",
        "canonical": "that",
        "variable_type": "label"
      },
      {
        "original": "and",
        "canonical": "and",
        "variable_type": "label"
      },
      {
        "original": "of",
        "canonical": "of",
        "variable_type": "label"
      },
      {
        "original": "week",
        "canonical": "week",
        "variable_type": "label"
      },
      {
        "original": "new",
        "canonical": "new",
        "variable_type": "label"
      },
      {
        "original": "were",
        "canonical": "were",
        "variable_type": "label"
      },
      {
        "original": "are",
        "canonical": "are",
        "variable_type": "label"
      },
      {
        "original": "as",
        "canonical": "as",
        "variable_type": "label"
      },
      {
        "original": "Are",
        "canonical": "Are",
        "variable_type": "label"
      },
      {
        "original": "Yes",
        "canonical": "Yes",
        "variable_type": "label"
      },
      {
        "original": "or",
        "canonical": "or",
        "variable_type": "label"
      },
      {
        "original": "No",
        "canonical": "No",
        "variable_type": "label"
      }
    ],
    "asset_quality_flags": [],
    "is_usable": true,
    "discard_reason_codes": [],
    "created_at": "2026-03-24T07:48:30Z",
    "updated_at": "2026-03-24T07:48:30Z"
  }
]
```

#### node_records

```json
[
  {
    "node_id": "node_0e98e2ddb07cbed0927496ff",
    "problem_id": "prob_ceb7be29b46b8bf77a9328d4",
    "node_type": "text_fact",
    "canonical_value": "In a recent survey taken about the major channels on TV, it was found that channels 2, 3, 4, and 5 captured 30%, 25%, 20%, and 25% of the audience, respectively.",
    "surface_forms": [
      "In a recent survey taken about the major channels on TV, it was found that channels 2, 3, 4, and 5 captured 30%, 25%, 20%, and 25% of the audience, respectively."
    ],
    "origin_kind": "text",
    "cognitive_level": "objective",
    "source_refs": [
      "asset_44c3a2a8295c666b3dd2caeb"
    ],
    "evidence_refs": [
      "asset_44c3a2a8295c666b3dd2caeb"
    ],
    "upstream_node_ids": [],
    "value_type": "condition",
    "normalized_value": {
      "text": "In a recent survey taken about the major channels on TV, it was found that channels 2, 3, 4, and 5 captured 30%, 25%, 20%, and 25% of the audience, respectively.",
      "segment_index": 1,
      "mentions_visual": false,
      "numeric_tokens": [
        "2",
        "3",
        "4",
        "5",
        "30",
        "25",
        "20",
        "25"
      ],
      "unit_mentions": [
        "V",
        "h",
        "m",
        "s"
      ],
      "condition_role": "explicit"
    },
    "unit": "V,h,m,s",
    "confidence": 0.92,
    "verifiability": "high",
    "ambiguity_level": "low",
    "is_direct_from_source": true,
    "is_generated_by_system": false,
    "is_reviewed_by_human": false,
    "stage_created": "cleaning",
    "status": "active",
    "version": 1,
    "created_at": "2026-03-24T07:48:30Z",
    "updated_at": "2026-03-24T07:48:30Z"
  },
  {
    "node_id": "node_47925bf388403c52aa8ba286",
    "problem_id": "prob_ceb7be29b46b8bf77a9328d4",
    "node_type": "text_fact",
    "canonical_value": "During the first week of the new season, 500 viewers were interviewed.",
    "surface_forms": [
      "During the first week of the new season, 500 viewers were interviewed."
    ],
    "origin_kind": "text",
    "cognitive_level": "objective",
    "source_refs": [
      "asset_44c3a2a8295c666b3dd2caeb"
    ],
    "evidence_refs": [
      "asset_44c3a2a8295c666b3dd2caeb"
    ],
    "upstream_node_ids": [],
    "value_type": "condition",
    "normalized_value": {
      "text": "During the first week of the new season, 500 viewers were interviewed.",
      "segment_index": 2,
      "mentions_visual": false,
      "numeric_tokens": [
        "500"
      ],
      "unit_mentions": [
        "g",
        "h",
        "s"
      ],
      "condition_role": "explicit"
    },
    "unit": "g,h,s",
    "confidence": 0.92,
    "verifiability": "high",
    "ambiguity_level": "low",
    "is_direct_from_source": true,
    "is_generated_by_system": false,
    "is_reviewed_by_human": false,
    "stage_created": "cleaning",
    "status": "active",
    "version": 1,
    "created_at": "2026-03-24T07:48:30Z",
    "updated_at": "2026-03-24T07:48:30Z"
  },
  {
    "node_id": "node_4d24fa80fbba87e3cac95e7a",
    "problem_id": "prob_ceb7be29b46b8bf77a9328d4",
    "node_type": "target_slot",
    "canonical_value": "(Yes or No)",
    "surface_forms": [
      "(Yes or No)"
    ],
    "origin_kind": "text_structure",
    "cognitive_level": "computed",
    "source_refs": [
      "asset_44c3a2a8295c666b3dd2caeb"
    ],
    "evidence_refs": [
      "asset_44c3a2a8295c666b3dd2caeb"
    ],
    "upstream_node_ids": [],
    "value_type": "set",
    "normalized_value": {
      "slot_id": "slot_prob_ceb7be29b46b8bf77a9328d4_1",
      "variant_index": 1,
      "split_role": "single",
      "slot_type": "set",
      "target_text": "(Yes or No)",
      "expected_answer_type": "set",
      "expected_answer": "\\answer{No} We note that the expected values (150,125,100,125) are all > 5.\n\nH0: The TV audience is distributed over Channels 2, 3, 4, and 5 with percentages 30%, 25%, 20%, and 25%, respectively.\n\nHa: the audience distribution is not 30%, 25, 20%, and 25%, respectively\n\nWe calculate the chi-square = 5.167. To use the chi-square at a 10% significance level with df = 3, the critical chi-square-value is 6.25. Since 5.167 < 6.25, there is not significant evidence to reject H0",
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
    "created_at": "2026-03-24T07:48:30Z",
    "updated_at": "2026-03-24T07:48:30Z"
  },
  {
    "node_id": "node_8b4b2654808f867dfb533907",
    "problem_id": "prob_ceb7be29b46b8bf77a9328d4",
    "node_type": "answer_claim",
    "canonical_value": "\\answer{No} We note that the expected values (150,125,100,125) are all > 5.\n\nH0: The TV audience is distributed over Channels 2, 3, 4, and 5 with percentages 30%, 25%, 20%, and 25%, respectively.\n\nHa: the audience distribution is not 30%, 25, 20%, and 25%, respectively\n\nWe calculate the chi-square = 5.167. To use the chi-square at a 10% significance level with df = 3, the critical chi-square-value is 6.25. Since 5.167 < 6.25, there is not significant evidence to reject H0",
    "surface_forms": [
      "\\answer{No} We note that the expected values (150,125,100,125) are all > 5.\n\nH0: The TV audience is distributed over Channels 2, 3, 4, and 5 with percentages 30%, 25%, 20%, and 25%, respectively.\n\nHa: the audience distribution is not 30%, 25, 20%, and 25%, respectively\n\nWe calculate the chi-square = 5.167. To use the chi-square at a 10% significance level with df = 3, the critical chi-square-value is 6.25. Since 5.167 < 6.25, there is not significant evidence to reject H0"
    ],
    "origin_kind": "text",
    "cognitive_level": "objective",
    "source_refs": [
      "asset_d26b7576256b1d993bb3c818"
    ],
    "evidence_refs": [
      "asset_d26b7576256b1d993bb3c818"
    ],
    "upstream_node_ids": [],
    "value_type": "set",
    "normalized_value": {
      "answer": "\\answer{No} We note that the expected values (150,125,100,125) are all > 5.\n\nH0: The TV audience is distributed over Channels 2, 3, 4, and 5 with percentages 30%, 25%, 20%, and 25%, respectively.\n\nHa: the audience distribution is not 30%, 25, 20%, and 25%, respectively\n\nWe calculate the chi-square = 5.167. To use the chi-square at a 10% significance level with df = 3, the critical chi-square-value is 6.25. Since 5.167 < 6.25, there is not significant evidence to reject H0"
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
    "created_at": "2026-03-24T07:48:30Z",
    "updated_at": "2026-03-24T07:48:30Z"
  },
  {
    "node_id": "node_57a00fec9f0506fee99e0180",
    "problem_id": "prob_ceb7be29b46b8bf77a9328d4",
    "node_type": "perception_fact",
    "canonical_value": "primary_image::full_canvas::canvas",
    "surface_forms": [
      "canvas"
    ],
    "origin_kind": "vision",
    "cognitive_level": "objective",
    "source_refs": [
      "visual_prob_ceb7be29b46b8bf77a9328d4_1"
    ],
    "evidence_refs": [
      "visual_prob_ceb7be29b46b8bf77a9328d4_1"
    ],
    "upstream_node_ids": [],
    "value_type": "full_canvas",
    "normalized_value": {
      "entity_id": "canvas",
      "entity_type": "full_canvas",
      "bbox": {
        "x": 0,
        "y": 0,
        "width": 688,
        "height": 98
      },
      "salience": 1.0
    },
    "unit": null,
    "confidence": 0.8623,
    "verifiability": "medium",
    "ambiguity_level": "low",
    "is_direct_from_source": false,
    "is_generated_by_system": true,
    "is_reviewed_by_human": false,
    "stage_created": "cleaning",
    "status": "active",
    "version": 1,
    "created_at": "2026-03-24T07:48:30Z",
    "updated_at": "2026-03-24T07:48:30Z"
  },
  {
    "node_id": "node_f8ff40424329b1a1b9cf88e3",
    "problem_id": "prob_ceb7be29b46b8bf77a9328d4",
    "node_type": "perception_fact",
    "canonical_value": "primary_image::content_region::roi",
    "surface_forms": [
      "roi"
    ],
    "origin_kind": "vision",
    "cognitive_level": "objective",
    "source_refs": [
      "visual_prob_ceb7be29b46b8bf77a9328d4_1"
    ],
    "evidence_refs": [
      "visual_prob_ceb7be29b46b8bf77a9328d4_1"
    ],
    "upstream_node_ids": [],
    "value_type": "content_region",
    "normalized_value": {
      "entity_id": "roi",
      "entity_type": "content_region",
      "bbox": {
        "x": 0,
        "y": 0,
        "width": 688,
        "height": 98
      },
      "salience": 0.95
    },
    "unit": null,
    "confidence": 0.8623,
    "verifiability": "medium",
    "ambiguity_level": "low",
    "is_direct_from_source": false,
    "is_generated_by_system": true,
    "is_reviewed_by_human": false,
    "stage_created": "cleaning",
    "status": "active",
    "version": 1,
    "created_at": "2026-03-24T07:48:30Z",
    "updated_at": "2026-03-24T07:48:30Z"
  },
  {
    "node_id": "node_ca9de5ab33e8baac70272204",
    "problem_id": "prob_ceb7be29b46b8bf77a9328d4",
    "node_type": "perception_fact",
    "canonical_value": "primary_image::subregion::roi_top_left",
    "surface_forms": [
      "roi_top_left"
    ],
    "origin_kind": "vision",
    "cognitive_level": "objective",
    "source_refs": [
      "visual_prob_ceb7be29b46b8bf77a9328d4_1"
    ],
    "evidence_refs": [
      "visual_prob_ceb7be29b46b8bf77a9328d4_1"
    ],
    "upstream_node_ids": [],
    "value_type": "subregion",
    "normalized_value": {
      "entity_id": "roi_top_left",
      "entity_type": "subregion",
      "bbox": {
        "x": 0,
        "y": 0,
        "width": 344,
        "height": 49
      },
      "salience": 0.4344
    },
    "unit": null,
    "confidence": 0.8623,
    "verifiability": "medium",
    "ambiguity_level": "low",
    "is_direct_from_source": false,
    "is_generated_by_system": true,
    "is_reviewed_by_human": false,
    "stage_created": "cleaning",
    "status": "active",
    "version": 1,
    "created_at": "2026-03-24T07:48:30Z",
    "updated_at": "2026-03-24T07:48:30Z"
  },
  {
    "node_id": "node_b2c11b52fe4e6411d9eac0a4",
    "problem_id": "prob_ceb7be29b46b8bf77a9328d4",
    "node_type": "perception_fact",
    "canonical_value": "primary_image::subregion::roi_top_right",
    "surface_forms": [
      "roi_top_right"
    ],
    "origin_kind": "vision",
    "cognitive_level": "objective",
    "source_refs": [
      "visual_prob_ceb7be29b46b8bf77a9328d4_1"
    ],
    "evidence_refs": [
      "visual_prob_ceb7be29b46b8bf77a9328d4_1"
    ],
    "upstream_node_ids": [],
    "value_type": "subregion",
    "normalized_value": {
      "entity_id": "roi_top_right",
      "entity_type": "subregion",
      "bbox": {
        "x": 344,
        "y": 0,
        "width": 344,
        "height": 49
      },
      "salience": 0.4705
    },
    "unit": null,
    "confidence": 0.8623,
    "verifiability": "medium",
    "ambiguity_level": "low",
    "is_direct_from_source": false,
    "is_generated_by_system": true,
    "is_reviewed_by_human": false,
    "stage_created": "cleaning",
    "status": "active",
    "version": 1,
    "created_at": "2026-03-24T07:48:30Z",
    "updated_at": "2026-03-24T07:48:30Z"
  },
  {
    "node_id": "node_ed327eefd7e0d64da612d463",
    "problem_id": "prob_ceb7be29b46b8bf77a9328d4",
    "node_type": "perception_fact",
    "canonical_value": "primary_image::subregion::roi_bottom_left",
    "surface_forms": [
      "roi_bottom_left"
    ],
    "origin_kind": "vision",
    "cognitive_level": "objective",
    "source_refs": [
      "visual_prob_ceb7be29b46b8bf77a9328d4_1"
    ],
    "evidence_refs": [
      "visual_prob_ceb7be29b46b8bf77a9328d4_1"
    ],
    "upstream_node_ids": [],
    "value_type": "subregion",
    "normalized_value": {
      "entity_id": "roi_bottom_left",
      "entity_type": "subregion",
      "bbox": {
        "x": 0,
        "y": 49,
        "width": 344,
        "height": 49
      },
      "salience": 0.5219
    },
    "unit": null,
    "confidence": 0.8623,
    "verifiability": "medium",
    "ambiguity_level": "low",
    "is_direct_from_source": false,
    "is_generated_by_system": true,
    "is_reviewed_by_human": false,
    "stage_created": "cleaning",
    "status": "active",
    "version": 1,
    "created_at": "2026-03-24T07:48:30Z",
    "updated_at": "2026-03-24T07:48:30Z"
  },
  {
    "node_id": "node_2abdac04c13601aaac37df8f",
    "problem_id": "prob_ceb7be29b46b8bf77a9328d4",
    "node_type": "perception_fact",
    "canonical_value": "primary_image::subregion::roi_bottom_right",
    "surface_forms": [
      "roi_bottom_right"
    ],
    "origin_kind": "vision",
    "cognitive_level": "objective",
    "source_refs": [
      "visual_prob_ceb7be29b46b8bf77a9328d4_1"
    ],
    "evidence_refs": [
      "visual_prob_ceb7be29b46b8bf77a9328d4_1"
    ],
    "upstream_node_ids": [],
    "value_type": "subregion",
    "normalized_value": {
      "entity_id": "roi_bottom_right",
      "entity_type": "subregion",
      "bbox": {
        "x": 344,
        "y": 49,
        "width": 344,
        "height": 49
      },
      "salience": 0.4891
    },
    "unit": null,
    "confidence": 0.8623,
    "verifiability": "medium",
    "ambiguity_level": "low",
    "is_direct_from_source": false,
    "is_generated_by_system": true,
    "is_reviewed_by_human": false,
    "stage_created": "cleaning",
    "status": "active",
    "version": 1,
    "created_at": "2026-03-24T07:48:30Z",
    "updated_at": "2026-03-24T07:48:30Z"
  },
  {
    "node_id": "node_5a9e2e4f5a090a77fc7295ba",
    "problem_id": "prob_ceb7be29b46b8bf77a9328d4",
    "node_type": "text_fact",
    "canonical_value": "In a recent survey taken about the major channels on TV, it was found that channels 2, 3, 4, and 5 captured 30%, 25%, 20%, and 25% of the audience, respectively. During the first week of the new season, 500 viewers were interviewed. Suppose that the actual observed numbers are as follows. Are the differences significant? (Yes or No)",
    "surface_forms": [
      "In a recent survey taken about the major channels on TV, it was found that channels 2, 3, 4, and 5 captured 30%, 25%, 20%, and 25% of the audience, respectively. During the first week of the new season, 500 viewers were interviewed. Suppose that the actual observed numbers are as follows. Are the differences significant? (Yes or No)"
    ],
    "origin_kind": "reasoning",
    "cognitive_level": "computed",
    "source_refs": [
      "asset_4bf02841d0ccf37c552851a4"
    ],
    "evidence_refs": [
      "asset_4bf02841d0ccf37c552851a4"
    ],
    "upstream_node_ids": [],
    "value_type": "text",
    "normalized_value": {
      "open_variant_id": "open_c08f8756373b8cbaf21fa68b",
      "parent_problem_id": "prob_ceb7be29b46b8bf77a9328d4",
      "variant_index": 1,
      "title": "SCEMQA 开放题",
      "rewritten_question_text": "In a recent survey taken about the major channels on TV, it was found that channels 2, 3, 4, and 5 captured 30%, 25%, 20%, and 25% of the audience, respectively. During the first week of the new season, 500 viewers were interviewed. Suppose that the actual observed numbers are as follows. Are the differences significant? (Yes or No)",
      "expected_answer_type": "set",
      "expected_answer": "\\answer{No} We note that the expected values (150,125,100,125) are all > 5.\n\nH0: The TV audience is distributed over Channels 2, 3, 4, and 5 with percentages 30%, 25%, 20%, and 25%, respectively.\n\nHa: the audience distribution is not 30%, 25, 20%, and 25%, respectively\n\nWe calculate the chi-square = 5.167. To use the chi-square at a 10% significance level with df = 3, the critical chi-square-value is 6.25. Since 5.167 < 6.25, there is not significant evidence to reject H0",
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
    "created_at": "2026-03-24T07:48:30Z",
    "updated_at": "2026-03-24T07:48:30Z"
  },
  {
    "node_id": "node_66841072ee3fa99798c0f78a",
    "problem_id": "prob_ceb7be29b46b8bf77a9328d4",
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
    "created_at": "2026-03-24T07:48:30Z",
    "updated_at": "2026-03-24T07:48:30Z"
  },
  {
    "node_id": "node_2c8211e312fafa75e04e2f62",
    "problem_id": "prob_ceb7be29b46b8bf77a9328d4",
    "node_type": "quality_signal",
    "canonical_value": "severe_crop_loss",
    "surface_forms": [
      "severe_crop_loss"
    ],
    "origin_kind": "system_quality",
    "cognitive_level": "computed",
    "source_refs": [],
    "evidence_refs": [],
    "upstream_node_ids": [],
    "value_type": "text",
    "normalized_value": {
      "flag": "severe_crop_loss"
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
    "created_at": "2026-03-24T07:48:30Z",
    "updated_at": "2026-03-24T07:48:30Z"
  },
  {
    "node_id": "node_50486da8afd546a37a3bc0ca",
    "problem_id": "prob_ceb7be29b46b8bf77a9328d4",
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
      "solvability_id": "solv_prob_ceb7be29b46b8bf77a9328d4",
      "problem_id": "prob_ceb7be29b46b8bf77a9328d4",
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
      "created_at": "2026-03-24T07:48:30Z"
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
    "created_at": "2026-03-24T07:48:30Z",
    "updated_at": "2026-03-24T07:48:30Z"
  },
  {
    "node_id": "node_bba3720db6b000f78484204f",
    "problem_id": "prob_ceb7be29b46b8bf77a9328d4",
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
    "created_at": "2026-03-24T07:48:30Z",
    "updated_at": "2026-03-24T07:48:30Z"
  }
]
```

#### field_audit_records

```json
[
  {
    "audit_id": "audit_11111eb784477b71bad48655",
    "problem_id": "prob_ceb7be29b46b8bf77a9328d4",
    "record_type": "problem_main_record",
    "field_name": "normalized_question_text",
    "before_value": "In a recent survey taken about the major channels on TV, it was found that channels 2, 3, 4, and 5 captured 30%, 25%, 20%, and 25% of the audience, respectively. During the first week of the new season, 500 viewers were interviewed. Suppose that the actual observed numbers are as follows. Are the differences significant? (Yes or No)",
    "after_value": "In a recent survey taken about the major channels on TV, it was found that channels 2, 3, 4, and 5 captured 30%, 25%, 20%, and 25% of the audience, respectively. During the first week of the new season, 500 viewers were interviewed. Suppose that the actual observed numbers are as follows. Are the differences significant? (Yes or No)",
    "change_type": "text_normalized",
    "trigger": "NormalizationAgent",
    "operator_type": "system",
    "created_at": "2026-03-24T07:48:30Z"
  },
  {
    "audit_id": "audit_5b43026cbcb3cf465fc108f5",
    "problem_id": "prob_ceb7be29b46b8bf77a9328d4",
    "record_type": "problem_main_record",
    "field_name": "normalized_answer_text",
    "before_value": "\\answer{No} We note that the expected values (150,125,100,125) are all > 5.\n\nH0: The TV audience is distributed over Channels 2, 3, 4, and 5 with percentages 30%, 25%, 20%, and 25%, respectively.\n\nHa: the audience distribution is not 30%, 25, 20%, and 25%, respectively\n\nWe calculate the chi-square = 5.167. To use the chi-square at a 10% significance level with df = 3, the critical chi-square-value is 6.25. Since 5.167 < 6.25, there is not significant evidence to reject H0.",
    "after_value": "\\answer{No} We note that the expected values (150,125,100,125) are all > 5.\n\nH0: The TV audience is distributed over Channels 2, 3, 4, and 5 with percentages 30%, 25%, 20%, and 25%, respectively.\n\nHa: the audience distribution is not 30%, 25, 20%, and 25%, respectively\n\nWe calculate the chi-square = 5.167. To use the chi-square at a 10% significance level with df = 3, the critical chi-square-value is 6.25. Since 5.167 < 6.25, there is not significant evidence to reject H0",
    "change_type": "answer_canonicalized",
    "trigger": "NormalizationAgent",
    "operator_type": "system",
    "created_at": "2026-03-24T07:48:30Z"
  },
  {
    "audit_id": "audit_5c07f9b6a0a1546584bb7ce0",
    "problem_id": "prob_ceb7be29b46b8bf77a9328d4",
    "record_type": "rewrite_report",
    "field_name": "rewrite_strategy",
    "before_value": null,
    "after_value": "keep_open",
    "change_type": "question_rewritten",
    "trigger": "QuestionRewriteAgent",
    "operator_type": "system",
    "created_at": "2026-03-24T07:48:30Z"
  },
  {
    "audit_id": "audit_bba3720db6b000f78484204f",
    "problem_id": "prob_ceb7be29b46b8bf77a9328d4",
    "record_type": "cleaning_record",
    "field_name": "decision",
    "before_value": null,
    "after_value": "reject",
    "change_type": "gate_decision",
    "trigger": "CleanGateAgent",
    "operator_type": "system",
    "created_at": "2026-03-24T07:48:30Z"
  },
  {
    "audit_id": "audit_9fcd3e5ee8824452380075db",
    "problem_id": "prob_ceb7be29b46b8bf77a9328d4",
    "record_type": "normalized_assets",
    "field_name": "variable_aliases",
    "before_value": null,
    "after_value": [
      {
        "original": "In",
        "canonical": "In",
        "variable_type": "label"
      },
      {
        "original": "a",
        "canonical": "a",
        "variable_type": "symbol"
      },
      {
        "original": "the",
        "canonical": "the",
        "variable_type": "label"
      },
      {
        "original": "on",
        "canonical": "on",
        "variable_type": "label"
      },
      {
        "original": "TV",
        "canonical": "TV",
        "variable_type": "label"
      },
      {
        "original": "it",
        "canonical": "it",
        "variable_type": "label"
      },
      {
        "original": "was",
        "canonical": "was",
        "variable_type": "label"
      },
      {
        "original": "that",
        "canonical": "that",
        "variable_type": "label"
      },
      {
        "original": "and",
        "canonical": "and",
        "variable_type": "label"
      },
      {
        "original": "of",
        "canonical": "of",
        "variable_type": "label"
      },
      {
        "original": "week",
        "canonical": "week",
        "variable_type": "label"
      },
      {
        "original": "new",
        "canonical": "new",
        "variable_type": "label"
      },
      {
        "original": "were",
        "canonical": "were",
        "variable_type": "label"
      },
      {
        "original": "are",
        "canonical": "are",
        "variable_type": "label"
      },
      {
        "original": "as",
        "canonical": "as",
        "variable_type": "label"
      },
      {
        "original": "Are",
        "canonical": "Are",
        "variable_type": "label"
      },
      {
        "original": "Yes",
        "canonical": "Yes",
        "variable_type": "label"
      },
      {
        "original": "or",
        "canonical": "or",
        "variable_type": "label"
      },
      {
        "original": "No",
        "canonical": "No",
        "variable_type": "label"
      }
    ],
    "change_type": "variable_canonicalized",
    "trigger": "NormalizationAgent",
    "operator_type": "system",
    "created_at": "2026-03-24T07:48:30Z"
  }
]
```

#### reject_records

```json
[
  {
    "reject_id": "reject_812a3fe7191f5a31abcda0a1",
    "problem_id": "prob_ceb7be29b46b8bf77a9328d4",
    "stage": "cleaning",
    "reject_level": "problem",
    "reject_reason_codes": [
      "low_resolution"
    ],
    "reject_reason_detail": "Question is already open-ended.",
    "blocking_fields": [
      "low_resolution",
      "severe_crop_loss"
    ],
    "evidence_refs": [
      "align_812a3fe7191f5a31abcda0a1",
      "solv_prob_ceb7be29b46b8bf77a9328d4"
    ],
    "recoverable": false,
    "recommended_action": "drop",
    "reviewed_by": null,
    "created_at": "2026-03-24T07:48:30Z"
  }
]
```

### 4.1 完整 sample bundle 原文件

- `outputs/user_requested_batch_review/pipeline_runs/run_637ca3432da6ddfb/datasets/scemqa/samples/prob_ceb7be29b46b8bf77a9328d4.json`
