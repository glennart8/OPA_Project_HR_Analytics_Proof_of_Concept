with  __dbt__cte__src_occupation as (
with stg_occupation as (select * from "job_ads"."staging"."job_ads")

select
    occupation__concept_id as occupation_id, -- För att joina yrke
    occupation_group__concept_id as occupation_group_id,
    --occupation_field__concept_id as occupation_field_id,
    occupation__label as occupation,
    occupation_group__label as occupation_group,
    occupation_field__label as occupation_field,
from stg_occupation
), dim_occupation as (select * from __dbt__cte__src_occupation)

select
   md5(cast(coalesce(cast(occupation as TEXT), '_dbt_utils_surrogate_key_null_') as TEXT)) as occupation_id, -- För att joina yrke
    occupation,
    --occupation_field_id,
    MAX(occupation_group) as occupation_group,
    MAX(occupation_field) as occupation_field
from dim_occupation
group by occupation--, occupation_field_id