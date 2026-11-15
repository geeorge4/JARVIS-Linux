#!/bin/sh
set -eu
cd "$(dirname "$0")"
python3 -m venv --system-site-packages .venv
.venv/bin/python -m pip install -r requirements.txt
if [ ! -f libjarvis_audio.so ] && command -v rustc >/dev/null 2>&1; then
    rustc --crate-type cdylib -O native/audio.rs -o libjarvis_audio.so
fi
printf '%s\n' 'Готово. Запуск: sh start.sh'
