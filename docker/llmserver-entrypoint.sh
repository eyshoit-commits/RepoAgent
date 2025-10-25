#!/usr/bin/env bash
set -euo pipefail

MODEL_URL=${MODEL_URL:-https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q8_0.gguf}
MODEL_PATH=${MODEL_PATH:-/models/tinyllama-1.1b-chat-v1.0.Q8_0.gguf}
LLMSERVER_PORT=${LLMSERVER_PORT:-27121}
LLMSERVER_HOST=${LLMSERVER_HOST:-0.0.0.0}

mkdir -p "$(dirname "${MODEL_PATH}")"
if [ ! -f "${MODEL_PATH}" ]; then
  echo "Downloading model weights from ${MODEL_URL}" >&2
  curl -L --fail "${MODEL_URL}" -o "${MODEL_PATH}.download"
  mv "${MODEL_PATH}.download" "${MODEL_PATH}"
fi

HELP_TEXT=$(llmserver --help 2>&1 || true)
if grep -q -- "--bind" <<<"${HELP_TEXT}"; then
  exec llmserver --model "${MODEL_PATH}" --bind "${LLMSERVER_HOST}:${LLMSERVER_PORT}"
elif grep -q -- "--host" <<<"${HELP_TEXT}" && grep -q -- "--port" <<<"${HELP_TEXT}"; then
  exec llmserver --model "${MODEL_PATH}" --host "${LLMSERVER_HOST}" --port "${LLMSERVER_PORT}"
else
  exec llmserver --model "${MODEL_PATH}"
fi
