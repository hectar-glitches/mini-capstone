import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.data_loader import get_shared_data, load_data, set_shared_data
from src.household_profiles import (
    list_households,
    get_household,
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

st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
    /* Inter across the whole page */
    html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
    /* Tighten default Streamlit padding so everything fits without scrolling */
    .block-container { padding-top: 1rem !important; padding-bottom: 0.5rem !important; }
    div[data-testid="stVerticalBlock"] > div { gap: 0.3rem !important; }

    .ward-pill {
        display: inline-block;
        padding: 0.2rem 0.75rem;
        border-radius: 999px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 0.4rem;
        cursor: pointer;
    }
    .window-pill {
        display: inline-block;
        padding: 0.15rem 0.6rem;
        border-radius: 4px;
        font-size: 0.78rem;
        margin: 0.1rem 0.1rem;
    }
    .window-best  { background: rgba(34,197,94,0.15);  color: #22c55e; }
    .window-worst { background: rgba(239,68,68,0.12);  color: #ef4444; }
    .impact-box {
        border-left: 3px solid #f59e0b;
        padding: 0.5rem 0.75rem;
        margin: 0.3rem 0;
        font-size: 0.88rem;
    }
    .incentive-bar-bg {
        background: #1e293b;
        border-radius: 4px;
        height: 10px;
        width: 100%;
        margin: 4px 0 2px 0;
    }
    .incentive-bar-fill {
        background: #22c55e;
        border-radius: 4px;
        height: 10px;
    }
    .fine-print { font-size: 0.72rem; color: #555; margin-top: 0.2rem; }
    h1 { font-size: 1.4rem !important; margin-bottom: 0 !important; }
    h3 { font-size: 1rem !important; margin-bottom: 0.2rem !important; }
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
# Sidebar — household + appliance selectors (compact)
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("**Where do you live?**")
    household_options = list_households()
    hh_keys   = [k for k, _ in household_options]
    hh_labels = [k.capitalize() for k, _ in household_options]

    selected_idx = st.radio(
        "Ward",
        options=range(len(hh_keys)),
        format_func=lambda i: hh_labels[i],
        index=0,
        label_visibility="collapsed",
    )
    selected_key = hh_keys[selected_idx]
    hh = get_household(selected_key)

    st.markdown("---")
    st.markdown("**Which appliance are you planning to use?**")
    shiftable_appliances = [a for a in hh["appliances"] if a["category"] == "shiftable"]
    selected_appliance_name = st.selectbox(
        "Appliance",
        options=[a["name"] for a in shiftable_appliances],
        label_visibility="collapsed",
    )
    selected_appliance = next(
        a for a in shiftable_appliances if a["name"] == selected_appliance_name
    )

# ---------------------------------------------------------------------------
# Data gate
# ---------------------------------------------------------------------------
if df is None:
    st.warning("Fetch TEPCO data from the Overview page first, then return here.")
    st.stop()

# ---------------------------------------------------------------------------
# Compute carbon profile + current intensity
# ---------------------------------------------------------------------------
profile = get_hourly_carbon_profile(df)

latest_data  = df.iloc[-1]
total_gen_cols = [
    "nuclear_mw", "thermal_lng_mw", "thermal_coal_mw", "thermal_oil_mw",
    "thermal_other_mw", "hydro_mw", "geothermal_mw", "biomass_mw",
    "solar_actual_mw", "wind_actual_mw", "pumped_hydro_mw",
    "battery_mw", "interconnector_mw", "other_mw",
]
total_gen_now = sum(float(latest_data.get(c, 0) or 0) for c in total_gen_cols if c in df.columns)
coal_now = float(latest_data.get("thermal_coal_mw", 0) or 0)
lng_now  = float(latest_data.get("thermal_lng_mw",  0) or 0)
oil_now  = float(latest_data.get("thermal_oil_mw",  0) or 0)
current_intensity = (
    (coal_now * 900 + lng_now * 450 + oil_now * 650) / total_gen_now
    if total_gen_now > 0 else 0.0
)

best_windows  = find_best_windows(profile,  n=3)
worst_windows = find_worst_windows(profile, n=3)
best_intensity = best_windows[0]["carbon_intensity_mean"] if best_windows else current_intensity

app    = selected_appliance
impact = calculate_action_impact(app, current_intensity, best_intensity)

# ---------------------------------------------------------------------------
# Page header — single compact line
# ---------------------------------------------------------------------------
now_hour = pd.Timestamp.now().hour
st.markdown(
    f"## {hh['icon']} {hh['label']} &nbsp;·&nbsp; "
    f"<span style='font-size:0.9rem;color:#888;font-weight:400'>"
    f"Grid now: <strong style='color:#60a5fa'>{current_intensity:.0f} gCO₂/kWh</strong> &nbsp;|&nbsp; "
    f"{pd.Timestamp.now().strftime('%H:%M')}</span>",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Two-column layout: chart left, action right
# ---------------------------------------------------------------------------
col_chart, col_action = st.columns([3, 2], gap="large")

with col_chart:
    st.markdown("**Carbon intensity today** — green = best windows · red = avoid")

    if not profile.empty:
        fig = go.Figure()

        best_hours  = {w["hour"] for w in best_windows}
        worst_hours = {w["hour"] for w in worst_windows}

        # Green zones (best windows) — clearly visible, soft glow feel
        for h in best_hours:
            fig.add_vrect(x0=h - 0.5, x1=h + 0.5,
                          fillcolor="rgba(22,163,74,0.28)",
                          line=dict(color="rgba(22,163,74,0.55)", width=1),
                          layer="below")

        # Red zones (worst windows)
        for h in worst_hours:
            fig.add_vrect(x0=h - 0.5, x1=h + 0.5,
                          fillcolor="rgba(185,28,28,0.25)",
                          line=dict(color="rgba(185,28,28,0.50)", width=1),
                          layer="below")

        # Clean white line — zones do the colour storytelling, line stays minimal
        fig.add_trace(go.Scatter(
            x=profile["hour"],
            y=profile["carbon_intensity_mean"],
            mode="lines",
            line=dict(color="rgba(255,255,255,0.90)", width=2.5,
                      shape="spline", smoothing=0.5),
            name="gCO₂/kWh",
            hovertemplate="%{x}:00 — %{y:.0f} gCO₂/kWh<extra></extra>",
        ))

        # Current hour marker
        fig.add_vline(x=now_hour, line_dash="dot", line_color="#f59e0b",
                      annotation_text="Now", annotation_position="top right",
                      annotation_font_color="#f59e0b", annotation_font_size=11)

        fig.update_layout(
            xaxis=dict(title=None, tickmode="linear", tick0=0, dtick=3,
                       tickformat="%02d:00", range=[-0.5, 23.5],
                       tickfont=dict(size=10)),
            yaxis=dict(title="gCO₂/kWh", tickfont=dict(size=10)),
            template="plotly_dark",
            height=220,
            margin=dict(t=8, b=28, l=48, r=8),
            showlegend=False,
            hovermode="x unified",
        )
        st.plotly_chart(fig, use_container_width=True)

        # Best / worst window pills — compact row
        best_pills  = " ".join(
            f'<span class="window-pill window-best">✓ {w["label"]}</span>'
            for w in best_windows)
        worst_pills = " ".join(
            f'<span class="window-pill window-worst">✗ {w["label"]}</span>'
            for w in worst_windows)
        st.markdown(
            f'<div style="line-height:2">{best_pills}&nbsp;&nbsp;{worst_pills}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.info("Fetching grid data… if this persists, check your connection.")

    # Appliance load summary
    st.markdown("&nbsp;")
    st.markdown("**Your appliances**")
    fixed_apps    = [a for a in hh["appliances"] if a["category"] == "fixed"]
    shiftable_all = [a for a in hh["appliances"] if a["category"] == "shiftable"]

    # Fixed loads → one compact muted line (no icons, just names)
    fixed_summary = " · ".join(a["name"] for a in fixed_apps)
    st.markdown(
        f'<p style="color:#4a5568;font-size:0.78rem;margin:0 0 8px 0;letter-spacing:0.01em">'
        f'Always on &nbsp;—&nbsp; {fixed_summary}</p>',
        unsafe_allow_html=True,
    )

    # Shiftable → spacious green pills, no icons
    pills = "".join(
        f'<span style="display:inline-block;margin:3px 4px 3px 0;padding:5px 12px;'
        f'background:rgba(34,197,94,0.10);border:1px solid rgba(34,197,94,0.30);'
        f'border-radius:5px;font-size:0.82rem;color:#4ade80;letter-spacing:0.01em">'
        f'{a["name"]} '
        f'<span style="color:#4a5568;font-size:0.75rem">{a["kwh"]} kWh</span></span>'
        for a in shiftable_all
    )
    st.markdown(
        f'<p style="color:#4ade80;font-size:0.75rem;font-weight:500;letter-spacing:0.06em;'
        f'text-transform:uppercase;margin:0 0 5px 0">Flexible</p>'
        f'<div style="line-height:1.2">{pills}</div>',
        unsafe_allow_html=True,
    )

with col_action:
    # --- Action comparison ---
    st.markdown(f"**{app['name']}** — timing impact")

    c_now, c_vs, c_best = st.columns([5, 1, 5])
    with c_now:
        st.metric(f"If you use it now", f"{impact['co2_now_g']:.0f} g CO₂",
                  help=f"{app['kwh']} kWh × {current_intensity:.0f} g/kWh (current grid mix)")
    with c_vs:
        st.markdown("<div style='text-align:center;padding-top:1.8rem;color:#555'>→</div>",
                    unsafe_allow_html=True)
    with c_best:
        if best_windows:
            bw = best_windows[0]
            st.metric(
                f"If you wait until {bw['label']}",
                f"{impact['co2_best_g']:.0f} g CO₂",
                delta=f"−{impact['co2_saved_g']:.0f} g" if impact['co2_saved_g'] > 0 else "Already the best time",
                delta_color="inverse",
                help=f"{app['kwh']} kWh × {best_intensity:.0f} g/kWh (cleaner grid window)",
            )

    if impact["co2_saved_g"] > 0:
        st.markdown(
            f'<div class="impact-box">'
            f'Waiting saves <strong>{impact["co2_saved_g"]:.0f} g CO₂</strong> '
            f'({impact["pct_improvement"]:.0f}% less per use). '
            f'Over 30 uses: ~<strong>{impact["co2_saved_g"]*30/1000:.2f} kg</strong> saved.'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="impact-box">The grid is at its cleanest right now — no need to wait.</div>',

            unsafe_allow_html=True,
        )

    st.markdown("---")

    # --- Incentive tracker ---
    st.markdown("**节電チャレンジ — Power-Saving Challenge**" if False else "**Power-Saving Challenge**")
    st.markdown(
        '<div style="font-size:0.8rem;color:#666;line-height:1.6;margin-bottom:8px">'
        'Each time you delay an appliance until a green window, tap <em>I shifted it</em> below. '
        'Reach <strong style="color:#ccc">500 g saved</strong> to complete the challenge.'
        '</div>',
        unsafe_allow_html=True,
    )

    if "action_log" not in st.session_state:
        st.session_state["action_log"] = []

    total_saved_g = sum(st.session_state["action_log"])
    actions_count = len(st.session_state["action_log"])
    CHALLENGE_GOAL_G = 500.0
    progress_pct = min(total_saved_g / CHALLENGE_GOAL_G * 100, 100)
    remaining_g = max(CHALLENGE_GOAL_G - total_saved_g, 0)

    # Progress bar + status line
    st.markdown(
        f'<div class="incentive-bar-bg">'
        f'<div class="incentive-bar-fill" style="width:{int(progress_pct)}%"></div>'
        f'</div>'
        f'<div style="font-size:0.78rem;color:#777;margin-top:3px">'
        f'{total_saved_g:.0f} g saved &nbsp;·&nbsp; {remaining_g:.0f} g to go &nbsp;·&nbsp; {actions_count} shifts'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    bc1, bc2 = st.columns([3, 1])
    with bc1:
        if st.button(f"I shifted it — {app['name']}", use_container_width=True):
            st.session_state["action_log"].append(max(impact["co2_saved_g"], 0))
            st.rerun()
    with bc2:
        if st.button("Reset", use_container_width=True):
            st.session_state["action_log"] = []
            st.rerun()

    if progress_pct >= 100:
        st.success("Challenge complete — 500 g saved!")
    elif actions_count > 0:
        st.caption(f"{remaining_g:.0f} g more to reach the goal.")

    st.markdown("---")

    with st.expander("Methodology", expanded=False):
        st.markdown(
            f"Carbon intensity: Coal 900 · LNG 450 · Oil 650 gCO₂/kWh (mix-based average, not marginal). "
            f"Appliance values are modelled estimates from Japanese energy label standards, "
            f"not measured consumption. Household profile: census-justified archetype "
            f"({hh['census_note']}). Incentive display is a design reference only."
        )
