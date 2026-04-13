from __future__ import annotations

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pipeline2.clients import ModelRouter, OpenAICompatibleClient
from pipeline2.config import ModelEndpointConfig


class ModelRouterAvailabilityTests(unittest.TestCase):
    def test_ensure_available_raises_when_no_endpoint_has_key(self) -> None:
        router = ModelRouter(
            primary=OpenAICompatibleClient(ModelEndpointConfig(name="primary", api_key="", enabled=True)),
            fallback=OpenAICompatibleClient(ModelEndpointConfig(name="fallback", api_key="", enabled=True)),
        )

        with self.assertRaises(RuntimeError) as context:
            router.ensure_available("pipeline2 annotate")

        self.assertIn("pipeline2 annotate", str(context.exception))
        self.assertIn("PIPELINE2_API_KEY_PRIMARY", str(context.exception))

    def test_has_available_endpoint_accepts_fallback_key(self) -> None:
        router = ModelRouter(
            primary=OpenAICompatibleClient(ModelEndpointConfig(name="primary", api_key="", enabled=True)),
            fallback=OpenAICompatibleClient(ModelEndpointConfig(name="fallback", api_key="dummy-key", enabled=True)),
        )

        self.assertTrue(router.has_available_endpoint())
        router.ensure_available("pipeline2 annotate")


if __name__ == "__main__":
    unittest.main()
