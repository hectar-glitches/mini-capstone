import pandas as pd
import streamlit as st

# Global data store using session state
def set_shared_data(df):
    """Store dataframe in session state for multi-page access."""
    st.session_state['shared_df'] = df

def get_shared_data():
    """Retrieve dataframe from session state."""
    return st.session_state.get('shared_df', None)

@st.cache_data
def load_data(file):
    """Load and cache data from uploaded file."""
    try:
        df = pd.read_csv(file)
        
        # Auto-detect and convert datetime columns
        for col in df.columns:
            # Try to convert to datetime if column name suggests it's a date
            if any(keyword in col.lower() for keyword in ['date', 'time', 'timestamp', 'datetime']):
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                except:
                    pass
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

def get_data_info(df):
    """Get basic information about the dataset."""
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
