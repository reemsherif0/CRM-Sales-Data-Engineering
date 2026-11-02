with dates as (
    select cast(d as date) as full_date
    from generate_series(date '2016-01-01', date '2017-12-31', interval 1 day) as t(d)
)

select
    -1 as date_key,
    cast(null as date) as full_date,
    cast(null as integer) as year,
    cast(null as integer) as quarter,
    cast(null as integer) as month,
    'Not Available' as month_name,
    cast(null as integer) as day,
    'Not Available' as day_of_week

union all

select
    cast(strftime(full_date, '%Y%m%d') as integer) as date_key,
    full_date,
    year(full_date) as year,
    quarter(full_date) as quarter,
    month(full_date) as month,
    strftime(full_date, '%B') as month_name,
    day(full_date) as day,
    strftime(full_date, '%A') as day_of_week
from dates