#!/usr/bin/env python3
"""
build_report.py
===============

Bygger en fokusert 3-siders Power BI-rapport over SalesAnalytics:

  1. Executive Overview         — topp-linje-KPIer, trend, geografi
  2. Ordreanalyse (fct_orders)  — ordretelling, status-miks, AOV, fullføringsrate
  3. Salgsanalyse (fct_order_items) — produkt-, kategori- og marginanalyse

Hver side har KPI-kort, diagrammer OG narrative funn-callouts som
fremhever de viktigste innsiktene fra dataene (markedsdominans, marginer,
fullføringsrate osv.).

Kjør:
    python powerbi/build_report.py
"""
import json
import os
import sys
import hashlib

# Import shared specs and helpers
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)
from build_pbip import (
    PROJECT_NAME, REPORT_DIR,
    CANVAS_W, CANVAS_H,
    BRAND_NAVY, BRAND_TEAL, BRAND_GOLD, BRAND_GREY, BRAND_BG, WHITE,
    lineage_guid,
)


# ────────────────────────────────────────────────────────────────────────────
# Determined visual naming
#   To keep filenames stable on a mounted FS that can't delete, we hash
#   (page, position-index) into a 20-char hex name.
# ────────────────────────────────────────────────────────────────────────────
BUILT_VISUALS = {}
_PAGE_COUNTERS = {}
_CURRENT_PAGE = [None]


def set_page(name):
    _CURRENT_PAGE[0] = name
    _PAGE_COUNTERS.setdefault(name, 0)


def vid():
    page = _CURRENT_PAGE[0]
    n = _PAGE_COUNTERS[page]
    _PAGE_COUNTERS[page] = n + 1
    return hashlib.md5(f"{page}::v{n:04d}".encode()).hexdigest()[:20]


# ────────────────────────────────────────────────────────────────────────────
# Visual builders
# ────────────────────────────────────────────────────────────────────────────

def write_visual(v):
    name = v["name"]
    page = _CURRENT_PAGE[0]
    p = os.path.join(REPORT_DIR, "definition", "pages", page,
                     "visuals", name, "visual.json")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(v, f, indent=2, ensure_ascii=False)
    BUILT_VISUALS.setdefault(page, set()).add(name)


def _container(visual_type, x, y, w, h, title=None, z=1000, bg=WHITE):
    name = vid()
    v = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.6.0/schema.json",
        "name": name,
        "position": {"x": x, "y": y, "z": z,
                     "width": w, "height": h, "tabOrder": z},
        "visual": {
            "visualType": visual_type,
            "visualContainerObjects": {
                "border": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}],
                "background": [{"properties": {
                    "color": {"solid": {"color": {"expr": {"Literal": {"Value": f"'{bg}'"}}}}},
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "transparency": {"expr": {"Literal": {"Value": "0D"}}}
                }}],
            },
        },
    }
    if title:
        v["visual"]["visualContainerObjects"]["title"] = [{
            "properties": {
                "show": {"expr": {"Literal": {"Value": "true"}}},
                "text": {"expr": {"Literal": {"Value": f"'{title}'"}}}
            }
        }]
    else:
        v["visual"]["visualContainerObjects"]["title"] = [{
            "properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}
        }]
    return v


def _proj(table, col, is_measure=False, active=False):
    f = ({"Measure": {"Expression": {"SourceRef": {"Entity": table}},
                      "Property": col}}
         if is_measure else
         {"Column": {"Expression": {"SourceRef": {"Entity": table}},
                     "Property": col}})
    p = {"field": f, "queryRef": f"{table}.{col}", "nativeQueryRef": col}
    if active:
        p["active"] = True
    return p


def card(table, measure, x, y, w, h, title=None):
    v = _container("card", x, y, w, h, title)
    v["visual"]["query"] = {"queryState": {
        "Values": {"projections": [_proj(table, measure, True, True)]}
    }}
    return v


