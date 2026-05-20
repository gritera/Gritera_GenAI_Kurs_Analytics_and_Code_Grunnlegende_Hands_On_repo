#!/usr/bin/env python3
"""
build_polished_report.py — Bygger en polert 3-siders Power BI-rapport.

Tre sider:
  1. Executive Overview            — topp-linje-KPIer + trend + geografi
  2. Ordreanalyse (fct_orders)     — ordretelling, status, kunde
  3. Salgsanalyse (fct_order_items) — produkt, kategori, margin

Layered gradient background, hero KPI cards med farger-bånd, line/donut/bar charts,
narrative insight callouts. Korte folder-navn (v###) for å holde Windows-stier
under 260 tegn.
"""
import json, os, hashlib

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_DIR = os.path.join(THIS_DIR, "SalesAnalytics.Report")
PAGES_DIR = os.path.join(REPORT_DIR, "definition", "pages")
DATASET_NAME = "SalesAnalytics"

# Brand palette
NAVY      = "#0B2A4A"
TEAL      = "#1F8FA3"
GOLD      = "#E0A458"
ROSE      = "#D9534F"
GREEN     = "#4FB286"
GREY      = "#5B6770"
LIGHT_BG  = "#F5F7FA"
PANEL_BG  = "#FFFFFF"
WHITE     = "#FFFFFF"
DARK_TEXT = "#0B2A4A"
MUTED     = "#6E7C8A"

CANVAS_W, CANVAS_H = 1920, 1080

# Per-page deterministic visual ID counter (short!)
_PAGE = [None]
_COUNT = {}
BUILT = {}

def set_page(name):
    _PAGE[0] = name
    _COUNT.setdefault(name, 0)
    BUILT.setdefault(name, set())

def vid():
    page = _PAGE[0]
    n = _COUNT[page]
    _COUNT[page] = n + 1
    # 6-char name: p{1-3}{3-hex-counter}_{1-char}
    short = "v" + hashlib.md5(f"{page}::{n:04d}".encode()).hexdigest()[:5]
    return short


# ────────────────────────────────────────────────────────────────────────────
# Visual builders — all return a dict ready to write to visual.json
# ────────────────────────────────────────────────────────────────────────────

def write_visual(v):
    page = _PAGE[0]
    name = v["name"]
    path = os.path.join(PAGES_DIR, page, "visuals", name, "visual.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(v, f, indent=2, ensure_ascii=False)
    BUILT[page].add(name)


def proj(table, col_or_measure, is_measure=False, active=False):
    f = ({"Measure": {"Expression": {"SourceRef": {"Entity": table}}, "Property": col_or_measure}}
         if is_measure else
         {"Column": {"Expression": {"SourceRef": {"Entity": table}}, "Property": col_or_measure}})
    qref = f"{DATASET_NAME}.{col_or_measure}" if is_measure else f"{table}.{col_or_measure}"
    p = {"field": f, "queryRef": qref, "nativeQueryRef": col_or_measure}
    if active:
        p["active"] = True
    return p


def base_visual(visual_type, x, y, w, h, title=None):
    name = vid()
    v = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.8.0/schema.json",
        "name": name,
        "position": {"x": x, "y": y, "z": 1000, "height": h, "width": w, "tabOrder": 1000},
        "visual": {"visualType": visual_type, "visualContainerObjects": {}}
    }
    if title:
        v["visual"]["visualContainerObjects"]["title"] = [{
            "properties": {
                "show": {"expr": {"Literal": {"Value": "true"}}},
                "text": {"expr": {"Literal": {"Value": f"'{title}'"}}}
            }
        }]
    return v


def card(table, measure, x, y, w, h, title=None):
    v = base_visual("card", x, y, w, h, title)
    v["visual"]["query"] = {"queryState": {
        "Values": {"projections": [proj(table, measure, True, True)]}
    }}
    return v


