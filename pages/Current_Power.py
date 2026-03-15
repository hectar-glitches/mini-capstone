import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
from src.data_loader import get_shared_data, load_data, set_shared_data

st.set_page_config(page_title=" Current Power Mix", layout="wide")

# Smooth auto-refresh every 60 seconds without jarring page blank
# This triggers a rerun and clears the data cache to fetch fresh data from TEPCO
refresh_count = st_autorefresh(interval=60000, key="datarefresh")

# Clear cached data on each refresh to fetch latest from TEPCO
if refresh_count and refresh_count > 0:
    load_data.clear()
    if 'shared_df' in st.session_state:
        del st.session_state['shared_df']

# Custom CSS for better styling
st.markdown("""
<style>
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.8; }
    }
    
    @keyframes glow {
        0%, 100% { text-shadow: 0 0 20px rgba(34, 197, 94, 0.3); }
        50% { text-shadow: 0 0 30px rgba(34, 197, 94, 0.5), 0 0 40px rgba(34, 197, 94, 0.3); }
    }
    
    .time-display {
        text-align: center;
        padding: 1rem 0;
        animation: fadeIn 0.8s ease-out;
    }
    
    .time-number {
        font-size: 2.5rem;
        font-weight: 600;
        color: #e0e0e0;
        letter-spacing: 0.1em;
        margin: 0;
    }
    
    .time-date {
        font-size: 0.9rem;
        color: #888;
        margin-top: 0.25rem;
        letter-spacing: 0.05em;
    }
    
    .hero-metric {
        text-align: center;
        padding: 2rem 1rem;
        animation: fadeIn 1s ease-out;
    }
    
    .hero-number {
        font-size: 6rem;
        font-weight: 700;
        line-height: 1;
        color: #22c55e;
        margin: 0;
        animation: glow 3s ease-in-out infinite;
        display: inline-block;
    }
    
    .hero-label {
        font-size: 1.4rem;
        color: #d0d0d0;
        margin-top: 1.25rem;
        font-weight: 500;
        letter-spacing: 0.02em;
        display: block;
        text-align: center;
    }
    
    .renewable-icon {
        font-size: 3rem;
        animation: pulse 2s ease-in-out infinite;
        display: inline-block;
        margin-bottom: 0.5rem;
    }
    
    .insight-box {
        background: transparent;
        border-left: 3px solid #3b82f6;
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
    }
    
    .action-box {
        background: transparent;
        border-left: 3px solid #22c55e;
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

st.title(" Tokyo's Energy Mix")

# Display the timestamp - clean and minimal
actual_time_now = pd.Timestamp.now()
time_display = actual_time_now.strftime('%H:%M')
date_display = actual_time_now.strftime('%B %d, %Y')

st.markdown(f"""
<div class="time-display">
    <div class="time-number">{time_display}</div>
    <div class="time-date">{date_display} JST</div>
</div>
""", unsafe_allow_html=True)

st.caption("Data source: TEPCO Power Grid")

# Load data
df = get_shared_data()
if df is None:
    df = load_data()
    set_shared_data()

if df is None:
    st.error("Unable to load data. Please fetch data from the Overview page.")
    st.stop()

# Get "current" time data - use the most recent data available
# TEPCO publishes data every 30 minutes, so we'll show the latest available reading
now = pd.Timestamp.now()

# Get the most recent data point from the CSV
# This will be the latest 30-minute interval that TEPCO has published
latest_data = df.iloc[-1]
data_date = latest_data.get('date')
data_time = latest_data.get('time', '')

# Create datetime for latest data point
if data_date is not None and data_time:
    latest_datetime = pd.to_datetime(f"{data_date} {data_time}", errors='coerce')
else:
    latest_datetime = data_date

# Define power source categories
renewable_sources = {
    'hydro_mw': ' Hydro',
    'solar_actual_mw': ' Solar',
    'wind_actual_mw': ' Wind',
    'geothermal_mw': ' Geothermal',
    'biomass_mw': ' Biomass'
}

fossil_sources = {
    'thermal_lng_mw': ' LNG',
    'thermal_coal_mw': ' Coal',
    'thermal_oil_mw': ' Oil',
    'thermal_other_mw': ' Other Thermal'
}

other_sources = {
    'nuclear_mw': ' Nuclear',
    'pumped_hydro_mw': ' Pumped Hydro',
    'battery_mw': ' Battery',
    'interconnector_mw': ' Grid Connection'
}

# Calculate totals
renewable_total = sum([latest_data.get(src, 0) for src in renewable_sources.keys()])
fossil_total = sum([latest_data.get(src, 0) for src in fossil_sources.keys()])
other_total = sum([latest_data.get(src, 0) for src in other_sources.keys()])
total_generation = renewable_total + fossil_total + other_total

# Calculate percentages
renewable_pct = (renewable_total / total_generation * 100) if total_generation > 0 else 0
fossil_pct = (fossil_total / total_generation * 100) if total_generation > 0 else 0
other_pct = (other_total / total_generation * 100) if total_generation > 0 else 0

# Calculate average renewable percentage across all data
df_copy = df.copy()

# Create a proper datetime column combining date and time
if 'time' in df_copy.columns and 'date' in df_copy.columns:
    # Combine date and time into a single datetime column
    df_copy['datetime'] = pd.to_datetime(
        df_copy['date'].astype(str) + ' ' + df_copy['time'].astype(str),
        errors='coerce'
    )
else:
    # If no time column, use date as datetime
    df_copy['datetime'] = df_copy['date']

df_copy['renewable_total'] = df_copy[[col for col in renewable_sources.keys() if col in df_copy.columns]].sum(axis=1)
df_copy['total_gen'] = (
    df_copy['renewable_total'] + 
    df_copy[[col for col in fossil_sources.keys() if col in df_copy.columns]].sum(axis=1) +
    df_copy[[col for col in other_sources.keys() if col in df_copy.columns]].sum(axis=1)
)
df_copy['renewable_pct'] = (df_copy['renewable_total'] / df_copy['total_gen'] * 100).fillna(0)
average_renewable_pct = df_copy['renewable_pct'].mean()

# Calculate carbon intensity for current and average
coal_mw = latest_data.get('thermal_coal_mw', 0)
lng_mw = latest_data.get('thermal_lng_mw', 0)
oil_mw = latest_data.get('thermal_oil_mw', 0)
carbon_intensity = ((coal_mw * 900) + (lng_mw * 450) + (oil_mw * 650)) / total_generation if total_generation > 0 else 0

# Calculate carbon intensity for all rows in the dataframe
df_copy['coal_emissions'] = df_copy['thermal_coal_mw'].fillna(0) * 900
df_copy['lng_emissions'] = df_copy['thermal_lng_mw'].fillna(0) * 450
df_copy['oil_emissions'] = df_copy['thermal_oil_mw'].fillna(0) * 650
df_copy['total_emissions'] = df_copy['coal_emissions'] + df_copy['lng_emissions'] + df_copy['oil_emissions']
df_copy['carbon_intensity'] = (df_copy['total_emissions'] / df_copy['total_gen']).fillna(0)
avg_carbon_intensity = df_copy['carbon_intensity'].mean()
carbon_diff = carbon_intensity - avg_carbon_intensity

# Calculate difference from average
diff_from_avg = renewable_pct - average_renewable_pct

# Big renewable percentage display
st.markdown("---")

# Big renewable percentage display
col_left, col_center, col_right = st.columns([1, 2, 1])
with col_center:
    # Simple display with CSS animations only (JavaScript doesn't work reliably in Streamlit)
    st.markdown(f"""
    <div class="hero-metric">
        <div class="renewable-icon">🌱</div>
        <div class="hero-number">{renewable_pct:.1f}%</div>
        <div class="hero-label">Renewable Energy Right Now</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Show when the data was actually published by TEPCO
    if data_date is not None and data_time:
        data_timestamp = f"{data_date.strftime('%Y-%m-%d')} {data_time}"
        st.caption(f" Showing latest TEPCO data from: {data_timestamp} (updates every 30 min)")
    else:
        st.caption("📊 Showing latest available data (TEPCO publishes every 30 minutes)")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Immediate action/interpretation - cleaner design without heavy color boxes
    if diff_from_avg > 2:
        st.markdown(f"""
        <div class="action-box">
            <div style="font-size: 0.9rem; color: #22c55e; font-weight: 600; margin-bottom: 0.5rem;">
                ✓ {abs(diff_from_avg):.1f}% above average ({average_renewable_pct:.1f}%)
            </div>
            <div style="color: #666; font-size: 0.95rem;">
                Grid is relatively cleaner right now. Good time for flexible electricity use (charging devices, running dishwasher, laundry).
            </div>
        </div>
        """, unsafe_allow_html=True)
    elif diff_from_avg < -2:
        st.markdown(f"""
        <div class="insight-box">
            <div style="font-size: 0.9rem; color: #3b82f6; font-weight: 600; margin-bottom: 0.5rem;">
                {abs(diff_from_avg):.1f}% below average ({average_renewable_pct:.1f}%)
            </div>
            <div style="color: #666; font-size: 0.95rem;">
                Grid is more carbon-intensive than usual. If possible, delay flexible electricity use to cleaner periods.
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="insight-box">
            <div style="font-size: 0.9rem; color: #888; font-weight: 600; margin-bottom: 0.5rem;">
                At average ({average_renewable_pct:.1f}%)
            </div>
            <div style="color: #666; font-size: 0.95rem;">
                Grid conditions are typical for this dataset. Check the pattern below for cleaner times today.
            </div>
        </div>
        """, unsafe_allow_html=True)

# Metrics table
st.markdown("---")
st.subheader("Detailed Metrics")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label=" Current Renewable", 
        value=f"{renewable_pct:.1f}%",
        delta=f"{diff_from_avg:+.1f}%",
        help="Percentage of generation from renewable sources (hydro, solar, wind, geothermal, biomass)"
    )
