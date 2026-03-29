# Pipeline Module Contracts

## 1. 说明

本文档记录多数据集采集与清洗流水线的模块契约，重点明确：

- 模块职责
- 不负责什么
- 期望输入
- 期望输出
- 字段级输出结构
- 稳定性要求

本文档的字段约束以**当前主线代码**与**当前 LER rewrite 结果结构**为基准。

---

## 2. `pipeline_setup.py`

### 功能说明
负责 Setup 阶段，生成本次 run 的运行上下文。

### 不负责什么
- 不处理样本级业务逻辑
- 不做 rewrite
- 不做 clean gate
- 不做 records 汇总

### 期望输入
- CLI 参数
- YAML 配置
- 默认配置

### 期望输出

#### `SetupContext`

```python
{
  "config": object,
  "pipeline_run_id": str,
  "ingest_batch_id": str,
  "run_dir": str | Path,
  "records_dir": str | Path,
  "dataset_root": str | Path,
  "aggregate_summary": {
    "pipeline_run_id": str,
    "started_at": str,
    "dataset_summaries": list
  }
}
```

### 字段要求
- `pipeline_run_id`：必填，稳定字符串 ID
- `ingest_batch_id`：必填，批次 ID
- `run_dir`：必填，运行输出目录
- `aggregate_summary`：必填，run 级 summary 容器

---

## 3. `pipeline_collection.py`

### 功能说明
负责 Collection 阶段，将原始样本转成清洗前的结构化中间结果。

### 不负责什么
- 不做最终 clean decision
- 不做最终 records 序列化
- 不做 dataset/run summary 聚合

### 期望输入
- 原始样本
- connector 产物
- 配置
- 图片资源

### 期望输出

```python
{
  "sample": object,
  "problem_id": str,
  "language": str,
  "question_norm": {
    "normalized_text": str,
    "unit_normalization_map": list,
    "variable_aliases": list
  },
  "answer_norm": {
    "normalized_text": str,
    "unit_normalization_map": list,
    "variable_aliases": list
  },
  "normalized_question_text": str,
  "normalized_answer_text": str,
  "choices": dict,
  "answer_type": str,
  "requires_image": bool,
  "text_completeness": float,
  "image_paths": list,
  "image_bytes_list": list,
  "image_qualities": list,
  "quality_flags": list,
  "potential_scores": {
    "potential_score": float | int,
    "priority_score": float | int,
    "priority_tier": str
  }
}
```

### 关键字段要求
- `problem_id`：必填，样本唯一 ID
- `normalized_question_text`：必填
- `normalized_answer_text`：必填，可为空串但字段不能消失
- `choices`：必须始终为 dict，不能为 `None`
- `quality_flags`：必须始终为 list

---

## 4. `cleaning_semantics.py`

### 功能说明
负责文本结构、视觉结构、图文对齐、可解性分析。

### 不负责什么
- 不做 rewrite
- 不做最终 decision
- 不做 records 汇总

### 期望输入
- 规范化 question / answer
- 图像质量信息
- 图片对象
- 样本元数据

### 期望输出

```python
{
  "text_structure": {
    "question_type": str | None,
    "has_equation": bool | None,
    "has_blank": bool | None,
    "completeness": float | None,
    "structure_flags": list[str]
  },
  "visual_structure": {
    "image_count": int,
    "visual_type": str | None,
    "contains_chart": bool | None,
    "contains_table": bool | None,
    "visual_flags": list[str]
  },
  "alignment_record": {
    "alignment_status": str,
    "alignment_score": float | None,
    "cross_modal_refs": list,
    "risk_flags": list[str]
  },
  "solvability_report": {
    "solvability_score": float | None,
    "reasoning_path_exists": bool,
    "path_mode": str | None,
    "decision_hint": str,
    "failure_codes": list[str]
  }
}
```

### 关键字段要求
- `alignment_record.alignment_status`：必填，供 gate 直接消费
- `solvability_report.decision_hint`：必填，典型值 `pass/review/reject`
- `solvability_report.failure_codes`：必须为 list

---

## 5. `pipeline_cleaning.py`

### 功能说明
当前核心业务模块，负责 rewrite、clean gate、记录构建。

### 不负责什么
- 不负责 run 级 summary 聚合
- 不应长期承载所有共享 runtime 与客户端细节

---

### 5.1 `rewrite_report`

#### 期望输出

```python
{
  "strategy": str,
  "rationale": str,
  "variants": [
    {
      "variant_id": str,
      "title": str,
      "rewritten_question_text": str,
      "expected_answer_type": str,
      "expected_answer": str,
      "split_role": str
    }
  ],
  "discard_reason_codes": list[str],
  "llm_used": bool
}
```

