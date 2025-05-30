WITH mart_chosen_vacancy AS (SELECT * FROM {{ref('fct_job_ads')}}) 

SELECT
    jd.headline,                                 
    jd.description,                                         
    jd.employment_type,
    jd.duration,
    jd.salary_type,
    jd.scope_of_work_min,
    jd.scope_of_work_max,    
    jd.webpage_url,
    jd.description_conditions,                            
    a.experience_required,
    a.driver_license,    
    m.publication_date,
    m.application_deadline

FROM mart_chosen_vacancy m
JOIN refined.dim_auxilliary_attributes a ON m.auxilliary_attributes_id = a.id_aux
JOIN refined.dim_job_details jd ON m.job_details_id = jd.job_details_id
