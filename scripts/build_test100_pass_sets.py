#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import random
import shutil
from pathlib import Path
from typing import Any, Dict, List

WORKDIR = Path('/root/.openclaw/workspace/agent-pipeline')
READY = WORKDIR / 'ready'
EXPORTS = WORKDIR / 'ready_problem_exports'

TASKS = [
    {
        'dataset': 'eee_bench',
        'src_package': 'run_outputs_similarity_dedup__eee_bench',
        'dst_package': 'run_outputs_similarity_dedup__eee_bench_test100_pass',
        'count': 100,
        'seed': 42,
    },
    {
        'dataset': 'mathvision',
        'src_package': 'run_outputs_similarity_dedup__mathvision',
        'dst_package': 'run_outputs_similarity_dedup__mathvision_test100_pass',
        'count': 100,
        'seed': 42,
    },
]


def read_json(path: Path) -> Dict[str, Any]:
    with path.open('r', encoding='utf-8') as f:
        return json.load(f)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def get_problem_id(sample: Dict[str, Any], sample_path: Path) -> str:
    for block, key in [
        ('problem_main_record', 'problem_id'),
        ('candidate_problem_record', 'problem_id'),
        ('source_intake_record', 'problem_id'),
    ]:
        record = sample.get(block) or {}
        value = record.get(key)
        if value:
            return str(value)
    return sample_path.stem


def is_pass(sample: Dict[str, Any]) -> bool:
    cleaning = sample.get('cleaning_records') or []
    if cleaning and isinstance(cleaning[0], dict):
        return str(cleaning[0].get('decision') or '').lower() == 'pass'
    return False


def get_score(sample: Dict[str, Any]) -> float:
    initial = sample.get('initial_scoring_record') or {}
    main = sample.get('problem_main_record') or {}
    cand = sample.get('candidate_problem_record') or {}
    candidates = [
        initial.get('multi_step_score'),
        main.get('multi_step_score'),
        cand.get('initial_multi_solution_score'),
        initial.get('image_dependency_score'),
    ]
    for value in candidates:
        if isinstance(value, (int, float)):
            return float(value)
        try:
            return float(value)
        except Exception:
            pass
    return 0.0


def collect_pass_samples(dataset_root: Path) -> List[Dict[str, Any]]:
    items = []
    for sample_path in sorted((dataset_root / 'samples').glob('prob_*.json')):
        sample = read_json(sample_path)
        if not is_pass(sample):
            continue
        items.append({
            'path': sample_path,
            'sample': sample,
            'problem_id': get_problem_id(sample, sample_path),
            'score': get_score(sample),
        })
    return items


def stratified_pick(items: List[Dict[str, Any]], count: int, seed: int) -> List[Dict[str, Any]]:
    rng = random.Random(seed)
    items = sorted(items, key=lambda x: (x['score'], x['problem_id']))
    if len(items) < count:
        raise RuntimeError(f'Not enough pass samples: need {count}, got {len(items)}')
    bin_count = min(5, count)
    bins: List[List[Dict[str, Any]]] = [[] for _ in range(bin_count)]
    for idx, item in enumerate(items):
        bucket = min(bin_count - 1, math.floor(idx * bin_count / len(items)))
        bins[bucket].append(item)
    selected: List[Dict[str, Any]] = []
    base = count // bin_count
    rem = count % bin_count
    for i, bucket in enumerate(bins):
        need = base + (1 if i < rem else 0)
        pool = bucket[:]
        rng.shuffle(pool)
        selected.extend(sorted(pool[:need], key=lambda x: (x['score'], x['problem_id'])))
    if len(selected) < count:
        selected_ids = {x['problem_id'] for x in selected}
        remaining = [x for x in items if x['problem_id'] not in selected_ids]
        rng.shuffle(remaining)
        selected.extend(sorted(remaining[: count - len(selected)], key=lambda x: (x['score'], x['problem_id'])))
    return sorted(selected[:count], key=lambda x: (x['score'], x['problem_id']))


def copy_matching_assets(src_dataset_root: Path, dst_dataset_root: Path, problem_id: str) -> None:
    for sub in ['artifacts/images', 'artifacts/crops', 'assets', 'images']:
        src = src_dataset_root / sub
        if not src.exists():
            continue
        for path in src.rglob('*'):
            if not path.is_file():
                continue
            if problem_id not in path.name:
                continue
            rel = path.relative_to(src_dataset_root)
            dst = dst_dataset_root / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, dst)


