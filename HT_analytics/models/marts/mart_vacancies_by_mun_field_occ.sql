WITH fct AS (
    SELECT *
    FROM {{ ref('fct_job_ads') }}
)


SELECT 
    f.job_details_id, -- Hitta ett annat unikt id för varje annons för att sedan kunna använda det i mart_vacancies_by_city
    o.occupation,
    o.occupation_field,
    e.employer_name,
    f.vacancies,
    e.employer_organization_number,
    LOWER(e.workplace_municipality) AS workplace_municipality  -- Behövs för filtrering
FROM fct f
JOIN refined.dim_employer e ON f.employer_id = e.employer_id
JOIN refined.dim_occupation o ON f.occupation_id = o.occupation_id
WHERE 
    e.workplace_municipality IS NOT NULL
    AND e.employer_name IS NOT NULL
    AND o.occupation IS NOT NULL
