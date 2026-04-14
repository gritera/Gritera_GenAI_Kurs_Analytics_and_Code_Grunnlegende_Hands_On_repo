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
npm install -g @anthropic-ai/claude-code@latest 2>/dev/null || {
  echo "MERK: Claude Code npm-installasjon feilet."
  echo "      Du kan installere manuelt: npm install -g @anthropic-ai/claude-code"
  echo "      Eller følg instruksjonene på https://docs.anthropic.com/en/docs/claude-code"
}

# ---- dbt prosjekt ----
echo "Kjører dbt seed + run..."
dbt seed --quiet
dbt run --quiet

echo ""
echo "=== Miljøet er klart! ==="
echo ""
echo "Neste steg:"
echo "  dbt debug          # verifiser at alt fungerer"
echo "  claude             # start Claude Code (krever ANTHROPIC_API_KEY)"
echo ""
