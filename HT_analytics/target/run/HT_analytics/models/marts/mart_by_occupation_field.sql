
  
  create view "job_ads"."marts"."mart_by_occupation_field__dbt_tmp" as (
    -- or a specific occupation field (i.e. Data/IT), 
-- which occupation (i.e. data engineer) has a higher number of vacanies?

-- WITH mart_by_occfield AS (SELECT * FROM "job_ads"."refined"."fct_job_ads")

--     SELECT
--         o.occupation_id,
--         o.occupation_field, 
--         o.occupation, 
--         SUM(m.vacancies) as number_of_vacancies

--     FROM mart_by_occfield m
    
--     JOIN refined.dim_occupation o ON m.occupation_id = o.occupation_id
--     WHERE o.occupation_field_id = 'j7Cq_ZJe_GkT'
--     GROUP BY o.occupation_id, o.occupation_field, o.occupation
--     ORDER BY number_of_vacancies DESC
 
 ------------------------------------------

WITH mart_by_occfield AS (SELECT * FROM "job_ads"."refined"."fct_job_ads")

    SELECT
        o.occupation_id,
        o.occupation_field, 
        o.occupation, 
        MAX(m.vacancies) as highest_number_of_vacancies

    FROM mart_by_occfield m
    
    JOIN refined.dim_occupation o ON m.occupation_id = o.occupation_id
    WHERE o.occupation_field_id = 'j7Cq_ZJe_GkT'
    GROUP BY o.occupation_id, o.occupation_field, o.occupation
    ORDER BY highest_number_of_vacancies DESC
  );
