"""Language-model integration helpers."""

from .local import BaseLocalModelClient, LocalModelError, build_client

__all__ = ["BaseLocalModelClient", "LocalModelError", "build_client"]
