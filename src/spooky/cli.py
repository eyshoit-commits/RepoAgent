"""Command line entrypoints for the Spooky platform."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import typer

from .configuration import ConfigLoader
from .documentation.generator import DocumentationGenerator
from .llm import LocalModelError, build_client

app = typer.Typer(help="Utilities for the Spooky orchestration platform.")


@app.command("generate-readme")
def generate_readme(
    docs_root: Path = typer.Option(Path("docs"), help="Directory containing Markdown sources."),
    output_path: Path = typer.Option(Path("README.md"), help="Target README path."),
) -> None:
    """Compose README.md from managed documentation sections."""
    generator = DocumentationGenerator(docs_root=docs_root, output_path=output_path)
    path = generator.write()
    typer.echo(f"README generated at {path}")


@app.command("list-languages")
def list_languages(
    config_path: Path = typer.Option(Path("config/languages.yaml"), help="Language manifest path."),
) -> None:
    """List configured programming language toolchains."""
    loader = ConfigLoader(languages_path=config_path)
    languages = loader.load_languages()
    for language in languages:
        typer.echo(
            f"- {language.name} ({language.id})\n"
            f"  build: {language.build}\n"
            f"  run: {language.run}\n"
            f"  verify: {language.verify}\n"
        )


@app.command("list-models")
def list_models(
    models_path: Path = typer.Option(Path("config/models.yaml"), help="Model manifest path."),
) -> None:
    """List model presets and local server definitions."""
    loader = ConfigLoader(models_path=models_path)
    presets = loader.load_model_presets()
    servers = loader.load_local_servers()

    typer.echo("Model presets:")
    for name, preset in presets.items():
        typer.echo(
            f"- {name}: provider={preset.provider} model={preset.model} params={preset.parameters}"
        )

    typer.echo("\nLocal servers:")
    for name, server_cfg in servers.items():
        api_key_env = server_cfg.api_key_env or "<none>"
        typer.echo(
            f"- {name}: {server_cfg.base_url} (provider={server_cfg.provider}, api_key_env={api_key_env})"
        )


@app.command("ping-local")
def ping_local(
    server: str = typer.Option(..., help="Server alias defined in models.yaml."),
    models_path: Path = typer.Option(Path("config/models.yaml"), help="Model manifest path."),
    timeout: float = typer.Option(10.0, help="Request timeout in seconds."),
) -> None:
    """Validate connectivity to a local model runtime."""
    loader = ConfigLoader(models_path=models_path)
    servers = loader.load_local_servers()
    if server not in servers:
        raise typer.BadParameter(f"Server '{server}' not defined in {models_path}")

    spec = servers[server]
    api_key: Optional[str] = os.getenv(spec.api_key_env) if spec.api_key_env else None

    client = build_client(provider=spec.provider, base_url=spec.base_url, api_key=api_key)
    client.timeout = timeout
    try:
        metadata = client.ping()
    except LocalModelError as exc:
        raise typer.Exit(code=1) from exc

    typer.echo(f"Connection successful: {metadata}")


if __name__ == "__main__":
    app()
