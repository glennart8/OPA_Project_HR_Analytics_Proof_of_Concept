import streamlit as st
import pandas as pd
import duckdb
import plotly.express as px
import os
from LLM.llm import get_sql_code, get_results
from dashboard_common import show_buttons, get_connection
from styles import load_background_style

# --- SIDKONFIGURATION ---
st.set_page_config(layout="wide")

# --- LADDA IN BAKGRUNDSBILD MED ÖVERLÄGG, TEXTFÄRG ---
st.markdown(load_background_style(), unsafe_allow_html=True)

# --- ANSLUTNING TILL DUCKDB ---
con = get_connection()

# --- LÄS IN KOMMUNBEFOLKNING ---
pop_df = (
    pd.read_csv("kommun_befolkning_2024.csv")
      .rename(columns={"Kommun": "workplace_municipality", "Folkmängd": "population"})
)
# Gör lowercase för enkel join
pop_df["workplace_municipality"] = pop_df["workplace_municipality"].str.strip().str.lower()


#############################    TOP-CONTAINER    ##################################

with st.container():
    col_filter, col_statistik = st.columns([1, 1])

    # --- FILTRERING ---
    with col_filter:
        st.markdown("### 🔎 Filtrera jobbannonser")
        col_kommun, col_falt, col_yrke = st.columns(3)

        with col_kommun:
            municipalities = con.execute(""" 
                SELECT DISTINCT workplace_municipality 
                FROM refined.dim_employer 
            """).fetchdf()['workplace_municipality'].dropna().sort_values().tolist()
            municipalities = ['Alla'] + municipalities
            municipality_filter = st.selectbox("Välj kommun:", municipalities)

        with col_falt:
            occupation_fields = con.execute("""
                SELECT DISTINCT occupation_field
                FROM refined.dim_occupation
            """).fetchdf()['occupation_field'].dropna().sort_values().tolist()
            occupation_fields = ['Alla'] + occupation_fields
            occupation_field_filter = st.selectbox("Välj yrkesfält:", occupation_fields)

        with col_yrke:
            occupations = con.execute("""
                SELECT DISTINCT occupation
                FROM refined.dim_occupation
                WHERE occupation_field = ?
            """, (occupation_field_filter,)).fetchdf()['occupation'].dropna().sort_values().tolist()
            occupations = ['Alla'] + occupations
            occupation_filter = st.selectbox("Välj yrkeskategori:", occupations)
                           
    # --- HÄMTA FILTRERAD DATA EFTER FILTERNING --- 
        # VAR TVUNGEN ATT HA DISTINCT HÄR, ANNARS KOM DUBLETTER MED
    query = """
        SELECT DISTINCT * 
        FROM marts.mart_vacancies_by_mun_field_occ
        WHERE 1=1
    """
    params = []

    if municipality_filter != 'Alla':
        query += " AND workplace_municipality = ?"
        params.append(municipality_filter.lower())

    if occupation_field_filter != 'Alla':
        query += " AND occupation_field = ?"
        params.append(occupation_field_filter)

    if occupation_filter != 'Alla':
        query += " AND occupation = ?"
        params.append(occupation_filter)

    query += " ORDER BY occupation"

    filtered_jobs = con.execute(query, params).fetchdf()
    
    filtered_jobs_to_show = (
        filtered_jobs
        .drop(columns=["workplace_municipality", "occupation_field", "job_details_id"])
        .rename(columns={"occupation": "Yrke", "employer_name": "Arb.givare", "vacancies": "Antal tjänster", "employer_organization_number": "Org.Nr"})
    )
    
    # --- GENERELL STATISTIK ---
    with col_statistik:

        if not (occupation_field_filter != 'Alla'):
            if not filtered_jobs.empty:
                stats_df = (
                    filtered_jobs
                    .groupby("occupation_field")
                    .size()
                    .reset_index(name="total_vacancies")
                )

                # Skapa exakt 4 kolumner för jämn layout
                stat_cols = st.columns(4)
                symbols = [":hammer:", ":performing_arts:", ":female-teacher:"]
                
                
                with stat_cols[0]:
                    st.write("")
                    st.metric("Antal jobbannonser", len(filtered_jobs))

                for col, (index, row), symbol in zip(stat_cols[1:], stats_df.iterrows(), symbols):
                    
                    with col:
                        st.write("")
                        st.metric(label=f"{symbol} {row['occupation_field']}", value=row["total_vacancies"])
                
            else:
                st.info("Ingen statistik tillgänglig för det valda filtret.")

#############################    RESULTAT    ##################################

# --- HUVUDKOLUMLAYOUT: RESULTAT (vänster) + YTTERLIGARE STATISTIK (höger) ---
col_resultat, col_extra_stat = st.columns([1, 1])

