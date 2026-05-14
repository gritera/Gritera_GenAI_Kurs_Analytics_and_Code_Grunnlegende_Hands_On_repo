---
title: Dokumentasjon
---

# Dokumentasjon

Dette dashboardet er bygget med **Evidence** på toppen av et **dbt + DuckDB**-prosjekt for kurset _"Grunnleggende Generativ AI Kurs for Analytics & Code"_.

---

## Dataflyt

```
CSV-filer (seeds/)
    ↓  dbt seed
raw_* tabeller (main_raw schema)
    ↓  dbt run (staging)
stg_* views (main schema)
    ↓  dbt run (intermediate)
int_complaints_enriched
    ↓  dbt run (marts)
mart_complaint_summary
    ↓  npm run sources
Evidence parquet-cache
    ↓  Evidence dev server
Dashboard (denne siden)
```

---

## Datakilder

| Tabell | Rader | Beskrivelse |
|---|---|---|
| `raw_customers` | 15 | Kunder fra ulike norske regioner |
| `raw_products` | 12 | Produktkatalog — kaffe, te og snacks |
| `raw_orders` | 20 | Ordrer med status og totalbeløp |
| `raw_order_items` | 42 | Ordrelinjer — produkt, antall og pris |
| `raw_complaints` | 11 | Kundeklager knyttet til ordrer |

---

## dbt-modeller

### Staging (`models/staging/`)
Én-til-én-mapping fra rå CSV-data. Rensing og typekonvertering.

| Modell | Beskrivelse |
|---|---|
| `stg_customers` | Kunder med `full_name`, region og aktiv-flag |
| `stg_orders` | Ordrer med dato, status og `total_amount_nok` |
| `stg_products` | Produkter med pris, kostnad, kategori og leverandør |

### Intermediate (`models/intermediate/`)
Forretningslogikk og joins på tvers av kilder.

| Modell | Beskrivelse |
|---|---|
| `int_complaints_enriched` | Klager beriket med kundenavn, region og ordredata. Beregner `days_to_resolve` og `is_resolved`. |

### Marts (`models/marts/`)
Ferdige aggregater klare for analyse.

| Modell | Beskrivelse |
|---|---|
| `mart_complaint_summary` | Månedlig oppsummering per klagekategori: antall, løste, behandlingstid og løsningsgrad. |

---

## Dashboard-sider

| Side | URL | Innhold |
|---|---|---|
| Hjem | `/` | Overordnet KPI-oversikt for salg og klager |
| Kunder | `/kunder` | Kundetabell med ordrehistorikk og regionsfordeling |
| Produkter | `/produkter` | Produktkatalog med marginer og kategorifordeling |
| Klager | `/klager` | Klagehåndtering — kategori, løsningsgrad og detaljtabell |
| Dokumentasjon | `/dokumentasjon` | Denne siden |

---

## Teknisk stack

| Komponent | Versjon |
|---|---|
| dbt-core | 1.11 |
| dbt-duckdb | 1.10 |
| DuckDB | 1.10 |
| Evidence | latest |
| Node.js | 20 |
| Python | 3.12 |

---

## Kjøre prosjektet

```bash
# Last inn CSV-data
dbt seed

# Bygg alle dbt-modeller
dbt run

# Kjør tester
dbt test

# Kompiler datakilder til Evidence
cd dashboard && npm run sources

# Start dashboard-server
npm run dev
```
