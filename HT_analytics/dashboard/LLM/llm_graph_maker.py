# HR-byrån vill skapa en graf som visar vilka huvudsakliga egenskaper arbetsgivare inom ett visst yrkesområde söker hos jobbsökande. 
# De vill publicera grafen på LinkedIn för att locka sökande med dessa egenskaper att kontakta byrån.
# Det finns flera textkolumner i jobbannonsdata, till exempel description. 
# Använd en LLM (stort språkmodell) för att analysera dessa kolumner och ta fram en analys. 
# Lägg sedan till en visualisering baserad på analysen i din Streamlit-dashboard.

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
import google.generativeai as genai
import duckdb
import streamlit as st

load_dotenv()  # Laddar .env-filen
api_key = os.getenv("API_KEY")

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.0-flash")
                              
    
def get_properties():

    with open("LLM/llm_graph_maker_context.txt", "r") as file:
        llm_graph_maker_context = file.read()

    # Kanske borde lägga in en if-sats eller nåt som gör att context_text endast läses in första gången och inte kommande sökningar
    prompt = f"""
            Kan du hämta ut ord som defineras som "egenskaper" i kolumnen 'description' i vår databas. 
            Sammanställ dessa och visa de 10 mest förekommande orden i en lista.
            
            Du måste använda denna SQL-kod för att få tillgång till datan:
    
            select description from refined.job_details

            ## Kontext:
            {llm_graph_maker_context}
            
            # """

    response = model.generate_content(prompt)
    output = response.text

    # # Tar bort markdown-klamrar
    # clean_sql = raw_sql.strip().removeprefix("```sql").removesuffix("```").strip()

    return output


   
    