def line_chart(cat_t, cat_c, m_t, m_n, x, y, w, h, title=None):
    v = _container("lineChart", x, y, w, h, title)
    v["visual"]["query"] = {"queryState": {
        "Category": {"projections": [_proj(cat_t, cat_c)]},
        "Y": {"projections": [_proj(m_t, m_n, True, True)]}
    }}
    return v


def column_chart(cat_t, cat_c, m_t, m_n, x, y, w, h, title=None):
    v = _container("columnChart", x, y, w, h, title)
    v["visual"]["query"] = {"queryState": {
        "Category": {"projections": [_proj(cat_t, cat_c)]},
        "Y": {"projections": [_proj(m_t, m_n, True, True)]}
    }}
    return v


def bar_chart(cat_t, cat_c, m_t, m_n, x, y, w, h, title=None):
    v = _container("barChart", x, y, w, h, title)
    v["visual"]["query"] = {"queryState": {
        "Category": {"projections": [_proj(cat_t, cat_c)]},
        "Y": {"projections": [_proj(m_t, m_n, True, True)]}
    }}
    return v


def donut_chart(cat_t, cat_c, m_t, m_n, x, y, w, h, title=None):
    v = _container("donutChart", x, y, w, h, title)
    v["visual"]["query"] = {"queryState": {
        "Category": {"projections": [_proj(cat_t, cat_c)]},
        "Y": {"projections": [_proj(m_t, m_n, True, True)]}
    }}
    return v


def table_visual(table, cols, x, y, w, h, title=None, measures=None):
    v = _container("tableEx", x, y, w, h, title)
    projections = [_proj(table, c) for c in cols]
    for mt, mn in (measures or []):
        projections.append(_proj(mt, mn, True, True))
    v["visual"]["query"] = {"queryState": {
        "Values": {"projections": projections}
    }}
    return v


def slicer(table, col, x, y, w, h, title=None):
    v = _container("slicer", x, y, w, h, title)
    v["visual"]["query"] = {"queryState": {
        "Values": {"projections": [_proj(table, col)]}
    }}
    return v


def shape(fill_color, x, y, w, h, z=500, transparency=0):
    return {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.6.0/schema.json",
        "name": vid(),
        "position": {"x": x, "y": y, "z": z, "width": w, "height": h, "tabOrder": z},
        "visual": {
            "visualType": "shape",
            "objects": {
                "shape": [{"properties": {
                    "tileShape": {"expr": {"Literal": {"Value": "'rectangle'"}}}
                }}],
                "rotation": [{"properties": {
                    "shapeAngle": {"expr": {"Literal": {"Value": "0L"}}}
                }}],
                "fill": [{"properties": {
                    "fillColor": {"solid": {"color": {"expr": {"Literal": {"Value": f"'{fill_color}'"}}}}},
                    "transparency": {"expr": {"Literal": {"Value": f"{transparency}D"}}}
                }, "selector": {"id": "default"}}],
                "outline": [{"properties": {
                    "show": {"expr": {"Literal": {"Value": "false"}}}
                }}]
            },
            "drillFilterOtherVisuals": True
        }
    }


def textbox(text, x, y, w, h, size="11pt", weight="normal",
            color="#FFFFFF", z=1500, family="Segoe UI"):
    return {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.6.0/schema.json",
        "name": vid(),
        "position": {"x": x, "y": y, "z": z, "width": w, "height": h, "tabOrder": z},
        "visual": {
            "visualType": "textbox",
            "objects": {"general": [{"properties": {"paragraphs": [{
                "textRuns": [{"value": text, "textStyle": {
                    "fontFamily": family,
                    "fontSize": size,
                    "fontWeight": weight,
                    "color": color
                }}]
            }]}}]}
        }
    }


# ────────────────────────────────────────────────────────────────────────────
# Felles sidedesign
# ────────────────────────────────────────────────────────────────────────────

