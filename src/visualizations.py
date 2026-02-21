import plotly.express as px
import plotly.graph_objects as go


def create_chart(df):
    """Create a simple visualization from dataframe."""
    numeric_cols = df.select_dtypes(include=['number']).columns
    
    if len(numeric_cols) >= 2:
        fig = px.scatter(df, x=numeric_cols[0], y=numeric_cols[1])
    elif len(numeric_cols) == 1:
        fig = px.histogram(df, x=numeric_cols[0])
    else:
        fig = px.bar(
            x=df.columns,
            y=[len(df)] * len(df.columns),
            labels={'x': 'Columns', 'y': 'Count'}
        )

    return fig


def create_distribution_chart(df, column, chart_type='histogram'):
    """Create distribution visualization for a single column."""
    if chart_type == 'histogram':
        fig = px.histogram(
            df,
            x=column,
            title=f'Distribution of {column}',
            labels={column: column, 'count': 'Frequency'},
            marginal='box'
        )
    elif chart_type == 'box_plot':
        fig = px.box(
            df,
            y=column,
            title=f'Box Plot of {column}',
            labels={column: 'Value'}
        )
    elif chart_type == 'violin_plot':
        fig = px.violin(
            df,
            y=column,
            title=f'Violin Plot of {column}',
            labels={column: 'Value'},
            box=True
        )
    else:
        fig = px.histogram(df, x=column)
    
    fig.update_layout(
        template='plotly_white',
        hovermode='x unified'
    )

    return fig


def create_correlation_heatmap(df):
    """Create correlation heatmap for numeric columns."""
    numeric_df = df.select_dtypes(include=['number'])
    
    if len(numeric_df.columns) < 2:
        return None

    corr_matrix = numeric_df.corr()
    
    fig = px.imshow(
        corr_matrix,
        title='Correlation Matrix',
        labels=dict(color="Correlation"),
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        color_continuous_scale='RdBu_r',
        zmin=-1,
        zmax=1,
        aspect='auto'
    )
    
    fig.update_layout(
        template='plotly_white',
        width=700,
        height=700
    )

    return fig


def create_timeseries_chart(df, time_col, value_cols):
    """Create interactive time-series chart."""
    fig = go.Figure()

    for col in value_cols:
        fig.add_trace(go.Scatter(
            x=df[time_col],
            y=df[col],
            mode='lines+markers',
            name=col,
            hovertemplate=(
                f'<b>{col}</b><br>%{{x}}<br>'
                'Value: %{y:.2f}<extra></extra>'
            )
        ))
    
    fig.update_layout(
        title='Time Series Visualization',
        xaxis_title='Time',
        yaxis_title='Value',
        template='plotly_white',
        hovermode='x unified',
        showlegend=True,
        height=500
    )

    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(
                    count=1, label="1d", step="day",
                    stepmode="backward"
                ),
                dict(
                    count=7, label="1w", step="day",
                    stepmode="backward"
                ),
                dict(
                    count=1, label="1m", step="month",
                    stepmode="backward"
                ),
                dict(
                    count=3, label="3m", step="month",
                    stepmode="backward"
                ),
                dict(step="all", label="All")
            ])
        )
    )

    return fig


def create_pattern_analysis_chart(pattern_df, pattern_type, value_col):
    """Create pattern analysis visualization."""
    x_col = pattern_df.columns[0]  # First column is the grouping

    fig = go.Figure()

    # Add mean line
    fig.add_trace(go.Scatter(
        x=pattern_df[x_col],
        y=pattern_df['mean'],
        mode='lines+markers',
        name='Mean',
        line=dict(color='blue', width=3),
        hovertemplate='<b>Mean</b><br>%{x}<br>%{y:.2f}<extra></extra>'
    ))
    
    # Add min/max range
    if 'min' in pattern_df.columns and 'max' in pattern_df.columns:
        fig.add_trace(go.Scatter(
            x=pattern_df[x_col],
            y=pattern_df['max'],
            mode='lines',
            name='Max',
            line=dict(color='lightblue', dash='dash'),
            hovertemplate='<b>Max</b><br>%{x}<br>%{y:.2f}<extra></extra>'
        ))

        fig.add_trace(go.Scatter(
            x=pattern_df[x_col],
            y=pattern_df['min'],
            mode='lines',
            name='Min',
            line=dict(color='lightblue', dash='dash'),
            fill='tonexty',
            hovertemplate='<b>Min</b><br>%{x}<br>%{y:.2f}<extra></extra>'
        ))
    
    fig.update_layout(
        title=f'{pattern_type} Pattern Analysis for {value_col}',
        xaxis_title=pattern_type,
        yaxis_title=value_col,
        template='plotly_white',
        hovermode='x unified',
        height=400
    )

    return fig