def line_chart(cat_t, cat_c, m_t, m_n, x, y, w, h, title=None):
    v = base_visual("lineChart", x, y, w, h, title)
    v["visual"]["query"] = {"queryState": {
        "Category": {"projections": [proj(cat_t, cat_c)]},
        "Y": {"projections": [proj(m_t, m_n, True, True)]}
    }}
    return v


def column_chart(cat_t, cat_c, m_t, m_n, x, y, w, h, title=None):
    v = base_visual("columnChart", x, y, w, h, title)
    v["visual"]["query"] = {"queryState": {
        "Category": {"projections": [proj(cat_t, cat_c)]},
        "Y": {"projections": [proj(m_t, m_n, True, True)]}
    }}
    return v


def bar_chart(cat_t, cat_c, m_t, m_n, x, y, w, h, title=None):
    v = base_visual("barChart", x, y, w, h, title)
    v["visual"]["query"] = {"queryState": {
        "Category": {"projections": [proj(cat_t, cat_c)]},
        "Y": {"projections": [proj(m_t, m_n, True, True)]}
    }}
    return v


def donut_chart(cat_t, cat_c, m_t, m_n, x, y, w, h, title=None):
    v = base_visual("donutChart", x, y, w, h, title)
    v["visual"]["query"] = {"queryState": {
        "Category": {"projections": [proj(cat_t, cat_c)]},
        "Y": {"projections": [proj(m_t, m_n, True, True)]}
    }}
    return v


def table_visual(table, cols, x, y, w, h, title=None, measures=None):
    v = base_visual("tableEx", x, y, w, h, title)
    projections = [proj(table, c) for c in cols]
    for mt, mn in (measures or []):
        projections.append(proj(mt, mn, True, True))
    v["visual"]["query"] = {"queryState": {
        "Values": {"projections": projections}
    }}
    return v


def slicer(table, col, x, y, w, h, title=None):
    v = base_visual("slicer", x, y, w, h, title)
    v["visual"]["query"] = {"queryState": {
        "Values": {"projections": [proj(table, col)]}
    }}
    return v


def shape(fill_color, x, y, w, h, z=500, transparency=0):
    return {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.8.0/schema.json",
        "name": vid(),
        "position": {"x": x, "y": y, "z": z, "height": h, "width": w, "tabOrder": z},
        "visual": {
            "visualType": "shape",
            "objects": {
                "shape": [{"properties": {
                    "tileShape": {"expr": {"Literal": {"Value": "'rectangle'"}}}
                }}],
                "fill": [{"properties": {
                    "fillColor": {"solid": {"color": {"expr": {"Literal": {"Value": f"'{fill_color}'"}}}}},
                    "transparency": {"expr": {"Literal": {"Value": f"{transparency}D"}}}
                }, "selector": {"id": "default"}}]
            }
        }
    }


