#!/usr/bin/env python3
"""
export_marts_to_csv.py
======================

Eksporterer dimensjonelle marter fra `kurs.duckdb` til `powerbi/data/`
slik at Power BI-prosjektet kan lese dem som CSV-import.

Forutsetter at `dbt seed` og `dbt run --select staging tag:core` er kjørt.

Kjør:
    python powerbi/export_marts_to_csv.py
"""
import os
import sys

try:
    import duckdb
except ImportError:
    sys.exit("Kjør først: pip install duckdb")

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(THIS_DIR)
DUCKDB_PATH = os.path.join(REPO_ROOT, "kurs.duckdb")
OUT_DIR = os.path.join(THIS_DIR, "data")

TABLES = ["dim_customer", "dim_product", "dim_date", "fct_orders", "fct_order_items"]


def main():
    if not os.path.isfile(DUCKDB_PATH):
        sys.exit(f"Fant ikke {DUCKDB_PATH}. Kjør først:\n"
                 f"    dbt seed && dbt run --select staging tag:core")
    os.makedirs(OUT_DIR, exist_ok=True)
    con = duckdb.connect(DUCKDB_PATH, read_only=True)
    for t in TABLES:
        out = os.path.join(OUT_DIR, f"{t}.csv")
        con.execute(f"COPY main.{t} TO '{out}' (HEADER, DELIMITER ',')")
        n = con.execute(f"SELECT COUNT(*) FROM main.{t}").fetchone()[0]
        print(f"  {t:20s} → {n:>5d} rader → {out}")
    print(f"\nFerdig. Kjør deretter: python powerbi/build_pbip.py")


if __name__ == "__main__":
    main()
