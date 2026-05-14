---
title: Kurs-dashboard
---

```sql kpi
select
    sum(total_amount_nok)                                                   as total_omsetning,
    count(*)                                                                as antall_ordrer,
    sum(total_amount_nok) / count(*)                                        as snitt_ordreverdi,
    count(*) filter (where status = 'completed')                            as fullforte_ordrer
from kurs.stg_orders
```

```sql klage_kpi
select
    count(*)                                                                as totalt_klager,
    count(*) filter (where antall_loste = antall_klager)                    as maaneder_100pct,
    round(avg(prosent_lost), 1)                                             as snitt_losningsgrad,
    round(avg(snitt_behandlingstid_dager), 1)                               as snitt_behandlingstid
from kurs.mart_complaint_summary
```

```sql salg_per_status
select
    status,
    count(*)                                                                as antall,
    sum(total_amount_nok)                                                   as total_nok
from kurs.stg_orders
group by status
order by antall desc
```

```sql topp_produkter
select
    p.product_name,
    p.category,
    sum(oi.quantity)                                                        as solgt_antall,
    sum(oi.line_total_nok)                                                  as total_nok
from kurs.raw_order_items oi
join kurs.stg_products p on oi.product_id = p.product_id
group by p.product_name, p.category
order by total_nok desc
limit 6
```

```sql klager_per_kategori
select
    klagekategori,
    sum(antall_klager)                                                      as antall,
    round(avg(prosent_lost), 1)                                             as losningsgrad,
    round(avg(snitt_behandlingstid_dager), 1)                               as snitt_dager
from kurs.mart_complaint_summary
group by klagekategori
order by antall desc
```

```sql maanedlig_total
select
    maaned,
    sum(antall_klager)  as antall_klager,
    sum(antall_loste)   as antall_loste
from kurs.mart_complaint_summary
group by maaned
order by maaned
```

# Kurs-dashboard

> Fiktiv norsk e-handel — kaffe, te og snacks

---

## Salg

<BigValue data={kpi} value=total_omsetning  title="Total omsetning" fmt=num0 />
<BigValue data={kpi} value=antall_ordrer    title="Antall ordrer" />
<BigValue data={kpi} value=snitt_ordreverdi title="Snitt ordreverdi" fmt=num0 />
<BigValue data={kpi} value=fullforte_ordrer title="Fullførte ordrer" />

<BarChart
    data={salg_per_status}
    x=status
    y=antall
    title="Ordrer per status"
    colorPalette={['#3b82f6','#10b981','#f59e0b','#ef4444']}
/>

---

## Topp produkter

<DataTable data={topp_produkter} rows=6>
    <Column id=product_name title="Produkt" />
    <Column id=category title="Kategori" />
    <Column id=solgt_antall title="Solgt" />
    <Column id=total_nok title="Omsetning (NOK)" fmt=num0 />
</DataTable>

---

## Klager

<BigValue data={klage_kpi} value=totalt_klager        title="Totalt klager" />
<BigValue data={klage_kpi} value=snitt_losningsgrad   title="Snitt løsningsgrad" suffix="%" />
<BigValue data={klage_kpi} value=snitt_behandlingstid title="Snitt behandlingstid" suffix=" dager" />

<BarChart
    data={klager_per_kategori}
    x=klagekategori
    y=antall
    title="Klager per kategori"
    colorPalette={['#f59e0b','#ef4444','#8b5cf6']}
/>

<BarChart
    data={maanedlig_total}
    x=maaned
    y={['antall_klager','antall_loste']}
    labels={['Totalt','Løste']}
    title="Klager og løste per måned"
    type=grouped
/>
