"""Shared configuration dataclasses."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict


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


@dataclass
class KarmaConfig:
    """Configuration describing karma thresholds and persistence."""

    thresholds: Dict[str, int]
    default_role: str
    storage_path: Path
