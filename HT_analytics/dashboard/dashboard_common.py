import pandas as pd
import duckdb
import streamlit as st

def get_connection():
    return duckdb.connect("../job_ads.duckdb")

con = get_connection()

def load_data(query):
    con = get_connection()
    return con.execute(query).df()

def show_buttons(jobs_to_search):  
    for index, row in jobs_to_search.iterrows():
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