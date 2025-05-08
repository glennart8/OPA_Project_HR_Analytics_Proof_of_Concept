WITH mart_by_mun_field_occ AS (
    SELECT *
    FROM {{ ref('fct_job_ads') }}
)

SELECT 
    LOWER(e.workplace_municipality) AS workplace_municipality,
    o.occupation_field,
    o.occupation,
    SUM(m.vacancies) AS total_vacancies

FROM mart_by_mun_field_occ m
JOIN refined.dim_employer e ON m.employer_id = e.employer_id
JOIN refined.dim_occupation o ON m.occupation_id = o.occupation_id

WHERE 
    e.workplace_municipality IS NOT NULL
    AND o.occupation_field IS NOT NULL
    AND o.occupation IS NOT NULL

GROUP BY 
    LOWER(e.workplace_municipality),
    o.occupation_field,
    o.occupation

ORDER BY 
    total_vacancies DESC
