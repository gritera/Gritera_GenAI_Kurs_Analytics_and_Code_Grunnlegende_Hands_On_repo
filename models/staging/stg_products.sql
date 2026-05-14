with source as (
    select * from {{ ref('raw_products') }}
),

renamed as (
    select
        product_id,
        product_name,
        category,
        cast(price_nok as numeric) as price_nok,
        cast(cost_nok as numeric) as cost_nok,
        supplier,
        cast(is_available as boolean) as is_available,
        cast(created_at as date) as created_at
    from source
)

select * from renamed
