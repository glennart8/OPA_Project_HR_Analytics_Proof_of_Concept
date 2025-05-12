import streamlit as st
import pandas as pd
import duckdb

### UPPLÄGG ###
# SIDEBAR TILL VÄNSTER              -  Välj kommun, fält, yrke + någon extra grej nedanför? Typ allmän statistik i små KPI:er    
# ANNONSER FÖR MATCHNING I MITTEN   -  Visa specifika annonser baserat på filtreringen
# STATISTIK TILL HÖGER              -  Visa statistik utifrån filtrering 
# EXTRA - KLICKA TILL PAGE 2        -  Visa karta - klicka och få statistik/annonser


# connecta till databas
con = duckdb.connect('../job_ads.duckdb')

# Minska marginalerna på sidorna
st.set_page_config(layout="wide")

# Skapa tre kolumner
col1, col2, col3 = st.columns([0.4, 1, 1])  # [vänster, mitten, höger]

# --- VÄNSTER ---
with col1:
    st.header("Filter")

    municipalities = con.execute("""
        SELECT DISTINCT workplace_municipality
        FROM refined.dim_employer                 
    """).fetchdf()['workplace_municipality'].dropna().sort_values().tolist()
    municipalities = ['Alla'] + municipalities 
    municipality_filter = st.selectbox("Välj kommun:", municipalities)

    occupation_fields = con.execute("""
        SELECT DISTINCT occupation_field
        FROM refined.dim_occupation
    """).fetchdf()['occupation_field'].dropna().sort_values().tolist()
    occupation_fields = ['Alla'] + occupation_fields
    occupation_field_filter = st.selectbox("Välj yrkesfält:", occupation_fields)

    occupations = con.execute("""
        SELECT DISTINCT occupation
        FROM refined.dim_occupation
        WHERE occupation_field = ?
    """, (occupation_field_filter,)).fetchdf()['occupation'].dropna().sort_values().tolist()
    occupations = ['Alla'] + occupations
    occupation_filter = st.selectbox("Välj yrkeskategori:", occupations)


# --- MITTEN ---
with col2:
    st.header("Lediga jobb")

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

    # Dölj vissa kolumner
    filtered_jobs = filtered_jobs.drop(columns=["workplace_municipality", "occupation_field"])

    if filtered_jobs.empty:
        st.warning("Tyvärr finns det inga tjänster ute inom detta område.")
    else:
        st.dataframe(filtered_jobs, hide_index=True)
        
    ##################### CHOOSE A VACANCY ######################

    # Om man valt kommun och fält - visa knappar
    if municipality_filter != 'Alla' and occupation_field_filter != 'Alla':

        # Skapa knappar för varje jobbannons
        for index, row in filtered_jobs.iterrows():
            job_id = row['job_details_id']  # använder rätt nyckel
            employer = row['employer_name']
            occupation = row['occupation']
            
            # Använd en beskrivande etikett
            button_label = f"Visa info för {occupation} hos {employer}"
            
            if st.button(button_label, key=index):
                # Hämta detaljer för det valda jobbet
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
                    # ✅ Nu finns headline tillgänglig!
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
with col3:
    st.header("Statistik")

    # population_df = pd.read_csv("Kommun_befolking_2024.csv")
    # population_df["Kommun"] = population_df["Kommun"].str.strip().str.title()

    



    
    
    
