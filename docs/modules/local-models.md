# Local Model Integrations

Spooky abstracts local large-language-model runtimes by exposing a shared HTTP transport contract. Out of the box
it supports:

- **Ollama** via the REST API served on port `11434`.
- **OpenAI-compatible servers** (e.g., FastChat, vLLM, LM Studio) with token-based authentication.
- **Model presets** for Llama, ChatGLM, Qwen, and GLM4 families through declarative YAML definitions.

The CLI can ping an endpoint, ensuring the runtime is online before dispatching work. New providers can be added by
implementing the `BaseLocalModelClient` protocol in `src/spooky/llm/local.py`.
