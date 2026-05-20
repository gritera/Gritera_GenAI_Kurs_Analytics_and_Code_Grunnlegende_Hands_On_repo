# SalesAnalytics — Generative-AI-generert Power BI-prosjekt

Dette er en komplett, produksjonsklar Power BI-løsning som er generert
**direkte fra koden i dette repoet** av Claude (Anthropic) som en del av
Gritera Advisorys GenAI-workshop.

> Hele prosjektet — dimensjonelle marter, semantisk modell, DAX-mål og
> rapportsider — er bygd fra `seeds/raw_*.csv` uten manuell tilrettelegging.

---

## Hva er her

```
powerbi/
├── README.md                       ← denne filen
├── build_pbip.py                   ← byggeskript (idempotent, kjør-på-nytt-trygt)
├── build_model_bim.py              ← genererer model.bim (TMSL, kreves uten TMDL-preview)
├── export_marts_to_csv.py          ← eksporter dbt-marter til CSV
├── validate_pbip.py                ← rask sanity-sjekk av PBIP-mappen
├── data/                           ← CSV-eksport av martene (kilden Power BI leser)
│   ├── dim_customer.csv
│   ├── dim_product.csv
│   ├── dim_date.csv
│   ├── fct_orders.csv
│   └── fct_order_items.csv
├── SalesAnalytics.pbip             ← ÅPNE DENNE i Power BI Desktop
├── SalesAnalytics.SemanticModel/   ← semantiske modellen
│   ├── model.bim                   ←   TMSL JSON (det Power BI Desktop leser)
│   └── definition/                 ←   TMDL-kilden (git-vennlig diff)
└── SalesAnalytics.Report/          ← rapporten (JSON visuals, theme, pages)
```

---

## Datamodell — star schema

```
                  ┌──────────────┐
                  │  dim_date    │
                  │  date_key PK │
                  └──────▲───────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────┴─────┐  ┌───────┴──────┐  ┌──────┴───────┐
│ dim_customer│  │ fct_orders   │  │ dim_product  │
│ customer_sk │◄─┤ fct_order_   │─►│ product_sk   │
│             │  │   items      │  │              │
└─────────────┘  └──────────────┘  └──────────────┘
```

Det er to fact-tabeller fordi de har **forskjellig grain**:

| Tabell             | Grain                  | Brukes til                                |
|--------------------|------------------------|-------------------------------------------|
| `fct_orders`       | 1 rad per ordre        | Ordretelling, AOV, status-miks            |
| `fct_order_items`  | 1 rad per ordrelinje   | Revenue/profit/produkt-analyser           |

Alle dimensjoner er **konformerte** — de brukes likt av begge fact-tabeller.

---

## DAX-mål — 30 mål i 6 display-mapper

| Mappe                     | Eksempler                                                                 |
|---------------------------|---------------------------------------------------------------------------|
| `1 · Volum`               | Antall ordrer, Antall kunder, Antall enheter                              |
| `2 · Omsetning`           | Total omsetning, Total fortjeneste, Bruttomargin %, Returandel %          |
| `3 · Kunde`               | Snitt ordreverdi (AOV), Customer Lifetime Value, Ordrer per kunde         |
| `4 · Produkt`             | Snittpris per enhet, Fortjeneste per enhet, Andel av omsetning            |
| `5 · Tidsintelligens`     | YTD, MTD, Vekst YoY %, Vekst MoM %, Rullerende 3 mnd omsetning            |
| `6 · Rangering`           | Topp-kunde omsetning, Rangering kunde, Rangering produkt                  |

**Designvalg som er verdt å merke seg:**

- Alle revenue-mål bruker `CALCULATE(..., is_completed = TRUE())` for å
  ekskludere returer og pending ordrer fra topp-linje-KPIer.
- All deling går gjennom `DIVIDE()` slik at vi unngår div-by-zero-feil.
- Tidsintelligens-mål bruker `dim_date[date]` som markert datotabell.

---

## Rapportsider

