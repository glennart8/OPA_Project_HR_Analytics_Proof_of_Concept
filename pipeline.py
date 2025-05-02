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
    return json.loads(response.content.decode("utf8"))

# Deklarerar en DLT-resource som strömmar jobbannonser från API:t och lägger till dem i pipelinen utan att skriva över tidigare data
@dlt.resource(write_disposition="append")
def jobsearch_resource(params):
    """
    params should include at least:
      - "q": your query
      - "limit": page size (e.g. 100)
    """
    url = "https://jobsearch.api.jobtechdev.se"
    url_for_search = f"{url}/search"
    limit = params.get("limit", 100) # Varför 2 gånger? Get() för att kunna använda limit??? Mer återanvändning?
    offset = 0

    # Startar loop för att hämta data sida för sida tills inga fler träffar finns eller maxgräns nåtts
    while True:
        # build this page’s params
        page_params = dict(params, offset=offset) # Varför inte offset i parameterdict? Är det för att offset ändras för varje loop?
        data = _get_ads(url_for_search, page_params)

        hits = data.get("hits", []) # using get() to avoid KeyError if "hits" is not present
        if not hits:
            break

        for ad in hits:
            yield ad

        # Maxgräns
        if len(hits) < limit or offset > 1900:
            break

        offset += limit


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
        

if __name__ == "__main__":
    working_directory = Path(__file__).parent
    os.chdir(working_directory)

    query = ""
    table_name = "job_ads"
    occupation_fields = ("j7Cq_ZJe_GkT", "9puE_nYg_crq", "MVqp_eS8_kDZ") # Teknisk inriktning, "Hälso sjukvård", "Pedagogik"

    run_pipeline(query, table_name, occupation_fields)