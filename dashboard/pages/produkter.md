---
title: Produkter
---

# Produkter

```sql produkter
select
    product_name,
    category,
    price_nok,
    cost_nok,
    round(price_nok - cost_nok, 2) as margin_nok,
    supplier,
    is_available
from kurs.stg_products
order by price_nok desc
```

```sql per_kategori
select category, count(*) as antall, avg(price_nok) as snitt_pris
from kurs.stg_products
group by category
order by antall desc
```

<DataTable data={produkter} search=true />

---

## Produkter per kategori

<BarChart data={per_kategori} x=category y=antall title="Antall produkter per kategori" />
