from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pipeline2 import annotation_modules
from pipeline2.agents import PipelineDataContractError, group_solutions


class AnnotationModulesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.problem = {
            "problem_id": "prob_test_001",
            "question_text": "观察图像并求目标角。",
            "standard_answer": "65",
            "images": ["/tmp/fake_image.png"],
            "dataset_name": "UnitTest",
            "source_problem_id": "src_1",
            "subject": "数学",
            "requires_image": True,
            "text_dominant": False,
            "alignment_status": "good",
            "solvability_score": 1.0,
            "sample_path": "/tmp/prob_test_001.json",
            "sample_record": {
                "visual_structure_records": [{"visual_entities": [], "visual_relations": []}],
                "text_structure_records": [{"text_segments": [], "targets": [], "entities": []}],
            },
        }
        self.method = {
            "method_id": "1",
            "method_draft": "先识别图中角关系，再按线性对求解。",
        }

    def test_build_ptk_foundation_repair_loop(self) -> None:
        side_effect = [
            {
                "p_facts": [
                    {
                        "p_id": "p1",
                        "fact_text": "图中存在一个角。",
                        "confidence": 0.8,
                        "visual_anchor": "center",
                    }
                ]
            },
            {
                "t_facts": [
                    {
                        "t_id": "t1",
                        "fact_text": "求目标角大小。",
                        "fact_role": "goal",
                    }
                ]
            },
            {
                "k_atoms": [
                    {
                        "k_id": "k1",
                        "knowledge_text": "线性对互补。",
                        "knowledge_type": "principle",
                        "applicability_note": "相邻角共线时可用。",
                    }
                ]
            },
            {
                "pass": False,
                "critical_issues": ["p_facts 缺少足够 grounding。"],
                "revision_instructions": "补充更具体的视觉锚点。",
                "grounding_score": 0.2,
                "coverage_score": 0.6,
            },
            {
                "p_facts": [
                    {
                        "p_id": "p1",
                        "fact_text": "图中在点 X 处标有一个 115° 的角。",
                        "confidence": 0.95,
                        "visual_anchor": "vertex X / angle label 115°",
                    }
                ],
                "t_facts": [
                    {
                        "t_id": "t1",
                        "fact_text": "求角 VXW 的大小。",
                        "fact_role": "goal",
                    }
                ],
                "k_atoms": [
                    {
                        "k_id": "k1",
                        "knowledge_text": "线性对互补。",
                        "knowledge_type": "principle",
                        "applicability_note": "相邻角共线时可用。",
                    }
                ],
                "revision_summary": "补入明确视觉锚点并保留必要文本与知识。",
            },
            {
                "pass": True,
                "critical_issues": [],
                "revision_instructions": "无",
                "grounding_score": 0.95,
                "coverage_score": 0.9,
            },
        ]

        with patch.object(annotation_modules, "_call_router", side_effect=side_effect):
            result = annotation_modules.build_ptk_foundation(router=None, problem=self.problem, max_repair_rounds=1)

        self.assertEqual(result["p_facts"][0]["visual_anchor"], "vertex X / angle label 115°")
        self.assertTrue(result["audit"]["passed"])
        self.assertEqual(len(result["audit"]["rounds"]), 2)
        self.assertEqual(result["audit"]["rounds"][0]["polish_summary"], "补入明确视觉锚点并保留必要文本与知识。")

    def test_extract_claims_bundle_repair_loop(self) -> None:
        p_facts = [
            {
                "p_id": "p1",
                "fact_text": "图中在点 X 处标有一个 115° 的角。",
                "confidence": 0.95,
                "visual_anchor": "vertex X / angle label 115°",
            }
        ]
        t_facts = [{"t_id": "t1", "fact_text": "求角 VXW 的大小。", "fact_role": "goal"}]
        k_atoms = [{"k_id": "k1", "knowledge_text": "线性对互补。", "knowledge_type": "principle", "applicability_note": "相邻角共线时可用。"}]

        side_effect = [
            {
                "claims": [
                    {
                        "claim_id": "c1",
                        "claim_text": "图中有一个 115° 的角。",
                        "claim_type": "perception",
                        "depends_on": [],
                        "evidence_hint": "读取角标。",
                    },
                    {
                        "claim_id": "c2",
                        "claim_text": "答案是 65°。",
                        "claim_type": "final_answer",
                        "depends_on": [],
                        "evidence_hint": "直接给出答案。",
                    },
                ]
            },
            {
                "pass": False,
                "critical_issues": ["缺少桥梁 claim，final answer 没有依赖。"],
                "revision_instructions": "加入线性对与计算步骤，并修正 depends_on。",
                "atomicity_score": 0.4,
                "dependency_score": 0.1,
                "grounding_score": 0.8,
            },
            {
                "claims": [
                    {
                        "claim_id": "c1",
                        "claim_text": "图中在点 X 处标有一个 115° 的角。",
                        "claim_type": "perception",
                        "depends_on": [],
                        "evidence_hint": "读取角标。",
                    },
                    {
                        "claim_id": "c2",
                        "claim_text": "115° 与目标角构成线性对。",
                        "claim_type": "derivation",
                        "depends_on": ["c1"],
                        "evidence_hint": "由图中共线关系确定。",
                    },
                    {
                        "claim_id": "c3",
                        "claim_text": "线性对角和为 180°。",
                        "claim_type": "knowledge_call",
                        "depends_on": ["c2"],
                        "evidence_hint": "调用线性对规则。",
                    },
                    {
                        "claim_id": "c4",
                        "claim_text": "目标角 = 180° - 115° = 65°。",
                        "claim_type": "calculation",
                        "depends_on": ["c2", "c3"],
                        "evidence_hint": "进行补角计算。",
                    },
                    {
                        "claim_id": "c5",
                        "claim_text": "角 VXW 的大小是 65°。",
                        "claim_type": "final_answer",
                        "depends_on": ["c4"],
                        "evidence_hint": "输出最终答案。",
                    },
                ],
                "revision_summary": "补足桥梁与计算 claim，并显式依赖。",
            },
            {
                "pass": True,
                "critical_issues": [],
                "revision_instructions": "无",
                "atomicity_score": 0.95,
                "dependency_score": 0.95,
                "grounding_score": 0.9,
            },
        ]

        with patch.object(annotation_modules, "_call_router", side_effect=side_effect):
            result = annotation_modules.extract_claims_bundle(
                router=None,
                problem=self.problem,
                method=self.method,
                cot_text="先看到 115°，再用线性对得到 65°。",
                p_facts=p_facts,
                t_facts=t_facts,
                k_atoms=k_atoms,
                max_repair_rounds=1,
            )

        self.assertTrue(result["audit"]["passed"])
        self.assertEqual(result["claims"][-1]["claim_type"], "final_answer")
        self.assertEqual(result["claims"][-1]["depends_on"], ["c4"])
        self.assertEqual(result["audit"]["rounds"][0]["polish_summary"], "补足桥梁与计算 claim，并显式依赖。")

    def test_extract_claims_bundle_raises_on_unfixable_claims(self) -> None:
        p_facts = [
            {
                "p_id": "p1",
                "fact_text": "图中在点 X 处标有一个 115° 的角。",
                "confidence": 0.95,
                "visual_anchor": "vertex X / angle label 115°",
            }
        ]
        t_facts = [{"t_id": "t1", "fact_text": "求角 VXW 的大小。", "fact_role": "goal"}]
        k_atoms = [{"k_id": "k1", "knowledge_text": "线性对互补。", "knowledge_type": "principle", "applicability_note": "相邻角共线时可用。"}]

        side_effect = [
            {
                "claims": [
                    {
                        "claim_id": "c1",
                        "claim_text": "图中在点 X 处标有一个 115° 的角。",
                        "claim_type": "perception",
                        "depends_on": [],
                        "evidence_hint": "读取角标。",
                    }
                ]
            },
            {
                "pass": False,
                "critical_issues": ["缺少最终答案 claim。"],
                "revision_instructions": "补出最终答案 claim。",
                "atomicity_score": 0.5,
                "dependency_score": 0.5,
                "grounding_score": 0.9,
            },
        ]

        with patch.object(annotation_modules, "_call_router", side_effect=side_effect):
            with self.assertRaises(PipelineDataContractError):
                annotation_modules.extract_claims_bundle(
                    router=None,
                    problem=self.problem,
                    method=self.method,
                    cot_text="只有观察，没有结论。",
                    p_facts=p_facts,
                    t_facts=t_facts,
                    k_atoms=k_atoms,
                    max_repair_rounds=0,
                )


class GroupSolutionsTests(unittest.TestCase):
    def test_group_solutions_uses_planned_method_count_for_coverage(self) -> None:
        problem = {
            "problem_id": "prob_test_002",
            "question_text": "求值。",
            "standard_answer": "42",
        }
        methods = [{"method_id": "1"}]
        r_nodes = [{"r_id": "r1"}]

        with patch("pipeline2.agents._call_router", return_value={
            "solutions": [
                {
                    "solution_id": "s1",
                    "method_signature": "单一路径",
                    "required_r_ids": ["r1"],
                    "optional_r_ids": [],
                    "ordered_core_path": ["r1"],
                    "supported_answer": "42",
                    "member_method_ids": ["1"],
                }
            ]
        }):
            _, _, coverage_state = group_solutions(
                router=None,
                problem=problem,
                methods=methods,
                r_nodes=r_nodes,
                claim_sequences=[],
                claim_mappings=[],
                k_atoms=[],
                planned_method_count=3,
            )

        self.assertEqual(coverage_state["method_count"], 3)
        self.assertEqual(coverage_state["qualified_method_count"], 1)


if __name__ == "__main__":
    unittest.main()
