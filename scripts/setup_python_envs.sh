#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# JARVIS — Python Environment Setup (Windows/Unix compatible)
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

PYTHON=${PYTHON:-python}
PACKAGES=("core" "voice" "memory" "skills")
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "╔══════════════════════════════════════════════════════════╗"
echo "║          JARVIS Python Environment Setup                 ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

if ! command -v "$PYTHON" &>/dev/null; then
    echo "❌  $PYTHON not found."
    exit 1
fi

PY_VER=$("$PYTHON" --version 2>&1)
echo "✅  Using $PY_VER"
echo ""

for pkg in "${PACKAGES[@]}"; do
    PKG_DIR="$ROOT_DIR/packages/$pkg"

    if [ ! -d "$PKG_DIR" ]; then
        echo "⚠️   packages/$pkg not found — skipping"
        continue
    fi

    echo "──── packages/$pkg ────────────────────────────────────────"

    VENV="$PKG_DIR/.venv"

    if [ ! -d "$VENV" ]; then
        echo "  Creating .venv..."
        "$PYTHON" -m venv "$VENV"
    else
        echo "  .venv already exists — skipping creation"
    fi

    # Detect Windows vs Unix activate path
    if [ -f "$VENV/Scripts/activate" ]; then
        ACTIVATE="$VENV/Scripts/activate"
    elif [ -f "$VENV/bin/activate" ]; then
        ACTIVATE="$VENV/bin/activate"
    else
        echo "  ❌  Could not find activate script in .venv — skipping"
        continue
    fi

    # shellcheck source=/dev/null
    source "$ACTIVATE"

    # Use venv python directly (required on Windows)
    if [ -f "$VENV/Scripts/python.exe" ]; then
        PYTHON_VENV="$VENV/Scripts/python.exe"
    else
        PYTHON_VENV="$VENV/bin/python"
    fi

    echo "  Upgrading pip..."
    "$PYTHON_VENV" -m pip install --quiet --upgrade pip

    echo "  Installing dependencies from requirements.txt..."
    "$PYTHON_VENV" -m pip install --quiet -r "$PKG_DIR/requirements.txt"

    deactivate
    echo "  ✅  packages/$pkg environment ready"
    echo ""
done

echo "╔══════════════════════════════════════════════════════════╗"
echo "║  All Python environments are ready.                      ║"
echo "║                                                          ║"
echo "║  Next: python scripts/check_hardware.py                  ║"
echo "╚══════════════════════════════════════════════════════════╝"