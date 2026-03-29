from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, TypedDict

import os
import yaml
from PIL import Image

try:
    from .pipeline_utils import expand_env_placeholders, is_unresolved_env_placeholder
except ImportError:
    from pipeline_utils import expand_env_placeholders, is_unresolved_env_placeholder


@dataclass
class ModelConfig:
    base_url: str = "https://synai996.space/v1"
    api_key: str = os.environ.get("OPENAI_API_KEY", "")
    model: str = "gpt-5.4"
    reasoning_effort: str = "xhigh"
    temperature: float = 0.1
    timeout_seconds: int = 180
    retry_attempts: int = 3
    retry_backoff_seconds: float = 2.0
    enabled: bool = True
    agent_only_extraction: bool = False


@dataclass
class ThresholdConfig:
    min_width: int = 256
    min_height: int = 256
    min_sharpness_score: float = 0.22
    min_readability_score: float = 0.35
    min_contrast_score: float = 18.0
    reject_clean_score_below: float = 0.45
    review_clean_score_below: float = 0.62
    min_text_completeness_score: float = 0.60
    min_alignment_consistency: float = 0.55


@dataclass
class DatasetSpec:
    key: str
    display_name: str
    subject: str
    note: str
    source_kind: str
    source_locator: str
    split: Optional[str] = None
    hf_config_name: Optional[str] = None
    question_fields: List[str] = field(default_factory=list)
    answer_fields: List[str] = field(default_factory=list)
    image_fields: List[str] = field(default_factory=list)
    choice_fields: List[str] = field(default_factory=list)
    metadata_fields: List[str] = field(default_factory=list)
    force_requires_image: bool = False
    multi_solution_mode: str = "auto"
    answer_index_base: Optional[int] = None


