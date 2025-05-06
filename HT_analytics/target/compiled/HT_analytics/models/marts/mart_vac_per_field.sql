-- visa arbetsområden med flest arbetsannonser
-- visa annonser innehållande bygg (med LIKE %finsnickeri% i description typ) sortera på nyckelord
-- visa annonser innehållande specialområden inom sjukvård på samma sätt som ovan, t.ex: någon spec form av röntgen

-- visa inom vilken region flest arbeten inom kultur/media/pedagogik/bygg finns?
-- 3 kpi:er som visar antalet annonser inom respk. område


-- visar antalet tjänster per område - PGA APPEND SÅ DUBBLAS TJÄNSTERNA! WHAT TO DO!?!
WITH mart_vac_per_field AS (SELECT * FROM "job_ads"."refined"."fct_job_ads")

    SELECT
        SUM(m.vacancies) AS total_vacancies, -- COUNT ger 300 k tjänster, SUM ger 468k tjänster,
        o.occupation_field

    FROM mart_vac_per_field m
    JOIN refined.dim_occupation o ON m.occupation_id = o.occupation_id
    JOIN refined.dim_employer e ON m.employer_id = e.employer_id
    WHERE e.workplace_address__municipality = 'Göteborg'
    GROUP BY o.occupation_field
    ORDER BY total_vacancies DESC