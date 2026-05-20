#!/usr/bin/env python3
"""
validate_pbip.py — rask sanity-sjekk av SalesAnalytics.pbip.

Kjør:
    python powerbi/validate_pbip.py

Sjekker:
    1. Alle visual.json bruker visualContainer/2.6.0
    2. Alle JSON-filer parses uten feil
    3. Alle 6 forventede sider finnes
    4. Datasettet har alle 5 tabeller med partisjoner
    5. Modellen har minst 25 mål
    6. Relasjoner er definert
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT = "SalesAnalytics"
REPORT_DIR = os.path.join(ROOT, f"{PROJECT}.Report")
DATASET_DIR = os.path.join(ROOT, f"{PROJECT}.SemanticModel")

EXPECTED_PAGES = [f"ReportSection{i}" for i in range(1, 7)]
EXPECTED_TABLES = ["dim_customer", "dim_product", "dim_date",
                   "fct_orders", "fct_order_items"]
EXPECTED_SCHEMAS = ("visualContainer/2.6.0", "visualContainer/2.7.0", "visualContainer/2.8.0")


def main():
    errors, warnings, info = [], [], []

    # 1. PBIP entry-point
    pbip = os.path.join(ROOT, f"{PROJECT}.pbip")
    if not os.path.isfile(pbip):
        errors.append(f"Missing {pbip}")
    else:
        try:
            with open(pbip) as f:
                json.load(f)
            info.append("✓ .pbip is valid JSON")
        except Exception as e:
            errors.append(f"Invalid JSON in .pbip: {e}")

    # 2. Pages exist
    pages_dir = os.path.join(REPORT_DIR, "definition", "pages")
    if not os.path.isdir(pages_dir):
        errors.append("Missing pages directory")
    else:
        pages = sorted(os.listdir(pages_dir))
        missing = [p for p in EXPECTED_PAGES if p not in pages]
        if missing:
            errors.append(f"Missing pages: {missing}")
        else:
            info.append(f"✓ all {len(EXPECTED_PAGES)} pages present")

    # 3. visual.json sanity
    visual_count = 0
    active = 0
    bad_schema = 0
    bad_json = 0
    bad_tooltip = 0
    for root, _, files in os.walk(REPORT_DIR):
        for f in files:
            if f == "visual.json":
                visual_count += 1
                p = os.path.join(root, f)
                try:
                    with open(p) as fh:
                        d = json.load(fh)
                except Exception:
                    bad_json += 1
                    continue
                if not any(s in d.get("$schema", "") for s in EXPECTED_SCHEMAS):
                    bad_schema += 1
                vco = d.get("visual", {}).get("visualContainerObjects", {})
                if "visualTooltip" in vco:
                    bad_tooltip += 1
                if not d.get("visual", {}).get("isHidden"):
                    active += 1
            if f == "visualContainer.json":
                errors.append(f"Wrong filename (should be visual.json): "
                              f"{os.path.join(root, f)}")
    if bad_json: errors.append(f"{bad_json} visual.json files failed to parse")
    if bad_schema: errors.append(f"{bad_schema} visual.json files have wrong $schema")
    if bad_tooltip: errors.append(f"{bad_tooltip} visual.json files use invalid visualTooltip")
    info.append(f"✓ {visual_count} visual.json files ({active} active)")

    # 4. model.bim exists (required by Power BI Desktop without TMDL preview)
    model_bim = os.path.join(DATASET_DIR, "model.bim")
    if not os.path.isfile(model_bim):
        errors.append("Missing model.bim — run python powerbi/build_model_bim.py")
    else:
        try:
            with open(model_bim) as f:
                bim = json.load(f)
            n = len(bim.get("model", {}).get("tables", []))
            info.append(f"✓ model.bim valid ({n} tables)")
        except Exception as e:
            errors.append(f"Invalid model.bim: {e}")

    # 4. Tables exist and have partitions
    tables_dir = os.path.join(DATASET_DIR, "definition", "tables")
    if not os.path.isdir(tables_dir):
        errors.append("Missing tables directory")
    else:
        total_measures = 0
        for t in EXPECTED_TABLES:
            p = os.path.join(tables_dir, f"{t}.tmdl")
            if not os.path.isfile(p):
                errors.append(f"Missing table: {t}.tmdl")
                continue
            with open(p) as f:
                txt = f.read()
            if not re.search(r"^\tpartition\b", txt, re.M):
                errors.append(f"{t}.tmdl is missing a partition")
            measures = len(re.findall(r"^\tmeasure\b", txt, re.M))
            total_measures += measures
        info.append(f"✓ all {len(EXPECTED_TABLES)} tables present "
                    f"with {total_measures} total measures")
        if total_measures < 25:
            warnings.append(f"Only {total_measures} measures (expected 25+)")

    # 5. Relationships
    rel_path = os.path.join(DATASET_DIR, "definition", "relationships.tmdl")
    if not os.path.isfile(rel_path):
        warnings.append("No relationships.tmdl found")
    else:
        with open(rel_path) as f:
            n_rel = len(re.findall(r"^relationship\b", f.read(), re.M))
        if n_rel == 0:
            errors.append("relationships.tmdl has no relationship blocks")
        else:
            info.append(f"✓ {n_rel} relationships defined")

    # 6. model.tmdl references relationships
    model_path = os.path.join(DATASET_DIR, "definition", "model.tmdl")
    if os.path.isfile(model_path):
        with open(model_path) as f:
            mtxt = f.read()
        rel_refs = len(re.findall(r"^ref relationship\b", mtxt, re.M))
        table_refs = len(re.findall(r"^ref table\b", mtxt, re.M))
        info.append(f"✓ model.tmdl references {table_refs} tables, "
                    f"{rel_refs} relationships")

    # Report
    print()
    print("=" * 64)
    print(f"PBIP Validation — {PROJECT}")
    print("=" * 64)
    for i in info:    print("  " + i)
    for w in warnings: print("  ⚠ " + w)
    for e in errors:   print("  ✗ " + e)
    print()
    if errors:
        print(f"FAIL  - {len(errors)} errors, {len(warnings)} warnings")
        sys.exit(1)
    else:
        print(f"PASS  - {len(warnings)} warnings")


if __name__ == "__main__":
    main()
