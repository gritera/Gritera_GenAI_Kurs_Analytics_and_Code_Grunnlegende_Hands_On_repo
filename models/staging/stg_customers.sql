with source as (
    select * from {{ ref('raw_customers') }}
),

renamed as (
    select
        customer_id,
        first_name,
        last_name,
        first_name || ' ' || last_name as full_name,
        email,
        region,
        cast(created_at as date) as created_at,
        is_active
    from source
)

select * from renamed
