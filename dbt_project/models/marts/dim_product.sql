select
    row_number() over (order by product_name) as product_key,
    product_name,
    series,
    sales_price
from {{ ref('stg_products') }}