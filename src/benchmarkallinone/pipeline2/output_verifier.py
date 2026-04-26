from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .agents import PipelineDataContractError
from .clients import ModelRouter
from .config import Pipeline2Config
from .utils import read_json, write_json
from .verification_modules import validate_problem_structure


def _is_problem_bundle(data: Any) -> bool:
    if not isinstance(data, dict):
        return False
    if not isinstance(data.get("runtime_problem"), dict):
        return False
    required_list_fields = ["claim_sequences", "r_nodes", "claim_mappings", "p_facts", "t_facts", "k_atoms"]
    return all(isinstance(data.get(field_name), list) for field_name in required_list_fields)


def _collect_problem_bundle_paths(input_path: Path) -> Tuple[List[Path], List[Path]]:
    if not input_path.exists():
        raise PipelineDataContractError(f"[OutputVerifier] Input path `{input_path}` does not exist.")

    if input_path.is_file():
        data = read_json(input_path)
        if not _is_problem_bundle(data):
            raise PipelineDataContractError(
                f"[OutputVerifier] File `{input_path}` is not a valid pipeline problem bundle JSON."
            )
        return [input_path], []

    bundle_paths: List[Path] = []
    skipped_paths: List[Path] = []
    for candidate in sorted(path for path in input_path.rglob("*.json") if path.is_file()):
        data = read_json(candidate)
        if _is_problem_bundle(data):
            bundle_paths.append(candidate)
        else:
            skipped_paths.append(candidate)
    if not bundle_paths:
        raise PipelineDataContractError(
            f"[OutputVerifier] No valid pipeline problem bundles were discovered under `{input_path}`."
        )
    return bundle_paths, skipped_paths


def _node_judgment_is_correct(judgment: Dict[str, Any]) -> bool:
    return (
        bool(judgment.get("supported"))
        and bool(judgment.get("has_valid_source_claims"))
        and not bool(judgment.get("overmerged"))
        and not bool(judgment.get("missing_key_information"))
    )


def _safe_accuracy(correct: int, total: int) -> Optional[float]:
    if total <= 0:
        return None
    return round(correct / total, 4)


def audit_problem_bundle(router: ModelRouter, bundle_path: Path) -> Dict[str, Any]:
    bundle = read_json(bundle_path)
    if not _is_problem_bundle(bundle):
        raise PipelineDataContractError(
            f"[OutputVerifier] File `{bundle_path}` is not a valid pipeline problem bundle JSON."
        )

    runtime_problem = bundle.get("runtime_problem") or {}
    verification_audit = validate_problem_structure(
        router,
        runtime_problem,
        bundle.get("claim_sequences", []),
        bundle.get("r_nodes", []),
        bundle.get("claim_mappings", []),
        bundle.get("p_facts", []),
        bundle.get("t_facts", []),
        bundle.get("k_atoms", []),
    )

    node_lookup = {
        str(item.get("r_id", "")): item
        for item in bundle.get("r_nodes", [])
        if isinstance(item, dict)
    }

    final_reports = [
        item for item in verification_audit.get("final_cot_validations", []) if isinstance(item, dict)
    ]
    incorrect_final_cots = [
        {
            "method_id": item.get("method_id", ""),
            "summary": item.get("summary", ""),
            "failure_reasons": item.get("failure_reasons", []),
            "unsupported_steps": item.get("unsupported_steps", []),
            "missing_bridge_steps": item.get("missing_bridge_steps", []),
        }
        for item in final_reports
        if not bool(item.get("pass"))
    ]
    final_total = len(final_reports)
    final_correct = final_total - len(incorrect_final_cots)

    node_report = verification_audit.get("node_set_validation", {}) if isinstance(verification_audit, dict) else {}
    node_judgments = [
        item for item in node_report.get("node_judgments", []) if isinstance(item, dict)
    ]
    incorrect_nodes = []
    for item in node_judgments:
        if _node_judgment_is_correct(item):
            continue
        r_id = str(item.get("r_id", ""))
        node_record = node_lookup.get(r_id, {})
        incorrect_nodes.append(
            {
                "r_id": r_id,
                "canonical_claim": node_record.get("canonical_claim", ""),
                "node_type": node_record.get("node_type", ""),
                "issue_types": item.get("issue_types", []),
                "reason": item.get("reason", ""),
                "supported": bool(item.get("supported")),
                "has_valid_source_claims": bool(item.get("has_valid_source_claims")),
                "overmerged": bool(item.get("overmerged")),
                "missing_key_information": bool(item.get("missing_key_information")),
            }
        )
    node_total = len(node_judgments)
    node_correct = node_total - len(incorrect_nodes)

    return {
        "problem_id": runtime_problem.get("problem_id") or bundle.get("problem_record", {}).get("problem_id", ""),
        "bundle_path": str(bundle_path),
        "audit_passed": bool(verification_audit.get("passed")),
        "validated_method_ids": verification_audit.get("validated_method_ids", []),
        "skipped_method_ids": verification_audit.get("skipped_method_ids", []),
        "final_cot": {
            "total": final_total,
            "correct": final_correct,
            "incorrect": len(incorrect_final_cots),
            "accuracy": _safe_accuracy(final_correct, final_total),
            "incorrect_items": incorrect_final_cots,
        },
        "nodes": {
            "total": node_total,
            "correct": node_correct,
            "incorrect": len(incorrect_nodes),
            "accuracy": _safe_accuracy(node_correct, node_total),
            "incorrect_items": incorrect_nodes,
            "set_pass": bool(node_report.get("pass")),
            "global_failures": node_report.get("global_failures", []),
        },
        "global_failures": verification_audit.get("global_failures", []),
        "verification_audit": verification_audit,
    }


