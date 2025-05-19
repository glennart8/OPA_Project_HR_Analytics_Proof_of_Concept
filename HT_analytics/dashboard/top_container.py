import streamlit as st
from dashboard_common import get_connection



con = get_connection()

#############################    TOP-CONTAINER    ##################################
with st.container():
    col_filter, col_statistik = st.columns([1, 1])
   
    def filter_jobs ():
        # --- FILTRERING ---
        with col_filter:
            st.markdown("### 🔎 Filtrera jobbannonser")
            col_kommun, col_falt, col_yrke = st.columns(3)

            with col_kommun:
                municipalities = con.execute(""" 
                    SELECT DISTINCT workplace_municipality 
                    FROM refined.dim_employer 
                """).fetchdf()['workplace_municipality'].dropna().sort_values().tolist()
                municipalities = ['Alla'] + municipalities
                municipality_filter = st.selectbox("Välj kommun:", municipalities)

            with col_falt:
                occupation_fields = con.execute("""
                    SELECT DISTINCT occupation_field
                    FROM refined.dim_occupation
                """).fetchdf()['occupation_field'].dropna().sort_values().tolist()
                occupation_fields = ['Alla'] + occupation_fields
                occupation_field_filter = st.selectbox("Välj yrkesfält:", occupation_fields)

            with col_yrke:
                occupations = con.execute("""
                    SELECT DISTINCT occupation
                    FROM refined.dim_occupation
                    WHERE occupation_field = ?
                """, (occupation_field_filter,)).fetchdf()['occupation'].dropna().sort_values().tolist()
                occupations = ['Alla'] + occupations
                occupation_filter = st.selectbox("Välj yrkeskategori:", occupations)
                
        return municipality_filter, occupation_field_filter, occupation_filter
            
                    
    def get_jobs(municipality_filter, occupation_field_filter, occupation_filter):                    
        # --- HÄMTA FILTRERAD DATA EFTER FILTERNING --- 
            # VAR TVUNGEN ATT HA DISTINCT HÄR, ANNARS KOM DUBLETTER MED
        query = """
            SELECT DISTINCT * 
            FROM marts.mart_vacancies_by_mun_field_occ
            WHERE 1=1
        """
        params = []

        if municipality_filter != 'Alla':
            query += " AND workplace_municipality = ?"
            params.append(municipality_filter.lower())

        if occupation_field_filter != 'Alla':
            query += " AND occupation_field = ?"
            params.append(occupation_field_filter)

        if occupation_filter != 'Alla':
            query += " AND occupation = ?"
            params.append(occupation_filter)

        query += " ORDER BY occupation"

        filtered_jobs = con.execute(query, params).fetchdf()
        
        filtered_jobs_to_show = (
            filtered_jobs
            .drop(columns=["workplace_municipality", "occupation_field", "job_details_id"])
            .rename(columns={"occupation": "Yrke", "employer_name": "Arb.givare", "vacancies": "Antal tjänster", "employer_organization_number": "Org.Nr"})
        )
        
        return filtered_jobs_to_show
        

        # --- GENERELL STATISTIK ---
        with col_statistik:

            if not (occupation_field_filter != 'Alla'):
                if not filtered_jobs.empty:
                    stats_df = (
                        filtered_jobs
                        .groupby("occupation_field")
                        .size()
                        .reset_index(name="total_vacancies")
                    )

                    # Skapa exakt 4 kolumner för jämn layout
                    stat_cols = st.columns(4)
                    symbols = [":hammer:", ":performing_arts:", ":female-teacher:"]
                    
                    
                    with stat_cols[0]:
                        st.write("")
                        st.metric("Antal jobbannonser", len(filtered_jobs))

                    for col, (index, row), symbol in zip(stat_cols[1:], stats_df.iterrows(), symbols):
                        
                        with col:
                            st.write("")
                            st.metric(label=f"{symbol} {row['occupation_field']}", value=row["total_vacancies"])
                    
                else:
                    st.info("Ingen statistik tillgänglig för det valda filtret.")