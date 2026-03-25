#!/usr/bin/env bash
# setup_backend.sh — Install the Voice2MIDI Python backend
# Creates a dedicated venv at ~/.voice2midi/venv

set -e

VENV_DIR="$HOME/.voice2midi/venv"

echo "=== Voice2MIDI Backend Setup ==="
echo ""

# ── Python check ─────────────────────────────────────────────────────────────
# Try modern Python versions first (3.12, 3.11, 3.10), then fall back to python3
PYTHON_BIN=""
for candidate in python3.12 python3.11 python3.10 python3; do
    if command -v "$candidate" &>/dev/null; then
        VER=$("$candidate" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
        MAJOR=$(echo "$VER" | cut -d. -f1)
        MINOR=$(echo "$VER" | cut -d. -f2)
        if [ "$MAJOR" -gt 3 ] || { [ "$MAJOR" -eq 3 ] && [ "$MINOR" -ge 10 ]; }; then
            PYTHON_BIN="$candidate"
            PY_VERSION="$VER"
            break
        fi
    fi
done

if [ -z "$PYTHON_BIN" ]; then
    echo "ERROR: Python 3.10 or higher is required but was not found."
    echo ""
    echo "macOS ships with Python 3.9 which is too old. Install a newer version:"
    echo ""
    echo "  Option 1 (Homebrew):"
    echo "    brew install python@3.12"
    echo "    echo 'export PATH=\"/opt/homebrew/opt/python@3.12/bin:\$PATH\"' >> ~/.zprofile"
    echo "    source ~/.zprofile"
    echo ""
    echo "  Option 2 (python.org):"
    echo "    Download from https://www.python.org/downloads/"
    echo ""
    exit 1
fi

echo "Found Python $PY_VERSION ($PYTHON_BIN)"

# ── Create venv ───────────────────────────────────────────────────────────────
echo ""
echo "Creating virtual environment at $VENV_DIR ..."
mkdir -p "$(dirname "$VENV_DIR")"
"$PYTHON_BIN" -m venv "$VENV_DIR"

VENV_PY="$VENV_DIR/bin/python3"
VENV_PIP="$VENV_DIR/bin/pip"

echo "Upgrading pip ..."
"$VENV_PIP" install --upgrade pip --quiet

# ── Install dependencies ──────────────────────────────────────────────────────
echo ""
echo "Installing dependencies (this may take a few minutes — TensorFlow is ~1 GB) ..."
"$VENV_PIP" install -r "$(dirname "$0")/requirements.txt"

# ── Validate ─────────────────────────────────────────────────────────────────
echo ""
echo "Validating installation ..."

"$VENV_PY" - <<'EOF'
import sys

# Deep import — catches pkg_resources/setuptools failures that shallow imports miss
missing = []
for pkg, import_stmt in [
    ("basic_pitch", "from basic_pitch.predict import main"),
    ("scipy",       "import scipy.signal.windows"),
    ("onnxruntime", "import onnxruntime"),
    ("rumps",       "import rumps"),
]:
    try:
        exec(import_stmt)
    except Exception as e:
        missing.append(f"{pkg} ({e})")

if missing:
    print(f"ERROR: Import failures:\n  " + "\n  ".join(missing))
    sys.exit(1)

# Confirm scipy.signal.gaussian is accessible (via monkey-patch path)
import scipy.signal.windows as w
assert hasattr(w, "gaussian"), "scipy.signal.windows.gaussian not found"

print("basic_pitch predict OK")
print("All packages OK.")
EOF

echo ""
echo "=== Setup complete! ==="
echo ""
echo "Run Voice2MIDI with:"
echo "  ~/.voice2midi/venv/bin/python voice2midi.py"
echo ""
echo "Or build the .app:"
echo "  $VENV_PIP install py2app"
echo "  $VENV_PY setup.py py2app"
