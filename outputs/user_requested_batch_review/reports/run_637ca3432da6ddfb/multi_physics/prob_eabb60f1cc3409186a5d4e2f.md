# muti- physics / prob_eabb60f1cc3409186a5d4e2f

- source_problem_id: `0`
- source_split: `repo_discovered`
- clean_decision: `pass`
- rewrite_strategy: `keep_open`
- full sample bundle JSON: `outputs/user_requested_batch_review/pipeline_runs/run_637ca3432da6ddfb/datasets/multi_physics/samples/prob_eabb60f1cc3409186a5d4e2f.json`

## 1. 原始内容（处理前）

### 1.1 原始快照

```json
{
  "dataset_key": "multi_physics",
  "source_problem_id": "0",
  "source_split": "repo_discovered",
  "raw_question_text": "电动车由静止开始在平直的公路上行驶，其运动的v—t图象如图所示。\nA. 12s末电动车的加速度大小为1/3m/s2\nB. 0~20s内电动车的平均速度为2.5m/s\nC. 0~50s内电动车的位移大小为200m\nD. 0~50s内电动车的平均速度大于4m/s",
  "raw_answer_text": "D",
  "choice_map": {},
  "image_sources": [
    "outputs/repo_cache/multi_physics/Data/../Data/1/0_0.png"
  ],
  "metadata": {
    "data_file": "outputs/repo_cache/multi_physics/Data/1.json",
    "question_field": "question",
    "answer_field": "answer",
    "image_field": "picture",
    "choice_field": null
  },
  "raw_record": {
    "category": "exclusive",
    "question": "电动车由静止开始在平直的公路上行驶，其运动的v—t图象如图所示。\nA. 12s末电动车的加速度大小为1/3m/s2\nB. 0~20s内电动车的平均速度为2.5m/s\nC. 0~50s内电动车的位移大小为200m\nD. 0~50s内电动车的平均速度大于4m/s",
    "picture": [
      "../Data/1/0_0.png"
    ],
    "answer": [
      "D"
    ],
    "analysis": "12s末电动车的加速度大小为对应12末速度图象的斜率，不是1/3m/s，选项A错误。0~20s内电动车的平均速度大于2.5m/s，选项B错误。根据速度图面积表示位移可知，0~50s内电动车的位移大小大于200m，选项C错误。根据平均速度的定义式可知，0~50s内电动车的平均速度大于4m/s，选项D正确。",
    "index": 0,
    "level": 2
  }
}
```

### 1.2 原始图片

- [`0_0.png`](outputs/repo_cache/multi_physics/Data/../Data/1/0_0.png)

## 2. 处理前后对照

### 2.1 关键字段对照

| 字段 | 处理前 | 处理后 |
| --- | --- | --- |
| question_text | 电动车由静止开始在平直的公路上行驶，其运动的v—t图象如图所示。 A. 12s末电动车的加速度大小为1/3m/s2 B. 0~20s内电动车的平均速度为2.5m/s C. 0~50s内电动车的位移大小为200m D. 0~50s内电动车的平均速度大于4m/s | 电动车由静止开始在平直的公路上行驶,其运动的v—t图象如图所示。 A. 12s末电动车的加速度大小为1/3m/s2 B. 0~20s内电动车的平均速度为2.5m/s C. 0~50s内电动车的位移大小为200m D. 0~50s内电动车的平均速度大于4m/s |
| answer_text | D | D |
| answer_type | - | option |
| image_count | 1 | 1 |
| text_dominant | - | False |
| cleaning_path | - | multimodal_full |
| clean_decision | - | pass |
| alignment_status | - | good |
| solvability_decision_hint | - | pass |
| rewrite_strategy | - | keep_open |

### 2.2 结构化处理后结果

#### problem_main_record

```json
{
  "problem_id": "prob_eabb60f1cc3409186a5d4e2f",
  "source_dataset": "muti- physics",
  "source_split": "repo_discovered",
  "source_problem_id": "0",
  "ingest_batch_id": "multidataset-clean_20260324T074830Z",
  "problem_type": "multimodal_reasoning",
  "domain_tags": [
    "物理"
  ],
  "language": "zh",
  "raw_question_text": "电动车由静止开始在平直的公路上行驶，其运动的v—t图象如图所示。\nA. 12s末电动车的加速度大小为1/3m/s2\nB. 0~20s内电动车的平均速度为2.5m/s\nC. 0~50s内电动车的位移大小为200m\nD. 0~50s内电动车的平均速度大于4m/s",
  "normalized_question_text": "电动车由静止开始在平直的公路上行驶,其运动的v—t图象如图所示。\nA. 12s末电动车的加速度大小为1/3m/s2\nB. 0~20s内电动车的平均速度为2.5m/s\nC. 0~50s内电动车的位移大小为200m\nD. 0~50s内电动车的平均速度大于4m/s",
  "raw_answer_text": "D",
  "normalized_answer_text": "D",
  "answer_type": "option",
  "image_count": 1,
  "has_multiple_images": false,
  "requires_image": true,
  "multimodal_strength_score": 0.9668,
  "multi_step_score": 0.4727,
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
  "candidate_id": "cand_eabb60f1cc3409186a5d4e2f",
  "text_dominant": false,
  "cleaning_path": "multimodal_full",
  "alignment_status": "good",
  "solvability_score": 1.0,
  "solvability_decision_hint": "pass",
  "created_at": "2026-03-24T07:48:58Z",
  "updated_at": "2026-03-24T07:48:58Z",
  "initial_image_dependency_score": 0.9,
  "initial_multi_solution_score": 0.18,
  "initial_verifiability_score": 0.8781,
  "multi_solution_mining_policy": "conservative"
}
```

#### clean_problem_record

```json
{
  "clean_problem_record_id": "cleanprob_b866c55bf673640b6806b264",
  "problem_id": "prob_eabb60f1cc3409186a5d4e2f",
  "source_dataset": "muti- physics",
  "source_problem_id": "0",
  "normalized_question_text": "电动车由静止开始在平直的公路上行驶,其运动的v—t图象如图所示。\nA. 12s末电动车的加速度大小为1/3m/s2\nB. 0~20s内电动车的平均速度为2.5m/s\nC. 0~50s内电动车的位移大小为200m\nD. 0~50s内电动车的平均速度大于4m/s",
  "normalized_answer_text": "D",
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
  "clean_decision": "pass",
  "decision_reason_codes": [
    "meets_cleaning_requirements"
  ],
  "created_at": "2026-03-24T07:48:58Z"
}
```

#### normalized_assets

