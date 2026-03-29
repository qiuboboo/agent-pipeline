# Pipeline Modules

This document defines the intended responsibility boundary of each pipeline module.

---

## `pipeline_types.py`
**Purpose**
- Define stable dataclasses and typed artifacts used across modules.

**Owns**
- `ModelConfig`
- `ThresholdConfig`
- `DatasetSpec`
- `PipelineConfig`
- `UnifiedSample`
- Future typed contracts for preprocess/rewrite/decision artifacts.

**Must not own**
- Business logic
- IO logic
- LLM calls

---

## `pipeline_utils.py`
**Purpose**
- Pure utility helpers with no pipeline-stage ownership.

**Owns**
- JSON helpers
- hash helpers
- whitespace/text helpers
- env placeholder helpers
- directory/file helpers

**Must not own**
- Dataset-specific rules
- Rewrite logic
- Connector logic

---

## `pipeline_prompts.py`
**Purpose**
- Prompt path definitions and prompt loading.

**Owns**
- prompt file paths
- `read_prompt`

---

## `pipeline_logging.py`
**Purpose**
- Structured operational logging for runs and samples.

**Owns**
- `RunLogger`
- log formatting rules
- stage logging conventions

**Logging rule**
- Logs are required and should remain meaningful, concise, and diagnostically useful.

---

## `pipeline_clients.py`
**Purpose**
- External model/service clients.

**Owns**
- `OpenAICompatibleClient`

---

## `pipeline_normalization.py`
**Purpose**
- Text normalization and answer normalization rules.

**Owns**
- `TextNormalizer`
- `resolve_multiple_choice_answer_text`
- dataset-specific answer index rules

**Inputs**
- raw or normalized text
- choice map
- dataset answer index metadata

**Outputs**
- normalized text
- normalized semantic answer
- answer type judgments
- rewrite helper judgments

---

## `pipeline_extraction.py`
**Purpose**
- Extract question/answer/image/choice data from raw source rows.

**Owns**
- heuristic extraction
- prompt-based extraction
- field-selection helpers
- image-path normalization helpers
- choice parsing helpers

---

## `pipeline_connectors/`
**Purpose**
- Load source rows from specific data sources and convert them to `UnifiedSample`.

**Modules**
- `base.py`
- `local_file.py`
- `huggingface.py`
- `github.py`
- `unavailable.py`

**Contract**
- Emit stable `UnifiedSample` objects and source status information.

---

## `pipeline_quality.py`
**Purpose**
- Image quality and multimodal usability analysis.

**Owns**
- `ImageQualityAnalyzer`
- image quality metrics

---

## `pipeline_rewrite.py`
**Purpose**
- Rewrite eligible problems into open-ended variants.

**Owns**
- `BaseStructuredAgent`
- `RewriteAgent`
- rewrite fallback policy
- rewrite LLM interaction

**Contract**
- Preserve rewrite report fields:
  - `strategy`
  - `rationale`
  - `variants`
  - `discard_reason_codes`
  - `llm_used`

---

## `pipeline_rewrite_compat.py`
**Purpose**
- Temporary migration-only compatibility code for rewrite output normalization.

**Current expected content**
- temporary rewrite variant normalization helpers

**Rule**
- This module must shrink over time and be deleted once the rewrite path fully matches the intended `ler`-style behavior.

---

## `pipeline_decision.py`
**Purpose**
- Pass/review/reject decision logic.

**Owns**
- decision agent
- fallback decision logic
- reason code selection

---

## `pipeline_records.py`
**Purpose**
- Build persistent output records and artifacts.

**Owns**
- rewrite records
- clean problem records
- asset records
- node records
- field audits
- cleaning records

**Rule**
- Output schemas must remain stable unless documentation and downstream expectations are updated together.

---

## `pipeline_orchestrator.py`
**Purpose**
- Coordinate the entire run without owning detailed stage logic.

**Owns**
- run sequencing
- stage invocation
- run summary production

**Must not own**
- large embedded rule logic for rewrite/decision/extraction
