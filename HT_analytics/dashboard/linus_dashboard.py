import pandas as pd
import duckdb
import plotly.express as px
import streamlit as st

# inställningar
st.set_page_config(page_title="Jobbkrav Dashboard", layout="wide")
st.title("Kompetenskrav")

# koppla in data
con = duckdb.connect('../job_ads.duckdb')

# Ladda data
df = con.execute("""
    SELECT 
        f.job_details_id,
        f.publication_date,
        e.workplace_municipality AS municipality,
        o.occupation_group,
        sk.label AS requirement
    FROM refined.fct_job_ads f
    JOIN refined.dim_employer e ON f.employer_id = e.employer_id
    JOIN refined.dim_occupation o ON f.occupation_id = o.occupation_id
    LEFT JOIN staging.job_ads__must_have__skills sk ON sk._dlt_parent_id = f.job_details_id
    WHERE f.publication_date >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '3 months'
""").df()

# Sidebar
municipality = st.sidebar.selectbox("Välj kommun", sorted(df["municipality"].dropna().unique()))
occupation = st.sidebar.selectbox("Välj yrkesgrupp", sorted(df["occupation_group"].dropna().unique()))

# Filtrering
filtered = df[(df["municipality"] == municipality) & (df["occupation_group"] == occupation)]

# Visa krav 
st.subheader(f"Krav som efterfrågas i {municipality} för yrkesgruppen '{occupation}'")
if not filtered.empty:
    top_req = filtered["requirement"].value_counts().reset_index()
    top_req.columns = ["Krav", "Antal annonser"]
    st.dataframe(top_req)

    st.bar_chart(top_req.set_index("Krav"))
else:
    st.warning("Inga annonser hittades för vald kommun och yrkesgrupp.")

    #ej färdig då datan inte är klar
