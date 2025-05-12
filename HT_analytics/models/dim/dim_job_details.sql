WITH job_details as (SELECT * FROM {{ref ('src_job_details')}})

select
    {{ dbt_utils.generate_surrogate_key(['id'])}} as job_details_id,
    headline,
    description, 
    description_html_formatted,
    employment_type,
    duration,
    salary_type,
    scope_of_work_min,
    scope_of_work_max,
    coalesce(webpage_url, 'url ej angiven') as webpage_url,
    coalesce(description_conditions, 'Ej specificerat') as description_conditions

from job_details