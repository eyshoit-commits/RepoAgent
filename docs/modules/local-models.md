# Local Model Integrations

Spooky abstracts local large-language-model runtimes by exposing a shared HTTP transport contract. Out of the box
it supports:

- **Ollama** via the REST API served on port `11434`, with a ready-to-use Qwen3:0.6b preset.
- **OpenAI-compatible servers** (e.g., FastChat, vLLM, LM Studio) with token-based authentication.
- **llmserver-rs**, a lightweight Rust microservice that streams GGUF models such as TinyLlama at
  `http://llmserver:27121`.
- **Model presets** for Llama, ChatGLM, Qwen, GLM4, and TinyLlama families through declarative YAML definitions.

The CLI can ping an endpoint, ensuring the runtime is online before dispatching work. New providers can be added by
implementing the `BaseLocalModelClient` protocol in `src/spooky/llm/local.py`, while configuration lives in
`config/models.yaml` so that runtimes remain hot-swappable.
