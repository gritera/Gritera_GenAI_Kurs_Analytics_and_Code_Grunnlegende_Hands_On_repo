{{
    config(
        materialized='table',
        tags=['mart', 'core', 'fact']
    )
}}

/*
    fct_order_items
    ---------------
    Lowest-grain transactional fact.

    Grain  : one row per order line
    Use    : revenue / profit / quantity analyses, product performance, basket
    Keys
        order_item_id   — natural key
        order_id        — natural key (to fct_orders)
        customer_sk     — FK -> dim_customer.customer_sk
        product_sk      — FK -> dim_product.product_sk
        order_date_key  — FK -> dim_date.date_key

    Measures
        - quantity
        - unit_price_nok
        - line_revenue_nok      = quantity * unit_price
        - line_cost_nok         = quantity * standard_cost
        - line_profit_nok       = revenue - cost
        - line_margin_pct       = profit / revenue
*/

with items as (

    select * from {{ ref('raw_order_items') }}

),

orders as (

    select * from {{ ref('stg_orders') }}

),

products as (

    select * from {{ ref('stg_products') }}

),

joined as (

    select
        -- Natural keys
        i.order_item_id,
        i.order_id,

        -- FK to dim_customer (via order)
        cast(md5(cast(o.customer_id as varchar)) as varchar)            as customer_sk,
        o.customer_id,

        -- FK to dim_product
        cast(md5(cast(i.product_id as varchar)) as varchar)             as product_sk,
        i.product_id,

        -- FK to dim_date
        cast(strftime(o.order_date, '%Y%m%d') as integer)               as order_date_key,
        o.order_date,

        -- Inherited order attributes (denormalised for convenience)
        o.status                                                        as order_status,
        case when o.status = 'completed' then true else false end       as is_completed,

        -- Quantities / amounts
        i.quantity,
        i.unit_price_nok,
        i.line_total_nok                                                as line_revenue_nok,
        cast(i.quantity * p.cost_nok as double)                         as line_cost_nok,
        cast(i.line_total_nok - (i.quantity * p.cost_nok) as double)    as line_profit_nok,

        case
            when i.line_total_nok = 0 or i.line_total_nok is null then null
            else (i.line_total_nok - (i.quantity * p.cost_nok)) / i.line_total_nok
        end                                                             as line_margin_pct

    from items     as i
    left join orders   as o on i.order_id = o.order_id
    left join products as p on i.product_id = p.product_id

)

select * from joined
