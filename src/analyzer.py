import pandas as pd
import numpy as np


def analyze_data(df):
    """Generate basic statistics from dataframe."""
    return {
        "rows": len(df),
        "columns": len(df.columns),
        "numeric_columns": len(df.select_dtypes(include=['number']).columns),
        "missing_values": int(df.isnull().sum().sum())
    }


def get_descriptive_stats(df):
    """Get comprehensive descriptive statistics for numeric columns."""
    numeric_df = df.select_dtypes(include=['number'])
    
    if numeric_df.empty:
        return None
    
    stats = numeric_df.describe().T
    
    # Add additional statistics
    stats['median'] = numeric_df.median()
    stats['variance'] = numeric_df.var()
    stats['skewness'] = numeric_df.skew()
    stats['kurtosis'] = numeric_df.kurtosis()
    stats['missing'] = numeric_df.isnull().sum()
    stats['missing_pct'] = (numeric_df.isnull().sum() / len(df) * 100).round(2)
    
    # Reorder columns for better readability
    ordered_cols = ['count', 'missing', 'missing_pct', 'mean', 'median', 'std', 
                    'min', '25%', '50%', '75%', 'max', 'variance', 'skewness', 'kurtosis']
    stats = stats[[col for col in ordered_cols if col in stats.columns]]
    
    return stats.round(4)


def get_data_quality_report(df):
    """Generate comprehensive data quality report."""
    total_cells = df.shape[0] * df.shape[1]
    missing_cells = df.isnull().sum().sum()
    
    missing_by_col = df.isnull().sum()
    missing_by_col = missing_by_col[missing_by_col > 0].to_dict()
    
    return {
        'total_missing': int(missing_cells),
        'completeness': ((total_cells - missing_cells) / total_cells * 100) if total_cells > 0 else 0,
        'duplicates': int(df.duplicated().sum()),
        'columns_with_missing': len(missing_by_col),
        'missing_by_column': missing_by_col
    }


def detect_time_patterns(df, time_col, value_col, pattern_type='hourly'):
    """Detect and analyze time-based patterns in data."""
    df = df.copy()
    
    if pattern_type == 'hourly':
        df['group'] = df[time_col].dt.hour
        group_label = 'Hour'
    elif pattern_type == 'day_of_week':
        df['group'] = df[time_col].dt.day_name()
        group_label = 'Day of Week'
        # Order by day
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    elif pattern_type == 'monthly':
        df['group'] = df[time_col].dt.month_name()
        group_label = 'Month'
        month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December']
    elif pattern_type == 'seasonal':
        df['group'] = df[time_col].dt.month.map({
            12: 'Winter', 1: 'Winter', 2: 'Winter',
            3: 'Spring', 4: 'Spring', 5: 'Spring',
            6: 'Summer', 7: 'Summer', 8: 'Summer',
            9: 'Fall', 10: 'Fall', 11: 'Fall'
        })
        group_label = 'Season'
        season_order = ['Winter', 'Spring', 'Summer', 'Fall']
    else:
        return None
    
    # Aggregate patterns
    patterns = df.groupby('group')[value_col].agg([
        ('mean', 'mean'),
        ('median', 'median'),
        ('std', 'std'),
        ('min', 'min'),
        ('max', 'max'),
        ('count', 'count')
    ]).reset_index()
    
    patterns.columns = [group_label, 'mean', 'median', 'std', 'min', 'max', 'count']
    
    # Sort by appropriate order
    if pattern_type == 'day_of_week':
        patterns[group_label] = pd.Categorical(patterns[group_label], categories=day_order, ordered=True)
        patterns = patterns.sort_values(group_label)
    elif pattern_type == 'monthly':
        patterns[group_label] = pd.Categorical(patterns[group_label], categories=month_order, ordered=True)
        patterns = patterns.sort_values(group_label)
    elif pattern_type == 'seasonal':
        patterns[group_label] = pd.Categorical(patterns[group_label], categories=season_order, ordered=True)
        patterns = patterns.sort_values(group_label)
    else:
        patterns = patterns.sort_values(group_label)
    
    return patterns.round(4)


def get_time_aggregations(df, time_col, value_cols, frequency='daily', agg_func='mean'):
    """Aggregate time-series data by specified frequency."""
    df = df.copy()
    df = df.set_index(time_col)
    
    # Map frequency to pandas resample rule
    freq_map = {
        'hourly': 'H',
        'daily': 'D',
        'weekly': 'W',
        'monthly': 'M'
    }
    
    freq_rule = freq_map.get(frequency, 'D')
    
    # Aggregate
    if agg_func == 'mean':
        aggregated = df[value_cols].resample(freq_rule).mean()
    elif agg_func == 'sum':
        aggregated = df[value_cols].resample(freq_rule).sum()
    elif agg_func == 'min':
        aggregated = df[value_cols].resample(freq_rule).min()
    elif agg_func == 'max':
        aggregated = df[value_cols].resample(freq_rule).max()
    elif agg_func == 'median':
        aggregated = df[value_cols].resample(freq_rule).median()
    else:
        aggregated = df[value_cols].resample(freq_rule).mean()
    
    aggregated = aggregated.reset_index()
    
    return aggregated
