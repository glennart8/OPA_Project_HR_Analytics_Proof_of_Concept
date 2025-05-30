from pathlib import Path
from dagster_dbt import DbtCliResource, DbtProject, dbt_assets
import dagster as dg
from dagster import define_asset_job, AssetSelection


# Sökväg till dbt-projektet
dbt_project_directory = Path(__file__).parent / "HT_analytics"
profiles_dir = Path.home() / ".dbt" 

# Initiera DbtProject
dbt_project = DbtProject(
    project_dir=str(dbt_project_directory),
    profiles_dir=profiles_dir
)

dbt_resource = DbtCliResource(project_dir=dbt_project)

# Förbered manifest (kompilerar vid behov)
dbt_project.prepare_if_dev()


# DBT ASSETS 
# Yields Dagster events streamed from the dbt CLI
@dbt_assets(manifest=dbt_project.manifest_path,) #access metadata of dbt project so that dagster understand structure of the dbt project
def dbt_models(context: dg.AssetExecutionContext, dbt: DbtCliResource):
    yield from dbt.cli(["build"], context=context).stream() #compile the project and collect all results


# DBT JOB
dbt_job = define_asset_job(
    "dbt_job",
    selection = AssetSelection.all() 
)


# SENSOR
@dg.asset_sensor(asset_key=dg.AssetKey("dlt_jobads_source_jobsearch_resource"),
                 job_name="dbt_job")
def dlt_load_sensor():
    yield dg.RunRequest()