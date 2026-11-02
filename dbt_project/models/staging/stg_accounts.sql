select
    account as account_name,
    case when sector = 'technolgy' then 'technology' else sector end as sector,
    year_established,
    revenue as revenue_musd,
    employees,
    case when office_location = 'Philipines' then 'Philippines'
        else office_location end as office_location,
    subsidiary_of as parent_account_name
from {{ source('raw', 'accounts') }}