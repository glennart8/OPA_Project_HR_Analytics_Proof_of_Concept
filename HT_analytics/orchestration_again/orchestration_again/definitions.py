from orchestration_again.dbt_assets import dbt_assets_def, dbt_job
from orchestration_again.dlt_assets import dlt_load, dlt_job
from dagster import Definitions
from dagster_dbt import DbtCliResource
from pathlib import Path

# Justera till din projektsökväg!
DBT_PROJECT_DIR = Path(__file__).resolve().parents[2] 
DBT_PROFILES_DIR = None  # eller din profiles_dir om du har en sådan

defs = Definitions(
    assets=[dlt_load, dbt_assets_def],
    jobs=[dlt_job, dbt_job],
    resources={
        "dbt": DbtCliResource(
            project_dir=DBT_PROJECT_DIR,
            profiles_dir=DBT_PROFILES_DIR,
        )
    }
)
