import streamlit as st
import pandas as pd
from src.data_loader import load_data, get_shared_data, set_shared_data
from src.visualizations import create_distribution_chart, create_correlation_heatmap
from src.analyzer import get_descriptive_stats, get_data_quality_report

st.set_page_config(page_title="Overview", layout="wide", page_icon="📊")

st.title(" Data Overview")

# Get shared data
df = get_shared_data()

if df is None:
    st.info("👈 Upload a CSV file from the Home page to get started")
    st.stop()

# Sidebar controls
with st.sidebar:
    st.header("Filter Controls")
    
    # Column selection for filtering
    all_columns = df.columns.tolist()
    selected_columns = st.multiselect(
        "Select columns to display",
        all_columns,
        default=all_columns[:10] if len(all_columns) > 10 else all_columns
    )
    
    # Row filtering
    if st.checkbox("Filter rows"):
        max_rows = len(df)
        row_range = st.slider(
            "Select row range",
            0, max_rows,
            (0, min(1000, max_rows))
        )
        df_display = df.iloc[row_range[0]:row_range[1]]
    else:
        df_display = df

# Filter by selected columns if any selected
if selected_columns:
    df_display = df_display[selected_columns]

# Main content
tab1, tab2, tab3 = st.tabs([" Data Preview", " Statistics", " Distributions"])

with tab1:
    st.subheader("Data Preview")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Rows", f"{len(df):,}")
    with col2:
        st.metric("Total Columns", len(df.columns))
    with col3:
        st.metric("Numeric Columns", len(df.select_dtypes(include=['number']).columns))
    with col4:
        st.metric("Memory Usage", f"{df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    
    st.dataframe(df_display, use_container_width=True, height=400)
    
    # Download option
    csv = df_display.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=" Download filtered data as CSV",
        data=csv,
        file_name="filtered_data.csv",
        mime="text/csv",
    )

with tab2:
    st.subheader("Descriptive Statistics")
    
    stats_df = get_descriptive_stats(df)
    if stats_df is not None:
        st.dataframe(stats_df, use_container_width=True)
        
        # Show column data types
        st.subheader("Column Data Types")
        dtype_df = pd.DataFrame({
            'Column': df.dtypes.index,
            'Data Type': df.dtypes.values.astype(str)
        })
        st.dataframe(dtype_df, use_container_width=True)
    else:
        st.info("No numeric columns found for statistical analysis")

with tab3:
    st.subheader("Distribution Analysis")
    
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    if numeric_cols:
        col1, col2 = st.columns(2)
        
        with col1:
            selected_col = st.selectbox("Select column for distribution", numeric_cols)
        
        with col2:
            chart_type = st.selectbox("Chart type", ["Histogram", "Box Plot", "Violin Plot"])
        
        if selected_col:
            fig = create_distribution_chart(df, selected_col, chart_type.lower().replace(" ", "_"))
            st.plotly_chart(fig, use_container_width=True)
        
        # Correlation heatmap
        if len(numeric_cols) > 1:
            st.subheader("Correlation Matrix")
            fig_corr = create_correlation_heatmap(df)
            st.plotly_chart(fig_corr, use_container_width=True)
    else:
        st.info("No numeric columns available for distribution analysis")
