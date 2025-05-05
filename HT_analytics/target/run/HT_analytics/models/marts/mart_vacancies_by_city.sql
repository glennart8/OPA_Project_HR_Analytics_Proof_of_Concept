
  
  create view "job_ads"."marts"."mart_vacancies_by_city__dbt_tmp" as (
    WITH mart_by_city AS (SELECT * FROM "job_ads"."refined"."fct_job_ads")

    SELECT 
        LOWER(e.workplace_city) AS city,
        SUM(m.vacancies) AS number_of_vacancies
        
    FROM mart_by_city m
    JOIN refined.dim_employer e ON m.employer_id = e.employer_id
    WHERE e.workplace_city IS NOT NULL
    GROUP BY LOWER(e.workplace_city)
    ORDER BY number_of_vacancies DESC
    

--------------------------
  );