def textbox(text, x, y, w, h, size="12pt", weight="normal", color=DARK_TEXT,
            z=1500, family="Segoe UI"):
    return {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.8.0/schema.json",
        "name": vid(),
        "position": {"x": x, "y": y, "z": z, "height": h, "width": w, "tabOrder": z},
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
# Layout primitives
# ────────────────────────────────────────────────────────────────────────────

def gradient_background():
    """Layered shapes give an illusion of a gradient — navy top, teal middle."""
    # Light page bg
    write_visual(shape(LIGHT_BG, 0, 0, CANVAS_W, CANVAS_H, z=10))
    # Navy header band
    write_visual(shape(NAVY, 0, 0, CANVAS_W, 130, z=100))
    # Teal accent gradient band
    write_visual(shape(TEAL, 0, 130, CANVAS_W, 8, z=110))
    # Subtle teal panel under header
    write_visual(shape("#1B435E", 0, 138, CANVAS_W, 14, z=110, transparency=50))


def page_header(title, subtitle):
    write_visual(textbox(title, 50, 25, 1500, 55,
                         size="32pt", weight="bold", color=WHITE, z=200))
    write_visual(textbox(subtitle, 50, 82, 1500, 30,
                         size="13pt", color="#A8C5DC", z=201))
    write_visual(textbox("GRITERA · ANALYTICS", CANVAS_W - 380, 45, 340, 30,
                         size="12pt", weight="bold", color=GOLD, z=202))


def kpi_card(table, measure, x, y, w, h, label, accent=TEAL, title_in_visual=None):
    """A polished KPI card: accent stripe + white panel + card visual.
    Layout: stripe (8px) → label band (40px) → value area (h-48px)."""
    # White panel background
    write_visual(shape(PANEL_BG, x, y, w, h, z=400))
    # Top accent stripe — taller for visibility
    write_visual(shape(accent, x, y, w, 8, z=410))
    # Label band: positioned with more room
    write_visual(textbox(label.upper(), x + 24, y + 18, w - 48, 28,
                         size="10pt", weight="bold", color=MUTED, z=420))
    # The card value visual (positioned below the label, with padding)
    c = card(table, measure, x + 14, y + 52, w - 28, h - 64,
             title=None)
    # Override styling — hide native title, transparent background
    c["visual"]["visualContainerObjects"] = {
        "title": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}],
        "background": [{"properties": {
            "color": {"solid": {"color": {"expr": {"Literal": {"Value": f"'{PANEL_BG}'"}}}}},
            "show": {"expr": {"Literal": {"Value": "true"}}},
            "transparency": {"expr": {"Literal": {"Value": "100D"}}}
        }}],
    }
    write_visual(c)


def chart_panel(visual_factory, x, y, w, h, title):
    """Wrap a chart in a white panel for consistent styling.
    Layout: title band (50px) → chart area (h-58px)."""
    write_visual(shape(PANEL_BG, x, y, w, h, z=400))
    # Title bar with proper spacing
    write_visual(textbox(title.upper(), x + 24, y + 18, w - 48, 28,
                         size="11pt", weight="bold", color=NAVY, z=420))
    # The chart itself, padded inside the panel
    v = visual_factory(x + 14, y + 56, w - 28, h - 68)
    v["visual"]["visualContainerObjects"]["title"] = [{
        "properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}
    }]
    v["visual"]["visualContainerObjects"]["background"] = [{"properties": {
        "color": {"solid": {"color": {"expr": {"Literal": {"Value": f"'{PANEL_BG}'"}}}}},
        "show": {"expr": {"Literal": {"Value": "true"}}},
        "transparency": {"expr": {"Literal": {"Value": "100D"}}}
    }}]
    write_visual(v)


def insight_callout(headline, body, x, y, w, h, accent=GOLD):
    write_visual(shape(PANEL_BG, x, y, w, h, z=400))
    write_visual(shape(accent, x, y, 6, h, z=410))
    write_visual(textbox("INNSIKT", x + 24, y + 12, w - 40, 18,
                         size="8pt", weight="bold", color=accent, z=420))
    write_visual(textbox(headline, x + 24, y + 30, w - 40, 38,
                         size="14pt", weight="bold", color=NAVY, z=421))
    write_visual(textbox(body, x + 24, y + 70, w - 40, h - 78,
                         size="10pt", color=GREY, z=422))


def slicer_panel(table, col, x, y, w, h, label):
    write_visual(shape(PANEL_BG, x, y, w, h, z=400))
    write_visual(textbox(label.upper(), x + 20, y + 14, w - 40, 22,
                         size="10pt", weight="bold", color=MUTED, z=420))
    s = slicer(table, col, x + 14, y + 44, w - 28, h - 56)
    s["visual"]["visualContainerObjects"]["title"] = [{
        "properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}
    }]
    write_visual(s)


def page_footer(label):
    write_visual(shape("#1B2E47", 0, CANVAS_H - 26, CANVAS_W, 26, z=100))
    write_visual(textbox(
        f"SalesAnalytics  ·  GenAI-generert demo for Gritera Advisory  ·  {label}",
        24, CANVAS_H - 22, 1872, 20,
        size="9pt", color="#A8C5DC", z=200))