```json
{
  "normalized_assets_id": "nassets_b866c55bf673640b6806b264",
  "problem_id": "prob_eabb60f1cc3409186a5d4e2f",
  "normalized_question_text": "电动车由静止开始在平直的公路上行驶,其运动的v—t图象如图所示。\nA. 12s末电动车的加速度大小为1/3m/s2\nB. 0~20s内电动车的平均速度为2.5m/s\nC. 0~50s内电动车的位移大小为200m\nD. 0~50s内电动车的平均速度大于4m/s",
  "normalized_answer_text": "D",
  "question_unit_normalization_map": [],
  "answer_unit_normalization_map": [],
  "variable_aliases": [
    {
      "original": "A",
      "canonical": "A",
      "variable_type": "symbol"
    },
    {
      "original": "s2",
      "canonical": "s2",
      "variable_type": "label"
    },
    {
      "original": "B",
      "canonical": "B",
      "variable_type": "symbol"
    },
    {
      "original": "s",
      "canonical": "s",
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
      "text": "电动车由静止开始在平直的公路上行驶,其运动的v—t图象如图所示。"
    },
    {
      "segment_index": 2,
      "text": "A."
    },
    {
      "segment_index": 3,
      "text": "12s末电动车的加速度大小为1/3m/s2"
    },
    {
      "segment_index": 4,
      "text": "B."
    },
    {
      "segment_index": 5,
      "text": "0~20s内电动车的平均速度为2.5m/s"
    },
    {
      "segment_index": 6,
      "text": "C."
    },
    {
      "segment_index": 7,
      "text": "0~50s内电动车的位移大小为200m"
    },
    {
      "segment_index": 8,
      "text": "D."
    },
    {
      "segment_index": 9,
      "text": "0~50s内电动车的平均速度大于4m/s"
    }
  ],
  "image_regions": [
    {
      "image_index": 1,
      "source_uri": "outputs/repo_cache/multi_physics/Data/../Data/1/0_0.png",
      "roi_bbox": {
        "x": 13,
        "y": 5,
        "width": 551,
        "height": 247
      },
      "readability_score": 0.8178,
      "contrast_score": 42.8476
    }
  ],
  "text_dominant": false,
  "cleaning_path": "multimodal_full",
  "created_at": "2026-03-24T07:48:58Z"
}
```

#### text_structure_record

```json
{
  "text_structure_id": "text_prob_eabb60f1cc3409186a5d4e2f",
  "problem_id": "prob_eabb60f1cc3409186a5d4e2f",
  "question_type": "open",
  "conditions": [
    {
      "text": "电动车由静止开始在平直的公路上行驶,其运动的v—t图象如图所示。",
      "segment_index": 1,
      "mentions_visual": false,
      "numeric_tokens": [],
      "unit_mentions": [],
      "condition_role": "explicit"
    },
    {
      "text": "12s末电动车的加速度大小为1/3m/s2",
      "segment_index": 3,
      "mentions_visual": false,
      "numeric_tokens": [
        "12",
        "1",
        "3",
        "2"
      ],
      "unit_mentions": [
        "m",
        "s"
      ],
      "condition_role": "explicit"
    },
    {
      "text": "0~20s内电动车的平均速度为2.5m/s",
      "segment_index": 5,
      "mentions_visual": false,
      "numeric_tokens": [
        "0",
        "20",
        "2.5"
      ],
      "unit_mentions": [
        "m",
        "s"
      ],
      "condition_role": "explicit"
    },
    {
      "text": "0~50s内电动车的位移大小为200m",
      "segment_index": 7,
      "mentions_visual": false,
      "numeric_tokens": [
        "0",
        "50",
        "200"
      ],
      "unit_mentions": [
        "m",
        "s"
      ],
      "condition_role": "explicit"
    },
    {
      "text": "0~50s内电动车的平均速度大于4m/s",
      "segment_index": 9,
      "mentions_visual": false,
      "numeric_tokens": [
        "0",
        "50",
        "4"
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
      "text": "电动车由静止开始在平直的公路上行驶,其运动的v—t图象如图所示。\nA. 12s末电动车的加速度大小为1/3m/s2\nB. 0~20s内电动车的平均速度为2.5m/s\nC. 0~50s内电动车的位移大小为200m\nD. 0~50s内电动车的平均速度大于4m/s",
      "segment_index": 9,
      "mentions_visual": false,
      "numeric_tokens": [
        "12",
        "1",
        "3",
        "2",
        "0",
        "20",
        "2.5",
        "0",
        "50",
        "200",
        "0",
        "50",
        "4"
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
      "slot_id": "slot_prob_eabb60f1cc3409186a5d4e2f_1",
      "variant_index": 1,
      "split_role": "single",
      "slot_type": "option",
      "target_text": "0~50s内电动车的平均速度大于4m/s",
      "expected_answer_type": "option",
      "expected_answer": "D",
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
      "original": "s2",
      "canonical": "s2",
      "variable_type": "label"
    },
    {
      "original": "B",
      "canonical": "B",
      "variable_type": "symbol"
    },
    {
      "original": "s",
      "canonical": "s",
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
    "m",
    "s"
  ],
  "sentence_segments": [
    {
      "segment_index": 1,
      "text": "电动车由静止开始在平直的公路上行驶,其运动的v—t图象如图所示。"
    },
    {
      "segment_index": 2,
      "text": "A."
    },
    {
      "segment_index": 3,
      "text": "12s末电动车的加速度大小为1/3m/s2"
    },
    {
      "segment_index": 4,
      "text": "B."
    },
    {
      "segment_index": 5,
      "text": "0~20s内电动车的平均速度为2.5m/s"
    },
    {
      "segment_index": 6,
      "text": "C."
    },
    {
      "segment_index": 7,
      "text": "0~50s内电动车的位移大小为200m"
    },
    {
      "segment_index": 8,
      "text": "D."
    },
    {
      "segment_index": 9,
      "text": "0~50s内电动车的平均速度大于4m/s"
    }
  ],
  "requires_visual_grounding": true,
  "text_structure_status": "complete",
  "parser_confidence": 0.92,
  "created_at": "2026-03-24T07:48:58Z"
}
```

#### visual_structure_records

```json
[
  {
    "visual_structure_id": "visual_prob_eabb60f1cc3409186a5d4e2f_1",
    "problem_id": "prob_eabb60f1cc3409186a5d4e2f",
    "image_index": 1,
    "image_asset_role": "primary_image",
    "global_attributes": {
      "visual_kind": "wide_diagram",
      "aspect_ratio": 2.2568,
      "dark_pixel_ratio": 0.0424,
      "readability_score": 0.8178,
      "has_roi": true
    },
    "visual_entities": [
      {
        "entity_id": "canvas",
        "entity_type": "full_canvas",
        "bbox": {
          "x": 0,
          "y": 0,
          "width": 580,
          "height": 257
        },
        "salience": 1.0
      },
      {
        "entity_id": "roi",
        "entity_type": "content_region",
        "bbox": {
          "x": 13,
          "y": 5,
          "width": 551,
          "height": 247
        },
        "salience": 0.95
      },
      {
        "entity_id": "roi_top_left",
        "entity_type": "subregion",
        "bbox": {
          "x": 13,
          "y": 5,
          "width": 275,
          "height": 123
        },
        "salience": 0.411
      },
      {
        "entity_id": "roi_bottom_left",
        "entity_type": "subregion",
        "bbox": {
          "x": 13,
          "y": 128,
          "width": 275,
          "height": 124
        },
        "salience": 0.412
      },
      {
        "entity_id": "roi_bottom_right",
        "entity_type": "subregion",
        "bbox": {
          "x": 288,
          "y": 128,
          "width": 276,
          "height": 124
        },
        "salience": 0.4007
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
        "target_entity_id": "roi_bottom_left",
        "relation": "left_of"
      },
      {
        "source_entity_id": "roi_bottom_left",
        "target_entity_id": "roi_bottom_right",
        "relation": "left_of"
      }
    ],
    "parser_confidence": 0.9271,
    "created_at": "2026-03-24T07:48:58Z"
  }
]
```

