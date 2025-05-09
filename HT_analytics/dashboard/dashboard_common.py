import pandas as pd
import duckdb

def get_connection():
    return duckdb.connect("../job_ads.duckdb")

def load_data(query):
    con = get_connection()
    return con.execute(query).df()