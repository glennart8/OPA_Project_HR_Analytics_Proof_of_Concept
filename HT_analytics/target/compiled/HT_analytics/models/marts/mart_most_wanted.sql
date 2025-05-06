-- Visar inom vilket område flest tjänster finns (sorterat på group)
WITH mart_most_wanted AS (SELECT * FROM "job_ads"."refined"."fct_job_ads")

SELECT o.occupation_group
FROM mart_most_wanted m
JOIN refined.dim_occupation o ON m.occupation_id = o.occupation_id
JOIN refined.dim_employer e ON m.employer_id = e.employer_id
WHERE e.workplace_address__municipality = 'Göteborg'
GROUP BY o.occupation_group
ORDER BY SUM(m.vacancies) DESC
LIMIT 1