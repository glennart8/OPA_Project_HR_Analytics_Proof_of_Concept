with employer as (
  select * from {{ ref('src_employer') }}
)

select 
    {{ dbt_utils.generate_surrogate_key(['employer_workplace', 'workplace_municipality']) }} as employer_id,
    MAX(coalesce(employer_name, 'namn ej angiven')) as employer_name,
    MAX(coalesce(employer_organization_number, 'saknar organisationsnummer')) as employer_organization_number,
    coalesce(employer_workplace, 'plats ej angiven') as employer_workplace,
    coalesce(workplace_municipality, 'kommun ej angiven') as workplace_municipality,
    MAX(coalesce(workplace_region, 'region ej angiven')) as workplace_region,
    MAX(coalesce(workplace_country, 'land ej angiven')) as workplace_country,
    MAX(coalesce(workplace_city, 'stad ej angiven')) as workplace_city,
    MAX(coalesce(employer_url, 'url ej angiven')) as employer_url
from employer
group by employer_workplace, workplace_municipality