#### alignment_record

```json
{
  "alignment_id": "align_b866c55bf673640b6806b264",
  "problem_id": "prob_eabb60f1cc3409186a5d4e2f",
  "image_entity_refs": [
    "visual_prob_eabb60f1cc3409186a5d4e2f_1::roi",
    "visual_prob_eabb60f1cc3409186a5d4e2f_1::roi_top_left",
    "visual_prob_eabb60f1cc3409186a5d4e2f_1::roi_bottom_left",
    "visual_prob_eabb60f1cc3409186a5d4e2f_1::roi_bottom_right"
  ],
  "text_span_refs": [
    "asset_prob_eabb60f1cc3409186a5d4e2f_question_text_normalized"
  ],
  "alignment_pairs": [
    {
      "text_ref": "A",
      "image_ref": "visual_prob_eabb60f1cc3409186a5d4e2f_1::roi",
      "relation": "grounds_label",
      "confidence": 0.7818
    },
    {
      "text_ref": "B",
      "image_ref": "visual_prob_eabb60f1cc3409186a5d4e2f_1::roi",
      "relation": "grounds_label",
      "confidence": 0.7818
    },
    {
      "text_ref": "C",
      "image_ref": "visual_prob_eabb60f1cc3409186a5d4e2f_1::roi",
      "relation": "grounds_label",
      "confidence": 0.7818
    },
    {
      "text_ref": "D",
      "image_ref": "visual_prob_eabb60f1cc3409186a5d4e2f_1::roi",
      "relation": "grounds_label",
      "confidence": 0.7818
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
  "created_at": "2026-03-24T07:48:58Z",
  "cleaning_path": "multimodal_full",
  "text_dominant": false
}
```

#### solvability_report

```json
{
  "solvability_id": "solv_prob_eabb60f1cc3409186a5d4e2f",
  "problem_id": "prob_eabb60f1cc3409186a5d4e2f",
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
  "created_at": "2026-03-24T07:48:58Z"
}
```

#### cleaning_record

```json
{
  "cleaning_id": "clean_b866c55bf673640b6806b264",
  "problem_id": "prob_eabb60f1cc3409186a5d4e2f",
  "cleaning_version": "v3.0.0",
  "pipeline_run_id": "run_637ca3432da6ddfb",
  "dataset_name": "muti- physics",
  "input_asset_ids": [
    "asset_3d95b38604f99898ac28b15d",
    "asset_aca400e65591162d786be3df",
    "asset_4924652344f73d3c512a6d28",
    "asset_0dc6491c9db7ad693a3fc531",
    "asset_291737e5e43d05a0c69844b9",
    "asset_562cc28d0df2ea63136d32c4",
    "asset_78e39087e09f59f5be6f78fe"
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
      "check": "image_quality_1",
      "result": {
        "width": 580,
        "height": 257,
        "blur_score": 5342.2017,
        "contrast_score": 42.8476,
        "noise_score": 31.5641,
        "readability_score": 0.8178,
        "crop_integrity_score": 1.0,
        "roi_bbox": {
          "x": 13,
          "y": 5,
          "width": 551,
          "height": 247
        },
        "perceptual_hash": "1f7f413f7f7f0080"
      },
      "passed": true
    }
  ],
  "alignment_summary": {
    "alignment_id": "align_b866c55bf673640b6806b264",
    "coverage_score": 0.9,
    "consistency_score": 0.9,
    "alignment_status": "good",
    "conflict_count": 1
  },
  "text_structure_summary": {
    "text_structure_id": "text_prob_eabb60f1cc3409186a5d4e2f",
    "question_type": "open",
    "condition_count": 5,
    "target_count": 1,
    "answer_slot_count": 1,
    "status": "complete"
  },
  "solvability_summary": {
    "solvability_id": "solv_prob_eabb60f1cc3409186a5d4e2f",
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
  "clean_score": 0.8825,
  "decision": "pass",
  "decision_reason_codes": [
    "meets_cleaning_requirements"
  ],
  "review_ticket_id": null,
  "operator_type": "system",
  "started_at": "2026-03-24T07:48:58Z",
  "finished_at": "2026-03-24T07:48:58Z",
  "candidate_id": "cand_eabb60f1cc3409186a5d4e2f",
  "cleaning_path": "multimodal_full",
  "text_dominant": false
}
```

## 3. 开放化改写前后

### 3.1 改写前

```json
{
  "question_text_before_rewrite": "电动车由静止开始在平直的公路上行驶,其运动的v—t图象如图所示。\nA. 12s末电动车的加速度大小为1/3m/s2\nB. 0~20s内电动车的平均速度为2.5m/s\nC. 0~50s内电动车的位移大小为200m\nD. 0~50s内电动车的平均速度大于4m/s",
  "answer_text_before_rewrite": "D",
  "raw_question_text": "电动车由静止开始在平直的公路上行驶，其运动的v—t图象如图所示。\nA. 12s末电动车的加速度大小为1/3m/s2\nB. 0~20s内电动车的平均速度为2.5m/s\nC. 0~50s内电动车的位移大小为200m\nD. 0~50s内电动车的平均速度大于4m/s",
  "raw_answer_text": "D"
}
```

### 3.2 改写后

```json
{
  "rewrite_report": {
    "rewrite_id": "rewrite_b866c55bf673640b6806b264",
    "problem_id": "prob_eabb60f1cc3409186a5d4e2f",
    "source_problem_id": "0",
    "strategy": "keep_open",
    "rationale": "Question is already open-ended.",
    "discard_reason_codes": [],
    "variant_count": 1,
    "variants": [
      {
        "open_variant_id": "open_1d08e45644522516238990ac",
        "parent_problem_id": "prob_eabb60f1cc3409186a5d4e2f",
        "variant_index": 1,
        "title": "muti- physics 开放题",
        "rewritten_question_text": "电动车由静止开始在平直的公路上行驶,其运动的v—t图象如图所示。\nA. 12s末电动车的加速度大小为1/3m/s2\nB. 0~20s内电动车的平均速度为2.5m/s\nC. 0~50s内电动车的位移大小为200m\nD. 0~50s内电动车的平均速度大于4m/s",
        "expected_answer_type": "option",
        "expected_answer": "D",
        "split_role": "single"
      }
    ],
    "created_at": "2026-03-24T07:48:58Z"
  },
  "open_ended_problem_variants": [
    {
      "open_variant_id": "open_1d08e45644522516238990ac",
      "parent_problem_id": "prob_eabb60f1cc3409186a5d4e2f",
      "variant_index": 1,
      "title": "muti- physics 开放题",
      "rewritten_question_text": "电动车由静止开始在平直的公路上行驶,其运动的v—t图象如图所示。\nA. 12s末电动车的加速度大小为1/3m/s2\nB. 0~20s内电动车的平均速度为2.5m/s\nC. 0~50s内电动车的位移大小为200m\nD. 0~50s内电动车的平均速度大于4m/s",
      "expected_answer_type": "option",
      "expected_answer": "D",
      "split_role": "single"
    }
  ]
}
```

