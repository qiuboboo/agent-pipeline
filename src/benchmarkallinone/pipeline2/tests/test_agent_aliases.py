from __future__ import annotations

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pipeline2.agents import _normalize_node_type


class AgentAliasTests(unittest.TestCase):
    def test_identification_alias_maps_to_perception(self) -> None:
        self.assertEqual(_normalize_node_type("identification", "NodeInduction"), "perception")

    def test_recognition_alias_maps_to_perception(self) -> None:
        self.assertEqual(_normalize_node_type("recognition", "NodeInduction"), "perception")


if __name__ == "__main__":
    unittest.main()
