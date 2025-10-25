# Architecture

The platform is intentionally modular:

- **Documentation pipeline** – parses Markdown assets from the `docs/` tree and composes a canonical
  `README.md`. This keeps high-level documentation synchronized with the implementation.
- **Language adapters** – declarative metadata in `config/languages.yaml` describes how to compile or
  execute workloads across Python, Java, C, C++, and other ecosystems.
- **Model providers** – connectors in `src/spooky/llm` expose a shared protocol for local runtimes such as
  Ollama, `llmserver-rs`, or HTTP-compatible OpenAI deployments, and for remote managed services.

The modules communicate through lightweight configuration files serialized with YAML, enabling hot-swappable
components without code changes.
