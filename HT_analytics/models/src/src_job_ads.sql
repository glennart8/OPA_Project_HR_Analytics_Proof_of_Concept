with stg_job_ads as (select * from {{ source('job_ads', 'stg_ads') }})

select
    -- 
    --occupation__concept_id, -- för att joina med yrke
    occupation__label,
    id, -- för job_details
    employer__workplace,
    workplace_address__municipality,
    number_of_vacancies as vacancies,
    relevance,
    application_deadline,
    experience_required, -- Var tvugna att ha dessa här för att kunna hämta dem i fct
    driving_license_required as driver_license,
    access_to_own_car,
    publication_date,

from stg_job_ads