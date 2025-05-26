WITH skills AS (
    SELECT DISTINCT skill_label
    FROM {{ ref('src_skills') }}
    WHERE skill_label IS NOT NULL
)

SELECT
    {{ dbt_utils.generate_surrogate_key(['skill_label']) }} AS skill_id,
    skill_label
FROM skills
