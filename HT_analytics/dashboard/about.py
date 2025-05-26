import streamlit as st

def show_about_text():
    st.markdown("<hr/>", unsafe_allow_html=True)
    st.markdown("#### Om")
    st.markdown(
        """
        - Data hämtas från Jobtech API och aggregeras i DuckDB.  
        - By: Henke, Jonas, Linus
        """
    )