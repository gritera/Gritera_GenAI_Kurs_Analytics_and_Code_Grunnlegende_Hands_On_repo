{{
    config(
        materialized='table',
        tags=['mart', 'core', 'dimension']
    )
}}

/*
    dim_date
    --------
    Conformed Date dimension.

    Grain  : one row per calendar day
    Range  : 2023-01-01 .. 2025-12-31  (covers all order_dates plus buffer)

    All Power BI time-intelligence measures join via date_key (INTEGER, YYYYMMDD).
*/

with date_spine as (

    select
        cast(d as date) as date_day
    from
        range(
            date '2023-01-01',
            date '2026-01-01',
            interval 1 day
        ) as t(d)

),

enriched as (

    select
        -- Integer surrogate key for relationships (YYYYMMDD)
        cast(strftime(date_day, '%Y%m%d') as integer)                          as date_key,

        -- The date itself
        date_day                                                               as date,

        -- Year/quarter/month/day breakdown
        cast(extract(year   from date_day) as integer)                         as year,
        cast(extract(quarter from date_day) as integer)                        as quarter_no,
        'K' || cast(extract(quarter from date_day) as varchar)                 as quarter_label,
        cast(extract(year from date_day) as varchar) || '-K' ||
            cast(extract(quarter from date_day) as varchar)                    as year_quarter,
        cast(extract(month from date_day) as integer)                          as month_no,
        strftime(date_day, '%Y-%m')                                            as year_month,
        strftime(date_day, '%B')                                               as month_name,
        strftime(date_day, '%b')                                               as month_name_short,

        -- Week
        cast(extract(week from date_day) as integer)                           as iso_week,
        strftime(date_day, '%Y') || '-U' || strftime(date_day, '%V')           as year_week,

        -- Day attributes
        cast(extract(day      from date_day) as integer)                       as day_of_month,
        cast(extract(dayofyear from date_day) as integer)                      as day_of_year,
        cast(extract(isodow   from date_day) as integer)                       as day_of_week_no,
        strftime(date_day, '%A')                                               as day_name,
        case
            when extract(isodow from date_day) in (6, 7) then true
            else false
        end                                                                    as is_weekend,

        -- Relative flags useful for "today / yesterday / current month"
        case when date_day = current_date                       then true else false end as is_today,
        case when date_trunc('month',  date_day) = date_trunc('month',  current_date) then true else false end as is_current_month,
        case when extract(year from date_day)  = extract(year from current_date)      then true else false end as is_current_year

    from date_spine

)

select * from enriched
order by date
