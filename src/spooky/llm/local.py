"""Local model server integrations."""
from __future__ import annotations

import abc
import json
from typing import Any, Dict, Optional
from urllib import error as urllib_error
from urllib import request as urllib_request

try:  # pragma: no cover - exercised implicitly when requests is installed
    import requests
except ModuleNotFoundError:  # pragma: no cover - fallback when requests is unavailable
    requests = None  # type: ignore[assignment]


class LocalModelError(RuntimeError):
    """Raised when connectivity or validation fails for a local model runtime."""


class _HttpResponse:
    """Minimal HTTP response wrapper used by the local model clients."""

    def __init__(self, status: int, body: bytes) -> None:
        self.status = status
        self._body = body

    @property
    def text(self) -> str:
        return self._body.decode("utf-8", errors="replace")

    def json(self) -> Any:
        return json.loads(self.text)


def _http_get(
    url: str,
    *,
    timeout: float,
    headers: Optional[Dict[str, str]] = None,
    error_message: str,
):
    """Perform an HTTP GET using requests when available, otherwise urllib."""

    if requests is not None:  # pragma: no branch - executed when dependency installed
        try:
            response = requests.get(url, timeout=timeout, headers=headers or {})
            response.raise_for_status()
            return response
        except requests.RequestException as exc:  # pragma: no cover - depends on runtime environment
            raise LocalModelError(error_message) from exc

    req = urllib_request.Request(url, headers=headers or {})
    try:
        with urllib_request.urlopen(req, timeout=timeout) as resp:
            status = getattr(resp, "status", resp.getcode())
            body = resp.read()
    except urllib_error.URLError as exc:
        raise LocalModelError(error_message) from exc

    if status >= 400:
        raise LocalModelError(error_message)

    return _HttpResponse(status=status, body=body)


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
        response = _http_get(
            f"{self.base_url}/api/tags",
            timeout=self.timeout,
            error_message="Failed to contact Ollama runtime",
        )

        payload = response.json()
        tags = [model.get("name", "unknown") for model in payload.get("models", [])]
        return {"provider": "ollama", "models": ", ".join(tags)}


class OpenAICompatibleClient(BaseLocalModelClient):
    """Client for OpenAI-compatible HTTP APIs."""

    def __init__(self, base_url: str, api_key: Optional[str] = None, timeout: float = 10.0) -> None:
        super().__init__(base_url=base_url, timeout=timeout)
        self.api_key = api_key

    def ping(self) -> Dict[str, str]:  # noqa: D401 - short description inherited
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        response = _http_get(
            f"{self.base_url}/v1/models",
            timeout=self.timeout,
            headers=headers,
            error_message="Failed to contact OpenAI-compatible runtime",
        )

        payload = response.json()
        data = payload.get("data", [])
        models = [model.get("id", "unknown") for model in data]
        return {"provider": "openai-compatible", "models": ", ".join(models)}


class LlmServerRsClient(BaseLocalModelClient):
    """Client for the `llmserver-rs` Rust microservice."""

    HEALTH_ENDPOINT = "/health"
    MODELS_ENDPOINT = "/models"

    def ping(self) -> Dict[str, str]:  # noqa: D401 - short description inherited
        response = _http_get(
            f"{self.base_url}{self.HEALTH_ENDPOINT}",
            timeout=self.timeout,
            error_message="Failed to contact llmserver-rs runtime",
        )

        metadata: Dict[str, str] = {"provider": "llmserver-rs"}
        try:
            payload = response.json()
        except ValueError:
            payload = {"status": response.text.strip() or "ok"}

        if isinstance(payload, dict):
            metadata.update({k: str(v) for k, v in payload.items()})
        else:  # pragma: no cover - defensive branch for unexpected payloads
            metadata["status"] = str(payload)

        try:
            models_response = _http_get(
                f"{self.base_url}{self.MODELS_ENDPOINT}",
                timeout=self.timeout,
                error_message="Failed to fetch llmserver-rs model metadata",
            )
            models_payload = models_response.json()
            if isinstance(models_payload, dict):
                models = models_payload.get("models")
            else:
                models = models_payload
            if isinstance(models, list):
                metadata["models"] = ", ".join(str(item) for item in models)
        except LocalModelError:
            metadata.setdefault("models", "unknown")
        except ValueError:
            metadata.setdefault("models", "unknown")

        return metadata


def build_client(provider: str, base_url: str, api_key: Optional[str] = None) -> BaseLocalModelClient:
    """Factory helper that constructs a client for the requested provider."""
    if provider == "ollama":
        return OllamaClient(base_url)
    if provider == "openai-compatible":
        return OpenAICompatibleClient(base_url, api_key=api_key)
    if provider == "llmserver-rs":
        return LlmServerRsClient(base_url)
    raise ValueError(f"Unsupported local model provider: {provider}")
