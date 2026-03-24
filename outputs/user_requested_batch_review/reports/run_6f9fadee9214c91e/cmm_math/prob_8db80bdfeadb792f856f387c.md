# CMM-Math / prob_8db80bdfeadb792f856f387c

- source_problem_id: `19900`
- source_split: `train`
- clean_decision: `pass`
- rewrite_strategy: `blank_open`
- full sample bundle JSON: `outputs/user_requested_batch_review/pipeline_runs/run_6f9fadee9214c91e/datasets/cmm_math/samples/prob_8db80bdfeadb792f856f387c.json`

## 1. 原始内容（处理前）

### 1.1 原始快照

```json
{
  "dataset_key": "cmm_math",
  "source_problem_id": "19900",
  "source_split": "train",
  "raw_question_text": "在平面直角坐标系 $x O y$ 中, $M$ 为不等式组 $\\left\\{\\begin{array}{l}2 x-y-2 \\geq 0, \\\\ x+2 y-1 \\geq 0, \\\\ 3 x+y-8 \\leq 0\\end{array}\\right.$ 所表示的区域上一动点,则直线 OM 斜率的最小值为 ( )",
  "raw_answer_text": "A",
  "choice_map": {
    "A": "$-\\frac{1}{3}$",
    "B": "$-\\frac{1}{2}$",
    "C": "1",
    "D": "2"
  },
  "image_sources": [],
  "metadata": {
    "row_index": 9,
    "question_field": "question",
    "answer_field": "answer",
    "image_field": "image",
    "choice_field": "options"
  },
  "raw_record": {
    "id": "19900",
    "image": "[\"9285.jpg\"]",
    "answer": "A",
    "solution": "null",
    "level": "高二",
    "question": "在平面直角坐标系 $x O y$ 中, $M$ 为不等式组 $\\left\\{\\begin{array}{l}2 x-y-2 \\geq 0, \\\\ x+2 y-1 \\geq 0, \\\\ 3 x+y-8 \\leq 0\\end{array}\\right.$ 所表示的区域上一动点,则直线 OM 斜率的最小值为 ( )",
    "options": "A. $-\\frac{1}{3}$\nB. $-\\frac{1}{2}$\nC. 1\nD. 2",
    "subject": "解析几何",
    "analysis": "由线性约束条件可知其对应的可行域如图, 通过观察图象可知当过原点的直线经过点 A 的时候斜率最小,\n\n<ImageHere>\n\n由方程组 $\\left\\{\\begin{array}{l}3 x+y-8=0, \\\\ x+2 y-1=0\\end{array}\\right.$ 得 $A(3,-1)$, 所以直线 $\\mathrm{OM}$ 斜率的最小值为 $k=\\frac{-1}{3}=-\\frac{1}{3}$."
  }
}
```

## 2. 处理前后对照

### 2.1 关键字段对照

