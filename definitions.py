from dbt_assets import dbt_models, dbt_job, dbt_resource, dlt_load_sensor
from dlt_assets import dlt_load, dlt_job, dlt_resource, schedule_dlt
from pathlib import Path
import dagster as dg

# Justera till din projektsökväg!
DBT_PROJECT_DIR = Path(__file__).parent / "HT_analytics"
DBT_PROFILES_DIR = Path.home() / ".dbt"

defs = dg.Definitions(
                    assets=[dlt_load, dbt_models], 
                    resources={"dlt": dlt_resource,
                               "dbt": dbt_resource},
                    jobs=[dlt_job, dbt_job],
                    schedules=[schedule_dlt],
                    sensors=[dlt_load_sensor],
                    )
