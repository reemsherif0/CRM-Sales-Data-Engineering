select f.n as fact_rows, s.n as staging_rows
from (select count(*) as n from {{ ref('fact_opportunities') }}) f
cross join (select count(*) as n from {{ ref('stg_sales_pipeline') }}) s
where f.n <> s.n