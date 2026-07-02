#!/bin/bash
# uv-runner.sh (Saved in the root of your git repo)

export PATH="$HOME/.local/bin:$PATH"

# Dynamically calculate the absolute path of the directory containing THIS wrapper script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Grab the Python script name passed from JEC
TARGET_SCRIPT="$1"
shift

# Execute uv run using the dynamically computed absolute path
uv run -- "$SCRIPT_DIR/$TARGET_SCRIPT" "$@"