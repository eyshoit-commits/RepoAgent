#!/usr/bin/env python
"""Helper script to regenerate README.md from docs."""
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from spooky.documentation.generator import DocumentationGenerator


def main() -> None:
    generator = DocumentationGenerator(docs_root=Path("docs"), output_path=Path("README.md"))
    path = generator.write()
    print(f"README generated at {path}")


if __name__ == "__main__":
    main()
