with stg_occupation as (select * from {{ source('job_ads', 'stg_ads') }})

select
    occupation__concept_id as occupation_id, -- För att joina yrke
    occupation_group__concept_id as occupation_group_id,
    occupation__label as occupation,
    occupation_group__label as occupation_group,
    occupation_field__label as occupation_field,
from stg_occupation