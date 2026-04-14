# Gritera GenAI Kurs — Hands-on

Praktisk prosjekt for kurset **Grunnleggende Generativ AI Kurs for Analytics & Code**.

Et ferdig dbt-prosjekt med DuckDB, seed-data og starter-modeller — klar til bruk med Claude Code eller GitHub Copilot.

## Kom i gang

### Steg 1: Lag din egen kopi

Klikk **Use this template** → **Create a new repository** øverst på denne siden. Velg ditt eget GitHub-brukernavn som eier.

### Steg 2: Åpne i Codespace

Gå til ditt nye repo → klikk **Code** → **Codespaces** → **Create codespace on main**.

Vent ~2 minutter. Miljøet installerer automatisk:
- Python 3.12 med dbt-core og dbt-duckdb
- Claude Code CLI
- VS Code extensions (Copilot, dbt Power User, Rainbow CSV)
- Seed-data lastes og starter-modeller bygges

### Steg 3: Verifiser

Når Codespace er klart, åpne terminalen og kjør:

```bash
dbt debug
```

Du skal se: `All checks passed!`

### Steg 4: Start AI-assistenten

**Claude Code:**
```bash
claude
# Krever ANTHROPIC_API_KEY — du får denne fra instruktøren
```

**GitHub Copilot:** Allerede aktivert i VS Code hvis du har Copilot-tilgang.

## Prosjektet

Fiktiv norsk e-handel (NordicRetail) med kaffe, te og snacks.

### Datasett

| Tabell | Rader | Beskrivelse |
|--------|-------|-------------|
| `raw_customers` | 15 | Kunder fra ulike regioner |
| `raw_products` | 12 | Produktkatalog med priser og leverandører |
| `raw_orders` | 20 | Ordrer med status og totalbeløp |
| `raw_order_items` | 42 | Ordrelinjer — produkter per ordre |
| `raw_complaints` | 11 | Kundeklager knyttet til ordrer |

### Ferdige modeller (mønsterreferanse)

```
models/staging/
  stg_customers.sql + .yml   ← bruk som mønster
  stg_orders.sql + .yml      ← bruk som mønster
```

Disse bruker du som referanse når du ber AI-assistenten lage nye modeller.

### Din oppgave

Bygg ut prosjektet med hjelp av AI:

```
models/
  staging/        ← lag stg_products, stg_complaints, stg_order_items
  intermediate/   ← lag int_order_details, int_customer_complaints
  marts/          ← lag fct_orders, dim_customers, dim_products
```

## Nyttige kommandoer

```bash
dbt seed                          # Last inn CSV-data
dbt run                           # Bygg alle modeller
dbt test                          # Kjør tester
dbt run --select stg_products     # Bygg én spesifikk modell
dbt test --select stg_products    # Test én spesifikk modell
```

## Trenger du hjelp?

Rekk opp hånden — instruktøren hjelper deg.
