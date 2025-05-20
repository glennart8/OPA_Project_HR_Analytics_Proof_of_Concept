import streamlit as st

# Visa totala antal jobb och antal jobb inom olika fält

def show_general_statistics(filtered_jobs):
    
    stats_df = (
        filtered_jobs
        .groupby("occupation_field")
        .size()
        .reset_index(name="total_vacancies")
    )

    # Skapar 4 kolumner
    stat_cols = st.columns(4)
    symbols = [":hammer:", ":performing_arts:", ":female-teacher:"]
    
    with stat_cols[0]:
        st.write("")
        st.metric("Antal jobbannonser", len(filtered_jobs))

    for col, (index, row), symbol in zip(stat_cols[1:], stats_df.iterrows(), symbols):
        with col:
            st.write("")
            st.metric(label=f"{symbol} {row['occupation_field']}", value=row["total_vacancies"])
    

