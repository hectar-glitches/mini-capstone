import streamlit as st

st.set_page_config(page_title="Overview", layout="wide", page_icon="⚡")

st.title("Tokyo Power Consumption Analyzer")
st.caption(
    "A dashboard for understanding where Tokyo's electricity comes from, how carbon-heavy "
    "the grid is right now, and when it makes sense to shift flexible household tasks to cleaner windows."
)

st.divider()

# Core questions
st.subheader("The core question")

col1, col2 = st.columns(2)
with col1:
    st.markdown("**Is now a good time to use electricity — or should I wait a few hours?**")
with col2:
    st.markdown(
        "**If I shift one flexible task (laundry, EV charging, hot water) to a cleaner window, "
        "how much CO\u2082 does that save?**"
    )

st.divider()

# How it works
st.subheader("How it works")

st.markdown("""
The dashboard pulls live generation data from **TEPCO** (Tokyo Electric Power Company) — the utility
that serves the greater Tokyo area. TEPCO publishes a breakdown of how much electricity is being
generated from each fuel source at any given time: coal, LNG (gas), oil, nuclear, solar, wind,
hydro, and others.

From that fuel mix, the dashboard estimates **carbon intensity** — roughly how many grams of CO\u2082
are associated with producing one kilowatt-hour of electricity right now. Coal is the heaviest
(~900 gCO\u2082/kWh), LNG is moderate (~450), and renewables are near zero. When the grid is running
on more solar and less coal, the carbon intensity drops — and that is the right time to run
high-draw appliances.
""")

st.divider()

# ── Pages guide
st.subheader("What each page does")

c1, c2 = st.columns(2)

with c1:
    st.markdown("#### ⚡ Current Power Mix")
    st.markdown(
        "Shows the grid's fuel breakdown and carbon intensity at this moment. "
        "Auto-refreshes every 60 seconds. Start here to get an instant read on the grid."
    )

with c2:
    st.markdown("#### 🏠 Household Actions")
    st.markdown(
        "Choose a household profile (Shibuya, Adachi, or Setagaya) and a flexible appliance. "
        "The dashboard finds the cleanest windows in the day and shows the estimated CO\u2082 "
        "difference between acting now versus waiting."
    )

st.divider()

# ── Household profiles 
st.subheader("About the household profiles")

st.markdown("""
The three profiles — **Shibuya-ku**, **Adachi-ku**, and **Setagaya-ku** — are modeled archetypes
based on the 2020 Japanese Population Census. They do not represent real households and do not
mean the grid mix differs by ward (it does not). Their purpose is to reflect different
routines and flexibility constraints:

- **Shibuya** — single or couple, compact apartment, ~6–8 kWh/day, 40% of load is shiftable
- **Adachi** — family or elderly household, standard apartment/house, ~14–16 kWh/day, 35% shiftable
- **Setagaya** — larger family household with EV, ~18–22 kWh/day, higher absolute shift potential

Appliance energy values are estimates grounded in METI Top Runner efficiency standards.
Actual in-use consumption of older stock is typically 1.2–1.5\u00d7 the label value.
""")

st.divider()

#  Caveats 
st.subheader("What this dashboard does not claim")

st.markdown("""
This dashboard uses grid-level TEPCO data, not household smart-meter data.
It does not measure what appliances you personally ran today.
Carbon intensity is an estimate derived from reported generation categories and should be
used for relative comparisons and timing decisions, not treated as a precise emissions measurement.
Household profiles are modeled archetypes meant to support interpretation, not real household records.
""")
