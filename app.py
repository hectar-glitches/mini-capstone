import streamlit as st
import pandas as pd
from src.data_loader import (
    load_data, set_shared_data, get_shared_data, get_data_info
)

st.set_page_config(
    page_title="Data Analyzer Dashboard",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="expanded"
)

st.title("📊 Data Analyzer Dashboard")
st.markdown("### A comprehensive tool for exploring and analyzing CSV data")

# Sidebar
with st.sidebar:
    st.header("📁 Data Upload")
    uploaded_file = st.file_uploader("Upload CSV file", type=['csv'])
    
    if uploaded_file:
        # Load and cache data
        df = load_data(uploaded_file)
        
        if df is not None:
            # Store in session state for multi-page access
            set_shared_data(df)
            
            st.success("✅ File loaded successfully!")
            
            # Show basic info
            info = get_data_info(df)
            st.metric("Rows", f"{info['rows']:,}")
            st.metric("Columns", info['columns'])
            st.metric("Size", f"{info['memory_mb']:.2f} MB")
    else:
        st.info("Upload a CSV file to begin analysis")

# Main content
df = get_shared_data()

if df is not None:
    st.markdown("---")
    
    # Quick overview section
    st.subheader("📋 Quick Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    Info = get_data_info(df)
    
    with col1:
        st.metric("Total Rows", f"{info['rows']:,}")
    with col2:
        st.metric("Total Columns", info['columns'])
    with col3:
        st.metric("Numeric Columns", info['numeric_cols'])
    with col4:
        st.metric("DateTime Columns", info['datetime_cols'])
    
    # Data preview
    st.subheader("🔍 Data Preview")
    st.dataframe(df.head(10), use_container_width=True)
    
    # Column information
    st.subheader("📊 Column Information")
    
    col_info = []
    for col in df.columns:
        col_info.append({
            'Column Name': col,
            'Data Type': str(df[col].dtype),
            'Non-Null Count': df[col].count(),
            'Null Count': df[col].isnull().sum(),
            'Unique Values': df[col].nunique()
        })
    
    col_df = pd.DataFrame(col_info)
    st.dataframe(col_df, use_container_width=True)
    
    # Quick visualization
    st.subheader("📈 Quick Visualization")
    
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    if len(numeric_cols) >= 1:
        col1, col2 = st.columns([1, 3])
        
        with col1:
            if len(numeric_cols) >= 2:
                st.write("**Scatter Plot**")
                x_col = st.selectbox("X-axis", numeric_cols, key='x')
                y_col = st.selectbox(
                    "Y-axis",
                    [col for col in numeric_cols if col != x_col],
                    key='y'
                )
                
                import plotly.express as px
                fig = px.scatter(df, x=x_col, y=y_col, opacity=0.6)
                fig.update_layout(template='plotly_white', height=400)
            else:
                st.write("**Histogram**")
                selected_col = st.selectbox("Select column", numeric_cols)
                
                import plotly.express as px
                fig = px.histogram(df, x=selected_col)
                fig.update_layout(template='plotly_white', height=400)
        
        with col2:
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No numeric columns available for quick visualization")
    
    # Navigation guide
    st.markdown("---")
    st.subheader("🧭 Navigate to Analysis Pages")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **📊 Overview Page**
        - Comprehensive data statistics
        - Distribution analysis
        - Correlation heatmaps
        - Data quality reports
        """)
    
    with col2:
        st.markdown("""
        **📈 Time Series Page**
        - Interactive time-series plots
        - Pattern analysis (hourly, daily, weekly)
        - Date range filtering
        - Time-based aggregations
        """)
    
    st.info("👈 Use the sidebar to navigate between pages")

else:
    # Welcome message when no data is loaded
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        ## 🚀 Getting Started
        
        1. **Upload your CSV file** using the sidebar
        2. **Explore the data** on this home page
        3. **Navigate** to specialized analysis pages:
           - 📊 **Overview**: Comprehensive statistics and distributions
           - 📈 **Time Series**: Temporal pattern analysis
        
        ---
        
        ### ✨ Features
        
        - **Interactive Visualizations**: Explore your data with dynamic charts
        - **Statistical Analysis**: Get detailed descriptive statistics
        - **Time Series Support**: Automatic datetime detection and pattern analysis
        - **Data Quality Reports**: Identify missing values and duplicates
        - **Export Capabilities**: Download filtered and analyzed data
        
        ---
        
        ### 📝 Supported Data
        
        - CSV files with any structure
        - Numeric, categorical, and datetime columns
        - Time-series data with automatic detection
        - Large datasets with efficient caching
        """)
