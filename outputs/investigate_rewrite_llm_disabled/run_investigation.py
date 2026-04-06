import json, re, inspect, traceback
from pathlib import Path
from collections import Counter, defaultdict

REPORT = {
    'run_id': 'run_cf4370b4bf405a34',
    'steps': [],
    'findings': {},
    'errors': [],
}

def step(name, **data):
    REPORT['steps'].append({'step': name, **data})

try:
    from benchmark.src import multidataset_cleaning_pipeline as m
    step('import_module_ok', module=str(m.__file__))

    # 1) inspect config defaults and rewrite code
    REPORT['findings']['rewrite_signature'] = str(inspect.signature(m.RewriteAgent.rewrite))
    REPORT['findings']['rewrite_source_excerpt'] = inspect.getsource(m.RewriteAgent.rewrite)
    REPORT['findings']['pipeline_config_from_dict_excerpt'] = inspect.getsource(m.PipelineConfig.from_dict)
    REPORT['findings']['default_model_config'] = {
        'enabled': getattr(m.ModelConfig(), 'enabled', None),
        'model_name': getattr(m.ModelConfig(), 'model_name', None),
        'base_url': getattr(m.ModelConfig(), 'base_url', None),
        'agent_only_extraction': getattr(m.ModelConfig(), 'agent_only_extraction', None),
    }
    step('inspect_code_done')

    # 2) load yaml config if possible
    cfg_path = Path('configs/candidate_200_remote.yaml')
    if cfg_path.exists():
        text = cfg_path.read_text(encoding='utf-8')
        REPORT['findings']['candidate_200_remote_yaml_head'] = '\n'.join(text.splitlines()[:120])
        try:
            import yaml
            cfg_obj = yaml.safe_load(text)
            REPORT['findings']['candidate_200_remote_yaml_model'] = cfg_obj.get('model') if isinstance(cfg_obj, dict) else None
            pcfg = m.PipelineConfig.from_dict(cfg_obj or {})
            REPORT['findings']['parsed_model_config'] = {
                'enabled': getattr(pcfg.model, 'enabled', None),
                'model_name': getattr(pcfg.model, 'model_name', None),
                'base_url': getattr(pcfg.model, 'base_url', None),
                'api_key_present': bool(getattr(pcfg.model, 'api_key', None)),
                'agent_only_extraction': getattr(pcfg.model, 'agent_only_extraction', None),
            }
            step('parse_yaml_ok')
        except Exception as e:
            REPORT['errors'].append({'stage':'parse_yaml','error':repr(e), 'traceback': traceback.format_exc()})
    
    # 3) inspect actual run records for choices and rewrite usage
    run = Path('outputs/candidate_200_remote_long/run_cf4370b4bf405a34/datasets')
    rewrite_rows = []
    candidate_rows = []
    for ds in sorted([p for p in run.iterdir() if p.is_dir()]):
        rp = ds/'records'/'rewrite_reports.jsonl'
        cp = ds/'records'/'candidate_problem_records.jsonl'
        if rp.exists():
            with rp.open() as fh:
                for line in fh:
                    if line.strip():
                        o = json.loads(line)
                        rewrite_rows.append((ds.name, o))
        if cp.exists():
            with cp.open() as fh:
                for line in fh:
                    if line.strip():
                        o = json.loads(line)
                        candidate_rows.append((ds.name, o))
    REPORT['findings']['rewrite_report_count'] = len(rewrite_rows)
    REPORT['findings']['rewrite_llm_used_counter'] = dict(Counter(str(o.get('llm_used')) for _,o in rewrite_rows))
    REPORT['findings']['rewrite_strategy_counter'] = dict(Counter(o.get('strategy') for _,o in rewrite_rows))
    
    by_ds_choice = defaultdict(Counter)
    examples = defaultdict(list)
    for ds,o in candidate_rows:
        md = o.get('metadata', {}) or {}
        by_ds_choice[ds][str(md.get('choice_field'))] += 1
        if len(examples[ds]) < 5:
            examples[ds].append({
                'source_problem_id': o.get('source_problem_id'),
                'choice_field': md.get('choice_field'),
                'raw_answer_text': o.get('raw_answer_text'),
                'has_image': o.get('has_image'),
                'image_count': o.get('image_count'),
            })
    REPORT['findings']['choice_field_counts_by_dataset'] = {k: dict(v) for k,v in by_ds_choice.items()}
    REPORT['findings']['choice_field_examples'] = examples
    step('scan_records_done', rewrite_report_count=len(rewrite_rows), candidate_problem_count=len(candidate_rows))

    # 4) inspect actual choices passed from samples (choice_map) to see if empty or not
    sample_choice_stats = defaultdict(lambda: Counter())
    sample_examples = defaultdict(list)
    for ds in sorted([p for p in run.iterdir() if p.is_dir()]):
        sp = ds/'samples'
        if not sp.exists():
            continue
        for f in sorted(sp.glob('*.json')):
            o = json.loads(f.read_text())
            cpr = o.get('candidate_problem_record', {}) or {}
            # try pull rewrite info and raw choice map from candidate metadata/raw record if present in sample structure
            cp_md = (cpr.get('metadata') or {}) if isinstance(cpr, dict) else {}
            choice_field = cp_md.get('choice_field')
            # infer whether expected answer looks option and inspect rewrite variant
            rewrite = (o.get('rewrite_reports') or [{}])[0]
            variant = (rewrite.get('variants') or [{}])[0] if isinstance(rewrite, dict) else {}
            expected = variant.get('expected_answer')
            # raw_record often embedded in candidate_problem_record? sample json may not carry it directly; just inspect sample file text for "choice_map"
            txt = f.read_text()
            has_choice_map = 'choice_map' in txt
            sample_choice_stats[ds.name]['files'] += 1
            sample_choice_stats[ds.name][f'choice_field:{choice_field}'] += 1
            sample_choice_stats[ds.name][f'has_choice_map:{has_choice_map}'] += 1
            if len(sample_examples[ds.name]) < 3:
                sample_examples[ds.name].append({
                    'file': f.name,
                    'choice_field': choice_field,
                    'rewrite_strategy': rewrite.get('strategy') if isinstance(rewrite, dict) else None,
                    'expected_answer': expected,
                    'has_choice_map_token_in_sample_json': has_choice_map,
                })
    REPORT['findings']['sample_choice_stats'] = {k: dict(v) for k,v in sample_choice_stats.items()}
    REPORT['findings']['sample_choice_examples'] = sample_examples
    step('scan_samples_done')

    # 5) inspect chat_json implementation and call sites
    REPORT['findings']['chat_json_excerpt'] = inspect.getsource(m.OpenAICompatibleClient.chat_json)
    REPORT['findings']['rewrite_init_excerpt'] = inspect.getsource(m.RewriteAgent.__init__)
    # crude grep via source text for instantiation
    src = Path(m.__file__).read_text(encoding='utf-8')
    inst_lines = []
    for i, line in enumerate(src.splitlines(), start=1):
        if 'RewriteAgent(' in line or 'DecisionAgent(' in line or 'OpenAICompatibleClient(' in line:
            inst_lines.append({'line': i, 'text': line})
    REPORT['findings']['instantiation_lines'] = inst_lines[:120]
    step('inspect_instantiation_done')

    # 6) provisional conclusion candidates
    REPORT['findings']['provisional'] = {
        'confirmed': [
            'All 190 rewrite reports lack llm_used=True',
            'Several datasets have non-null choice_field, so not all samples lack choice metadata',
        ],
        'open_questions': [
            'Whether parsed choices dict passed into RewriteAgent.rewrite is empty despite non-null choice_field',
            'Whether RewriteAgent client.config.enabled is false at runtime for this run',
            'Whether chat_json is called from rewrite path and returns empty',
        ]
    }
except Exception as e:
    REPORT['errors'].append({'stage':'top','error':repr(e), 'traceback': traceback.format_exc()})

out = Path('outputs/investigate_rewrite_llm_disabled/report.json')
out.write_text(json.dumps(REPORT, ensure_ascii=False, indent=2), encoding='utf-8')
summary = Path('outputs/investigate_rewrite_llm_disabled/report.txt')
lines = []
lines.append('Investigation report generated.')
for s in REPORT.get('steps', []):
    lines.append(f"STEP {s.get('step')}: {json.dumps({k:v for k,v in s.items() if k!='step'}, ensure_ascii=False)}")
for err in REPORT.get('errors', []):
    lines.append(f"ERROR {err.get('stage')}: {err.get('error')}")
summary.write_text('\n'.join(lines), encoding='utf-8')
print(str(out))
print(str(summary))
