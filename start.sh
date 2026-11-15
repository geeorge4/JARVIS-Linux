#!/bin/sh
set -eu
cd "$(dirname "$0")"
if [ -x .venv/bin/python ]; then
    exec .venv/bin/python jarvis_ui.py "$@"
fi
exec python3 jarvis_ui.py "$@"
