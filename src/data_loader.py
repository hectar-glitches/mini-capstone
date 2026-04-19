import pandas as pd
import streamlit as st
from src.data_fetcher import fetch_data


# Global data store using session state
def set_shared_data():
    """
    Store dataframe in session state for multi-page access.
    
    Args: None
    Returns: None
    """
    df = load_data()
    st.session_state['shared_df'] = df


def get_shared_data():
    """
    Retrieve dataframe from session state.
    
    Args: None
    Returns: Shared DataFrame
    """
    return st.session_state.get('shared_df', None)


@st.cache_data
def load_data():
    """
    Load and cache data from uploaded file.
    
    Args: None
    Returns: DataFrame for session use
    """
    try:
        file = fetch_data()  # Fetch data from the source (e.g., TEPCO website)
        df = pd.read_csv(file, encoding="utf-8-sig", skiprows=1)
        
        # Auto-detect and convert datetime columns first
        for col in df.columns:
            # Try to convert to datetime if column name suggests it's a date
            if any(keyword in col.lower() for keyword in ['date', 'time', 'timestamp', 'datetime']):
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Try to convert numeric columns (force conversion, coerce errors to NaN)
        for col in df.columns:
            # Skip if already datetime
            if df[col].dtype != 'datetime64[ns]':
                # Try converting to numeric, coerce non-numeric to NaN
                converted = pd.to_numeric(df[col], errors='coerce')
                # Only keep conversion if at least some values are numeric
                if converted.notna().sum() > 0:
                    df[col] = converted
    
        # Optional: Rename Japanese columns to English (only if they exist)
        rename_map = {
            "DATE": "date",
            "TIME": "time",
            "エリア需要": "area_demand_mw",
            "原子力": "nuclear_mw",
            "火力(LNG)": "thermal_lng_mw",
            "火力(石炭)": "thermal_coal_mw",
            "火力(石油)": "thermal_oil_mw",
            "火力(その他)": "thermal_other_mw",
            "水力": "hydro_mw",
            "地熱": "geothermal_mw",
            "バイオマス": "biomass_mw",
            "太陽光発電実績": "solar_actual_mw",
            "太陽光出力制御量": "solar_curtailment_mw",
            "風力発電実績": "wind_actual_mw",
            "風力出力制御量": "wind_curtailment_mw",
            "揚水": "pumped_hydro_mw",
            "蓄電池": "battery_mw",
            "連系線": "interconnector_mw",
            "その他": "other_mw",
            "合計": "total_supply_mw",
        }
        
        # Only rename columns that actually exist in the dataframe
        existing_renames = {k: v for k, v in rename_map.items() if k in df.columns}
        df = df.rename(columns=existing_renames)

        return df

    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None


def time_now_for_display():
    """
    Get the data for the previous month for 'live-display' mockup.
    
    Args:
    None
    Returns:
    String representing the previous month in "YYYY-MM" format
    """
    now = pd.Timestamp.now()
    previous_month = now - pd.DateOffset(months=1)
    return previous_month.strftime("%Y-%m")


def get_time_from_df():
    """
    Function to filter the DataFrame for the previous month (for 'live-display' mockup).
    
    Args:
    None
    Returns:
    DataFrame containing the data for the past 24 hours
    """
    df = get_shared_data()
    if df is None:
        return None
    
    display_time = time_now_for_display()
    filtered_df = df[df['date'].dt.strftime("%Y-%m") == display_time]
    
    return filtered_df
    

def get_data_info():
    """
    Get basic information about the dataset.
    
    Args: None
    Returns: Overview of the DataFrame
    """

    df = get_shared_data()
    if df is None:
        return None
    
    return {
        'rows': len(df),
        'columns': len(df.columns),
        'numeric_cols': len(df.select_dtypes(include=['number']).columns),
        'datetime_cols': len(df.select_dtypes(include=['datetime64']).columns),
        'object_cols': len(df.select_dtypes(include=['object']).columns),
        'memory_mb': df.memory_usage(deep=True).sum() / 1024**2
    }


def percentages():
    """
    Calculates the percentage of each power source for a time period
    
    Keyword arguments:
    df -- DataFrame containing power source data
    Return: DataFrame with percentage of each power source
    """
    df = get_shared_data()
    if df is None:
        return None
    
    percentage_df = df.copy()
    numeric_cols = df.select_dtypes(include=['number']).columns
    for col in numeric_cols:
        percentage_df[col] = df[col] / df[numeric_cols].sum(axis=1) * 100
    
    return percentage_df


def calculate_renewable_percentage():
    """
    Calculates the percentage of renewable energy sources in the total supply
    
    Keyword arguments:
    df -- DataFrame containing power source data
    Return: Percentage of renewable energy sources
    """