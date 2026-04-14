with source as (
    select * from {{ ref('raw_orders') }}
),

renamed as (
    select
        order_id,
        customer_id,
        cast(order_date as date) as order_date,
        status,
        total_amount_nok
    from source
)

select * from renamed
