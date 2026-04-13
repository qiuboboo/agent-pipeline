from __future__ import annotations

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pipeline2.annotation_modules import _normalize_claim_critique, _normalize_ptk_critique


class CritiqueNormalizationTests(unittest.TestCase):
    def test_ptk_critique_accepts_empty_revision_instructions_when_passed(self) -> None:
        normalized = _normalize_ptk_critique(
            {
                "pass": True,
                "critical_issues": [],
                "grounding_score": 0.95,
                "coverage_score": 0.9,
            }
        )
        self.assertEqual(normalized["revision_instructions"], "No changes needed.")

    def test_claim_critique_accepts_empty_revision_instructions_when_passed(self) -> None:
        normalized = _normalize_claim_critique(
            {
                "pass": True,
                "critical_issues": [],
                "atomicity_score": 0.95,
                "dependency_score": 0.94,
                "grounding_score": 0.93,
            }
        )
        self.assertEqual(normalized["revision_instructions"], "No changes needed.")


if __name__ == "__main__":
    unittest.main()
