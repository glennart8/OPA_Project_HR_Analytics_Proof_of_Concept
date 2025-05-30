WITH mart_by_occfield AS (SELECT * FROM {{ref('fct_job_ads')}})

    SELECT
        o.occupation_id,
        o.occupation_field, 
        o.occupation, 
        MAX(m.vacancies) as highest_number_of_vacancies

    FROM mart_by_occfield m
    
    JOIN refined.dim_occupation o ON m.occupation_id = o.occupation_id
    --WHERE o.occupation_field_id = 'j7Cq_ZJe_GkT'
    WHERE o.occupation_field = 'Bygg och anläggning'
    GROUP BY o.occupation_id, o.occupation_field, o.occupation
    ORDER BY highest_number_of_vacancies DESC