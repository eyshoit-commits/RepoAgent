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

4. Test connectivity with the bundled local runtimes. The command accepts any server alias
   from `config/models.yaml` and verifies that the health and model metadata endpoints respond:

   ```bash
   spooky-cli ping-local --server ollama        # Ollama with Qwen3:0.6b pulled automatically
   spooky-cli ping-local --server llmserver_rs  # Rust llmserver-rs serving TinyLlama
   ```

5. Manage member karma and trigger automatic promotions:

   ```bash
   spooky-cli karma award alice --points 10
   spooky-cli karma status alice
   spooky-cli karma leaderboard --limit 5
   ```
