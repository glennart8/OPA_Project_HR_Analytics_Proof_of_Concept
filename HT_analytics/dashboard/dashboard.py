import pandas as pd
import duckdb
import plotly
import streamlit as st

con = duckdb.connect('../job_ads.duckdb')

df = con.execute("SELECT occupation_field, SUM(total_vacancies) AS total_vacancies FROM marts.mart_vac_per_field GROUP BY occupation_field ORDER BY total_vacancies DESC").fetchdf()
# Lista alla tabeller
#tables = con.execute("SHOW TABLES").fetchall()


# df = con.execute("SELECT * FROM refined.fct_job_ads LIMIT 10" )
# print(df)


# import os
# print("Finns filen?", os.path.exists('../job_ads.duckdb')) # True

### TEST ###

# # Visa alla scheman
# print("Scheman:")
# print(con.execute("SELECT * FROM information_schema.schemata").fetchdf())

# # Visa alla tabeller i alla scheman
# print("\nTabeller:")
# print(con.execute("SELECT * FROM duckdb_tables()").fetchdf())

# # Hämta data från en tabell i staging-schemat, t.ex. job_ads
# df = con.execute("SELECT * FROM staging.job_ads").fetchdf()
# print(df)

###

# MOST WANTED 
df_most_wanted = con.execute("SELECT * FROM marts.mart_most_wanted").df()
print(df_most_wanted)

st.write("Occupation group")
st.dataframe(df_most_wanted)

# NO EXPERIENCE
df_no_experience = con.execute("SELECT * FROM marts.mart_no_experience_req")
st.dataframe(df_no_experience)

# BY OCCUPATION FIELD
df_by_field = con.execute("SELECT * FROM marts.mart_by_occupation_field")
st.subheader("Flest annonser inom Bygg och Anläggning")
st.dataframe(df_by_field)

# BY CITY
df_by_city = con.execute("SELECT * FROM marts.mart_vacancies_by_city")
st.dataframe(df_by_city)
