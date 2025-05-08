
  
  create view "job_ads"."marts"."mart_no_experience_req__dbt_tmp" as (
    WITH mart_no_experience AS (SELECT * FROM "job_ads"."refined"."fct_job_ads") 

SELECT
    -- jd.headline,                              -- headline                     från job_details
    a.experience_required,                       -- experience_required från     från auxillary
    jd.scope_of_work_min,                        -- employment_type              från job_details
    e.workplace_municipality,                    -- workplace_city               från employer
    o.occupation_group,                          -- occupation_group             från occupation
    m.vacancies                                  -- vacancies                    från fact

FROM mart_no_experience m
JOIN refined.dim_auxilliary_attributes a ON m.auxilliary_attributes_id = a.id_aux
JOIN refined.dim_job_details jd ON m.job_details_id = jd.job_details_id
JOIN refined.dim_employer e ON m.employer_id = e.employer_id
JOIN refined.dim_occupation o ON m.occupation_id = o.occupation_id

WHERE 
    a.experience_required = 'False'
    AND jd.scope_of_work_min < 100
    AND e.workplace_municipality = 'Göteborg'
    AND o.occupation_group LIKE '%lärare%'

-- GROUP BY 
--     a.experience_required,
--     jd.scope_of_work_min,
--     e.workplace_address__municipality,
--     o.occupation_group,
--     m.vacancies

ORDER BY
    m.vacancies DESC
  );
