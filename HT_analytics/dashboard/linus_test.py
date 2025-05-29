import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from dashboard_common import get_connection
def linus_stats():
    # # setup
    # st.set_page_config(
    #     page_title="Skills Analysis Dashboard",
    #     page_icon="🎯",
    #     layout="wide"
    # )

    st.title("🎯 Job Skills Analysis Dashboard")
    st.markdown("Analysis of skills requirements from jobs with special requirements")

    # Load data
    @st.cache_data
    def load_data():
        connection = get_connection()
        return pd.read_sql(
            "SELECT * FROM marts.mart_special_req", 
            connection
        )

    # Load data
    df = load_data()

    # filters
    st.sidebar.header("Filters")

    # Filter skill type
    all_skill_types = df['skill_requirement_type'].dropna().unique().tolist()
    skill_types_options = ["All"] + sorted(all_skill_types)

    selected_skill_types = st.sidebar.multiselect(
        "Skill Requirement Type",
        options=skill_types_options,
        default=["All"]
    )

    # logic
    if "All" in selected_skill_types or not selected_skill_types:
        selected_skill_types = all_skill_types


    #Municipality Filter
    all_municipalities = sorted(df['municipality'].dropna().astype(str).unique().tolist())
    municipality_options = ["All"] + all_municipalities
    selected_municipalities = st.sidebar.multiselect(
        "Municipality",
        options=municipality_options,
        default=["All"]
    )

    if "All" in selected_municipalities or not selected_municipalities:
        selected_municipalities = all_municipalities


    # Title Filter
    all_job_titles = sorted(df['job_title'].dropna().unique().tolist())
    job_title_options = ["All"] + all_job_titles
    selected_job_titles = st.sidebar.multiselect(
        "Job Title",
        options=job_title_options,
        default=["All"]
    )

    if "All" in selected_job_titles or not selected_job_titles:
        selected_job_titles = all_job_titles


    # Apply filters
    filtered_df = df[
        (df['skill_requirement_type'].isin(selected_skill_types)) &
        (df['municipality'].astype(str).isin(selected_municipalities)) &
        (df['job_title'].isin(selected_job_titles))
    ]


    # Main
    col1, col2 = st.columns([2, 1]) 

    with col1:
        st.subheader("📊 Most In-Demand Skills")
        skills_count = filtered_df.groupby(['skill_needed', 'skill_requirement_type']).size().reset_index(name='count')
        skills_total = skills_count.groupby('skill_needed')['count'].sum().sort_values(ascending=False)
        
        # Bar chart
        fig_bar = px.bar(
            skills_count.merge(skills_total.reset_index().rename(columns={'count': 'total_count'}), on='skill_needed')
            .sort_values('total_count', ascending=False).head(20),
            x='skill_needed',
            y='count',
            color='skill_requirement_type',
            title="Top 20 Skills by Demand",
            color_discrete_map={'Must_have': '#FF6B6B', 'nice_to_have': '#4ECDC4'},
            height=400
        )
        fig_bar.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        st.subheader("📈 Summary Statistics")
        
        # Key metrics
        total_jobs = len(filtered_df['job_title'].unique())
        total_skills = len(filtered_df['skill_needed'].unique())
        avg_skills_per_job = len(filtered_df) / total_jobs if total_jobs > 0 else 0
        
        st.metric("Total Unique Jobs", total_jobs)
        st.metric("Total Unique Skills", total_skills)
        st.metric("Avg Skills per Job", f"{avg_skills_per_job:.1f}")
        
        # Skill type distribution
        skill_type_dist = filtered_df['skill_requirement_type'].value_counts()
        
        fig_pie = px.pie(
            values=skill_type_dist.values,
            names=skill_type_dist.index,
            title="Must Have vs Nice to Have",
            color_discrete_map={'must_have': '#FF6B6B', 'nice_to_have': '#4ECDC4'}
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # Data Table
    st.subheader("📋 Detailed Data")
    with st.expander("View Raw Data"):
        st.dataframe(
            filtered_df.groupby(['skill_needed', 'skill_requirement_type', 'municipality'])
            .size().reset_index(name='job_count')
            .sort_values('job_count', ascending=False),
            use_container_width=True
        )
