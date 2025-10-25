# Deployment

Run the bundled Docker Compose stack to launch the CLI container together with an Ollama sidecar:

```bash
docker compose up --build
```

The `spooky` service executes `spooky-cli generate-readme` on startup, ensuring documentation remains
consistent. The Ollama container exposes its HTTP interface on port `11434` with a baked-in health check,
which the CLI can probe via `spooky-cli ping-local --server ollama`.
