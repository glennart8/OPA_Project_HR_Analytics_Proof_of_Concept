-- models/fct/fct_job_skill.sql

WITH job_ads AS (
    SELECT * FROM {{ ref('src_job_ads') }}
),
skills AS (
    SELECT * FROM {{ ref('src_skills') }}
)

SELECT
    {{ dbt_utils.generate_surrogate_key(['j.id']) }} AS job_details_id,
    {{ dbt_utils.generate_surrogate_key(['j.occupation__label']) }} AS occupation_id,
    {{ dbt_utils.generate_surrogate_key(['j.employer__workplace', 'j.workplace_address__municipality']) }} AS employer_id,
    {{ dbt_utils.generate_surrogate_key(['s.skill_label']) }} AS skill_id
FROM skills s
left JOIN job_ads j
    ON s.skill_id = j.id
