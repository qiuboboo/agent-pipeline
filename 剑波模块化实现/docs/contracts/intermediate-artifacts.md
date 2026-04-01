# Intermediate Artifacts Contract

This document freezes the intended shape of internal pipeline artifacts during the refactor. Field names should remain stable unless an explicit migration is documented.

## 1. Extracted Record Contract

Expected fields:
- `raw_question_text: str`
- `raw_answer_text: str`
- `choice_map: Dict[str, str]`
- `image_paths: List[str]`
- `force_requires_image: bool`
- `extraction_notes: List[str]`
- `question_field: Optional[str]`
- `answer_field: Optional[str]`
- `image_field: Optional[str]`
- `choice_field: Optional[str]`

Current producer alignment:
- extraction helpers live in `benchmark/src/pipeline_extraction.py`
- collection-stage orchestration lives in `benchmark/src/pipeline_collection.py`

## 2. Preprocessed Sample Contract

Expected fields currently consumed downstream include:
- `problem_id`
- `raw_question_text`
- `raw_answer_text`
- `normalized_question_text`
- `normalized_answer_text`
- `original_answer_type`
- `choices`
- `image_paths`
- `image_bytes_list`
- `image_qualities`
- `requires_image`
- `text_completeness`
- `question_norm`
- `answer_norm`
- `normalized_assets`
- `cleaning_path`

Current producer alignment:
- normalization and image quality logic live in `benchmark/src/pipeline_normalization.py`
- collection-stage preprocessing lives in `benchmark/src/pipeline_collection.py`
- structure / alignment / solvability signals are supplemented by `benchmark/src/cleaning_semantics.py`

## 3. Rewrite Report Contract

Required top-level fields:
- `strategy: str`
- `rationale: str`
- `variants: List[RewriteVariant]`
- `discard_reason_codes: List[str]`
- `llm_used: bool`

### RewriteVariant Contract
Required fields:
- `variant_id: str`
- `title: str`
- `rewritten_question_text: str`
- `expected_answer_type: str`
- `expected_answer: str`
- `split_role: str`

Current producer alignment:
- rewrite runtime lives in `benchmark/src/pipeline_rewrite.py`
- rewrite orchestration and downstream assembly live in `benchmark/src/pipeline_cleaning.py`
- temporary compatibility normalization currently remains inside `pipeline_rewrite.py` via `normalize_rewrite_variants_temp(...)`

## 4. Decision / Gate Contract

Expected fields:
- `decision: str`
- `reason_codes: List[str]`
- `rationale: str`
- `review_required: bool`
- `llm_used: bool`

Current producer alignment:
- gate decision is currently assembled in `benchmark/src/pipeline_cleaning.py`
- parts of the broader runtime still remain in `benchmark/src/multidataset_cleaning_pipeline.py` during the refactor transition

## 5. Stability Rule

During refactor:
- preserve field names
- preserve label values where possible
- preserve result semantics
- document any unavoidable schema change before landing code
