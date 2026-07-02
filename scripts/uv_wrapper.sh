#!/bin/sh
export PATH="$HOME/.local/bin:$PATH"
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)

exec uv run -- "$SCRIPT_DIR/scripts/boilerplate.py" "$@"