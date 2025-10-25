"""Utilities for generating consolidated documentation artifacts."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List


@dataclass
class DocumentationGenerator:
    """Compose documentation assets into a single README."""

    docs_root: Path = Path("docs")
    output_path: Path = Path("README.md")

    def load_markdown_sections(self, subdirectory: str) -> List[str]:
        """Return markdown sections sorted lexicographically within a subdirectory."""
        directory = self.docs_root / subdirectory
        if not directory.exists():
            return []

        sections: List[str] = []
        for path in sorted(directory.glob("*.md")):
            sections.append(path.read_text(encoding="utf-8").strip())
        return sections

    def compose(self) -> str:
        """Compose the README payload from the managed markdown sections."""
        global_sections = self.load_markdown_sections("global")
        module_sections = self.load_markdown_sections("modules")

        body: List[str] = []
        body.extend(global_sections)
        if module_sections:
            body.append("# Modules")
            body.extend(module_sections)

        return "\n\n".join(self._trim_empty(section for section in body)) + "\n"

    def write(self) -> Path:
        """Write the composed README to disk."""
        content = self.compose()
        self.output_path.write_text(content, encoding="utf-8")
        return self.output_path

    @staticmethod
    def _trim_empty(sections: Iterable[str]) -> Iterable[str]:
        for section in sections:
            if section:
                yield section.strip()
