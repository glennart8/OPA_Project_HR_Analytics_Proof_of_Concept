-- visa procentuell ökning/minskning jämför med tidigare år? Visar ju bara aktiva annonser vilket inte gör det möjligt...

-- jämför antalet annonser inom respk. arbetsområde sett över tid (3 mån), visa ökningen i procent?

-- 1. Filtrera annonser publicerade de senaste 3 månaderna
-- 2. Gruppera på både månad och yrkesgrupp
-- 3. Summera antal tjänster (vacancies)
-- 4. Räkna månatlig procentuell förändring per grupp

--Hög procentull ökningar visar på trender, medan 0 eller låg procent visar att en viss yrkesgrupp har svårt att tillsätta personal 

WITH mart_trends AS (
    SELECT 
        m.vacancies,
        o.occupation_group,
       -- o.occupation_field_id,
        DATE_TRUNC('month', m.publication_date) AS month -- DATE_TRUNC används för att hämta månad och år från publiceringsdatumet
    FROM "job_ads"."refined"."fct_job_ads" m
    JOIN refined.dim_occupation o ON m.occupation_id = o.occupation_id
    JOIN refined.dim_employer e ON m.employer_id = e.employer_id
    WHERE e.workplace_municipality = 'Göteborg'
      AND m.publication_date >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '3 months'
      --AND o.occupation_field_id = 'j7Cq_ZJe_GkT' -- Visar endast 'Bygg och anläggning'
      
),

-- visar månatliga totalsummor av tjänster per yrkesgrupp
monthly_totals AS (
    SELECT
        occupation_group,
        month,
        SUM(vacancies) AS total_vacancies -- SUM() används för att summera antalet tjänster per månad och yrkesgrupp
    FROM mart_trends
    GROUP BY occupation_group, month
),

-- visar månatliga totalsummor av tjänster per yrkesgrupp MED FÖRGÅENDE månads värde
with_change AS (
    SELECT
        occupation_group,
        month,
        total_vacancies,
        LAG(total_vacancies) OVER (PARTITION BY occupation_group ORDER BY month) AS prev_month_vacancies -- LAG() används för att hämta värdet från föregående månad
    FROM monthly_totals
)

-- visar månatliga totalsummor av tjänster per yrkesgrupp MED FÖRGÅENDE månads värde och procentuell förändring
SELECT
    occupation_group,
    month,
    total_vacancies,
    prev_month_vacancies,
    CAST( 
        100.0 * (total_vacancies - prev_month_vacancies) / NULLIF(prev_month_vacancies, 0) AS INTEGER -- NULLIF - undvika division med noll, AS INTEGER - konvertera till heltal 
    ) || '%' AS percent_change
FROM with_change
WHERE prev_month_vacancies IS NOT NULL -- filtrera bort rader där föregående månads värde är NULL för att inte visa nullvärden inom procentuell förändring
ORDER BY percent_change DESC, month