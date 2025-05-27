import dlt
from pathlib import Path
import sys
from dagster_dlt import dlt_assets

# === DATABASE ===
db_path = str(Path(__file__).parents[2] / "job_ads.duckdb")

# === ROOT ===
root = Path(__file__).parents[3]
sys.path.insert(0, str(root))

# === IMPORTERA DIN DLT-KÄLLA ===
from pipeline import jobads_source

# === SKAPA DIN PIPELINE ===
pipeline = dlt.pipeline(
    pipeline_name="jobads_hits",
    dataset_name="staging",
    destination=dlt.destinations.duckdb(db_path)
)

# === DAGSTER-ASSET ===
@dlt_assets(
    dlt_source=jobads_source(),
    dlt_pipeline=pipeline
)
def dlt_load():
    pipeline.run()  # OBS: INTE "yield from"

# DBT
