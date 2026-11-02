select
    row_number() over (order by sales_agent_name) as sales_agent_key,
    sales_agent_name,
    manager,
    regional_office
from {{ ref('stg_sales_teams') }}