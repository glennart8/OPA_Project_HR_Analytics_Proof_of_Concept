from dotenv import load_dotenv
import os
import google.generativeai as genai
import duckdb


load_dotenv()  # Laddar .env-filen
api_key = os.getenv("API_KEY")

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.0-flash"
                              )
                   
def get_sql_code(query: str):

    with open("LLM/llm-context.txt", "r") as file:
        context_text = file.read()

    # Kanske borde lägga in en if-sats eller nåt som gör att context_text endast läses in första gången och inte kommande sökningar
    prompt = f"""
            Du är en SQL-expert som hjälper till att hitta relevanta jobbannonser.
            Skriv en komplett SQL-fråga som kan köras direkt i DuckDB.
            Använd alltid schema-namn, t.ex. refined.fct_job_ads.
            Använd inga Jinja-kommandon som {{ ref('...') }}.
            Undvik alias som är SQL-reserverade ord, t.ex. 'do'.
            Använd alias som occ, fja, de, jd.
            Returnera endast SQL-frågan, ingen förklaring.

            ## Kontext:
            {context_text}

            ## Fråga från användaren:
            "{query}"

            ## Instruktion:
            Skriv en SQL-fråga som använder informationen i kontexten ovan och besvarar användarens fråga. Returnera endast SQL-frågan utan förklaring.
            """

    response = model.generate_content(prompt)
    raw_sql = response.text

    # Tar bort markdown-klamrar
    clean_sql = raw_sql.strip().removeprefix("```sql").removesuffix("```").strip()

    return clean_sql
    
def get_results(query):    
    con = duckdb.connect('../job_ads.duckdb')
    query_df = con.execute(query).df()
    return query_df
    