@dataclass
class PipelineConfig:
    sample_per_dataset: int = 30
    sample_strategy: str = "head"
    shuffle_seed: int = 42
    output_root: str = "benchmarkallinone/outputs/multidataset_cleaning"
    cleaning_version: str = "v3.1.0"
    batch_id_prefix: str = "benchmarkallinone-clean"
    save_sample_bundle: bool = True
    git_cache_root: str = "benchmarkallinone/outputs/repo_cache"
    model: ModelConfig = field(default_factory=ModelConfig)
    thresholds: ThresholdConfig = field(default_factory=ThresholdConfig)
    datasets: List[DatasetSpec] = field(default_factory=list)

    @classmethod
    def default_dataset_specs(cls) -> List[DatasetSpec]:
        return [
            DatasetSpec(
                key="geosqa",
                display_name="GeoSQA",
                subject="地理",
                note="论文页公开，但当前未配置稳定程序化下载入口",
                source_kind="source_unavailable",
                source_locator="https://aclanthology.org/D19-1597/",
            ),
            DatasetSpec(
                key="scemqa",
                display_name="SCEMQA",
                subject="数学、物理、生物、化学",
                note="GitHub 公开仓库，尝试自动发现数据文件",
                source_kind="github",
                source_locator="https://github.com/SceMQA/SceMQA",
                question_fields=["question", "problem", "query", "text"],
                answer_fields=["answer", "solution", "label"],
                image_fields=["image", "image_path", "img_path", "diagram"],
                answer_index_base=0,
            ),
            DatasetSpec(
                key="geometry3k",
                display_name="Geometry3K",
                subject="数学",
                note="GitHub 公开仓库，尝试自动发现数据文件",
                source_kind="github",
                source_locator="https://github.com/lupantech/InterGPS",
                question_fields=["problem_text", "compact_text", "annotat_text", "problem", "question", "text"],
                answer_fields=["answer", "solution", "label"],
                image_fields=["img_diagram", "img_problem", "diagram", "image", "img_path", "image_path"],
                choice_fields=["choices", "compact_choices", "options"],
                force_requires_image=True,
            ),
            DatasetSpec(
                key="cmm_math",
                display_name="CMM-Math",
                subject="数学",
                note="Hugging Face 数据集",
                source_kind="huggingface",
                source_locator="ecnu-icalk/cmm-math",
                split="train",
                question_fields=["question"],
                answer_fields=["answer", "solution"],
                image_fields=["decoded_image", "image"],
                choice_fields=["options", "choices"],
            ),
            DatasetSpec(
                key="mathvision",
                display_name="MathVision",
                subject="数学",
                note="Hugging Face 数据集",
                source_kind="huggingface",
                source_locator="MathLLMs/MathVision",
                split="test",
                question_fields=["question"],
                answer_fields=["answer", "solution"],
                image_fields=["decoded_image", "image"],
                choice_fields=["options", "choices"],
            ),
            DatasetSpec(
                key="mm_math",
                display_name="MM-Math",
                subject="数学",
                note="Hugging Face 数据集",
                source_kind="huggingface",
                source_locator="THU-KEG/MM_Math",
                split="train",
            ),
            DatasetSpec(
                key="seephy",
                display_name="Seephy",
                subject="物理",
                note="当前仅论文入口，未配置稳定程序化下载源",
                source_kind="source_unavailable",
                source_locator="https://arxiv.org/abs/2509.06079",
            ),
            DatasetSpec(
                key="multi_physics",
                display_name="muti- physics",
                subject="物理",
                note="GitHub 公开仓库，尝试自动发现数据文件",
                source_kind="github",
                source_locator="https://github.com/luozhongze/Multi-Physics",
                question_fields=["question", "problem", "query", "text"],
                answer_fields=["answer", "solution", "label"],
                image_fields=["picture", "image", "image_path", "img_path", "figure"],
            ),
            DatasetSpec(
                key="physreason",
                display_name="PhysReason",
                subject="物理",
                note="GitHub 公开仓库，尝试自动发现数据文件",
                source_kind="github",
                source_locator="https://github.com/dxzxy12138/PhysReason",
                question_fields=["question", "problem", "query", "text"],
                answer_fields=["answer", "solution", "label"],
                image_fields=["image", "image_path", "img_path", "figure"],
            ),
            DatasetSpec(
                key="eee_bench",
                display_name="EEE-Bench",
                subject="电气电子工程领域",
                note="Hugging Face 数据集",
                source_kind="huggingface",
                source_locator="afdsafas/EEE-Bench",
                split="test",
                question_fields=["problem"],
                answer_fields=["solution"],
                image_fields=["image"],
            ),
            DatasetSpec(
                key="emma",
                display_name="EMMA",
                subject="数学、物理、代码、化学",
                note="当前仅论文入口，未配置稳定程序化下载源",
                source_kind="source_unavailable",
                source_locator="https://arxiv.org/abs/2501.05444",
            ),
        ]

    @classmethod
    def from_yaml(cls, path: Optional[str]) -> "PipelineConfig":
        if not path:
            return cls(datasets=cls.default_dataset_specs())
        with open(path, "r", encoding="utf-8") as file:
            raw = yaml.safe_load(file) or {}
        runtime = raw.get("runtime", {})
        model_raw = raw.get("model", {})
        threshold_raw = raw.get("thresholds", {})
        datasets_raw = raw.get("datasets", [])
        datasets = [DatasetSpec(**item) for item in datasets_raw] if datasets_raw else cls.default_dataset_specs()
        model_defaults = asdict(ModelConfig())
        model_data = {**model_defaults, **model_raw}
        model_data = {key: expand_env_placeholders(value) for key, value in model_data.items()}
        env_api_key = os.environ.get("OPENAI_API_KEY", "")
        if env_api_key:
            model_data["api_key"] = env_api_key
        if model_data.get("enabled", True):
            api_key_value = model_data.get("api_key", "")
            if not api_key_value or is_unresolved_env_placeholder(api_key_value):
                raise ValueError(
                    "Model is enabled but api_key is missing or unresolved. "
                    "Set OPENAI_API_KEY in the environment or provide a concrete model.api_key in YAML."
                )
        return cls(
            sample_per_dataset=runtime.get("sample_per_dataset", 30),
            sample_strategy=runtime.get("sample_strategy", "head"),
            shuffle_seed=runtime.get("shuffle_seed", 42),
            output_root=runtime.get("output_root", "outputs/multidataset_cleaning"),
            cleaning_version=runtime.get("cleaning_version", "v3.0.0"),
            batch_id_prefix=runtime.get("batch_id_prefix", "multidataset-clean"),
            save_sample_bundle=runtime.get("save_sample_bundle", True),
            git_cache_root=runtime.get("git_cache_root", "outputs/repo_cache"),
            model=ModelConfig(**model_data),
            thresholds=ThresholdConfig(**{**asdict(ThresholdConfig()), **threshold_raw}),
            datasets=datasets,
        )


