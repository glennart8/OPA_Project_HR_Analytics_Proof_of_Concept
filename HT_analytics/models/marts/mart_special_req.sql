{{ config(materialized='table') }}

-- Simple mart showing skills needed, job titles, municipalities, and employers
-- for jobs with special requirements (experience, license, or car access)

WITH base_job_data AS (
    
    SELECT 
        id as job_id,
        _dlt_id,
        occupation__label as job_title,
        employer__workplace as employer,
        workplace_address__municipality as municipality,
        experience_required,
        driving_license_required as driver_license,
        access_to_own_car
    FROM {{ source('job_ads', 'stg_ads') }}
    WHERE experience_required = true
       OR driving_license_required = true  
       OR access_to_own_car = true
),

skills AS (
    SELECT * FROM {{ ref('src_skills') }}
)


SELECT DISTINCT
    COALESCE(sk.skill_label, 'No specific skills listed') as skill_needed,
    COALESCE(sk.skill_type, 'none') as skill_requirement_type,
    jd.job_title,
    jd.municipality,
    jd.employer
    
FROM base_job_data jd
LEFT JOIN skills sk ON (
    jd.job_id = sk.job_id OR
    jd._dlt_id = sk.job_id 
)

ORDER BY 
    jd.municipality,
    jd.employer,
    jd.job_title,
    sk.skill_type DESC, 
    skill_needed