"""Local model server integrations."""
from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import Dict, Optional

import requests


class LocalModelError(RuntimeError):
    """Raised when connectivity or validation fails for a local model runtime."""


class BaseLocalModelClient(abc.ABC):
    """Abstract base client for local language-model servers."""

    def __init__(self, base_url: str, timeout: float = 10.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    @abc.abstractmethod
    def ping(self) -> Dict[str, str]:
        """Validate connectivity and return service metadata."""


class OllamaClient(BaseLocalModelClient):
    """Client for interacting with an Ollama runtime."""

    def ping(self) -> Dict[str, str]:  # noqa: D401 - short description inherited
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=self.timeout)
            response.raise_for_status()
        except requests.RequestException as exc:  # pragma: no cover - network errors are runtime specific
            raise LocalModelError("Failed to contact Ollama runtime") from exc

        payload = response.json()
        tags = [model.get("name", "unknown") for model in payload.get("models", [])]
        return {"provider": "ollama", "models": ", ".join(tags)}


@dataclass
class OpenAICompatibleClient(BaseLocalModelClient):
    """Client for OpenAI-compatible HTTP APIs."""

    api_key: Optional[str] = None

    def ping(self) -> Dict[str, str]:  # noqa: D401 - short description inherited
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        try:
            response = requests.get(
                f"{self.base_url}/v1/models",
                headers=headers,
                timeout=self.timeout,
            )
            response.raise_for_status()
        except requests.RequestException as exc:  # pragma: no cover - network errors are runtime specific
            raise LocalModelError("Failed to contact OpenAI-compatible runtime") from exc

        payload = response.json()
        data = payload.get("data", [])
        models = [model.get("id", "unknown") for model in data]
        return {"provider": "openai-compatible", "models": ", ".join(models)}


def build_client(provider: str, base_url: str, api_key: Optional[str] = None) -> BaseLocalModelClient:
    """Factory helper that constructs a client for the requested provider."""
    if provider == "ollama":
        return OllamaClient(base_url)
    if provider == "openai-compatible":
        return OpenAICompatibleClient(base_url, api_key=api_key)
    raise ValueError(f"Unsupported local model provider: {provider}")
