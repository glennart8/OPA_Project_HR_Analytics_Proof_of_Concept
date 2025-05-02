with stg_job_ads as (select * from {{ source('job_ads', 'stg_ads') }})

select
    occupation__label, -- Varför använder vi denna i stället för id??
    id, -- för job_details
    -- id_aux, -- HUR SKAPA ID:N???
    employer__workplace,
    workplace_address__municipality,
    number_of_vacancies as vacancies,
    relevance,
    application_deadline,
    experience_required,
    driving_license_required as driver_license,
    access_to_own_car
from stg_job_ads