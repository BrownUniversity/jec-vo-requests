#!/bin/sh
# uv_wrapper.sh

# Ensure uv is in the path
export PATH="$HOME/.local/bin:$PATH"

# 1. POSIX compliant way to find the script's directory
SCRIPT_DIR=$(dirname "$0")
SCRIPT_DIR=$(cd "$SCRIPT_DIR" && pwd)

# 2. Extract the target python script name
TARGET_SCRIPT="$1"

# 3. Safety check: If JEC passed an empty argument or an internal flag first, 
# prevent the shell from breaking
if [ -z "$TARGET_SCRIPT" ] || [ "$(echo "$TARGET_SCRIPT" | cut -c1-2)" = "//" ]; then
    echo "Error: Invalid or missing Python target script argument."
    exit 2
fi

# 4. Remove the target script from the argument list 
shift

# 5. Execute uv run using absolute paths. 
# We use "$@" to cleanly forward all remaining arguments (and JEC tokens) without evaluation.
exec uv run -- "$SCRIPT_DIR/$TARGET_SCRIPT" "$@"