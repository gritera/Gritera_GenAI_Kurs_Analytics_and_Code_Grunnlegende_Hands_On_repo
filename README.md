# Gritera GenAI Kurs — Hands-on

Praktisk prosjekt for kurset **Grunnleggende Generativ AI Kurs for Analytics & Code**.

Et ferdig dbt-prosjekt med DuckDB, seed-data og starter-modeller — klar til bruk med Claude Code eller GitHub Copilot.

## Kom i gang (anbefalt vei: GitHub Codespaces)

Du trenger bare en nettleser og en GitHub-konto. Alt installeres automatisk i skyen.

### Steg 1: Lag din egen kopi

Klikk **Use this template** → **Create a new repository** øverst på denne siden. Velg ditt eget GitHub-brukernavn som eier.

### Steg 2: Åpne i Codespace

Gå til ditt nye repo → klikk **Code** → **Codespaces** → **Create codespace on main**.

Vent ~2 minutter. Miljøet installerer automatisk:
- Python 3.12 + `uv` med dbt-core og dbt-duckdb
- Claude Code CLI
- VS Code extensions (Copilot, dbt Power User, Rainbow CSV)
- Seed-data lastes og starter-modeller bygges

### Steg 3: Verifiser

Når Codespace er klart, åpne terminalen og kjør:

```bash
uv run dbt debug
```

Du skal se: `All checks passed!`

Hvis noe ser feil ut — hopp ned til **Steg 0 (AI-fallback)** lenger nede.

### Steg 4: Start AI-assistenten

**Claude Code:**
```bash
claude
# Krever ANTHROPIC_API_KEY — du får denne fra instruktøren
```

**GitHub Copilot:** Allerede aktivert i VS Code hvis du har Copilot-tilgang.

---

## Steg 0 (AI-fallback): Lim dette inn hvis noe er feil

Hvis `uv run dbt debug` ikke gir "All checks passed!", eller du er usikker på om miljøet er klart — åpne Claude Code (`claude`) eller Copilot Chat og lim inn dette ene promptet:

> **Sett opp og verifiser dbt-prosjektet for meg.**
>
> Du står i et dbt + DuckDB-prosjekt (Python 3.12, uv, dbt-duckdb). Gjør følgende, i denne rekkefølgen, og stopp + forklar enkelt hvis noe feiler:
>
> 1. Sjekk at `uv` finnes (`uv --version`). Hvis ikke, installer via `pip install uv`.
> 2. Kjør `uv sync` for å installere alle Python-avhengigheter fra `pyproject.toml`.
> 3. Kjør `uv run dbt debug` og bekreft at det står "All checks passed!".
> 4. Kjør `uv run dbt seed` for å laste CSV-ene i `seeds/` inn i `kurs.duckdb`.
> 5. Kjør `uv run dbt run` for å bygge alle modellene under `models/`.
> 6. Kjør `uv run dbt test` og rapporter hvor mange tester som passerte.
> 7. Til slutt: skriv ut en kort oppsummering på norsk med (a) antall tabeller seedet, (b) antall modeller bygget, (c) antall tester, og (d) hva neste steg er ifølge `README.md`.
>
> Hvis et steg feiler: ikke gå videre. Forklar feilen i én setning og foreslå én konkret fiks før du venter på svar.

AI-en kjører kommandoene for deg og rapporterer om alt er grønt.

---

## Hvis Codespaces er blokkert (firma-PC, brannmur, etc.)

Noen arbeidsgivere blokkerer `github.com/codespaces` eller `*.github.dev`. Velg én av disse i prioritert rekkefølge:

### Plan B1: Privat PC + privat GitHub-konto
Den enkleste løsningen. Hjemme-PC eller mobilhotspot fra jobb-PC, og logg inn med en privat GitHub-konto. Du får 60 gratis Codespaces-timer/mnd — mer enn nok for dette kurset.

### Plan B2: Lokal kjøring med uv
Hvis du har Python 3.12 og kan installere ting lokalt:

```bash
# 1. Installer uv (én gang)
# macOS/Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh
# Windows (PowerShell):
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 2. Klon ditt repo og gå inn i mappen
git clone https://github.com/<ditt-brukernavn>/<repo-navn>.git
cd <repo-navn>

# 3. Installer alle avhengigheter
uv sync

# 4. Verifiser
uv run dbt debug
uv run dbt seed
uv run dbt run
uv run dbt test
```

For Claude Code lokalt:
```bash
npm install -g @anthropic-ai/claude-code
claude
```

For GitHub Copilot lokalt: åpne mappen i VS Code og logg inn med Copilot-konto.

### Plan B3: Si ifra til instruktøren
Hvis B1 og B2 ikke fungerer — rekk opp hånden ved kursstart. Vi finner en løsning (parring med en annen deltaker, eller en ekstra-Codespace fra instruktørens konto).

---

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

> Repoet inneholder også et Northwind-datasett under `seeds/northwind/`. Det er **deaktivert som standard** — for å laste dem, sett `+enabled: true` i `dbt_project.yml` under `seeds.kurs_dataplattform.northwind`.

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
uv run dbt seed                          # Last inn CSV-data
uv run dbt run                           # Bygg alle modeller
uv run dbt test                          # Kjør tester
uv run dbt run --select stg_products     # Bygg én spesifikk modell
uv run dbt test --select stg_products    # Test én spesifikk modell
```

## Trenger du hjelp?

Rekk opp hånden — instruktøren hjelper deg.
