import streamlit as st
import plotly.express as px
import pandas as pd
from map_per_capita import show_map_per_capita
from LLM.llm_graph_maker import get_properties
import numpy as np

def show_radiobuttons(filtered_jobs, pop_df, full_percap):
    mode = st.radio(
        "Välj vy:",
        ("Antal jobb per kategori", "Jobb per 1 000 invånare", "Visa karta med antal jobb/kommun", "Top 10 egenskaper"),
        index=0, horizontal=True
    )
    
    if filtered_jobs.empty:
        st.info("Ingen data att visa för de valda filtren.")
        return
    
    if mode == "Antal jobb per kategori":
        df_to_plot, x, y, title, labels, color = show_jobs_per_categories(filtered_jobs)
        build_fig(df_to_plot, x, y, title, labels, color)
    elif mode == "Jobb per 1 000 invånare":
        df_to_plot, x, y, title, labels = show_jobs_per_1000_inhabitants(filtered_jobs, pop_df)
        build_fig(df_to_plot, x, y, title, labels)
    elif mode == "Top 10 egenskaper":
        fields = ["Pedagogik", "Bygg och anläggning", "Kultur, media, design"]
        selected_field = st.selectbox("Välj yrkesfält:", fields)

        with st.spinner("Analyserar jobbannonser..."):
            result = get_properties(selected_field)
            # st.text(result)
            show_bubble_chart(result)            
    else:
        show_map_per_capita(full_percap)


def show_jobs_per_categories(filtered_jobs):
    stats_df = (
        filtered_jobs
        .groupby(["occupation", "occupation_field"])
        .size()
        .reset_index(name="value")
        .sort_values("value", ascending=False)
    )

    # Ta fram top 10 yrken
    top = stats_df.groupby("occupation", as_index=False)["value"].sum().nlargest(10, "value")
    
    # Slå ihop igen för att få med rätt occupation_field
    df_to_plot = stats_df[stats_df["occupation"].isin(top["occupation"])].copy()
    df_to_plot = df_to_plot.rename(columns={"occupation": "label"})

    x, y = "value", "label"
    title = "Antal jobb per yrkeskategori"
    labels = {"label": "Yrke", "value": "Antal jobb", "occupation_field": "Arbetsfält"}
    
    # Färg baserat på arbetsfält
    color = "occupation_field"

    return df_to_plot, x, y, title, labels, color

def show_bubble_chart(result):
    df = pd.DataFrame(result)

    np.random.seed(1)
    df["X"] = np.random.rand(len(df)) * 5
    df["Y"] = np.random.rand(len(df)) * 3

    min_font, max_font = 10, 28
    min_val = df["Värde"].min()
    max_val = df["Värde"].max()
    
    # Skapa TextSize kolumn med enkel formel
    df["TextSize"] = min_font + (df["Värde"] - min_val) / (max_val - min_val) * (max_font - min_font)

    df["Värde"] = df["Värde"].fillna(0).astype(float)
    
    fig = px.scatter(
        df,
        x="X", y="Y",
        size="Värde",
        text="Egenskap",
        color="Värde",
        color_continuous_scale="Cividis",
        size_max=100,
        title="Top 10 efterfrågade egenskaper",
    )

    fig.update_traces(
        textposition="middle center",
        textfont=dict(size=df["TextSize"]),
    )

    fig.update_layout(
        # title_font_color='Gold',
        xaxis=dict(showticklabels=False, visible=False),
        yaxis=dict(showticklabels=False, visible=False),
        plot_bgcolor="#181817",
        paper_bgcolor='#181817',
        title_font=dict(size=24, color="#F7E7CE", family="Arial"),
        font=dict(color="White"),
        height=500,
        margin=dict(l=20, r=20, t=40, b=20)
    )

    st.plotly_chart(fig)


def show_jobs_per_1000_inhabitants(filtered_jobs, pop_df):
    mun_df = (
            filtered_jobs
            .groupby("workplace_municipality")
            .size()
            .reset_index(name="antal_jobb")
        )
    df_to_plot = (
        mun_df
        .merge(pop_df, on="workplace_municipality", how="left")
        .assign(value=lambda d: (d["antal_jobb"] * 1000 / d["population"]).round(2))
        .sort_values("value", ascending=False)
        .rename(columns={"workplace_municipality":"label"})[["label","value"]]
        .head(10)
    )
    x, y = "value", "label"
    title = "Jobb per 1 000 invånare"
    labels = {"label": "Kommun", "value": "Jobb per 1 000 invånare"}
    return df_to_plot, x, y, title, labels

def build_fig(df_to_plot, x, y, title, labels, color=None):
    df_to_plot = df_to_plot.sort_values(x, ascending=True)
    
    fig = px.bar(
        df_to_plot,
        x=x, y=y,
        color=color,
        orientation="h",
        title=title,
        labels=labels,
        height=400,
        color_discrete_sequence=px.colors.qualitative.Plotly,
    )
    fig.update_traces(width=0.4)
    fig.update_layout(
        bargap=0.0,
        margin=dict(l=100, r=20, t=50, b=50),
    )
    st.plotly_chart(fig, use_container_width=True)


def per_capita_df(filtered_jobs: pd.DataFrame, pop_df: pd.DataFrame) -> pd.DataFrame:
    """
    Returnerar en DataFrame med kolumnerna:
    - label (kommun)
    - value (jobb per 1000 invånare)
    för ALLA kommuner.
    """
    mun_df = (
        filtered_jobs
        .groupby("workplace_municipality")
        .size()
        .reset_index(name="antal_jobb")
    )
    full = (
        pop_df.rename(columns={"workplace_municipality":"label"})
              .merge(mun_df, left_on="label", right_on="workplace_municipality", how="left")
              .fillna({"antal_jobb": 0})
              .assign(value=lambda d: (d["antal_jobb"] * 1000 / d["population"]).round(2))
              .loc[:, ["label", "value"]]
    )
    return full
