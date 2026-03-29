from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


@dataclass
class SetupContext:
    config: Any
    pipeline_run_id: str
    ingest_batch_id: str
    output_root: Path
    run_dir: Path
    records_dir: Path
    dataset_root: Path
    aggregate_summary: Dict[str, Any]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="多数据集采集与清洗智能体流水线")
    parser.add_argument("--config", type=str, default=None, help="YAML 配置文件路径")
    parser.add_argument("--output-dir", type=str, default=None, help="输出目录")
    parser.add_argument("--sample-per-dataset", type=int, default=None, help="每个数据集抽样数")
    parser.add_argument("--sample-strategy", type=str, choices=["head", "random"], default=None, help="抽样策略")
    parser.add_argument("--seed", type=int, default=None, help="随机种子")
    parser.add_argument("--disable-llm", action="store_true", help="禁用 LLM Agent，仅使用规则回退")
    parser.add_argument("--base-url", type=str, default=None, help="OpenAI 兼容接口 base url")
    parser.add_argument("--api-key", type=str, default=None, help="OpenAI 兼容接口 key")
    parser.add_argument("--model", type=str, default=None, help="模型名称")
    parser.add_argument("--reasoning-effort", type=str, default=None, help="推理强度，如 xhigh")
    return parser.parse_args()


def merge_cli_overrides(config: Any, args: argparse.Namespace) -> Any:
    if args.output_dir:
        config.output_root = args.output_dir
    if args.sample_per_dataset is not None:
        config.sample_per_dataset = args.sample_per_dataset
    if args.sample_strategy:
        config.sample_strategy = args.sample_strategy
    if args.seed is not None:
        config.shuffle_seed = args.seed
    if args.disable_llm:
        config.model.enabled = False
    if args.base_url:
        config.model.base_url = args.base_url
    if args.api_key:
        config.model.api_key = args.api_key
    if args.model:
        config.model.model = args.model
    if args.reasoning_effort:
        config.model.reasoning_effort = args.reasoning_effort
    return config


def build_setup_context(config: Any, ensure_dir: Any, stable_digest: Any, utc_now: Any) -> SetupContext:
    started_at = utc_now()
    pipeline_run_id = f"run_{stable_digest([started_at, 'multidataset-clean'], 16)}"
    ingest_batch_id = f"{config.batch_id_prefix}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    output_root = Path(config.output_root)
    run_dir = output_root / pipeline_run_id
    records_dir = run_dir / "records"
    dataset_root = run_dir / "datasets"
    ensure_dir(records_dir)
    ensure_dir(dataset_root)
    return SetupContext(
        config=config,
        pipeline_run_id=pipeline_run_id,
        ingest_batch_id=ingest_batch_id,
        output_root=output_root,
        run_dir=run_dir,
        records_dir=records_dir,
        dataset_root=dataset_root,
        aggregate_summary={
            "pipeline_run_id": pipeline_run_id,
            "started_at": started_at,
            "dataset_summaries": [],
        },
    )
