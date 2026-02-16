import pandas as pd

def analyze_data(df):
    """Generate basic statistics from dataframe."""
    return {
        "rows": len(df),
        "columns": len(df.columns),
        "numeric_columns": len(df.select_dtypes(include=['number']).columns),
        "missing_values": int(df.isnull().sum().sum())
    }
