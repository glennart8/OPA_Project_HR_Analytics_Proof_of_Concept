WITH job_base AS (
    SELECT
        f.id AS job_id,
        f.vacancies,
        f.publication_date,
        e.workplace_municipality,
        f.job_details_id
    FROM {{ ref('fct_job_ads') }} f
    JOIN {{ ref('dim_employer') }} e ON f.employer_id = e.employer_id
    WHERE e.workplace_municipality = 'Göteborg'
      AND f.publication_date >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '3 months'
),

skill_tags AS (
    SELECT
        _dlt_parent_id AS job_details_id,
        label AS skill_label
    FROM {{ ref('src_experience') }}
),

combined_skills AS (
    SELECT
        jb.job_id,
        DATE_TRUNC('month', jb.publication_date) AS month,
        jb.vacancies,
        st.skill_label
    FROM job_base jb
    LEFT JOIN skill_tags st ON jb.job_details_id = st.job_details_id
),

monthly_skills_agg AS (
    SELECT
        skill_label,
        month,
        COUNT(DISTINCT job_id) AS num_ads,
        SUM(vacancies) AS total_vacancies
    FROM combined_skills
    GROUP BY skill_label, month
),

with_change AS (
    SELECT
        skill_label,
        month,
        total_vacancies,
        LAG(total_vacancies) OVER (PARTITION BY skill_label ORDER BY month) AS prev_month_vacancies
    FROM monthly_skills_agg
)

SELECT
    skill_label,
    month,
    total_vacancies,
    prev_month_vacancies,
    CAST(
        100.0 * (total_vacancies - prev_month_vacancies) / NULLIF(prev_month_vacancies, 0) AS INTEGER
    ) || '%' AS percent_change
FROM with_change
WHERE prev_month_vacancies IS NOT NULL
ORDER BY percent_change DESC, month
