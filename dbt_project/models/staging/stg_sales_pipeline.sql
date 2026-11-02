select
    opportunity_id,
    sales_agent as sales_agent_name,
    case when product = 'GTXPro' then 'GTX Pro' else product end as product_name,
    account as account_name,
    deal_stage,
    engage_date,
    close_date,
    close_value
from {{ source('raw', 'sales_pipeline') }}