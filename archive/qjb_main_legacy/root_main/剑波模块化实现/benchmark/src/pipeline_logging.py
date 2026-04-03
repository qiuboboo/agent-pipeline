from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

try:
    from .pipeline_utils import ensure_dir
except ImportError:
    from pipeline_utils import ensure_dir


class RunLogger:
    def __init__(self, run_dir: Path, enabled: bool = True):
        self.enabled = enabled
        self.log_path = run_dir / "logs" / "run.log"
        ensure_dir(self.log_path.parent)

    def log(self, stage: str, message: str, dataset: Optional[str] = None, problem_id: Optional[str] = None) -> None:
        if not self.enabled:
            return
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        parts = [f"[{timestamp}]", f"[{stage}]"]
        if dataset:
            parts.append(f"dataset={dataset}")
        if problem_id:
            parts.append(f"problem_id={problem_id}")
        parts.append(message)
        with self.log_path.open("a", encoding="utf-8") as fh:
            fh.write(" ".join(parts) + "\n")
