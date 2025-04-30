with occupation as (select * from {{ref ('src_occupation')}})

select
   {{dbt_utils.generate_surrogate_key(['occupation_id'])}} as occupation_id, -- För att joina yrke
    occupation_group_id,
    occupation_field_id,
    occupation,
    occupation_group,
    occupation_field
from occupation