from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from .utils import env_expand


@dataclass
class ModelEndpointConfig:
    name: str = "primary"
    base_url: str = "https://synai996.space/v1"
    api_key: str = ""
    model: str = "gpt-5.4"
    reasoning_effort: str = "high"
    temperature: float = 0.1
    timeout_seconds: int = 180
    enabled: bool = True
    api_mode: str = "chat_completions"
    max_attempts: int = 6
    retry_base_delay_seconds: float = 1.5
    retry_max_delay_seconds: float = 15.0
    respect_retry_after: bool = True


@dataclass
class PathsConfig:
    ready_root: str = "ready"
    output_root: str = "pipeline2/outputs"
    checkpoint_db_path: str = "pipeline2/runtime/pipeline_langgraph.sqlite"


@dataclass
class RuntimeConfig:
    include_manual_review: bool = False
    max_problems: int = 0
    max_problem_workers: int = 4
    max_images_per_problem: int = 3
    save_runtime_snapshots: bool = False
    save_problem_bundles: bool = True
    enable_trace_patch_writes: bool = True
    enable_problem_structure_validation: bool = True
    fail_on_problem_structure_validation: bool = True
    problem_retry_attempts: int = 3
    continue_on_problem_error: bool = True
    log_level: str = "INFO"
    log_to_file: bool = True


@dataclass
class ThresholdConfig:
    method_score_thresholds: Tuple[float, float] = (0.33, 0.67)
    novelty_total_threshold: float = 0.55
    novelty_required_threshold: float = 0.50


@dataclass
class ModelRouterConfig:
    primary: ModelEndpointConfig = field(default_factory=ModelEndpointConfig)
    fallback: Optional[ModelEndpointConfig] = field(
        default_factory=lambda: ModelEndpointConfig(
            name="fallback",
            base_url="http://9854399.xyz:8888/v1",
            api_key="",
            model="gpt-5.4",
            reasoning_effort="high",
            temperature=0.1,
            timeout_seconds=180,
            enabled=True,
        )
    )


@dataclass
class Pipeline2Config:
    paths: PathsConfig = field(default_factory=PathsConfig)
    runtime: RuntimeConfig = field(default_factory=RuntimeConfig)
    thresholds: ThresholdConfig = field(default_factory=ThresholdConfig)
    models: ModelRouterConfig = field(default_factory=ModelRouterConfig)

    @classmethod
    def from_yaml(cls, path: Optional[str]) -> "Pipeline2Config":
        if not path:
            return cls()
        file_path = Path(path)
        with file_path.open("r", encoding="utf-8") as file:
            raw = yaml.safe_load(file) or {}
        expanded = env_expand(raw)
        return cls.from_dict(expanded)

    @classmethod
    def from_dict(cls, raw: Dict[str, Any]) -> "Pipeline2Config":
        paths_raw = raw.get("paths") or {}
        runtime_raw = raw.get("runtime") or {}
        thresholds_raw = raw.get("thresholds") or {}
        models_raw = raw.get("models") or {}
        primary_raw = models_raw.get("primary") or {}
        fallback_raw = models_raw.get("fallback")

        raw_thresholds = thresholds_raw.get("method_score_thresholds") or ThresholdConfig().method_score_thresholds
        threshold_values = [float(item) for item in raw_thresholds]
        if len(threshold_values) < 2:
            threshold_pair = ThresholdConfig().method_score_thresholds
        else:
            threshold_pair = (threshold_values[0], threshold_values[1])

        return cls(
            paths=PathsConfig(**{**PathsConfig().__dict__, **paths_raw}),
            runtime=RuntimeConfig(**{**RuntimeConfig().__dict__, **runtime_raw}),
            thresholds=ThresholdConfig(
                method_score_thresholds=threshold_pair,
                novelty_total_threshold=float(thresholds_raw.get("novelty_total_threshold", ThresholdConfig().novelty_total_threshold)),
                novelty_required_threshold=float(thresholds_raw.get("novelty_required_threshold", ThresholdConfig().novelty_required_threshold)),
            ),
            models=ModelRouterConfig(
                primary=ModelEndpointConfig(**{**ModelEndpointConfig().__dict__, **primary_raw}),
                fallback=(
                    ModelEndpointConfig(**{**ModelEndpointConfig(name="fallback").__dict__, **fallback_raw})
                    if isinstance(fallback_raw, dict)
                    else None
                ),
            ),
        )

    def resolve_path(self, path_like: str, project_root: Path) -> Path:
        candidate = Path(path_like)
        return candidate if candidate.is_absolute() else (project_root / candidate)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "paths": self.paths.__dict__.copy(),
            "runtime": self.runtime.__dict__.copy(),
            "thresholds": {
                **self.thresholds.__dict__,
                "method_score_thresholds": list(self.thresholds.method_score_thresholds),
            },
            "models": {
                "primary": self.models.primary.__dict__.copy(),
                "fallback": self.models.fallback.__dict__.copy() if self.models.fallback else None,
            },
        }
