with employer as (select * from {{ ref('src_employer') }})

select 
    {{ dbt_utils.generate_surrogate_key(['employer_workplace', 'workplace_municipality']) }} as employer_id,
    coalesce(employer_name, 'namn ej angiven') as employer_name,
    coalesce(employer_workplace, 'plats ej angiven') as employer_workplace,
    coalesce(employer_organization_number, 'saknar organisationsnummer') as employer_organization_number,
    coalesce(workplace_municipality, 'kommun ej angiven') as workplace_municipality,
    coalesce(workplace_region, 'region ej angiven') as workplace_region,
    coalesce(workplace_country, 'land ej angiven') as workplace_country,
    coalesce(workplace_city, 'stad ej angiven') as workplace_city
from employer
