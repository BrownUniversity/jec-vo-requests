#!/bin/sh
export PATH="$HOME/.local/bin:$PATH"
export UV_CACHE_DIR="/tmp/uv-cache"
export GCP_ORG_ID=$GCP_ORG_ID
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)

exec uv run -- "$SCRIPT_DIR/create_gcp_project.py" "$@"