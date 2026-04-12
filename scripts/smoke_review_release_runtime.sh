#!/usr/bin/env bash
set -euo pipefail
set +u
source ~/.bashrc >/dev/null 2>&1 || true
set -u
cd /root/.openclaw/workspace/agent-pipeline

TMP_DIR="$(mktemp -d /tmp/review_release_smoke.XXXXXX)"
trap 'rm -rf "$TMP_DIR"' EXIT

run_check() {
  local name="$1"
  shift
  echo "==> $name"
  "$@"
  echo
}

run_expect_fail_contains() {
  local name="$1"
  local needle="$2"
  shift 2
  local log="$TMP_DIR/${name// /_}.log"
  echo "==> $name (expect failure)"
  set +e
  "$@" >"$log" 2>&1
  local status=$?
  set -e
  cat "$log"
  if [[ $status -eq 0 ]]; then
    echo "[FAIL] expected command to fail: $name" >&2
    exit 1
  fi
  if ! grep -Fq "$needle" "$log"; then
    echo "[FAIL] expected error message not found for: $name" >&2
    exit 1
  fi
  echo "[OK] expected failure observed"
  echo
}

run_check "mm_math A export smoke" \
  python3 scripts/export_review_release_candidates.py \
    --policy-config configs/review_release_policies.yaml \
    --dataset mm_math \
    --release-bucket A \
    --out "$TMP_DIR/mm_math_A.json"

grep -Fq '"strict_A_bucket_candidates"' "$TMP_DIR/mm_math_A.json"
grep -Fq '"adjacent_text_sufficient_candidates"' "$TMP_DIR/mm_math_A.json"

action_msg='explicit candidate-json subset; do not auto-export from ready'
run_expect_fail_contains "seephys A1 explicit export refusal" "$action_msg" \
  python3 scripts/export_review_release_candidates.py \
    --policy-config configs/review_release_policies.yaml \
    --dataset seephys \
    --release-bucket A1 \
    --out "$TMP_DIR/seephys_A1.json"

echo "==> seephys A1 dry-run smoke"
python3 scripts/apply_manual_review_release.py \
  --policy-config configs/review_release_policies.yaml \
  --dataset seephys \
  --candidate-json docs/review/seephys_A1_alignment_metadata_candidates_2026-04-11.json \
  --release-bucket A1 \
  --dry-run > "$TMP_DIR/seephys_A1_dry_run.json"
echo

grep -Fq 'alignment metadata/image-reference misfire subset' "$TMP_DIR/seephys_A1_dry_run.json"
grep -Fq 'explicit candidate-json subset from alignment_requires_review samples' "$TMP_DIR/seephys_A1_dry_run.json"

echo "==> multi_physics B2 dry-run smoke"
python3 scripts/apply_manual_review_release.py \
  --policy-config configs/review_release_policies.yaml \
  --dataset multi_physics \
  --candidate-json docs/review/multi_physics_B2_bucket_candidates_2026-04-11.json \
  --release-bucket B2 \
  --dry-run > "$TMP_DIR/multi_physics_B2_dry_run.json"
echo

grep -Fq 'quality_risk_flags == [\"low_resolution\"]' "$TMP_DIR/multi_physics_B2_dry_run.json"
grep -Fq 'quality_risk_flags != [\"low_resolution\"]' "$TMP_DIR/multi_physics_B2_dry_run.json"

echo "All review-release smoke checks passed."
