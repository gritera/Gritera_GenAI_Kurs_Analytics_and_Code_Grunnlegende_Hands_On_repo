select
    order_item_id,
    order_id,
    product_id,
    quantity,
    unit_price_nok,
    line_total_nok
from main_raw.raw_order_items
