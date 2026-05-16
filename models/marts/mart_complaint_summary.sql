with enriched as (
    select * from {{ ref('int_complaints_enriched') }}
)

select
    date_trunc('month', created_at)::date                              as month,
    complaint_category                                                 as kategori,
    count(*)                                                           as total_complaints,
    count(*) filter (where status = 'resolved')                       as resolved_count,
    -- NULL-safe: FILTER restricts to resolved rows only;
    -- DATE - DATE returns integer days in DuckDB
    avg(resolved_at - created_at) filter (where status = 'resolved')  as avg_handling_days

from enriched
group by 1, 2
order by 1, 2
