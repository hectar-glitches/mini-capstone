"""
Household archetype definitions for the Tokyo energy flexibility dashboard.

Three census-justified modeled household profiles based on:
- 2020 Population Census (Tables 6-4, 8-1)
- Tokyo Statistical Yearbook housing data
- Japanese energy label standards for typical appliance consumption

These are modeled profiles, not actual household measurements.
Appliance consumption values are typical estimates, not monitored readings.
"""

import pandas as pd

# ---------------------------------------------------------------------------
# Carbon intensity emissions factors (gCO₂/kWh) — consistent with
# the values already used in Current_Power.py
# ---------------------------------------------------------------------------
EMISSIONS_FACTORS = {
    "thermal_coal_mw": 900,
    "thermal_lng_mw": 450,
    "thermal_oil_mw": 650,
}

# ---------------------------------------------------------------------------
# Appliance data per household archetype
#
# Each appliance dict has:
#   name          – display label
#   category      – "fixed" (not shiftable) or "shiftable"
#   kwh           – typical energy per run/day (kWh)
#   duration_h    – typical runtime in hours
#   typical_hour  – default start hour (24-h clock)
#   icon          – emoji for UI display
# ---------------------------------------------------------------------------

HOUSEHOLDS = {
    "shibuya": {
        "label": "Shibuya-ku — Central Apartment",
        "sublabel": "Single or couple, compact apartment",
        "icon": "🏙️",
        "daily_kwh_range": (6, 8),
        "shiftable_pct": 0.40,
        "description": (
            "Dense central ward with low family-household share. "
            "Minimal appliance set, no dishwasher or EV. "
            "40% of daily consumption is time-shiftable."
        ),
        "census_note": (
            "Justified by 2020 Census Table 6-4: Shibuya has one of Tokyo's "
            "lowest shares of family households and largest share of single-person households."
        ),
        "appliances": [
            {
                "id": "shibuya_ac",
                "name": "Air Conditioner",
                "category": "fixed",
                "kwh": 1.2,
                "duration_h": 4.0,
                "typical_hour": 19,
                "icon": "❄️",
                "note": "Evening use fixed by occupancy schedule",
            },
            {
                "id": "shibuya_fridge",
                "name": "Refrigerator",
                "category": "fixed",
                "kwh": 1.0,
                "duration_h": 24.0,
                "typical_hour": 0,
                "icon": "🧊",
                "note": "Continuous — not shiftable",
            },
            {
                "id": "shibuya_washer",
                "name": "Washing Machine",
                "category": "shiftable",
                "kwh": 0.8,
                "duration_h": 1.0,
                "typical_hour": 20,
                "icon": "🫧",
                "note": "Typically run in evening; can shift to solar peak",
            },
            {
                "id": "shibuya_lighting",
                "name": "Lighting & Electronics",
                "category": "fixed",
                "kwh": 1.5,
                "duration_h": 5.0,
                "typical_hour": 18,
                "icon": "💡",
                "note": "Evening occupancy driven",
            },
            {
                "id": "shibuya_cooking",
                "name": "Cooking (IH/Microwave)",
                "category": "fixed",
                "kwh": 0.6,
                "duration_h": 0.5,
                "typical_hour": 19,
                "icon": "🍳",
                "note": "Meal-time fixed",
            },
            {
                "id": "shibuya_devices",
                "name": "Device Charging",
                "category": "shiftable",
                "kwh": 0.3,
                "duration_h": 2.0,
                "typical_hour": 23,
                "icon": "🔋",
                "note": "Can shift to overnight or midday solar window",
            },
        ],
    },

    "adachi": {
        "label": "Adachi-ku — Family or Elderly Household",
        "sublabel": "Mixed family structure, standard apartment/house",
        "icon": "🏠",
        "daily_kwh_range": (14, 16),
        "shiftable_pct": 0.35,
        "description": (
            "Northern ward with higher elderly population and mixed family structures. "
            "Standard appliance set with daytime HVAC constraints. "
            "35% shiftable — lower than Setagaya due to less schedule flexibility."
        ),
        "census_note": (
            "Justified by 2020 Census Table 8-1: Adachi has above-average share of "
            "elderly-only households and multi-generational families."
        ),
        "appliances": [
            {
                "id": "adachi_ac",
                "name": "Air Conditioner",
                "category": "fixed",
                "kwh": 3.5,
                "duration_h": 10.0,
                "typical_hour": 8,
                "icon": "❄️",
                "note": "Extended daytime use by elderly residents — not shiftable",
            },
            {
                "id": "adachi_fridge",
                "name": "Refrigerator",
                "category": "fixed",
                "kwh": 1.2,
                "duration_h": 24.0,
                "typical_hour": 0,
                "icon": "🧊",
                "note": "Continuous — not shiftable",
            },
            {
                "id": "adachi_washer",
                "name": "Washing Machine",
                "category": "shiftable",
                "kwh": 1.0,
                "duration_h": 1.0,
                "typical_hour": 9,
                "icon": "🫧",
                "note": "Morning use; can shift to solar midday window",
            },
            {
                "id": "adachi_dryer",
                "name": "Dryer / Ventilation Fan",
                "category": "shiftable",
                "kwh": 1.2,
                "duration_h": 1.5,
                "typical_hour": 10,
                "icon": "💨",
                "note": "Can pair with washing machine shift",
            },
            {
                "id": "adachi_rice",
                "name": "Rice Cooker",
                "category": "shiftable",
                "kwh": 0.5,
                "duration_h": 0.75,
                "typical_hour": 17,
                "icon": "🍚",
                "note": "Dinner timing can shift ±2 hours",
            },
            {
                "id": "adachi_cooking",
                "name": "Cooking (Gas/IH)",
                "category": "fixed",
                "kwh": 1.0,
                "duration_h": 1.0,
                "typical_hour": 18,
                "icon": "🍳",
                "note": "Meal-time fixed",
            },
            {
                "id": "adachi_lighting",
                "name": "Lighting & TV",
                "category": "fixed",
                "kwh": 2.0,
                "duration_h": 8.0,
                "typical_hour": 17,
                "icon": "📺",
                "note": "Evening occupancy driven",
            },
            {
                "id": "adachi_water",
                "name": "Water Heater (Electric)",
                "category": "shiftable",
                "kwh": 2.5,
                "duration_h": 3.0,
                "typical_hour": 23,
                "icon": "🚿",
                "note": "Ideal overnight low-carbon window",
            },
        ],
    },

    "setagaya": {
        "label": "Setagaya-ku — Suburban Family",
        "sublabel": "Family household, larger dwelling + EV",
        "icon": "🏡",
        "daily_kwh_range": (18, 22),
        "shiftable_pct": 0.55,
        "description": (
            "Large residential ward with family-residential character and bigger dwellings. "
            "Full appliance suite including EV charging. "
            "55% shiftable — highest flexibility due to schedule control and EV."
        ),
        "census_note": (
            "Justified by 2020 Census Table 6-4: Setagaya has Tokyo's highest share of "
            "family households and largest average dwelling floor area."
        ),
        "appliances": [
            {
                "id": "setagaya_ac",
                "name": "Air Conditioner (×2 units)",
                "category": "fixed",
                "kwh": 4.0,
                "duration_h": 8.0,
                "typical_hour": 7,
                "icon": "❄️",
                "note": "Multiple rooms — fixed by household schedule",
            },
            {
                "id": "setagaya_fridge",
                "name": "Refrigerator (large)",
                "category": "fixed",
                "kwh": 1.5,
                "duration_h": 24.0,
                "typical_hour": 0,
                "icon": "🧊",
                "note": "Continuous — not shiftable",
            },
            {
                "id": "setagaya_washer",
                "name": "Washing Machine",
                "category": "shiftable",
                "kwh": 1.0,
                "duration_h": 1.0,
                "typical_hour": 9,
                "icon": "🫧",
                "note": "Best shifted to solar peak (10:00–14:00)",
            },
            {
                "id": "setagaya_dryer",
                "name": "Dryer",
                "category": "shiftable",
                "kwh": 2.0,
                "duration_h": 1.5,
                "typical_hour": 10,
                "icon": "💨",
                "note": "High-impact shift target",
            },
            {
                "id": "setagaya_dishwasher",
                "name": "Dishwasher",
                "category": "shiftable",
                "kwh": 1.0,
                "duration_h": 1.5,
                "typical_hour": 20,
                "icon": "🍽️",
                "note": "Post-dinner; can delay to post-22:00 low-demand window",
            },
            {
                "id": "setagaya_ev",
                "name": "EV Charging",
                "category": "shiftable",
                "kwh": 6.0,
                "duration_h": 4.0,
                "typical_hour": 22,
                "icon": "🔌",
                "note": "Highest-impact shiftable load — prefer overnight",
            },
            {
                "id": "setagaya_water",
                "name": "Water Heater (Electric)",
                "category": "shiftable",
                "kwh": 3.0,
                "duration_h": 3.0,
                "typical_hour": 23,
                "icon": "🚿",
                "note": "Ideal overnight low-carbon window",
            },
            {
                "id": "setagaya_cooking",
                "name": "Cooking (IH Cooktop)",
                "category": "fixed",
                "kwh": 1.2,
                "duration_h": 1.0,
                "typical_hour": 18,
                "icon": "🍳",
                "note": "Meal-time fixed",
            },
            {
                "id": "setagaya_lighting",
                "name": "Lighting & Electronics",
                "category": "fixed",
                "kwh": 2.0,
                "duration_h": 6.0,
                "typical_hour": 17,
                "icon": "💡",
                "note": "Evening occupancy driven",
            },
        ],
    },
}


