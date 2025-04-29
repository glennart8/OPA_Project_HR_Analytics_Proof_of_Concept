with stg_job_ads as (select * from "job_ads"."staging"."job_ads")

select
    occupation__label, -- För att joina fact-tabell
    id,
    employer__workplace,
    workplace_address__municipality,
    number_of_vacancies as vacancies,
    relevance,
    application_deadline
from stg_job_ads