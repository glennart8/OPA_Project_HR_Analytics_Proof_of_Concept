# BY CITY
import pandas as pd
import duckdb
import plotly
import streamlit as st
from dashboard_common import load_data

population_df = pd.read_csv("kommun_befolkning_2024.csv")

query = """
    SELECT workplace_municipality,
        occupation_field,
        SUM(total_vacancies) AS Antal_lediga_jobb
    FROM marts.mart_vacancies_by_mun_field_occ
        GROUP BY workplace_municipality, occupation_field
"""



job_df = load_data(query)

job_df["workplace_municipality"] = job_df["workplace_municipality"].str.strip().str.title()
population_df["Kommun"] = population_df["Kommun"].str.strip().str.title()

merged_df = pd.merge(job_df, population_df.rename(columns={"Kommun": "workplace_municipality"}), on="workplace_municipality", how="inner")

merged_df["Jobb per 1000 invånare"] = (merged_df["Antal_lediga_jobb"] * 1000 / merged_df["Folkmängd"].round(2))

yrkesgrupper = sorted(merged_df["occupation_field"].unique())
vald_grupp = st.selectbox("Välj yrkesgrupp", yrkesgrupper)

filtered = merged_df[merged_df["occupation_field"] == vald_grupp]

top10 = filtered.sort_values("Jobb per 1000 invånare", ascending=False).head(10)

st.title("Jobb per 1000 invånare per kommun")
st.subheader(f"Top 10 kommuner inom {vald_grupp}")
st.dataframe(top10[["workplace_municipality", "Antal_lediga_jobb", "Folkmängd", "Jobb per 1000 invånare"]], hide_index=True)




