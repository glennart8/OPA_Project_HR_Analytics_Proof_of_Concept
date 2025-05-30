import dlt
from pathlib import Path
import dagster as dg
from dagster_dlt import DagsterDltResource, dlt_assets

# === DATABASE ===
db_path = str(Path(__file__).parent / "HT_analytics/job_ads.duckdb")

# === IMPORTERA DIN DLT-KÄLLA ===
from pipeline import jobads_source

dlt_resource = DagsterDltResource()

# === DAGSTER-ASSET ===
@dlt_assets(
    dlt_source=jobads_source(),
    dlt_pipeline = dlt.pipeline( # HÄR AHDE VI SKRIVIT PIPELINE BARA
        pipeline_name="jobads_hits",
        dataset_name="staging",
        destination=dlt.destinations.duckdb(db_path),
    ),
)
def dlt_load(context: dg.AssetExecutionContext, dlt: DagsterDltResource): # MÅSTE HA EMD CONTEXT OCH RESOURCE
    yield from dlt.run(context=context) #yield all items from running the pipeline

# === JOB ===
dlt_job = dg.define_asset_job("dlt_job", selection=dg.AssetSelection.keys("dlt_jobads_source_jobsearch_resource")) # BEHÖVER HETA SOM FUNKTIONERNA

# === SCHEDULE ===
schedule_dlt = dg.ScheduleDefinition(
    job=dlt_job,
    cron_schedule="33 9 * * *" #UTC
)
