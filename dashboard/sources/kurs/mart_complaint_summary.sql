select
    date_trunc('month', c.created_at::timestamp)                    as maaned,
    c.category                                                       as klagekategori,
    count(*)                                                         as antall_klager,
    count(*) filter (where c.status = 'resolved')                   as antall_loste,
    round(avg(
        datediff('day', c.created_at, c.resolved_at)
    ) filter (where c.status = 'resolved'), 1)                      as snitt_behandlingstid_dager,
    round(
        100.0 * count(*) filter (where c.status = 'resolved') / count(*), 1
    )                                                                as prosent_lost
from main_raw.raw_complaints c
group by 1, 2
order by 1, 2
