import pandas as pd
import duckdb
import plotly
import streamlit as st

con = duckdb.connect('../job_ads.duckdb')

# 1. Välj kommun, fält och yrkestitel
# 2. Filtrera och visa dessa DYNAMISKT tillsammans med namnet på företaget och org.nummer
# 3. Eventuell fortsättning: 
#                           skapa en graf med antalet annonser per kommun och yrkestitel
#                           På en karta, dynamiskt visa var aretsplatserna ligger        

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
    st.dataframe(filtered_jobs)



### TEST

# test_jobs2 = con.execute("""
# SELECT 
#     -- LOWER(e.workplace_municipality) AS workplace_municipality,
#     -- o.occupation_field,
#     o.occupation,
#     e.employer_name,
#     e.employer_workplace,
#     m.vacancies
# FROM refined.fct_job_ads m
# JOIN refined.dim_employer e ON m.employer_id = e.employer_id
# JOIN refined.dim_occupation o ON m.occupation_id = o.occupation_id
# WHERE LOWER(e.workplace_municipality) = ?
# ORDER BY o.occupation
# """, (municipality_filter_lower,)).fetchdf()

# st.dataframe(test_jobs2)


