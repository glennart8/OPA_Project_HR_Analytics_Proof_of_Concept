with stg_employer as (select * from {{ source('job_ads', 'stg_ads') }})

select
    id, -- För att joina företaget
    employer__name as employer_name,
    employer__workplace as employer_workplace,
    employer_organization_number,
    workplace_street_address,
    workplace_region,
    workplace_postcode,
    workplace_city,
    workplace_country
from stg_employer