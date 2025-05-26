import folium
import streamlit as st
from streamlit_folium import folium_static
import json
import numpy as np
import pandas as pd

def show_map_per_capita(full_percap: pd.DataFrame):
    # 1) Ladda GeoJSON
    with open("data/swedish_municipalities.geojson.txt", "r", encoding="utf-8") as f:
        geo_data = json.load(f)

    # 2) Normalisera kommunnamn i din DataFrame och GeoJSON
    full_percap["label"] = (
        full_percap["label"]
        .str.strip()
        .str.title()
    )
    # Bygg en snabb lookup från label -> värde
    value_map = dict(zip(full_percap["label"], full_percap["value"]))

    # Loop igenom alla features i geo_data och lägg in jobb_per_1000
    for feat in geo_data["features"]:
        kom = feat["properties"]["kom_namn"].strip().title()
        feat["properties"]["kom_namn"] = kom
        feat["properties"]["jobb_per_1000"] = value_map.get(kom, None)

    # 3) Skapa bas-kartan
    folium_map = folium.Map(location=[60.0, 15.0], zoom_start=5)

    # 4) Choropleth-lagret
    min_val = 0
    max_val = full_percap["value"].max()
    threshold_scale = list(np.linspace(min_val, max_val, 6))

    folium.Choropleth(
        geo_data=geo_data,
        name="choropleth",
        data=full_percap,
        columns=["label", "value"],
        key_on="feature.properties.kom_namn",
        fill_color="OrRd",
        threshold_scale=threshold_scale,
        fill_opacity=0.9,
        line_opacity=0.4,
        legend_name="Jobb per 1 000 invånare",
        reset=True,
    ).add_to(folium_map)

    # 5) Lägg på transparent GeoJson-overlay med Tooltip
    folium.GeoJson(
        geo_data,
        style_function=lambda feature: {
            "fillColor": "transparent",
            "color": "transparent",
        },
        tooltip=folium.GeoJsonTooltip(
            fields=["kom_namn", "jobb_per_1000"],
            aliases=["Kommun:", "Jobb/1000 inv:"],
            localize=True,
            labels=True,
            sticky=False,
        ),
        name="Kommuner (hover)",
    ).add_to(folium_map)

    folium.LayerControl().add_to(folium_map)

    # 6) Visa i Streamlit
    st.title("Jobb per 1 000 invånare – per kommun")
    folium_static(folium_map)
