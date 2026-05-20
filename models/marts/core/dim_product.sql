{{
    config(
        materialized='table',
        tags=['mart', 'core', 'dimension']
    )
}}

/*
    dim_product
    -----------
    Conformed product dimension.

    Grain  : one row per product (current snapshot)
    Source : stg_products
    Keys
        product_sk   — surrogate key (md5 hash of product_id)
        product_id   — natural / business key

    Business attributes
        - Product name, category, supplier
        - List price, standard cost, list margin
        - Price tier (Lav / Middels / Premium)
        - Availability flag
*/

with products as (

    select * from {{ ref('stg_products') }}

),

enriched as (

    select
        -- Surrogate key
        cast(md5(cast(product_id as varchar)) as varchar)              as product_sk,

        -- Natural key
        product_id,

        -- Descriptive attributes
        product_name,
        coalesce(category, 'Ukjent')                                   as category,
        coalesce(supplier, 'Ukjent')                                   as supplier,

        -- Economics (list)
        price_nok                                                      as list_price_nok,
        cost_nok                                                       as standard_cost_nok,
        cast(price_nok - cost_nok as double)                           as list_margin_nok,

        case
            when price_nok = 0 or price_nok is null then null
            else (price_nok - cost_nok) / price_nok
        end                                                            as list_margin_pct,

        -- Price tier
        case
            when price_nok < 50  then 'Lav'
            when price_nok < 80  then 'Middels'
            else                      'Premium'
        end                                                            as price_tier,

        -- Status
        is_available,
        case when is_available then 'Tilgjengelig' else 'Utgått' end   as availability_status,

        created_at                                                     as product_launch_date,
        cast(extract(year from created_at) as integer)                 as launch_year

    from products

)

select * from enriched
