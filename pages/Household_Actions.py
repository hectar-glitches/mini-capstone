import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.data_loader import get_shared_data, load_data, set_shared_data
from src.household_profiles import (
    HOUSEHOLDS,
    list_households,
    get_household,
    compute_carbon_intensity_series,
    get_hourly_carbon_profile,
    find_best_windows,
    find_worst_windows,
    calculate_action_impact,
)

st.set_page_config(
    page_title="Household Actions",
    layout="wide",
    page_icon="🏠",
)

# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    .section-header {
        font-size: 1.1rem;
        font-weight: 600;
        color: #d0d0d0;
        margin-bottom: 0.5rem;
        letter-spacing: 0.02em;
    }
    .appliance-card {
        border-left: 3px solid #3b82f6;
        padding: 0.6rem 1rem;
        margin: 0.4rem 0;
    }
    .appliance-card.shiftable {
        border-left-color: #22c55e;
    }
    .window-best {
        border-left: 3px solid #22c55e;
        padding: 0.5rem 1rem;
        margin: 0.3rem 0;
    }
    .window-worst {
        border-left: 3px solid #ef4444;
        padding: 0.5rem 1rem;
        margin: 0.3rem 0;
    }
    .impact-box {
        border-left: 3px solid #f59e0b;
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
    }
    .incentive-bar-bg {
        background: #1e293b;
        border-radius: 4px;
        height: 12px;
        width: 100%;
        margin: 6px 0 2px 0;
    }
    .incentive-bar-fill {
        background: #22c55e;
        border-radius: 4px;
        height: 12px;
    }
    .disclaimer {
        font-size: 0.78rem;
        color: #666;
        font-style: italic;
        margin-top: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
df = get_shared_data()
if df is None:
    df = load_data()
    if df is not None:
        set_shared_data()

# ---------------------------------------------------------------------------
# Sidebar — household selector
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("Household Profile")
    st.caption("Select the modeled household archetype that best matches your situation.")

    household_options = list_households()
    hh_labels = [label for _, label in household_options]
    hh_keys = [key for key, _ in household_options]

    selected_idx = st.radio(
        "Household type",
        options=range(len(hh_labels)),
        format_func=lambda i: hh_labels[i],
        index=0,
    )
    selected_key = hh_keys[selected_idx]
    hh = get_household(selected_key)

    st.markdown("---")
    st.caption(hh["census_note"])

    st.markdown("---")
    st.header("Appliance Action")
    shiftable_appliances = [a for a in hh["appliances"] if a["category"] == "shiftable"]
    selected_appliance_name = st.selectbox(
        "Which appliance are you planning to run?",
        options=[a["name"] for a in shiftable_appliances],
        help="Only shiftable appliances are shown — fixed loads cannot be scheduled differently.",
    )
    selected_appliance = next(
        a for a in shiftable_appliances if a["name"] == selected_appliance_name
    )

# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------
st.title(f"{hh['icon']} Household Actions")
st.markdown(
    f"**{hh['label']}** · {hh['sublabel']}"
)
st.markdown(hh["description"])
st.markdown("---")

# ---------------------------------------------------------------------------
# Data gate — require data to be loaded
# ---------------------------------------------------------------------------
if df is None:
    st.warning(
        "No TEPCO data loaded. Please go to the **Overview** page and fetch TEPCO data first, "
        "then return here."
    )
    st.stop()

# ---------------------------------------------------------------------------
# Compute carbon intensity profile and current intensity
# ---------------------------------------------------------------------------
profile = get_hourly_carbon_profile(df)

latest_data = df.iloc[-1]
total_gen_cols = [
    "nuclear_mw", "thermal_lng_mw", "thermal_coal_mw", "thermal_oil_mw",
    "thermal_other_mw", "hydro_mw", "geothermal_mw", "biomass_mw",
    "solar_actual_mw", "wind_actual_mw", "pumped_hydro_mw",
    "battery_mw", "interconnector_mw", "other_mw",
]
total_gen_now = sum(
    float(latest_data.get(c, 0) or 0) for c in total_gen_cols if c in df.columns
)
coal_now = float(latest_data.get("thermal_coal_mw", 0) or 0)
lng_now = float(latest_data.get("thermal_lng_mw", 0) or 0)
oil_now = float(latest_data.get("thermal_oil_mw", 0) or 0)
current_intensity = (
    (coal_now * 900 + lng_now * 450 + oil_now * 650) / total_gen_now
    if total_gen_now > 0
    else 0.0
)

best_windows = find_best_windows(profile, n=3)
worst_windows = find_worst_windows(profile, n=3)
best_intensity = best_windows[0]["carbon_intensity_mean"] if best_windows else current_intensity

# ---------------------------------------------------------------------------
# Section 1 — 24-hour carbon intensity chart with best/worst bands
# ---------------------------------------------------------------------------
st.subheader("📊 24-Hour Carbon Intensity Pattern")
st.caption(
    "Based on TEPCO historical generation mix data. "
    "Green bands = lower-carbon periods (better for flexible loads). "
    "Red bands = higher-carbon periods (avoid if possible)."
)

if not profile.empty:
    fig = go.Figure()

    # Shaded best windows
    for w in best_windows:
        h = w["hour"]
        fig.add_vrect(
            x0=h - 0.5,
            x1=h + 0.5,
            fillcolor="rgba(34,197,94,0.12)",
            line_width=0,
            layer="below",
        )

    # Shaded worst windows
    for w in worst_windows:
        h = w["hour"]
        fig.add_vrect(
            x0=h - 0.5,
            x1=h + 0.5,
            fillcolor="rgba(239,68,68,0.10)",
            line_width=0,
            layer="below",
        )

    # Mean intensity line
    fig.add_trace(
        go.Scatter(
            x=profile["hour"],
            y=profile["carbon_intensity_mean"],
            mode="lines+markers",
            name="Avg gCO₂/kWh",
            line=dict(color="#60a5fa", width=2.5),
            marker=dict(size=5),
            hovertemplate="Hour %{x}:00 — %{y:.0f} gCO₂/kWh<extra></extra>",
        )
    )

    # Range band (min–max)
    fig.add_trace(
        go.Scatter(
            x=pd.concat([profile["hour"], profile["hour"].iloc[::-1]]),
            y=pd.concat(
                [profile["carbon_intensity_max"], profile["carbon_intensity_min"].iloc[::-1]]
            ),
            fill="toself",
            fillcolor="rgba(96,165,250,0.08)",
            line=dict(width=0),
            name="Min–Max range",
            hoverinfo="skip",
        )
    )

    # Current hour marker
    now_hour = pd.Timestamp.now().hour
    now_intensity_row = profile[profile["hour"] == now_hour]
    if not now_intensity_row.empty:
        fig.add_vline(
            x=now_hour,
            line_dash="dot",
            line_color="#f59e0b",
            annotation_text="Now",
            annotation_position="top",
            annotation_font_color="#f59e0b",
        )

    fig.update_layout(
        xaxis=dict(
            title="Hour of Day",
            tickmode="linear",
            tick0=0,
            dtick=2,
            tickformat="%02d:00",
            range=[-0.5, 23.5],
        ),
        yaxis=dict(title="Carbon Intensity (gCO₂/kWh)"),
        template="plotly_dark",
        height=340,
        margin=dict(t=20, b=40),
        showlegend=True,
        legend=dict(orientation="h", y=-0.25),
        hovermode="x unified",
    )

    st.plotly_chart(fig, use_container_width=True)

    # Best / worst window callouts
    col_best, col_worst = st.columns(2)
    with col_best:
        st.markdown('<div class="section-header">✅ Best windows to run flexible loads</div>', unsafe_allow_html=True)
        for w in best_windows:
            st.markdown(
                f'<div class="window-best">'
                f'<strong>{w["label"]}</strong> — '
                f'{w["carbon_intensity_mean"]:.0f} gCO₂/kWh'
                f'</div>',
                unsafe_allow_html=True,
            )
    with col_worst:
        st.markdown('<div class="section-header">⚠️ Avoid running heavy loads</div>', unsafe_allow_html=True)
        for w in worst_windows:
            st.markdown(
                f'<div class="window-worst">'
                f'<strong>{w["label"]}</strong> — '
                f'{w["carbon_intensity_mean"]:.0f} gCO₂/kWh'
                f'</div>',
                unsafe_allow_html=True,
            )
else:
    st.info("Carbon intensity profile requires TEPCO generation mix columns (thermal_coal_mw, thermal_lng_mw, etc.).")

st.markdown("---")

# ---------------------------------------------------------------------------
# Section 2 — Household load profile (fixed vs shiftable)
# ---------------------------------------------------------------------------
st.subheader(f"{hh['icon']} {hh['label']} — Appliance Load Profile")

daily_kwh_mid = sum(hh["daily_kwh_range"]) / 2
shiftable_kwh = daily_kwh_mid * hh["shiftable_pct"]
fixed_kwh = daily_kwh_mid - shiftable_kwh

col_a, col_b, col_c = st.columns(3)
with col_a:
    st.metric(
        "Typical Daily Use",
        f"{hh['daily_kwh_range'][0]}–{hh['daily_kwh_range'][1]} kWh",
        help="Modeled estimate based on dwelling type and family structure",
    )
with col_b:
    st.metric(
        "Shiftable Load",
        f"{hh['shiftable_pct']*100:.0f}%",
        f"~{shiftable_kwh:.1f} kWh/day",
        help="Proportion of daily consumption that can be time-shifted",
    )
with col_c:
    st.metric(
        "Fixed Load",
        f"{(1-hh['shiftable_pct'])*100:.0f}%",
        f"~{fixed_kwh:.1f} kWh/day",
        delta_color="off",
        help="Loads tied to occupancy or continuous operation",
    )

st.markdown("")

col_fixed, col_shift = st.columns(2)

with col_fixed:
    st.markdown('<div class="section-header">🔒 Fixed loads (not shiftable)</div>', unsafe_allow_html=True)
    for app in hh["appliances"]:
        if app["category"] == "fixed":
            st.markdown(
                f'<div class="appliance-card">'
                f'{app["icon"]} <strong>{app["name"]}</strong> — '
                f'{app["kwh"]} kWh/run &nbsp;·&nbsp; '
                f'<span style="color:#888;font-size:0.85rem;">{app["note"]}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

with col_shift:
    st.markdown('<div class="section-header">⏱️ Shiftable loads (timing-flexible)</div>', unsafe_allow_html=True)
    for app in hh["appliances"]:
        if app["category"] == "shiftable":
            st.markdown(
                f'<div class="appliance-card shiftable">'
                f'{app["icon"]} <strong>{app["name"]}</strong> — '
                f'{app["kwh"]} kWh/run &nbsp;·&nbsp; '
                f'<span style="color:#888;font-size:0.85rem;">{app["note"]}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

with st.expander("ℹ️ Data transparency — how these values are derived"):
    st.markdown("""
    **Appliance consumption values** are typical estimates derived from Japanese energy label standards
    and dwelling characteristics. They are **not** measured from actual households.

    **Household profiles** are census-justified archetypes, not claims about individual residents.
    Sources: 2020 Population Census (Tables 6-4, 8-1), Tokyo Statistical Yearbook.

    **Shiftable percentage** reflects schedule flexibility based on household structure and occupancy
    patterns, not monitored load disaggregation.
    """)

st.markdown("---")

# ---------------------------------------------------------------------------
# Section 3 — Action comparison calculator
# ---------------------------------------------------------------------------
st.subheader("⚡ Action Comparison: Now vs. Optimal Window")

app = selected_appliance
impact = calculate_action_impact(app, current_intensity, best_intensity)

col_now, col_arrow, col_best_col = st.columns([2, 1, 2])

with col_now:
    st.markdown(f"### {app['icon']} Run **now**")
    st.metric("Carbon intensity", f"{current_intensity:.0f} gCO₂/kWh")
    st.metric("CO₂ this run", f"{impact['co2_now_g']:.0f} g")
    st.markdown(f"*{app['kwh']} kWh × {current_intensity:.0f} g/kWh*")

with col_arrow:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("### →")

with col_best_col:
    if best_windows:
        bw = best_windows[0]
        st.markdown(f"### ✅ Shift to **{bw['label']}**")
        st.metric("Carbon intensity", f"{best_intensity:.0f} gCO₂/kWh")
        st.metric(
            "CO₂ this run",
            f"{impact['co2_best_g']:.0f} g",
            delta=f"−{impact['co2_saved_g']:.0f} g saved",
            delta_color="inverse",
        )
        st.markdown(f"*{app['kwh']} kWh × {best_intensity:.0f} g/kWh*")
    else:
        st.info("No best window data available.")

if impact["co2_saved_g"] > 0:
    st.markdown(
        f'<div class="impact-box">'
        f'<strong>Shifting {app["name"]} saves ~{impact["co2_saved_g"]:.0f} g CO₂ this run</strong> '
        f'({impact["pct_improvement"]:.1f}% reduction). '
        f'Over 30 runs that is ~{impact["co2_saved_g"] * 30 / 1000:.2f} kg CO₂.'
        f'</div>',
        unsafe_allow_html=True,
    )
elif current_intensity <= best_intensity:
    st.markdown(
        '<div class="impact-box">'
        'The grid is already at or near its cleanest for the day — '
        'now is a good time to run this appliance.'
        '</div>',
        unsafe_allow_html=True,
    )

st.caption(
    "CO₂ savings are based on average mix-based intensity (gCO₂/kWh) from TEPCO historical data. "
    "Actual marginal emissions may differ depending on which generator responds to demand shifts."
)

st.markdown("---")

# ---------------------------------------------------------------------------
# Section 4 — Illustrative incentive display (design reference)
# ---------------------------------------------------------------------------
st.subheader("🏅 Illustrative Incentive Framework")
st.caption(
    "The display below models behavioral design patterns observed in Japanese utility "
    "demand-response programs (TEPCO 節電チャレンジ, SoftBank Eco-Denki, Octopus Energy Japan). "
    "This is a **design reference prototype** — no actual points or rewards are issued."
)

# Simulate a session-persistent action log
if "action_log" not in st.session_state:
    st.session_state["action_log"] = []  # list of co2_saved_g per logged action

col_log, col_progress = st.columns([1, 2])

with col_log:
    st.markdown("**Log a shift action**")
    if st.button(f"✅ Log: shifted {app['icon']} {app['name']}"):
        st.session_state["action_log"].append(
            max(impact["co2_saved_g"], 0)
        )
        st.success(f"Logged! +{max(impact['co2_saved_g'], 0):.0f} g CO₂ saved.")
    if st.button("🗑️ Reset log"):
        st.session_state["action_log"] = []

with col_progress:
    total_saved_g = sum(st.session_state["action_log"])
    actions_count = len(st.session_state["action_log"])

    # Challenge goal: 500 g CO₂ saved = illustrative program threshold
    CHALLENGE_GOAL_G = 500.0
    progress_pct = min(total_saved_g / CHALLENGE_GOAL_G * 100, 100)
    bar_width = int(progress_pct)

    st.markdown("**節電チャレンジ — Power-Saving Challenge (illustrative)**")
    st.markdown(
        f'<div class="incentive-bar-bg">'
        f'<div class="incentive-bar-fill" style="width:{bar_width}%;"></div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f"**{total_saved_g:.0f} / {CHALLENGE_GOAL_G:.0f} g CO₂** saved this session "
        f"({progress_pct:.0f}%) — {actions_count} action{'s' if actions_count != 1 else ''} logged"
    )

    if progress_pct >= 100:
        st.success(
            "🎉 Challenge goal reached! In a real TEPCO DR program this milestone "
            "would be exchangeable for retailer vouchers or points."
        )
    elif progress_pct >= 50:
        st.info(f"Halfway there — {CHALLENGE_GOAL_G - total_saved_g:.0f} g more to go.")

    st.markdown(
        '<p class="disclaimer">'
        "Design reference: TEPCO 節電チャレンジ (2022); SoftBank Eco-Denki app; "
        "Octopus Energy Japan 節電チャレンジ. No actual rewards are implemented."
        "</p>",
        unsafe_allow_html=True,
    )

st.markdown("---")

# ---------------------------------------------------------------------------
# Footer methodology note
# ---------------------------------------------------------------------------
with st.expander("📋 Methodology & Academic Framing"):
    st.markdown(f"""
    **Profile used:** {hh['label']} (modeled household archetype)

    **Census justification:** {hh['census_note']}

    **Consumption values:** Typical estimates from Japanese energy label standards and dwelling
    characteristics. Not individual household measurements.

    **Carbon intensity method:** Average mix-based intensity (gCO₂/kWh) computed from TEPCO
    generation mix data using standard emissions factors:
    Coal 900 g/kWh · LNG 450 g/kWh · Oil 650 g/kWh.
    This is average intensity, not marginal emissions from demand changes.

    **Timing windows:** Identified from hourly aggregates across the full TEPCO dataset loaded
    in this session. Best windows are the three lowest-intensity hours on average.

    **Incentive display:** Design reference prototype modelling real Japanese utility DR programs.
    No actual point redemption or distribution is implemented.

    **Scoping boundary:** This dashboard provides timing-based guidance using real TEPCO data
    and modeled household profiles. It does not perform smart meter integration,
    appliance-level monitoring, or load disaggregation.
    """)
