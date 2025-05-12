import pandas as pd
import duckdb
import plotly
import streamlit as st

con = duckdb.connect('../job_ads.duckdb')

# 1. Välj kommun, fält och yrkestitel
# 2. Filtrera och visa dessa DYNAMISKT tillsammans med namnet på företaget och org.nummer
# 3. Eventuell fortsättning: 
#                           skapa en graf med antalet annonser per kommun och yrkestitel
#                           På en karta, dynamiskt visa var arbetsplatserna ligger   
#                           Välj ett alternativ och se mer information om det jobbet        


# HÄMTA UNIKA KOMMUNER
municipalities = con.execute("""
    SELECT DISTINCT workplace_municipality
    FROM refined.dim_employer                 
""").fetchdf()['workplace_municipality'].dropna().sort_values().tolist()

# Skapar listan 'Alla' som visar alla jobb
municipalities = ['Alla'] + municipalities 
municipality_filter = st.selectbox("Välj kommun:", municipalities)


# HÄMTA UNIKA YRKESFÄLT
occupation_fields = con.execute("""
    SELECT DISTINCT occupation_field
    FROM refined.dim_occupation
""").fetchdf()['occupation_field'].dropna().sort_values().tolist()

occupation_fields = ['Alla'] + occupation_fields
occupation_field_filter = st.selectbox("Välj yrkesfält:", occupation_fields)


# HÄMTA UNIKA YRKEN
occupations = con.execute("""
    SELECT DISTINCT occupation
    FROM refined.dim_occupation
    WHERE occupation_field = ?
""", (occupation_field_filter,)).fetchdf()['occupation'].dropna().sort_values().tolist()

occupations = ['Alla'] + occupations
occupation_filter = st.selectbox("Välj yrkeskategori:", occupations)

### Definiera SQL-frågan med parametrar för filtrering, som kan ändras dynamiskt
query = """
    SELECT *
    FROM marts.mart_vacancies_by_mun_field_occ
    WHERE 1=1 -- För att kunna appenda senare (lägga till filtren), smart ju
"""
params = []

# När användaren völjer något annat än 'Alla' så filtreras det på den valda kommunen
if municipality_filter != 'Alla':
    query += " AND workplace_municipality = ?"
    params.append(municipality_filter.lower())

if occupation_field_filter != 'Alla':
    query += " AND occupation_field = ?"
    params.append(occupation_field_filter)

if occupation_filter != 'Alla':
    query += " AND occupation = ?"
    params.append(occupation_filter)

query += " ORDER BY occupation"

filtered_jobs = con.execute(query, params).fetchdf()

# För att dölja municipality och occupation_field, måste finnas med i marts för att filtrera
filtered_jobs = filtered_jobs.drop(columns=["workplace_municipality", "occupation_field"])

# Visar ett "felmeddelande" om det inte finns några jobb att visa
if filtered_jobs.empty:
    st.warning("Tyvärr finns det inga tjänster ute inom detta område.")
else:
    st.dataframe(filtered_jobs, hide_index=True)
    
    
##################### CHOOSE A VACANCY ######################

    # # Skapa knappar för varje jobbannons
    # for index, row in filtered_jobs.iterrows():
    #     job_id = row['id']  
    #     job_headline = row['headline']
        
    #     # Skapa en knapp för varje jobb
    #     if st.button(f"Visa detaljer för {job_headline}"):
    #         # När knappen trycks, kör SQL-frågan för att hämta detaljer för den valda tjänsten
    #         vacancy_details_query = """
    #             WITH mart_chosen_vacancy AS (
    #                 SELECT * FROM {{ ref('fct_job_ads') }}
    #             )
    #             SELECT
    #                 jd.headline,                                 
    #                 jd.description,                                         
    #                 jd.employment_type,
    #                 jd.duration,
    #                 jd.salary_type,
    #                 jd.scope_of_work_min,
    #                 jd.scope_of_work_max,    
    #                 jd.webpage_url,
    #                 jd.description_conditions,                            
    #                 a.experience_required,
    #                 a.driver_license,    
    #                 m.publication_date,
    #                 m.application_deadline
    #             FROM mart_chosen_vacancy m
    #             JOIN refined.dim_auxilliary_attributes a ON m.auxilliary_attributes_id = a.id_aux
    #             JOIN refined.dim_job_details jd ON m.job_details_id = jd.job_details_id
    #             WHERE m.id = ?
    #         """
    #         # Kör SQL-frågan för den valda tjänsten
    #         vacancy_details = con.execute(vacancy_details_query, (job_id,)).fetchdf()
            
    #         # Visa detaljer för den valda tjänsten
    #         if not vacancy_details.empty:
    #             st.write(f"**{vacancy_details['headline'][0]}**")
    #             st.write(f"**Beskrivning**: {vacancy_details['description'][0]}")
    #             st.write(f"**Anställningstyp**: {vacancy_details['employment_type'][0]}")
    #             st.write(f"**Varaktighet**: {vacancy_details['duration'][0]}")
    #             st.write(f"**Lön**: {vacancy_details['salary_type'][0]}")
    #             st.write(f"**Omfattning**: {vacancy_details['scope_of_work_min'][0]} - {vacancy_details['scope_of_work_max'][0]}")
    #             st.write(f"**Webbsida**: {vacancy_details['webpage_url'][0]}")
    #             st.write(f"**Villkor**: {vacancy_details['description_conditions'][0]}")
    #             st.write(f"**Erfarenhet som krävs**: {vacancy_details['experience_required'][0]}")
    #             st.write(f"**Körkort**: {vacancy_details['driver_license'][0]}")
    #             st.write(f"**Publiceringsdatum**: {vacancy_details['publication_date'][0]}")
    #             st.write(f"**Sista ansökningsdatum**: {vacancy_details['application_deadline'][0]}")
    #         else:
    #             st.warning("Inga detaljer tillgängliga för denna tjänst.")