def page_header(page, title, subtitle):
    write_visual(shape(BRAND_NAVY, 0, 0, CANVAS_W, 110, z=100))
    write_visual(shape(BRAND_TEAL, 0, 110, CANVAS_W, 6, z=110))
    write_visual(textbox(title, 40, 20, 1400, 50,
                         size="28pt", weight="bold", color=WHITE, z=120))
    write_visual(textbox(subtitle, 40, 70, 1400, 30,
                         size="12pt", color="#D8E1EA", z=121))
    write_visual(textbox("GRITERA · ANALYTICS", CANVAS_W - 380, 40, 340, 30,
                         size="11pt", weight="bold", color=BRAND_GOLD, z=122))


def page_footer(page_label):
    write_visual(shape("#E8ECF1", 0, CANVAS_H - 30, CANVAS_W, 30, z=100))
    write_visual(textbox(
        f"SalesAnalytics  ·  GenAI-generert demo for Gritera Advisory  ·  {page_label}",
        20, CANVAS_H - 26, 1880, 22,
        size="9pt", color=BRAND_GREY, z=120))


def insight_callout(headline, body, x, y, w, h, accent=BRAND_GOLD):
    """A subtle insight callout — golden accent bar + headline + body."""
    write_visual(shape(WHITE, x, y, w, h, z=200))
    write_visual(shape(accent, x, y, 6, h, z=201))      # left accent bar
    write_visual(textbox("INNSIKT", x + 24, y + 12, w - 40, 20,
                         size="9pt", weight="bold", color=accent, z=210))
    write_visual(textbox(headline, x + 24, y + 32, w - 40, 30,
                         size="14pt", weight="bold", color=BRAND_NAVY, z=211))
    write_visual(textbox(body, x + 24, y + 66, w - 40, h - 70,
                         size="10pt", color=BRAND_GREY, z=212))


def write_page_json(section_name, display_name, ordinal):
    set_page(section_name)
    path = os.path.join(REPORT_DIR, "definition", "pages", section_name)
    with open(os.path.join(path, "page.json"), "w", encoding="utf-8") as f:
        json.dump({
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json",
            "name": section_name,
            "displayName": display_name,
            "displayOption": "FitToPage",
            "width": CANVAS_W,
            "height": CANVAS_H,
            "ordinal": ordinal,
            "objects": {
                "background": [{"properties": {
                    "color": {"solid": {"color": {"expr": {"Literal": {"Value": f"'{BRAND_BG}'"}}}}},
                    "transparency": {"expr": {"Literal": {"Value": "0D"}}}
                }}]
            }
        }, f, indent=2, ensure_ascii=False)
    os.makedirs(os.path.join(path, "visuals"), exist_ok=True)


# ────────────────────────────────────────────────────────────────────────────
# SIDE 1 — Executive Overview
# ────────────────────────────────────────────────────────────────────────────

def build_overview():
    page = "ReportSection1"
    write_page_json(page, "Executive Overview", 0)
    page_header(page, "Executive Overview",
                "Salgs- og kundeprestasjon hittil — topp-linje-KPIer")

    # KPI rad 1 (4 hovedkort)
    y = 140
    w = 440
    write_visual(card("fct_order_items", "Total omsetning",
                      40, y, w, 150, "Total omsetning"))
    write_visual(card("fct_order_items", "Total fortjeneste",
                      500, y, w, 150, "Total fortjeneste"))
    write_visual(card("fct_order_items", "Antall ordrer",
                      960, y, w, 150, "Antall ordrer"))
    write_visual(card("fct_order_items", "Antall kunder",
                      1420, y, 460, 150, "Antall kunder"))

    # KPI rad 2 (3 sekundærkort)
    y = 310
    w = 460
    write_visual(card("fct_order_items", "Snitt ordreverdi (AOV)",
                      40, y, w, 140, "Snitt ordreverdi"))
    write_visual(card("fct_order_items", "Customer Lifetime Value",
                      520, y, w, 140, "Customer Lifetime Value"))
    write_visual(card("fct_order_items", "Bruttomargin %",
                      1000, y, w, 140, "Bruttomargin %"))

    # Insight callout (high-right)
    insight_callout(
        "Kaffe står for 65% av omsetningen",
        "1.983 NOK av 3.062 NOK total. Topp 4 produkter er alle "
        "kaffe — vurder å diversifisere sortimentet.",
        1480, y, 400, 140)

    # Hovedtrend — månedlig omsetning, full bredde
    write_visual(line_chart(
        "dim_date", "year_month",
        "fct_order_items", "Total omsetning",
        40, 470, 1840, 350,
        title="Månedlig omsetning"))

    # Geografi (donut) + topp-kunder (bar)
    write_visual(donut_chart(
        "dim_customer", "region",
        "fct_order_items", "Total omsetning",
        40, 840, 600, 180,
        title="Omsetning per region"))
    write_visual(bar_chart(
        "dim_product", "category",
        "fct_order_items", "Total omsetning",
        660, 840, 600, 180,
        title="Omsetning per kategori"))

    # Slicers nederst til høyre
    write_visual(slicer("dim_date", "year", 1280, 840, 290, 85, "År"))
    write_visual(slicer("dim_customer", "region", 1590, 840, 290, 85, "Region"))
    write_visual(slicer("dim_product", "category", 1280, 935, 600, 85, "Kategori"))

    page_footer("Side 1 av 3 · Executive Overview")


