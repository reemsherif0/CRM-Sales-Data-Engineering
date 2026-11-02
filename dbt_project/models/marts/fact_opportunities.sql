-- depends_on: {{ ref('dim_date') }}
select
    p.opportunity_id,
    coalesce(a.account_key, -1) as account_key,
    pr.product_key,
    ag.sales_agent_key,
    coalesce(cast(strftime(p.engage_date, '%Y%m%d') as integer), -1) as engage_date_key,
    coalesce(cast(strftime(p.close_date, '%Y%m%d') as integer), -1) as close_date_key,
    p.deal_stage,
    p.close_value
from {{ ref('stg_sales_pipeline') }} as p
left join {{ ref('dim_account') }} as a
    on p.account_name = a.account_name
left join {{ ref('dim_product') }} as pr
    on p.product_name = pr.product_name
left join {{ ref('dim_sales_agent') }} as ag
    on p.sales_agent_name = ag.sales_agent_name