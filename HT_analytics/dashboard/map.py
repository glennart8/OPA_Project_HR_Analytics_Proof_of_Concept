# Ha en fil där sveriges kommuner finns med
# Fixa en dataframe som visar antal jobb / kommun
# Använd st.map för att visa karta
# färglägg kommunerna efter antalet jobb, starkare färg = fler jobb

# Blev för mycket extragrejer för att visa antalet jobb när man hovrar....

import streamlit as st
import folium
from streamlit_folium import folium_static
import json
import pandas as pd
from dashboard_common import get_connection

con = con = get_connection()

# Ladda geojson med Sveriges kommuner & skapa lista över kommunamnen
with open("data/swedish_municipalities.geojson.txt", "r", encoding="utf-8") as f:
    geo_data = json.load(f)

alla_kommuner = [feature["properties"]["kom_namn"] for feature in geo_data["features"]]

# SQL-fråga från mart
query = """
WITH mart_vac_per_municipality AS (
    SELECT * FROM refined.fct_job_ads
)
SELECT
    COALESCE(e.workplace_municipality, 'Okänd') AS kommun,
    SUM(m.vacancies) AS antal_jobb
FROM mart_vac_per_municipality m
LEFT JOIN refined.dim_employer e ON m.employer_id = e.employer_id
GROUP BY e.workplace_municipality
ORDER BY antal_jobb DESC
"""

# Läs data från mart
job_data_from_mart = pd.read_sql(query, con)

# Gör en DataFrame med alla kommuner + jobb (0 där inga jobb finns)
job_data = pd.DataFrame({"kommun": alla_kommuner})
job_data = job_data.merge(job_data_from_mart, on="kommun", how="left").fillna(0)
job_data["antal_jobb"] = job_data["antal_jobb"].astype(int)

# Skapa karta
m = folium.Map(location=[60.0, 15.0], zoom_start=5)


folium.Choropleth(
    geo_data=geo_data,
    name="choropleth",
    data=job_data,
    columns=["kommun", "antal_jobb"],
    key_on="feature.properties.kom_namn",
    fill_color="OrRd",
    fill_opacity=0.9,
    line_opacity=0.4,
    legend_name="Antal jobb per kommun"
).add_to(m)

folium.LayerControl().add_to(m)

st.title("Antal tjänster per kommun i Sverige")
folium_static(m)
