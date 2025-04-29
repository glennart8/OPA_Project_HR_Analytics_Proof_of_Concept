with stg_employer as (select * from "job_ads"."staging"."job_ads")

select
    id, -- För att joina företaget
    employer__name as employer_name,
    employer__workplace as employer_workplace,
    employer__organization_number as employer_organization_number,
    workplace_address__street_address as workplace_street_adress,
    workplace_address__region as workplace_region,
    workplace_address__postcode as workplace_postcode,
    workplace_address__city as workplace_city,
    workplace_address__country as workplace_country
from stg_employer