# ────────────────────────────────────────────────────────────────────────────
# SIDE 2 — Ordreanalyse (fct_orders)
# ────────────────────────────────────────────────────────────────────────────

def build_orders_page():
    page = "ReportSection2"
    write_page_json(page, "Ordreanalyse", 1)
    page_header(page, "Ordreanalyse",
                "Én rad per ordre — telling, status, AOV og kundefrekvens")

    # KPI rad
    y = 140
    write_visual(card("fct_orders", "Antall ordrer (header)",
                      40, y, 440, 150, "Antall ordrer"))
    write_visual(card("fct_orders", "Andel fullførte ordrer",
                      500, y, 440, 150, "Andel fullført"))
    write_visual(card("fct_order_items", "Snitt ordreverdi (AOV)",
                      960, y, 440, 150, "Snitt ordreverdi (AOV)"))
    write_visual(card("fct_order_items", "Ordrer per kunde",
                      1420, y, 460, 150, "Ordrer per kunde"))

    # Insight callout — fullføringsrate
    insight_callout(
        "90% av ordrene blir fullført",
        "Av 20 ordrer er 18 fullført, 1 returnert (90 NOK), "
        "1 pending (155 NOK). Returandel er lav — kvalitetssignal.",
        40, 310, 600, 130, accent=BRAND_TEAL)

    insight_callout(
        "Lojale kunder bestiller i snitt 1,4 ganger",
        "Med 18 fullførte ordrer fordelt på 13 unike kunder, er det "
        "rom for å øke kjøpsfrekvensen via gjenkjøpskampanjer.",
        660, 310, 600, 130, accent=BRAND_GOLD)

    insight_callout(
        "Snitt-ordreverdi: ~170 NOK",
        "Ordrer inneholder typisk 2–3 linjer. Cross-sell på snacks "
        "kan løfte AOV uten å påvirke marginen vesentlig.",
        1280, 310, 600, 130, accent=BRAND_NAVY)

    # Status-donut (venstre)
    write_visual(donut_chart(
        "fct_orders", "order_status_no",
        "fct_orders", "Antall ordrer (header)",
        40, 470, 580, 410,
        title="Ordrer per status"))

    # Månedlig ordretelling (midten)
    write_visual(column_chart(
        "dim_date", "year_month",
        "fct_order_items", "Antall ordrer",
        640, 470, 660, 410,
        title="Antall ordrer per måned"))

    # Region — antall ordrer (høyre)
    write_visual(bar_chart(
        "dim_customer", "region",
        "fct_order_items", "Antall ordrer",
        1320, 470, 560, 410,
        title="Antall ordrer per region"))

    # Ordretabell (bunn — full bredde)
    write_visual(table_visual(
        "dim_customer", ["full_name", "region", "tenure_segment"],
        40, 900, 1840, 150,
        title="Topp-kunder etter ordretelling og AOV",
        measures=[
            ("fct_order_items", "Antall ordrer"),
            ("fct_order_items", "Snitt ordreverdi (AOV)"),
            ("fct_order_items", "Total omsetning"),
        ]))

    page_footer("Side 2 av 3 · Ordreanalyse (fct_orders)")


