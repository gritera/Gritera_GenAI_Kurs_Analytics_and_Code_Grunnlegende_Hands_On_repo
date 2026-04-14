# kurs-dataplattform

Dette er et dbt-prosjekt for kurset "Grunnleggende Generativ AI Kurs for Analytics & Code".

## Stack
- **dbt-core** med **DuckDB** som adapter
- SQL-dialekt: DuckDB (PostgreSQL-lignende syntaks)
- Python 3.12

## Prosjektstruktur
```
models/
  staging/     → 1:1-mapping fra rå kilder, rensing og typekonvertering
  intermediate/ → Forretningslogikk, joins og beregninger
  marts/       → Ferdige modeller klare for analyse og rapportering
seeds/         → CSV-filer som lastes med `dbt seed`
tests/         → Egendefinerte tester
```

## Konvensjoner
- Staging-modeller heter `stg_<kilde>.sql` med tilhørende `.yml`-fil
- Intermediate-modeller heter `int_<beskrivelse>.sql`
- Mart-modeller heter `fct_<fakta>.sql` eller `dim_<dimensjon>.sql`
- Bruk `{{ ref('modellnavn') }}` — aldri direkte tabellreferanser
- Alle modeller skal ha en `.yml`-fil med beskrivelser og tester
- Bruk CTEer for lesbarhet: `with source as (...), renamed as (...)`
- DuckDB-spesifikke funksjoner er tillatt (f.eks. `strptime`, `list_agg`)

## Datasett
Fiktiv norsk e-handel med kaffe, te og snacks:
- `raw_customers` — 15 kunder fra ulike regioner
- `raw_products` — 12 produkter med priser og leverandører
- `raw_orders` — 20 ordrer med status
- `raw_order_items` — 42 ordrelinjer
- `raw_complaints` — 11 kundeklager

## Kjøring
```bash
dbt seed    # last inn CSV-data
dbt run     # bygg alle modeller
dbt test    # kjør tester
```