def _summarize_reports(problem_reports: Sequence[Dict[str, Any]], skipped_paths: Sequence[Path]) -> Dict[str, Any]:
    final_total = sum(int(item.get("final_cot", {}).get("total", 0)) for item in problem_reports)
    final_correct = sum(int(item.get("final_cot", {}).get("correct", 0)) for item in problem_reports)
    node_total = sum(int(item.get("nodes", {}).get("total", 0)) for item in problem_reports)
    node_correct = sum(int(item.get("nodes", {}).get("correct", 0)) for item in problem_reports)

    return {
        "problem_count": len(problem_reports),
        "audit_pass_problem_count": sum(1 for item in problem_reports if item.get("audit_passed")),
        "audit_fail_problem_count": sum(1 for item in problem_reports if not item.get("audit_passed")),
        "final_cot": {
            "total": final_total,
            "correct": final_correct,
            "incorrect": final_total - final_correct,
            "accuracy": _safe_accuracy(final_correct, final_total),
        },
        "nodes": {
            "total": node_total,
            "correct": node_correct,
            "incorrect": node_total - node_correct,
            "accuracy": _safe_accuracy(node_correct, node_total),
        },
        "skipped_non_bundle_file_count": len(skipped_paths),
        "skipped_non_bundle_files": [str(path) for path in skipped_paths],
    }


def run_output_verifier(
    config: Pipeline2Config,
    project_root: Path,
    input_path: Path,
    report_path: Optional[Path] = None,
) -> Dict[str, Any]:
    bundle_paths, skipped_paths = _collect_problem_bundle_paths(input_path)
    router = ModelRouter.from_configs(config.models.primary)
    router.ensure_available("pipeline2 output-verifier")

    problem_reports = [audit_problem_bundle(router, bundle_path) for bundle_path in bundle_paths]
    result = {
        "input_path": str(input_path if input_path.is_absolute() else (project_root / input_path)),
        "summary": _summarize_reports(problem_reports, skipped_paths),
        "problems": problem_reports,
        "usage_summary": router.usage_summary(),
    }
    if report_path is not None:
        write_json(report_path, result)
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="pipeline2 output verifier: 只依赖 pipeline 产物，对 final_cot 与 r_nodes 做独立审计并统计正确率"
    )
    default_config_path = str(Path(__file__).resolve().parent / "configs" / "default_pipeline2.yaml")
    parser.add_argument("--config", type=str, default=default_config_path, help="pipeline2 YAML 配置路径")
    parser.add_argument(
        "--input-path",
        type=str,
        required=True,
        help="完整 pipeline 输出问题包 JSON 文件或目录路径（例如 problems 目录）",
    )
    parser.add_argument(
        "--report-path",
        type=str,
        default=None,
        help="可选：将审计结果写入指定 JSON 文件",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    project_root = Path(__file__).resolve().parents[1]
    config = Pipeline2Config.from_yaml(getattr(args, "config", None))
    result = run_output_verifier(
        config=config,
        project_root=project_root,
        input_path=Path(args.input_path),
        report_path=Path(args.report_path) if getattr(args, "report_path", None) else None,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
