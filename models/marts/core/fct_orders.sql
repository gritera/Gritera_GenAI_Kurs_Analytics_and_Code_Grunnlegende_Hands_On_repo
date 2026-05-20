{{
    config(
        materialized='table',
        tags=['mart', 'core', 'fact']
    )
}}

/*
    fct_orders
    ----------
    Order-header fact table.

    Grain  : one row per order
    Use    : order-count metrics, AOV, conversion, status mix
    Keys
        order_id      — natural key
        customer_sk   — FK -> dim_customer.customer_sk
        order_date_key — FK -> dim_date.date_key

    Measures (sums)
        - order_total_nok    : header total (from source)
        - line_revenue_nok   : sum of order_items line_total (recomputed from rows)
        - line_cost_nok      : sum of order_items quantity * product cost
        - line_profit_nok    : revenue - cost
        - line_quantity      : sum of quantities in order
        - line_count         : number of distinct lines
*/

with orders as (

    select * from {{ ref('stg_orders') }}

),

items as (

    select
        oi.order_id,
        sum(oi.line_total_nok)                              as line_revenue_nok,
        sum(oi.quantity * p.cost_nok)                       as line_cost_nok,
        sum(oi.quantity)                                    as line_quantity,
        count(*)                                            as line_count
    from {{ ref('raw_order_items') }} as oi
    left join {{ ref('stg_products') }} as p
        on oi.product_id = p.product_id
    group by oi.order_id

),

joined as (

    select
        -- Keys
        o.order_id,
        cast(md5(cast(o.customer_id as varchar)) as varchar)                as customer_sk,
        o.customer_id,
        cast(strftime(o.order_date, '%Y%m%d') as integer)                   as order_date_key,
        o.order_date,

        -- Order attributes
        o.status                                                            as order_status,
        case
            when o.status = 'completed' then 'Fullført'
            when o.status = 'pending'   then 'Avventer'
            when o.status = 'returned'  then 'Returnert'
            else o.status
        end                                                                 as order_status_no,

        case when o.status = 'completed' then true else false end           as is_completed,
        case when o.status = 'returned'  then true else false end           as is_returned,

        -- Measures
        o.total_amount_nok                                                  as order_total_nok,
        coalesce(i.line_revenue_nok, 0)                                     as line_revenue_nok,
        coalesce(i.line_cost_nok,    0)                                     as line_cost_nok,
        coalesce(i.line_revenue_nok, 0) - coalesce(i.line_cost_nok, 0)      as line_profit_nok,
        coalesce(i.line_quantity, 0)                                        as line_quantity,
        coalesce(i.line_count,    0)                                        as line_count

    from orders        as o
    left join items    as i  on o.order_id = i.order_id

)

select * from joined