#### 关键字段要求
- `strategy`：必填，稳定字段名，不得重命名
- `variants`：必填，必须始终为 list
- `discard_reason_codes`：必填，必须始终为 list
- `llm_used`：必填，必须保留

#### `strategy` 典型值
- `keep_open`
- `blank_open`
- `split_open`
- `drop_image_index`

---

### 5.2 `rewrite_report.variants[*]`

#### 期望输出

```python
{
  "variant_id": str,
  "title": str,
  "rewritten_question_text": str,
  "expected_answer_type": str,
  "expected_answer": str,
  "split_role": str
}
```

#### 关键字段要求
- `variant_id`：必填，如 `open_1`
- `rewritten_question_text`：必填
- `expected_answer_type`：必填
- `expected_answer`：必填，可为空串但字段不能消失
- `split_role`：必填

---

### 5.3 `open_ended_problem_variants`

#### 期望输出

```python
[
  {
    "open_variant_id": str,
    "parent_problem_id": str,
    "variant_index": int,
    "title": str,
    "rewritten_question_text": str,
    "expected_answer_type": str,
    "expected_answer": str,
    "split_role": str
  }
]
```

#### 关键字段要求
- `open_variant_id`：必填，稳定唯一 ID
- `parent_problem_id`：必填
- `variant_index`：必填，从 1 开始

---

### 5.4 `gate`

#### 期望输出

```python
{
  "decision": str,
  "decision_reason_codes": list[str],
  "risk_reason_codes": list[str],
  "suggested_next_action": str,
  "review_required": bool,
  "quality_score": float | None,
  "llm_override_used": bool
}
```

#### 当前强依赖字段
- `decision`
- `decision_reason_codes`
- `suggested_next_action`
- `review_required`

#### `decision` 典型值
- `pass`
- `review`
- `reject`

---

### 5.5 `rewrite_record`

#### 期望输出

```python
{
  "record_type": "rewrite_report",
  "problem_id": str,
  "strategy": str | None,
  "rationale": str | None,
  "llm_used": bool | None,
  "discard_reason_codes": list[str],
  "variant_count": int,
  "variants": [
    {
      "open_variant_id": str,
      "title": str,
      "rewritten_question_text": str,
      "expected_answer_type": str,
      "expected_answer": str,
      "split_role": str
    }
  ],
  "created_at": str
}
```

---

### 5.6 `cleaning_record`

#### 期望输出

```python
{
  "problem_id": str,
  "source_dataset": str,
  "quality_flags": list[str],
  "alignment_status": str | None,
  "solvability_score": float | None,
  "solvability_decision_hint": str | None,
  "rewrite_summary": {
    "strategy": str | None,
    "variant_count": int,
    "discard_reason_codes": list[str]
  },
  "decision": str,
  "decision_reason_codes": list[str],
  "review_ticket_id": str | None,
  "quality_checks": list,
  "actions": list,
  "created_at": str
}
```

---

### 5.7 `reject_record`

#### 期望输出

```python
{
  "problem_id": str,
  "reject_reason_codes": list[str],
  "reject_reason_detail": str,
  "quality_flags": list[str],
  "alignment_status": str | None,
  "solvability_decision_hint": str | None,
  "created_at": str
}
```

---

### 5.8 `problem_main_record`

#### 期望输出

```python
{
  "problem_id": str,
  "source_dataset": str,
  "source_problem_id": str,
  "normalized_question_text": str,
  "normalized_answer_text": str,
  "answer_type": str,
  "image_count": int,
  "requires_image": bool,
  "current_status": str,
  "clean_decision": str,
  "clean_decision_reason_codes": list[str],
  "annotation_ready": bool,
  "qa_precheck_ready": bool,
  "rewrite_strategy": str | None,
  "open_variant_count": int,
  "alignment_status": str | None,
  "solvability_decision_hint": str | None,
  "created_at": str
}
```

#### `current_status` 典型值
- `clean_passed`
- `cleaning_review`
- `clean_rejected`

---

### 5.9 `asset_record`

#### 期望输出

```python
{
  "asset_id": str,
  "problem_id": str,
  "asset_type": str,
  "asset_role": str,
  "source_uri": str | None,
  "storage_uri": str | None,
  "file_format": str | None,
  "file_size_bytes": int | None,
  "width": int | None,
  "height": int | None,
  "sha256": str | None,
  "perceptual_hash": str | None,
  "source_text_snapshot": str | None,
  "normalized_text_snapshot": str | None,
  "text_completeness_score": float | None,
  "blur_score": float | None,
  "readability_score": float | None,
  "noise_score": float | None,
  "cropped_from_asset_id": str | None,
  "roi_bbox": dict | None,
  "unit_normalization_map": list,
  "variable_aliases": list,
  "asset_quality_flags": list[str],
  "is_usable": bool,
  "discard_reason_codes": list[str],
  "created_at": str,
  "updated_at": str
}
```

