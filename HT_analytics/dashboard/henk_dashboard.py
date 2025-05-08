# VÄLJ KOMMUN
dim_employer = con.execute("SELECT * FROM refined.dim_employer").fetchdf()
product_filter = st.selectbox("Välj kommun:", dim_employer['workplace_address__municipality'].unique())
# VÄLJ YRKESTITEL

# VÄLJ nåt mer
