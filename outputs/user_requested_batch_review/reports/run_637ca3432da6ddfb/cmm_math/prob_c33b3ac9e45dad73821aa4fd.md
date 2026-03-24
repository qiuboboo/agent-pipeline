# CMM-Math / prob_c33b3ac9e45dad73821aa4fd

- source_problem_id: `18947`
- source_split: `train`
- clean_decision: `pass`
- rewrite_strategy: `blank_open`
- full sample bundle JSON: `outputs/user_requested_batch_review/pipeline_runs/run_637ca3432da6ddfb/datasets/cmm_math/samples/prob_c33b3ac9e45dad73821aa4fd.json`

## 1. 原始内容（处理前）

### 1.1 原始快照

```json
{
  "dataset_key": "cmm_math",
  "source_problem_id": "18947",
  "source_split": "train",
  "raw_question_text": "设 $\\triangle A B C$ 的内角 $A, B, C$ 的对边分别为 $a, b, c,(a+b+c)(a-b+c)=a c, \\sin A \\sin C=\\frac{\\sqrt{3}-1}{4}$, 则\n角 $C=(\\quad)$",
  "raw_answer_text": "A",
  "choice_map": {
    "A": "$C=15^{\\circ}$ 或 $C=45^{\\circ}$",
    "B": "$C=15^{\\circ}$ 或 $C=30^{\\circ}$",
    "C": "$C=60^{\\circ}$ 或 $C=45^{\\circ}$",
    "D": "$C=30^{\\circ}$ 或 $C=60^{\\circ}$"
  },
  "image_sources": [],
  "metadata": {
    "row_index": 16,
    "question_field": "question",
    "answer_field": "answer",
    "image_field": null,
    "choice_field": "options"
  },
  "raw_record": {
    "id": "18947",
    "image": "[]",
    "answer": "A",
    "solution": "null",
    "level": "高二",
    "question": "设 $\\triangle A B C$ 的内角 $A, B, C$ 的对边分别为 $a, b, c,(a+b+c)(a-b+c)=a c, \\sin A \\sin C=\\frac{\\sqrt{3}-1}{4}$, 则\n角 $C=(\\quad)$",
    "options": "A. $C=15^{\\circ}$ 或 $C=45^{\\circ}$\nB. $C=15^{\\circ}$ 或 $C=30^{\\circ}$\nC. $C=60^{\\circ}$ 或 $C=45^{\\circ}$\nD. $C=30^{\\circ}$ 或 $C=60^{\\circ}$",
    "subject": "解析几何",
    "analysis": "因为 $(a+b+c)(a-b+c)=a c$ ，所以 $a^{2}+c^{2}-b^{2}=-a c$.\n\n由余弦定理得, $\\cos B=\\frac{a^{2}+c^{2}-b^{2}}{2 a c}=-\\frac{1}{2}$ ，\n\n因此 $B=120^{\\circ}$, 所以 $A+C=60^{\\circ}$, 所以 $\\cos (A-C)=\\cos A \\cos C+\\sin A \\sin C$\n\n$=\\cos A \\cos C-\\sin A \\sin C+2 \\sin A \\sin C=\\cos (A+C)+2 \\sin A \\sin C$\n\n$=\\frac{1}{2}+2 \\times \\frac{\\sqrt{3}-1}{4}=\\frac{\\sqrt{3}}{2}$, 故 $A-C=30^{\\circ}$ 或 $A-C=-30^{\\circ}$, 因此, $C=15^{\\circ}$ 或 $C=45^{\\circ}$, 故选 $\\mathrm{A}$ 。"
  }
}
```

### 1.2 原始图片

- （无）

## 2. 处理前后对照

### 2.1 关键字段对照

