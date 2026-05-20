{{
    config(
        materialized='table',
        tags=['mart', 'core', 'dimension']
    )
}}

/*
    dim_customer
    ------------
    Conformed customer dimension.

    Grain  : one row per customer (current snapshot)
    Source : stg_customers
    Keys
        customer_sk  — surrogate key (md5 hash of customer_id)
        customer_id  — natural / business key (BIGINT from source)

    Business attributes
        - Full name, email, region
        - Customer segment derived from tenure
        - Acquisition cohort (year-month of created_at)
        - Active flag
*/

with customers as (

    select * from {{ ref('stg_customers') }}

),

enriched as (

    select
        -- Surrogate key (md5 hash for analytics)
        cast(md5(cast(customer_id as varchar)) as varchar)        as customer_sk,

        -- Natural key
        customer_id,

        -- Descriptive attributes
        first_name,
        last_name,
        full_name,
        email,
        coalesce(region, 'Ukjent')                                as region,

        -- Dates
        created_at                                                as customer_since_date,
        date_trunc('month', created_at)::date                     as acquisition_month,
        cast(strftime(created_at, '%Y-%m') as varchar)            as acquisition_cohort,
        cast(extract(year from created_at) as integer)            as acquisition_year,

        -- Status flag
        is_active,
        case when is_active then 'Aktiv' else 'Inaktiv' end       as customer_status,

        -- Tenure-based segment (days since signup, as of dbt run time)
        case
            when date_diff('day', created_at, current_date) < 180  then 'Ny kunde'
            when date_diff('day', created_at, current_date) < 365  then 'Etablert'
            else                                                        'Lojal'
        end                                                       as tenure_segment

    from customers

)

select * from enriched
