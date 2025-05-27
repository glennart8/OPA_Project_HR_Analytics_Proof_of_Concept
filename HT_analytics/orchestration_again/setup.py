from setuptools import find_packages, setup

setup(
    name="orchestration_again",
    packages=find_packages(exclude=["orchestration_again_tests"]),
    install_requires=[
        "dagster",
        "dagster-dlt",
        "dagster-dbt",
        "dagster-webserver",
        "dlt",  # Själva DLT-ramverket
        "duckdb",  # Eftersom du skriver till DuckDB
        "dbt-core",  # Om du använder dbt CLI eller core-funktionalitet
    ],
    extras_require={
        "dev": [
            "dagster-cloud",
            "pytest",
        ],
    },
)
