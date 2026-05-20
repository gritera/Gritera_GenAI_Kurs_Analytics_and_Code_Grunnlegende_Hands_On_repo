#!/usr/bin/env python3
"""
build_model_bim.py
==================

Genererer model.bim (TMSL JSON) ved siden av TMDL-filene, slik at PBIP-
prosjektet åpnes direkte i Power BI Desktop UTEN at brukeren må aktivere
TMDL-preview-funksjonen.

Kjør:
    python powerbi/build_model_bim.py

Output:
    powerbi/SalesAnalytics.SemanticModel/model.bim

model.bim er den kanoniske TMSL JSON-representasjonen av semantiske modeller.
Den dupliserer innholdet i .tmdl-filene, men brukes av eldre PBIP-mode.
"""
import json
import os
import sys
import hashlib

# Importer specs fra build_pbip.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_pbip import TABLES, RELATIONSHIPS, MEASURES, PROJECT_NAME, lineage_guid


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(THIS_DIR, f"{PROJECT_NAME}.SemanticModel")

DTYPE_TMSL = {
    "int64":    "int64",
    "double":   "double",
    "string":   "string",
    "dateTime": "dateTime",
    "boolean":  "boolean",
}


def build_m_partition(table_name, columns):
    """Power Query M-uttrykk som leser CSV med Table.TransformColumnTypes."""
    type_map = {
        "int64":    "Int64.Type",
        "double":   "type number",
        "string":   "type text",
        "dateTime": "type date",
        "boolean":  "type logical",
    }
    pairs = ", ".join(
        f'{{"{c[0]}", {type_map[c[1]]}}}' for c in columns
    )
    return [
        "let",
        f'    Source = Csv.Document(File.Contents(RepoPath & "/{table_name}.csv"), '
        f'[Delimiter=",", Columns={len(columns)}, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),',
        '    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),',
        f'    Typed = Table.TransformColumnTypes(Promoted, {{{pairs}}})',
        "in",
        "    Typed",
    ]


def column_json(name, dtype, summarize_by, format_string,
                is_hidden, sort_by, data_category):
    col = {
        "name": name,
        "dataType": DTYPE_TMSL[dtype],
        "sourceColumn": name,
        "summarizeBy": summarize_by,
        "lineageTag": lineage_guid(),
        "annotations": [
            {"name": "SummarizationSetBy", "value": "Automatic"}
        ],
    }
    if format_string:
        col["formatString"] = format_string
    if is_hidden:
        col["isHidden"] = True
    if sort_by:
        col["sortByColumn"] = sort_by
    if data_category:
        col["dataCategory"] = data_category
    if dtype == "dateTime":
        col["annotations"].append({
            "name": "UnderlyingDateTimeDataType", "value": "Date"
        })
    return col


def measure_json(name, expression, format_string, display_folder):
    m = {
        "name": name,
        "expression": expression,
        "lineageTag": lineage_guid(),
    }
    if format_string:
        m["formatString"] = format_string
    if display_folder:
        m["displayFolder"] = display_folder
    m["annotations"] = [
        {"name": "PBI_FormatHint", "value": '{"isGeneralNumber":true}'}
    ]
    return m


def table_json(table_name, spec):
    cols = spec["columns"]
    hidden = spec.get("hidden_columns", set())
    sort_map = spec.get("sort_columns", {})
    is_date_table = spec.get("is_date_table", False)

    # Columns
    table_cols = []
    for col in cols:
        name, dtype, summarize, fmt = col
        is_hidden = name in hidden
        sort_by = sort_map.get(name)
        data_cat = "Time" if (is_date_table and name == "date") else None
        table_cols.append(column_json(
            name, dtype, summarize, fmt, is_hidden, sort_by, data_cat
        ))

    # Measures
    table_measures = [
        measure_json(name, expr, fmt, folder)
        for tbl, name, expr, fmt, folder in MEASURES
        if tbl == table_name
    ]

    # Partition
    partition = {
        "name": table_name,
        "mode": "import",
        "source": {
            "type": "m",
            "expression": build_m_partition(table_name, cols),
        },
    }

    t = {
        "name": table_name,
        "lineageTag": lineage_guid(),
        "columns": table_cols,
        "partitions": [partition],
        "annotations": [{"name": "PBI_ResultType", "value": "Table"}],
    }
    if table_measures:
        t["measures"] = table_measures
    if is_date_table:
        t["dataCategory"] = "Time"
    return t


