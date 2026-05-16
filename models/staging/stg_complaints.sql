with source as (
    select * from {{ ref('raw_complaints') }}
),

renamed as (
    select
        complaint_id,
        customer_id,
        order_id,
        category,
        description,
        status,
        cast(created_at as date)  as created_at,
        cast(resolved_at as date) as resolved_at
    from source
)

select * from renamed
