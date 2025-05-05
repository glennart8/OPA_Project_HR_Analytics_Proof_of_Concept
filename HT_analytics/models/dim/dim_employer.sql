with employer as (select * from {{ ref('src_employer') }})

select 
    {{ dbt_utils.generate_surrogate_key(['employer_workplace', 'workplace_address__municipality']) }} as employer_id,
    employer_name,
    employer_workplace,
    employer_organization_number,
    workplace_address__municipality,
    workplace_street_address,
    workplace_region,
    workplace_postcode,
    workplace_city,
    workplace_country
from employer