## 4. 完整 collection + cleaning 输出对象

#### candidate_problem_record

```json
{
  "candidate_id": "cand_eabb60f1cc3409186a5d4e2f",
  "source_dataset": "muti- physics",
  "source_split": "repo_discovered",
  "source_problem_id": "0",
  "subject": "物理",
  "raw_question_text": "电动车由静止开始在平直的公路上行驶，其运动的v—t图象如图所示。\nA. 12s末电动车的加速度大小为1/3m/s2\nB. 0~20s内电动车的平均速度为2.5m/s\nC. 0~50s内电动车的位移大小为200m\nD. 0~50s内电动车的平均速度大于4m/s",
  "raw_answer_text": "D",
  "has_image": true,
  "image_count": 1,
  "requires_image": true,
  "text_dominant": false,
  "recommended_cleaning_path": "multimodal_full",
  "initial_image_dependency_score": 0.9,
  "initial_multi_solution_score": 0.18,
  "initial_verifiability_score": 0.8781,
  "multi_solution_mining_policy": "conservative",
  "should_push_multi_solution_agent": false,
  "multi_solution_policy_rationale": "该数据集更可能以单解题为主，不强推多解 agent，只保留基础可验证性与可标注性检查。",
  "metadata": {
    "data_file": "outputs/repo_cache/multi_physics/Data/1.json",
    "question_field": "question",
    "answer_field": "answer",
    "image_field": "picture",
    "choice_field": null
  },
  "created_at": "2026-03-24T07:48:58Z"
}
```

#### raw_asset_bundle

```json
{
  "raw_asset_bundle_id": "bundle_642472c2bbd6f51b0d5f695b",
  "candidate_id": "cand_eabb60f1cc3409186a5d4e2f",
  "source_dataset": "muti- physics",
  "source_problem_id": "0",
  "assets": [
    {
      "asset_role": "question_text_raw",
      "storage_uri": "inline://prob_eabb60f1cc3409186a5d4e2f/question_source",
      "is_present": true
    },
    {
      "asset_role": "answer_text_raw",
      "storage_uri": "inline://prob_eabb60f1cc3409186a5d4e2f/answer_source",
      "is_present": true
    },
    {
      "asset_role": "image_raw",
      "storage_uri": "outputs/repo_cache/multi_physics/Data/../Data/1/0_0.png",
      "is_present": true,
      "width": 580,
      "height": 257
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
    "initial_verifiability_score": 0.8781
  },
  "created_at": "2026-03-24T07:48:58Z"
}
```

#### candidate_pool_entry

```json
{
  "candidate_pool_entry_id": "cpool_9f2e726d4f03f891295543cb",
  "candidate_id": "cand_eabb60f1cc3409186a5d4e2f",
  "source_dataset": "muti- physics",
  "source_problem_id": "0",
  "candidate_status": "ready_for_cleaning",
  "priority_score": 0.6774,
  "priority_tier": "normal",
  "recommended_cleaning_path": "multimodal_full",
  "multi_solution_mining_policy": "conservative",
  "initial_scores": {
    "initial_image_dependency_score": 0.9,
    "initial_multi_solution_score": 0.18,
    "initial_verifiability_score": 0.8781
  },
  "created_at": "2026-03-24T07:48:58Z"
}
```

#### clean_pool_entries

```json
[
  {
    "clean_pool_entry_id": "cleanpool_b866c55bf673640b6806b264",
    "candidate_id": "cand_eabb60f1cc3409186a5d4e2f",
    "problem_id": "prob_eabb60f1cc3409186a5d4e2f",
    "dataset_name": "muti- physics",
    "pool_status": "ready_for_annotation",
    "clean_decision": "pass",
    "review_required": false,
    "rewrite_strategy": "keep_open",
    "open_variant_count": 1,
    "text_dominant": false,
    "cleaning_path": "multimodal_full",
    "created_at": "2026-03-24T07:48:58Z"
  }
]
```

#### rewrite_reports

```json
[
  {
    "rewrite_id": "rewrite_b866c55bf673640b6806b264",
    "problem_id": "prob_eabb60f1cc3409186a5d4e2f",
    "source_problem_id": "0",
    "strategy": "keep_open",
    "rationale": "Question is already open-ended.",
    "discard_reason_codes": [],
    "variant_count": 1,
    "variants": [
      {
        "open_variant_id": "open_1d08e45644522516238990ac",
        "parent_problem_id": "prob_eabb60f1cc3409186a5d4e2f",
        "variant_index": 1,
        "title": "muti- physics 开放题",
        "rewritten_question_text": "电动车由静止开始在平直的公路上行驶,其运动的v—t图象如图所示。\nA. 12s末电动车的加速度大小为1/3m/s2\nB. 0~20s内电动车的平均速度为2.5m/s\nC. 0~50s内电动车的位移大小为200m\nD. 0~50s内电动车的平均速度大于4m/s",
        "expected_answer_type": "option",
        "expected_answer": "D",
        "split_role": "single"
      }
    ],
    "created_at": "2026-03-24T07:48:58Z"
  }
]
```

#### open_ended_problem_variants

```json
[
  {
    "open_variant_id": "open_1d08e45644522516238990ac",
    "parent_problem_id": "prob_eabb60f1cc3409186a5d4e2f",
    "variant_index": 1,
    "title": "muti- physics 开放题",
    "rewritten_question_text": "电动车由静止开始在平直的公路上行驶,其运动的v—t图象如图所示。\nA. 12s末电动车的加速度大小为1/3m/s2\nB. 0~20s内电动车的平均速度为2.5m/s\nC. 0~50s内电动车的位移大小为200m\nD. 0~50s内电动车的平均速度大于4m/s",
    "expected_answer_type": "option",
    "expected_answer": "D",
    "split_role": "single"
  }
]
```

#### asset_records