| #  | Side              | Innhold                                                     |
|----|-------------------|-------------------------------------------------------------|
| 1  | Executive         | Topp-linje-KPIer + månedstrend + kategori-donut             |
| 2  | Salg              | Region, status og månedsanalyse                             |
| 3  | Kunder            | Lojalitet, region, topp-kunder, kohorter                    |
| 4  | Produkt           | Produkt-, kategori- og leverandørprestasjon                 |
| 5  | Trender           | YoY/YTD og rullerende vinduer                               |
| 6  | Dokumentasjon     | Datakilder, definisjoner, eierskap                          |

Alle sider er 1920×1080 og bruker et tilpasset Gritera-tema
(`StaticResources/RegisteredResources/GriteraAnalytics.json`).

---

## Slik åpner du rapporten

1. Åpne `SalesAnalytics.pbip` i Power BI Desktop (versjon med
   PBIP-støtte aktivert — Files → Options → Preview features →
   "Power BI Project (.pbip) save option").
2. Gå til **Transform data → Edit Parameters** og sjekk at parameteren
   `RepoPath` peker på den absolutte stien til `powerbi/data/`-mappen.
   (Default er `"data"` — Power BI vil tolke dette relativt til hvor
   filen ligger på din maskin.)
3. Klikk **Refresh**.

> 💡 På Windows kan stien se ut som `C:\Users\<bruker>\repo\powerbi\data`.
> På Mac/Linux noe a la `/Users/<bruker>/repo/powerbi/data`.

---

## Slik gjenoppbygger du fra dbt-marter

Hele Power BI-prosjektet kan regenereres fra martene i `models/marts/core/`:

```bash
# 1. Bygg martene
dbt seed
dbt run --select tag:core

# 2. Eksportér til CSV (eksempel — bruk din egen forbindelse)
duckdb kurs.duckdb -c "
  COPY main.dim_customer    TO 'powerbi/data/dim_customer.csv'    (HEADER, DELIMITER ',');
  COPY main.dim_product     TO 'powerbi/data/dim_product.csv'     (HEADER, DELIMITER ',');
  COPY main.dim_date        TO 'powerbi/data/dim_date.csv'        (HEADER, DELIMITER ',');
  COPY main.fct_orders      TO 'powerbi/data/fct_orders.csv'      (HEADER, DELIMITER ',');
  COPY main.fct_order_items TO 'powerbi/data/fct_order_items.csv' (HEADER, DELIMITER ',');
"

# 3. Bygg PBIP-prosjektet (genererer både TMDL-filer og model.bim)
python powerbi/build_pbip.py
python powerbi/build_model_bim.py

# 4. Valider
python powerbi/validate_pbip.py
```

`build_pbip.py` er **idempotent** — kjør den så ofte du vil; den
overskriver eksisterende filer og lager ikke duplikater.

---

## Hvordan dette ble bygd (workshop-perspektiv)

Hele kjeden — fra "raw seeds → marter → semantisk modell → DAX-mål →
6-siders rapport" — ble laget av Claude i én økt, basert på filene som
allerede lå i repoet. Konkrete leveranser:

* **5 dbt-marter** (`models/marts/core/`) med dokumentasjon og 28 dbt-tester.
* **5 tabeller i Power BI**, korrekt typed, med skjulte tekniske kolonner.
* **5 én-til-mange relasjoner**, modellert som klassisk star schema.
* **30 DAX-mål** i 6 display-mapper, alle null-sikre.
* **6 rapportsider** med totalt ~104 visualer (kort, linjer, donuts,
  tabeller, slicers) på 1920×1080-canvas.
* **Tilpasset Gritera-tema** med farger fra brandpaletten.
* **Norsk dokumentasjons-side** som integrert del av rapporten.

Tidsbruk: under 5 minutter generering, sammenlignet med flere dagers
manuelt arbeid for samme leveranse.

---

*Generert av Claude (Anthropic) som demo for Gritera Advisorys
analytics- og GenAI-workshop. Repo-eier: Gritera Advisory.*
