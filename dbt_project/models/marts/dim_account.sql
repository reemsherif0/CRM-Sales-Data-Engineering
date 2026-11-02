with accounts as (
    select
        row_number() over (order by account_name) as account_key,
        *
    from {{ ref('stg_accounts') }}
)

select
    -1 as account_key,
    'Unknown' as account_name,
    cast(null as varchar) as sector,
    cast(null as bigint) as year_established,
    cast(null as double) as revenue_musd,
    cast(null as bigint) as employees,
    cast(null as varchar) as office_location,
    cast(null as varchar) as parent_account_name

union all

select
    account_key,
    account_name,
    sector,
    year_established,
    revenue_musd,
    employees,
    office_location,
    parent_account_name
from accounts