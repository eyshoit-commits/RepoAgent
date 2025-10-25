from pathlib import Path

from spooky.documentation.generator import DocumentationGenerator


def test_compose_readme(tmp_path: Path) -> None:
    docs_root = tmp_path / "docs"
    (docs_root / "global").mkdir(parents=True)
    (docs_root / "modules").mkdir()

    (docs_root / "global" / "a.md").write_text("# A", encoding="utf-8")
    (docs_root / "modules" / "b.md").write_text("## B", encoding="utf-8")

    generator = DocumentationGenerator(docs_root=docs_root, output_path=tmp_path / "README.md")
    generator.write()

    content = (tmp_path / "README.md").read_text(encoding="utf-8")
    assert "# A" in content
    assert "# Modules" in content
    assert "## B" in content
