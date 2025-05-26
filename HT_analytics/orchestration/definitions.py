# ==================== #
#        Set Up        #
# ==================== #

import dagster as dg
from dagster_dbt import DbtCliResource, DbtProject, dbt_assets
from dagster_dlt import DagsterDltResource, dlt_assets
import dlt
from pathlib import Path
import sys
from pipeline import jobads_source

# En asset är en funktion eller process som skapar något.
# När du definierar en asset i kod gör du en funktion som skapar (yieldar eller returnerar) just den biten data.

# dlt_resource - Du har en datakälla som hämtar rådata från ett API 
# dbt_resource - Du processar och transformerar datan med dbt
# schedule - Du vill automatisera detta så att hämtningen körs varje dag kl 14.
# sensors - När hämtningen är klar, kör du dbt-transformationerna.
# Allt definieras i defs som Dagster laddar och kör.

# @dlt.resource definierar hur du hämtar data från API.
# @dlt.source grupperar en eller flera resources till en källa.
# @dlt_assets skapar assets baserat på en dlt-pipeline.
# @dbt_assets gör dbt-modeller till assets.
# dg.define_asset_job definierar vilka assets som ska köras i ett jobb.
# dg.ScheduleDefinition säger när ett jobb ska köras automatiskt.
# @dg.asset_sensor startar ett jobb när ett asset ändras (t.ex. efter ett annat jobb).

# Lägg till sökvägen till rootmappen OPA..
root = Path(__file__).parents[2]  # Går två steg upp från orchestration/
sys.path.insert(0, str(root)) # För att hänvisa till var modulerna ska importeras ifrån

# VI HAR INGEN SOURCE I PIPELINEN
from pipeline import jobads_source
 
# Gå upp ett steg till HT_Analytics och peka på filen
db_path = str(Path(__file__).parents[1] / "job_ads.duckdb")


# ==================== #
#       dlt Asset      #
# ==================== #

dlt_resource = DagsterDltResource() # VAD GÖR DENNA?

@dlt_assets(
    dlt_source = jobads_source(),
    dlt_pipeline = dlt.pipeline(
        pipeline_name="jobads_hits",
        dataset_name="staging",
        destination=dlt.destinations.duckdb(db_path)
    )
)
                                                    
def dlt_load(context, dlt):
  yield from dlt.run(context=context)


# ==================== #
#       dbt Asset      #
# ==================== #

# DBT-PROJEKT MAPP
dbt_project_directory = Path(__file__).parents[1]
profiles_dir = Path.home() / ".dbt" # IS THIS CORRECT?!  

# SKAPAR SJÄLVA DBT-PROJEKTET MED OVANSTÅENDE TVÅ PARAMETRAR
dbt_project = DbtProject(project_dir=dbt_project_directory, # TAR IN VÅR DBT-FOLDER
                         profiles_dir=profiles_dir)         # TAR IN VÅR PROFILES.YAML

# References the dbt project object
dbt_resource = DbtCliResource(project_dir=dbt_project) # VAD HÄNDER HÄR?

# Compiles the dbt project & allow Dagster to build an asset graph
dbt_project.prepare_if_dev() # FÖRSTÅR INTE......

# Yields Dagster events streamed from the dbt CLI
@dbt_assets(manifest=dbt_project.manifest_path,) # Gör alla dbt-modeller till Dagster assets, baserat på manifestet.
def dbt_models(context: dg.AssetExecutionContext, dbt: DbtCliResource):
    yield from dbt.cli(["build"], context=context).stream() # kör modellerna


# ==================== #
#         Job          #
# ==================== #

# Definirerar ett dlt- och ett dbt-jobb.
job_dlt = dg.define_asset_job("job_dlt", selection=dg.AssetSelection.keys("dlt_jobads_source_jobsearch_resource"))
# job_dbt = dg.define_asset_job("job_dbt", selection=dg.AssetSelection.keys("staging/original_headline"))
job_dbt = dg.define_asset_job("job_dbt", selection=dg.AssetSelection.assets(["dbt_mobels"])) # VILKA ASSETS SKA KÖRAS, ALLA SKA VÄL KÖRAS?


# ==================== #
#       Schedule       #
# ==================== #

# Schemalägg dlt inhämtning
schedule_dlt = dg.ScheduleDefinition(
    job=job_dlt,
    cron_schedule="17 12 * * *" #UTC
)

# ==================== #
#        Sensor        #
# ==================== #

# Sätt en sensor som reagerar på när dlt körs och startar nästa jobb
@dg.asset_sensor(
  asset_key=dg.AssetKey("dlt_jobads_source_jobsearch_resource"),
  job_name="job_dbt",
)
def dlt_load_sensor():
  yield dg.RunRequest()


# ==================== #
#     Definitions      #
# ==================== #

# Dagster object that contains the dbt assets and resource
defs = dg.Definitions(
                    assets=[dlt_load, dbt_models], 
                    resources={"dlt": dlt_resource,
                               "dbt": dbt_resource},
                    jobs=[job_dlt, job_dbt],
                    schedules=[schedule_dlt],
                    sensors=[dlt_load_sensor],
                    )