# Power BI Development Standards

> This document defines the compliance rules that all Power BI projects in this repository
> must follow. Automated compliance routines (see `.claude/routines/compliance-review.md`)
> validate every project against these rules on every push and on a nightly schedule.
>
> **How to read this document**: Each section contains numbered rules (e.g. `R-COLOR-01`).
> The compliance agent checks every rule individually. Violations are reported with the
> rule ID, the file path, the offending value, and a suggested fix.
>
> **Scope**: All `.pbip` projects under `/reports/`. Legacy `.pbix` files are out of scope
> and should be migrated to PBIP before being added to this repo.

---

## 1. Repository structure

### R-REPO-01: PBIP format only

All Power BI projects MUST be committed as PBIP (Power BI Project) format.
Binary `.pbix` files are not permitted in the repo.

- ✅ `/reports/sales-dashboard/sales-dashboard.pbip`
- ❌ `/reports/sales-dashboard.pbix`

### R-REPO-02: Folder layout

Each project lives in its own folder under `/reports/` and follows this layout:

```
/reports/<project-name>/
├── <project-name>.pbip
├── <project-name>.Report/
│   ├── definition.pbir
│   ├── definition/
│   │   ├── pages/
│   │   ├── report.json
│   │   └── reportExtensions.json
│   └── StaticResources/
│       └── SharedResources/
│           └── BaseThemes/
│               └── gritera.json
├── <project-name>.SemanticModel/
│   ├── definition.pbism
│   └── definition/
│       ├── model.tmdl
│       ├── tables/
│       └── relationships.tmdl
└── README.md
```

### R-REPO-03: Project naming

Project folder names MUST be `kebab-case`, lowercase, ASCII only, no spaces.

- ✅ `sales-dashboard`, `customer-360`, `kpi-overview`
- ❌ `Sales Dashboard`, `salesDashboard`, `kunde_360`, `KPI Overview`

### R-REPO-04: README required

Every project folder MUST contain a `README.md` at its root with these sections:
- **Purpose** — one paragraph describing what the report is for
- **Data sources** — list of source systems and connection types
- **Owner** — name and email of the responsible analyst
- **Refresh schedule** — how often the model refreshes in production

---

## 2. Color theme (Gritera Advisory)

All reports MUST use the Gritera brand palette. No exceptions, no "creative" deviations.

### R-COLOR-01: Theme file present

A Power BI theme file MUST exist at:
`<project>.Report/StaticResources/SharedResources/BaseThemes/gritera.json`

The theme MUST be referenced in `report.json` as the active theme.

### R-COLOR-02: Core palette

The theme's `dataColors` array MUST contain exactly these values in this order:

| Position | Hex       | Name           |
|----------|-----------|----------------|
| 1        | `#1E2C52` | Mørk blå       |
| 2        | `#3658A3` | Blå            |
| 3        | `#416866` | Grønn          |
| 4        | `#563379` | Lilla          |
| 5        | `#203433` | Mørk grønn     |
| 6        | `#361E4C` | Mørk lilla     |
| 7        | `#A9B7DE` | Lys blå        |
| 8        | `#A4D3D0` | Lys grønn      |

### R-COLOR-03: Accent and structural colors

The theme MUST define:

```json
{
  "background": "#FBF3E8",
  "foreground": "#4D0000",
  "tableAccent": "#FF5B3C",
  "good": "#416866",
  "neutral": "#3658A3",
  "bad": "#FF5B3C",
  "maximum": "#1E2C52",
  "center": "#A9B7DE",
  "minimum": "#FBF3E8",
  "null": "#F0E4D0"
}
```

### R-COLOR-04: Forbidden colors

These colors MUST NOT appear anywhere in theme files or as visual-level color overrides:

| Forbidden    | Why                                  | Use instead                |
|--------------|--------------------------------------|----------------------------|
| `#FFFFFF`    | Generic white — not on-brand          | `#FBF3E8` (Gritera Cream)  |
| `#000000` bg | Generic black — not on-brand          | `#4D0000` (Gritera Maroon) |
| `#0078D4`    | Power BI default blue                 | `#3658A3` (Gritera Blå)    |
| `#118DFF`    | Power BI default blue (alt)           | `#3658A3` (Gritera Blå)    |
| `#E66C37`    | Power BI default orange               | `#FF5B3C` (Gritera Orange) |
| Any other    | If not in §2.2 or §2.3, it's wrong    | See palette                |

### R-COLOR-05: Orange used as accent only

`#FF5B3C` (Gritera Orange) is an accent color. It MUST NOT be used as:
- A page background
- A primary data color (positions 1–6 in `dataColors`)
- A large fill area exceeding 20% of a visual's surface

It MAY be used for: KPI emphasis, alert states, callout borders, slicer selection indicators.

---

## 3. Naming conventions

### R-NAME-01: Tables

Table names MUST be `PascalCase`, singular for dimensions, plural for facts.

- ✅ `Customer`, `Product`, `SalesOrder`, `Sales`, `Inventories`
- ❌ `customers`, `customer_table`, `tbl_Customer`, `DIM_Customer`