```json
[
  {
    "asset_id": "asset_3d95b38604f99898ac28b15d",
    "problem_id": "prob_eabb60f1cc3409186a5d4e2f",
    "asset_type": "text",
    "asset_role": "question_text_source",
    "source_uri": "source://multi_physics/repo_discovered/0/question",
    "storage_uri": "inline://prob_eabb60f1cc3409186a5d4e2f/question_source",
    "file_format": "txt",
    "file_size_bytes": 273,
    "width": null,
    "height": null,
    "sha256": "3a3bc9a391146e716db911b6acf2f89b7d9f4b4d63f6d575f5e1ca47a8a3968b",
    "perceptual_hash": null,
    "source_text_snapshot": "电动车由静止开始在平直的公路上行驶，其运动的v—t图象如图所示。\nA. 12s末电动车的加速度大小为1/3m/s2\nB. 0~20s内电动车的平均速度为2.5m/s\nC. 0~50s内电动车的位移大小为200m\nD. 0~50s内电动车的平均速度大于4m/s",
    "normalized_text_snapshot": null,
    "text_completeness_score": 0.6652,
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
        "original": "s2",
        "canonical": "s2",
        "variable_type": "label"
      },
      {
        "original": "B",
        "canonical": "B",
        "variable_type": "symbol"
      },
      {
        "original": "s",
        "canonical": "s",
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
    "created_at": "2026-03-24T07:48:58Z",
    "updated_at": "2026-03-24T07:48:58Z"
  },
  {
    "asset_id": "asset_aca400e65591162d786be3df",
    "problem_id": "prob_eabb60f1cc3409186a5d4e2f",
    "asset_type": "text",
    "asset_role": "question_text_normalized",
    "source_uri": null,
    "storage_uri": "inline://prob_eabb60f1cc3409186a5d4e2f/question_normalized",
    "file_format": "txt",
    "file_size_bytes": 271,
    "width": null,
    "height": null,
    "sha256": "7f956dcd64b5cf7c70621457cf58109cc6f3a8a19bd357fff56a0edfa32db557",
    "perceptual_hash": null,
    "source_text_snapshot": "电动车由静止开始在平直的公路上行驶，其运动的v—t图象如图所示。\nA. 12s末电动车的加速度大小为1/3m/s2\nB. 0~20s内电动车的平均速度为2.5m/s\nC. 0~50s内电动车的位移大小为200m\nD. 0~50s内电动车的平均速度大于4m/s",
    "normalized_text_snapshot": "电动车由静止开始在平直的公路上行驶,其运动的v—t图象如图所示。\nA. 12s末电动车的加速度大小为1/3m/s2\nB. 0~20s内电动车的平均速度为2.5m/s\nC. 0~50s内电动车的位移大小为200m\nD. 0~50s内电动车的平均速度大于4m/s",
    "text_completeness_score": 0.6652,
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
        "original": "s2",
        "canonical": "s2",
        "variable_type": "label"
      },
      {
        "original": "B",
        "canonical": "B",
        "variable_type": "symbol"
      },
      {
        "original": "s",
        "canonical": "s",
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
    "created_at": "2026-03-24T07:48:58Z",
    "updated_at": "2026-03-24T07:48:58Z"
  },
  {
    "asset_id": "asset_4924652344f73d3c512a6d28",
    "problem_id": "prob_eabb60f1cc3409186a5d4e2f",
    "asset_type": "answer",
    "asset_role": "answer_raw",
    "source_uri": "source://multi_physics/repo_discovered/0/answer",
    "storage_uri": "inline://prob_eabb60f1cc3409186a5d4e2f/answer_raw",
    "file_format": "txt",
    "file_size_bytes": 1,
    "width": null,
    "height": null,
    "sha256": "3f39d5c348e5b79d06e842c114e6cc571583bbf44e4b0ebfda1a01ec05745d43",
    "perceptual_hash": null,
    "source_text_snapshot": "D",
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
        "original": "D",
        "canonical": "D",
        "variable_type": "symbol"
      }
    ],
    "asset_quality_flags": [],
    "is_usable": true,
    "discard_reason_codes": [],
    "created_at": "2026-03-24T07:48:58Z",
    "updated_at": "2026-03-24T07:48:58Z"
  },
  {
    "asset_id": "asset_0dc6491c9db7ad693a3fc531",
    "problem_id": "prob_eabb60f1cc3409186a5d4e2f",
    "asset_type": "answer",
    "asset_role": "answer_normalized",
    "source_uri": null,
    "storage_uri": "inline://prob_eabb60f1cc3409186a5d4e2f/answer_normalized",
    "file_format": "txt",
    "file_size_bytes": 1,
    "width": null,
    "height": null,
    "sha256": "3f39d5c348e5b79d06e842c114e6cc571583bbf44e4b0ebfda1a01ec05745d43",
    "perceptual_hash": null,
    "source_text_snapshot": "D",
    "normalized_text_snapshot": "D",
    "text_completeness_score": 1.0,
    "blur_score": null,
    "readability_score": null,
    "noise_score": null,
    "cropped_from_asset_id": null,
    "roi_bbox": null,
    "unit_normalization_map": [],
    "variable_aliases": [
      {
        "original": "D",
        "canonical": "D",
        "variable_type": "symbol"
      }
    ],
    "asset_quality_flags": [],
    "is_usable": true,
    "discard_reason_codes": [],
    "created_at": "2026-03-24T07:48:58Z",
    "updated_at": "2026-03-24T07:48:58Z"
  },
  {
    "asset_id": "asset_291737e5e43d05a0c69844b9",
    "problem_id": "prob_eabb60f1cc3409186a5d4e2f",
    "asset_type": "image",
    "asset_role": "primary_image",
    "source_uri": "outputs/repo_cache/multi_physics/Data/../Data/1/0_0.png",
    "storage_uri": "outputs/user_requested_batch_review/pipeline_runs/run_637ca3432da6ddfb/datasets/multi_physics/artifacts/images/prob_eabb60f1cc3409186a5d4e2f_primary.png",
    "file_format": "png",
    "file_size_bytes": 9111,
    "width": 580,
    "height": 257,
    "sha256": "688dd0f240350a60281bae60adbadd81e7db426d63809cc1b6f4a35099321d1b",
    "perceptual_hash": "1f7f413f7f7f0080",
    "source_text_snapshot": null,
    "normalized_text_snapshot": null,
    "text_completeness_score": null,
    "blur_score": 5342.2017,
    "readability_score": 0.8178,
    "noise_score": 31.5641,
    "cropped_from_asset_id": null,
    "roi_bbox": {
      "x": 13,
      "y": 5,
      "width": 551,
      "height": 247
    },
    "unit_normalization_map": [],
    "variable_aliases": [],
    "asset_quality_flags": [],
    "is_usable": true,
    "discard_reason_codes": [],
    "created_at": "2026-03-24T07:48:58Z",
    "updated_at": "2026-03-24T07:48:58Z"
  },
  {
    "asset_id": "asset_562cc28d0df2ea63136d32c4",
    "problem_id": "prob_eabb60f1cc3409186a5d4e2f",
    "asset_type": "crop",
    "asset_role": "region_crop",
    "source_uri": null,
    "storage_uri": "outputs/user_requested_batch_review/pipeline_runs/run_637ca3432da6ddfb/datasets/multi_physics/artifacts/crops/prob_eabb60f1cc3409186a5d4e2f_primary_roi.png",
    "file_format": "png",
    "file_size_bytes": 8953,
    "width": 551,
    "height": 247,
    "sha256": "6a021a4de3b3a623dcb4412e310f23b99665f45b9ec469b5453ae455eb90b07b",
    "perceptual_hash": "1f7f433f7f7f0000",
    "source_text_snapshot": null,
    "normalized_text_snapshot": null,
    "text_completeness_score": null,
    "blur_score": 5342.2017,
    "readability_score": 0.8178,
    "noise_score": 31.5641,
    "cropped_from_asset_id": "asset_291737e5e43d05a0c69844b9",
    "roi_bbox": {
      "x": 13,
      "y": 5,
      "width": 551,
      "height": 247
    },
    "asset_quality_flags": [],
    "is_usable": true,
    "discard_reason_codes": [],
    "created_at": "2026-03-24T07:48:58Z",
    "updated_at": "2026-03-24T07:48:58Z"
  },
  {
    "asset_id": "asset_78e39087e09f59f5be6f78fe",
    "problem_id": "prob_eabb60f1cc3409186a5d4e2f",
    "asset_type": "text",
    "asset_role": "question_text_open_variant",
    "source_uri": null,
    "storage_uri": "inline://open_1d08e45644522516238990ac",
    "file_format": "txt",
    "file_size_bytes": 271,
    "width": null,
    "height": null,
    "sha256": "7f956dcd64b5cf7c70621457cf58109cc6f3a8a19bd357fff56a0edfa32db557",
    "perceptual_hash": null,
    "source_text_snapshot": "电动车由静止开始在平直的公路上行驶，其运动的v—t图象如图所示。\nA. 12s末电动车的加速度大小为1/3m/s2\nB. 0~20s内电动车的平均速度为2.5m/s\nC. 0~50s内电动车的位移大小为200m\nD. 0~50s内电动车的平均速度大于4m/s",
    "normalized_text_snapshot": "电动车由静止开始在平直的公路上行驶,其运动的v—t图象如图所示。\nA. 12s末电动车的加速度大小为1/3m/s2\nB. 0~20s内电动车的平均速度为2.5m/s\nC. 0~50s内电动车的位移大小为200m\nD. 0~50s内电动车的平均速度大于4m/s",
    "text_completeness_score": 0.6652,
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
        "original": "s2",
        "canonical": "s2",
        "variable_type": "label"
      },
      {
        "original": "B",
        "canonical": "B",
        "variable_type": "symbol"
      },
      {
        "original": "s",
        "canonical": "s",
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
    "created_at": "2026-03-24T07:48:58Z",
    "updated_at": "2026-03-24T07:48:58Z"
  }
]
```

