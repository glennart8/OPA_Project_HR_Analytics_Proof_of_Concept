from dotenv import load_dotenv
import os
import google.generativeai as genai
import duckdb
import streamlit as st

# i content ska vi skicka in den text som användaren skrivit
# någonstans ska vi definera att ai ska översätta detta till sql-kod som passar just våran databas med alla namn osv

# Användaren:    Visa alla arbeten som inte kräver någon tidigare erfarenhet
# Gemeni:        SELECT * FROM refined.job_ads WHERE aux.experience_required NOT TRUE JOIN dim_auxilliary_attributes as aux

# Ta den SQL-kod som gemeni ger oss, skicka in den till resultats-dataframen på något sätt


load_dotenv()  # Laddar .env-filen
api_key = os.getenv("API_KEY")

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.0-flash"
                              )
def get_answer(question):
    response = model.generate_content()
    return response.text   
        
    


def get_sql_code(query: str):
    with open("llm-context.txt", "r") as file:
        context_text = file.read()

    # Kanske borde lägga in en if-sats eller nåt som gör att context_text endast läses in första gången och inte kommande sökningar
    prompt = f"""
            Du är en SQL-expert som hjälper till att hitta relevanta jobbannonser.

            ## Kontext:
            {context_text}

            ## Fråga från användaren:
            "{query}"

            ## Instruktion:
            Skriv en SQL-fråga som använder informationen i kontexten ovan och besvarar användarens fråga. Returnera endast SQL-frågan utan förklaring.
            """

    response = model.generate_content(prompt)
    return response.text
    
def get_results(query):
    con = duckdb.connect('job_ads.duckdb')
    query_df = con.execute(query).df()
    return query_df
    