### R-NAME-02: Columns

Column names MUST be `Title Case With Spaces` for user-facing columns, and
`PascalCase` for technical/key columns.

- ✅ `Customer Name`, `Order Date`, `Net Revenue NOK`, `CustomerID`, `SK_Product`
- ❌ `customer_name`, `orderDate`, `net_revenue`, `customer name`

### R-NAME-03: Measures

Measure names MUST:
- Start with a capital letter
- Use `Title Case` with spaces
- Include the unit suffix when applicable: ` NOK`, ` %`, ` (Count)`, ` (YoY)`
- Be globally unique across the model

- ✅ `Total Revenue NOK`, `Margin %`, `Active Customers (Count)`, `Revenue YoY %`
- ❌ `totalRevenue`, `[Measure 1]`, `Sum of Sales`, `measure_revenue`

### R-NAME-04: Measure folders (display folders)

Every measure MUST be assigned to a Display Folder. Top-level folders allowed:

- `01 Revenue`
- `02 Cost`
- `03 Margin`
- `04 Volume`
- `05 Customer`
- `06 Time Intelligence`
- `99 Internal` (for helper measures not exposed to end users)

Measures without a display folder, or in folders not on this list, fail this rule.

### R-NAME-05: Hidden technical columns

Surrogate keys, raw IDs, and any column not intended for end-user consumption MUST be
hidden from the report view (`isHidden: true` in TMDL).

---

## 4. Data model

### R-MODEL-01: Star schema

All models MUST follow a star schema. Snowflake patterns require an exception documented
in the project's `README.md` under a `### Modeling exceptions` heading.

### R-MODEL-02: Single direction relationships

All relationships MUST be single-direction (`crossFilteringBehavior: oneDirection`)
unless documented in `README.md`. Bidirectional filtering across multiple relationships
is the leading cause of ambiguous filter context.

### R-MODEL-03: Dedicated date table

Every model that contains a date column MUST have a dedicated `Date` table marked as
the date table (`dataCategory: Time`). Auto date/time MUST be disabled
(`discourageImplicitMeasures: true` in `model.tmdl`).

### R-MODEL-04: No calculated columns where measures suffice

Calculated columns are permitted only when:
- They are used in a slicer, filter, or relationship
- They cannot be replaced by a measure

If a calculated column exists, it MUST have an annotation explaining why:

```tmdl
column 'Customer Segment' = SWITCH(...)
    annotation Justification = "Used as slicer on page 'Customer Overview'"
```

Calculated columns without a `Justification` annotation fail this rule.

### R-MODEL-05: Cardinality declared

Every relationship MUST have explicit `fromCardinality` and `toCardinality` set.
Defaults are not acceptable.

---

## 5. DAX standards

### R-DAX-01: Formatting

DAX measures MUST be formatted with:
- One clause per line for expressions longer than 80 characters
- Two-space indentation for nested function arguments
- `CALCULATE`, `FILTER`, `SUMX`, etc. on their own line when used

✅ Good:
```dax
Total Revenue NOK =
CALCULATE(
  SUMX(
    Sales,
    Sales[Quantity] * Sales[Unit Price]
  ),
  Sales[Status] = "Confirmed"
)
```

❌ Bad:
```dax
Total Revenue NOK = CALCULATE(SUMX(Sales, Sales[Quantity] * Sales[Unit Price]), Sales[Status] = "Confirmed")
```

### R-DAX-02: No `SUM` on calculated expressions

`SUM(Table[Col1] * Table[Col2])` is invalid DAX. Use `SUMX` for row-by-row evaluation:

- ✅ `SUMX(Sales, Sales[Quantity] * Sales[Unit Price])`
- ❌ `SUM(Sales[Quantity] * Sales[Unit Price])`

### R-DAX-03: Prefer variables for repeated expressions

If the same expression appears more than once in a measure, it MUST be extracted into a
`VAR`. This improves both readability and performance.

### R-DAX-04: No implicit measures

Implicit measures (dragging a numeric column directly into a visual) are forbidden.
Every numeric value displayed in a visual MUST come from an explicit measure.

The model MUST set `discourageImplicitMeasures: true` in `model.tmdl`.

### R-DAX-05: Time intelligence uses `Date` table

Time intelligence functions (`SAMEPERIODLASTYEAR`, `DATEADD`, `DATESYTD`, etc.) MUST
reference the dedicated `Date` table from R-MODEL-03. Using a date column from a fact
table directly is not permitted.

### R-DAX-06: No `FILTER(ALL(...))` antipattern when not needed

`CALCULATE(expr, FILTER(ALL(Table[Col]), Table[Col] = value))` should usually be
`CALCULATE(expr, Table[Col] = value)`. The longer form is allowed only when the table
filter context genuinely needs to be removed first; this case MUST be documented with
a comment above the measure.

---

## 6. Pages and visuals

### R-PAGE-01: Required pages

Every report MUST contain at least these pages, in this order:

