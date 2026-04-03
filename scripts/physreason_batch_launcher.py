#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

import yaml


def build_config(start: int, end: int, output_root: str, base_url: str, api_key: str | None) -> dict:
    model_cfg = {
        "base_url": base_url,
        "model": "gpt-5.4",
        "reasoning_effort": "high",
        "temperature": 0.1,
        "timeout_seconds": 180,
        "enabled": True,
    }
    if api_key:
        model_cfg["api_key"] = api_key

    return {
        "runtime": {
            "sample_per_dataset": end - start,
            "sample_strategy": "head",
            "shuffle_seed": 42,
            "sample_concurrency": 1,
            "output_root": output_root,
            "cleaning_version": "v3.2.0",
            "batch_id_prefix": f"benchmarkallinone-physreason-{start:04d}-{end:04d}",
            "save_sample_bundle": True,
            "git_cache_root": "outputs/repo_cache",
        },
        "model": model_cfg,
        "datasets": [
            {
                "key": "physreason",
                "display_name": "PhysReason",
                "subject": "物理",
                "note": f"分批运行区间 mini[{start}:{end}]",
                "source_kind": "huggingface",
                "source_locator": "zhibei1204/PhysReason",
                "split": f"mini[{start}:{end}]",
                "question_fields": ["question", "problem", "query", "text"],
                "answer_fields": ["answer", "solution", "label"],
                "image_fields": ["image", "decoded_image", "image_path", "img_path", "figure"],
                "choice_fields": ["choices", "options"],
            }
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Batch launcher for PhysReason")
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--end", type=int, required=True)
    parser.add_argument("--step", type=int, default=20)
    parser.add_argument("--config-dir", default="configs/generated")
    parser.add_argument("--output-prefix", default="outputs/physreason_batched_eval")
    parser.add_argument("--base-url", default=os.getenv("OPENAI_BASE_URL", "http://9854399.xyz:8888/v1"))
    parser.add_argument("--api-key", default=os.getenv("OPENAI_API_KEY", ""))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    repo = Path(__file__).resolve().parents[1]
    config_dir = repo / args.config_dir
    config_dir.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    for start in range(args.start, args.end, args.step):
        end = min(start + args.step, args.end)
        name = f"physreason_{start:04d}_{end:04d}.yaml"
        config_path = config_dir / name
        output_root = f"{args.output_prefix}/{start:04d}_{end:04d}"
        cfg = build_config(start, end, output_root, args.base_url, args.api_key)
        config_path.write_text(yaml.safe_dump(cfg, sort_keys=False, allow_unicode=True), encoding="utf-8")

        cmd = [sys.executable, "run_pipeline.py", "--config", str(config_path)]
        print(f"\n=== Batch mini[{start}:{end}] ===")
        print("CONFIG:", config_path)
        print("OUTPUT:", output_root)
        print("BASE_URL:", args.base_url)
        print("CMD:", " ".join(cmd))
        if args.dry_run:
            continue
        result = subprocess.run(cmd, cwd=repo, env=env)
        if result.returncode != 0:
            print(f"Batch mini[{start}:{end}] failed with code {result.returncode}", file=sys.stderr)
            return result.returncode

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