# ---------------------------------------------------------------------------
# Carbon intensity helpers
# ---------------------------------------------------------------------------

def compute_carbon_intensity_series(df: pd.DataFrame) -> pd.Series:
    """
    Compute per-row grid carbon intensity (gCO₂/kWh) from TEPCO generation mix.

    Uses the same emissions factors as Current_Power.py:
        Coal  → 900 g/kWh
        LNG   → 450 g/kWh
        Oil   → 650 g/kWh

    Args:
        df: DataFrame produced by data_loader.load_data(), which must contain
            columns thermal_coal_mw, thermal_lng_mw, thermal_oil_mw and at
            least one total generation column.

    Returns:
        pd.Series of carbon intensity values (gCO₂/kWh), NaN where total is 0.
    """
    fossil_cols = {
        "thermal_coal_mw": 900,
        "thermal_lng_mw": 450,
        "thermal_oil_mw": 650,
    }

    generation_cols = [
        "nuclear_mw", "thermal_lng_mw", "thermal_coal_mw", "thermal_oil_mw",
        "thermal_other_mw", "hydro_mw", "geothermal_mw", "biomass_mw",
        "solar_actual_mw", "wind_actual_mw", "pumped_hydro_mw",
        "battery_mw", "interconnector_mw", "other_mw",
    ]

    avail_gen = [c for c in generation_cols if c in df.columns]
    total = df[avail_gen].fillna(0).sum(axis=1)

    emissions = sum(
        df[col].fillna(0) * factor
        for col, factor in fossil_cols.items()
        if col in df.columns
    )

    intensity = emissions / total.replace(0, float("nan"))
    return intensity


