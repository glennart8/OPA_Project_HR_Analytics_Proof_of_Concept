with fct_job_ads as (select * from {{ref("src_job_ads")}})

select 
    occupation_id,
    job_details_id,
    employer_id,
    auxilliary_attributes_id,
    vacancies,
    relevance,
    application_deadline

from fct_job_ads