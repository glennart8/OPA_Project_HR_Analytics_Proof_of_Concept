with dim_occupation as (select * from {{ref ('src_occupation')}})

select
   {{dbt_utils.generate_surrogate_key(['occupation'])}} as occupation_id, -- För att joina yrke
    occupation,
    MAX(occupation_group) as occupation_group,
    MAX(occupation_field) as occupation_field
from dim_occupation
group by occupation