# ────────────────────────────────────────────────────────────────────────────
# SIDE 1 — Executive Overview
# ────────────────────────────────────────────────────────────────────────────

def page_executive():
    set_page("ReportSection1")
    gradient_background()
    page_header("Executive Overview",
                "Salgs- og kundeprestasjon  ·  topp-linje-KPIer og hovedtrender")

    # Hero KPI cards (top row, 4 cards) — Y=170, height=160
    kpi_card("fct_order_items", "Total omsetning", 40, 170, 440, 170,
             "Total omsetning", accent=TEAL)
    kpi_card("fct_order_items", "Total fortjeneste", 500, 170, 440, 170,
             "Total fortjeneste", accent=GREEN)
    kpi_card("fct_order_items", "Antall ordrer", 960, 170, 440, 170,
             "Antall ordrer", accent=GOLD)
    kpi_card("fct_order_items", "Antall kunder", 1420, 170, 460, 170,
             "Antall kunder", accent=NAVY)

    # Secondary KPIs (3 across, narrower)
    kpi_card("fct_order_items", "Snitt ordreverdi (AOV)", 40, 360, 440, 130,
             "Snitt ordreverdi (AOV)", accent=TEAL)
    kpi_card("fct_order_items", "Customer Lifetime Value", 500, 360, 440, 130,
             "Customer Lifetime Value", accent=GREEN)
    kpi_card("fct_order_items", "Bruttomargin %", 960, 360, 440, 130,
             "Bruttomargin %", accent=GOLD)

    # Insight callout (right of secondary KPIs)
    insight_callout(
        "Kaffe står for 65% av omsetningen",
        "Topp 4 produkter er alle kaffe. Vurder å diversifisere sortimentet "
        "eller heve marginen på te (67,5%).",
        1420, 360, 460, 130, accent=GOLD)

    # Main monthly trend (line, full width)
    chart_panel(
        lambda x, y, w, h: line_chart("dim_date", "year_month",
                                       "fct_order_items", "Total omsetning",
                                       x, y, w, h),
        40, 510, 1230, 380,
        "Månedlig omsetning")

    # Category donut (right column)
    chart_panel(
        lambda x, y, w, h: donut_chart("dim_product", "category",
                                        "fct_order_items", "Total omsetning",
                                        x, y, w, h),
        1290, 510, 590, 380,
        "Omsetning per kategori")

    # Slicer row at the bottom
    slicer_panel("dim_date", "year",       40,   910, 440, 130, "År")
    slicer_panel("dim_customer", "region", 500,  910, 440, 130, "Region")
    slicer_panel("dim_product", "category", 960, 910, 440, 130, "Kategori")
    slicer_panel("dim_customer", "tenure_segment", 1420, 910, 460, 130, "Lojalitetssegment")

    page_footer("Side 1 av 3 · Executive Overview")


# ────────────────────────────────────────────────────────────────────────────
# SIDE 2 — Ordreanalyse (fct_orders)
# ────────────────────────────────────────────────────────────────────────────

