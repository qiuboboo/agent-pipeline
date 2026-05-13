# PPT Production Stats 2026-05-13

This directory contains PPT-facing production statistics built from the current local canonical `agent-pipeline/outputs` and `agent-pipeline/ready` state.

## Source Files

- `outputs/*/run_*/summary.json`: canonical run-level usage and request timing.
- `ready/*/summary.json`: outputs-to-ready conversion, dedup, release-gate totals, final ready counts.
- `ready/*/selection_manifest.json`: sample-level release execution, `released_from_review`, `release_bucket`, `release_mode`, `candidate_json`, and `source_reason_codes`.
- `ready/*/samples/*.json`: taxonomy (`problem_main_record.domain_tags`), rewrite strategy, solvability reports, and quality-risk/failure-code occurrences.
- `configs/review_release_policies.yaml`: configured review-release buckets and release basis text.
- `docs/review/*.json`: explicit candidate-set files used to measure `candidate_count` for explicit/manual release buckets.

## Canonical Scope

- Table 1 uses the union of `source_runs` referenced by current production `ready/*/summary.json` directories, so smoke/debug outputs are excluded by construction.
- Tables 2-6 use the current production `ready/` top-level dataset directories.

## Caveats

- `candidate_count` and `actual_released_count` are intentionally separated. `candidate_count` comes from explicit candidate JSON metadata/list length when available; `actual_released_count` comes from `selection_manifest.kept_samples[].released_from_review`.
- Some datasets have empty `structured_release_buckets` but non-zero explicit/manual release via `explicit_release_candidate_count` and `release_mode=explicit_candidate_subset`.
- Table 3 keeps `candidate_count` and `actual_released_count` separate. For explicit buckets, `candidate_count` comes from candidate JSON metadata/list length; if the candidate JSON is older than the final ready execution, the two values may legitimately differ.
- Table 5 level-1 taxonomy is mapped primarily from the final ready dataset package into a compact presentation taxonomy, with `domain_tags` used only as fallback for unmapped datasets.
- Table 6 counts are reason occurrences, not unique samples. The source is primarily `selection_manifest.source_reason_codes`, with supplemental occurrence counting from sample `quality_risk_flags` and solvability `failure_codes`.
- `rewrite_resolvability` is an occurrence-level operational bucket derived from sample rewrite strategy, audit trail, and solvability outcome: `rewrite_not_needed / rewritten_and_solvable / rewritten_but_still_risky`.

## Files

- `01_run_level_usage_summary.csv / .md`: canonical production outputs run-level usage summary
- `02_dataset_level_outputs_to_ready_conversion.csv / .md`: dataset-level outputs-to-ready conversion
- `03_review_release_actual_execution.csv / .md`: review release actual execution
- `04_empty_release_buckets.csv / .md`: datasets with empty release buckets
- `05_ready_taxonomy_level1_distribution.csv / .md`: level-1 taxonomy distribution
- `05_dataset_taxonomy_heatmap.csv / .md`: dataset × taxonomy heatmap
- `06_reason_category_distribution.csv / .md`: reason category distribution
- `06_source_attribution_distribution.csv / .md`: source attribution distribution
- `06_rewrite_resolvability_distribution.csv / .md`: rewrite-resolvability distribution
