select f.total as fact_total, s.total as staging_total
from (select coalesce(sum(close_value), 0) as total from {{ ref('fact_opportunities') }}) f
cross join (select coalesce(sum(close_value), 0) as total from {{ ref('stg_sales_pipeline') }}) s
where f.total <> s.total