def page_orders():
    set_page("ReportSection2")
    gradient_background()
    page_header("Ordreanalyse",
                "Faktatabell: fct_orders  ·  én rad per ordre")

    # KPI row
    kpi_card("fct_orders", "Antall ordrer (header)", 40, 170, 440, 170,
             "Antall ordrer", accent=TEAL)
    kpi_card("fct_orders", "Andel fullførte ordrer", 500, 170, 440, 170,
             "Andel fullført", accent=GREEN)
    kpi_card("fct_order_items", "Snitt ordreverdi (AOV)", 960, 170, 440, 170,
             "Snitt ordreverdi (AOV)", accent=GOLD)
    kpi_card("fct_order_items", "Ordrer per kunde", 1420, 170, 460, 170,
             "Ordrer per kunde", accent=NAVY)

    # Insight callouts (3 across)
    insight_callout(
        "90% av ordrene fullføres",
        "18 av 20 fullført, 1 returnert (90 NOK), 1 pending (155 NOK). "
        "Returandelen er meget lav — kvalitetssignal.",
        40, 360, 600, 130, accent=GREEN)
    insight_callout(
        "13 unike kunder, 18 fullførte ordrer",
        "Gjennomsnittlig 1,4 ordrer per kunde. Rom for å øke kjøpsfrekvens "
        "gjennom gjenkjøpskampanjer.",
        660, 360, 600, 130, accent=GOLD)
    insight_callout(
        "Snitt-ordreverdi: ~170 NOK",
        "Ordrer inneholder typisk 2–3 linjer. Cross-sell på snacks kan løfte "
        "AOV uten å påvirke marginen vesentlig.",
        1280, 360, 600, 130, accent=NAVY)

    # Charts row
    chart_panel(
        lambda x, y, w, h: donut_chart("fct_orders", "order_status_no",
                                        "fct_orders", "Antall ordrer (header)",
                                        x, y, w, h),
        40, 510, 600, 380,
        "Ordrer per status")

    chart_panel(
        lambda x, y, w, h: column_chart("dim_date", "year_month",
                                         "fct_order_items", "Antall ordrer",
                                         x, y, w, h),
        660, 510, 620, 380,
        "Antall ordrer per måned")

    chart_panel(
        lambda x, y, w, h: bar_chart("dim_customer", "region",
                                      "fct_order_items", "Antall ordrer",
                                      x, y, w, h),
        1300, 510, 580, 380,
        "Antall ordrer per region")

    # Customer table (full width)
    chart_panel(
        lambda x, y, w, h: table_visual("dim_customer",
            ["full_name", "region", "tenure_segment"],
            x, y, w, h,
            measures=[
                ("fct_order_items", "Antall ordrer"),
                ("fct_order_items", "Snitt ordreverdi (AOV)"),
                ("fct_order_items", "Total omsetning"),
            ]),
        40, 910, 1840, 130,
        "Topp-kunder etter omsetning og frekvens")

    page_footer("Side 2 av 3 · Ordreanalyse (fct_orders)")


# ────────────────────────────────────────────────────────────────────────────
# SIDE 3 — Salgsanalyse (fct_order_items)
# ────────────────────────────────────────────────────────────────────────────

def page_sales():
    set_page("ReportSection3")
    gradient_background()
    page_header("Salgsanalyse",
                "Faktatabell: fct_order_items  ·  én rad per ordrelinje")

    # KPI row
    kpi_card("fct_order_items", "Total omsetning", 40, 170, 440, 170,
             "Total omsetning", accent=TEAL)
    kpi_card("fct_order_items", "Total fortjeneste", 500, 170, 440, 170,
             "Total fortjeneste", accent=GREEN)
    kpi_card("fct_order_items", "Bruttomargin %", 960, 170, 440, 170,
             "Bruttomargin %", accent=GOLD)
    kpi_card("fct_order_items", "Antall enheter", 1420, 170, 460, 170,
             "Antall enheter", accent=NAVY)

    # Insight callouts
    insight_callout(
        "Te har høyest margin: 67,5%",
        "Selv om kaffe står for 65% av volumet, gir te best margin per krone. "
        "Push markedsføring mot te-segmentet.",
        40, 360, 600, 130, accent=GOLD)
    insight_callout(
        "Fjordkaffe Espresso er bestselger",
        "8 enheter, 799 NOK omsetning. Topp 5 produkter er alle kaffe — "
        "produktkonsentrasjon å være oppmerksom på.",
        660, 360, 600, 130, accent=TEAL)
    insight_callout(
        "Premium-produkter dominerer",
        "Produkter med pris >80 NOK genererer mer enn halvparten av "
        "omsetningen — kundene betaler for kvalitet.",
        1280, 360, 600, 130, accent=NAVY)

    # Charts
    chart_panel(
        lambda x, y, w, h: bar_chart("dim_product", "product_name",
                                      "fct_order_items", "Total omsetning",
                                      x, y, w, h),
        40, 510, 920, 380,
        "Topp-produkter etter omsetning")

    chart_panel(
        lambda x, y, w, h: column_chart("dim_product", "category",
                                         "fct_order_items", "Total fortjeneste",
                                         x, y, w, h),
        980, 510, 450, 380,
        "Fortjeneste per kategori")

    chart_panel(
        lambda x, y, w, h: donut_chart("dim_product", "price_tier",
                                        "fct_order_items", "Total omsetning",
                                        x, y, w, h),
        1450, 510, 430, 380,
        "Omsetning per pristier")

    # Product detail table (full width)
    chart_panel(
        lambda x, y, w, h: table_visual("dim_product",
            ["product_name", "category", "supplier"],
            x, y, w, h,
            measures=[
                ("fct_order_items", "Antall enheter"),
                ("fct_order_items", "Total omsetning"),
                ("fct_order_items", "Total fortjeneste"),
                ("fct_order_items", "Bruttomargin %"),
            ]),
        40, 910, 1840, 130,
        "Produktprestasjon — omsetning, enheter og margin")

    page_footer("Side 3 av 3 · Salgsanalyse (fct_order_items)")


