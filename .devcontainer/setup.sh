#!/usr/bin/env bash
set -euo pipefail

echo "=== Gritera GenAI Kurs — Miljøoppsett ==="

# ---- Installer uv ----
# Base-imaget (python:3.12) har pip; vi installerer uv via PyPI for å unngå
# avhengighet til ghcr.io devcontainer-features som kan feile på restriktive nett.
if ! command -v uv >/dev/null 2>&1; then
  echo "Installerer uv via pip..."
  pip install --quiet --user uv
  # Sørg for at uv er på PATH i denne økten og fremtidige shells
  USER_BIN="$(python -m site --user-base)/bin"
  export PATH="$USER_BIN:$PATH"
  if ! grep -q "$USER_BIN" ~/.bashrc 2>/dev/null; then
    echo "export PATH=\"$USER_BIN:\$PATH\"" >> ~/.bashrc
  fi
fi

# ---- Python-avhengigheter via uv ----
echo "Installerer dbt og avhengigheter med uv..."
uv sync

# ---- Claude Code CLI ----
echo "Installerer Claude Code..."
npm install -g @anthropic-ai/claude-code@latest || {
  echo "MERK: Claude Code npm-installasjon feilet."
  echo "      Installer manuelt: npm install -g @anthropic-ai/claude-code"
}

# Sørg for at npm global bin er i PATH for fremtidige shell-økter
NPM_BIN="$(npm prefix -g)/bin"
if [[ ":$PATH:" != *":$NPM_BIN:"* ]]; then
  echo "export PATH=\"\$PATH:$NPM_BIN\"" >> ~/.bashrc
  export PATH="$PATH:$NPM_BIN"
fi

# ---- dbt prosjekt ----
echo "Kjører dbt seed + run..."
uv run dbt seed --quiet
uv run dbt run --quiet

echo ""
echo "=== Miljøet er klart! ==="
echo ""
echo "  uv run dbt debug   # verifiser at alt fungerer"
echo "  claude             # start Claude Code (krever ANTHROPIC_API_KEY)"
echo ""
