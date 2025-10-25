"""Spooky package initialization."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("spooky")
except PackageNotFoundError:  # pragma: no cover - fallback during editable installs
    __version__ = "0.1.0"

__all__ = ["__version__"]
