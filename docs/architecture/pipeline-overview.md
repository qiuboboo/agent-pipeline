# Pipeline Overview

## Goal

This pipeline ingests multimodal benchmark samples from multiple sources, normalizes them into a shared sample representation, evaluates image/text usability, rewrites eligible samples into open-ended variants, makes a cleaning decision, and writes standardized output records.

## Refactor Principles

These principles are binding for the refactor:

1. Keep modules small and independent.
2. Preserve parameter names, labels, and output result schemas.
3. Preserve observable behavior unless a change is explicitly planned and documented.
4. Ensure each module can be tested independently.
5. Keep meaningful logs; do not remove useful operational logging.
6. Whenever code changes, update the corresponding documentation in the same change.
7. Documentation must describe module purpose, inputs, outputs, dependencies, and test expectations.

## Current End-to-End Flow

1. **Load config**
   - Read YAML, environment variables, and CLI overrides.
   - Build `PipelineConfig`.
2. **Discover and load source samples**
   - Use a connector for local, Hugging Face, GitHub, or unavailable sources.
   - Convert source rows into `UnifiedSample` values.
3. **Extract raw fields**
   - Extract question text, answer text, choice map, image paths, and extraction metadata.
4. **Normalize text and answer semantics**
   - Normalize question/answer text.
   - Resolve multiple-choice answer labels or numeric indexes into semantic answers when possible.
5. **Analyze image quality**
   - Compute image quality summaries and multimodal usability signals.
6. **Rewrite into open-ended variants**
   - Produce rewrite strategy, rationale, variants, and discard reason codes.
7. **Assess / decide**
   - Combine text/image/rewrite/alignment/solvability signals.
   - Produce pass/review/reject decision.
8. **Build output records**
   - Write sample-level records, rewrite records, asset records, audits, and summaries.
9. **Persist run outputs**
   - Save logs, JSON/JSONL outputs, run summaries, and sample bundles.

## Planned Modular Architecture

The target architecture is:

- `pipeline_types.py`
- `pipeline_utils.py`
- `pipeline_prompts.py`
- `pipeline_logging.py`
- `pipeline_clients.py`
- `pipeline_normalization.py`
- `pipeline_extraction.py`
- `pipeline_quality.py`
- `pipeline_rewrite.py`
- `pipeline_rewrite_compat.py` (temporary, migration-only)
- `pipeline_decision.py`
- `pipeline_records.py`
- `pipeline_connectors/`
- `pipeline_orchestrator.py`

## Migration Rule

Refactoring should first freeze and document contracts, then move code without changing public schemas, and only then simplify or remove temporary compatibility layers.