def build_export_payload(dst_package_root: Path, dataset: str) -> Dict[str, Any]:
    dataset_root = dst_package_root / 'datasets' / dataset
    problems = []
    for sample_path in sorted((dataset_root / 'samples').glob('prob_*.json')):
        sample = read_json(sample_path)
        main = sample.get('problem_main_record') or {}
        cand = sample.get('candidate_problem_record') or {}
        norm = sample.get('normalization_record') or {}
        source = sample.get('source_intake_record') or {}
        problem_id = get_problem_id(sample, sample_path)
        q = main.get('normalized_question_text') or main.get('raw_question_text') or norm.get('normalized_question_text') or cand.get('raw_question_text') or source.get('raw_question_text') or ''
        a = main.get('normalized_answer_text') or main.get('raw_answer_text') or norm.get('normalized_answer_text') or cand.get('raw_answer_text') or source.get('raw_answer_text') or ''
        image_paths = []
        for sub in ['artifacts/images', 'artifacts/crops']:
            base = dataset_root / sub
            if not base.exists():
                continue
            for p in sorted(base.rglob('*')):
                if p.is_file() and problem_id in p.name:
                    image_paths.append(p.relative_to(READY).as_posix())
        problems.append({
            'problem_id': problem_id,
            'question_text': q,
            'standard_answer': a,
            'images': sorted(set(image_paths)),
            'source_meta': {
                'ready_package': dst_package_root.name,
                'dataset_key': dataset,
                'dataset_root': dataset_root.relative_to(READY).as_posix(),
                'source_dataset': main.get('source_dataset') or cand.get('source_dataset'),
                'source_split': main.get('source_split'),
                'source_problem_id': main.get('source_problem_id') or source.get('source_problem_id'),
            },
            'multi_solution_hint': None,
            'ingest_status': 'ready',
            'difficulty': get_score(sample),
            'multimodal_score': (sample.get('initial_scoring_record') or {}).get('image_dependency_score'),
            'multi_solution_score': (sample.get('initial_scoring_record') or {}).get('multi_step_score'),
        })
    return {
        'file_id': f'{dst_package_root.name}__{dataset}',
        'stage': 'raw_to_problem',
        'source_file_name': f'{dst_package_root.name}__{dataset}.json',
        'problems': problems,
    }


def main() -> None:
    report = []
    for task in TASKS:
        dataset = task['dataset']
        src_dataset_root = READY / dataset / task['src_package'] / 'datasets' / dataset
        dst_package_root = READY / dataset / task['dst_package']
        dst_dataset_root = dst_package_root / 'datasets' / dataset
        if dst_package_root.exists():
            shutil.rmtree(dst_package_root)
        (dst_dataset_root / 'samples').mkdir(parents=True, exist_ok=True)
        (dst_dataset_root / 'artifacts' / 'images').mkdir(parents=True, exist_ok=True)
        (dst_dataset_root / 'artifacts' / 'crops').mkdir(parents=True, exist_ok=True)

        pass_items = collect_pass_samples(src_dataset_root)
        selected = stratified_pick(pass_items, task['count'], task['seed'])

        manifest = {
            'dataset_key': dataset,
            'selection_rule': 'test100_pass_only_stratified_by_multi_step_score_quantile_bins',
            'selection_count': len(selected),
            'filter_rule': 'cleaning_records[0].decision == pass',
            'pass_pool_size': len(pass_items),
            'score_field': 'initial_scoring_record.multi_step_score (fallback to related score fields)',
            'bin_count': 5,
            'kept_problem_ids': [],
            'kept_samples': [],
        }
        scores = []
        for entry in selected:
            sample_path = entry['path']
            problem_id = entry['problem_id']
            shutil.copy2(sample_path, dst_dataset_root / 'samples' / sample_path.name)
            copy_matching_assets(src_dataset_root, dst_dataset_root, problem_id)
            manifest['kept_problem_ids'].append(problem_id)
            manifest['kept_samples'].append({
                'problem_id': problem_id,
                'sample_path': (dst_dataset_root / 'samples' / sample_path.name).relative_to(dst_package_root).as_posix(),
                'source_sample_path': sample_path.as_posix(),
                'difficulty_score': entry['score'],
                'decision': 'pass',
            })
            scores.append(entry['score'])

        write_json(dst_dataset_root / 'selection_manifest.json', manifest)
        write_json(dst_dataset_root / 'summary.json', {
            'dataset_key': dataset,
            'processed_samples': len(selected),
            'selected_samples': len(selected),
            'selection_rule': 'test100_pass_only_stratified_by_multi_step_score_quantile_bins',
            'filter_rule': 'cleaning_records[0].decision == pass',
            'pass_pool_size': len(pass_items),
            'score_field': 'initial_scoring_record.multi_step_score (fallback to related score fields)',
            'score_min': min(scores) if scores else None,
            'score_max': max(scores) if scores else None,
            'score_avg': round(sum(scores) / len(scores), 6) if scores else None,
            'source_package': task['src_package'],
        })

        export_payload = build_export_payload(dst_package_root, dataset)
        export_path = EXPORTS / f"{task['dst_package']}__{dataset}.json"
        write_json(export_path, export_payload)
        report.append({
            'dataset': dataset,
            'pass_pool_size': len(pass_items),
            'ready_package': str(dst_package_root),
            'export_json': str(export_path),
            'count': len(selected),
        })

    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