# ────────────────────────────────────────────────────────────────────────────
# Page writers
# ────────────────────────────────────────────────────────────────────────────

def write_page_json(section_name, display_name):
    path = os.path.join(PAGES_DIR, section_name, "page.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json",
            "name": section_name,
            "displayName": display_name,
            "displayOption": "FitToPage",
            "height": CANVAS_H,
            "width": CANVAS_W
        }, f, indent=2, ensure_ascii=False)


def update_pages_json():
    pages_json = os.path.join(PAGES_DIR, "pages.json")
    with open(pages_json, "w", encoding="utf-8") as f:
        json.dump({
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.0.0/schema.json",
            "pageOrder": ["ReportSection1", "ReportSection2", "ReportSection3"],
            "activePageName": "ReportSection1"
        }, f, indent=2, ensure_ascii=False)


def neutralize_stale():
    """Overwrite any visual.json NOT in BUILT[page] with a hidden off-canvas card."""
    for page in os.listdir(PAGES_DIR):
        vd = os.path.join(PAGES_DIR, page, "visuals")
        if not os.path.isdir(vd):
            continue
        live = BUILT.get(page, set())
        for folder in os.listdir(vd):
            if folder in live:
                continue
            vp = os.path.join(vd, folder, "visual.json")
            if not os.path.isfile(vp):
                continue
            noop = {
                "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.8.0/schema.json",
                "name": folder,
                "position": {"x": -10000, "y": -10000, "z": 0,
                             "height": 1, "width": 1, "tabOrder": 0},
                "visual": {
                    "visualType": "card",
                    "query": {"queryState": {"Values": {"projections": [
                        proj("fct_order_items", "Antall ordrelinjer", True, True)
                    ]}}},
                    "visualContainerObjects": {
                        "title": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}]
                    }
                }
            }
            with open(vp, "w", encoding="utf-8") as f:
                json.dump(noop, f, indent=2, ensure_ascii=False)


def main():
    print("Bygger polert 3-siders rapport …")

    # Write page.json for the three active pages
    write_page_json("ReportSection1", "Executive Overview")
    write_page_json("ReportSection2", "Ordreanalyse")
    write_page_json("ReportSection3", "Salgsanalyse")

    # Build each page
    page_executive()
    page_orders()
    page_sales()

    update_pages_json()
    neutralize_stale()

    total = sum(len(s) for s in BUILT.values())
    print(f"\n✓ Skrevet {total} visuals fordelt på 3 sider:")
    for page, visuals in BUILT.items():
        print(f"    {page}: {len(visuals)} visuals")
    print("\nÅpne powerbi/SalesAnalytics.pbip i Power BI Desktop.")


if __name__ == "__main__":
    main()
