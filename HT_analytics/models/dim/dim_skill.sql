{# WITH skills as (SELECT * FROM {{ref ('src_skills')}}),
jobs as (SELECT * FROM {{ref ('src_job_ads')}})

Select
    {{ dbt_utils.generate_surrogate_key(['skill_id']) }} as skill_id,
    {{ dbt_utils.generate_surrogate_key(['occupation__label']) }} as
    occupation_id, 
    {{ dbt_utils.generate_surrogate_key(['id'])}} as job_details_id,
    {{ dbt_utils.generate_surrogate_key(['employer__workplace', 'workplace_address__municipality']) }} as employer_id,
    skill_label,
    occupation__label

from skills, jobs #}
{# WITH skills AS (
    SELECT * FROM {{ ref('src_skills') }}
)

SELECT
    {{ dbt_utils.generate_surrogate_key(['skill_id']) }} AS skill_id,
    MAX(COALESCE(skill_label, 'Namn ej angiven')) AS skill_label
FROM skills
GROUP BY skill_id #}

WITH skills AS (
    SELECT DISTINCT skill_label
    FROM {{ ref('src_skills') }}
)

SELECT
    {{ dbt_utils.generate_surrogate_key(['skill_label']) }} AS skill_id,
    skill_label
FROM skills