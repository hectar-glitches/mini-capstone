import pandas as pd
import streamlit as st

@st.cache_data
def load_data(file):
    """Load and cache data from uploaded file."""
    try:
        df = pd.read_csv(file)
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None
