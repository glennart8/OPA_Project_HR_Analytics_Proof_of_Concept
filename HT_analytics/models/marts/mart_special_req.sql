with mart_special_req as (select * from {{ ref('fct_job_skill') }})

select
    jd.headline,
    s.skill_label,
    o.occupation_group,
    e.workplace_municipality,

from mart_special_req m
join refined.dim_job_details jd on m.job_details_id = jd.job_details_id
join refined.dim_employer e on m.employer_id = e.employer_id
join refined.dim_occupation o on m.occupation_id = o.occupation_id
join refined.dim_skill s on m.skill_id = s.skill_id
