import pandas as pd
import duckdb
import plotly
import streamlit as st

con = duckdb.connect('../job_ads.duckdb')

# # BY CITY
# df_by_city = con.execute("SELECT * FROM marts.mart_vacancies_by_city")
# st.dataframe(df_by_city)


# HÄMTA UNIKA KOMMUNER
municipalities = con.execute("""
    SELECT DISTINCT workplace_municipality
    FROM refined.dim_employer                 
""").fetchdf()['workplace_municipality'].dropna().sort_values().tolist()

municipality_filter = st.selectbox("Välj kommun:", municipalities)

# HÄMTA UNIKA YRKESFÄLT
occupation_fields = con.execute("""
    SELECT DISTINCT occupation_field
    FROM refined.dim_occupation
""").fetchdf()['occupation_field'].dropna().sort_values().tolist()

occupation_field_filter = st.selectbox("Välj yrkesfält:", occupation_fields)

# HÄMTA UNIKA YRKEN
occupations = con.execute("""
    SELECT DISTINCT occupation
    FROM refined.dim_occupation
    WHERE occupation_field = ?
""", (occupation_field_filter,)).fetchdf()['occupation'].unique()

occupation_filter = st.selectbox("Välj yrkeskategori:", occupations)

# VISA ARBETEN EFTER ATT DE FILTRERATS
filtered_jobs = con.execute("""
    SELECT *
    FROM marts.mart_vacancies_by_mun_field_occ
    WHERE workplace_municipality = ?
    AND occupation_field = ?
    AND occupation = ?
""", (municipality_filter, occupation_field_filter, occupation_filter)).fetchdf()

# Visa de filtrerade jobben
st.dataframe(filtered_jobs)