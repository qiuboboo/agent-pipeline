# Rewrite Migration Notes

## Status

The rewrite path is currently being migrated toward `ler`-style behavior while preserving existing pipeline contracts.

## Migration Principles

1. Preserve rewrite report schema and downstream record expectations.
2. Move toward smaller, independent modules.
3. Keep meaningful logs.
4. Treat temporary compatibility layers as explicitly temporary.
5. Update documentation whenever rewrite behavior or structure changes.

## Current Temporary Compatibility Layer

Current temporary helper:
- `normalize_rewrite_variants_temp(...)`

Purpose:
- normalize rewrite output variants during migration
- preserve downstream field stability while rewrite internals are being refactored

Rule:
- remove this helper once rewrite output can be consumed directly without compatibility cleanup

## Target End State

The desired end state is:
- `pipeline_rewrite.py` contains the stable rewrite agent and rewrite fallback logic
- `pipeline_rewrite_compat.py` is empty or deleted
- rewrite output is directly consumable by downstream modules
- logs remain available for rewrite path diagnosis

## Required Documentation Updates

Any change to rewrite internals must keep these documents synchronized:
- `docs/architecture/pipeline-overview.md`
- `docs/architecture/pipeline-modules.md`
- `docs/contracts/intermediate-artifacts.md`
- this file
