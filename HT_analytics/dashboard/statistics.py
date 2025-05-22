import streamlit as st
import plotly.express as px
import pandas as pd


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

def show_statistics(filtered_jobs, pop_df):
    st.markdown("## 📊 Statistik")

    mode = st.radio(
        "Välj vy:",
        ("Antal jobb per kategori", "Jobb per 1 000 invånare"),
        index=0, horizontal=True
    )

    if filtered_jobs.empty:
        st.info("Ingen data att visa för de valda filtren.")
        return

    if mode == "Antal jobb per kategori":
        stats_df = (
            filtered_jobs
            .groupby(["occupation", "occupation_field"])
            .size()
            .reset_index(name="value")
            .sort_values("value", ascending=False)
        )
        top = stats_df.groupby("occupation", as_index=False)["value"]\
                      .sum()\
                      .nlargest(10, "value")
        df_to_plot = top.rename(columns={"occupation":"label"})
        x, y = "value", "label"
        title = "Antal jobb per yrkeskategori"
        labels = {"label": "Yrke", "value": "Antal jobb"}

    else:  # Jobb per 1 000 invånare
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

    # Bygg figuren en gång
    fig = px.bar(
        df_to_plot,
        x=x, y=y,
        orientation="h",
        title=title,
        labels=labels,
        height=350,
    )
    fig.update_traces(width=0.4)
    fig.update_layout(
        bargap=0.0,
        margin=dict(l=100, r=20, t=50, b=50),
    )
    st.plotly_chart(fig, use_container_width=True)
    
    return df_to_plot, mode