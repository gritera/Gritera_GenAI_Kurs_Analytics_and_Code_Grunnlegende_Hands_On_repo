with complaints as (
    select * from {{ ref('stg_complaints') }}
),

customers as (
    select * from {{ ref('stg_customers') }}
),

products as (
    select * from {{ ref('stg_products') }}
),

-- Pick the most expensive order item per order to avoid fan-out
-- (one order can contain multiple products)
primary_item as (
    select
        order_id,
        product_id,
        row_number() over (
            partition by order_id
            order by unit_price_nok desc
        ) as rn
    from {{ ref('raw_order_items') }}
),

primary_product_per_order as (
    select
        pi.order_id,
        p.product_id,
        p.product_name,
        p.category  as product_category,
        p.price_nok as product_price_nok,
        p.supplier
    from primary_item pi
    left join products p on pi.product_id = p.product_id
    where pi.rn = 1
)

select
    -- Complaint fields
    c.complaint_id,
    c.customer_id,
    c.order_id,
    c.category          as complaint_category,
    c.description,
    c.status,
    c.created_at,
    c.resolved_at,

    -- Customer fields
    cust.full_name       as customer_name,
    cust.email           as customer_email,
    cust.region          as customer_region,
    cust.is_active       as customer_is_active,

    -- Product fields (from primary order item)
    pp.product_id,
    pp.product_name,
    pp.product_category,
    pp.product_price_nok,
    pp.supplier

from complaints c
left join customers      cust on c.customer_id = cust.customer_id
left join primary_product_per_order pp on c.order_id = pp.order_id
