import streamlit as st
import pandas as pd
import duckdb

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

# --- TOPPCONTAINER: FILTER (vänster) + STATISTIK (höger) ---
with st.container():
    col_filter, col_statistik = st.columns([1.5, 1])

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
    query = """
        SELECT *
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
    filtered_jobs_to_show = filtered_jobs.drop(columns=["workplace_municipality", "occupation_field", "job_details_id"])

    # --- STATISTIK ---
    with col_statistik:
        st.metric("Antal jobbannonser", len(filtered_jobs))

        if not (municipality_filter != 'Alla' and occupation_field_filter != 'Alla'):
            if not filtered_jobs.empty:
                stats_df = (
                    filtered_jobs
                    .groupby("occupation_field")
                    .size()
                    .reset_index(name="total_vacancies")
                )

                cols = st.columns(3)
                symbols = [":hammer:", ":performing_arts:", ":female-teacher:"]

                for col, (index, row), symbol in zip(cols, stats_df.iterrows(), symbols):
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
                        JOIN refined.dim_auxilliary_attributes a ON m.auxilliary_attributes_id = a.id_aux
                        JOIN refined.dim_job_details jd ON m.job_details_id = jd.job_details_id
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
    st.header("📈 Ytterligare statistik")
    
