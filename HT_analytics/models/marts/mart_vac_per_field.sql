WITH mart_vac_per_field AS (SELECT * FROM {{ref('fct_job_ads')}})

    SELECT
        SUM(m.vacancies) AS total_vacancies,
        o.occupation_field

    FROM mart_vac_per_field m
    LEFT JOIN refined.dim_occupation o ON m.occupation_id = o.occupation_id
    GROUP BY o.occupation_field
    ORDER BY total_vacancies DESC
    
