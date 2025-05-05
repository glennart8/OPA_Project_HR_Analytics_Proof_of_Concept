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
    access_to_own_car
from stg_job_ads