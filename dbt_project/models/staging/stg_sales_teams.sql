select
    sales_agent as sales_agent_name,
    manager,
    regional_office
from {{ source('raw', 'sales_teams') }}