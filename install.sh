#!/usr/bin/env bash
# Polaris Plugins Official — install script
# Downloads pre-built binaries from GitHub Releases and installs to ~/.local/bin
set -euo pipefail

REPO="polarisagi/polarisagi-plugins-official"
INSTALL_DIR="${HOME}/.local/bin"

# ── OS / arch detection ────────────────────────────────────────────────────────
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m)
case "$ARCH" in
  x86_64)          ARCH="amd64" ;;
  aarch64|arm64)   ARCH="arm64" ;;
  *)
    echo "Unsupported architecture: $ARCH"
    exit 1
    ;;
esac

# Windows (Git Bash / MSYS2) detection
EXT=""
if [[ "$OS" == "mingw"* || "$OS" == "msys"* || "$OS" == "cygwin"* ]]; then
  OS="windows"
  EXT=".exe"
fi

echo "Detected: ${OS}/${ARCH}"

# ── Resolve latest release tag ─────────────────────────────────────────────────
TAG=$(curl -fsSL "https://api.github.com/repos/${REPO}/releases/latest" \
  | grep '"tag_name"' \
  | sed 's/.*"tag_name": *"\(.*\)".*/\1/')

if [[ -z "$TAG" ]]; then
  echo "Failed to fetch latest release tag."
  exit 1
fi

echo "Latest release: ${TAG}"
BASE_URL="https://github.com/${REPO}/releases/download/${TAG}"

# ── Install directory ──────────────────────────────────────────────────────────
mkdir -p "$INSTALL_DIR"

# ── Download helper ────────────────────────────────────────────────────────────
download() {
  local url="$1"
  local dest="$2"
  echo "  Downloading $(basename "$dest") ..."
  curl -fsSL "$url" -o "$dest"
  chmod +x "$dest"
}

# ── polarisagi-computer-mcp (Rust) ────────────────────────────────────────────────
echo ""
echo "[1/2] Installing polarisagi-computer-mcp ..."
download \
  "${BASE_URL}/polarisagi-computer-mcp_${OS}_${ARCH}${EXT}" \
  "${INSTALL_DIR}/polarisagi-computer-mcp${EXT}"

# ── polarisagi-knowledge-base (Go) ────────────────────────────────────────────────
echo ""
echo "[2/2] Installing polarisagi-knowledge-base ..."
download \
  "${BASE_URL}/polarisagi-knowledge-base_${OS}_${ARCH}${EXT}" \
  "${INSTALL_DIR}/polarisagi-knowledge-base${EXT}"

# ── PATH reminder ──────────────────────────────────────────────────────────────
echo ""
echo "Done! Binaries installed to: ${INSTALL_DIR}"
echo ""

if [[ ":$PATH:" != *":${INSTALL_DIR}:"* ]]; then
  echo "Add the following line to your shell profile (~/.bashrc / ~/.zshrc):"
  echo ""
  echo "  export PATH=\"\${HOME}/.local/bin:\$PATH\""
  echo ""
fi

echo "Browser Use (polarisagi-browser-use) uses Playwright MCP and requires Node.js."
echo "No install needed — npx downloads it automatically on first use."
echo ""
echo "See https://polarisagi.online/ for full documentation."
