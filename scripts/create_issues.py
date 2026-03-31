#!/usr/bin/env python3
"""
Creates GitHub issues documenting code inefficiencies and feature improvement
opportunities identified in the mini-capstone repository.

Usage (requires GH_TOKEN env var with issues:write permission):
    python scripts/create_issues.py

The script skips any issue whose title already exists to make it safe to run
more than once.
"""

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

REPO = os.environ.get("GITHUB_REPOSITORY", "hectar-glitches/mini-capstone")
TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
API_BASE = "https://api.github.com"


# ---------------------------------------------------------------------------
# Issue definitions
# ---------------------------------------------------------------------------

ISSUES = [
    {
        "title": "Bug: `calculate_renewable_percentage()` in data_loader.py has no implementation",
        "labels": ["bug"],
        "body": (
            "## Description\n\n"
            "The function `calculate_renewable_percentage()` is defined in "
            "`src/data_loader.py` but its body is empty. Any code path that calls "
            "this function will silently return `None`, producing incorrect results "
            "on every page that relies on it.\n\n"
            "## Location\n\n"
            "`src/data_loader.py` — function body is missing (starts around line 166).\n\n"
            "## Expected Behaviour\n\n"
            "The function should sum all renewable-energy columns (hydro, solar, wind, "
            "geothermal, biomass) and return their share of total generation as a "
            "percentage (0-100).\n\n"
            "## Suggested Fix\n\n"
            "```python\n"
            "def calculate_renewable_percentage(df=None):\n"
            '    """Return mean renewable energy percentage across all rows."""\n'
            "    if df is None:\n"
            "        df = get_shared_data()\n"
            "    if df is None:\n"
            "        return None\n\n"
            '    renewable_cols = ["hydro_mw", "solar_actual_mw", "wind_actual_mw",\n'
            '                      "geothermal_mw", "biomass_mw"]\n'
            "    available = [c for c in renewable_cols if c in df.columns]\n"
            '    all_mw = [c for c in df.columns if c.endswith("_mw")]\n\n'
            "    renewable_total = df[available].fillna(0).sum(axis=1)\n"
            "    total_gen = df[all_mw].fillna(0).sum(axis=1)\n\n"
            "    if total_gen.sum() == 0:\n"
            "        return 0.0\n"
            "    return float(\n"
            '        (renewable_total / total_gen.replace(0, float("nan")) * 100).mean()\n'
            "    )\n"
            "```\n"
        ),
    },
    {
        "title": "Bug: Year/month rollover logic in data_fetcher.py is incorrect",
        "labels": ["bug"],
        "body": (
            "## Description\n\n"
            "In `src/data_fetcher.py`, the fallback URL is built by manually "
            "decrementing the month integer:\n\n"
            "```python\n"
            "month = today.month - 1 if today.month > 1 else 12\n"
            "if month == 12:\n"
            "    year -= 1\n"
            "```\n\n"
            "This is fragile: the year decrement only fires when the month rolls to 12 "
            "(i.e. in January). In all other months `year` stays as `today.year` which "
            "is correct, but the logic is hard to reason about. More importantly, if "
            "both the primary and fallback URLs fail there is no third fallback and the "
            "function returns `None` with no user-facing feedback.\n\n"
            "## Suggested Fix\n\n"
            "Use `datetime` arithmetic instead of manual integer math:\n\n"
            "```python\n"
            "from datetime import datetime\n"
            "from dateutil.relativedelta import relativedelta\n"
            "import logging\n\n"
            "logger = logging.getLogger(__name__)\n\n"
            "def _tepco_url(dt):\n"
            "    return (\n"
            '        f"https://www.tepco.co.jp/forecast/html/images/"\n'
            '        f"eria_jukyu_{dt.year}{dt.month:02d}_03.csv"\n'
            "    )\n\n"
            "def fetch_data():\n"
            "    today = datetime.now()\n"
            "    for delta_months in (0, -1, -2):\n"
            "        candidate = today + relativedelta(months=delta_months)\n"
            "        url = _tepco_url(candidate)\n"
            "        try:\n"
            "            response = requests.get(url, timeout=10)\n"
            "            response.raise_for_status()\n"
            "            return io.BytesIO(response.content)\n"
            "        except requests.HTTPError:\n"
            '            logger.warning("HTTP error for URL: %s", url)\n'
            "        except requests.RequestException as exc:\n"
            '            logger.error("Network error: %s", exc)\n'
            "            break\n"
            "    return None\n"
            "```\n"
        ),
    },
    {
        "title": "Bug: action_log in Household_Actions page grows unbounded in session state",
        "labels": ["bug"],
        "body": (
            "## Description\n\n"
            "In `pages/4_Household_Actions.py`, every time the user logs a "
            "power-saving action it is appended to `st.session_state[\"action_log\"]` "
            "with no upper bound. In a long-running Streamlit session the list grows "
            "without limit, consuming increasing memory and slowing down page "
            "re-renders. Additionally the log is never persisted, so all data is lost "
            "when the browser tab is refreshed.\n\n"
            "## Suggested Fixes\n\n"
            "1. Cap the in-memory log and evict the oldest entries:\n\n"
            "```python\n"
            "MAX_ACTION_LOG = 200\n\n"
            "def append_action(entry: dict) -> None:\n"
            '    log = st.session_state.setdefault("action_log", [])\n'
            "    log.append(entry)\n"
            "    if len(log) > MAX_ACTION_LOG:\n"
            '        st.session_state["action_log"] = log[-MAX_ACTION_LOG:]\n'
            "```\n\n"
            "2. Add a CSV download button so users can export their history before "
            "refreshing.\n"
        ),
    },
    {
        "title": "Code Quality: Emissions factors hardcoded in three separate files",
        "labels": ["enhancement"],
        "body": (
            "## Description\n\n"
            "The CO2 emissions intensity values for coal (900 g CO2/kWh), "
            "LNG (450 g CO2/kWh), and oil (650 g CO2/kWh) are copy-pasted into at "
            "least **three** different source files:\n\n"
            "- `pages/3_Current_Power.py`\n"
            "- `src/household_profiles.py`\n"
            "- `pages/4_Household_Actions.py`\n\n"
            "If any value needs updating (e.g. revised IPCC figures), all three files "
            "must be changed in sync, which is an error-prone maintenance hazard.\n\n"
            "## Suggested Fix\n\n"
            "Create `src/constants.py` and import from it everywhere:\n\n"
            "```python\n"
            "# src/constants.py\n\n"
            "# CO2 emissions factors (g CO2 per kWh generated)\n"
            "EMISSIONS_FACTORS_G_PER_KWH = {\n"
            '    "thermal_coal_mw": 900,\n'
            '    "thermal_lng_mw":  450,\n'
            '    "thermal_oil_mw":  650,\n'
            "}\n\n"
            "TEPCO_RATE_JPY_PER_KWH   = 31.0    # residential flat-rate tariff\n"
            "CHALLENGE_GOAL_G_CO2     = 500.0   # daily savings target\n"
            "AUTO_REFRESH_INTERVAL_MS = 60_000  # live-data polling interval\n"
            "```\n\n"
            "Then replace every inline literal with an import from this module.\n"
        ),
    },
    {
        "title": "Code Quality: Sidebar data-source selector duplicated across four pages",
        "labels": ["enhancement"],
        "body": (
            "## Description\n\n"
            "The logic that renders the 'Fetch TEPCO data / Upload CSV file' sidebar "
            "widget is copied verbatim into:\n\n"
            "- `app.py`\n"
            "- `pages/1_Overview.py`\n"
            "- `pages/2_Time_Series.py`\n"
            "- `pages/4_Household_Actions.py`\n\n"
            "This is roughly 15-20 lines repeated four times (~80 duplicate lines of "
            "code in total). Any change to the sidebar must be made in all four places.\n\n"
            "## Suggested Fix\n\n"
            "Extract the widget into a shared helper, e.g. `src/components.py`:\n\n"
            "```python\n"
            "# src/components.py\n"
            "import streamlit as st\n"
            "from src.data_loader import load_data, set_shared_data\n"
            "from src.data_fetcher import fetch_data\n\n"
            "def render_data_source_sidebar() -> bool:\n"
            '    """Render the data-source selector in the sidebar.\n\n'
            "    Returns:\n"
            "        True when new data was successfully loaded into session state.\n"
            '    """\n'
            "    with st.sidebar:\n"
            '        st.header("Data Source")\n'
            "        choice = st.radio(\n"
            '            "Choose data source",\n'
            '            ["Fetch TEPCO data", "Upload CSV file"],\n'
            "        )\n"
            '        if choice == "Upload CSV file":\n'
            '            uploaded = st.file_uploader("Upload CSV file", type=["csv"])\n'
            "            if uploaded:\n"
            "                load_data(uploaded)\n"
            "                set_shared_data()\n"
            '                st.success("File loaded successfully!")\n'
            "                return True\n"
            "        else:\n"
            '            if st.button("Fetch Latest TEPCO data"):\n'
            "                file_like = fetch_data()\n"
            "                if file_like:\n"
            "                    load_data(file_like)\n"
            "                    set_shared_data()\n"
            '                    st.success("TEPCO data fetched successfully!")\n'
            "                    return True\n"
            "    return False\n"
            "```\n\n"
            "Each page then imports and calls this single function.\n"
        ),
    },
    {
        "title": "Code Quality: Replace print() statements with structured logging",
        "labels": ["enhancement"],
        "body": (
            "## Description\n\n"
            "`src/data_fetcher.py` (and potentially other modules) uses bare `print()` "
            "calls for diagnostic output. These messages cannot be filtered by severity, "
            "captured by log aggregators, or suppressed in production.\n\n"
            "## Suggested Fix\n\n"
            "Replace `print()` with Python's standard `logging` module:\n\n"
            "```python\n"
            "# src/data_fetcher.py\n"
            "import logging\n\n"
            "logger = logging.getLogger(__name__)\n\n"
            "# Before:  print('Trying URL:', url)\n"
            "logger.debug('Trying URL: %s', url)\n\n"
            "# Before:  print('Error:', e)\n"
            "logger.warning('Failed to fetch TEPCO data: %s', e)\n"
            "```\n\n"
            "Configure the root logger once in `app.py`:\n\n"
            "```python\n"
            "import logging\n"
            "logging.basicConfig(\n"
            "    level=logging.INFO,\n"
            '    format="%(asctime)s  %(name)-25s  %(levelname)-8s  %(message)s",\n'
            ")\n"
            "```\n"
        ),
    },
    {
        "title": "Enhancement: Add input validation for uploaded CSV files",
        "labels": ["enhancement"],
        "body": (
            "## Description\n\n"
            "When a user uploads a CSV file, it is passed directly to `load_data()` "
            "with no pre-flight checks. This can produce confusing stack traces for:\n\n"
            "- Files that exceed a safe size limit.\n"
            "- Non-UTF-8 encoded files (the parser will raise `UnicodeDecodeError`).\n"
            "- Files missing expected columns.\n"
            "- Files where all values in a column are `NaN`, breaking downstream "
            "arithmetic.\n\n"
            "## Suggested Fix\n\n"
            "Add a `validate_dataframe()` helper in `src/data_loader.py` or a new "
            "`src/validator.py`:\n\n"
            "```python\n"
            "class DataValidationError(ValueError):\n"
            '    """Raised when an uploaded DataFrame fails validation."""\n\n'
            "def validate_dataframe(df) -> None:\n"
            '    """Raise DataValidationError if df is not usable."""\n'
            "    if df.empty:\n"
            '        raise DataValidationError("The uploaded file contains no data rows.")\n'
            "    if df.shape[1] < 2:\n"
            "        raise DataValidationError(\n"
            '            "The file must contain at least two columns."\n'
            "        )\n"
            "    all_null_cols = [c for c in df.columns if df[c].isna().all()]\n"
            "    if all_null_cols:\n"
            "        raise DataValidationError(\n"
            '            f"The following columns are entirely empty: {all_null_cols}"\n'
            "        )\n"
            "```\n\n"
            "Wrap the file-upload handler in each page with a "
            "`try/except DataValidationError` block and surface the error via "
            "`st.error()`.\n"
        ),
    },
    {
        "title": "Enhancement: Add unit tests -- currently zero test coverage",
        "labels": ["enhancement"],
        "body": (
            "## Description\n\n"
            "The repository contains **no test files**. Every function in `src/` is "
            "untested, making refactoring risky and regressions invisible.\n\n"
            "## Suggested Initial Test Suite\n\n"
            "```\n"
            "tests/\n"
            "    conftest.py                  # shared fixtures (sample DataFrames)\n"
            "    test_data_loader.py          # load_data, detect_datetime_columns\n"
            "    test_data_fetcher.py         # URL construction, error handling\n"
            "    test_analyzer.py             # descriptive_stats, detect_time_patterns\n"
            "    test_household_profiles.py   # archetype data, carbon window logic\n"
            "    test_visualizations.py       # chart functions return valid Plotly figures\n"
            "```\n\n"
            "### Example\n\n"
            "```python\n"
            "# tests/test_analyzer.py\n"
            "import pandas as pd\n"
            "from src.analyzer import descriptive_stats\n\n"
            "def test_descriptive_stats_returns_expected_keys():\n"
            '    df = pd.DataFrame({"value": [1, 2, 3, 4, 5]})\n'
            "    stats = descriptive_stats(df)\n"
            '    for key in ("mean", "median", "std", "min", "max"):\n'
            "        assert key in stats\n\n"
            "def test_descriptive_stats_with_empty_df_returns_none():\n"
            "    assert descriptive_stats(pd.DataFrame()) is None\n"
            "```\n\n"
            "## Acceptance Criteria\n\n"
            "- [ ] `pytest` runs successfully on a fresh clone.\n"
            "- [ ] Line coverage >= 60% for all files in `src/`.\n"
            "- [ ] A CI step runs the tests on every push.\n"
        ),
    },
    {
        "title": "Enhancement: Add type hints and docstrings to all functions in src/",
        "labels": ["enhancement"],
        "body": (
            "## Description\n\n"
            "None of the functions in the `src/` package have:\n\n"
            "- **Type annotations** -- IDEs cannot infer argument/return types.\n"
            "- **Docstrings** -- No machine-readable documentation.\n\n"
            "## Example -- Current vs Desired\n\n"
            "```python\n"
            "# CURRENT\n"
            "def descriptive_stats(df):\n"
            "    if df is None or df.empty:\n"
            "        return None\n\n"
            "# DESIRED\n"
            "def descriptive_stats(df: pd.DataFrame | None) -> dict[str, float] | None:\n"
            '    """Return basic descriptive statistics for all numeric columns.\n\n'
            "    Args:\n"
            "        df: Input DataFrame. Returns None if empty or None.\n\n"
            "    Returns:\n"
            "        Dict with keys mean, median, std, min, max, skewness,\n"
            "        kurtosis and corresponding float values, or None.\n"
            '    """\n'
            "    if df is None or df.empty:\n"
            "        return None\n"
            "```\n\n"
            "## Files Affected\n\n"
            "All modules in `src/`: `data_loader.py`, `data_fetcher.py`, "
            "`analyzer.py`, `visualizations.py`, `household_profiles.py`.\n"
        ),
    },
    {
        "title": "Performance: Carbon intensity series recalculated on every page render",
        "labels": ["enhancement"],
        "body": (
            "## Description\n\n"
            "In `pages/3_Current_Power.py` the full carbon intensity time-series is "
            "recomputed from scratch on **every Streamlit re-render** (triggered by any "
            "widget interaction or auto-refresh tick). For a full month of 30-minute "
            "data (~1,440 rows) the overhead is small today, but this pattern will not "
            "scale as the dataset grows.\n\n"
            "## Suggested Fix\n\n"
            "Wrap the computation in `@st.cache_data`, keyed on the DataFrame:\n\n"
            "```python\n"
            "@st.cache_data\n"
            "def compute_carbon_intensity(df: pd.DataFrame) -> pd.Series:\n"
            '    """Return gCO2/kWh for each row. Cached until df changes."""\n'
            '    coal  = df.get("thermal_coal_mw", 0)\n'
            '    lng   = df.get("thermal_lng_mw",  0)\n'
            '    oil   = df.get("thermal_oil_mw",  0)\n'
            '    mw_cols = [c for c in df.columns if c.endswith("_mw")]\n'
            '    total = df[mw_cols].sum(axis=1).replace(0, float("nan"))\n'
            "    return (coal * 900 + lng * 450 + oil * 650) / total\n"
            "```\n\n"
            "Streamlit's cache is automatically invalidated when `df` changes, so "
            "this is safe and requires no manual cache management.\n"
        ),
    },
    {
        "title": "Enhancement: Add JSON and Excel export options alongside CSV",
        "labels": ["enhancement"],
        "body": (
            "## Description\n\n"
            "The Overview page currently offers only a CSV download of the raw data. "
            "Users who need to open the data in Excel or feed it into other tooling "
            "have no convenient option.\n\n"
            "## Suggested Addition\n\n"
            "Add an Export expander in `pages/1_Overview.py` with three download "
            "buttons:\n\n"
            "```python\n"
            "import io\n"
            "with st.expander('Export Data'):\n"
            "    col1, col2, col3 = st.columns(3)\n"
            "    with col1:\n"
            "        st.download_button(\n"
            '            "CSV",\n'
            "            df.to_csv(index=False).encode(),\n"
            '            "tepco_data.csv", "text/csv",\n'
            "        )\n"
            "    with col2:\n"
            "        st.download_button(\n"
            '            "JSON",\n'
            '            df.to_json(orient="records", date_format="iso").encode(),\n'
            '            "tepco_data.json", "application/json",\n'
            "        )\n"
            "    with col3:\n"
            "        buf = io.BytesIO()\n"
            "        df.to_excel(buf, index=False)\n"
            "        st.download_button(\n"
            '            "Excel", buf.getvalue(), "tepco_data.xlsx",\n'
            '            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",\n'
            "        )\n"
            "```\n\n"
            "`openpyxl` (a pandas optional dependency) is required for Excel export.\n"
        ),
    },
    {
        "title": "Enhancement: Make timezone handling explicit (currently hardcoded to JST)",
        "labels": ["enhancement"],
        "body": (
            "## Description\n\n"
            "All datetime processing implicitly assumes Japan Standard Time "
            "(JST / UTC+9). There is no timezone-aware parsing, no tz-aware DataFrame "
            "index, and no user-facing timezone selector.\n\n"
            "Consequences:\n"
            "- If the app is deployed on a server in a different timezone, 'current "
            "hour' comparisons in `Current_Power.py` will be wrong.\n"
            "- Users outside Japan cannot align 'best time window' recommendations to "
            "their local clock.\n\n"
            "## Suggested Fix\n\n"
            "1. Parse datetimes as tz-aware in `src/data_loader.py`:\n\n"
            "```python\n"
            "import pytz\n"
            'JST = pytz.timezone("Asia/Tokyo")\n'
            'df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(JST)\n'
            "```\n\n"
            "2. Add a timezone selector to the sidebar:\n\n"
            "```python\n"
            "tz_name = st.sidebar.selectbox(\n"
            '    "Display timezone",\n'
            '    ["Asia/Tokyo", "UTC", "America/New_York", "Europe/London"],\n'
            "    index=0,\n"
            ")\n"
            "import pytz\n"
            'df["date_local"] = df["date"].dt.tz_convert(pytz.timezone(tz_name))\n'
            "```\n"
        ),
    },
]


