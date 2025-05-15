import streamlit as st
import pandas as pd
import duckdb
import plotly.express as px

# URLS För bilder
# bygg - https://images.unsplash.com/photo-1589939705384-5185137a7f0f?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D
# pedagogik - https://images.unsplash.com/photo-1580894732444-8ecded7900cd?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D
# kultur - https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D

import streamlit as st
import pandas as pd
import duckdb

# --- SIDKONFIGURATION ---
st.set_page_config(layout="wide")

# --- BAKGRUNDSBILD MED ÖVERLÄGG ---
st.markdown(f"""
    <style>
    .stApp {{
        background-image:
            linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)),
            url("https://images.unsplash.com/photo-1589939705384-5185137a7f0f?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D");
        background-size: cover;
        background-position: center;
    }}
    </style>
""", unsafe_allow_html=True)


# --- ANSLUTNING TILL DUCKDB ---
con = duckdb.connect('../job_ads.duckdb')

# --- LÄS IN KOMMUNBEFOLKNING ---
pop_df = (
    pd.read_csv("kommun_befolkning_2024.csv")
      .rename(columns={"Kommun": "workplace_municipality", "Folkmängd": "population"})
)
# Gör lowercase för enkel join
pop_df["workplace_municipality"] = pop_df["workplace_municipality"].str.strip().str.lower()

# --- TOPPCONTAINER: FILTER (vänster) + STATISTIK (höger) ---
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
            
        query_for_llm = st.text_input("", placeholder="Berätta vad du söker")

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
                    st.metric("Antal jobbannonser", len(filtered_jobs))

                for col, (index, row), symbol in zip(stat_cols[1:], stats_df.iterrows(), symbols):
                
                    with col:
                        st.metric(label=f"{symbol} {row['occupation_field']}", value=row["total_vacancies"])
                
            else:
                st.info("Ingen statistik tillgänglig för det valda filtret.")


# --- HUVUDKOLUMLAYOUT: RESULTAT (vänster) + YTTERLIGARE STATISTIK (höger) ---
col_resultat, col_extra_stat = st.columns([1, 1])

# --- VÄNSTER: JOBBRESULTAT ---
with col_resultat:
    st.header("🍹 Lediga jobb")

    if filtered_jobs.empty:
        st.warning("Tyvärr finns det inga tjänster ute inom detta område.")
    else:
        st.dataframe(filtered_jobs_to_show, hide_index=True)

        if municipality_filter != 'Alla' and occupation_field_filter != 'Alla':
            for index, row in filtered_jobs.iterrows():
                job_id = row['job_details_id']
                employer = row['employer_name']
                occupation = row['occupation']
                button_label = f"Visa info för {occupation} hos {employer}"

                if st.button(button_label, key=index):
                    vacancy_details_query = """
                        SELECT
                            jd.headline,                                 
                            jd.description,
                            jd.employment_type,
                            jd.duration,
                            jd.salary_type,
                            jd.scope_of_work_min,
                            jd.scope_of_work_max,    
                            jd.webpage_url,
                            jd.description_conditions,
                            a.experience_required,
                            a.driver_license,
                            m.publication_date,
                            m.application_deadline
                        FROM refined.fct_job_ads m
                        LEFT JOIN refined.dim_auxilliary_attributes a ON m.auxilliary_attributes_id = a.id_aux
                        LEFT JOIN refined.dim_job_details jd ON m.job_details_id = jd.job_details_id
                        WHERE m.job_details_id = ?
                    """
                    vacancy_details = con.execute(vacancy_details_query, (job_id,)).fetchdf()

                    if not vacancy_details.empty:
                        st.subheader(vacancy_details['headline'][0])
                        st.write(vacancy_details['description'][0])
                        st.write(f"Anställningstyp: {vacancy_details['employment_type'][0]}")
                        st.write(f"Varaktighet: {vacancy_details['duration'][0]}")
                        st.write(f"Lön: {vacancy_details['salary_type'][0]}")
                        st.write(f"Omfattning: {vacancy_details['scope_of_work_min'][0]}–{vacancy_details['scope_of_work_max'][0]}")
                        st.write(f"Webbsida: {vacancy_details['webpage_url'][0]}")
                        st.write(f"Villkor: {vacancy_details['description_conditions'][0]}")
                        st.write(f"Erfarenhet krävs: {vacancy_details['experience_required'][0]}")
                        st.write(f"Körkort: {vacancy_details['driver_license'][0]}")
                        st.write(f"Publiceringsdatum: {vacancy_details['publication_date'][0]}")
                        st.write(f"Sista ansökningsdatum: {vacancy_details['application_deadline'][0]}")
                    else:
                        st.warning("Inga detaljer tillgängliga för denna tjänst.")

# --- HÖGER: YTTERLIGARE STATISTIK ---
with col_extra_stat:
    st.markdown("## 📊 Statistik")

    # Välj vy: råa antal jobb per yrkeskategori eller jobb per 1 000 invånare
    mode = st.radio(
        "Välj vy:",
        ("Antal jobb per kategori", "Jobb per 1 000 invånare"),
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
                .groupby("occupation")
                .size()
                .reset_index(name="value")
                .sort_values("value", ascending=False)
            )
            x_label, y_label = "Antal jobb", "Yrke"
            title = "Antal jobb per yrkeskategori"
            orient = "h"

        else:
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
            stats_df = percap.rename(columns={"workplace_municipality": "label"})[["label", "value"]]
            x_label, y_label = "Antal jobb", "Kommun"
            title = "Jobb per 1 000 invånare"
            orient = "h"

        # Ta topp 10
        display_df = stats_df.head(10).sort_values('value', ascending=False).reset_index(drop=True)
        display_df.columns = [y_label, x_label]

        # Rita horisontellt stapeldiagram med mörkt tema
        fig = px.bar(
            display_df,
            x=x_label,
            y=y_label,
            orientation=orient,
            title=title,
            labels={y_label: y_label.replace("_", " ").title(), x_label: x_label.replace("_", " ").title()},
            # template="plotly_dark",
            height=350
            ##color= WHAT TO WRITE!!?! Får inte OCCUPATION_FIELD att fungerar korrekt....
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

        # About-sektion längst ner
        st.markdown("<hr/>", unsafe_allow_html=True)
        st.markdown("#### Om")
        st.markdown(
            """
            - Data hämtas från Jobtech API och aggregeras i DuckDB.  
            """
        )


    



    