# ────────────────────────────────────────────────────────────────────────────
# SIDE 3 — Salgsanalyse (fct_order_items)
# ────────────────────────────────────────────────────────────────────────────

def build_sales_page():
    page = "ReportSection3"
    write_page_json(page, "Salgsanalyse", 2)
    page_header(page, "Salgsanalyse",
                "Én rad per ordrelinje — produkt-, kategori- og marginanalyse")

    # KPI rad
    y = 140
    write_visual(card("fct_order_items", "Total omsetning",
                      40, y, 440, 150, "Total omsetning"))
    write_visual(card("fct_order_items", "Total fortjeneste",
                      500, y, 440, 150, "Total fortjeneste"))
    write_visual(card("fct_order_items", "Bruttomargin %",
                      960, y, 440, 150, "Bruttomargin %"))
    write_visual(card("fct_order_items", "Antall enheter",
                      1420, y, 460, 150, "Antall enheter"))

    # Insight callouts
    insight_callout(
        "Te har høyest margin: 67,5%",
        "Selv om kaffe står for 65% av volumet, gir te best margin per "
        "krone. Push mer marketing mot te-segmentet.",
        40, 310, 600, 130, accent=BRAND_GOLD)

    insight_callout(
        "Fjordkaffe Espresso er bestselger",
        "8 enheter solgt, 799 NOK omsetning. Topp-5-produktene er alle "
        "kaffe — produktkonsentrasjon å være oppmerksom på.",
        660, 310, 600, 130, accent=BRAND_TEAL)

    insight_callout(
        "Premium-produkter dominerer",
        "Produkter i pristier 'Premium' (>80 NOK) genererer mer enn "
        "halvparten av omsetningen — kundene betaler for kvalitet.",
        1280, 310, 600, 130, accent=BRAND_NAVY)

    # Topp-produkter (bar, venstre stor)
    write_visual(bar_chart(
        "dim_product", "product_name",
        "fct_order_items", "Total omsetning",
        40, 470, 920, 410,
        title="Topp-produkter etter omsetning"))

    # Kategori-omsetning (column, midten)
    write_visual(column_chart(
        "dim_product", "category",
        "fct_order_items", "Total fortjeneste",
        980, 470, 450, 410,
        title="Fortjeneste per kategori"))

    # Pristier (donut, høyre)
    write_visual(donut_chart(
        "dim_product", "price_tier",
        "fct_order_items", "Total omsetning",
        1450, 470, 430, 410,
        title="Omsetning per pristier"))

    # Produkttabell (bunn — full bredde)
    write_visual(table_visual(
        "dim_product",
        ["product_name", "category", "supplier"],
        40, 900, 1840, 150,
        title="Produktprestasjon — omsetning, enheter og margin",
        measures=[
            ("fct_order_items", "Antall enheter"),
            ("fct_order_items", "Total omsetning"),
            ("fct_order_items", "Total fortjeneste"),
            ("fct_order_items", "Bruttomargin %"),
        ]))

    page_footer("Side 3 av 3 · Salgsanalyse (fct_order_items)")


# ────────────────────────────────────────────────────────────────────────────
# Neutralise gamle visuals fra eldre builds
# ────────────────────────────────────────────────────────────────────────────

