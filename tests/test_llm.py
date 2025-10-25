from typing import Any, Dict

import pytest

from spooky.llm.local import (
    LlmServerRsClient,
    LocalModelError,
    OllamaClient,
    OpenAICompatibleClient,
    build_client,
)


class _Response:
    def __init__(self, payload: Any) -> None:
        self._payload = payload

    @property
    def text(self) -> str:
        return ""

    def json(self) -> Any:
        return self._payload


def test_llmserver_rs_ping(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: Dict[str, int] = {"health": 0, "models": 0}

    def fake_get(url: str, *, timeout: float, headers: Dict[str, str] | None = None, error_message: str) -> _Response:
        if url.endswith("/health"):
            calls["health"] += 1
            return _Response({"status": "ok", "version": "0.5.0"})
        if url.endswith("/models"):
            calls["models"] += 1
            return _Response({"models": ["tinyllama-1.1b-chat-v1.0.Q8_0.gguf"]})
        raise AssertionError(f"unexpected url {url}")

    monkeypatch.setattr("spooky.llm.local._http_get", fake_get)

    client = LlmServerRsClient("http://llmserver:27121")
    metadata = client.ping()

    assert calls["health"] == 1
    assert calls["models"] == 1
    assert metadata["provider"] == "llmserver-rs"
    assert metadata["status"] == "ok"
    assert "tinyllama-1.1b-chat-v1.0.Q8_0.gguf" in metadata["models"]


def test_llmserver_rs_ping_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_get(url: str, *, timeout: float, headers: Dict[str, str] | None = None, error_message: str) -> _Response:
        raise LocalModelError(error_message)

    monkeypatch.setattr("spooky.llm.local._http_get", fake_get)

    client = LlmServerRsClient("http://llmserver:27121")
    with pytest.raises(LocalModelError):
        client.ping()


def test_openai_compatible_client_uses_authorization_header(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: Dict[str, Any] = {}

    def fake_get(url: str, *, timeout: float, headers: Dict[str, str] | None = None, error_message: str) -> _Response:
        captured["url"] = url
        captured["timeout"] = timeout
        captured["headers"] = headers or {}
        return _Response({"data": [{"id": "glm-4"}]})

    monkeypatch.setattr("spooky.llm.local._http_get", fake_get)

    client = OpenAICompatibleClient("https://llm-gateway.internal:9443", api_key="top-secret", timeout=5.0)
    metadata = client.ping()

    assert captured["url"] == "https://llm-gateway.internal:9443/v1/models"
    assert captured["timeout"] == 5.0
    assert captured["headers"].get("Authorization") == "Bearer top-secret"
    assert metadata["provider"] == "openai-compatible"
    assert "glm-4" in metadata["models"]


def test_ollama_client_lists_tags(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_get(url: str, *, timeout: float, headers: Dict[str, str] | None = None, error_message: str) -> _Response:
        assert url == "http://ollama:11434/api/tags"
        return _Response({"models": [{"name": "qwen3:0.6b"}, {"name": "llama3"}]})

    monkeypatch.setattr("spooky.llm.local._http_get", fake_get)

    client = OllamaClient("http://ollama:11434")
    metadata = client.ping()

    assert metadata["provider"] == "ollama"
    assert "qwen3:0.6b" in metadata["models"]


def test_build_client_supports_llmserver() -> None:
    client = build_client("llmserver-rs", "http://llmserver:27121")
    assert isinstance(client, LlmServerRsClient)


def test_build_client_supports_openai(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("spooky.llm.local._http_get", lambda *args, **kwargs: _Response({"data": []}))

    client = build_client("openai-compatible", "https://llm-gateway.internal:9443", api_key="token")
    assert isinstance(client, OpenAICompatibleClient)
    assert client.base_url == "https://llm-gateway.internal:9443"
