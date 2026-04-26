from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, TypedDict


class BatchState(TypedDict, total=False):
    batch_id: str
    problems: List[Dict[str, Any]]
    failed_problems: List[Dict[str, Any]]


class ProblemStateBase(TypedDict):
    batch_id: str
    problem: Dict[str, Any]


class ProblemState(ProblemStateBase, total=False):
    problem_record: Dict[str, Any]
    p_facts: List[Dict[str, Any]]
    t_facts: List[Dict[str, Any]]
    k_atoms: List[Dict[str, Any]]
    ptk_audit: Dict[str, Any]
    cot_variants: List[Dict[str, Any]]
    claim_sequences: List[Dict[str, Any]]
    claim_extraction_failures: List[Dict[str, Any]]
    r_nodes: List[Dict[str, Any]]
    claim_mappings: List[Dict[str, Any]]
    solution_library: List[Dict[str, Any]]
    solution_memberships: List[Dict[str, Any]]
    evidence_bindings: List[Dict[str, Any]]
    coverage_state: Dict[str, Any]
    trace_mapping_index: Dict[str, Any]
    verification_audit: Dict[str, Any]
    problem_bundle: Dict[str, Any]
    problem_error: Dict[str, Any]


class MethodStateBase(TypedDict):
    batch_id: str
    problem: Dict[str, Any]
    method: Dict[str, Any]


class MethodState(MethodStateBase, total=False):
    current_cot_text: str
    current_cot_key: str
    current_answer: str


@dataclass
class LoadedReadyProblem:
    problem_id: str
    question_text: str
    standard_answer: str
    images: List[str] = field(default_factory=list)
    initial_multi_solution_score: float = 0.0
    dataset_name: str = ""
    source_problem_id: str = ""
    subject: str = ""
    requires_image: bool = False
    text_dominant: bool = False
    alignment_status: str = "unknown"
    solvability_score: float = 0.0
    clean_pool_status: str = ""
    clean_decision: str = ""
    sample_path: str = ""
    sample_record: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_runtime_problem(self) -> Dict[str, Any]:
        return {
            "problem_id": self.problem_id,
            "question_text": self.question_text,
            "standard_answer": self.standard_answer,
            "images": list(self.images),
            "initial_multi_solution_score": self.initial_multi_solution_score,
            "dataset_name": self.dataset_name,
            "source_problem_id": self.source_problem_id,
            "subject": self.subject,
            "requires_image": self.requires_image,
            "text_dominant": self.text_dominant,
            "alignment_status": self.alignment_status,
            "solvability_score": self.solvability_score,
            "clean_pool_status": self.clean_pool_status,
            "clean_decision": self.clean_decision,
            "sample_path": self.sample_path,
            "metadata": dict(self.metadata),
        }


@dataclass
class ClaimRecord:
    claim_id: str
    problem_id: str
    method_id: str
    claim_text: str
    claim_type: str
    depends_on: List[str] = field(default_factory=list)
    evidence_hint: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "claim_id": self.claim_id,
            "problem_id": self.problem_id,
            "method_id": self.method_id,
            "claim_text": self.claim_text,
            "claim_type": self.claim_type,
            "depends_on": list(self.depends_on),
            "evidence_hint": self.evidence_hint,
        }


@dataclass
class NodeRecord:
    r_id: str
    problem_id: str
    node_type: str
    canonical_claim: str
    surface_forms: List[str] = field(default_factory=list)
    equivalence_group_id: str = ""
    support_level: str = "MEDIUM"
    source_claim_ids: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "r_id": self.r_id,
            "problem_id": self.problem_id,
            "node_type": self.node_type,
            "canonical_claim": self.canonical_claim,
            "surface_forms": list(self.surface_forms),
            "equivalence_group_id": self.equivalence_group_id,
            "support_level": self.support_level,
            "source_claim_ids": list(self.source_claim_ids),
        }


@dataclass
class SolutionRecord:
    solution_id: str
    problem_id: str
    method_signature: str
    required_r_ids: List[str] = field(default_factory=list)
    optional_r_ids: List[str] = field(default_factory=list)
    ordered_core_path: List[str] = field(default_factory=list)
    supported_answer: str = ""
    member_method_ids: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "solution_id": self.solution_id,
            "problem_id": self.problem_id,
            "method_signature": self.method_signature,
            "required_r_ids": list(self.required_r_ids),
            "optional_r_ids": list(self.optional_r_ids),
            "ordered_core_path": list(self.ordered_core_path),
            "supported_answer": self.supported_answer,
            "member_method_ids": list(self.member_method_ids),
        }
