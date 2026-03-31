# Data Analyzer Dashboard

A comprehensive, multi-page Streamlit dashboard for exploring, analyzing, and visualizing CSV data. Built with extensibility in mind for domain-specific adaptations (e.g., TEPCO electricity data).

## Features

### Home Page
- **File Upload**: Drag-and-drop CSV upload with automatic caching
- **Quick Overview**: Instant data preview and column information
- **Quick Visualization**: Interactive scatter plots or histograms
- **Data Info**: Row counts, column types, memory usage

### Overview Page
- **Comprehensive Statistics**: Mean, median, std, skewness, kurtosis, and more
- **Distribution Analysis**: Histograms, box plots, violin plots
- **Correlation Analysis**: Interactive heatmaps for numeric columns
- **Data Quality Reports**: Missing value analysis and duplicate detection
- **Customizable Filtering**: Select columns and row ranges
- **Export Capability**: Download filtered data as CSV

### Time Series Analysis Page
- **Automatic DateTime Detection**: Smart column identification
- **Interactive Time-Series Plots**: Zoom, pan, and range selection
- **Pattern Analysis**: Hourly, daily, weekly, monthly, and seasonal patterns
- **Date Range Filtering**: Focus on specific time periods
- **Flexible Aggregation**: Aggregate by hour/day/week/month with multiple functions (mean, sum, min, max, median)
- **Multi-Series Support**: Plot and compare multiple variables simultaneously

## Structure

```
mini-capstone/
├── app.py                      # Home page with upload and quick preview
├── pages/
│   ├── 1_📊_Overview.py        # Comprehensive data analysis
│   └── 2_📈_Time_Series.py     # Time-series specific analysis
├── src/
│   ├── __init__.py
│   ├── data_loader.py          # Data loading with datetime detection
│   ├── analyzer.py             # Statistical analysis and pattern detection
│   └── visualizations.py       # All chart creation functions
├── requirements.txt
└── README.md
```

## Installation

1. Clone or download this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Run the Dashboard

```bash
streamlit run app.py
```

The dashboard will open in your default browser at `http://localhost:8501`

### Basic Workflow

1. **Upload Data**: Use the sidebar to upload your CSV file
2. **Home Page**: Get a quick overview and preview
3. **Navigate**:
   - Go to ** Overview** for detailed statistics and distributions
   - Go to ** Time Series** for temporal pattern analysis (if data contains dates)

## Example Use Cases

### Generic Data Analysis
- Upload any CSV dataset
- Explore distributions and correlations
- Identify data quality issues
- Export filtered subsets

### Time-Series Data
- Upload data with timestamp columns
- Analyze patterns by hour, day of week, month, or season
- Compare multiple metrics over time
- Filter and aggregate for specific periods

### Domain-Specific Adaptation (e.g., TEPCO Electricity)
This dashboard is designed to be easily adapted for specific use cases:

1. **Modify `data_loader.py`**: Add domain-specific data sources
2. **Customize `analyzer.py`**: Add specialized metrics (e.g., carbon intensity)
3. **Extend visualization**: Create domain-specific charts
4. **Add pages**: Create new pages for specific analyses

## Technical Details

### Key Technologies
- **Streamlit**: Multi-page app framework
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive visualizations
- **NumPy**: Numerical computations

### Performance Features
- `@st.cache_data` for efficient data loading
- Session state for multi-page data sharing
- Optimized visualizations for large datasets

### Extensibility
- Modular architecture for easy customization
- Separate concerns: data loading, analysis, visualization
- Template structure ready for domain-specific adaptation

## Future Enhancements

### Potential Extensions for Domain-Specific Use
- API integration for live data (e.g., TEPCO API)
- Custom metrics and KPIs
- Uncertainty visualization for estimated values
- Comparative analysis across multiple time periods
- Machine learning forecasting
- Advanced filtering and querying

## Customization Guide

### Adding a New Page

1. Create a new file in `pages/` directory: `3_YourPage.py`
2. Use session state to access shared data:
```python
from src.data_loader import get_shared_data
df = get_shared_data()
```

### Adding New Analysis Functions

1. Add function to `src/analyzer.py`
2. Import and use in your pages

### Creating Custom Visualizations

1. Add visualization function to `src/visualizations.py`
2. Use Plotly for interactive charts

## License

This project is open for educational and research purposes.

## Contributing

Feel free to fork, modify, and adapt this dashboard for your specific needs!
