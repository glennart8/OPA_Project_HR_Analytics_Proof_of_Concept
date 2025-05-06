with  __dbt__cte__src_job_ads as (
with stg_job_ads as (select * from "job_ads"."staging"."job_ads")

select
    -- 
    occupation__concept_id, -- för att joina med yrke
    id, -- för job_details
    -- id_aux, -- HUR SKAPA ID:N???
    employer__workplace,
    workplace_address__municipality,
    number_of_vacancies as vacancies,
    relevance,
    application_deadline,
    experience_required, -- Var tvugna att ha dessa här för att kunna hämta dem i fct
    driving_license_required as driver_license,
    access_to_own_car,
    publication_date
from stg_job_ads
), fct_job_ads as (select * from __dbt__cte__src_job_ads)

select 
    md5(cast(coalesce(cast(occupation__concept_id as TEXT), '_dbt_utils_surrogate_key_null_') as TEXT)) AS occupation_id,
    md5(cast(coalesce(cast(id as TEXT), '_dbt_utils_surrogate_key_null_') as TEXT)) as job_details_id,
    md5(cast(coalesce(cast(employer__workplace as TEXT), '_dbt_utils_surrogate_key_null_') || '-' || coalesce(cast(workplace_address__municipality as TEXT), '_dbt_utils_surrogate_key_null_') as TEXT)) as employer_id,
    md5(cast(coalesce(cast(experience_required as TEXT), '_dbt_utils_surrogate_key_null_') || '-' || coalesce(cast(driver_license as TEXT), '_dbt_utils_surrogate_key_null_') || '-' || coalesce(cast(access_to_own_car as TEXT), '_dbt_utils_surrogate_key_null_') as TEXT)) as auxilliary_attributes_id,
    vacancies,
    relevance,
    application_deadline,
    publication_date

from fct_job_ads


-- md5(cast(coalesce(cast(occupation__concept_id as TEXT), '_dbt_utils_surrogate_key_null_') as TEXT)) AS occupation_id
-- md5(cast(coalesce(cast(occupation__label as TEXT), '_dbt_utils_surrogate_key_null_') as TEXT)) as occupation_id,