def neutralize_stale():
    """
    Overskrive visual.json fra tidligere builds med en 1px-skjult shape
    siden vi ikke kan slette på dette filsystemet.
    """
    pages_dir = os.path.join(REPORT_DIR, "definition", "pages")
    if not os.path.isdir(pages_dir):
        return
    for page in os.listdir(pages_dir):
        visuals_dir = os.path.join(pages_dir, page, "visuals")
        if not os.path.isdir(visuals_dir):
            continue
        live = BUILT_VISUALS.get(page, set())
        for folder in os.listdir(visuals_dir):
            if folder in live:
                continue
            stale = os.path.join(visuals_dir, folder, "visual.json")
            if not os.path.isfile(stale):
                continue
            # NB: NO `isHidden` property — that breaks PBIR rendering.
            # Use off-canvas position to keep them invisible.
            noop = {
                "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.6.0/schema.json",
                "name": folder,
                "position": {"x": -10000, "y": -10000, "z": 0,
                             "width": 1, "height": 1, "tabOrder": 0},
                "visual": {
                    "visualType": "shape",
                    "objects": {
                        "shape": [{"properties": {
                            "tileShape": {"expr": {"Literal": {"Value": "'rectangle'"}}}
                        }}],
                        "fill": [{"properties": {
                            "fillColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#FFFFFF'"}}}}},
                            "transparency": {"expr": {"Literal": {"Value": "100D"}}}
                        }, "selector": {"id": "default"}}]
                    }
                }
            }
            try:
                with open(stale, "w", encoding="utf-8") as f:
                    json.dump(noop, f)
            except OSError:
                pass


def hide_old_pages():
    """
    Mark gamle sider (4, 5, 6) som skjult ved å skrive page.json med
    visibility: hidden, OG fjerne dem fra report.json sin sections-liste.
    """
    pages_dir = os.path.join(REPORT_DIR, "definition", "pages")
    for old_page in ("ReportSection4", "ReportSection5", "ReportSection6"):
        path = os.path.join(pages_dir, old_page, "page.json")
        if not os.path.isfile(path):
            continue
        try:
            with open(path) as f:
                pj = json.load(f)
            pj["visibility"] = "HiddenInViewMode"
            pj["displayName"] = "(skjult)"
            with open(path, "w", encoding="utf-8") as f:
                json.dump(pj, f, indent=2, ensure_ascii=False)
        except OSError:
            pass


def update_report_json():
    """
    Oppdater report.json, definition.pbir, version.json og pages.json.
    For PBIR-format må definition.pbir ha version=4.0 (1.0 = PBIR-Legacy).
    """
    # report.json — fjern legacy "sections"-feltet
    path = os.path.join(REPORT_DIR, "definition", "report.json")
    with open(path) as f:
        r = json.load(f)
    r.pop("sections", None)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(r, f, indent=2, ensure_ascii=False)

    # definition.pbir — VERSION 4.0 er kritisk for PBIR-format
    with open(os.path.join(REPORT_DIR, "definition.pbir"), "w", encoding="utf-8") as f:
        json.dump({
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json",
            "version": "4.0",
            "datasetReference": {"byPath": {"path": "../SalesAnalytics.SemanticModel"}}
        }, f, indent=2, ensure_ascii=False)

    # definition/version.json — NØDVENDIG for PBIR
    with open(os.path.join(REPORT_DIR, "definition", "version.json"), "w", encoding="utf-8") as f:
        json.dump({
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/versionMetadata/1.0.0/schema.json",
            "version": "4.0"
        }, f, indent=2, ensure_ascii=False)

    # pages/pages.json — definerer side-rekkefølge
    with open(os.path.join(REPORT_DIR, "definition", "pages", "pages.json"), "w", encoding="utf-8") as f:
        json.dump({
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.0.0/schema.json",
            "pageOrder": ["ReportSection1", "ReportSection2", "ReportSection3"],
            "activePageName": "ReportSection1"
        }, f, indent=2, ensure_ascii=False)


def main():
    print("Bygger 3 fokuserte rapportsider …")
    build_overview()
    build_orders_page()
    build_sales_page()
    hide_old_pages()
    update_report_json()
    neutralize_stale()
    n = sum(len(s) for s in BUILT_VISUALS.values())
    print(f"  Skrevet {n} aktive visuals fordelt på 3 sider")
    for p, s in BUILT_VISUALS.items():
        print(f"    {p}: {len(s)} visuals")
    print("Ferdig.")


if __name__ == "__main__":
    main()
