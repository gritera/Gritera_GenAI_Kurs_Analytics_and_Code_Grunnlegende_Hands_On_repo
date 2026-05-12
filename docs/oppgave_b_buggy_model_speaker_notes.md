# Oppgave B — Debug en ødelagt modell · Speaker notes

**Tidsboks:** 5 minutter
**Filsti:** `models/exercises/buggy_model.sql`
**Mål:** Deltakerne erfarer at AI-agenten kan løse compile-feil raskt, men at de selv må verifisere logikken — AI-en stopper ofte ved "modellen kjører" uten å sjekke om dataene er riktige.

---

## De tre feilene

| # | Type | Hvor | Hva er galt |
|---|------|------|-------------|
| 1 | **dbt parse-feil** | `{{ ref('raw_order') }}` (linje 12) | Mangler `s` — riktig seed heter `raw_orders` |
| 2 | **DuckDB binder-feil** | `sum(oi.line_total)` (linje 27) | Kolonnen heter `line_total_nok`, ikke `line_total` |
| 3 | **Logisk feil i aggregering** | `p.product_name` i SELECT + GROUP BY (linje 25 + 30) | Ekstra dimensjon — gir én rad per produkt (12 rader) i stedet for én rad per kategori (3 rader) |

Feilene avdekkes i rekkefølge: bug 1 stopper dbt parse → fiks → bug 2 stopper DuckDB execution → fiks → modellen kjører grønt, men output er feil pga bug 3.

---

## Forventet flyt med deltaker + AI

### Etter steg 1 (`dbt run --select buggy_model`)

Deltakeren ser én feilmelding om gangen. Første feil:

```
Compilation Error in model buggy_model (models/exercises/buggy_model.sql)
  Model 'model.kurs_dataplattform.buggy_model' (models/exercises/buggy_model.sql) depends on a node named 'raw_order' which was not found
```

### Etter steg 2 (deltaker limer feil til AI)

AI fikser typisk `raw_order` → `raw_orders` umiddelbart. Deltakeren kjører på nytt og får ny feil:

```
Runtime Error in model buggy_model
  Binder Error: Referenced column "line_total" not found in FROM clause!
  Candidate bindings: "oi.line_total_nok"
```

DuckDB foreslår selv riktig navn — AI fikser dette også raskt.

### Etter steg 3 (modellen kjører grønt)

Her er det **kritiske punktet**. Modellen returnerer nå data uten feil — men deltakerne skal merke at **noe ikke stemmer**:

- Forventet radantall: **3** (én per kategori: Kaffe, Te, Snacks)
- Faktisk radantall: **~12** (én per produkt × kategori-kombinasjon)

Mange AI-agenter erklærer seieren her, og noen deltakere kan også gjøre det. Det er hele poenget med oppgaven — at de skal **verifisere logikken**, ikke bare at kommandoen fullfører.

---

## Verifikasjonskommandoer (instruktørens fasit)

Profilen heter `kurs.duckdb` (ikke `dev.duckdb` som vises på sliden — sliden har en mindre typo). Deltakerne kan bruke begge varianter:

**Anbefalt — dbt-native:**
```bash
dbt show --select buggy_model --limit 20
```

**Eller direkte mot DuckDB:**
```bash
duckcli kurs.duckdb -e "SELECT count(*) FROM buggy_model"
# eller
python -c "import duckdb; print(duckdb.connect('kurs.duckdb').execute('SELECT count(*) FROM buggy_model').fetchall())"
```

### Forventet ETTER alle tre feil er fikset

Modellen skal returnere **3 rader** med kolonner `category`, `num_orders`, `total_revenue_nok`. Omtrentlige tall (verdier kan variere noe ved seed-endringer):

| category | num_orders | total_revenue_nok |
|----------|-----------:|------------------:|
| Kaffe    | ~17        | ~1980             |
| Snacks   | ~9         | ~440              |
| Te       | ~10        | ~580              |

Hvis radantallet er **12** → bug 3 er ikke fikset.
Hvis radantallet er **0 eller error** → bug 1 eller 2 er ikke fikset.
Hvis tall ser oppblåste ut (mer enn dobbelt) → manglende `where status = 'completed'` (alternativ logisk feil deltakerne kan komme borti hvis AI omskriver mer enn nødvendig).

---

## Den korrekte modellen (instruktørens fasit)

```sql
with orders as (
    select * from {{ ref('raw_orders') }}
    where status = 'completed'
),

order_items as (
    select * from {{ ref('raw_order_items') }}
),

products as (
    select * from {{ ref('raw_products') }}
)

select
    p.category,
    count(distinct o.order_id) as num_orders,
    sum(oi.line_total_nok) as total_revenue_nok
from orders o
inner join order_items oi on o.order_id = oi.order_id
inner join products p on oi.product_id = p.product_id
group by p.category
order by p.category
```

Tre endringer fra buggy-versjonen:
1. `raw_order` → `raw_orders`
2. `oi.line_total` → `oi.line_total_nok`
3. Fjern `p.product_name` fra både SELECT og GROUP BY

---

## Pedagogiske poeng å trekke frem

1. **AI er sterk på syntaktiske feil, svak på semantiske.**
   Bug 1 og 2 fikses nær 100 % av tiden, korrekt og kjapt. Bug 3 krever at man kjenner forretningslogikken ("én rad per kategori") for å oppdage.

2. **"Det kjører" ≠ "det er riktig".**
   En kjørbar modell som returnerer feil data er **farligere** enn en som krasjer. En krasjet modell oppdages umiddelbart; et feil tall lever videre i rapporter.

3. **Verifiseringsdisiplin: alltid sammenlign mot forventning.**
   Lær deltakerne å spørre seg selv: "Hvor mange rader skal dette gi? Hva er størrelsesorden på tallet?" *før* de løper videre.

4. **Promptforbedring som diskusjonspunkt.**
   Slide 2 sier "Lim feilen til agenten — ikke oppsummer". Etter oppgaven kan instruktøren spørre: *Hva om vi hadde sagt "fiks alle feil og verifiser at output har 3 rader"? Hvordan endrer det resultatet?*

---

## Vanlige fallgruver under øvelsen

- **AI-en fjerner `where status = 'completed'`** når den prøver å fikse bug 2 (tror den prøver å være "snill" og inkludere alle data). → Tallene blir for høye. Fang dette ved å sjekke total revenue.
- **AI-en lager en helt ny modell** istedenfor å fikse den eksisterende. → Be deltakeren om å presisere "fiks denne filen, ikke skriv ny".
- **Deltakeren rapporterer "ferdig" på 30 sekunder.** → Be dem kjøre `dbt show --select buggy_model` og fortelle deg radantallet før de gir seg.
- **Modellen finnes ikke i DuckDB ennå** når de kjører verifiseringen. → De må kjøre `dbt run --select buggy_model` etter siste fix før tabellen finnes på disk.

---

## Variant for avanserte deltakere (5 min ekstra)

Hvis en deltaker er ferdig tidlig: be dem skrive en `.yml`-fil til modellen med tester som ville fanget bug 3 automatisk:

```yaml
version: 2
models:
  - name: buggy_model
    columns:
      - name: category
        tests:
          - unique          # ← ville feilet med duplikater fra bug 3
          - not_null
          - accepted_values:
              values: ['Kaffe', 'Te', 'Snacks']
```

Dette koblet sammen med poenget om verifisering: **tester er den varige formen for "alltid sjekke logikken"**.
