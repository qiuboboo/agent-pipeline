from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pipeline2.clients import OpenAICompatibleClient, ModelRouter
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
                wire_api="chat_completions",
                temperature=0.1,
                timeout_seconds=1,
                enabled=True,
            )
        )

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
                self._consumed = False

            def read(self, size: int = -1):
                del size
                if self._consumed:
                    return b""
                self._consumed = True
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

    def test_post_json_honors_deadline(self) -> None:
        client = self._client()

        with patch("urllib.request.urlopen", side_effect=TimeoutError("deadline-test")), patch("time.sleep", return_value=None), patch(
            "time.monotonic",
            side_effect=[0.0, 0.2, 0.4, 179.7, 180.1],
        ):
            result = client._post_json({"model": "gpt-5.4"}, deadline_monotonic=180.0, max_attempts=10)

        self.assertIsNone(result)
        self.assertIn("deadline", client.snapshot_usage().get("last_error") or "")

    def test_body_read_timeout_retries_until_success(self) -> None:
        client = self._client()

        class DummyResponse:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

        success_body = {
            "choices": [{"message": {"content": '{"ok": true}'}}],
            "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
        }

        with patch("urllib.request.urlopen", side_effect=[DummyResponse(), DummyResponse()]), patch.object(
            client,
            "_read_response_bytes",
            side_effect=[TimeoutError("body-timeout"), json.dumps(success_body).encode("utf-8")],
        ), patch("time.sleep", return_value=None):
            result = client.chat_json("sys", "user")

        self.assertIsNotNone(result)
        self.assertTrue(result["ok"])
        usage = client.snapshot_usage()
        self.assertEqual(usage["successful_request_count"], 1)
        self.assertEqual(usage["retry_count"], 1)

    def test_responses_api_uses_responses_endpoint_and_output_text(self) -> None:
        client = OpenAICompatibleClient(
            ModelEndpointConfig(
                name="responses-test",
                base_url="https://example.com",
                api_key="dummy",
                model="gpt-5.4",
                reasoning_effort="high",
                wire_api="responses",
                disable_response_storage=True,
                timeout_seconds=1,
                enabled=True,
            )
        )

        captured = {}

        class DummyResponse:
            def __init__(self, body):
                self.body = body
                self._consumed = False

            def read(self, size: int = -1):
                del size
                if self._consumed:
                    return b""
                self._consumed = True
                return json.dumps(self.body).encode("utf-8")

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

        def fake_urlopen(req, timeout):
            del timeout
            captured["url"] = req.full_url
            captured["payload"] = json.loads(req.data.decode("utf-8"))
            return DummyResponse(
                {
                    "output_text": '{"ok": true}',
                    "usage": {"input_tokens": 1, "output_tokens": 1, "total_tokens": 2},
                }
            )

        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            result = client.chat_json("sys", "user")

        self.assertEqual(captured["url"], "https://example.com/responses")
        self.assertFalse(captured["payload"]["store"])
        self.assertEqual(captured["payload"]["text"]["format"]["type"], "json_object")
        self.assertEqual(captured["payload"]["reasoning"]["effort"], "high")
        self.assertIsNotNone(result)
        self.assertTrue(result["ok"])

    def test_responses_api_uses_json_schema_when_provided(self) -> None:
        client = OpenAICompatibleClient(
            ModelEndpointConfig(
                name="responses-schema-test",
                base_url="https://example.com",
                api_key="dummy",
                model="gpt-5.4",
                reasoning_effort="high",
                wire_api="responses",
                disable_response_storage=True,
                timeout_seconds=1,
                enabled=True,
            )
        )

        captured = {}

        class DummyResponse:
            def __init__(self, body):
                self.body = body
                self._consumed = False

            def read(self, size: int = -1):
                del size
                if self._consumed:
                    return b""
                self._consumed = True
                return json.dumps(self.body).encode("utf-8")

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

        def fake_urlopen(req, timeout):
            del timeout
            captured["payload"] = json.loads(req.data.decode("utf-8"))
            return DummyResponse(
                {
                    "output_text": '{"ok": true}',
                    "usage": {"input_tokens": 1, "output_tokens": 1, "total_tokens": 2},
                }
            )

        schema = {
            "name": "unit_test_schema",
            "strict": True,
            "schema": {
                "type": "object",
                "additionalProperties": False,
                "properties": {"ok": {"type": "boolean"}},
                "required": ["ok"],
            },
        }

        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            result = client.chat_json("sys", "user", response_schema=schema)

        self.assertEqual(captured["payload"]["text"]["format"]["type"], "json_schema")
        self.assertEqual(captured["payload"]["text"]["format"]["name"], "unit_test_schema")
        self.assertTrue(captured["payload"]["text"]["format"]["strict"])
        self.assertEqual(captured["payload"]["text"]["format"]["schema"]["required"], ["ok"])
        self.assertIsNotNone(result)
        self.assertTrue(result["ok"])

    def test_msutools_responses_api_uses_sse_mode(self) -> None:
        client = OpenAICompatibleClient(
            ModelEndpointConfig(
                name="msutools-sse-test",
                base_url="https://www.msutools.cn",
                api_key="dummy",
                model="gpt-5.4",
                reasoning_effort="high",
                wire_api="responses",
                disable_response_storage=True,
                timeout_seconds=1,
                enabled=True,
            )
        )

        captured = {}
        sse_lines = [
            b'event: response.output_text.delta\n',
            b'data: {"text":"{\\"ok\\": "}\n',
            b'\n',
            b'event: response.output_text.delta\n',
            b'data: {"text":"true}"}\n',
            b'\n',
            b'event: response.completed\n',
            b'data: {"usage":{"input_tokens":1,"output_tokens":1,"total_tokens":2}}\n',
            b'\n',
        ]

        class DummyHeaders:
            def get_content_type(self):
                return "text/event-stream"

            def get(self, key, default=""):
                if key.lower() == "content-type":
                    return "text/event-stream"
                return default

        class DummyResponse:
            def __init__(self, lines):
                self._lines = list(lines)
                self.headers = DummyHeaders()

            def readline(self, size: int = -1):
                del size
                if self._lines:
                    return self._lines.pop(0)
                return b""

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

        def fake_urlopen(req, timeout):
            del timeout
            captured["payload"] = json.loads(req.data.decode("utf-8"))
            captured["accept"] = req.headers.get("Accept")
            return DummyResponse(sse_lines)

        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            result = client.chat_json("sys", "user")

        self.assertTrue(captured["payload"]["stream"])
        self.assertEqual(captured["accept"], "text/event-stream")
        self.assertIsNotNone(result)
        self.assertTrue(result["ok"])

    def test_event_stream_content_type_uses_sse_parser_without_known_host(self) -> None:
        client = OpenAICompatibleClient(
            ModelEndpointConfig(
                name="generic-sse-test",
                base_url="https://example.com",
                api_key="dummy",
                model="gpt-5.4",
                reasoning_effort="high",
                wire_api="responses",
                disable_response_storage=True,
                timeout_seconds=1,
                enabled=True,
            )
        )

        captured = {}
        sse_lines = [
            b'event: response.output_text.delta\n',
            b'data: {"text":"{\\"ok\\":true}"}\n',
            b'\n',
            b'event: response.completed\n',
            b'data: {"usage":{"input_tokens":1,"output_tokens":1,"total_tokens":2}}\n',
            b'\n',
        ]

        class DummyHeaders:
            def get_content_type(self):
                return "text/event-stream"

            def get(self, key, default=""):
                if key.lower() == "content-type":
                    return "text/event-stream"
                return default

        class DummyResponse:
            def __init__(self, lines):
                self._lines = list(lines)
                self.headers = DummyHeaders()

            def readline(self, size: int = -1):
                del size
                if self._lines:
                    return self._lines.pop(0)
                return b""

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

        def fake_urlopen(req, timeout):
            del timeout
            captured["payload"] = json.loads(req.data.decode("utf-8"))
            captured["accept"] = req.headers.get("Accept")
            return DummyResponse(sse_lines)

        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            result = client.chat_json("sys", "user")

        self.assertNotIn("stream", captured["payload"])
        self.assertEqual(captured["accept"], "application/json")
        self.assertIsNotNone(result)
        self.assertTrue(result["ok"])


