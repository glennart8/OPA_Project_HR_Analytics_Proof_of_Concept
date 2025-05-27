import json
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

    with open("LLM/llm_graph_maker_context.txt", "r", encoding="utf-8") as file:
        llm_graph_maker_context = file.read()

    # Hämta data
    query = f"""
    SELECT description
    FROM refined.dim_job_details j
    JOIN refined.dim_occupation o ON j.job_details_id = o.occupation_id
    WHERE o.occupation_field = '{field_name}'
    AND description IS NOT NULL
    """
    df = get_results(query)
    all_descriptions = "\n\n".join(df["description"].dropna().tolist())[:30000]

    # Skapa prompt
    prompt = f"""
        Du är en språkmodell som hjälper HR att analysera jobbannonser.

        Yrkesområde: {field_name}

        Din uppgift:
        - Läs igenom jobbannonsernas beskrivningar (description).
        - Identifiera och lista de 10 vanligaste personliga egenskaperna som arbetsgivare söker.
        - Returnera ENDAST ett JSON-objekt, utan inledning eller förklaring. Format:

        {{
            "Egenskap": ["Snäll", "Jättebra"],
            "Värde": [10, 20]
        }}

        --- Kontext ---
        {llm_graph_maker_context}

        --- Jobbannonser ---
        {all_descriptions}
    """

    response = model.generate_content(prompt)
    raw_text = response.text.strip()

    # Rensa bort ev. markdown-format
    import re
    match = re.search(r"{.*}", raw_text, re.DOTALL)
    json_str = match.group() if match else ""

    return json.loads(json_str)

