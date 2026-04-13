from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from types import SimpleNamespace

from pipeline2 import pipeline as annotation_pipeline
from pipeline2.agents import _call_router, judge_answer_equivalence, plan_methods, polish_cot, repair_answer, solve_method, verify_cot


class _FakeRouter:
    def __init__(self, response: dict):
        self.response = response

    def chat_json_with_images(self, system_prompt, user_prompt, images):
        return dict(self.response)

    def chat_json(self, system_prompt, user_prompt):
        return dict(self.response)

    def last_error_summary(self):
        return {"primary_last_error": None, "fallback_last_error": None}


class MultimodalCoTRequirementTests(unittest.TestCase):
    def setUp(self) -> None:
        self.image_paths = ["/tmp/fake_image.png"]
        self.problem = {
            "problem_id": "prob_mm_cot_001",
            "question_text": "Read the digit shown in the image and answer with that digit only.",
            "standard_answer": "7",
            "images": list(self.image_paths),
            "requires_image": True,
            "sample_record": {
                "visual_structure_records": [{"visual_entities": [], "visual_relations": []}],
                "text_structure_records": [{"text_segments": [], "targets": [], "entities": []}],
            },
        }
        self.method = {
            "method_id": "1",
            "method_draft": "先观察图中的数字形状，再输出识别结果。",
        }

    def test_solve_method_requires_images_for_image_grounded_problem(self) -> None:
        with patch(
            "pipeline2.agents._call_router",
            return_value={
                "cot_raw": "先观察图中的数字形状，再输出 7。",
                "model_answer": "7",
            },
        ) as mocked:
            result = solve_method(router=None, problem=self.problem, method=self.method)

        self.assertEqual(result["answer"], "7")
        self.assertEqual(mocked.call_args.args[3], self.image_paths)
        self.assertTrue(mocked.call_args.kwargs["require_images"])
        self.assertEqual(mocked.call_args.kwargs["agent_name"], "Solver")

    def test_answer_repair_requires_images_for_image_grounded_problem(self) -> None:
        with patch(
            "pipeline2.agents._call_router",
            return_value={
                "repaired_cot": "根据图中数字形状，修正后的答案仍为 7。",
                "repaired_answer": "7",
                "repair_notes": "已依据图片校正。",
            },
        ) as mocked:
            result = repair_answer(
                router=None,
                problem=self.problem,
                method=self.method,
                cot_text="先看图得到 1。",
                predicted_answer="1",
            )

        self.assertEqual(result["answer"], "7")
        self.assertEqual(mocked.call_args.args[3], self.image_paths)
        self.assertTrue(mocked.call_args.kwargs["require_images"])
        self.assertEqual(mocked.call_args.kwargs["agent_name"], "AnswerRepair")

    def test_verify_cot_requires_images_for_image_grounded_problem(self) -> None:
        with patch(
            "pipeline2.agents._call_router",
            return_value={
                "verify_pass": True,
                "critic_suggestions": "No changes needed.",
                "major_failures": [],
                "extractability_score": 1.0,
                "grounding_score": 1.0,
                "method_fidelity_score": 1.0,
            },
        ) as mocked:
            result = verify_cot(
                router=None,
                problem=self.problem,
                method=self.method,
                cot_text="先观察图像中的数字形状，再确定答案是 7。",
            )

        self.assertTrue(result["verify_pass"])
        self.assertEqual(mocked.call_args.args[3], self.image_paths)
        self.assertTrue(mocked.call_args.kwargs["require_images"])
        self.assertEqual(mocked.call_args.kwargs["agent_name"], "CoTVerify")

    def test_polish_cot_requires_images_for_image_grounded_problem(self) -> None:
        with patch(
            "pipeline2.agents._call_router",
            return_value={
                "polished_cot": "我直接观察图片中的数字形状，它是 7。",
                "polish_summary": "已补强图片 grounding。",
                "preserved_method_identity": True,
            },
        ) as mocked:
            result = polish_cot(
                router=None,
                problem=self.problem,
                method=self.method,
                cot_text="答案是 7。",
                suggestion="补充直接的图片依据。",
            )

        self.assertEqual(result["polished_cot"], "我直接观察图片中的数字形状，它是 7。")
        self.assertEqual(mocked.call_args.args[3], self.image_paths)
        self.assertTrue(mocked.call_args.kwargs["require_images"])
        self.assertEqual(mocked.call_args.kwargs["agent_name"], "CoTPolish")

    def test_call_router_rejects_text_mode_for_required_image_request(self) -> None:
        router = _FakeRouter({"ok": True, "_llm_request_mode": "text"})
        with patch("pipeline2.agents._load_images", return_value=[object()]):
            with self.assertRaisesRegex(Exception, "must be multimodal"):
                _call_router(
                    router=router,
                    system_prompt="system",
                    user_prompt="user",
                    image_paths=self.image_paths,
                    agent_name="Solver",
                    require_images=True,
                )

    def test_plan_methods_requires_images_for_image_grounded_problem(self) -> None:
        with patch(
            "pipeline2.agents._call_router",
            return_value={
                "methods": [
                    {
                        "method_id": "1",
                        "method_draft": "先直接看图识别数字，再输出该数字。",
                        "distinctiveness_rationale": "直接视觉识别路线。",
                        "image_role": "读取图中唯一数字的形状。",
                        "text_role": "遵循只输出数字的指令。",
                        "knowledge_role": "基础数字形状识别。",
                    }
                ]
            },
        ) as mocked:
            result = plan_methods(router=None, problem=self.problem, method_count=1)

        self.assertEqual(result[0]["method_id"], "1")
        self.assertEqual(mocked.call_args.args[3], self.image_paths)
        self.assertTrue(mocked.call_args.kwargs["require_images"])
        self.assertEqual(mocked.call_args.kwargs["agent_name"], "MethodPlanner")

    def test_answer_equivalence_requires_images_for_image_grounded_problem(self) -> None:
        with patch(
            "pipeline2.agents._call_router",
            return_value={
                "is_equivalent": True,
                "reason": "image-grounded match",
                "part_results": [],
            },
        ) as mocked:
            result = judge_answer_equivalence(
                router=None,
                problem=self.problem,
                predicted_answer="1",
                cot_text="我看到图里数字像 7。",
            )

        self.assertTrue(result["is_equivalent"])
        self.assertEqual(mocked.call_args.args[3], self.image_paths)
        self.assertTrue(mocked.call_args.kwargs["require_images"])
        self.assertEqual(mocked.call_args.kwargs["agent_name"], "AnswerEquivalenceJudge")

    def test_verify_round_records_multimodal_meta(self) -> None:
        state = {
            "batch_id": "batch_test",
            "problem": self.problem,
            "method": {
                "method_id": "1",
                "is_answer_match": True,
                "verify_reports": [],
            },
            "current_cot_text": "我直接观察图片中的数字形状，它是 7。",
        }
        verify_result = {
            "verify_pass": True,
            "critic_suggestions": "The trace is faithful to the image and no substantive revision is needed.",
            "major_failures": [],
            "extractability_score": 1.0,
            "grounding_score": 1.0,
            "method_fidelity_score": 1.0,
            "meta": {
                "_llm_request_mode": "multimodal",
                "_llm_endpoint_name": "primary",
                "_llm_elapsed_seconds": 1.23,
            },
        }

        with patch.object(annotation_pipeline, "get_context", return_value=SimpleNamespace(router=None)), patch.object(
            annotation_pipeline,
            "verify_cot",
            return_value=verify_result,
        ):
            result = annotation_pipeline._verify_round(state, 0)

        report = result["method"]["verify_reports"][0]
        self.assertEqual(report["llm_request_mode"], "multimodal")
        self.assertEqual(report["llm_endpoint_name"], "primary")
        self.assertEqual(report["llm_elapsed_seconds"], 1.23)


if __name__ == "__main__":
    unittest.main()