| 字段 | 处理前 | 处理后 |
| --- | --- | --- |
| question_text | 设 $\triangle A B C$ 的内角 $A, B, C$ 的对边分别为 $a, b, c,(a+b+c)(a-b+c)=a c, \sin A \sin C=\frac{\sqrt{3}-1}{4}$, 则 角 $C=(\quad)$ | 设 $\triangle A B C$ 的内角 $A, B, C$ 的对边分别为 $a, b, c,(a+b+c)(a-b+c)=a c, \sin A \sin C=\frac{\sqrt{3}-1}{4}$, 则 角 $C=(\quad)$ |
| answer_text | A | A |
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
  "problem_id": "prob_c33b3ac9e45dad73821aa4fd",
  "source_dataset": "CMM-Math",
  "source_split": "train",
  "source_problem_id": "18947",
  "ingest_batch_id": "multidataset-clean_20260324T074830Z",
  "problem_type": "multimodal_reasoning",
  "domain_tags": [
    "数学"
  ],
  "language": "zh",
  "raw_question_text": "设 $\\triangle A B C$ 的内角 $A, B, C$ 的对边分别为 $a, b, c,(a+b+c)(a-b+c)=a c, \\sin A \\sin C=\\frac{\\sqrt{3}-1}{4}$, 则\n角 $C=(\\quad)$",
  "normalized_question_text": "设 $\\triangle A B C$ 的内角 $A, B, C$ 的对边分别为 $a, b, c,(a+b+c)(a-b+c)=a c, \\sin A \\sin C=\\frac{\\sqrt{3}-1}{4}$, 则\n角 $C=(\\quad)$",
  "raw_answer_text": "A",
  "normalized_answer_text": "A",
  "answer_type": "option",
  "image_count": 0,
  "has_multiple_images": false,
  "requires_image": false,
  "multimodal_strength_score": 0.48,
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
  "rewrite_strategy": "blank_open",
  "open_variant_count": 1,
  "candidate_id": "cand_c33b3ac9e45dad73821aa4fd",
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
  "clean_problem_record_id": "cleanprob_a2abc3f1f514d4459ca19d1b",
  "problem_id": "prob_c33b3ac9e45dad73821aa4fd",
  "source_dataset": "CMM-Math",
  "source_problem_id": "18947",
  "normalized_question_text": "设 $\\triangle A B C$ 的内角 $A, B, C$ 的对边分别为 $a, b, c,(a+b+c)(a-b+c)=a c, \\sin A \\sin C=\\frac{\\sqrt{3}-1}{4}$, 则\n角 $C=(\\quad)$",
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
  "created_at": "2026-03-24T07:48:35Z"
}
```

#### normalized_assets

```json
{
  "normalized_assets_id": "nassets_a2abc3f1f514d4459ca19d1b",
  "problem_id": "prob_c33b3ac9e45dad73821aa4fd",
  "normalized_question_text": "设 $\\triangle A B C$ 的内角 $A, B, C$ 的对边分别为 $a, b, c,(a+b+c)(a-b+c)=a c, \\sin A \\sin C=\\frac{\\sqrt{3}-1}{4}$, 则\n角 $C=(\\quad)$",
  "normalized_answer_text": "A",
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
      "original": "a",
      "canonical": "a",
      "variable_type": "symbol"
    },
    {
      "original": "b",
      "canonical": "b",
      "variable_type": "symbol"
    },
    {
      "original": "c",
      "canonical": "c",
      "variable_type": "symbol"
    },
    {
      "original": "sin",
      "canonical": "sin",
      "variable_type": "label"
    },
    {
      "original": "frac",
      "canonical": "frac",
      "variable_type": "label"
    },
    {
      "original": "sqrt",
      "canonical": "sqrt",
      "variable_type": "label"
    },
    {
      "original": "quad",
      "canonical": "quad",
      "variable_type": "label"
    }
  ],
  "sentence_segments": [
    {
      "segment_index": 1,
      "text": "设 $\\triangle A B C$ 的内角 $A, B, C$ 的对边分别为 $a, b, c,(a+b+c)(a-b+c)=a c, \\sin A \\sin C=\\frac{\\sqrt{3}-1}{4}$, 则"
    },
    {
      "segment_index": 2,
      "text": "角 $C=(\\quad)$"
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
  "text_structure_id": "text_prob_c33b3ac9e45dad73821aa4fd",
  "problem_id": "prob_c33b3ac9e45dad73821aa4fd",
  "question_type": "multiple_choice",
  "conditions": [
    {
      "text": "设 $\\triangle A B C$ 的内角 $A, B, C$ 的对边分别为 $a, b, c,(a+b+c)(a-b+c)=a c, \\sin A \\sin C=\\frac{\\sqrt{3}-1}{4}$, 则",
      "segment_index": 1,
      "mentions_visual": false,
      "numeric_tokens": [
        "3",
        "-1",
        "4"
      ],
      "unit_mentions": [
        "A",
        "g",
        "s"
      ],
      "condition_role": "explicit"
    },
    {
      "text": "角 $C=(\\quad)$",
      "segment_index": 2,
      "mentions_visual": false,
      "numeric_tokens": [],
      "unit_mentions": [],
      "condition_role": "explicit"
    }
  ],
  "targets": [
    {
      "text": "设 $\\triangle A B C$ 的内角 $A, B, C$ 的对边分别为 $a, b, c,(a+b+c)(a-b+c)=a c, \\sin A \\sin C=\\frac{\\sqrt{3}-1}{4}$, 则\n角 $C=(\\quad)$",
      "segment_index": 2,
      "mentions_visual": false,
      "numeric_tokens": [
        "3",
        "-1",
        "4"
      ],
      "unit_mentions": [
        "A",
        "g",
        "s"
      ],
      "target_role": "fallback"
    }
  ],
  "answer_slots": [
    {
      "slot_id": "slot_prob_c33b3ac9e45dad73821aa4fd_1",
      "variant_index": 1,
      "split_role": "single",
      "slot_type": "numeric",
      "target_text": "角 $C=(\\quad)$",
      "expected_answer_type": "numeric",
      "expected_answer": "$C=15^{\\circ}$ 或 $C=45^{\\circ}$",
      "requires_visual_grounding": false
    }
  ],
  "entity_mentions": [
    {
      "mention": "angle",
      "entity_category": "angle",
      "requires_visual_grounding": true
    },
    {
      "mention": "triangle",
      "entity_category": "shape",
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
      "original": "a",
      "canonical": "a",
      "variable_type": "symbol"
    },
    {
      "original": "b",
      "canonical": "b",
      "variable_type": "symbol"
    },
    {
      "original": "c",
      "canonical": "c",
      "variable_type": "symbol"
    },
    {
      "original": "sin",
      "canonical": "sin",
      "variable_type": "label"
    },
    {
      "original": "frac",
      "canonical": "frac",
      "variable_type": "label"
    },
    {
      "original": "sqrt",
      "canonical": "sqrt",
      "variable_type": "label"
    },
    {
      "original": "quad",
      "canonical": "quad",
      "variable_type": "label"
    }
  ],
  "unit_mentions": [
    "A",
    "g",
    "s"
  ],
  "sentence_segments": [
    {
      "segment_index": 1,
      "text": "设 $\\triangle A B C$ 的内角 $A, B, C$ 的对边分别为 $a, b, c,(a+b+c)(a-b+c)=a c, \\sin A \\sin C=\\frac{\\sqrt{3}-1}{4}$, 则"
    },
    {
      "segment_index": 2,
      "text": "角 $C=(\\quad)$"
    }
  ],
  "requires_visual_grounding": true,
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
  "alignment_id": "align_a2abc3f1f514d4459ca19d1b",
  "problem_id": "prob_c33b3ac9e45dad73821aa4fd",
  "image_entity_refs": [],
  "text_span_refs": [
    "asset_prob_c33b3ac9e45dad73821aa4fd_question_text_normalized"
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
  "solvability_id": "solv_prob_c33b3ac9e45dad73821aa4fd",
  "problem_id": "prob_c33b3ac9e45dad73821aa4fd",
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
  "cleaning_id": "clean_a2abc3f1f514d4459ca19d1b",
  "problem_id": "prob_c33b3ac9e45dad73821aa4fd",
  "cleaning_version": "v3.0.0",
  "pipeline_run_id": "run_637ca3432da6ddfb",
  "dataset_name": "CMM-Math",
  "input_asset_ids": [
    "asset_514b9626dea759651caebd79",
    "asset_9b202766752e134681286dbb",
    "asset_8340f7f7b610b210c950458e",
    "asset_b94f2a5035305e32972454f3",
    "asset_79f49f6e8abe9d19527f6713"
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
    "alignment_id": "align_a2abc3f1f514d4459ca19d1b",
    "coverage_score": 1.0,
    "consistency_score": 1.0,
    "alignment_status": "good",
    "conflict_count": 0
  },
  "text_structure_summary": {
    "text_structure_id": "text_prob_c33b3ac9e45dad73821aa4fd",
    "question_type": "multiple_choice",
    "condition_count": 2,
    "target_count": 1,
    "answer_slot_count": 1,
    "status": "complete"
  },
  "solvability_summary": {
    "solvability_id": "solv_prob_c33b3ac9e45dad73821aa4fd",
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
  "clean_score": 0.8662,
  "decision": "pass",
  "decision_reason_codes": [
    "meets_cleaning_requirements"
  ],
  "review_ticket_id": null,
  "operator_type": "system",
  "started_at": "2026-03-24T07:48:35Z",
  "finished_at": "2026-03-24T07:48:35Z",
  "candidate_id": "cand_c33b3ac9e45dad73821aa4fd",
  "cleaning_path": "text_lightweight",
  "text_dominant": true
}
```

## 3. 开放化改写前后

### 3.1 改写前

```json
{
  "question_text_before_rewrite": "设 $\\triangle A B C$ 的内角 $A, B, C$ 的对边分别为 $a, b, c,(a+b+c)(a-b+c)=a c, \\sin A \\sin C=\\frac{\\sqrt{3}-1}{4}$, 则\n角 $C=(\\quad)$",
  "answer_text_before_rewrite": "A",
  "raw_question_text": "设 $\\triangle A B C$ 的内角 $A, B, C$ 的对边分别为 $a, b, c,(a+b+c)(a-b+c)=a c, \\sin A \\sin C=\\frac{\\sqrt{3}-1}{4}$, 则\n角 $C=(\\quad)$",
  "raw_answer_text": "A"
}
```

### 3.2 改写后

```json
{
  "rewrite_report": {
    "rewrite_id": "rewrite_a2abc3f1f514d4459ca19d1b",
    "problem_id": "prob_c33b3ac9e45dad73821aa4fd",
    "source_problem_id": "18947",
    "strategy": "blank_open",
    "rationale": "Converted multiple choice into blank-style open-ended question.",
    "discard_reason_codes": [],
    "variant_count": 1,
    "variants": [
      {
        "open_variant_id": "open_59dfb03c373e1324839dd62e",
        "parent_problem_id": "prob_c33b3ac9e45dad73821aa4fd",
        "variant_index": 1,
        "title": "CMM-Math 开放题",
        "rewritten_question_text": "设 $\\triangle A B C$ 的内角 $A, B, C$ 的对边分别为 $a, b, c,(a+b+c)(a-b+c)=a c, \\sin A \\sin C=\\frac{\\sqrt{3}-1}{4}$, 则\n角 $C=(\\quad)$",
        "expected_answer_type": "numeric",
        "expected_answer": "$C=15^{\\circ}$ 或 $C=45^{\\circ}$",
        "split_role": "single"
      }
    ],
    "created_at": "2026-03-24T07:48:35Z"
  },
  "open_ended_problem_variants": [
    {
      "open_variant_id": "open_59dfb03c373e1324839dd62e",
      "parent_problem_id": "prob_c33b3ac9e45dad73821aa4fd",
      "variant_index": 1,
      "title": "CMM-Math 开放题",
      "rewritten_question_text": "设 $\\triangle A B C$ 的内角 $A, B, C$ 的对边分别为 $a, b, c,(a+b+c)(a-b+c)=a c, \\sin A \\sin C=\\frac{\\sqrt{3}-1}{4}$, 则\n角 $C=(\\quad)$",
      "expected_answer_type": "numeric",
      "expected_answer": "$C=15^{\\circ}$ 或 $C=45^{\\circ}$",
      "split_role": "single"
    }
  ]
}
```

## 4. 完整 collection + cleaning 输出对象

#### candidate_problem_record

```json
{
  "candidate_id": "cand_c33b3ac9e45dad73821aa4fd",
  "source_dataset": "CMM-Math",
  "source_split": "train",
  "source_problem_id": "18947",
  "subject": "数学",
  "raw_question_text": "设 $\\triangle A B C$ 的内角 $A, B, C$ 的对边分别为 $a, b, c,(a+b+c)(a-b+c)=a c, \\sin A \\sin C=\\frac{\\sqrt{3}-1}{4}$, 则\n角 $C=(\\quad)$",
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
    "row_index": 16,
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
  "raw_asset_bundle_id": "bundle_3e01697dae56c52aed7b62a6",
  "candidate_id": "cand_c33b3ac9e45dad73821aa4fd",
  "source_dataset": "CMM-Math",
  "source_problem_id": "18947",
  "assets": [
    {
      "asset_role": "question_text_raw",
      "storage_uri": "inline://prob_c33b3ac9e45dad73821aa4fd/question_source",
      "is_present": true
    },
    {
      "asset_role": "answer_text_raw",
      "storage_uri": "inline://prob_c33b3ac9e45dad73821aa4fd/answer_source",
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
  "candidate_pool_entry_id": "cpool_7aa5e349d2d761abe850dbd9",
  "candidate_id": "cand_c33b3ac9e45dad73821aa4fd",
  "source_dataset": "CMM-Math",
  "source_problem_id": "18947",
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
    "clean_pool_entry_id": "cleanpool_a2abc3f1f514d4459ca19d1b",
    "candidate_id": "cand_c33b3ac9e45dad73821aa4fd",
    "problem_id": "prob_c33b3ac9e45dad73821aa4fd",
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
    "rewrite_id": "rewrite_a2abc3f1f514d4459ca19d1b",
    "problem_id": "prob_c33b3ac9e45dad73821aa4fd",
    "source_problem_id": "18947",
    "strategy": "blank_open",
    "rationale": "Converted multiple choice into blank-style open-ended question.",
    "discard_reason_codes": [],
    "variant_count": 1,
    "variants": [
      {
        "open_variant_id": "open_59dfb03c373e1324839dd62e",
        "parent_problem_id": "prob_c33b3ac9e45dad73821aa4fd",
        "variant_index": 1,
        "title": "CMM-Math 开放题",
        "rewritten_question_text": "设 $\\triangle A B C$ 的内角 $A, B, C$ 的对边分别为 $a, b, c,(a+b+c)(a-b+c)=a c, \\sin A \\sin C=\\frac{\\sqrt{3}-1}{4}$, 则\n角 $C=(\\quad)$",
        "expected_answer_type": "numeric",
        "expected_answer": "$C=15^{\\circ}$ 或 $C=45^{\\circ}$",
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
    "open_variant_id": "open_59dfb03c373e1324839dd62e",
    "parent_problem_id": "prob_c33b3ac9e45dad73821aa4fd",
    "variant_index": 1,
    "title": "CMM-Math 开放题",
    "rewritten_question_text": "设 $\\triangle A B C$ 的内角 $A, B, C$ 的对边分别为 $a, b, c,(a+b+c)(a-b+c)=a c, \\sin A \\sin C=\\frac{\\sqrt{3}-1}{4}$, 则\n角 $C=(\\quad)$",
    "expected_answer_type": "numeric",
    "expected_answer": "$C=15^{\\circ}$ 或 $C=45^{\\circ}$",
    "split_role": "single"
  }
]
```

#### asset_records

```json
[
  {
    "asset_id": "asset_514b9626dea759651caebd79",
    "problem_id": "prob_c33b3ac9e45dad73821aa4fd",
    "asset_type": "text",
    "asset_role": "question_text_source",
    "source_uri": "source://cmm_math/train/18947/question",
    "storage_uri": "inline://prob_c33b3ac9e45dad73821aa4fd/question_source",
    "file_format": "txt",
    "file_size_bytes": 146,
    "width": null,
    "height": null,
    "sha256": "374737ddb4793fea3e7a37667169b8c3341579b4fda9aeec728bf1258fa1984d",
    "perceptual_hash": null,
    "source_text_snapshot": "设 $\\triangle A B C$ 的内角 $A, B, C$ 的对边分别为 $a, b, c,(a+b+c)(a-b+c)=a c, \\sin A \\sin C=\\frac{\\sqrt{3}-1}{4}$, 则\n角 $C=(\\quad)$",
    "normalized_text_snapshot": null,
    "text_completeness_score": 0.6589,
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
        "original": "a",
        "canonical": "a",
        "variable_type": "symbol"
      },
      {
        "original": "b",
        "canonical": "b",
        "variable_type": "symbol"
      },
      {
        "original": "c",
        "canonical": "c",
        "variable_type": "symbol"
      },
      {
        "original": "sin",
        "canonical": "sin",
        "variable_type": "label"
      },
      {
        "original": "frac",
        "canonical": "frac",
        "variable_type": "label"
      },
      {
        "original": "sqrt",
        "canonical": "sqrt",
        "variable_type": "label"
      },
      {
        "original": "quad",
        "canonical": "quad",
        "variable_type": "label"
      }
    ],
    "asset_quality_flags": [],
    "is_usable": true,
    "discard_reason_codes": [],
    "created_at": "2026-03-24T07:48:35Z",
    "updated_at": "2026-03-24T07:48:35Z"
  },
  {
    "asset_id": "asset_9b202766752e134681286dbb",
    "problem_id": "prob_c33b3ac9e45dad73821aa4fd",
    "asset_type": "text",
    "asset_role": "question_text_normalized",
    "source_uri": null,
    "storage_uri": "inline://prob_c33b3ac9e45dad73821aa4fd/question_normalized",
    "file_format": "txt",
    "file_size_bytes": 146,
    "width": null,
    "height": null,
    "sha256": "374737ddb4793fea3e7a37667169b8c3341579b4fda9aeec728bf1258fa1984d",
    "perceptual_hash": null,
    "source_text_snapshot": "设 $\\triangle A B C$ 的内角 $A, B, C$ 的对边分别为 $a, b, c,(a+b+c)(a-b+c)=a c, \\sin A \\sin C=\\frac{\\sqrt{3}-1}{4}$, 则\n角 $C=(\\quad)$",
    "normalized_text_snapshot": "设 $\\triangle A B C$ 的内角 $A, B, C$ 的对边分别为 $a, b, c,(a+b+c)(a-b+c)=a c, \\sin A \\sin C=\\frac{\\sqrt{3}-1}{4}$, 则\n角 $C=(\\quad)$",
    "text_completeness_score": 0.6589,
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
        "original": "a",
        "canonical": "a",
        "variable_type": "symbol"
      },
      {
        "original": "b",
        "canonical": "b",
        "variable_type": "symbol"
      },
      {
        "original": "c",
        "canonical": "c",
        "variable_type": "symbol"
      },
      {
        "original": "sin",
        "canonical": "sin",
        "variable_type": "label"
      },
      {
        "original": "frac",
        "canonical": "frac",
        "variable_type": "label"
      },
      {
        "original": "sqrt",
        "canonical": "sqrt",
        "variable_type": "label"
      },
      {
        "original": "quad",
        "canonical": "quad",
        "variable_type": "label"
      }
    ],
    "asset_quality_flags": [],
    "is_usable": true,
    "discard_reason_codes": [],
    "created_at": "2026-03-24T07:48:35Z",
    "updated_at": "2026-03-24T07:48:35Z"
  },
  {
    "asset_id": "asset_8340f7f7b610b210c950458e",
    "problem_id": "prob_c33b3ac9e45dad73821aa4fd",
    "asset_type": "answer",
    "asset_role": "answer_raw",
    "source_uri": "source://cmm_math/train/18947/answer",
    "storage_uri": "inline://prob_c33b3ac9e45dad73821aa4fd/answer_raw",
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
    "created_at": "2026-03-24T07:48:35Z",
    "updated_at": "2026-03-24T07:48:35Z"
  },
  {
    "asset_id": "asset_b94f2a5035305e32972454f3",
    "problem_id": "prob_c33b3ac9e45dad73821aa4fd",
    "asset_type": "answer",
    "asset_role": "answer_normalized",
    "source_uri": null,
    "storage_uri": "inline://prob_c33b3ac9e45dad73821aa4fd/answer_normalized",
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
    "created_at": "2026-03-24T07:48:35Z",
    "updated_at": "2026-03-24T07:48:35Z"
  },
  {
    "asset_id": "asset_79f49f6e8abe9d19527f6713",
    "problem_id": "prob_c33b3ac9e45dad73821aa4fd",
    "asset_type": "text",
    "asset_role": "question_text_open_variant",
    "source_uri": null,
    "storage_uri": "inline://open_59dfb03c373e1324839dd62e",
    "file_format": "txt",
    "file_size_bytes": 146,
    "width": null,
    "height": null,
    "sha256": "374737ddb4793fea3e7a37667169b8c3341579b4fda9aeec728bf1258fa1984d",
    "perceptual_hash": null,
    "source_text_snapshot": "设 $\\triangle A B C$ 的内角 $A, B, C$ 的对边分别为 $a, b, c,(a+b+c)(a-b+c)=a c, \\sin A \\sin C=\\frac{\\sqrt{3}-1}{4}$, 则\n角 $C=(\\quad)$",
    "normalized_text_snapshot": "设 $\\triangle A B C$ 的内角 $A, B, C$ 的对边分别为 $a, b, c,(a+b+c)(a-b+c)=a c, \\sin A \\sin C=\\frac{\\sqrt{3}-1}{4}$, 则\n角 $C=(\\quad)$",
    "text_completeness_score": 0.6589,
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
        "original": "a",
        "canonical": "a",
        "variable_type": "symbol"
      },
      {
        "original": "b",
        "canonical": "b",
        "variable_type": "symbol"
      },
      {
        "original": "c",
        "canonical": "c",
        "variable_type": "symbol"
      },
      {
        "original": "sin",
        "canonical": "sin",
        "variable_type": "label"
      },
      {
        "original": "frac",
        "canonical": "frac",
        "variable_type": "label"
      },
      {
        "original": "sqrt",
        "canonical": "sqrt",
        "variable_type": "label"
      },
      {
        "original": "quad",
        "canonical": "quad",
        "variable_type": "label"
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
    "node_id": "node_0533078fbff79daf85b549ba",
    "problem_id": "prob_c33b3ac9e45dad73821aa4fd",
    "node_type": "text_fact",
    "canonical_value": "设 $\\triangle A B C$ 的内角 $A, B, C$ 的对边分别为 $a, b, c,(a+b+c)(a-b+c)=a c, \\sin A \\sin C=\\frac{\\sqrt{3}-1}{4}$, 则",
    "surface_forms": [
      "设 $\\triangle A B C$ 的内角 $A, B, C$ 的对边分别为 $a, b, c,(a+b+c)(a-b+c)=a c, \\sin A \\sin C=\\frac{\\sqrt{3}-1}{4}$, 则"
    ],
    "origin_kind": "text",
    "cognitive_level": "objective",
    "source_refs": [
      "asset_9b202766752e134681286dbb"
    ],
    "evidence_refs": [
      "asset_9b202766752e134681286dbb"
    ],
    "upstream_node_ids": [],
    "value_type": "condition",
    "normalized_value": {
      "text": "设 $\\triangle A B C$ 的内角 $A, B, C$ 的对边分别为 $a, b, c,(a+b+c)(a-b+c)=a c, \\sin A \\sin C=\\frac{\\sqrt{3}-1}{4}$, 则",
      "segment_index": 1,
      "mentions_visual": false,
      "numeric_tokens": [
        "3",
        "-1",
        "4"
      ],
      "unit_mentions": [
        "A",
        "g",
        "s"
      ],
      "condition_role": "explicit"
    },
    "unit": "A,g,s",
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
    "node_id": "node_c35f50da4d47aa6ff4a38f75",
    "problem_id": "prob_c33b3ac9e45dad73821aa4fd",
    "node_type": "text_fact",
    "canonical_value": "角 $C=(\\quad)$",
    "surface_forms": [
      "角 $C=(\\quad)$"
    ],
    "origin_kind": "text",
    "cognitive_level": "objective",
    "source_refs": [
      "asset_9b202766752e134681286dbb"
    ],
    "evidence_refs": [
      "asset_9b202766752e134681286dbb"
    ],
    "upstream_node_ids": [],
    "value_type": "condition",
    "normalized_value": {
      "text": "角 $C=(\\quad)$",
      "segment_index": 2,
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
    "created_at": "2026-03-24T07:48:35Z",
    "updated_at": "2026-03-24T07:48:35Z"
  },
  {
    "node_id": "node_ad59a576aaaf101ce78ae30a",
    "problem_id": "prob_c33b3ac9e45dad73821aa4fd",
    "node_type": "target_slot",
    "canonical_value": "角 $C=(\\quad)$",
    "surface_forms": [
      "角 $C=(\\quad)$"
    ],
    "origin_kind": "text_structure",
    "cognitive_level": "computed",
    "source_refs": [
      "asset_9b202766752e134681286dbb"
    ],
    "evidence_refs": [
      "asset_9b202766752e134681286dbb"
    ],
    "upstream_node_ids": [],
    "value_type": "numeric",
    "normalized_value": {
      "slot_id": "slot_prob_c33b3ac9e45dad73821aa4fd_1",
      "variant_index": 1,
      "split_role": "single",
      "slot_type": "numeric",
      "target_text": "角 $C=(\\quad)$",
      "expected_answer_type": "numeric",
      "expected_answer": "$C=15^{\\circ}$ 或 $C=45^{\\circ}$",
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
    "node_id": "node_aaa48b06d60a546a3369dd49",
    "problem_id": "prob_c33b3ac9e45dad73821aa4fd",
    "node_type": "answer_claim",
    "canonical_value": "A",
    "surface_forms": [
      "A"
    ],
    "origin_kind": "text",
    "cognitive_level": "objective",
    "source_refs": [
      "asset_b94f2a5035305e32972454f3"
    ],
    "evidence_refs": [
      "asset_b94f2a5035305e32972454f3"
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
    "created_at": "2026-03-24T07:48:35Z",
    "updated_at": "2026-03-24T07:48:35Z"
  },
  {
    "node_id": "node_ff54eeae1f8ec59c0642e788",
    "problem_id": "prob_c33b3ac9e45dad73821aa4fd",
    "node_type": "text_fact",
    "canonical_value": "设 $\\triangle A B C$ 的内角 $A, B, C$ 的对边分别为 $a, b, c,(a+b+c)(a-b+c)=a c, \\sin A \\sin C=\\frac{\\sqrt{3}-1}{4}$, 则\n角 $C=(\\quad)$",
    "surface_forms": [
      "设 $\\triangle A B C$ 的内角 $A, B, C$ 的对边分别为 $a, b, c,(a+b+c)(a-b+c)=a c, \\sin A \\sin C=\\frac{\\sqrt{3}-1}{4}$, 则\n角 $C=(\\quad)$"
    ],
    "origin_kind": "reasoning",
    "cognitive_level": "computed",
    "source_refs": [
      "asset_79f49f6e8abe9d19527f6713"
    ],
    "evidence_refs": [
      "asset_79f49f6e8abe9d19527f6713"
    ],
    "upstream_node_ids": [],
    "value_type": "text",
    "normalized_value": {
      "open_variant_id": "open_59dfb03c373e1324839dd62e",
      "parent_problem_id": "prob_c33b3ac9e45dad73821aa4fd",
      "variant_index": 1,
      "title": "CMM-Math 开放题",
      "rewritten_question_text": "设 $\\triangle A B C$ 的内角 $A, B, C$ 的对边分别为 $a, b, c,(a+b+c)(a-b+c)=a c, \\sin A \\sin C=\\frac{\\sqrt{3}-1}{4}$, 则\n角 $C=(\\quad)$",
      "expected_answer_type": "numeric",
      "expected_answer": "$C=15^{\\circ}$ 或 $C=45^{\\circ}$",
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
    "node_id": "node_294ff66221895c3f76c0bf06",
    "problem_id": "prob_c33b3ac9e45dad73821aa4fd",
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
      "solvability_id": "solv_prob_c33b3ac9e45dad73821aa4fd",
      "problem_id": "prob_c33b3ac9e45dad73821aa4fd",
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
    "node_id": "node_c8c3ebb0367f68e0050d62fc",
    "problem_id": "prob_c33b3ac9e45dad73821aa4fd",
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
    "audit_id": "audit_d5522576384760a4efb8a9c7",
    "problem_id": "prob_c33b3ac9e45dad73821aa4fd",
    "record_type": "problem_main_record",
    "field_name": "normalized_question_text",
    "before_value": "设 $\\triangle A B C$ 的内角 $A, B, C$ 的对边分别为 $a, b, c,(a+b+c)(a-b+c)=a c, \\sin A \\sin C=\\frac{\\sqrt{3}-1}{4}$, 则\n角 $C=(\\quad)$",
    "after_value": "设 $\\triangle A B C$ 的内角 $A, B, C$ 的对边分别为 $a, b, c,(a+b+c)(a-b+c)=a c, \\sin A \\sin C=\\frac{\\sqrt{3}-1}{4}$, 则\n角 $C=(\\quad)$",
    "change_type": "text_normalized",
    "trigger": "NormalizationAgent",
    "operator_type": "system",
    "created_at": "2026-03-24T07:48:35Z"
  },
  {
    "audit_id": "audit_3e2f4a0250bf3cd0f7568366",
    "problem_id": "prob_c33b3ac9e45dad73821aa4fd",
    "record_type": "problem_main_record",
    "field_name": "normalized_answer_text",
    "before_value": "A",
    "after_value": "A",
    "change_type": "answer_canonicalized",
    "trigger": "NormalizationAgent",
    "operator_type": "system",
    "created_at": "2026-03-24T07:48:35Z"
  },
  {
    "audit_id": "audit_7f1d0b1f3a630994710b889e",
    "problem_id": "prob_c33b3ac9e45dad73821aa4fd",
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
    "audit_id": "audit_c8c3ebb0367f68e0050d62fc",
    "problem_id": "prob_c33b3ac9e45dad73821aa4fd",
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
    "audit_id": "audit_72db226a7b36922ceaf50ea2",
    "problem_id": "prob_c33b3ac9e45dad73821aa4fd",
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
        "original": "a",
        "canonical": "a",
        "variable_type": "symbol"
      },
      {
        "original": "b",
        "canonical": "b",
        "variable_type": "symbol"
      },
      {
        "original": "c",
        "canonical": "c",
        "variable_type": "symbol"
      },
      {
        "original": "sin",
        "canonical": "sin",
        "variable_type": "label"
      },
      {
        "original": "frac",
        "canonical": "frac",
        "variable_type": "label"
      },
      {
        "original": "sqrt",
        "canonical": "sqrt",
        "variable_type": "label"
      },
      {
        "original": "quad",
        "canonical": "quad",
        "variable_type": "label"
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

- `outputs/user_requested_batch_review/pipeline_runs/run_637ca3432da6ddfb/datasets/cmm_math/samples/prob_c33b3ac9e45dad73821aa4fd.json`
