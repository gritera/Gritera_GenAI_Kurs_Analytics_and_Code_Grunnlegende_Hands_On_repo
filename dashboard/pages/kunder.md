---
title: Kunder
---

# Kunder

```sql kunder_med_ordrer
select
    c.full_name,
    c.email,
    c.region,
    count(o.order_id) as antall_ordrer,
    sum(o.total_amount_nok) as total_nok
from kurs.stg_customers c
left join kurs.stg_orders o on c.customer_id = o.customer_id
group by c.full_name, c.email, c.region
order by total_nok desc
```

```sql per_region
select region, count(*) as antall_kunder
from kurs.stg_customers
group by region
order by antall_kunder desc
```

<DataTable data={kunder_med_ordrer} search=true />

---

## Kunder per region

<BarChart data={per_region} x=region y=antall_kunder title="Kunder per region" />
