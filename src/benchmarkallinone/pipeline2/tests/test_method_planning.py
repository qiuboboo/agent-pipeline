from __future__ import annotations

import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pipeline2 import pipeline as annotation_pipeline
from pipeline2.agents import plan_method_collection, target_method_count_from_score


class MethodPlanningTests(unittest.TestCase):
    def test_target_method_count_from_score_uses_score_as_upper_bound_assumption(self) -> None:
        self.assertEqual(target_method_count_from_score(0.1, (0.33, 0.67)), 1)
        self.assertEqual(target_method_count_from_score(0.5, (0.33, 0.67)), 2)
        self.assertEqual(target_method_count_from_score(0.9, (0.33, 0.67)), 3)

    def test_plan_method_collection_keeps_only_unique_methods_when_high_score_cannot_reach_target(self) -> None:
        problem = {
            "problem_id": "prob_method_plan_001",
            "question_text": "题目文本",
            "standard_answer": "42",
        }
        side_effect = [
            {
                "methods": [
                    {
                        "method_id": "1",
                        "method_draft": "通过局部角追求解。",
                        "distinctiveness_rationale": "局部角追路线。",
                        "image_role": "读取局部角信息。",
                        "text_role": "定位目标角。",
                        "knowledge_role": "线性对。",
                    },
                    {
                        "method_id": "2",
                        "method_draft": "通过局部角追求解。",
                        "distinctiveness_rationale": "只是同一条路线的重复表述。",
                        "image_role": "读取局部角信息。",
                        "text_role": "定位目标角。",
                        "knowledge_role": "线性对。",
                    },
                    {
                        "method_id": "3",
                        "method_draft": "通过构造三角形角和求解。",
                        "distinctiveness_rationale": "三角形角和路线。",
                        "image_role": "读取三角形结构。",
                        "text_role": "识别目标角位置。",
                        "knowledge_role": "三角形内角和。",
                    },
                ]
            },
            {
                "methods": [
                    {
                        "method_id": "1",
                        "method_draft": "通过局部角追求解。",
                        "distinctiveness_rationale": "再次重复。",
                        "image_role": "读取局部角信息。",
                        "text_role": "定位目标角。",
                        "knowledge_role": "线性对。",
                    }
                ]
            },
            {
                "methods": []
            },
        ]

        with patch("pipeline2.agents._call_router", side_effect=side_effect):
            result = plan_method_collection(router=None, problem=problem, target_method_count=3, max_attempts=3)

        self.assertEqual(result["target_method_count_from_score"], 3)
        self.assertEqual(result["actual_method_count"], 2)
        self.assertFalse(result["met_target_method_count"])
        self.assertEqual(result["shortfall_reason"], "insufficient_distinct_routes_after_retry")
        self.assertEqual([item["method_id"] for item in result["methods"]], ["1", "2"])
        self.assertEqual(len(result["attempt_summaries"]), 3)

    def test_prepare_methods_node_uses_actual_unique_method_count(self) -> None:
        state = {
            "batch_id": "batch_test",
            "problem": {
                "problem_id": "prob_prepare_001",
                "question_text": "题目文本",
                "standard_answer": "42",
                "initial_multi_solution_score": 0.9,
            },
        }
        planning_bundle = {
            "target_method_count_from_score": 3,
            "actual_method_count": 2,
            "planning_attempt_count": 3,
            "met_target_method_count": False,
            "shortfall_reason": "insufficient_distinct_routes_after_retry",
            "attempt_summaries": [],
            "methods": [
                {
                    "method_id": "1",
                    "method_draft": "路线一",
                    "distinctiveness_rationale": "不同路线一",
                    "image_role": "图像角色一",
                    "text_role": "文本角色一",
                    "knowledge_role": "知识角色一",
                },
                {
                    "method_id": "2",
                    "method_draft": "路线二",
                    "distinctiveness_rationale": "不同路线二",
                    "image_role": "图像角色二",
                    "text_role": "文本角色二",
                    "knowledge_role": "知识角色二",
                },
            ],
        }
        ctx = SimpleNamespace(config=SimpleNamespace(thresholds=SimpleNamespace(method_score_thresholds=(0.33, 0.67))), router=None)

        with patch.object(annotation_pipeline, "get_context", return_value=ctx), patch.object(
            annotation_pipeline,
            "plan_method_collection",
            return_value=planning_bundle,
        ):
            result = annotation_pipeline._prepare_methods_node(state)

        self.assertEqual(len(result["problem"]["method"]), 2)
        self.assertEqual(result["problem"]["method_planning_metadata"]["target_method_count_from_score"], 3)
        self.assertEqual(result["problem"]["method_planning_metadata"]["actual_method_count"], 2)


if __name__ == "__main__":
    unittest.main()
