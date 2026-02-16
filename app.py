import streamlit as st
from src.data_loader import load_data
from src.visualizations import create_chart
from src.analyzer import analyze_data

st.set_page_config(page_title="Data Analyzer", layout="wide")

st.title(" Data Analyzer Dashboard")

# Sidebar
with st.sidebar:
    st.header("Controls")
    uploaded_file = st.file_uploader("Upload CSV", type=['csv'])
    
# Main content
if uploaded_file:
    df = load_data(uploaded_file)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Data Preview")
        st.dataframe(df)
        
    with col2:
        st.subheader("Statistics")
        stats = analyze_data(df)
        st.json(stats)
    
    st.subheader("Visualizations")
    chart = create_chart(df)
    st.plotly_chart(chart, use_container_width=True)
else:
    st.info("👈 Upload a CSV file to get started")
