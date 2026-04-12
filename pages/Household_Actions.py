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

shiftable_appliances = [a for a in hh["appliances"] if a["category"] == "shiftable"]

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
# Derived state — used in both columns
# ---------------------------------------------------------------------------
best_hours      = {w["hour"] for w in best_windows}
worst_hours     = {w["hour"] for w in worst_windows}
worst_intensity = worst_windows[0]["carbon_intensity_mean"] if worst_windows else current_intensity
in_best_window  = now_hour in best_hours

# ---------------------------------------------------------------------------
# Two-column layout: chart left, action right
# ---------------------------------------------------------------------------
col_chart, col_action = st.columns([3, 2], gap="large")

with col_chart:
    st.markdown("**Carbon intensity today** — green = best windows · red = avoid")

    if not profile.empty:
        fig = go.Figure()

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

    # --- Appliance selector — below the appliance list ---
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    st.markdown("**Which appliance are you planning to use?**")
    selected_appliance_name = st.selectbox(
        "Appliance",
        options=[a["name"] for a in shiftable_appliances],
        label_visibility="collapsed",
    )

app = next(a for a in shiftable_appliances if a["name"] == selected_appliance_name)
impact = calculate_action_impact(app, current_intensity, best_intensity)

with col_action:
    # --- Action comparison ---
    st.markdown(f"**{app['name']}** — timing impact")

    c_now, c_vs, c_best = st.columns([5, 1, 5])

    if in_best_window:
        # Already in a green window — compare now vs worst time
        co2_now_g      = app["kwh"] * current_intensity
        co2_worst_g    = app["kwh"] * worst_intensity
        saved_vs_worst = max(co2_worst_g - co2_now_g, 0)
        pct_vs_worst   = saved_vs_worst / co2_worst_g * 100 if co2_worst_g > 0 else 0
        ww = worst_windows[0] if worst_windows else None

        st.markdown(
            '<div style="font-size:0.78rem;color:#4ade80;margin-bottom:4px">'
            'You\'re already in a green window — now is the best time to run it.'
            '</div>',
            unsafe_allow_html=True,
        )
        with c_now:
            st.metric("Running it now", f"{co2_now_g:.0f} g CO₂",
                      help=f"{app['kwh']} kWh × {current_intensity:.0f} g/kWh (current grid)")
        with c_vs:
            st.markdown("<div style='text-align:center;padding-top:1.8rem;color:#555'>vs</div>",
                        unsafe_allow_html=True)
        with c_best:
            if ww:
                st.metric(
                    f"Peak time ({ww['label']})",
                    f"{co2_worst_g:.0f} g CO₂",
                    delta=f"−{saved_vs_worst:.0f} g" if saved_vs_worst > 0 else "Similar",
                    delta_color="inverse",
                    help=f"{app['kwh']} kWh × {worst_intensity:.0f} g/kWh (worst grid window)",
                )
        if saved_vs_worst > 0 and ww:
            st.markdown(
                f'<div class="impact-box">'
                f'Running now saves <strong>{saved_vs_worst:.0f} g CO₂</strong> '
                f'({pct_vs_worst:.0f}% less) vs the peak grid hours at {ww["label"]}. '
                f'Over 30 uses: ~<strong>{saved_vs_worst*30/1000:.2f} kg</strong> saved.'
                f'</div>',
                unsafe_allow_html=True,
            )
        log_g     = saved_vs_worst
        btn_label = f"I ran it now — {app['name']}"

    else:
        # Not in best window — show current vs best window
        bw = best_windows[0] if best_windows else None

        # Savings vs peak (always credited when user logs a shift)
        co2_worst_g   = app["kwh"] * worst_intensity
        saved_vs_peak = max(co2_worst_g - impact["co2_now_g"], 0)
        # Additional savings achievable by waiting for the best window
        extra_savings = impact["co2_saved_g"]  # co2_now - co2_best

        if bw:
            bw_hour = bw["hour"]
            hours_until = (bw_hour - now_hour) % 24
            if hours_until == 0:
                hours_until = 24
            day_prefix = "tomorrow " if bw_hour <= now_hour else ""
            if hours_until == 1:
                wait_hint = "in about 1 hour"
            elif hours_until < 24:
                wait_hint = f"in about {hours_until} hours"
            else:
                wait_hint = "tomorrow"
            wait_label = f"If you wait until {day_prefix}{bw['label']}"
        else:
            wait_hint = ""
            wait_label = "Best window"
            day_prefix = ""

        with c_now:
            st.metric(
                "If you use it now",
                f"{impact['co2_now_g']:.0f} g CO₂",
                delta=f"−{saved_vs_peak:.0f} g vs peak" if saved_vs_peak > 0 else None,
                delta_color="inverse",
                help=f"{app['kwh']} kWh × {current_intensity:.0f} g/kWh",
            )
        with c_vs:
            st.markdown("<div style='text-align:center;padding-top:1.8rem;color:#555'>→</div>",
                        unsafe_allow_html=True)
        with c_best:
            if bw:
                st.metric(
                    wait_label,
                    f"{impact['co2_best_g']:.0f} g CO₂",
                    delta=f"−{extra_savings:.0f} g more" if extra_savings > 0 else "Already optimal",
                    delta_color="inverse",
                    help=f"{app['kwh']} kWh × {best_intensity:.0f} g/kWh (cleaner grid window)",
                )

        if saved_vs_peak > 0 and bw:
            if extra_savings > 0:
                msg = (
                    f'Running now already saves <strong>{saved_vs_peak:.0f} g CO₂</strong> '
                    f'vs peak hours — good shift. '
                    f'Waiting {wait_hint} ({day_prefix}{bw["label"]}) '
                    f'saves <strong>{extra_savings:.0f} g more</strong>.'
                )
            else:
                msg = (
                    f'Running now saves <strong>{saved_vs_peak:.0f} g CO₂</strong> '
                    f'vs peak hours. The grid is already near its cleanest.'
                )
            st.markdown(
                f'<div class="impact-box">{msg}</div>',
                unsafe_allow_html=True,
            )
        elif extra_savings > 0 and bw:
            st.markdown(
                f'<div class="impact-box">'
                f'Waiting {wait_hint} ({day_prefix}{bw["label"]}) saves '
                f'<strong>{extra_savings:.0f} g CO₂</strong> vs running now.'
                f'</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="impact-box">The grid is at its cleanest right now — no need to wait.</div>',
                unsafe_allow_html=True,
            )
        # Always credit savings vs peak so any shift off-peak counts
        log_g     = saved_vs_peak if saved_vs_peak > 0 else max(extra_savings, 0)
        btn_label = f"I shifted it — {app['name']}"

    st.markdown("---")

    # --- Incentive tracker ---
    st.markdown("**Power-Saving Challenge**")

    CHALLENGES = {
        "Starter Shift": {
            "goal_g": 300,
            "goal_shifts": 3,
            "tag": "Beginner",
            "tag_color": "#22c55e",
            "program": "TEPCO 節電チャレンジ",
            "reward": "Bill credits for shifting load off peak hours",
        },
        "Carbon Reducer": {
            "goal_g": 500,
            "goal_shifts": 5,
            "tag": "Intermediate",
            "tag_color": "#f59e0b",
            "program": "SoftBank Eco-Denki",
            "reward": "Points redeemable per kWh avoided in high-carbon windows",
        },
        "Peak Avoider": {
            "goal_g": 1000,
            "goal_shifts": 8,
            "tag": "Advanced",
            "tag_color": "#ef4444",
            "program": "Octopus Energy Japan",
            "reward": "Time-of-use tariff: cheaper rates 10:00–14:00",
        },
    }
    challenge_keys = list(CHALLENGES.keys())

    if "action_log" not in st.session_state:
        st.session_state["action_log"] = []
    if "selected_challenge" not in st.session_state:
        st.session_state["selected_challenge"] = "Starter Shift"

    # Challenge selection cards — one per column
    ch_cols = st.columns(3)
    for i, (k, ch_opt) in enumerate(CHALLENGES.items()):
        with ch_cols[i]:
            active = st.session_state["selected_challenge"] == k
            border = ch_opt["tag_color"] if active else "rgba(255,255,255,0.08)"
            st.markdown(
                f'<div style="border:1px solid {border};border-radius:8px;'
                f'padding:8px 10px;font-size:0.76rem;line-height:1.65">'
                f'<span style="font-weight:600;font-size:0.8rem">{k}</span><br>'
                f'<span style="color:#888">{ch_opt["goal_g"]} g &nbsp;·&nbsp; '
                f'{ch_opt["goal_shifts"]} shifts</span><br>'
                f'<span style="color:{ch_opt["tag_color"]};font-size:0.7rem">'
                f'{ch_opt["tag"]}</span><br>'
                f'<span style="color:#556;font-size:0.69rem">{ch_opt["program"]}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

    new_challenge = st.radio(
        "Challenge",
        options=challenge_keys,
        index=challenge_keys.index(st.session_state["selected_challenge"]),
        horizontal=True,
        label_visibility="collapsed",
    )
    if new_challenge != st.session_state["selected_challenge"]:
        st.session_state["selected_challenge"] = new_challenge
        st.session_state["action_log"] = []
        st.rerun()

    ch = CHALLENGES[st.session_state["selected_challenge"]]
    total_saved_g = sum(st.session_state["action_log"])
    actions_count = len(st.session_state["action_log"])
    CHALLENGE_GOAL_G = float(ch["goal_g"])
    CHALLENGE_GOAL_SHIFTS = ch["goal_shifts"]

    g_pct = min(total_saved_g / CHALLENGE_GOAL_G * 100, 100)
    s_pct = min(actions_count / CHALLENGE_GOAL_SHIFTS * 100, 100)
    remaining_g = max(CHALLENGE_GOAL_G - total_saved_g, 0)
    remaining_s = max(CHALLENGE_GOAL_SHIFTS - actions_count, 0)

    # Dual progress bars
    st.markdown(
        f'<div style="margin-top:6px;font-size:0.74rem;color:#666;margin-bottom:1px">'
        f'CO₂ saved</div>'
        f'<div class="incentive-bar-bg">'
        f'<div class="incentive-bar-fill" style="width:{int(g_pct)}%"></div></div>'
        f'<div style="font-size:0.73rem;color:#777;margin-bottom:5px">'
        f'{total_saved_g:.0f} / {int(CHALLENGE_GOAL_G)} g'
        f'{"  ✓" if g_pct >= 100 else f"  — {remaining_g:.0f} g to go"}</div>'
        f'<div style="font-size:0.74rem;color:#666;margin-bottom:1px">'
        f'Shifts completed</div>'
        f'<div class="incentive-bar-bg">'
        f'<div class="incentive-bar-fill" style="width:{int(s_pct)}%"></div></div>'
        f'<div style="font-size:0.73rem;color:#777;margin-bottom:6px">'
        f'{actions_count} / {CHALLENGE_GOAL_SHIFTS}'
        f'{"  ✓" if s_pct >= 100 else f"  — {remaining_s} more"}</div>',
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    bc1, bc2 = st.columns([3, 1])
    with bc1:
        if st.button(btn_label, use_container_width=True):
            st.session_state["action_log"].append(max(log_g, 0))
            st.rerun()
    with bc2:
        if st.button("Reset", use_container_width=True):
            st.session_state["action_log"] = []
            st.rerun()

    if g_pct >= 100 and s_pct >= 100:
        other_programs = [
            (k2, v2) for k2, v2 in CHALLENGES.items()
            if k2 != st.session_state["selected_challenge"]
        ]
        other_html = "".join(
            f'<strong style="color:#bbb">{v2["program"]}</strong>'
            f' — {v2["reward"]}<br>'
            for _, v2 in other_programs
        )
        st.markdown(
            f'<div style="border:1px solid rgba(34,197,94,0.4);border-radius:8px;'
            f'padding:14px 16px;margin-top:8px">'
            f'<div style="color:#4ade80;font-weight:600;font-size:0.9rem;margin-bottom:6px">'
            f'Challenge complete — {int(CHALLENGE_GOAL_G)} g &amp; '
            f'{CHALLENGE_GOAL_SHIFTS} shifts</div>'
            f'<div style="font-size:0.8rem;color:#aaa;line-height:1.8;margin-bottom:8px">'
            f'You qualify for: <strong style="color:#ddd">{ch["program"]}</strong>'
            f' — {ch["reward"]}</div>'
            f'<div style="font-size:0.74rem;color:#666;line-height:1.8">'
            f'Other programs to explore:<br>{other_html}</div>'
            f'<div style="font-size:0.69rem;color:#444;margin-top:8px">'
            f'Illustrative design reference only. No actual rewards are issued here.'
            f'</div></div>',
            unsafe_allow_html=True,
        )
    elif actions_count > 0:
        unmet = []
        if g_pct < 100:
            unmet.append(f"{remaining_g:.0f} g more")
        if s_pct < 100:
            unmet.append(
                f"{remaining_s} more shift{'s' if remaining_s != 1 else ''}"
            )
        st.caption("Need: " + " and ".join(unmet) + " to complete.")

    st.markdown("---")

    with st.expander("Methodology", expanded=False):
        st.markdown(
            f"Carbon intensity: Coal 900 · LNG 450 · Oil 650 gCO₂/kWh (mix-based average, not marginal). "
            f"Appliance values are modelled estimates from Japanese energy label standards, "
            f"not measured consumption. Household profile: census-justified archetype "
            f"({hh['census_note']}). Incentive display is a design reference only."
        )
