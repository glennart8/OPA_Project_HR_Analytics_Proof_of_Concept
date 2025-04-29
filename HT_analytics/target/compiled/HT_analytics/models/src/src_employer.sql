with stg_job_ads as (select * from "job_ads"."staging"."job_ads")

select
    id, -- För att joina företaget
    employer__name,
    employer__workplace,
    employer_organization_number,
    workplace_street_address,
    workplace_region,
    workplace_postcode,
    workplace_city,
    workplace_country
from stg_job_ads