---

## 6. `pipeline_reporting.py`

### 功能说明
负责 dataset/run 级汇总，不重新做业务决策。

### 期望输出

#### dataset bundle

```python
{
  "problem_main_records": list,
  "cleaning_records": list,
  "reject_records": list,
  "rewrite_reports": list,
  "open_ended_problem_variants": list,
  "asset_records": list,
  "field_audit_records": list,
  "text_structure_records": list,
  "visual_structure_records": list,
  "alignment_records": list,
  "solvability_reports": list,
  "clean_pool_entries": list
}
```

#### dataset summary

```python
{
  "dataset_key": str,
  "dataset_name": str,
  "processed_samples": int,
  "decision_counts": {
    "pass": int,
    "review": int,
    "reject": int
  },
  "rewrite_strategy_counts": dict[str, int],
  "records_written": dict[str, int],
  "status": str
}
```

#### run summary

```python
{
  "pipeline_run_id": str,
  "started_at": str,
  "finished_at": str,
  "dataset_summaries": list,
  "totals": {
    "processed_samples": int,
    "pass": int,
    "review": int,
    "reject": int
  }
}
```

---

## 7. `pipeline_types.py`

### 功能说明
定义稳定共享类型与结构契约。

### 期望输出
该模块本身不输出业务记录，但应定义至少如下结构：

```python
PipelineRunContext
SetupContext
NormalizedSample
ExtractionResult
RewriteReport
OpenVariant
QualityGateResult
DecisionOverrideResult
ProblemMainRecord
CleaningRecord
RejectRecord
AssetRecord
DatasetSummary
RunSummary
```

---

## 8. `pipeline_utils.py`

### 功能说明
提供纯工具函数。

### 期望输出
- 纯文本转换结果：`str`
- 清洗后的结构：`dict | list`
- hash / stable id：`str`
- 摘要字符串：`str`

### 约束
- 优先纯函数
- 不藏共享状态
- 不定义业务契约

---

## 9. `pipeline_prompts.py`

### 功能说明
统一管理 prompt 模板与 prompt 组装。

### 期望输出

```python
{
  "system_prompt": str,
  "user_prompt": str,
  "prompt_name": str,
  "prompt_version": str | None,
  "prompt_meta": dict
}
```

### rewrite prompt 示例

```python
{
  "system_prompt": str,
  "user_prompt": str,
  "prompt_name": "rewrite",
  "prompt_version": str | None,
  "prompt_meta": {
    "dataset_name": str,
    "answer_type": str,
    "has_choices": bool
  }
}
```

### decision prompt 示例

```python
{
  "system_prompt": str,
  "user_prompt": str,
  "prompt_name": "decision_override",
  "prompt_version": str | None,
  "prompt_meta": {
    "quality_flag_count": int,
    "rewrite_strategy": str | None
  }
}
```

---

## 10. `pipeline_logging.py`

### 功能说明
统一日志输出格式。

### 期望输出

```python
{
  "event": str,
  "stage": str,
  "problem_id": str | None,
  "dataset": str | None,
  "pipeline_run_id": str | None,
  "status": str,
  "message": str,
  "details": dict,
  "timestamp": str
}
```

### 典型事件
- `stage_start`
- `stage_end`
- `rewrite_result`
- `gate_decision`
- `sample_failed`

---

## 11. `pipeline_clients.py`

### 功能说明
统一封装模型/API 客户端调用。

### 期望输出

```python
{
  "ok": bool,
  "text": str | None,
  "json": dict | None,
  "raw": object | None,
  "usage": {
    "prompt_tokens": int | None,
    "completion_tokens": int | None,
    "total_tokens": int | None
  },
  "latency_ms": int | None,
  "finish_reason": str | None,
  "error": str | None
}
```

---

## 12. `pipeline_normalization.py`

### 功能说明
负责把上游原始输入转成标准化样本结构。

### 期望输出

```python
{
  "problem_id": str,
  "language": str,
  "normalized_question_text": str,
  "normalized_answer_text": str,
  "question_norm": {
    "normalized_text": str,
    "unit_normalization_map": list,
    "variable_aliases": list
  },
  "answer_norm": {
    "normalized_text": str,
    "unit_normalization_map": list,
    "variable_aliases": list
  },
  "choices": dict[str, str],
  "answer_type": str,
  "requires_image": bool,
  "normalization_warnings": list[str]
}
```

---

## 13. `pipeline_extraction.py`

### 功能说明
负责将标准化样本转成结构分析结果。

### 期望输出