| 字段 | 处理前 | 处理后 |
| --- | --- | --- |
| question_text | 在平面直角坐标系 $x O y$ 中, $M$ 为不等式组 $\left\{\begin{array}{l}2 x-y-2 \geq 0, \\ x+2 y-1 \geq 0, \\ 3 x+y-8 \leq 0\end{array}\right.$ 所表示的区域上一动点,则直线 OM 斜率的最小值为 ( ) | 在平面直角坐标系 $x O y$ 中, $M$ 为不等式组 $\left\{\begin{array}{l}2 x-y-2 \geq 0, \\ x+2 y-1 \geq 0, \\ 3 x+y-8 \leq 0\end{array}\right.$ 所表示的区域上一动点,则直线 OM 斜率的最小值为 ( ) |
| answer_text | A | A |
| answer_type | - | option |
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
  "problem_id": "prob_8db80bdfeadb792f856f387c",
  "source_dataset": "CMM-Math",
  "source_split": "train",
  "source_problem_id": "19900",
  "ingest_batch_id": "multidataset-clean_20260324T063656Z",
  "problem_type": "multimodal_reasoning",
  "domain_tags": [
    "数学"
  ],
  "language": "zh",
  "raw_question_text": "在平面直角坐标系 $x O y$ 中, $M$ 为不等式组 $\\left\\{\\begin{array}{l}2 x-y-2 \\geq 0, \\\\ x+2 y-1 \\geq 0, \\\\ 3 x+y-8 \\leq 0\\end{array}\\right.$ 所表示的区域上一动点,则直线 OM 斜率的最小值为 ( )",
  "normalized_question_text": "在平面直角坐标系 $x O y$ 中, $M$ 为不等式组 $\\left\\{\\begin{array}{l}2 x-y-2 \\geq 0, \\\\ x+2 y-1 \\geq 0, \\\\ 3 x+y-8 \\leq 0\\end{array}\\right.$ 所表示的区域上一动点,则直线 OM 斜率的最小值为 ( )",
  "raw_answer_text": "A",
  "normalized_answer_text": "A",
  "answer_type": "option",
  "image_count": 0,
  "has_multiple_images": false,
  "requires_image": false,
  "multimodal_strength_score": 0.48,
  "multi_step_score": 0.3737,
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
  "candidate_id": "cand_8db80bdfeadb792f856f387c",
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
  "clean_problem_record_id": "cleanprob_a12c25b08257370c0f8b2176",
  "problem_id": "prob_8db80bdfeadb792f856f387c",
  "source_dataset": "CMM-Math",
  "source_problem_id": "19900",
  "normalized_question_text": "在平面直角坐标系 $x O y$ 中, $M$ 为不等式组 $\\left\\{\\begin{array}{l}2 x-y-2 \\geq 0, \\\\ x+2 y-1 \\geq 0, \\\\ 3 x+y-8 \\leq 0\\end{array}\\right.$ 所表示的区域上一动点,则直线 OM 斜率的最小值为 ( )",
  "normalized_answer_text": "A",
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
  "created_at": "2026-03-24T06:37:02Z"
}
```

#### normalized_assets

```json
{
  "normalized_assets_id": "nassets_a12c25b08257370c0f8b2176",
  "problem_id": "prob_8db80bdfeadb792f856f387c",
  "normalized_question_text": "在平面直角坐标系 $x O y$ 中, $M$ 为不等式组 $\\left\\{\\begin{array}{l}2 x-y-2 \\geq 0, \\\\ x+2 y-1 \\geq 0, \\\\ 3 x+y-8 \\leq 0\\end{array}\\right.$ 所表示的区域上一动点,则直线 OM 斜率的最小值为 ( )",
  "normalized_answer_text": "A",
  "question_unit_normalization_map": [],
  "answer_unit_normalization_map": [],
  "variable_aliases": [
    {
      "original": "x",
      "canonical": "x",
      "variable_type": "symbol"
    },
    {
      "original": "O",
      "canonical": "O",
      "variable_type": "symbol"
    },
    {
      "original": "y",
      "canonical": "y",
      "variable_type": "symbol"
    },
    {
      "original": "M",
      "canonical": "M",
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
      "original": "OM",
      "canonical": "OM",
      "variable_type": "label"
    }
  ],
  "sentence_segments": [
    {
      "segment_index": 1,
      "text": "在平面直角坐标系 $x O y$ 中, $M$ 为不等式组 $\\left\\{\\begin{array}{l}2 x-y-2 \\geq 0, \\\\ x+2 y-1 \\geq 0, \\\\ 3 x+y-8 \\leq 0\\end{array}\\right.$ 所表示的区域上一动点,则直线 OM 斜率的最小值为 ( )"
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
  "text_structure_id": "text_prob_8db80bdfeadb792f856f387c",
  "problem_id": "prob_8db80bdfeadb792f856f387c",
  "question_type": "multiple_choice",
  "conditions": [
    {
      "text": "在平面直角坐标系 $x O y$ 中, $M$ 为不等式组 $\\left\\{\\begin{array}{l}2 x-y-2 \\geq 0, \\\\ x+2 y-1 \\geq 0, \\\\ 3 x+y-8 \\leq 0\\end{array}\\right.$ 所表示的区域上一动点,则直线 OM 斜率的最小值为 ( )",
      "segment_index": 1,
      "mentions_visual": false,
      "numeric_tokens": [
        "2",
        "-2",
        "0",
        "+2",
        "-1",
        "0",
        "3",
        "-8",
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
      "text": "在平面直角坐标系 $x O y$ 中, $M$ 为不等式组 $\\left\\{\\begin{array}{l}2 x-y-2 \\geq 0, \\\\ x+2 y-1 \\geq 0, \\\\ 3 x+y-8 \\leq 0\\end{array}\\right.$ 所表示的区域上一动点,则直线 OM 斜率的最小值为 ( )",
      "segment_index": 1,
      "mentions_visual": false,
      "numeric_tokens": [
        "2",
        "-2",
        "0",
        "+2",
        "-1",
        "0",
        "3",
        "-8",
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
      "slot_id": "slot_prob_8db80bdfeadb792f856f387c_1",
      "variant_index": 1,
      "split_role": "single",
      "slot_type": "numeric",
      "target_text": "在平面直角坐标系 $x O y$ 中, $M$ 为不等式组 $\\left\\{\\begin{array}{l}2 x-y-2 \\geq 0, \\\\ x+2 y-1 \\geq 0, \\\\ 3 x+y-8 \\leq 0\\end{array}\\right.$ 所表示的区域上一动点,则直线 OM 斜率的最小值为 ( )",
      "expected_answer_type": "numeric",
      "expected_answer": "$-\\frac{1}{3}$",
      "requires_visual_grounding": false
    }
  ],
  "entity_mentions": [
    {
      "mention": "O",
      "entity_category": "label",
      "requires_visual_grounding": true
    },
    {
      "mention": "M",
      "entity_category": "label",
      "requires_visual_grounding": true
    },
    {
      "mention": "OM",
      "entity_category": "label",
      "requires_visual_grounding": true
    }
  ],
  "variable_aliases": [
    {
      "original": "x",
      "canonical": "x",
      "variable_type": "symbol"
    },
    {
      "original": "O",
      "canonical": "O",
      "variable_type": "symbol"
    },
    {
      "original": "y",
      "canonical": "y",
      "variable_type": "symbol"
    },
    {
      "original": "M",
      "canonical": "M",
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
      "original": "OM",
      "canonical": "OM",
      "variable_type": "label"
    }
  ],
  "unit_mentions": [
    "A",
    "g",
    "h"
  ],
  "sentence_segments": [
    {
      "segment_index": 1,
      "text": "在平面直角坐标系 $x O y$ 中, $M$ 为不等式组 $\\left\\{\\begin{array}{l}2 x-y-2 \\geq 0, \\\\ x+2 y-1 \\geq 0, \\\\ 3 x+y-8 \\leq 0\\end{array}\\right.$ 所表示的区域上一动点,则直线 OM 斜率的最小值为 ( )"
    }
  ],
  "requires_visual_grounding": true,
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
  "alignment_id": "align_a12c25b08257370c0f8b2176",
  "problem_id": "prob_8db80bdfeadb792f856f387c",
  "image_entity_refs": [],
  "text_span_refs": [
    "asset_prob_8db80bdfeadb792f856f387c_question_text_normalized"
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
  "solvability_id": "solv_prob_8db80bdfeadb792f856f387c",
  "problem_id": "prob_8db80bdfeadb792f856f387c",
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
  "cleaning_id": "clean_a12c25b08257370c0f8b2176",
  "problem_id": "prob_8db80bdfeadb792f856f387c",
  "cleaning_version": "v3.0.0",
  "pipeline_run_id": "run_6f9fadee9214c91e",
  "dataset_name": "CMM-Math",
  "input_asset_ids": [
    "asset_2126f04172784ffe95e7bbc2",
    "asset_483716380a482cb8a75fe098",
    "asset_dd5843439282ce16eb7cad23",
    "asset_f61423934b1d3777d7c9373a",
    "asset_e032ca8e929e93e32d574822"
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
      "variable_alias_count": 10
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
    "alignment_id": "align_a12c25b08257370c0f8b2176",
    "coverage_score": 1.0,
    "consistency_score": 1.0,
    "alignment_status": "good",
    "conflict_count": 0
  },
  "text_structure_summary": {
    "text_structure_id": "text_prob_8db80bdfeadb792f856f387c",
    "question_type": "multiple_choice",
    "condition_count": 1,
    "target_count": 1,
    "answer_slot_count": 1,
    "status": "complete"
  },
  "solvability_summary": {
    "solvability_id": "solv_prob_8db80bdfeadb792f856f387c",
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
  "clean_score": 0.8709,
  "decision": "pass",
  "decision_reason_codes": [
    "meets_cleaning_requirements"
  ],
  "review_ticket_id": null,
  "operator_type": "system",
  "started_at": "2026-03-24T06:37:02Z",
  "finished_at": "2026-03-24T06:37:02Z",
  "candidate_id": "cand_8db80bdfeadb792f856f387c",
  "cleaning_path": "text_lightweight",
  "text_dominant": true
}
```

## 3. 开放化改写前后

### 3.1 改写前

```json
{
  "question_text_before_rewrite": "在平面直角坐标系 $x O y$ 中, $M$ 为不等式组 $\\left\\{\\begin{array}{l}2 x-y-2 \\geq 0, \\\\ x+2 y-1 \\geq 0, \\\\ 3 x+y-8 \\leq 0\\end{array}\\right.$ 所表示的区域上一动点,则直线 OM 斜率的最小值为 ( )",
  "answer_text_before_rewrite": "A",
  "raw_question_text": "在平面直角坐标系 $x O y$ 中, $M$ 为不等式组 $\\left\\{\\begin{array}{l}2 x-y-2 \\geq 0, \\\\ x+2 y-1 \\geq 0, \\\\ 3 x+y-8 \\leq 0\\end{array}\\right.$ 所表示的区域上一动点,则直线 OM 斜率的最小值为 ( )",
  "raw_answer_text": "A"
}
```

### 3.2 改写后

```json
{
  "rewrite_report": {
    "rewrite_id": "rewrite_a12c25b08257370c0f8b2176",
    "problem_id": "prob_8db80bdfeadb792f856f387c",
    "source_problem_id": "19900",
    "strategy": "blank_open",
    "rationale": "Converted multiple choice into blank-style open-ended question.",
    "discard_reason_codes": [],
    "variant_count": 1,
    "variants": [
      {
        "open_variant_id": "open_1fc5d60b9a7bfd67ec15427a",
        "parent_problem_id": "prob_8db80bdfeadb792f856f387c",
        "variant_index": 1,
        "title": "CMM-Math 开放题",
        "rewritten_question_text": "在平面直角坐标系 $x O y$ 中, $M$ 为不等式组 $\\left\\{\\begin{array}{l}2 x-y-2 \\geq 0, \\\\ x+2 y-1 \\geq 0, \\\\ 3 x+y-8 \\leq 0\\end{array}\\right.$ 所表示的区域上一动点,则直线 OM 斜率的最小值为 ( )",
        "expected_answer_type": "numeric",
        "expected_answer": "$-\\frac{1}{3}$",
        "split_role": "single"
      }
    ],
    "created_at": "2026-03-24T06:37:02Z"
  },
  "open_ended_problem_variants": [
    {
      "open_variant_id": "open_1fc5d60b9a7bfd67ec15427a",
      "parent_problem_id": "prob_8db80bdfeadb792f856f387c",
      "variant_index": 1,
      "title": "CMM-Math 开放题",
      "rewritten_question_text": "在平面直角坐标系 $x O y$ 中, $M$ 为不等式组 $\\left\\{\\begin{array}{l}2 x-y-2 \\geq 0, \\\\ x+2 y-1 \\geq 0, \\\\ 3 x+y-8 \\leq 0\\end{array}\\right.$ 所表示的区域上一动点,则直线 OM 斜率的最小值为 ( )",
      "expected_answer_type": "numeric",
      "expected_answer": "$-\\frac{1}{3}$",
      "split_role": "single"
    }
  ]
}
```

## 4. 完整 collection + cleaning 输出对象

#### candidate_problem_record

```json
{
  "candidate_id": "cand_8db80bdfeadb792f856f387c",
  "source_dataset": "CMM-Math",
  "source_split": "train",
  "source_problem_id": "19900",
  "subject": "数学",
  "raw_question_text": "在平面直角坐标系 $x O y$ 中, $M$ 为不等式组 $\\left\\{\\begin{array}{l}2 x-y-2 \\geq 0, \\\\ x+2 y-1 \\geq 0, \\\\ 3 x+y-8 \\leq 0\\end{array}\\right.$ 所表示的区域上一动点,则直线 OM 斜率的最小值为 ( )",
  "raw_answer_text": "A",
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
    "row_index": 9,
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
  "raw_asset_bundle_id": "bundle_7371d9eb78439fa14019e72e",
  "candidate_id": "cand_8db80bdfeadb792f856f387c",
  "source_dataset": "CMM-Math",
  "source_problem_id": "19900",
  "assets": [
    {
      "asset_role": "question_text_raw",
      "storage_uri": "inline://prob_8db80bdfeadb792f856f387c/question_source",
      "is_present": true
    },
    {
      "asset_role": "answer_text_raw",
      "storage_uri": "inline://prob_8db80bdfeadb792f856f387c/answer_source",
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
  "candidate_pool_entry_id": "cpool_ea2bc58ad45d11ce4130bb6d",
  "candidate_id": "cand_8db80bdfeadb792f856f387c",
  "source_dataset": "CMM-Math",
  "source_problem_id": "19900",
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
    "clean_pool_entry_id": "cleanpool_a12c25b08257370c0f8b2176",
    "candidate_id": "cand_8db80bdfeadb792f856f387c",
    "problem_id": "prob_8db80bdfeadb792f856f387c",
    "dataset_name": "CMM-Math",
    "pool_status": "ready_for_annotation",
    "clean_decision": "pass",
    "review_required": false,
    "rewrite_strategy": "blank_open",
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
    "rewrite_id": "rewrite_a12c25b08257370c0f8b2176",
    "problem_id": "prob_8db80bdfeadb792f856f387c",
    "source_problem_id": "19900",
    "strategy": "blank_open",
    "rationale": "Converted multiple choice into blank-style open-ended question.",
    "discard_reason_codes": [],
    "variant_count": 1,
    "variants": [
      {
        "open_variant_id": "open_1fc5d60b9a7bfd67ec15427a",
        "parent_problem_id": "prob_8db80bdfeadb792f856f387c",
        "variant_index": 1,
        "title": "CMM-Math 开放题",
        "rewritten_question_text": "在平面直角坐标系 $x O y$ 中, $M$ 为不等式组 $\\left\\{\\begin{array}{l}2 x-y-2 \\geq 0, \\\\ x+2 y-1 \\geq 0, \\\\ 3 x+y-8 \\leq 0\\end{array}\\right.$ 所表示的区域上一动点,则直线 OM 斜率的最小值为 ( )",
        "expected_answer_type": "numeric",
        "expected_answer": "$-\\frac{1}{3}$",
        "split_role": "single"
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
    "open_variant_id": "open_1fc5d60b9a7bfd67ec15427a",
    "parent_problem_id": "prob_8db80bdfeadb792f856f387c",
    "variant_index": 1,
    "title": "CMM-Math 开放题",
    "rewritten_question_text": "在平面直角坐标系 $x O y$ 中, $M$ 为不等式组 $\\left\\{\\begin{array}{l}2 x-y-2 \\geq 0, \\\\ x+2 y-1 \\geq 0, \\\\ 3 x+y-8 \\leq 0\\end{array}\\right.$ 所表示的区域上一动点,则直线 OM 斜率的最小值为 ( )",
    "expected_answer_type": "numeric",
    "expected_answer": "$-\\frac{1}{3}$",
    "split_role": "single"
  }
]
```

#### asset_records

```json
[
  {
    "asset_id": "asset_2126f04172784ffe95e7bbc2",
    "problem_id": "prob_8db80bdfeadb792f856f387c",
    "asset_type": "text",
    "asset_role": "question_text_source",
    "source_uri": "source://cmm_math/train/19900/question",
    "storage_uri": "inline://prob_8db80bdfeadb792f856f387c/question_source",
    "file_format": "txt",
    "file_size_bytes": 223,
    "width": null,
    "height": null,
    "sha256": "621067194654204d39dcc9dac5bf92e3de16d26afcd79bc87b24039ede633ec5",
    "perceptual_hash": null,
    "source_text_snapshot": "在平面直角坐标系 $x O y$ 中, $M$ 为不等式组 $\\left\\{\\begin{array}{l}2 x-y-2 \\geq 0, \\\\ x+2 y-1 \\geq 0, \\\\ 3 x+y-8 \\leq 0\\end{array}\\right.$ 所表示的区域上一动点,则直线 OM 斜率的最小值为 ( )",
    "normalized_text_snapshot": null,
    "text_completeness_score": 0.6884,
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
        "original": "O",
        "canonical": "O",
        "variable_type": "symbol"
      },
      {
        "original": "y",
        "canonical": "y",
        "variable_type": "symbol"
      },
      {
        "original": "M",
        "canonical": "M",
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
        "original": "OM",
        "canonical": "OM",
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
    "asset_id": "asset_483716380a482cb8a75fe098",
    "problem_id": "prob_8db80bdfeadb792f856f387c",
    "asset_type": "text",
    "asset_role": "question_text_normalized",
    "source_uri": null,
    "storage_uri": "inline://prob_8db80bdfeadb792f856f387c/question_normalized",
    "file_format": "txt",
    "file_size_bytes": 223,
    "width": null,
    "height": null,
    "sha256": "621067194654204d39dcc9dac5bf92e3de16d26afcd79bc87b24039ede633ec5",
    "perceptual_hash": null,
    "source_text_snapshot": "在平面直角坐标系 $x O y$ 中, $M$ 为不等式组 $\\left\\{\\begin{array}{l}2 x-y-2 \\geq 0, \\\\ x+2 y-1 \\geq 0, \\\\ 3 x+y-8 \\leq 0\\end{array}\\right.$ 所表示的区域上一动点,则直线 OM 斜率的最小值为 ( )",
    "normalized_text_snapshot": "在平面直角坐标系 $x O y$ 中, $M$ 为不等式组 $\\left\\{\\begin{array}{l}2 x-y-2 \\geq 0, \\\\ x+2 y-1 \\geq 0, \\\\ 3 x+y-8 \\leq 0\\end{array}\\right.$ 所表示的区域上一动点,则直线 OM 斜率的最小值为 ( )",
    "text_completeness_score": 0.6884,
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
        "original": "O",
        "canonical": "O",
        "variable_type": "symbol"
      },
      {
        "original": "y",
        "canonical": "y",
        "variable_type": "symbol"
      },
      {
        "original": "M",
        "canonical": "M",
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
        "original": "OM",
        "canonical": "OM",
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
    "asset_id": "asset_dd5843439282ce16eb7cad23",
    "problem_id": "prob_8db80bdfeadb792f856f387c",
    "asset_type": "answer",
    "asset_role": "answer_raw",
    "source_uri": "source://cmm_math/train/19900/answer",
    "storage_uri": "inline://prob_8db80bdfeadb792f856f387c/answer_raw",
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
    "created_at": "2026-03-24T06:37:02Z",
    "updated_at": "2026-03-24T06:37:02Z"
  },
  {
    "asset_id": "asset_f61423934b1d3777d7c9373a",
    "problem_id": "prob_8db80bdfeadb792f856f387c",
    "asset_type": "answer",
    "asset_role": "answer_normalized",
    "source_uri": null,
    "storage_uri": "inline://prob_8db80bdfeadb792f856f387c/answer_normalized",
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
    "created_at": "2026-03-24T06:37:02Z",
    "updated_at": "2026-03-24T06:37:02Z"
  },
  {
    "asset_id": "asset_e032ca8e929e93e32d574822",
    "problem_id": "prob_8db80bdfeadb792f856f387c",
    "asset_type": "text",
    "asset_role": "question_text_open_variant",
    "source_uri": null,
    "storage_uri": "inline://open_1fc5d60b9a7bfd67ec15427a",
    "file_format": "txt",
    "file_size_bytes": 223,
    "width": null,
    "height": null,
    "sha256": "621067194654204d39dcc9dac5bf92e3de16d26afcd79bc87b24039ede633ec5",
    "perceptual_hash": null,
    "source_text_snapshot": "在平面直角坐标系 $x O y$ 中, $M$ 为不等式组 $\\left\\{\\begin{array}{l}2 x-y-2 \\geq 0, \\\\ x+2 y-1 \\geq 0, \\\\ 3 x+y-8 \\leq 0\\end{array}\\right.$ 所表示的区域上一动点,则直线 OM 斜率的最小值为 ( )",
    "normalized_text_snapshot": "在平面直角坐标系 $x O y$ 中, $M$ 为不等式组 $\\left\\{\\begin{array}{l}2 x-y-2 \\geq 0, \\\\ x+2 y-1 \\geq 0, \\\\ 3 x+y-8 \\leq 0\\end{array}\\right.$ 所表示的区域上一动点,则直线 OM 斜率的最小值为 ( )",
    "text_completeness_score": 0.6884,
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
        "original": "O",
        "canonical": "O",
        "variable_type": "symbol"
      },
      {
        "original": "y",
        "canonical": "y",
        "variable_type": "symbol"
      },
      {
        "original": "M",
        "canonical": "M",
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
        "original": "OM",
        "canonical": "OM",
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
    "node_id": "node_3ed6c81385e0019045cdd9b3",
    "problem_id": "prob_8db80bdfeadb792f856f387c",
    "node_type": "text_fact",
    "canonical_value": "在平面直角坐标系 $x O y$ 中, $M$ 为不等式组 $\\left\\{\\begin{array}{l}2 x-y-2 \\geq 0, \\\\ x+2 y-1 \\geq 0, \\\\ 3 x+y-8 \\leq 0\\end{array}\\right.$ 所表示的区域上一动点,则直线 OM 斜率的最小值为 ( )",
    "surface_forms": [
      "在平面直角坐标系 $x O y$ 中, $M$ 为不等式组 $\\left\\{\\begin{array}{l}2 x-y-2 \\geq 0, \\\\ x+2 y-1 \\geq 0, \\\\ 3 x+y-8 \\leq 0\\end{array}\\right.$ 所表示的区域上一动点,则直线 OM 斜率的最小值为 ( )"
    ],
    "origin_kind": "text",
    "cognitive_level": "objective",
    "source_refs": [
      "asset_483716380a482cb8a75fe098"
    ],
    "evidence_refs": [
      "asset_483716380a482cb8a75fe098"
    ],
    "upstream_node_ids": [],
    "value_type": "condition",
    "normalized_value": {
      "text": "在平面直角坐标系 $x O y$ 中, $M$ 为不等式组 $\\left\\{\\begin{array}{l}2 x-y-2 \\geq 0, \\\\ x+2 y-1 \\geq 0, \\\\ 3 x+y-8 \\leq 0\\end{array}\\right.$ 所表示的区域上一动点,则直线 OM 斜率的最小值为 ( )",
      "segment_index": 1,
      "mentions_visual": false,
      "numeric_tokens": [
        "2",
        "-2",
        "0",
        "+2",
        "-1",
        "0",
        "3",
        "-8",
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
    "node_id": "node_cedb24861b06a2236393aa72",
    "problem_id": "prob_8db80bdfeadb792f856f387c",
    "node_type": "target_slot",
    "canonical_value": "在平面直角坐标系 $x O y$ 中, $M$ 为不等式组 $\\left\\{\\begin{array}{l}2 x-y-2 \\geq 0, \\\\ x+2 y-1 \\geq 0, \\\\ 3 x+y-8 \\leq 0\\end{array}\\right.$ 所表示的区域上一动点,则直线 OM 斜率的最小值为 ( )",
    "surface_forms": [
      "在平面直角坐标系 $x O y$ 中, $M$ 为不等式组 $\\left\\{\\begin{array}{l}2 x-y-2 \\geq 0, \\\\ x+2 y-1 \\geq 0, \\\\ 3 x+y-8 \\leq 0\\end{array}\\right.$ 所表示的区域上一动点,则直线 OM 斜率的最小值为 ( )"
    ],
    "origin_kind": "text_structure",
    "cognitive_level": "computed",
    "source_refs": [
      "asset_483716380a482cb8a75fe098"
    ],
    "evidence_refs": [
      "asset_483716380a482cb8a75fe098"
    ],
    "upstream_node_ids": [],
    "value_type": "numeric",
    "normalized_value": {
      "slot_id": "slot_prob_8db80bdfeadb792f856f387c_1",
      "variant_index": 1,
      "split_role": "single",
      "slot_type": "numeric",
      "target_text": "在平面直角坐标系 $x O y$ 中, $M$ 为不等式组 $\\left\\{\\begin{array}{l}2 x-y-2 \\geq 0, \\\\ x+2 y-1 \\geq 0, \\\\ 3 x+y-8 \\leq 0\\end{array}\\right.$ 所表示的区域上一动点,则直线 OM 斜率的最小值为 ( )",
      "expected_answer_type": "numeric",
      "expected_answer": "$-\\frac{1}{3}$",
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
    "node_id": "node_773db59b0e4643f150ad3ef1",
    "problem_id": "prob_8db80bdfeadb792f856f387c",
    "node_type": "answer_claim",
    "canonical_value": "A",
    "surface_forms": [
      "A"
    ],
    "origin_kind": "text",
    "cognitive_level": "objective",
    "source_refs": [
      "asset_f61423934b1d3777d7c9373a"
    ],
    "evidence_refs": [
      "asset_f61423934b1d3777d7c9373a"
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
    "created_at": "2026-03-24T06:37:02Z",
    "updated_at": "2026-03-24T06:37:02Z"
  },
  {
    "node_id": "node_8181dbbf2b672cee60449206",
    "problem_id": "prob_8db80bdfeadb792f856f387c",
    "node_type": "text_fact",
    "canonical_value": "在平面直角坐标系 $x O y$ 中, $M$ 为不等式组 $\\left\\{\\begin{array}{l}2 x-y-2 \\geq 0, \\\\ x+2 y-1 \\geq 0, \\\\ 3 x+y-8 \\leq 0\\end{array}\\right.$ 所表示的区域上一动点,则直线 OM 斜率的最小值为 ( )",
    "surface_forms": [
      "在平面直角坐标系 $x O y$ 中, $M$ 为不等式组 $\\left\\{\\begin{array}{l}2 x-y-2 \\geq 0, \\\\ x+2 y-1 \\geq 0, \\\\ 3 x+y-8 \\leq 0\\end{array}\\right.$ 所表示的区域上一动点,则直线 OM 斜率的最小值为 ( )"
    ],
    "origin_kind": "reasoning",
    "cognitive_level": "computed",
    "source_refs": [
      "asset_e032ca8e929e93e32d574822"
    ],
    "evidence_refs": [
      "asset_e032ca8e929e93e32d574822"
    ],
    "upstream_node_ids": [],
    "value_type": "text",
    "normalized_value": {
      "open_variant_id": "open_1fc5d60b9a7bfd67ec15427a",
      "parent_problem_id": "prob_8db80bdfeadb792f856f387c",
      "variant_index": 1,
      "title": "CMM-Math 开放题",
      "rewritten_question_text": "在平面直角坐标系 $x O y$ 中, $M$ 为不等式组 $\\left\\{\\begin{array}{l}2 x-y-2 \\geq 0, \\\\ x+2 y-1 \\geq 0, \\\\ 3 x+y-8 \\leq 0\\end{array}\\right.$ 所表示的区域上一动点,则直线 OM 斜率的最小值为 ( )",
      "expected_answer_type": "numeric",
      "expected_answer": "$-\\frac{1}{3}$",
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
    "created_at": "2026-03-24T06:37:02Z",
    "updated_at": "2026-03-24T06:37:02Z"
  },
  {
    "node_id": "node_505c6d627949f0848a91c317",
    "problem_id": "prob_8db80bdfeadb792f856f387c",
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
      "solvability_id": "solv_prob_8db80bdfeadb792f856f387c",
      "problem_id": "prob_8db80bdfeadb792f856f387c",
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
    "node_id": "node_1c77d589fbe7e0d3c87a8894",
    "problem_id": "prob_8db80bdfeadb792f856f387c",
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
    "created_at": "2026-03-24T06:37:02Z",
    "updated_at": "2026-03-24T06:37:02Z"
  }
]
```

#### field_audit_records

```json
[
  {
    "audit_id": "audit_4356811656339428e5a44dc2",
    "problem_id": "prob_8db80bdfeadb792f856f387c",
    "record_type": "problem_main_record",
    "field_name": "normalized_question_text",
    "before_value": "在平面直角坐标系 $x O y$ 中, $M$ 为不等式组 $\\left\\{\\begin{array}{l}2 x-y-2 \\geq 0, \\\\ x+2 y-1 \\geq 0, \\\\ 3 x+y-8 \\leq 0\\end{array}\\right.$ 所表示的区域上一动点,则直线 OM 斜率的最小值为 ( )",
    "after_value": "在平面直角坐标系 $x O y$ 中, $M$ 为不等式组 $\\left\\{\\begin{array}{l}2 x-y-2 \\geq 0, \\\\ x+2 y-1 \\geq 0, \\\\ 3 x+y-8 \\leq 0\\end{array}\\right.$ 所表示的区域上一动点,则直线 OM 斜率的最小值为 ( )",
    "change_type": "text_normalized",
    "trigger": "NormalizationAgent",
    "operator_type": "system",
    "created_at": "2026-03-24T06:37:02Z"
  },
  {
    "audit_id": "audit_f89f22337a5078c87aa51335",
    "problem_id": "prob_8db80bdfeadb792f856f387c",
    "record_type": "problem_main_record",
    "field_name": "normalized_answer_text",
    "before_value": "A",
    "after_value": "A",
    "change_type": "answer_canonicalized",
    "trigger": "NormalizationAgent",
    "operator_type": "system",
    "created_at": "2026-03-24T06:37:02Z"
  },
  {
    "audit_id": "audit_38d7f399ec817b0a95f19aa5",
    "problem_id": "prob_8db80bdfeadb792f856f387c",
    "record_type": "rewrite_report",
    "field_name": "rewrite_strategy",
    "before_value": null,
    "after_value": "blank_open",
    "change_type": "question_rewritten",
    "trigger": "QuestionRewriteAgent",
    "operator_type": "system",
    "created_at": "2026-03-24T06:37:02Z"
  },
  {
    "audit_id": "audit_1c77d589fbe7e0d3c87a8894",
    "problem_id": "prob_8db80bdfeadb792f856f387c",
    "record_type": "cleaning_record",
    "field_name": "decision",
    "before_value": null,
    "after_value": "pass",
    "change_type": "gate_decision",
    "trigger": "CleanGateAgent",
    "operator_type": "system",
    "created_at": "2026-03-24T06:37:02Z"
  },
  {
    "audit_id": "audit_3380523d768be7d909f2e1c3",
    "problem_id": "prob_8db80bdfeadb792f856f387c",
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
        "original": "O",
        "canonical": "O",
        "variable_type": "symbol"
      },
      {
        "original": "y",
        "canonical": "y",
        "variable_type": "symbol"
      },
      {
        "original": "M",
        "canonical": "M",
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
        "original": "OM",
        "canonical": "OM",
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

- `outputs/user_requested_batch_review/pipeline_runs/run_6f9fadee9214c91e/datasets/cmm_math/samples/prob_8db80bdfeadb792f856f387c.json`
