# PhysReason 0:300 merged result summary

## Final decision

Use the merged result under:

- `outputs/physreason_merged_0000_0300/run_merged_physreason_0000_0300`

## Merge rule

- Keep main-run batches from `outputs/physreason_batched_eval` for all non-anomalous ranges.
- Replace the historically anomalous range `0180:0260` with rerun batches from `outputs/physreason_batched_eval_rerun_0180_0260`.

## Historical anomaly

The original main-run batches for the following ranges had historical batch-level risk due to `HTTP 502 Bad Gateway` and fallback behavior:

- `0180_0200`
- `0200_0220`
- `0220_0240`
- `0240_0260`

These were rerun successfully and selected as final sources in the merged result.

## Selected final sources

- Main-run kept:
  - `0000_0020` → `run_75c9bb874cc91453`
  - `0020_0040` → `run_591c7bfcce9db2c0`
  - `0040_0060` → `run_e2e33c557a0b30e2`
  - `0060_0080` → `run_345f6422c0aa8978`
  - `0080_0100` → `run_07c2202fce49a2b1`
  - `0100_0120` → `run_15003a01c911fca5`
  - `0120_0140` → `run_a3abfb503be9c708`
  - `0140_0160` → `run_6d98192f6ed56e5e`
  - `0160_0180` → `run_9d9c421d41d527d7`
  - `0260_0280` → `run_2cd96958623ccc52`
  - `0280_0300` → `run_ba0ffe67760a268a`
- Rerun replacement used:
  - `0180_0200` → `run_612f280946d8216b`
  - `0200_0220` → `run_0c6b1cdc856ee337`
  - `0220_0240` → `run_9ae62d2b51063fad`
  - `0240_0260` → `run_19fcdd8e59ae8685`

## Quality note

The selected rerun batches all finished with:

- `successful_request_count = 120`
- `last_error = null`

They may still contain small numbers of transient request failures and retries, but not the previous batch-level failure mode.
