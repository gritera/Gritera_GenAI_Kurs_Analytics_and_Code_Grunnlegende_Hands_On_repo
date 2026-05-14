with source as (
    select * from {{ ref('int_complaints_enriched') }}
),

monthly as (
    select
        date_trunc('month', created_at::timestamp)              as maaned,
        category                                                as klagekategori,
        count(*)                                                as antall_klager,
        count(*) filter (where is_resolved)                     as antall_loste,
        round(avg(days_to_resolve) filter (where is_resolved), 1)
                                                                as snitt_behandlingstid_dager,
        round(
            100.0 * count(*) filter (where is_resolved) / count(*),
            1
        )                                                       as prosent_lost
    from source
    group by 1, 2
)

select * from monthly
order by maaned, klagekategori
