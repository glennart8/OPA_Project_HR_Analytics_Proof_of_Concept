
  
  create view "job_ads"."main"."src_job_ads__dbt_tmp" as (
    with stg_job_ads as (select * from "job_ads"."staging"."job_ads")

select
    occupation__label, -- För att joina fact-tabell
    id,
    employer__workplace,
    workplace_address__municipality,
    auxilliary_attributes,

    number_of_vacancies as vacancies,
    relevance,
    application_deadline
from stg_job_ads
  );