```python
{
  "text_structure": {
    "question_type": str | None,
    "structure_flags": list[str],
    "text_completeness": float | None
  },
  "visual_structure": {
    "image_count": int,
    "visual_flags": list[str]
  },
  "alignment_record": {
    "alignment_status": str,
    "alignment_score": float | None,
    "risk_flags": list[str]
  },
  "solvability_report": {
    "solvability_score": float | None,
    "reasoning_path_exists": bool,
    "path_mode": str | None,
    "decision_hint": str,
    "failure_codes": list[str]
  },
  "quality_flags": list[str]
}
```

---

## 14. `pipeline_rewrite.py`

### 功能说明
负责正式 rewrite 路径输出，字段结构严格对齐当前主线 rewrite 契约。

### 期望输出

```python
{
  "strategy": str,
  "rationale": str,
  "variants": [
    {
      "variant_id": str,
      "title": str,
      "rewritten_question_text": str,
      "expected_answer_type": str,
      "expected_answer": str,
      "split_role": str
    }
  ],
  "discard_reason_codes": list[str],
  "llm_used": bool
}
```

### 硬约束
- `strategy` 不得改名
- `variants` 必须始终为 list
- `discard_reason_codes` 必须始终为 list
- `llm_used` 必须保留

---

## 15. `pipeline_rewrite_compat.py`

### 功能说明
仅作临时兼容桥接，不定义长期正式契约。

### 期望输出

```python
{
  "rewrite_report": {
    "strategy": str,
    "rationale": str,
    "variants": list,
    "discard_reason_codes": list[str],
    "llm_used": bool
  },
  "compat_meta": {
    "compat_used": bool,
    "legacy_input_version": str | None,
    "legacy_output_version": str | None,
    "adaptation_notes": list[str]
  }
}
```

---

## 16. `pipeline_quality.py`

### 功能说明
负责质量评估与约束检查。

### 期望输出

```python
{
  "quality_flags": list[str],
  "quality_components": {
    "text_completeness": float | None,
    "image_readability": float | None,
    "alignment_score": float | None,
    "solvability_score": float | None
  },
  "quality_score": float | None,
  "warnings": list[str],
  "hard_failures": list[str]
}
```

---

## 17. `pipeline_decision.py`

### 功能说明
负责 clean gate 与 decision override 结果统一输出。

### 期望输出

```python
{
  "decision": str,
  "decision_reason_codes": list[str],
  "suggested_next_action": str,
  "review_required": bool,
  "llm_override": {
    "used": bool,
    "decision": str | None,
    "reason_codes": list[str],
    "rationale": str | None
  }
}
```

---

## 18. `pipeline_records.py`

### 功能说明
负责组装最终 records bundle。

### 期望输出

```python
{
  "problem_main_record": dict,
  "cleaning_record": dict,
  "reject_record": dict | None,
  "rewrite_record": dict,
  "open_variants": list[dict],
  "asset_records": list[dict],
  "field_audit_records": list[dict],
  "text_structure_records": list[dict],
  "visual_structure_records": list[dict],
  "alignment_records": list[dict],
  "solvability_reports": list[dict],
  "clean_pool_entry": dict | None
}
```

---

## 19. `pipeline_connectors/base.py`

### 功能说明
定义 connector 的统一输出契约。

### 期望输出

```python
{
  "source_status": str,
  "samples": list,
  "detail": str | None
}
```

### `source_status` 典型值
- `available`
- `source_unavailable`
- `empty`

---

## 20. `pipeline_orchestrator.py`

### 功能说明
负责串联所有阶段并汇总单样本/单次运行结果。

### 期望输出

#### 单样本级

```python
{
  "problem_id": str,
  "status": "success" | "failed",
  "rewrite_report": dict,
  "gate": dict,
  "records_bundle": dict,
  "error": str | None
}
```

#### 运行级

```python
{
  "setup": dict,
  "collection": dict,
  "extraction": dict,
  "rewrite": dict,
  "quality": dict,
  "decision": dict,
  "records": dict,
  "report": dict | None,
  "status": str,
  "error": str | None
}
```

---

## 21. 最重要的硬约束总结

以下字段在重构中必须保持稳定：

### rewrite 侧
- `strategy`
- `rationale`
- `variants`
- `discard_reason_codes`
- `llm_used`

### variant 侧
- `variant_id`
- `title`
- `rewritten_question_text`
- `expected_answer_type`
- `expected_answer`
- `split_role`

### decision / gate 侧
- `decision`
- `decision_reason_codes`
- `suggested_next_action`
- `review_required`

### problem main 侧
- `clean_decision`
- `clean_decision_reason_codes`
- `rewrite_strategy`
- `annotation_ready`
- `qa_precheck_ready`

### reporting 侧
- `decision_counts`
- `rewrite_strategy_counts`
