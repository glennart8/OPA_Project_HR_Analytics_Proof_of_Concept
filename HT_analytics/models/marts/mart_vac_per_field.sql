-- visa arbetsområden med flest arbetsannonser
-- visa annonser innehållande bygg (med LIKE %finsnickeri% i description typ) sortera på nyckelord
-- visa annonser innehållande specialområden inom sjukvård på samma sätt som ovan, t.ex: någon spec form av röntgen

-- visa inom vilken region flest arbeten inom kultur/media/pedagogik/bygg finns?
-- 3 kpi:er som visar antalet annonser inom respk. område


-- visar antalet tjänster per område - PGA APPEND SÅ DUBBLAS TJÄNSTERNA! WHAT TO DO!?!
WITH mart_vac_per_field AS (SELECT * FROM {{ref('fct_job_ads')}})

    SELECT
        SUM(m.vacancies) AS total_vacancies,
        o.occupation_field

    FROM mart_vac_per_field m
    LEFT JOIN refined.dim_occupation o ON m.occupation_id = o.occupation_id
    GROUP BY o.occupation_field
    ORDER BY total_vacancies DESC
    
