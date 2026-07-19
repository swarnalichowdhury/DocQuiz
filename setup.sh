#!/usr/bin/env bash
set -e

echo "=== DocQuiz setup ==="

# 1. Detect OS
OS_NAME="$(uname -s)"
case "$OS_NAME" in
    Linux*)             PLATFORM="linux" ;;
    Darwin*)            PLATFORM="mac" ;;
    MINGW*|MSYS*|CYGWIN*) PLATFORM="windows" ;;
    *)                  PLATFORM="unknown" ;;
esac
echo "Detected platform: $PLATFORM"

print_python_install_help() {
    echo ""
    echo "Python 3.10+ is required but was not found (or is too old)."
    echo "Install it with the command for your system, then re-run this script:"
    case "$PLATFORM" in
        windows)
            echo "  winget install -e --id Python.Python.3.12"
            echo "  (or download from https://python.org — tick 'Add python.exe to PATH')"
            ;;
        mac)
            echo "  brew install python@3.12"
            echo "  (no Homebrew? download from https://python.org)"
            ;;
        linux)
            echo "  sudo apt install python3 python3-venv python3-pip    # Debian/Ubuntu"
            echo "  sudo dnf install python3                             # Fedora"
            ;;
        *)
            echo "  Download from https://python.org"
            ;;
    esac
}

# 2. Find a Python interpreter (3.10+)
PYTHON=""
for candidate in python3 python; do
    if command -v "$candidate" >/dev/null 2>&1; then
        # Reject the Windows Store stub, which exists but isn't real Python
        if version_output=$("$candidate" --version 2>&1) && [[ "$version_output" == Python\ 3.* ]]; then
            minor=$(echo "$version_output" | sed 's/Python 3\.\([0-9]*\).*/\1/')
            if [ "$minor" -ge 10 ] 2>/dev/null; then
                PYTHON="$candidate"
                break
            else
                echo "Found $version_output at '$candidate' — too old, need 3.10+."
            fi
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    print_python_install_help
    exit 1
fi
echo "Using $($PYTHON --version)"

# 3. Create venv + install deps (prefer uv if available)
if command -v uv >/dev/null 2>&1; then
    echo "uv found, using it..."
    uv venv .venv
    uv pip install -r requirements.txt --python .venv
else
    echo "uv not found, using standard venv + pip..."
    "$PYTHON" -m venv .venv
    if [ "$PLATFORM" = "windows" ]; then
        ./.venv/Scripts/python.exe -m pip install --upgrade pip
        ./.venv/Scripts/python.exe -m pip install -r requirements.txt
    else
        ./.venv/bin/python -m pip install --upgrade pip
        ./.venv/bin/python -m pip install -r requirements.txt
    fi
fi

# 4. Set up .env
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env from .env.example — add your GROQ_API_KEY before running anything."
else
    echo ".env already exists, leaving it alone."
fi

# 5. Print next steps
echo ""
echo "=== Setup done ==="
if [ "$PLATFORM" = "windows" ]; then
    echo "Activate with:  source .venv/Scripts/activate"
else
    echo "Activate with:  source .venv/bin/activate"
fi
echo "Then add GROQ_API_KEY to .env and run:"
echo "  python starter/main.py sample_notes/python_oop_basics.pdf"
