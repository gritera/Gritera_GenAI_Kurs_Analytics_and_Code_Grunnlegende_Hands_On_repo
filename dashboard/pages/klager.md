---
title: Klager
---

```sql kpi
select
    count(*)                                                            as totalt,
    count(*) filter (where status = 'resolved')                        as loste,
    count(*) filter (where status = 'open')                            as apne,
    round(100.0 * count(*) filter (where status = 'resolved')
        / count(*), 1)                                                 as losningsgrad,
    round(avg(dager_til_losning) filter (where status = 'resolved'), 1) as snitt_dager
from kurs.klager_detalj
```

```sql per_kategori
select
    kategori,
    count(*)                                                            as antall,
    count(*) filter (where status = 'resolved')                        as loste,
    round(100.0 * count(*) filter (where status = 'resolved')
        / count(*), 1)                                                 as losningsgrad,
    round(avg(dager_til_losning) filter (where status = 'resolved'), 1) as snitt_dager
from kurs.klager_detalj
group by kategori
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

```sql losningsgrad_per_kategori
select
    klagekategori,
    sum(antall_klager)                                              as antall,
    sum(antall_loste)                                               as loste,
    round(100.0 * sum(antall_loste) / sum(antall_klager), 1)       as losningsgrad,
    round(avg(snitt_behandlingstid_dager), 1)                      as snitt_dager
from kurs.mart_complaint_summary
group by klagekategori
order by antall desc
```

```sql alle_klager
select
    complaint_id,
    kategori,
    status,
    kunde,
    region,
    created_at,
    dager_til_losning,
    beskrivelse
from kurs.klager_detalj
order by created_at desc
```

# Klager

<BigValue data={kpi} value=totalt       title="Totalt klager" />
<BigValue data={kpi} value=loste        title="Løste klager" />
<BigValue data={kpi} value=apne         title="Åpne klager" />
<BigValue data={kpi} value=losningsgrad title="Løsningsgrad" suffix="%" />
<BigValue data={kpi} value=snitt_dager  title="Snitt behandlingstid" suffix=" dager" />

---

## Per kategori

<DataTable data={per_kategori}>
    <Column id=kategori        title="Kategori" />
    <Column id=antall          title="Antall" />
    <Column id=loste           title="Løste" />
    <Column id=losningsgrad    title="Løsningsgrad %" />
    <Column id=snitt_dager     title="Snitt dager" />
</DataTable>

<BarChart
    data={per_kategori}
    x=kategori
    y=antall
    title="Klager per kategori"
    colorPalette={['#f59e0b','#ef4444','#8b5cf6']}
/>

---

## Klager over tid

<BarChart
    data={maanedlig_total}
    x=maaned
    y={['antall_klager','antall_loste']}
    labels={['Totalt','Løste']}
    title="Klager og løste per måned"
    type=grouped
/>

## Løsningsgrad og behandlingstid per kategori

<BarChart
    data={losningsgrad_per_kategori}
    x=klagekategori
    y=losningsgrad
    title="Løsningsgrad per kategori (%)"
    colorPalette={['#10b981','#f59e0b','#8b5cf6']}
/>

<BarChart
    data={losningsgrad_per_kategori}
    x=klagekategori
    y=snitt_dager
    title="Snitt behandlingstid i dager per kategori"
    colorPalette={['#3b82f6','#f59e0b','#8b5cf6']}
/>

---

## Alle klager

<DataTable data={alle_klager} search=true>
    <Column id=complaint_id    title="ID" />
    <Column id=kategori        title="Kategori" />
    <Column id=status          title="Status" />
    <Column id=kunde           title="Kunde" />
    <Column id=region          title="Region" />
    <Column id=created_at      title="Opprettet" />
    <Column id=dager_til_losning title="Dager til løsning" />
    <Column id=beskrivelse     title="Beskrivelse" />
</DataTable>
