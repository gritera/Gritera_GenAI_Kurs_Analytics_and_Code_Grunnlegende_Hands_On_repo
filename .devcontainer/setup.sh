#!/usr/bin/env bash
set -euo pipefail

echo "=== Gritera GenAI Kurs — Miljøoppsett ==="

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
