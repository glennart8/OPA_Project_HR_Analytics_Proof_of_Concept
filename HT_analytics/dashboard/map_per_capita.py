import folium
import streamlit as st
from streamlit_folium import folium_static
import json
import numpy as np

def show_map(df_to_plot):

    # Ladda GeoJSON
    with open("data/swedish_municipalities.geojson.txt", "r", encoding="utf-8") as f:
        geo_data = json.load(f)

    # Säkerställ att kommunnamn matchar (strip + lower)
    df_to_plot["label"] = df_to_plot["label"].str.strip().str.lower()
    for f in geo_data["features"]:
        f["properties"]["kom_namn"] = f["properties"]["kom_namn"].strip().lower()

    # Kontrollera matchning mellan df och geojson
    geo_kommuner = [f["properties"]["kom_namn"] for f in geo_data["features"]]
    df_kommuner = df_to_plot["label"].unique()
    missing = set(df_kommuner) - set(geo_kommuner)
    if missing:
        st.warning(f"Följande kommuner finns i data men saknas i GeoJSON: {missing}")

    # Skapa karta
    folium_map = folium.Map(location=[60.0, 15.0], zoom_start=5)

    # Skapa threshold_scale: 6 nivåer från 0 upp till maxvärdet
    min_val = 0
    max_val = df_to_plot["value"].max()
    threshold_scale = list(np.linspace(min_val, max_val, 6))

    folium.Choropleth(
        geo_data=geo_data,
        name="choropleth",
        data=df_to_plot,
        columns=["label", "value"],
        key_on="feature.properties.kom_namn",
        fill_color="OrRd",
        threshold_scale=threshold_scale,
        fill_opacity=0.9,
        line_opacity=0.4,
        legend_name="Jobb per 1 000 invånare",
        reset=True,
    ).add_to(folium_map)

    folium.LayerControl().add_to(folium_map)
    st.title("Jobb per 1 000 invånare – per kommun")
    folium_static(folium_map)
