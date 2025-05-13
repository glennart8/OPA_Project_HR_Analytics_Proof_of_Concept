WITH mart_spec_req AS (SELECT * FROM {{ ref('fct_job_ads') }})

SELECT 
    m.job_details_id,
    o.occupation_id,
    o.occupation_field,
    o.occupation,
    MAX(m.vacancies) AS Highest_vacancies,

FROM mart_spec_req m

JOIN refined.dim_occupation o ON m.occupation_id = o.occupation_id

WHERE LOWER(jd.jo) LIKE '%Röntgen % '
   -- OR LOWER(o.occupation) LIKE '%radiolog%'

GROUP BY m.job_details_id, o.occupation_id, o.occupation_field, o.occupation
ORDER BY Highest_vacancies DESC
