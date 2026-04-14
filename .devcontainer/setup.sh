#!/bin/bash
set -e

echo "=== Gritera GenAI Kurs — Miljøoppsett ==="

# ---- Python-avhengigheter ----
echo "Installerer dbt og DuckDB..."
pip install --quiet \
  dbt-core \
  dbt-duckdb \
  pandas \
  sqlfluff

# ---- Claude Code CLI ----
echo "Installerer Claude Code..."
npm install -g @anthropic-ai/claude-code@latest || {
  echo "MERK: Claude Code npm-installasjon feilet."
  echo "      Installer manuelt: npm install -g @anthropic-ai/claude-code"
}

# Sørg for at npm global bin er i PATH
NPM_BIN="$(npm prefix -g)/bin"
if [[ ":$PATH:" != *":$NPM_BIN:"* ]]; then
  echo "export PATH=\"\$PATH:$NPM_BIN\"" >> ~/.bashrc
  export PATH="$PATH:$NPM_BIN"
fi

# ---- dbt prosjekt ----
echo "Kjører dbt seed + run..."
dbt seed --quiet
dbt run --quiet

echo ""
echo "=== Miljøet er klart! ==="
echo ""
echo "  dbt debug          # verifiser at alt fungerer"
echo "  claude             # start Claude Code (krever ANTHROPIC_API_KEY)"
echo ""
