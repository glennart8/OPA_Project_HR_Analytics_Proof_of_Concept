from dagster import Definitions, load_assets_from_modules
from OPA_Project_HR_Analytics_Proof_of_Concept.pipeline import jobads_source

from orchestration_again import assets  # noqa: TID252

all_assets = load_assets_from_modules([assets])

defs = Definitions(
    assets=all_assets,
)