@dataclass
class UnifiedSample:
    dataset_key: str
    dataset_display_name: str
    subject: str
    source_dataset: str
    source_split: str
    source_problem_id: str
    raw_question_text: str
    raw_answer_text: str
    images: List[Image.Image] = field(default_factory=list)
    image_sources: List[str] = field(default_factory=list)
    raw_record: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    choice_map: Dict[str, str] = field(default_factory=dict)
    force_requires_image: bool = False

    @property
    def image(self) -> Optional[Image.Image]:
        return self.images[0] if self.images else None

    @property
    def image_source(self) -> Optional[str]:
        return self.image_sources[0] if self.image_sources else None


RewriteStrategy = Literal["keep_open", "blank_open", "split_open", "drop_image_index"]


class RewriteVariant(TypedDict):
    variant_id: str
    title: str
    rewritten_question_text: str
    expected_answer_type: str
    expected_answer: str
    split_role: str


class RewriteReport(TypedDict, total=False):
    strategy: RewriteStrategy
    rationale: str
    variants: List[RewriteVariant]
    discard_reason_codes: List[str]
    llm_used: bool
    fallback_used: bool
    fallback_reason: Optional[str]
    schema_valid: bool
    normalization_warnings: List[str]


class GateResult(TypedDict):
    decision: str
    decision_reason_codes: List[str]
    clean_score: float
    score_breakdown: Dict[str, Any]
    suggested_next_action: str
    review_required: bool


class ExtractedRecord(TypedDict):
    raw_question_text: str
    raw_answer_text: str
    choice_map: Dict[str, str]
    image_paths: List[str]
    force_requires_image: bool
    extraction_notes: List[str]
    question_field: Optional[str]
    answer_field: Optional[str]
    image_field: Optional[str]
    choice_field: Optional[str]


class PreprocessedSample(TypedDict, total=False):
    problem_id: str
    candidate_id: str
    language: str
    raw_question_text: str
    raw_answer_text: str
    normalized_question_text: str
    normalized_answer_text: str
    original_answer_type: str
    choices: Dict[str, str]
    image_count: int
    image_paths: List[Any]
    image_bytes_list: List[bytes]
    image_qualities: List[Dict[str, Any]]
    requires_image: bool
    text_completeness: float
    question_norm: Dict[str, Any]
    answer_norm: Dict[str, Any]
    normalized_assets: Dict[str, Any]
    cleaning_path: str


class CleaningRecord(TypedDict, total=False):
    problem_id: str
    cleaning_version: str
    pipeline_run_id: str
    dataset_name: str
    decision: str
    decision_reason_codes: List[str]
    review_ticket_id: Optional[str]
    rewrite_summary: Dict[str, Any]


class RejectRecord(TypedDict, total=False):
    reject_id: str
    problem_id: str
    stage: str
    reject_reason_codes: List[str]
    reject_reason_detail: str
    created_at: str


class ProblemMainRecord(TypedDict, total=False):
    problem_id: str
    source_dataset: str
    source_problem_id: str
    normalized_question_text: str
    normalized_answer_text: str
    answer_type: str
    image_count: int
    requires_image: bool
    current_status: str
    clean_decision: str
    clean_decision_reason_codes: List[str]
    annotation_ready: bool
    qa_precheck_ready: bool
    rewrite_strategy: Optional[str]
    open_variant_count: int
    alignment_status: Optional[str]
    solvability_decision_hint: Optional[str]
    created_at: str

