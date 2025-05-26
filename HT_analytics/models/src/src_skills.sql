WITH must_have_skills AS (
    SELECT 
        _dlt_parent_id AS job_id,
        label AS skill_label,
        'must_have' AS skill_type
    FROM {{ source('job_ads', 'stg_skill') }}
),

nice_skills AS (
    SELECT 
        _dlt_parent_id AS job_id,
        label AS skill_label,
        'nice_to_have' AS skill_type
    FROM {{ source('job_ads', 'stg_nice_skill') }} 
)

SELECT
    job_id,
    skill_label,
    skill_type,
    -- Add a flag for easy filtering
    CASE WHEN skill_type = 'must_have' THEN true ELSE false END AS is_required_skill,
    CASE WHEN skill_type = 'nice_to_have' THEN true ELSE false END AS is_optional_skill
    
FROM must_have_skills

UNION ALL

SELECT
    job_id,
    skill_label,
    skill_type,
    CASE WHEN skill_type = 'must_have' THEN true ELSE false END AS is_required_skill,
    CASE WHEN skill_type = 'nice_to_have' THEN true ELSE false END AS is_optional_skill
    
FROM nice_skills

ORDER BY job_id, skill_type DESC, skill_label