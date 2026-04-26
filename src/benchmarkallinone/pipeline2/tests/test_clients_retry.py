from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pipeline2.clients import OpenAICompatibleClient
from pipeline2.config import ModelEndpointConfig


class ClientRetryTests(unittest.TestCase):
    def _client(self) -> OpenAICompatibleClient:
        return OpenAICompatibleClient(
            ModelEndpointConfig(
                name="retry-test",
                base_url="https://example.com/v1",
                api_key="dummy",
                model="gpt-5.4",
                reasoning_effort="xhigh",
                temperature=0.1,
                timeout_seconds=1,
                enabled=True,
            )
        )

    def test_retry_delay_uses_endpoint_config(self) -> None:
        client = OpenAICompatibleClient(
            ModelEndpointConfig(
                name="retry-test",
                base_url="https://example.com/v1",
                api_key="dummy",
                retry_base_delay_seconds=5,
                retry_max_delay_seconds=60,
            )
        )

        self.assertEqual(client._retry_delay_seconds(1), 5)
        self.assertEqual(client._retry_delay_seconds(2), 10)
        self.assertEqual(client._retry_delay_seconds(5), 60)

    def test_missing_json_retries_until_success(self) -> None:
        client = self._client()
        responses = [
            {
                "choices": [{"message": {"content": ""}}],
                "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
            },
            {
                "choices": [{"message": {"content": '{"ok": true}'}}],
                "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
            },
        ]

        class DummyResponse:
            def __init__(self, body):
                self.body = body
                self.status = 200
                self.headers = {"Content-Type": "application/json"}
            def getcode(self):
                return self.status
            def read(self):
                import json
                return json.dumps(self.body).encode("utf-8")
            def __enter__(self):
                return self
            def __exit__(self, exc_type, exc, tb):
                return False

        def fake_urlopen(req, timeout):
            return DummyResponse(responses.pop(0))

        with patch("urllib.request.urlopen", side_effect=fake_urlopen), patch("time.sleep", return_value=None):
            result = client.chat_json("sys", "user")

        self.assertIsNotNone(result)
        self.assertTrue(result["ok"])
        usage = client.snapshot_usage()
        self.assertEqual(usage["successful_request_count"], 1)
        self.assertEqual(usage["retry_count"], 1)


if __name__ == "__main__":
    unittest.main()
