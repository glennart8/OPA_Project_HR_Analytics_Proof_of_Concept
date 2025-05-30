import streamlit as st
from LLM.llm import get_sql_code, get_results
from dashboard_common import show_buttons

def ask_gemeni(query_for_llm):
    sql_code_from_llm = get_sql_code(query_for_llm)
    # st.write(sql_code_from_llm)
    result_from_llm = get_results(sql_code_from_llm)
    
    if result_from_llm.empty:
        st.warning("Tyvärr finns det inga tjänster ute inom detta område.")
    else:
        st.dataframe(result_from_llm)
        # FUNKAR DÅLIGT HÄR, VISAR VISSA TEXTER MEN INTE ANDRA
        show_buttons(result_from_llm) 
      
def show_filtered_jobs(filtered_jobs, filtered_jobs_to_show, municipality_filter, occupation_field_filter):    
    if filtered_jobs.empty:
        st.warning("Tyvärr finns det inga tjänster ute inom detta område.")
    else:
        # Begränsa till de första 350 resultaten
        limited_jobs_to_show = filtered_jobs_to_show.head(350)
        
        # Styla och visa
        styled_df = limited_jobs_to_show.style.set_properties(**{'color': '#FFC87C'})  # #FFB347
        st.dataframe(styled_df, hide_index=True)

        # Om vi valt de 2 första filtren
        if municipality_filter != 'Alla' and occupation_field_filter != 'Alla':
            show_buttons(filtered_jobs)