# --- VÄNSTER: JOBBRESULTAT ---
with col_resultat:
    
    st.header("🍹 Lediga jobb")

    query_for_llm = st.text_input(" ", placeholder="Berätta vad du söker", label_visibility="collapsed")
    
    # Om vi skriver till LLM
    if query_for_llm:      
        sql_code_from_llm = get_sql_code(query_for_llm)
        st.write(sql_code_from_llm)
        result_from_llm = get_results(sql_code_from_llm)
        
        if result_from_llm.empty:
            st.warning("Tyvärr finns det inga tjänster ute inom detta område.")
        else:
            st.dataframe(result_from_llm)
            # Visa knappar för arbeten (Ska vi ha något filter för att inte visa alla???)
            # FUNKAR DÅLIGT HÄR, VISAR VISSA TEXTER MEN INTE ANDRA
            show_buttons(result_from_llm)
    
    # Om vi filtrerar via dropdown-menyerna     
    else:
        if filtered_jobs.empty:
            st.warning("Tyvärr finns det inga tjänster ute inom detta område.")
        else:
            styled_df = filtered_jobs_to_show.style.set_properties(**{'color': '#FFC87C'}) # #FFB347, 
            st.dataframe(styled_df, hide_index=True)

            # Om vi valt de 2 första filtren
            if municipality_filter != 'Alla' and occupation_field_filter != 'Alla':
                show_buttons(filtered_jobs)

#############################    STATISTIK    ##################################

with col_extra_stat:
    st.markdown("## 📊 Statistik")

    # Välj vy: råa antal jobb per yrkeskategori eller jobb per 1 000 invånare
    mode = st.radio(
        "Välj vy:",
        ("Antal jobb per kategori", "Jobb per 1 000 invånare", "Linus stuff"),
        index=0,
        horizontal=True
    )

    if filtered_jobs.empty:
        st.info("Ingen data att visa för de valda filtren.")
    else:
        if mode == "Antal jobb per kategori":
            # Gruppar på yrkeskategori i stället för yrkesfält
            stats_df = (
                filtered_jobs
                .groupby(["occupation", "occupation_field"])  # Färg på occupation_field
                .size()
                .reset_index(name="value")
                .sort_values("value", ascending=False)
            )

            # Topp 10 yrkeskategorier 
            top_occupations = stats_df.groupby("occupation")["value"].sum().nlargest(10).index

            # Filtrera stats_df för att bara ha topp 10 occupations
            df_to_plot = stats_df[stats_df["occupation"].isin(top_occupations)].reset_index(drop=True)

            x_label, y_label = "Antal jobb", "Yrke"
            title = "Antal jobb per yrkeskategori"
            orient = "h"
            color_col = "occupation_field"
            labels = {"occupation": y_label, "value": x_label, "occupation_field": "Arbetsfält"}

        elif mode == "Jobb per 1 000 invånare":
            # Räkna jobb per kommun och justera per 1000 invånare
            mun_df = (
                filtered_jobs
                .groupby("workplace_municipality")
                .size()
                .reset_index(name="antal_jobb")
            )
            percap = (
                mun_df
                .merge(pop_df, on="workplace_municipality", how="left")
                .assign(value=lambda df: (df["antal_jobb"] * 1000 / df["population"]).round(2))
                .sort_values("value", ascending=False)
            )
            stats_df = percap.rename(columns={"workplace_municipality": "label"})[["label", "value"]].head(10)

            df_to_plot = stats_df
            x_label, y_label = "Jobb per 1 000 invånare", "Kommun"
            title = "Jobb per 1 000 invånare"
            orient = "h"
            color_col = None
            labels = {"label": y_label, "value": x_label}

        elif mode == "Linus stuff":
            pass

        if not df_to_plot.empty:
            # Rita horisontellt stapeldiagram med mörkt tema
            fig = px.bar(
                df_to_plot,
                x="value",
                y=df_to_plot.columns[0],  # label-kolumnen: 'occupation' eller 'label'
                color=color_col if color_col else None,
                orientation=orient,
                title=title,
                labels=labels,
                height=350,
                color_discrete_sequence=px.colors.qualitative.Set1
            )

            # Justera stapeltjocklek och mellanrum
            fig.update_traces(width=0.4)
            fig.update_layout(
                bargap=0.0,
                margin=dict(l=100, r=20, t=50, b=50),
                xaxis=dict(
                    title_font=dict(size=12, color="white"),
                    tickfont=dict(size=11, color="white"),
                    showgrid=False
                ),
                yaxis=dict(
                    title_font=dict(size=12, color="white"),
                    tickfont=dict(size=11, color="white")
                ),
                font=dict(color="white"),
                plot_bgcolor="rgba(30,30,30,0)",
                paper_bgcolor="rgba(30,30,30,0.5)"        
            )
            fig.update_yaxes(categoryorder='total ascending')
            st.plotly_chart(fig, use_container_width=True)


############################# ABOUT #############################

        # About-sektion längst ner
        st.markdown("<hr/>", unsafe_allow_html=True)
        st.markdown("#### Om")
        st.markdown(
            """
            - Data hämtas från Jobtech API och aggregeras i DuckDB.  
            - By: Henke, Jonas, Linus
            """
        )

#############################    LLM    ##################################



    



    