#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
status=0
"$SCRIPT_DIR/run_multidataset_validation_20.sh" "$@" || status=$?
echo
if [[ $status -eq 0 ]]; then
  echo "运行完成。"
else
  echo "运行失败，退出码: $status"
fi
print -n "按回车键关闭窗口... "
read -r
exit $status