with col2:
    st.metric(
        label=" Today's Average", 
        value=f"{average_renewable_pct:.1f}%",
        help="Average renewable share across all available data"
    )
with col3:
    st.metric(
        label=" Current Carbon", 
        value=f"{carbon_intensity:.0f}g",
        delta=f"{carbon_diff:+.0f}g",
        delta_color="inverse",
        help="Average grid carbon intensity (gCO₂/kWh) based on generation mix"
    )

# Add assumptions expander
with st.expander(" Methodology & Assumptions"):
    st.markdown("""
    **What these numbers represent:**
    - **Renewable share:** Percentage of total generation from hydro, solar, wind, geothermal, and biomass
    - **Grid carbon intensity:** Average emissions per kWh based on generation mix only
    
    **Key assumptions:**
    - Carbon intensity uses standard emissions factors: Coal ~900g CO₂/kWh, LNG ~450g CO₂/kWh, Oil ~650g CO₂/kWh
    - Grid imports (interconnector/連系線) are included in total supply but not assigned specific carbon intensity
    - Pumped hydro (揚水) and battery (蓄電池) storage are treated separately from primary generation
    - Solar and wind curtailment columns are excluded from calculations
    - **Important:** This shows average mix-based intensity, not marginal impact. Your additional electricity use may have different emissions depending on which generator responds to demand changes.
    
    **Data quality:**
    - Values are estimates based on generation mix and standard emissions factors
    - Actual carbon intensity varies based on plant efficiency, fuel quality, and operational conditions
    - Update cadence: 30-minute intervals from TEPCO
    """)

