from dotenv import load_dotenv
import os
import google.generativeai as genai
import duckdb

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
        
    # PROBLEM 1 - Gemeni er oss markdown-syntax ``` och dessa behöver ta bort så att koden kann läsas in ordentligt
    # PROBLEM 2 - DO (som i dim_occupation är ett reserverat ord och behöver bytas ut - skriv in i kontexten så att llm unviker DO
    # PROBLEM 3 - {{ JINJASYNTAX }} kan inte läsas 
    # PROBLEM 4 - hittar inte fct_job_ads (inte specificerat refined tror jag)
    # PROBLEM 5 - vi skapar en ny job_ads.duckdb och connetar inte till den rätta - därför hittas inte tabellerna
    # PROBLEM 6 - Hittar inte vissa saker, t.ex. 
    # FIXAD     - där ingen erfarenhet krävs ger LLM %Ej krav% - behöver specificera såna grejer i kontexten
    # FIXAD     - driver_licence required och access_to_own_car funkar inte
    # FIXAD     - jd.employment_type = 'Vanlig anstÃ¤llning', funkar inte att köra encoding = 'utf8'
    # FIXAD     - Samma encoding fel om man söker på "fast lön"
    # FIXAD     - Kan inte visa deltid då den söker på employment_type i stället för description_conditions 
                
    
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
    