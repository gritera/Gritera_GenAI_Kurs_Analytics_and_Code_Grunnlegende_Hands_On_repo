select
    c.complaint_id,
    c.category                                                          as kategori,
    c.status,
    c.created_at,
    c.resolved_at,
    datediff('day', c.created_at, c.resolved_at)                        as dager_til_losning,
    c.description                                                       as beskrivelse,
    cu.full_name                                                        as kunde,
    cu.region,
    o.order_date,
    o.total_amount_nok
from main_raw.raw_complaints c
left join main.stg_customers cu on c.customer_id = cu.customer_id
left join main.stg_orders    o  on c.order_id    = o.order_id
order by c.created_at desc
