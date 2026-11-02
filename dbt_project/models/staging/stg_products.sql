select
    product as product_name,
    series,
    sales_price
from {{ source('raw', 'products') }}