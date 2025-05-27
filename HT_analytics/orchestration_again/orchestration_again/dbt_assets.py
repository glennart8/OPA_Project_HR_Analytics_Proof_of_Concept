from dagster import AssetSelection, define_asset_job, Definitions
from dagster_dbt import DbtProject, dbt_assets, DbtCliResource
from pathlib import Path

# Ange var ditt dbt-projekt ligger
DBT_PROJECT_DIR = Path(__file__).resolve().parents[2]  # Går två steg upp till HT_analytics
DBT_PROFILES_DIR = None  # None = använd ~/.dbt/profiles.yml

# Skapa DbtProject-objekt
my_dbt_project = DbtProject(
    project_dir=str(DBT_PROJECT_DIR),
    profiles_dir=DBT_PROFILES_DIR,
)

# Skapa dbt-assets med nya API:t
@dbt_assets(manifest=my_dbt_project.manifest_path, required_resource_keys={"dbt"})
def dbt_assets_def(context):
    yield from context.resources.dbt.cli(["run"]).stream()


# JOB för att köra dbt-assets
dbt_job = define_asset_job(
    name="dbt_transformation_job",
    selection=AssetSelection.groups("analytics")
)
