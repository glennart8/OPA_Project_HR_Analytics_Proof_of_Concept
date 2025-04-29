
  
  create view "job_ads"."main"."src_occupation__dbt_tmp" as (
    with stg_job_ads as (select * from "job_ads"."staging"."job_ads")

select
    occupation__concept_id as occupation_id, -- För att joina yrke
    occupation_group__concept_id as occupation_group_id,
    occupation_field__concept_id as occupation_field_id,
    occupation__label as occupation,
    occupation_group__label as occupation_group,
    occupation_field__label as occupation_field,
from stg_job_ads
  );
