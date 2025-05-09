# BY CITY
import pandas as pd
import duckdb
import plotly
import streamlit as st
from dashboard_common import load_data

query = "SELECT * FROM marts.mart_vacancies_by_city"

df = load_data(query)

st.title("Jobbdetaljer")
st.dataframe(df)


