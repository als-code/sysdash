#!/usr/bin/env bash
# Bootstrap mínimo: asegura python3 y delega el resto a sysdash.setup (Rich).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

if ! command -v python3 >/dev/null 2>&1; then
    echo "✗ python3 is required" >&2
    exit 1
fi

# Si el venv aún no existe, créalo en silencio para poder importar Rich.
if [[ ! -x "${ROOT}/.venv/bin/python" ]]; then
    if ! python3 -m venv "${ROOT}/.venv" 2>/dev/null; then
        py_minor="$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
        if command -v nala >/dev/null; then
            sudo nala install -y "python${py_minor}-venv" || sudo nala install -y python3-venv
        elif command -v apt >/dev/null; then
            sudo apt install -y "python${py_minor}-venv" || sudo apt install -y python3-venv
        fi
        python3 -m venv "${ROOT}/.venv"
    fi
    "${ROOT}/.venv/bin/pip" install -q -e "${ROOT}"
fi

exec "${ROOT}/.venv/bin/python" -m sysdash.setup
