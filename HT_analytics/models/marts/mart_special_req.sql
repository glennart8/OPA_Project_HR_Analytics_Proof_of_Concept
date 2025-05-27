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
    -- Load skills from the source table
skills AS (
    SELECT * FROM {{ ref('src_skills') }}
),
    -- create driver license as a skill
driver_license_skills AS (
    SELECT 
        job_id,
        'Driver License' as skill_label,
        'must_have' as skill_type
    FROM base_job_data 
    WHERE driver_license = true
    
    UNION ALL
    
    SELECT  
        _dlt_id as job_id,
        'Driver License' as skill_label,
        'must_have' as skill_type
    FROM base_job_data 
    WHERE driver_license = true AND _dlt_id IS NOT NULL
),

    -- create car access as a skill
car_access_skills AS (
    SELECT 
        job_id,
        'Access to Own Car' as skill_label,
        'must_have' as skill_type
    FROM base_job_data 
    WHERE access_to_own_car = true
    
    UNION ALL
    
    SELECT 
        _dlt_id as job_id,
        'Access to Own Car' as skill_label,
        'must_have' as skill_type
    FROM base_job_data 
    WHERE access_to_own_car = true AND _dlt_id IS NOT NULL
),

-- Combine all skills
all_skills AS (
    SELECT skill_label, skill_type, job_id FROM skills
    UNION ALL
    SELECT skill_label, skill_type, job_id FROM driver_license_skills
    UNION ALL
    SELECT skill_label, skill_type, job_id FROM car_access_skills
)

SELECT DISTINCT
    COALESCE(sk.skill_label, 'No specific skills listed') as skill_needed,
    COALESCE(sk.skill_type, 'none') as skill_requirement_type,
    jd.job_title,
    jd.municipality,
    jd.employer
    
FROM base_job_data jd
LEFT JOIN all_skills sk ON (
    jd.job_id = sk.job_id OR
    jd._dlt_id = sk.job_id 
)

ORDER BY 
    jd.municipality,
    jd.employer,
    jd.job_title,
    sk.skill_type DESC, 
    skill_needed