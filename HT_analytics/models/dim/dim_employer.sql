with employer as (select * from {{ ref('src_employer') }})

select 
    {{ dbt_utils.generate_surrogate_key(['id'])}} as employer_id,
    employer_name,
    employer_workplace,
    employer_organization_number,
    workplace_street_adress,
    workplace_region,
    workplace_postcode,
    workplace_city,
    workplace_country
from employer