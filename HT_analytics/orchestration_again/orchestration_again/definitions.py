from orchestration_again.dbt_assets import dbt_models, dbt_job, dbt_resource
from orchestration_again.dlt_assets import dlt_load, dlt_job, dlt_resource
from dagster import Definitions
from dagster_dbt import DbtCliResource
from pathlib import Path
import dagster as dg


# Justera till din projektsökväg!
DBT_PROJECT_DIR = Path(__file__).resolve().parents[2] 
DBT_PROFILES_DIR = None  # eller din profiles_dir om du har en sådan

defs = dg.Definitions(
                    assets=[dlt_load, dbt_models], 
                    resources={"dlt": dlt_resource,
                               "dbt": dbt_resource},
                    jobs=[dlt_job, dbt_job],
                    # schedules=[schedule_dlt],
                    # sensors=[dlt_load_sensor],
                    )