#### node_records

```json
[
  {
    "node_id": "node_0dc0bb9ddf965391df4b68bb",
    "problem_id": "prob_eabb60f1cc3409186a5d4e2f",
    "node_type": "text_fact",
    "canonical_value": "电动车由静止开始在平直的公路上行驶,其运动的v—t图象如图所示。",
    "surface_forms": [
      "电动车由静止开始在平直的公路上行驶,其运动的v—t图象如图所示。"
    ],
    "origin_kind": "text",
    "cognitive_level": "objective",
    "source_refs": [
      "asset_aca400e65591162d786be3df"
    ],
    "evidence_refs": [
      "asset_aca400e65591162d786be3df"
    ],
    "upstream_node_ids": [],
    "value_type": "condition",
    "normalized_value": {
      "text": "电动车由静止开始在平直的公路上行驶,其运动的v—t图象如图所示。",
      "segment_index": 1,
      "mentions_visual": false,
      "numeric_tokens": [],
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
    "created_at": "2026-03-24T07:48:58Z",
    "updated_at": "2026-03-24T07:48:58Z"
  },
  {
    "node_id": "node_8be9b3a5dc5f2f14232a8aa1",
    "problem_id": "prob_eabb60f1cc3409186a5d4e2f",
    "node_type": "text_fact",
    "canonical_value": "12s末电动车的加速度大小为1/3m/s2",
    "surface_forms": [
      "12s末电动车的加速度大小为1/3m/s2"
    ],
    "origin_kind": "text",
    "cognitive_level": "objective",
    "source_refs": [
      "asset_aca400e65591162d786be3df"
    ],
    "evidence_refs": [
      "asset_aca400e65591162d786be3df"
    ],
    "upstream_node_ids": [],
    "value_type": "condition",
    "normalized_value": {
      "text": "12s末电动车的加速度大小为1/3m/s2",
      "segment_index": 3,
      "mentions_visual": false,
      "numeric_tokens": [
        "12",
        "1",
        "3",
        "2"
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
    "created_at": "2026-03-24T07:48:58Z",
    "updated_at": "2026-03-24T07:48:58Z"
  },
  {
    "node_id": "node_5d9f47b3a4c950cb651c1d4d",
    "problem_id": "prob_eabb60f1cc3409186a5d4e2f",
    "node_type": "text_fact",
    "canonical_value": "0~20s内电动车的平均速度为2.5m/s",
    "surface_forms": [
      "0~20s内电动车的平均速度为2.5m/s"
    ],
    "origin_kind": "text",
    "cognitive_level": "objective",
    "source_refs": [
      "asset_aca400e65591162d786be3df"
    ],
    "evidence_refs": [
      "asset_aca400e65591162d786be3df"
    ],
    "upstream_node_ids": [],
    "value_type": "condition",
    "normalized_value": {
      "text": "0~20s内电动车的平均速度为2.5m/s",
      "segment_index": 5,
      "mentions_visual": false,
      "numeric_tokens": [
        "0",
        "20",
        "2.5"
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
    "created_at": "2026-03-24T07:48:58Z",
    "updated_at": "2026-03-24T07:48:58Z"
  },
  {
    "node_id": "node_9de13c41bf639c4952ac0b32",
    "problem_id": "prob_eabb60f1cc3409186a5d4e2f",
    "node_type": "text_fact",
    "canonical_value": "0~50s内电动车的位移大小为200m",
    "surface_forms": [
      "0~50s内电动车的位移大小为200m"
    ],
    "origin_kind": "text",
    "cognitive_level": "objective",
    "source_refs": [
      "asset_aca400e65591162d786be3df"
    ],
    "evidence_refs": [
      "asset_aca400e65591162d786be3df"
    ],
    "upstream_node_ids": [],
    "value_type": "condition",
    "normalized_value": {
      "text": "0~50s内电动车的位移大小为200m",
      "segment_index": 7,
      "mentions_visual": false,
      "numeric_tokens": [
        "0",
        "50",
        "200"
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
    "created_at": "2026-03-24T07:48:58Z",
    "updated_at": "2026-03-24T07:48:58Z"
  },
  {
    "node_id": "node_9f7efc458393482c3465749d",
    "problem_id": "prob_eabb60f1cc3409186a5d4e2f",
    "node_type": "text_fact",
    "canonical_value": "0~50s内电动车的平均速度大于4m/s",
    "surface_forms": [
      "0~50s内电动车的平均速度大于4m/s"
    ],
    "origin_kind": "text",
    "cognitive_level": "objective",
    "source_refs": [
      "asset_aca400e65591162d786be3df"
    ],
    "evidence_refs": [
      "asset_aca400e65591162d786be3df"
    ],
    "upstream_node_ids": [],
    "value_type": "condition",
    "normalized_value": {
      "text": "0~50s内电动车的平均速度大于4m/s",
      "segment_index": 9,
      "mentions_visual": false,
      "numeric_tokens": [
        "0",
        "50",
        "4"
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
    "created_at": "2026-03-24T07:48:58Z",
    "updated_at": "2026-03-24T07:48:58Z"
  },
  {
    "node_id": "node_9b4b92ebf1e9d9d6b275fdd4",
    "problem_id": "prob_eabb60f1cc3409186a5d4e2f",
    "node_type": "target_slot",
    "canonical_value": "0~50s内电动车的平均速度大于4m/s",
    "surface_forms": [
      "0~50s内电动车的平均速度大于4m/s"
    ],
    "origin_kind": "text_structure",
    "cognitive_level": "computed",
    "source_refs": [
      "asset_aca400e65591162d786be3df"
    ],
    "evidence_refs": [
      "asset_aca400e65591162d786be3df"
    ],
    "upstream_node_ids": [],
    "value_type": "option",
    "normalized_value": {
      "slot_id": "slot_prob_eabb60f1cc3409186a5d4e2f_1",
      "variant_index": 1,
      "split_role": "single",
      "slot_type": "option",
      "target_text": "0~50s内电动车的平均速度大于4m/s",
      "expected_answer_type": "option",
      "expected_answer": "D",
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
    "created_at": "2026-03-24T07:48:58Z",
    "updated_at": "2026-03-24T07:48:58Z"
  },
  {
    "node_id": "node_c8b9c793055408f923b4a29e",
    "problem_id": "prob_eabb60f1cc3409186a5d4e2f",
    "node_type": "answer_claim",
    "canonical_value": "D",
    "surface_forms": [
      "D"
    ],
    "origin_kind": "text",
    "cognitive_level": "objective",
    "source_refs": [
      "asset_0dc6491c9db7ad693a3fc531"
    ],
    "evidence_refs": [
      "asset_0dc6491c9db7ad693a3fc531"
    ],
    "upstream_node_ids": [],
    "value_type": "option",
    "normalized_value": {
      "answer": "D"
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
    "created_at": "2026-03-24T07:48:58Z",
    "updated_at": "2026-03-24T07:48:58Z"
  },
  {
    "node_id": "node_64fa52e63a7681471f603f3f",
    "problem_id": "prob_eabb60f1cc3409186a5d4e2f",
    "node_type": "perception_fact",
    "canonical_value": "primary_image::full_canvas::canvas",
    "surface_forms": [
      "canvas"
    ],
    "origin_kind": "vision",
    "cognitive_level": "objective",
    "source_refs": [
      "visual_prob_eabb60f1cc3409186a5d4e2f_1"
    ],
    "evidence_refs": [
      "visual_prob_eabb60f1cc3409186a5d4e2f_1"
    ],
    "upstream_node_ids": [],
    "value_type": "full_canvas",
    "normalized_value": {
      "entity_id": "canvas",
      "entity_type": "full_canvas",
      "bbox": {
        "x": 0,
        "y": 0,
        "width": 580,
        "height": 257
      },
      "salience": 1.0
    },
    "unit": null,
    "confidence": 0.9271,
    "verifiability": "medium",
    "ambiguity_level": "low",
    "is_direct_from_source": false,
    "is_generated_by_system": true,
    "is_reviewed_by_human": false,
    "stage_created": "cleaning",
    "status": "active",
    "version": 1,
    "created_at": "2026-03-24T07:48:58Z",
    "updated_at": "2026-03-24T07:48:58Z"
  },
  {
    "node_id": "node_39ce216578e4743e5d673e56",
    "problem_id": "prob_eabb60f1cc3409186a5d4e2f",
    "node_type": "perception_fact",
    "canonical_value": "primary_image::content_region::roi",
    "surface_forms": [
      "roi"
    ],
    "origin_kind": "vision",
    "cognitive_level": "objective",
    "source_refs": [
      "visual_prob_eabb60f1cc3409186a5d4e2f_1"
    ],
    "evidence_refs": [
      "visual_prob_eabb60f1cc3409186a5d4e2f_1"
    ],
    "upstream_node_ids": [],
    "value_type": "content_region",
    "normalized_value": {
      "entity_id": "roi",
      "entity_type": "content_region",
      "bbox": {
        "x": 13,
        "y": 5,
        "width": 551,
        "height": 247
      },
      "salience": 0.95
    },
    "unit": null,
    "confidence": 0.9271,
    "verifiability": "medium",
    "ambiguity_level": "low",
    "is_direct_from_source": false,
    "is_generated_by_system": true,
    "is_reviewed_by_human": false,
    "stage_created": "cleaning",
    "status": "active",
    "version": 1,
    "created_at": "2026-03-24T07:48:58Z",
    "updated_at": "2026-03-24T07:48:58Z"
  },
  {
    "node_id": "node_7302505833c5bf7d0712110d",
    "problem_id": "prob_eabb60f1cc3409186a5d4e2f",
    "node_type": "perception_fact",
    "canonical_value": "primary_image::subregion::roi_top_left",
    "surface_forms": [
      "roi_top_left"
    ],
    "origin_kind": "vision",
    "cognitive_level": "objective",
    "source_refs": [
      "visual_prob_eabb60f1cc3409186a5d4e2f_1"
    ],
    "evidence_refs": [
      "visual_prob_eabb60f1cc3409186a5d4e2f_1"
    ],
    "upstream_node_ids": [],
    "value_type": "subregion",
    "normalized_value": {
      "entity_id": "roi_top_left",
      "entity_type": "subregion",
      "bbox": {
        "x": 13,
        "y": 5,
        "width": 275,
        "height": 123
      },
      "salience": 0.411
    },
    "unit": null,
    "confidence": 0.9271,
    "verifiability": "medium",
    "ambiguity_level": "low",
    "is_direct_from_source": false,
    "is_generated_by_system": true,
    "is_reviewed_by_human": false,
    "stage_created": "cleaning",
    "status": "active",
    "version": 1,
    "created_at": "2026-03-24T07:48:58Z",
    "updated_at": "2026-03-24T07:48:58Z"
  },
  {
    "node_id": "node_c0ca8b624e15724c7bddbfaf",
    "problem_id": "prob_eabb60f1cc3409186a5d4e2f",
    "node_type": "perception_fact",
    "canonical_value": "primary_image::subregion::roi_bottom_left",
    "surface_forms": [
      "roi_bottom_left"
    ],
    "origin_kind": "vision",
    "cognitive_level": "objective",
    "source_refs": [
      "visual_prob_eabb60f1cc3409186a5d4e2f_1"
    ],
    "evidence_refs": [
      "visual_prob_eabb60f1cc3409186a5d4e2f_1"
    ],
    "upstream_node_ids": [],
    "value_type": "subregion",
    "normalized_value": {
      "entity_id": "roi_bottom_left",
      "entity_type": "subregion",
      "bbox": {
        "x": 13,
        "y": 128,
        "width": 275,
        "height": 124
      },
      "salience": 0.412
    },
    "unit": null,
    "confidence": 0.9271,
    "verifiability": "medium",
    "ambiguity_level": "low",
    "is_direct_from_source": false,
    "is_generated_by_system": true,
    "is_reviewed_by_human": false,
    "stage_created": "cleaning",
    "status": "active",
    "version": 1,
    "created_at": "2026-03-24T07:48:58Z",
    "updated_at": "2026-03-24T07:48:58Z"
  },
  {
    "node_id": "node_07294330be67eec0b79081c2",
    "problem_id": "prob_eabb60f1cc3409186a5d4e2f",
    "node_type": "perception_fact",
    "canonical_value": "primary_image::subregion::roi_bottom_right",
    "surface_forms": [
      "roi_bottom_right"
    ],
    "origin_kind": "vision",
    "cognitive_level": "objective",
    "source_refs": [
      "visual_prob_eabb60f1cc3409186a5d4e2f_1"
    ],
    "evidence_refs": [
      "visual_prob_eabb60f1cc3409186a5d4e2f_1"
    ],
    "upstream_node_ids": [],
    "value_type": "subregion",
    "normalized_value": {
      "entity_id": "roi_bottom_right",
      "entity_type": "subregion",
      "bbox": {
        "x": 288,
        "y": 128,
        "width": 276,
        "height": 124
      },
      "salience": 0.4007
    },
    "unit": null,
    "confidence": 0.9271,
    "verifiability": "medium",
    "ambiguity_level": "low",
    "is_direct_from_source": false,
    "is_generated_by_system": true,
    "is_reviewed_by_human": false,
    "stage_created": "cleaning",
    "status": "active",
    "version": 1,
    "created_at": "2026-03-24T07:48:58Z",
    "updated_at": "2026-03-24T07:48:58Z"
  },
  {
    "node_id": "node_8be169f4330966e3e5ea3245",
    "problem_id": "prob_eabb60f1cc3409186a5d4e2f",
    "node_type": "text_fact",
    "canonical_value": "电动车由静止开始在平直的公路上行驶,其运动的v—t图象如图所示。\nA. 12s末电动车的加速度大小为1/3m/s2\nB. 0~20s内电动车的平均速度为2.5m/s\nC. 0~50s内电动车的位移大小为200m\nD. 0~50s内电动车的平均速度大于4m/s",
    "surface_forms": [
      "电动车由静止开始在平直的公路上行驶,其运动的v—t图象如图所示。\nA. 12s末电动车的加速度大小为1/3m/s2\nB. 0~20s内电动车的平均速度为2.5m/s\nC. 0~50s内电动车的位移大小为200m\nD. 0~50s内电动车的平均速度大于4m/s"
    ],
    "origin_kind": "reasoning",
    "cognitive_level": "computed",
    "source_refs": [
      "asset_78e39087e09f59f5be6f78fe"
    ],
    "evidence_refs": [
      "asset_78e39087e09f59f5be6f78fe"
    ],
    "upstream_node_ids": [],
    "value_type": "text",
    "normalized_value": {
      "open_variant_id": "open_1d08e45644522516238990ac",
      "parent_problem_id": "prob_eabb60f1cc3409186a5d4e2f",
      "variant_index": 1,
      "title": "muti- physics 开放题",
      "rewritten_question_text": "电动车由静止开始在平直的公路上行驶,其运动的v—t图象如图所示。\nA. 12s末电动车的加速度大小为1/3m/s2\nB. 0~20s内电动车的平均速度为2.5m/s\nC. 0~50s内电动车的位移大小为200m\nD. 0~50s内电动车的平均速度大于4m/s",
      "expected_answer_type": "option",
      "expected_answer": "D",
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
    "created_at": "2026-03-24T07:48:58Z",
    "updated_at": "2026-03-24T07:48:58Z"
  },
  {
    "node_id": "node_bdf8d64eddc28f838effafa8",
    "problem_id": "prob_eabb60f1cc3409186a5d4e2f",
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
      "solvability_id": "solv_prob_eabb60f1cc3409186a5d4e2f",
      "problem_id": "prob_eabb60f1cc3409186a5d4e2f",
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
      "created_at": "2026-03-24T07:48:58Z"
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
    "created_at": "2026-03-24T07:48:58Z",
    "updated_at": "2026-03-24T07:48:58Z"
  },
  {
    "node_id": "node_8665fe5101569c1f4bcd917c",
    "problem_id": "prob_eabb60f1cc3409186a5d4e2f",
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
    "created_at": "2026-03-24T07:48:58Z",
    "updated_at": "2026-03-24T07:48:58Z"
  }
]
```

