# Låt LLM analysera kolumner som innehåller nyckelord för egenskaper
#   - Ge LLM tillgång till databasen och väsentliga kolumner (description i alla fall)
#   - Ge LLM kontexten att den ska leta efter "egenskaper" som söks
#   - Den summerar ord som är "egenskaper" - returnerar top 20
#   - LLM:en får aktiveras när vi filtrerar på fält (?) Eller radiobutton
    
# Bygg en graf (för varje fält) där dessa egenskaper är samlade, top 20 anträffade nyckelord??? 
#   - 

# LinkedIn länk typ

### ARBETSGÅNG ###

# 1. Trycker på radiobutton
#   - Skapa knapp 
#   - If/sats

# 2. Välj fält
#   - När vi trycker fält - LLM gör:
#                                   - kontext och prompt för att veta LLM:ens roll, vad den ska hämta, sql-koden som ska skrivas osv.  
#                                   - LLM ska både hämta,bearbeta och sammanställa datan                 
#                                   - tillgång till description, SQL-kod krävs för att hämta datan
#                                   - uppmanas att leta efter rätt saker (kolla decsription)
#                                       - t.ex. kvalifikationer, "vi söker dig som är", "erfarenhet inom"
#                                   - sammanställa top 10

# 3. Visa graf med top 10
#   - bygg graf med mest förekommande ord i plotly express
#   - 


from dotenv import load_dotenv
import os
import duckdb
import google.generativeai as genai
from LLM.llm import get_results

load_dotenv()  # Laddar .env-filen
api_key = os.getenv("API_KEY")

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.0-flash")
                              
    
def get_properties(field_name: str):
    # kontext
    with open("LLM/llm_graph_maker_context.txt", "r", encoding="utf-8") as file:
        llm_graph_maker_context = file.read()

    # SQL
    query = f"""
    SELECT description
    FROM refined.dim_job_details j
    JOIN refined.dim_occupation o ON j.job_details_id = o.occupation_id
    WHERE o.occupation_field = '{field_name}'
    AND description IS NOT NULL
    """

    # Hämta data
    df = get_results(query)

    # Sammanfoga beskrivningar
    all_descriptions = "\n\n".join(df["description"].dropna().tolist())[:10000]  # Begränsa längd

    # Prompt till LLM
    prompt = f"""
        Du är en språkmodell som hjälper HR att analysera jobbannonser.

        Yrkesområde: {field_name}

        Din uppgift:
        - Läs igenom jobbannonsernas beskrivningar (description).
        - Identifiera och lista de 10 vanligaste personliga egenskaperna som arbetsgivare söker.
        - Returnera en enkel lista numrerad 1-10.

        --- Kontext ---
        {llm_graph_maker_context}

        --- Jobbannonser ---
        {all_descriptions}
        """

    # Kör LLM
    response = model.generate_content(prompt)
    return response.text

    