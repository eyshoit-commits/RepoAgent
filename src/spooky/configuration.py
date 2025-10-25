"""Configuration loading utilities."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import yaml

from .config_models import KarmaConfig, LanguageConfig, LocalServer, ModelPreset


class ConfigLoader:
    """Load language and model metadata from YAML manifests."""

    def __init__(
        self,
        languages_path: Path | None = None,
        models_path: Path | None = None,
        karma_path: Path | None = None,
    ) -> None:
        self.languages_path = languages_path or Path("config/languages.yaml")
        self.models_path = models_path or Path("config/models.yaml")
        self.karma_path = karma_path or Path("config/karma.yaml")

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

    def load_karma_config(self) -> KarmaConfig:
        data = self._load_yaml(self.karma_path) or {}

        raw_thresholds = data.get("thresholds", {})
        if not raw_thresholds:
            raise ValueError("karma configuration must define at least one threshold")

        default_role = data.get("default_role")
        normalized_thresholds = {str(role): int(value) for role, value in raw_thresholds.items()}

        if default_role is None:
            default_role = min(normalized_thresholds, key=lambda role: normalized_thresholds[role])
        if default_role not in normalized_thresholds:
            raise ValueError("default_role must reference a defined threshold")

        storage_spec = data.get("storage", {})
        storage_path_value = storage_spec.get("path", "var/karma_state.json")
        storage_path = Path(storage_path_value)
        if not storage_path.is_absolute():
            storage_path = (self.karma_path.parent / storage_path).resolve()

        return KarmaConfig(
            thresholds=normalized_thresholds,
            default_role=str(default_role),
            storage_path=storage_path,
        )

    @staticmethod
    def _load_yaml(path: Path) -> Any:
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")
        return yaml.safe_load(path.read_text(encoding="utf-8"))
