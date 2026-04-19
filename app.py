import streamlit as st
from src.data_loader import fetch_data, load_data, set_shared_data, get_shared_data, get_data_info

st.set_page_config(
    page_title="Tokyo Power Consumption Analyzer",
    layout="wide",
    page_icon="⚡",
    initial_sidebar_state="expanded",
)

# ── Sidebar: data loading ─────────────────────────────────────────────────────
with st.sidebar:
    st.header("Data")

    if st.button("Fetch latest TEPCO data", use_container_width=True):
        with st.spinner("Fetching..."):
            file_like = fetch_data()
            if file_like is not None:
                load_data.clear()
                if "shared_df" in st.session_state:
                    del st.session_state["shared_df"]
                df = load_data()
                set_shared_data()

    df = get_shared_data()
    if df is not None:
        info = get_data_info()
        st.success("Data loaded")
        st.metric("Rows", f"{info['rows']:,}")
        date_col = df["date"] if "date" in df.columns else None
        if date_col is not None:
            st.caption(
                f"{date_col.min().strftime('%Y-%m-%d')} → {date_col.max().strftime('%Y-%m-%d')}"
            )

# ── Main ──────────────────────────────────────────────────────────────────────
st.title("Tokyo Power Consumption Analyzer")
st.caption(
    "Understand where Tokyo's electricity comes from, how carbon-heavy the grid is right now, "
    "and when to shift flexible household tasks to cleaner windows."
)

st.divider()

df = get_shared_data()

if df is None:
    st.info("Fetch the latest TEPCO data from the sidebar to get started.")
else:
    st.success("Data loaded — use the pages in the sidebar to explore.")
    st.markdown("**Where to go next:**")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Current Power Mix")
        st.markdown("Live grid fuel breakdown and carbon intensity. Auto-refreshes every 60 s.")
    with col2:
        st.markdown("#### Household Actions")
        st.markdown("Pick a household profile and appliance to find the cleanest window today.")