class _StubClient:
    def __init__(self, responses, *, timeout_seconds: int = 1):
        self.responses = list(responses)
        self.calls = 0
        self.config = ModelEndpointConfig(name="stub", api_key="dummy", enabled=True, timeout_seconds=timeout_seconds)
        self._usage_lock = __import__("threading").Lock()
        self.usage_totals = {"last_error": None, "failed_request_count": 0}

    def chat_json(self, system_prompt, user_prompt, response_schema=None, *, deadline_monotonic=None, max_attempts=3):
        del system_prompt, user_prompt, response_schema, deadline_monotonic, max_attempts
        self.calls += 1
        if self.responses:
            response = self.responses.pop(0)
            if isinstance(response, BaseException):
                raise response
            return response
        return None

    def chat_json_with_images(self, system_prompt, user_prompt, images, response_schema=None, *, deadline_monotonic=None, max_attempts=3):
        del system_prompt, user_prompt, images, response_schema, deadline_monotonic, max_attempts
        self.calls += 1
        if self.responses:
            response = self.responses.pop(0)
            if isinstance(response, BaseException):
                raise response
            return response
        return None

    def snapshot_usage(self):
        return dict(self.usage_totals)


class ModelRouterRetryWindowTests(unittest.TestCase):
    def test_router_invokes_primary_once(self) -> None:
        primary = _StubClient([{"ok": True}])
        router = ModelRouter(primary=primary, fallback=None)

        result = router.chat_json("sys", "user")

        self.assertEqual(result, {"ok": True})
        self.assertEqual(primary.calls, 1)

    def test_router_does_not_retry_or_use_fallback(self) -> None:
        primary = _StubClient([None])
        fallback = _StubClient([{"ok": True}])
        router = ModelRouter(primary=primary, fallback=fallback)

        result = router.chat_json("sys", "user")

        self.assertIsNone(result)
        self.assertEqual(primary.calls, 1)
        self.assertEqual(fallback.calls, 0)

    def test_router_marks_timeout_when_client_call_hangs(self) -> None:
        primary = _StubClient([None], timeout_seconds=1)
        router = ModelRouter(primary=primary, fallback=None)

        class DummyThread:
            def __init__(self, target=None, daemon=None):
                del daemon
                self._target = target
                self._alive = True

            def start(self):
                return None

            def join(self, timeout=None):
                del timeout
                return None

            def is_alive(self):
                return True

        with patch("pipeline2.clients.threading.Thread", DummyThread):
            result = router._invoke_client_method_with_timeout(primary, "chat_json", "sys", "user")

        self.assertIsNone(result)
        self.assertIn("timed out", primary.snapshot_usage()["last_error"])


if __name__ == "__main__":
    unittest.main()
