#!/bin/bash
# Lançador da app CCT (macOS) — duplo clique para abrir
cd "$(dirname "$0")/.."
if [ -x ".venv/bin/python" ]; then PY=".venv/bin/python"; else PY="python3"; fi
"$PY" -m cct.app
