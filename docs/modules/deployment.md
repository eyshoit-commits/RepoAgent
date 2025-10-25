# Deployment

Run the bundled Docker Compose stack to launch the CLI container together with two local-model
sidecars: `ollama` for Qwen3:0.6b inference and `llmserver` for TinyLlama served via
[`llmserver-rs`](https://github.com/eyshoit-commits/llmserver-rs/):

```bash
docker compose up --build
```

The `spooky` service executes `spooky-cli generate-readme` on startup, ensuring documentation remains
consistent. The Ollama container exposes its HTTP interface on port `11434` with a baked-in health check,
which the CLI can probe via `spooky-cli ping-local --server ollama`. The Rust `llmserver` sidecar listens
on port `27121` and automatically downloads the
[`TinyLlama-1.1B-Chat-v1.0.Q8_0.gguf`](https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF)
weights on first boot so the bundled `tinyllama_q8_chat` preset can be exercised locally.
