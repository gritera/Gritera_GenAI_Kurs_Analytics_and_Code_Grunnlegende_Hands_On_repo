-- ⚠️ Denne modellen inneholder TRE bevisste feil — finn og fiks dem.
--
-- Mål: omsetning og antall ordrer per produktkategori for fullførte ordrer.
--
-- Steg 1: kjør `dbt run --select buggy_model` og les feilmeldingen.
-- Steg 2: lim hele feilmeldingen til AI-agenten og be den fikse.
-- Steg 3: når modellen kjører grønt — verifiser radantall og kategorifordeling.
--         Den siste feilen gir IKKE compile-error. Den gir feil data.

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
