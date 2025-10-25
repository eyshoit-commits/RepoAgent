"""Configuration loading utilities."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

import yaml


@dataclass
class LanguageConfig:
    id: str
    name: str
    build: str
    run: str
    verify: str


@dataclass
class ModelPreset:
    name: str
    provider: str
    model: str
    parameters: Dict[str, Any]


@dataclass
class LocalServer:
    provider: str
    base_url: str
    api_key_env: str | None = None


class ConfigLoader:
    """Load language and model metadata from YAML manifests."""

    def __init__(self, languages_path: Path | None = None, models_path: Path | None = None) -> None:
        self.languages_path = languages_path or Path("config/languages.yaml")
        self.models_path = models_path or Path("config/models.yaml")

    def load_languages(self) -> List[LanguageConfig]:
        entries = self._load_yaml(self.languages_path) or []
        languages: List[LanguageConfig] = []
        for entry in entries:
            languages.append(LanguageConfig(**entry))
        return languages

    def load_models(self) -> Dict[str, Any]:
        return self._load_yaml(self.models_path) or {}

    def load_model_presets(self) -> Dict[str, ModelPreset]:
        models = self.load_models().get("presets", {})
        return {
            name: ModelPreset(
                name=name,
                provider=spec["provider"],
                model=spec["model"],
                parameters=spec.get("parameters", {}),
            )
            for name, spec in models.items()
        }

    def load_local_servers(self) -> Dict[str, LocalServer]:
        servers = self.load_models().get("local_servers", {})
        return {
            name: LocalServer(
                provider=spec.get("provider", name),
                base_url=spec["base_url"],
                api_key_env=spec.get("api_key_env"),
            )
            for name, spec in servers.items()
        }

    @staticmethod
    def _load_yaml(path: Path) -> Any:
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")
        return yaml.safe_load(path.read_text(encoding="utf-8"))
