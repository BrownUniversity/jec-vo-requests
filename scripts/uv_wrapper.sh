#!/bin/sh
export PATH="$HOME/.local/bin:$PATH"
export UV_CACHE_DIR="/tmp/uv-cache"
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)

exec uv run -- "$SCRIPT_DIR/boilerplate.py" "$@"