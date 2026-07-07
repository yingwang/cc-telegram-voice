#!/usr/bin/env bash
# One-time setup for offline voice transcription.
#
# Creates a Python virtualenv with PyAV (for decoding), then builds whisper.cpp
# and downloads a Whisper model (for recognition). Everything lands inside this
# repo directory, so the setup is self-contained and easy to delete.
#
# Re-running is safe: each step is skipped if it is already done.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_ROOT"

MODEL_NAME="ggml-small-q5_1.bin"
MODEL_URL="https://huggingface.co/ggerganov/whisper.cpp/resolve/main/${MODEL_NAME}"

echo "==> 1/3  Python virtualenv with PyAV"
if [ ! -d ".venv" ]; then
  if command -v uv >/dev/null 2>&1; then
    uv venv .venv
    uv pip install --python .venv/bin/python -r requirements.txt
  else
    python3 -m venv .venv
    ./.venv/bin/pip install --upgrade pip
    ./.venv/bin/pip install -r requirements.txt
  fi
else
  echo "    .venv already exists, skipping"
fi

echo "==> 2/3  whisper.cpp"
if [ ! -x "whisper.cpp/build/bin/whisper-cli" ]; then
  if ! command -v cmake >/dev/null 2>&1; then
    echo "    cmake is required to build whisper.cpp." >&2
    echo "    macOS:  brew install cmake" >&2
    echo "    Debian: sudo apt-get install cmake build-essential" >&2
    exit 1
  fi
  if [ ! -d "whisper.cpp" ]; then
    git clone --depth 1 https://github.com/ggerganov/whisper.cpp.git
  fi
  cmake -S whisper.cpp -B whisper.cpp/build
  cmake --build whisper.cpp/build --config Release -j
else
  echo "    whisper-cli already built, skipping"
fi

echo "==> 3/3  Whisper model ($MODEL_NAME, ~180 MB)"
mkdir -p models
if [ ! -f "models/${MODEL_NAME}" ]; then
  if command -v curl >/dev/null 2>&1; then
    curl -L --fail -o "models/${MODEL_NAME}" "$MODEL_URL"
  else
    wget -O "models/${MODEL_NAME}" "$MODEL_URL"
  fi
else
  echo "    model already present, skipping"
fi

echo
echo "Setup complete. Quick test:"
echo "    ./.venv/bin/python transcribe.py path/to/voice.oga --lang zh"
