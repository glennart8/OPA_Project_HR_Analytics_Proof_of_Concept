import pandas as pd
import duckdb
import plotly.express as px
import streamlit as st
from dashboard_common import load_data

# Ladda befolkningsdata
population_df = pd.read_csv("kommun_befolkning_2024.csv")
population_df["Kommun"] = population_df["Kommun"].str.strip().str.title()

# Ladda jobbdata
query = """
    SELECT workplace_municipality AS Kommun,
           occupation_field,
           occupation AS Yrkesgrupp,
           SUM(total_vacancies) AS Antal_lediga_jobb
    FROM marts.mart_vacancies_by_mun_field_occ
    GROUP BY workplace_municipality, occupation_field, occupation
"""

job_df = load_data(query)
job_df["Kommun"] = job_df["Kommun"].str.strip().str.title()

# Slå ihop
merged_df = pd.merge(job_df, population_df, on="Kommun", how="inner")
merged_df["Jobb per 1000 invånare"] = (
    merged_df["Antal_lediga_jobb"] * 1000 / merged_df["Folkmängd"]
).round(2)

# Sidebar
with st.sidebar:
    yrkesgrupper = ["Välj yrkesgrupp"] + sorted(merged_df["occupation_field"].unique())
    yrkesgrupp = st.selectbox("Välj yrkesgrupp", yrkesgrupper, index=0, placeholder="Skriv för att söka")

    if yrkesgrupp != "Välj yrkesgrupp":
        kommuner = ["Välj kommun", "Hela landet"] + sorted(
            merged_df[merged_df["occupation_field"] == yrkesgrupp]["Kommun"].unique()
        )
        kommun = st.selectbox("Välj kommun", kommuner, index=0, placeholder="Skriv för att söka")
    else:
        kommun = None

    if kommun and kommun not in ["Välj kommun", "Hela landet"]:
        yrken = ["Välj yrke"] + sorted(
            merged_df[
                (merged_df["occupation_field"] == yrkesgrupp) &
                (merged_df["Kommun"] == kommun)
            ]["Yrkesgrupp"].unique()
        )
        yrke = st.selectbox("Välj yrke", yrken, index=0, placeholder="Skriv för att söka")
    else:
        yrke = None

# Visa hela landet
if yrkesgrupp != "Välj yrkesgrupp" and kommun == "Hela landet":
    total_df = (
        merged_df[merged_df["occupation_field"] == yrkesgrupp]
        .groupby("Yrkesgrupp")
        .agg({"Antal_lediga_jobb": "sum", "Folkmängd": "sum"})
        .reset_index()
    )
    total_df["Jobb per 1000 invånare"] = (
        total_df["Antal_lediga_jobb"] * 1000 / total_df["Folkmängd"]
    ).round(2)

    st.title("Statistik för hela landet")
    st.subheader(f"Yrkesgrupp: {yrkesgrupp}")
    st.dataframe(total_df[["Yrkesgrupp", "Antal_lediga_jobb", "Jobb per 1000 invånare"]], hide_index=True)

    fig = px.bar(
        total_df.sort_values("Antal_lediga_jobb", ascending=False).head(10),
        x="Yrkesgrupp",
        y="Antal_lediga_jobb",
        title="Topp 10 yrken i hela landet",
        labels={"Yrkesgrupp": "Yrke", "Antal_lediga_jobb": "Antal jobb"}
    )
    st.plotly_chart(fig, use_container_width=True)

# Visa filtrerat resultat för vald kommun och yrke
elif yrkesgrupp != "Välj yrkesgrupp" and kommun not in [None, "Välj kommun", "Hela landet"] and yrke and yrke != "Välj yrke":
    st.title("Jobb per 1000 invånare")
    st.subheader(f"Statistik för {kommun} inom {yrkesgrupp} – {yrke}")

    vald_df = merged_df[
        (merged_df["occupation_field"] == yrkesgrupp) &
        (merged_df["Kommun"] == kommun) &
        (merged_df["Yrkesgrupp"] == yrke)
    ]
    st.dataframe(vald_df[["Antal_lediga_jobb", "Folkmängd", "Jobb per 1000 invånare"]], hide_index=True)

    top_yrken = merged_df[
        (merged_df["occupation_field"] == yrkesgrupp) &
        (merged_df["Kommun"] == kommun)
    ]
    top_yrken = top_yrken.groupby("Yrkesgrupp")["Antal_lediga_jobb"].sum().reset_index()
    top_yrken = top_yrken.sort_values("Antal_lediga_jobb", ascending=False).head(10)

    fig = px.bar(
        top_yrken,
        x="Yrkesgrupp",
        y="Antal_lediga_jobb",
        title="Topp 10 yrken i kommunen",
        labels={"Yrkesgrupp": "Yrke", "Antal lediga jobb": "Antal jobb"}
    )
    st.plotly_chart(fig, use_container_width=True)