st.caption(" **Note:** This shows average mix-based intensity, not marginal impact of additional consumption.")

# Power Source Breakdown
st.markdown("---")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(" Source Mix")
    
    # Calculate non-renewable (fossil + nuclear)
    non_renewable_total = fossil_total + other_total

    # Create simplified pie chart
    fig = go.Figure(data=[go.Pie(
        labels=[' Renewable', ' Non-Renewable'],
        values=[renewable_total, non_renewable_total],
        hole=0.4,
        marker=dict(
            colors=['#22c55e', '#ef4444'],
            line=dict(color='white', width=3)
        ),
        textinfo='label+percent',
        textfont=dict(size=16, color='white'),
        textposition='inside'
    )])
    
    fig.update_layout(
        height=300,
        showlegend=False,
        margin=dict(l=10, r=10, t=10, b=10)
    )
    
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader(" Details")
    st.caption("Sources >1%")
    
    # Show only major sources (>1%)
    all_sources = []
    for src, label in renewable_sources.items():
        value = latest_data.get(src, 0)
        if value > 0:
            pct = (value / total_generation * 100) if total_generation > 0 else 0
            all_sources.append({'Source': label, '%': pct})
    
    for src, label in fossil_sources.items():
        value = latest_data.get(src, 0)
        if value > 0:
            pct = (value / total_generation * 100) if total_generation > 0 else 0
            all_sources.append({'Source': label, '%': pct})
    
    nuclear_val = latest_data.get('nuclear_mw', 0)
    if nuclear_val > 0:
        pct = (nuclear_val / total_generation * 100) if total_generation > 0 else 0
        all_sources.append({'Source': ' Nuclear', '%': pct})
    
    # Sort by percentage and show only >1%
    all_sources_df = pd.DataFrame(all_sources)
    major_sources = all_sources_df[all_sources_df['%'] > 1.0].sort_values('%', ascending=False)
    major_sources['%'] = major_sources['%'].apply(lambda x: f"{x:.1f}")
    
    if len(major_sources) > 0:
        st.dataframe(major_sources, use_container_width=True, hide_index=True, height=250)

