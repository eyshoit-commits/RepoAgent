# Spooky Platform Overview

Spooky is a modular orchestration layer for generative AI workflows. It provides a consistent interface
for local and remote language models, curated documentation, and tooling to produce distribution-ready
artifacts such as README files or deployment manifests.

# Architecture

The platform is intentionally modular:

- **Documentation pipeline** – parses Markdown assets from the `docs/` tree and composes a canonical
  `README.md`. This keeps high-level documentation synchronized with the implementation.
- **Language adapters** – declarative metadata in `config/languages.yaml` describes how to compile or
  execute workloads across Python, Java, C, C++, and other ecosystems.
- **Model providers** – connectors in `src/spooky/llm` expose a shared protocol for local runtimes such as
  Ollama or HTTP-compatible OpenAI deployments, and for remote managed services.

The modules communicate through lightweight configuration files serialized with YAML, enabling hot-swappable
components without code changes.

# Usage

1. Install the Python package in editable mode:

   ```bash
   pip install -e .
   ```

2. Generate the synchronized `README.md`:

   ```bash
   spooky-cli generate-readme
   ```

3. Discover supported languages and models:

   ```bash
   spooky-cli list-languages
   spooky-cli list-models
   ```

4. Test connectivity with a local Ollama or OpenAI-compatible deployment:

   ```bash
   spooky-cli ping-local --server ollama
   ```

5. Manage member karma and trigger automatic promotions:

   ```bash
   spooky-cli karma award alice --points 10
   spooky-cli karma status alice
   spooky-cli karma leaderboard --limit 5
   ```

# Modules

# Deployment

Run the bundled Docker Compose stack to launch the CLI container together with an Ollama sidecar:

```bash
docker compose up --build
```

The `spooky` service executes `spooky-cli generate-readme` on startup, ensuring documentation remains
consistent. The Ollama container exposes its HTTP interface on port `11434` with a baked-in health check,
which the CLI can probe via `spooky-cli ping-local --server ollama`.

## Karma System

The karma subsystem tracks community contributions and automatically promotes members to the
**specialist** role once they accumulate sufficient points. Configuration lives in `config/karma.yaml`:

```yaml
default_role: novice
thresholds:
  novice: 0
  contributor: 40
  specialist: 100
storage:
  path: ../var/karma_state.json
```

- `thresholds` defines the minimum karma required for each role.
- `default_role` is applied to new members that have not earned karma yet.
- `storage.path` persists balances so that promotions survive restarts.

Use the CLI to interact with the system:

```bash
spooky-cli karma award alice --points 10   # grant karma
spooky-cli karma status alice              # inspect current role
spooky-cli karma leaderboard --limit 5     # view top performers
```

When a member crosses the configured `specialist` threshold, their role automatically updates
without restarting the application, enabling hot-swappable promotions aligned with the platform's
modular principles.

# Language Adapters

The `config/languages.yaml` file defines compilation or execution commands per language. Each entry specifies
an identifier, runtime tooling, and a verification command that can be invoked by external orchestrators.

Example entry:

```yaml
- id: java
  name: Java 21
  build: mvn -q -DskipTests package
  run: java -jar target/app.jar
  verify: mvn -q test
```

The CLI surfaces this metadata so you can plug it into CI/CD pipelines or developer automation.

# Local Model Integrations

Spooky abstracts local large-language-model runtimes by exposing a shared HTTP transport contract. Out of the box
it supports:

- **Ollama** via the REST API served on port `11434`.
- **OpenAI-compatible servers** (e.g., FastChat, vLLM, LM Studio) with token-based authentication.
- **Model presets** for Llama, ChatGLM, Qwen, and GLM4 families through declarative YAML definitions.

The CLI can ping an endpoint, ensuring the runtime is online before dispatching work. New providers can be added by
implementing the `BaseLocalModelClient` protocol in `src/spooky/llm/local.py`.