1. **Forside** (`page_id: cover`) — title, last refresh, owner, navigation buttons
2. **Sammendrag** (`page_id: summary`) — top-level KPIs only
3. *(report-specific content pages)*
4. **Detaljer** (`page_id: details`) — drill-through target page
5. **Dokumentasjon** (`page_id: documentation`) — data sources, measure descriptions,
   change log

### R-PAGE-02: Page size

All pages MUST be 16:9, 1280 × 720 (Standard) OR 1920 × 1080 (Full HD).
No "Custom" sizes.

### R-PAGE-03: Page background

Page background MUST be `#FBF3E8` (Gritera Cream). Visual backgrounds may be `#FFFFFF`
with 0% transparency (Power BI does not support `#FBF3E8` as a visual-level fill in all
visual types, so visual backgrounds are exempt from R-COLOR-04).

### R-PAGE-04: Header band

Every page MUST start with a header band at the top:
- Height: 60 px on 1080p pages, 40 px on 720p pages
- Fill: `#4D0000` (Gritera Maroon)
- Contains page title in white text, left-aligned, General Sans Medium 18–24pt

### R-PAGE-05: No "Page 1", "Untitled", "Copy of"

Page display names MUST be meaningful. Default Power BI names are rejected:

- ❌ `Page 1`, `Page 2`, `Untitled Page`, `Copy of Sammendrag`
- ✅ `Forside`, `Salg per region`, `Kundetilfredshet`

### R-VIS-01: No default visual titles

Every visual MUST have an explicit, meaningful title. Visuals with default titles like
`Sum of Revenue by Date` fail this rule. The title should describe the business
question, e.g., `Omsetning per måned`.

### R-VIS-02: Tooltips configured

Bar, line, column, and area visuals MUST have at least one tooltip field configured
beyond the visual's own axis/value.

### R-VIS-03: No "Show items with no data"

This setting causes silent performance problems. It MUST be off on all visuals unless
documented in a comment in the page-level `.json`.

---

## 7. Documentation

### R-DOC-01: Measure descriptions

Every measure exposed to end users (i.e., not in display folder `99 Internal`) MUST
have a `description` property in TMDL:

```tmdl
measure 'Total Revenue NOK' = SUMX(Sales, Sales[Quantity] * Sales[Unit Price])
    description = "Total confirmed sales revenue in NOK, before VAT."
    formatString = "#,0 kr"
    displayFolder = "01 Revenue"
```

### R-DOC-02: Table descriptions

Every table MUST have a `description` property explaining what the table represents and
where the data comes from.

### R-DOC-03: Changelog

The `README.md` of each project MUST include a `## Changelog` section with entries in
reverse chronological order. New entries are required for any merged PR that touches
the project.

```markdown
## Changelog

- 2026-05-20 — Added customer churn measures (Tore)
- 2026-04-15 — Migrated to Gritera theme v2 (Kristian)
```

---

## 8. Performance

### R-PERF-01: Model file size

Compressed `.pbip` model file size SHOULD be under 100 MB. Projects over 100 MB MUST
document why in `README.md` under `### Size justification`.

### R-PERF-02: No high-cardinality columns hidden

Columns with cardinality > 1,000,000 unique values MUST be either:
- Reduced via aggregation tables, OR
- Documented as necessary in `README.md`

### R-PERF-03: Aggregation tables for fact tables > 10M rows

Fact tables with more than 10 million rows MUST have at least one aggregation table
defined, with the relationship and aggregation precedence set in the model.

---

## 9. Security and data handling

### R-SEC-01: No row-level personal data exposed

Columns containing personally identifiable information (PII) — full names, national ID
numbers, exact addresses, phone numbers, email addresses — MUST be either:
- Hidden from the report view (`isHidden: true`), OR
- Aggregated to a non-identifying level

### R-SEC-02: RLS for multi-tenant data

Any model containing data scoped to specific business units, customers, or regions
MUST have Row-Level Security (RLS) roles defined in `model.tmdl`.

### R-SEC-03: No credentials in repo

Connection strings, API keys, service principal secrets, or database passwords MUST
NOT appear anywhere in the repository — not in TMDL, not in `.pbip`, not in M scripts,
not in comments, not in `README.md`. Use parameters and environment-based binding instead.

---

## 10. Exception process

A project may deviate from a specific rule by adding an `EXCEPTIONS.md` file at the
project root with this format:

```markdown
# Exceptions

## R-MODEL-02 (Single direction relationships)
- **Why**: The Forecast vs Actual comparison requires bidirectional filtering between
  Calendar and ForecastVersion.
- **Approved by**: Kristian Solberg, 2026-04-12
- **Review date**: 2026-10-12
```

The compliance routine reads `EXCEPTIONS.md` and will not flag rules listed there,
provided each exception includes a Why, an Approver, and a Review date in the future.
Expired exceptions are reported as violations.

---

## Version

| Version | Date       | Author   | Change                                    |
|---------|------------|----------|-------------------------------------------|
| 1.0     | 2026-05-20 | Tore     | Initial standards committed to repo       |
