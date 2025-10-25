#!/usr/bin/env python
"""Helper script to regenerate README.md from docs."""
from pathlib import Path

from spooky.documentation.generator import DocumentationGenerator


def main() -> None:
    generator = DocumentationGenerator(docs_root=Path("docs"), output_path=Path("README.md"))
    path = generator.write()
    print(f"README generated at {path}")


if __name__ == "__main__":
    main()
