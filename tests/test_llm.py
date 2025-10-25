from typing import Any, Dict

import pytest

from spooky.llm.local import LlmServerRsClient, LocalModelError, build_client


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


def test_build_client_supports_llmserver() -> None:
    client = build_client("llmserver-rs", "http://llmserver:27121")
    assert isinstance(client, LlmServerRsClient)
