import streamlit as st
st.set_page_config(layout="wide")
import pandas as pd
from dashboard_common import get_connection
from styles import load_background_style
from results import ask_gemeni, show_filtered_jobs
from statistics import show_statistics
from about import show_about_text
from general_statistics import show_general_statistics
from top_container import filter_jobs, get_jobs, show_jobs

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

##########    TOP-CONTAINER    ##########

with st.container():
    col_filter, col_statistik = st.columns([1, 1])

    # --- FILTRERING ---
    with col_filter:
        
        municipality_filter, occupation_field_filter, occupation_filter = filter_jobs()
        query, params = get_jobs(municipality_filter, occupation_field_filter, occupation_filter)
        filtered_jobs, filtered_jobs_to_show = show_jobs(query, params)
        # filtered_jobs, filtered_jobs_to_show = get_jobs(municipality_filter, occupation_field_filter, occupation_filter)
    
    # --- GENERELL STATISTIC ---
    with col_statistik:
        
        if not filtered_jobs.empty:
            show_general_statistics(filtered_jobs)
        else:
            st.info("Ingen statistik tillgänglig för det valda filtret.")

##########   RESULTAT    ###########

col_resultat, col_extra_stat = st.columns([1, 1])

with col_resultat:
    st.header("🍹 Lediga jobb")
    query_for_llm = st.text_input(" ", placeholder="Berätta vad du söker", label_visibility="collapsed")
    
    if query_for_llm:
        ask_gemeni(query_for_llm)
    else:
        show_filtered_jobs(filtered_jobs, filtered_jobs_to_show, municipality_filter, occupation_field_filter)    
    
###########    STATISTIK    ##########

with col_extra_stat:  
    show_statistics(filtered_jobs, pop_df)

###########     ABOUT     ##########
    show_about_text()