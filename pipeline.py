import dlt
import requests
import json
from pathlib import Path
import os

# Definierar en hjälpfunktion som gör ett GET-anrop mot Jobtechs API och returnerar JSON-svaret som Python-objekt
def _get_ads(url_for_search, params):
    headers = {"accept": "application/json"}
    response = requests.get(url_for_search, headers=headers, params=params)
    response.raise_for_status()  # check for http errors
    
    response.encoding = "utf-8"
    
    return response.json()

# Deklarerar en DLT-resource som strömmar jobbannonser från API:t och lägger till dem i pipelinen utan att skriva över tidigare data
@dlt.resource(write_disposition="append")
def jobsearch_resource(context):
    # Om inga params skickas in, använd dessa default‐värden:
    params = context.metadata.get("params", {
        "q": "",
        "limit": 100,
        "occupation_fields": ["j7Cq_ZJe_GkT", "9puE_nYg_crq", "MVqp_eS8_kDZ"],
    })

    url = "https://jobsearch.api.jobtechdev.se/search"
    for field in params["occupation_fields"]:
        offset = 0
        while True:
            page_params = {
                "q": params["q"],
                "limit": params["limit"],
                "offset": offset,
                "occupation-field": field,
            }
            data = _get_ads(url, page_params)
            hits = data.get("hits", [])
            if not hits:
                break
            yield from hits
            if len(hits) < params["limit"]:
                break
            offset += params["limit"]

# -------------- ENDAST FÖR MANUELL KÖRNING   ---------------
def run_pipeline(query, table_name, occupation_fields):
    # Skapar en pipeline med ett namn och anger att vi använder DuckDB som destination (lokal databasfil)
    pipeline = dlt.pipeline(
        pipeline_name="job_ads_demo",
        destination=dlt.destinations.duckdb("job_ads.duckdb"),
        dataset_name="staging",
    )

    for occupation_field in occupation_fields:
        params = {"q": query, "limit": 100, "occupation-field": occupation_field} # "q" är en sökparameter i Jobtechs API
        
        # Kör pipelinen med datakällan vi skapade (jobsearch_resource) och skickar in API-parametrarna
        pipeline.run( # using run() to start the pipeline
            jobsearch_resource(params=params), table_name=table_name # varför skrivs table_name in som inparameter här?
        )
        
 
# För att det ska funka med dagster behöver vi en dlt-source som ska innehålal en dlt-resource
@dlt.source
def jobads_source():
    return jobsearch_resource 
  

if __name__ == "__main__":
    working_directory = Path(__file__).parent
    os.chdir(working_directory)

    query = ""
    table_name = "job_ads"
    occupation_fields = ("j7Cq_ZJe_GkT", "9puE_nYg_crq", "MVqp_eS8_kDZ") # Teknisk inriktning, "Hälso sjukvård", "Pedagogik"

    run_pipeline(query, table_name, occupation_fields)