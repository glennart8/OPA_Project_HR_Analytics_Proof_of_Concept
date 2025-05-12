import streamlit as st
import pandas as pd
import duckdb

# Setup
st.set_page_config(layout="wide")
con = duckdb.connect('../job_ads.duckdb')

# --- CONTAINER ---
# --- CONTAINER INOM KOLUMN (50%) ---
col_filter, _ = st.columns([1, 1])  # col_filter blir bara på 50% av kolumnen

with col_filter:
    with st.container():
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

# --- TVÅ KOLUMNER: Resultat & Statistik ---
col_resultat, col_statistik = st.columns([1.5, 1])  # [mitten, höger]

# --- MITTEN ---
with col_resultat:
    st.header("🍹 Lediga jobb")

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
    filtered_jobs = filtered_jobs.drop(columns=["workplace_municipality", "occupation_field"])

    if filtered_jobs.empty:
        st.warning("Tyvärr finns det inga tjänster ute inom detta område.")
    else:
        st.dataframe(filtered_jobs, hide_index=True)

        # Om man har kryssat i plats och fält ska knappar visas för mer info
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
                        st.write(f"{vacancy_details['description'][0]}")
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

# --- HÖGER ---
with col_statistik:
    st.header("📊 Statistik")
    st.metric("Antal jobbannonser", len(filtered_jobs))
    
        # Hämta data från mart_vacancies_per_field
    stats_df = con.execute("""
        SELECT * FROM marts.mart_vac_per_field
        ORDER BY total_vacancies DESC
    """).fetchdf()

    # Skapa 3 kolumner för att visa yrkesfält
    cols = st.columns(3)

    # Vi skapar en tuple med etiketter och värden för de tre första yrkesfälten och antal annonser
    labels = stats_df['occupation_field'].tolist()  # De tre första yrkesfälten
    values = stats_df['total_vacancies'].astype(int).tolist()  # Omvandla till heltal för att slippa decimal

    # Iterera och visa värdena i respektive kolumn
    for col, label, value in zip(cols, labels, values):
        with col:  # Specificera vilken kolumn vi skriver till
            st.metric(label=label, value=str(value))