def build_model_bim():
    # Stable relationship IDs based on column signature
    rels = []
    for rel in RELATIONSHIPS:
        from_t, from_c, to_t, to_c, behaviour = rel
        sig = f"{from_t}.{from_c}=>{to_t}.{to_c}"
        h = hashlib.md5(sig.encode()).hexdigest()
        rid = f"{h[0:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"
        r = {
            "name": rid,
            "fromTable": from_t,
            "fromColumn": from_c,
            "toTable": to_t,
            "toColumn": to_c,
        }
        if behaviour == "bothDirections":
            r["crossFilteringBehavior"] = "bothDirections"
        rels.append(r)

    # Default to the absolute path on this user's machine.
    # User can edit via Transform data → Edit Parameters → RepoPath.
    default_repo_path = (
        "C:\\\\Users\\\\ToreLundell-Nygjelte\\\\OneDrive - Gritera\\\\"
        "Gritera_AI\\\\HandsOnAnalyticsCourse\\\\"
        "Gritera_GenAI_Kurs_Analytics_and_Code_Grunnlegende_Hands_On_repo\\\\"
        "powerbi\\\\data"
    )
    expressions = [{
        "name": "RepoPath",
        "kind": "m",
        "expression": (
            f'"{default_repo_path}" meta [IsParameterQuery=true, '
            f'Type="Text", IsParameterQueryRequired=true]'
        ),
        "lineageTag": lineage_guid(),
        "annotations": [{"name": "PBI_ResultType", "value": "Text"}],
    }]

    cultures = [{
        "name": "nb-NO",
        "linguisticMetadata": {
            "content": {"Version": "1.0.0", "Language": "nb-NO"},
            "contentType": "json"
        }
    }]

    bim = {
        "name": PROJECT_NAME,
        "compatibilityLevel": 1567,
        "model": {
            "culture": "nb-NO",
            "dataAccessOptions": {
                "legacyRedirects": True,
                "returnErrorValuesAsNull": True,
            },
            "defaultPowerBIDataSourceVersion": "powerBI_V3",
            "sourceQueryCulture": "nb-NO",
            "tables": [table_json(t, spec) for t, spec in TABLES.items()],
            "relationships": rels,
            "expressions": expressions,
            "cultures": cultures,
            "annotations": [
                {"name": "PBIDesktopVersion", "value": "2.131.1203.0 (24.12)"},
                {"name": "PBI_QueryOrder",
                 "value": json.dumps(list(TABLES.keys()))},
                {"name": "__PBI_TimeIntelligenceEnabled", "value": "0"},
                {"name": "TabularEditor_SerializeOptions",
                 "value": json.dumps({
                    "IgnoreInferredObjects": True,
                    "IgnoreInferredProperties": True,
                    "IgnoreTimestamps": True,
                    "SplitMultilineStrings": True,
                    "PrefixFilenames": False,
                    "LocalTranslations": False,
                    "LocalPerspectives": False,
                    "LocalRelationships": False,
                    "Levels": ["Data Sources", "Shared Expressions",
                               "Perspectives", "Translations", "Relationships",
                               "Roles", "Tables/Columns", "Tables/Hierarchies",
                               "Tables/Measures", "Tables/Partitions",
                               "Tables/Calculation Items"]
                 })},
            ],
        },
    }
    return bim


def main():
    bim = build_model_bim()
    out = os.path.join(DATASET_DIR, "model.bim")
    os.makedirs(DATASET_DIR, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(bim, f, indent=2, ensure_ascii=False)
    n_tables = len(bim["model"]["tables"])
    n_meas = sum(len(t.get("measures", [])) for t in bim["model"]["tables"])
    n_rels = len(bim["model"]["relationships"])
    print(f"Wrote {out}")
    print(f"  {n_tables} tables, {n_meas} measures, {n_rels} relationships")


if __name__ == "__main__":
    main()
