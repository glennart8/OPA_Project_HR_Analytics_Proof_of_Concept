WITH stg_experience AS (
    SELECT * FROM {{ source('job_ads__must_have__skills', 'stg_ads') }}
),

select
    _dlt_parent_id AS experience_id,
    label AS skill_label
    
    FROM stg_experience

