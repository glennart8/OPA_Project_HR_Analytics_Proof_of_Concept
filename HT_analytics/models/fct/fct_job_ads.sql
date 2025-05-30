 with fct_job_ads as (
  select * from {{ ref('src_job_ads') }}
)

select         -- här hade vi tidigare 'occupation' i stälet eftersom vi bytt namn i source, det skulle man tydligen inte ha. VET INTE VARFÖR!?!
  {{ dbt_utils.generate_surrogate_key(['occupation__label']) }} as occupation_id, 
  {{ dbt_utils.generate_surrogate_key(['id'])}} as job_details_id,
  {{ dbt_utils.generate_surrogate_key(['employer__workplace', 'workplace_address__municipality']) }} as employer_id,
  {{ dbt_utils.generate_surrogate_key(['experience_required','driver_license','access_to_own_car'])}} as auxilliary_attributes_id,
  vacancies,
  relevance,
  application_deadline,
  publication_date
from fct_job_ads