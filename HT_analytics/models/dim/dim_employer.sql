with employer as (select * from {{ ref('src_employer') }})

select 
    {{ dbt_utils.generate_surrogate_key(['id'])}} as employer_id,
    employer__name,
    employer__workplace,
    employer_organization_number,
    workplace_street_address,
    workplace_region,
    workplace_postcode,
    workplace_city,
    workplace_country
from employer