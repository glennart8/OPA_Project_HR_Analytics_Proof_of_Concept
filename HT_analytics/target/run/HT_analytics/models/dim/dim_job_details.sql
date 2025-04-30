
  
  create view "job_ads"."refined"."dim_job_details__dbt_tmp" as (
    WITH  __dbt__cte__src_job_details as (
with stg_job_details as (select * from "job_ads"."staging"."job_ads")

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
), job_details as (SELECT * FROM __dbt__cte__src_job_details)

select
    md5(cast(coalesce(cast(id as TEXT), '_dbt_utils_surrogate_key_null_') as TEXT)) as job_details_id,
    headline,
    description, 
    description_html_formatted,
    employment_type,
    duration,
    salary_type,
    scope_of_work_min,
    scope_of_work_max
from job_details
  );
