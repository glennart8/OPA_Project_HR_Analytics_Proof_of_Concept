import pandas as pd
import duckdb
import plotly
import streamlit as st

con = duckdb.connect('../job_ads.duckdb')

# 1. Välj kommun, fält och yrkestitel
# 2. Visa dessa tillsammans med namnet på företaget och en headline



# HÄMTA UNIKA KOMMUNER
municipalities = con.execute("""
    SELECT DISTINCT workplace_municipality
    FROM refined.dim_employer                 
""").fetchdf()['workplace_municipality'].dropna().sort_values().tolist()

municipality_filter = st.selectbox("Välj kommun:", municipalities)
municipality_filter_lower = municipality_filter.lower()
st.write("Vald kommun:", municipality_filter)

# HÄMTA UNIKA YRKESFÄLT
occupation_fields = con.execute("""
    SELECT DISTINCT occupation_field
    FROM refined.dim_occupation
""").fetchdf()['occupation_field'].dropna().sort_values().tolist()

occupation_field_filter = st.selectbox("Välj yrkesfält:", occupation_fields)
st.write("Valt yrkesfält:", occupation_field_filter)

# HÄMTA UNIKA YRKEN
occupations = con.execute("""
    SELECT DISTINCT occupation
    FROM refined.dim_occupation
    WHERE occupation_field = ?
""", (occupation_field_filter,)).fetchdf()['occupation'].unique()

occupation_filter = st.selectbox("Välj yrkeskategori:", occupations)
st.write("Vald yrkeskategori:", occupation_filter)

# VISA ARBETEN EFTER ATT DE FILTRERATS
filtered_jobs = con.execute("""
    SELECT *
    FROM marts.mart_vacancies_by_mun_field_occ
    WHERE workplace_municipality = ?
    AND occupation = ?
    ORDER BY occupation
""", (municipality_filter_lower, occupation_filter)).fetchdf()

# För att dölja municipality, måste finnas med i marts för att filtrera
filtered_jobs = filtered_jobs.drop(columns=["workplace_municipality"])

# Visa de filtrerade jobben
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