# Today's pattern section
st.markdown("---")
st.subheader(" Today's Pattern")
st.caption("Carbon intensity over the past 24 hours • Red dot shows current time")

# Get today's data (last 24 hours)
recent_df = df_copy.tail(48).copy()  # Get more data to ensure we have full 24h (48 × 30min intervals)

# Create timeline chart with current time marked
fig_timeline = go.Figure()

# Add carbon intensity line
fig_timeline.add_trace(go.Scatter(
    x=recent_df['datetime'],
    y=recent_df['carbon_intensity'],
    name='Carbon Intensity',
    line=dict(color='#3b82f6', width=2),
    fill='tozeroy',
    fillcolor='rgba(59, 130, 246, 0.1)'
))

# Add average line
fig_timeline.add_hline(
    y=avg_carbon_intensity, 
    line_dash="dash", 
    line_color="#666",
    annotation_text=f"Avg: {avg_carbon_intensity:.0f}g",
    annotation_position="right"
)

# Mark current time
current_carbon = carbon_intensity
fig_timeline.add_trace(go.Scatter(
    x=[latest_datetime],
    y=[current_carbon],
    mode='markers',
    marker=dict(size=12, color='#ef4444', symbol='circle'),
    name='Current',
    showlegend=False
))

fig_timeline.update_layout(
    xaxis_title="Time",
    yaxis_title="Carbon Intensity (gCO₂/kWh)",
    height=280,
    hovermode='x unified',
    margin=dict(l=20, r=20, t=10, b=40),
    showlegend=False
)

st.plotly_chart(fig_timeline, use_container_width=True)

# Data insights expander
with st.expander(" Data Details & What to Expect"):
    st.write("**About the Pattern:**")
    st.write("Typically, you'd see:")
    st.write("- **Lower carbon intensity during daylight** (solar generation)")
    st.write("- **Higher values at night** (no solar, more fossil fuels)")
    st.write("- **Variation throughout the day** as grid conditions change")
    st.write("")
    st.write("If the line is relatively flat, it indicates:")
    st.write("- Stable fossil fuel generation with minimal renewable contribution")
    st.write("- Consistent grid conditions (no major generation shifts)")
    st.write("")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Data Points", f"{len(df)} readings")
        st.metric("Time Coverage", f"{df['date'].min().strftime('%b %d')} - {df['date'].max().strftime('%b %d')}")
    with col2:
        carbon_min = df_copy['carbon_intensity'].min()
        carbon_max = df_copy['carbon_intensity'].max()
        carbon_variation = carbon_max - carbon_min
        st.metric("Carbon Intensity Range", f"{carbon_min:.0f} - {carbon_max:.0f} gCO₂/kWh", 
                 delta=f"{carbon_variation:.0f}g variation")
        
        renewable_min = df_copy['renewable_pct'].min()
        renewable_max = df_copy['renewable_pct'].max()
        st.metric("Renewable % Range", f"{renewable_min:.1f}% - {renewable_max:.1f}%")

# Footer
st.markdown("---")
st.caption(" Data: TEPCO Power Grid area supply–demand actuals (published every 30 minutes) | Carbon intensity uses standard emissions factors; values are estimates | Page checks for updates every 60 seconds")
