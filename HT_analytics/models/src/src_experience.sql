WITH stg_job_experience AS (
    SELECT * FROM {{ source('job_ads', 'stg_experience') }}
),

select
    _dlt_parent_id AS experience_id,
    label AS skill_label
from stg_job_experience