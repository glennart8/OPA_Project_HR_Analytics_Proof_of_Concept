import streamlit as st
import pandas as pd
from dashboard_common import get_connection
from styles import load_background_style
from results import ask_gemeni, show_filtered_jobs
from statistics import show_statistics
from about import show_about_text
from general_statistics import show_general_statistics

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
# Gör lowercase för att joina 
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
                show_general_statistics(filtered_jobs)
            else:
                st.info("Ingen statistik tillgänglig för det valda filtret.")

#############################    RESULTAT    ##################################

# --- HUVUDKOLUMLAYOUT ---
col_resultat, col_extra_stat = st.columns([1, 1])

with col_resultat:
    st.header("🍹 Lediga jobb")
    query_for_llm = st.text_input(" ", placeholder="Berätta vad du söker", label_visibility="collapsed")
    
    if query_for_llm:
        ask_gemeni(query_for_llm)
    else:
        show_filtered_jobs(filtered_jobs, filtered_jobs_to_show, municipality_filter, occupation_field_filter)    
    
#############################    STATISTIK    ##################################

    with col_extra_stat:  
        show_statistics(filtered_jobs, pop_df)

############################# ABOUT #############################
        show_about_text()




    