def get_hourly_carbon_profile(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate carbon intensity by hour of day across the full dataset.

    Returns a DataFrame with columns:
        hour            – 0..23
        carbon_intensity_mean  – mean gCO₂/kWh for that hour
        carbon_intensity_min   – min
        carbon_intensity_max   – max
    """
    df = df.copy()
    df["_intensity"] = compute_carbon_intensity_series(df)

    # Extract hour robustly.
    # load_data() converts any column whose name contains "time" to datetime,
    # so df["time"] may be a datetime64 (e.g. 1900-01-01 00:30:00) rather than
    # a plain "HH:MM" string.  We handle both cases.
    df["_hour"] = None

    if "time" in df.columns:
        t = df["time"]
        if pd.api.types.is_datetime64_any_dtype(t):
            # Already a datetime — extract hour directly
            df["_hour"] = t.dt.hour
        else:
            # String like "0:30" or "00:30" — parse the hour portion
            df["_hour"] = pd.to_datetime(
                t.astype(str), format="%H:%M", errors="coerce"
            ).dt.hour

    # Fall back to combining date + time into a full datetime
    if df["_hour"].isna().all():
        if "date" in df.columns:
            if "time" in df.columns:
                combined = (
                    pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")
                    + " "
                    + df["time"].astype(str).str.extract(r"(\d{1,2}:\d{2})")[0].fillna("00:00")
                )
                df["_hour"] = pd.to_datetime(combined, errors="coerce").dt.hour
            else:
                df["_hour"] = pd.to_datetime(df["date"], errors="coerce").dt.hour
        else:
            return pd.DataFrame()

    df["_hour"] = df["_hour"].astype("Int64")
    profile = (
        df.groupby("_hour")["_intensity"]
        .agg(
            carbon_intensity_mean="mean",
            carbon_intensity_min="min",
            carbon_intensity_max="max",
        )
        .reset_index()
        .rename(columns={"_hour": "hour"})
    )
    return profile


def find_best_windows(profile: pd.DataFrame, n: int = 3) -> list[dict]:
    """
    Return the n lowest-carbon hours from an hourly profile DataFrame.

    Args:
        profile: output of get_hourly_carbon_profile()
        n:       number of windows to return

    Returns:
        list of dicts with keys: hour, label, carbon_intensity_mean
    """
    if profile.empty:
        return []
    top = profile.nsmallest(n, "carbon_intensity_mean")
    result = []
    for _, row in top.iterrows():
        h = int(row["hour"])
        result.append(
            {
                "hour": h,
                "label": f"{h:02d}:00–{(h+1)%24:02d}:00",
                "carbon_intensity_mean": row["carbon_intensity_mean"],
            }
        )
    return result


def find_worst_windows(profile: pd.DataFrame, n: int = 3) -> list[dict]:
    """
    Return the n highest-carbon hours from an hourly profile DataFrame.

    Args:
        profile: output of get_hourly_carbon_profile()
        n:       number of windows to return

    Returns:
        list of dicts with keys: hour, label, carbon_intensity_mean
    """
    if profile.empty:
        return []
    top = profile.nlargest(n, "carbon_intensity_mean")
    result = []
    for _, row in top.iterrows():
        h = int(row["hour"])
        result.append(
            {
                "hour": h,
                "label": f"{h:02d}:00–{(h+1)%24:02d}:00",
                "carbon_intensity_mean": row["carbon_intensity_mean"],
            }
        )
    return result


def calculate_action_impact(
    appliance: dict,
    current_intensity: float,
    best_intensity: float,
) -> dict:
    """
    Calculate CO₂ and cost impact of shifting an appliance run to the best window.

    Args:
        appliance:         Appliance dict from a household's appliances list.
        current_intensity: Carbon intensity (gCO₂/kWh) right now.
        best_intensity:    Carbon intensity (gCO₂/kWh) in the best identified window.

    Returns:
        dict with keys:
            kwh               – appliance energy use per run
            co2_now_g         – gCO₂ if run now
            co2_best_g        – gCO₂ if shifted to best window
            co2_saved_g       – gCO₂ savings
            cost_saved_jpy    – approximate JPY savings (TEPCO residential rate ≈ ¥31/kWh)
            pct_improvement   – percentage CO₂ reduction
    """
    kwh = appliance["kwh"]
    co2_now = kwh * current_intensity          # gCO₂
    co2_best = kwh * best_intensity            # gCO₂
    co2_saved = co2_now - co2_best             # gCO₂

    # Approximate cost: carbon-aware price not available from TEPCO open data,
    # so we use a flat residential rate. This is illustrative only.
    TEPCO_RATE_JPY_PER_KWH = 31.0
    cost_saved = 0.0  # Flat-rate billing doesn't change with shift timing

    pct = (co2_saved / co2_now * 100) if co2_now > 0 else 0.0

    return {
        "kwh": kwh,
        "co2_now_g": round(co2_now, 1),
        "co2_best_g": round(co2_best, 1),
        "co2_saved_g": round(co2_saved, 1),
        "cost_saved_jpy": cost_saved,
        "pct_improvement": round(pct, 1),
    }


def get_household(household_key: str) -> dict:
    """Return a household archetype dict by key ('shibuya', 'adachi', 'setagaya')."""
    return HOUSEHOLDS[household_key]


def list_households() -> list[tuple[str, str]]:
    """Return list of (key, label) tuples for UI selectors."""
    return [(k, v["label"]) for k, v in HOUSEHOLDS.items()]
