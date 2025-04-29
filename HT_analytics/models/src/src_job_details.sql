with stg_job_details as (select * from {{ source('job_ads', 'stg_ads') }})

select
    id, -- För att joina job_details
    headline,
    description__text as description,
    description__text_formatted as description_html_formatted,
    employment_type__label as employment_type,
    duration__label as duration,
    salary_type__label as salary_type,
    scope_of_work__min as scope_of_work_min,
    scope_of_work__max as scope_of_work_max
from stg_job_details