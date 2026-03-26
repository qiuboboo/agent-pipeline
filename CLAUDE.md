# agent-pipeline collaboration guide

## Scope

This repository is the source of truth for pipeline code, local docs, run summaries, and validated implementation decisions.

When working here, prefer current repository files over prior chat memory or notes from other projects.

## Local repo guidance

- Treat code and docs in this repository as authoritative for current behavior.
- Prefer updating or referencing existing local docs instead of duplicating them elsewhere.
- For representative run outputs, use the convention documented in [docs/run_summaries/README.md](docs/run_summaries/README.md).
- Keep repository-visible summaries concise and scenario-based; do not dump large raw logs into tracked docs.

## Cross-repo memory sync

External memory, including summaries stored in other projects such as `agent-memory`, is advisory only.

Source-of-truth priority:
1. Current explicit user instruction
2. Current files in this repository
3. Current repository docs, including `docs/run_summaries/README.md`
4. External memory notes or summaries from other projects

### What may be synced outward

Only sync compact summaries of stable, verified information, such as:
- confirmed architectural decisions
- stable workflow conventions
- validated non-obvious debugging conclusions
- concise milestone summaries

### What must not be synced outward

Do not sync:
- raw full chat transcripts
- secrets, tokens, credentials, or private keys
- large logs or raw output dumps
- speculative ideas or unverified conclusions
- transient task state
- machine-specific local details unless explicitly required and clearly marked as local-only

### When to sync

Prefer milestone-based syncing rather than vague periodic syncing. Good sync points include:
- after a completed implementation task
- after a confirmed architecture clarification
- after a validated debugging conclusion

### Verification before using or writing memory

Before writing a summary to external memory:
- verify the conclusion in current repo files, or
- verify that the user explicitly confirmed it

Before using external memory inside this repo:
- cross-check it against current repository files
- if it is not verified in the repo, present it as a suggestion, not a fact
- if it conflicts with repo files or current user instructions, ignore the memory and follow the repo/user

### Cross-repo write boundary

When writing files, committing, or pushing changes to another project or repository such as `agent-memory`:
- ask for confirmation first unless the user has explicitly authorized that scope in this session or in this file
- prefer compact structured summaries over copied conversation dumps

## Suggested external summary shape

When exporting a reusable summary to another memory repository, prefer this structure:
- title
- repo
- status
- updated
- Decision
- Why
- Scope
- Evidence
- Do not assume

The goal is to preserve durable conclusions without letting external notes override current repository reality.
