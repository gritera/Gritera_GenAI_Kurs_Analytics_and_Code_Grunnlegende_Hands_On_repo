with complaints as (
    select * from {{ ref('raw_complaints') }}
),

customers as (
    select * from {{ ref('stg_customers') }}
),

orders as (
    select * from {{ ref('stg_orders') }}
),

enriched as (
    select
        c.complaint_id,
        c.category,
        c.description,
        c.status,
        c.created_at,
        c.resolved_at,
        case
            when c.resolved_at is not null
            then datediff('day', c.created_at, c.resolved_at)
        end as days_to_resolve,
        c.status = 'resolved' as is_resolved,
        cu.full_name as customer_name,
        cu.region,
        o.order_date,
        o.total_amount_nok
    from complaints c
    left join customers cu on c.customer_id = cu.customer_id
    left join orders o on c.order_id = o.order_id
)

select * from enriched
