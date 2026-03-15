import streamlit as st
import pandas as pd
from src.data_loader import get_shared_data
from src.visualizations import create_timeseries_chart, create_pattern_analysis_chart
from src.analyzer import detect_time_patterns, get_time_aggregations

st.set_page_config(page_title="Time Series Analysis", layout="wide")

st.title("Time Series Analysis")

# Get shared data
df = get_shared_data()

if df is None:
    st.info(" Upload a CSV file from the Home page to get started")
    st.stop()

# Detect datetime columns
datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
potential_datetime_cols = []

for col in df.columns:
    if col not in datetime_cols:
        try:
            pd.to_datetime(df[col], errors='coerce')
            if pd.to_datetime(df[col], errors='coerce').notna().sum() > len(df) * 0.5:
                potential_datetime_cols.append(col)
                
        except Exception:
            raise ValueError(f"Error processing column {col} for datetime conversion")

all_time_cols = datetime_cols + potential_datetime_cols

if not all_time_cols:
    st.warning(" No datetime columns detected in the dataset. This page is designed for time-series data.")
    st.info("**Tip**: Ensure your dataset has a column with dates/timestamps. The column should be in a recognizable date format (e.g., YYYY-MM-DD, MM/DD/YYYY, etc.)")
    st.stop()

# Sidebar controls
with st.sidebar:
    st.header("Time Series Controls")
    
    # Select datetime column
    time_col = st.selectbox("Select time column", all_time_cols)
    
    # Convert to datetime if needed
    if time_col not in datetime_cols:
        df[time_col] = pd.to_datetime(df[time_col], errors='coerce')
    
    # Remove rows with invalid dates
    df = df.dropna(subset=[time_col])
    df = df.sort_values(time_col)
    
    # Select numeric columns to plot
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    if not numeric_cols:
        st.error("No numeric columns found for time-series plotting")
        st.stop()
    
    value_cols = st.multiselect(
        "Select value columns to plot",
        numeric_cols,
        default=numeric_cols[:3] if len(numeric_cols) >= 3 else numeric_cols
    )
    
    # Date range filter
    st.subheader("Date Range Filter")
    min_date = df[time_col].min().date()
    max_date = df[time_col].max().date()
    
    date_range = st.date_input(
        "Select date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Aggregation options
    st.subheader("Aggregation")
    aggregation = st.selectbox(
        "Time aggregation",
        ["None", "Hourly", "Daily", "Weekly", "Monthly"],
        help="Aggregate data points by time period"
    )
    
    if aggregation != "None":
        agg_func = st.selectbox(
            "Aggregation function",
            ["mean", "sum", "min", "max", "median"]
        )

# Filter by date range
if len(date_range) == 2:
    start_date, end_date = date_range
    mask = (df[time_col].dt.date >= start_date) & (df[time_col].dt.date <= end_date)
    df_filtered = df[mask].copy()
else:
    df_filtered = df.copy()

if value_cols:
    # Main time series visualization
    st.subheader("Time Series Plot")
    
    # Apply aggregation if selected
    if aggregation != "None":
        df_plot = get_time_aggregations(df_filtered, time_col, value_cols, aggregation.lower(), agg_func)
    else:
        df_plot = df_filtered
    
    fig = create_timeseries_chart(df_plot, time_col, value_cols)
    st.plotly_chart(fig, use_container_width=True)
    
    # Pattern analysis
    st.subheader("Pattern Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        pattern_type = st.selectbox(
            "Pattern type",
            ["Hourly", "Day of Week", "Monthly", "Seasonal"]
        )
    
    with col2:
        pattern_col = st.selectbox(
            "Select column for pattern analysis",
            value_cols
        )
    
    if pattern_col:
        patterns = detect_time_patterns(df_filtered, time_col, pattern_col, pattern_type.lower().replace(" ", "_"))
        
        if patterns is not None:
            fig_pattern = create_pattern_analysis_chart(patterns, pattern_type, pattern_col)
            st.plotly_chart(fig_pattern, use_container_width=True)
            
            # Show pattern statistics
            st.subheader(f"{pattern_type} Statistics")
            st.dataframe(patterns, use_container_width=True)
    
    # Summary statistics for time period
    st.subheader("Time Period Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Data Points", f"{len(df_filtered):,}")
    with col2:
        st.metric("Time Span", f"{(df_filtered[time_col].max() - df_filtered[time_col].min()).days} days")
    with col3:
        if value_cols:
            st.metric("Avg Value", f"{df_filtered[value_cols[0]].mean()/1000:.2f}MW")
    with col4:
        if value_cols:
            st.metric("Total", f"{df_filtered[value_cols[0]].sum()/1000000:.2f}GW")

else:
    st.info("Please select at least one value column to plot")