#### field_audit_records

```json
[
  {
    "audit_id": "audit_dd0b7edf78af4e401a7d91ed",
    "problem_id": "prob_eabb60f1cc3409186a5d4e2f",
    "record_type": "problem_main_record",
    "field_name": "normalized_question_text",
    "before_value": "电动车由静止开始在平直的公路上行驶，其运动的v—t图象如图所示。\nA. 12s末电动车的加速度大小为1/3m/s2\nB. 0~20s内电动车的平均速度为2.5m/s\nC. 0~50s内电动车的位移大小为200m\nD. 0~50s内电动车的平均速度大于4m/s",
    "after_value": "电动车由静止开始在平直的公路上行驶,其运动的v—t图象如图所示。\nA. 12s末电动车的加速度大小为1/3m/s2\nB. 0~20s内电动车的平均速度为2.5m/s\nC. 0~50s内电动车的位移大小为200m\nD. 0~50s内电动车的平均速度大于4m/s",
    "change_type": "text_normalized",
    "trigger": "NormalizationAgent",
    "operator_type": "system",
    "created_at": "2026-03-24T07:48:58Z"
  },
  {
    "audit_id": "audit_c52de8e84bdcd15db4b61087",
    "problem_id": "prob_eabb60f1cc3409186a5d4e2f",
    "record_type": "problem_main_record",
    "field_name": "normalized_answer_text",
    "before_value": "D",
    "after_value": "D",
    "change_type": "answer_canonicalized",
    "trigger": "NormalizationAgent",
    "operator_type": "system",
    "created_at": "2026-03-24T07:48:58Z"
  },
  {
    "audit_id": "audit_930ccd9523c7c8cbd92ec16f",
    "problem_id": "prob_eabb60f1cc3409186a5d4e2f",
    "record_type": "rewrite_report",
    "field_name": "rewrite_strategy",
    "before_value": null,
    "after_value": "keep_open",
    "change_type": "question_rewritten",
    "trigger": "QuestionRewriteAgent",
    "operator_type": "system",
    "created_at": "2026-03-24T07:48:58Z"
  },
  {
    "audit_id": "audit_8665fe5101569c1f4bcd917c",
    "problem_id": "prob_eabb60f1cc3409186a5d4e2f",
    "record_type": "cleaning_record",
    "field_name": "decision",
    "before_value": null,
    "after_value": "pass",
    "change_type": "gate_decision",
    "trigger": "CleanGateAgent",
    "operator_type": "system",
    "created_at": "2026-03-24T07:48:58Z"
  },
  {
    "audit_id": "audit_effa6982c6692958be8c6d31",
    "problem_id": "prob_eabb60f1cc3409186a5d4e2f",
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
        "original": "s2",
        "canonical": "s2",
        "variable_type": "label"
      },
      {
        "original": "B",
        "canonical": "B",
        "variable_type": "symbol"
      },
      {
        "original": "s",
        "canonical": "s",
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
    "created_at": "2026-03-24T07:48:58Z"
  }
]
```

#### reject_records

```json
[]
```

### 4.1 完整 sample bundle 原文件

- `outputs/user_requested_batch_review/pipeline_runs/run_637ca3432da6ddfb/datasets/multi_physics/samples/prob_eabb60f1cc3409186a5d4e2f.json`
