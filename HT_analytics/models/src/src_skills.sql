WITH stg_job_skill AS (SELECT * FROM {{ source('job_ads', 
'stg_skill') }})

select
    _dlt_parent_id AS skill_id,
    label AS skill_label
from stg_job_skill