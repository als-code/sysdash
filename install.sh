#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

if ! command -v python3 >/dev/null; then
    echo "python3 required" >&2
    exit 1
fi

if [[ ! -x "${ROOT}/.venv/bin/python" ]]; then
    if ! python3 -m venv "${ROOT}/.venv" 2>/dev/null; then
        ver="$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
        if command -v nala >/dev/null; then
            sudo nala install -y "python${ver}-venv" || sudo nala install -y python3-venv
        elif command -v apt >/dev/null; then
            sudo apt install -y "python${ver}-venv" || sudo apt install -y python3-venv
        fi
        python3 -m venv "${ROOT}/.venv"
    fi
    "${ROOT}/.venv/bin/pip" install -q -e "${ROOT}"
fi

exec "${ROOT}/.venv/bin/python" -m sysdash.setup
