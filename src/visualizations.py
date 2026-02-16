import plotly.express as px

def create_chart(df):
    """Create a simple visualization from dataframe."""
    numeric_cols = df.select_dtypes(include=['number']).columns
    
    if len(numeric_cols) >= 2:
        fig = px.scatter(df, x=numeric_cols[0], y=numeric_cols[1])
    elif len(numeric_cols) == 1:
        fig = px.histogram(df, x=numeric_cols[0])
    else:
        fig = px.bar(x=df.columns, y=[len(df)] * len(df.columns), 
                     labels={'x': 'Columns', 'y': 'Count'})
    
    return fig
