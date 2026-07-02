#!/bin/bash
# uv-wrapper.sh

# 1. Grab the first argument, which will be the target Python script path
TARGET_SCRIPT="$1"

# 2. Shift the argument positional parameters left by 1.
# This drops the Python script name from "$@" so it isn't passed twice.
shift

# 3. Execute uv run, feeding it the target script and the remaining JEC args
uv run -- "$TARGET_SCRIPT" "$@"