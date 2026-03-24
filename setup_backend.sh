#!/usr/bin/env bash
# setup_backend.sh — Install the Voice2MIDI Python backend
# Creates a dedicated venv at ~/.voice2midi/venv

set -e

VENV_DIR="$HOME/.voice2midi/venv"

echo "=== Voice2MIDI Backend Setup ==="
echo ""

# ── Python check ─────────────────────────────────────────────────────────────
if ! command -v python3 &>/dev/null; then
    echo "ERROR: python3 not found."
    echo "Install Python 3.10+ from https://www.python.org/downloads/"
    exit 1
fi

PY_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "Found Python $PY_VERSION"

# Require 3.10+
MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
MINOR=$(echo "$PY_VERSION" | cut -d. -f2)
if [ "$MAJOR" -lt 3 ] || { [ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 10 ]; }; then
    echo "ERROR: Python 3.10 or higher is required (found $PY_VERSION)."
    exit 1
fi

# ── Create venv ───────────────────────────────────────────────────────────────
echo ""
echo "Creating virtual environment at $VENV_DIR ..."
mkdir -p "$(dirname "$VENV_DIR")"
python3 -m venv "$VENV_DIR"

VENV_PY="$VENV_DIR/bin/python3"
VENV_PIP="$VENV_DIR/bin/pip"

echo "Upgrading pip ..."
"$VENV_PIP" install --upgrade pip --quiet

# ── Install dependencies ──────────────────────────────────────────────────────
echo ""
echo "Installing dependencies (this may take a few minutes) ..."
"$VENV_PIP" install -r "$(dirname "$0")/requirements.txt"

# ── Validate ─────────────────────────────────────────────────────────────────
echo ""
echo "Validating installation ..."

"$VENV_PY" - <<'EOF'
import sys

missing = []
for pkg in ["basic_pitch", "scipy", "onnxruntime", "rumps"]:
    try:
        __import__(pkg)
    except ImportError:
        missing.append(pkg)

if missing:
    print(f"ERROR: Missing packages: {', '.join(missing)}")
    sys.exit(1)

# Confirm scipy.signal.gaussian is accessible (via monkey-patch path)
import scipy.signal.windows as w
assert hasattr(w, "gaussian"), "scipy.signal.windows.gaussian not found"

print("All packages OK.")
EOF

echo ""
echo "=== Setup complete! ==="
echo ""
echo "Run Voice2MIDI with:"
echo "  python3 voice2midi.py"
echo ""
echo "Or build the .app:"
echo "  $VENV_PY setup.py py2app"