# ---------------------------------------------------------------------------
# GitHub API helpers
# ---------------------------------------------------------------------------


def _api_request(method: str, path: str, body=None):
    url = f"{API_BASE}{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode()
        raise RuntimeError(
            f"GitHub API {method} {path} -> HTTP {exc.code}: {error_body}"
        ) from exc


def list_existing_issue_titles() -> set:
    """Return the set of open+closed issue titles already in the repo."""
    titles = set()
    page = 1
    while True:
        items = _api_request(
            "GET",
            f"/repos/{REPO}/issues?state=all&per_page=100&page={page}",
        )
        if not items:
            break
        for item in items:
            titles.add(item["title"])
        if len(items) < 100:
            break
        page += 1
    return titles


def ensure_label(name: str, color: str, description: str) -> None:
    """Create the label if it does not exist."""
    try:
        _api_request(
            "GET",
            f"/repos/{REPO}/labels/{urllib.parse.quote(name)}",
        )
    except RuntimeError:
        try:
            _api_request(
                "POST",
                f"/repos/{REPO}/labels",
                {"name": name, "color": color, "description": description},
            )
            print(f"  Created label '{name}'")
        except RuntimeError as exc:
            print(f"  Warning: could not create label '{name}': {exc}")


def create_issue(title: str, body: str, labels: list) -> int:
    result = _api_request(
        "POST",
        f"/repos/{REPO}/issues",
        {"title": title, "body": body, "labels": labels},
    )
    return result["number"]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    if not TOKEN:
        print(
            "ERROR: Set the GH_TOKEN (or GITHUB_TOKEN) environment variable "
            "to a personal access token with 'issues:write' permission.",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"Repository : {REPO}")
    print(f"Issues to create: {len(ISSUES)}\n")

    # Ensure standard labels exist
    ensure_label("bug", "d73a4a", "Something is not working correctly")
    ensure_label("enhancement", "a2eeef", "New feature or improvement request")

    # Fetch existing issue titles to avoid duplicates
    print("Fetching existing issues ...")
    existing_titles = list_existing_issue_titles()
    print(f"Found {len(existing_titles)} existing issue(s).\n")

    created = 0
    skipped = 0
    for issue in ISSUES:
        if issue["title"] in existing_titles:
            print(f"  SKIP  (already exists) : {issue['title'][:80]}")
            skipped += 1
            continue
        number = create_issue(issue["title"], issue["body"], issue["labels"])
        print(f"  CREATED #{number:4d} : {issue['title'][:80]}")
        created += 1

    print(f"\nDone. Created {created} issue(s), skipped {skipped} duplicate(s).")


if __name__ == "__main__":
    main()
