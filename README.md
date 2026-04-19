# Tokyo Power Consumption Analyzer

A Streamlit dashboard that shows Tokyo residents when to shift flexible household electricity tasks to lower-carbon windows, using live TEPCO generation mix data.

## What it does

The app answers two questions:

1. **How carbon-intensive is the Tokyo grid right now?** — based on the live TEPCO fuel mix (nuclear, solar, gas, coal, hydro, etc.)
2. **When is the cleanest window today to run a flexible appliance?** — calculated per household type using the same carbon intensity data

## Pages

| Page | Purpose |
|---|---|
| Home | Fetches latest TEPCO data; shows where to go next |
| Current Power Mix | Live fuel breakdown, carbon intensity gauge, auto-refreshes every 60 s |
| Household Actions | Household profile selector, appliance picker, best/worst timing windows, CO2 impact calculator, Power-Saving Challenge reference |
| Overview | About page — methodology, data sources, caveats |

## Household profiles

Three ward-based archetypes grounded in 2020 Population Census data:

| Profile | Ward | Daily consumption | Shiftable load |
|---|---|---|---|
| Central Apartment | Shibuya-ku | 6-8 kWh | 40% |
| Family / Elderly Household | Adachi-ku | 14-16 kWh | 35% |
| Suburban Family | Setagaya-ku | 18-22 kWh | 55% |

Appliance consumption values are based on METI Top Runner Programme standards, not monitored data.

## Setup

```bash
pip install -r requirements.txt
streamlit run app.py
```

Requires Python 3.10+. Tested on Python 3.13 (macOS ARM).

## Data source

TEPCO publishes daily generation mix CSV files at:
https://www.tepco.co.jp/forecast/html/area_jukyu-j.html

`src/data_fetcher.py` fetches the latest file automatically on first load. No manual download or CSV upload is needed.

## Structure

```
app.py                     # Home / data loader
pages/
    Current_Power.py       # Live grid mix and carbon intensity
    Household_Actions.py   # Household profiles, timing guidance, impact calculator
    Overview.py            # About / methodology
src/
    data_fetcher.py        # Fetches TEPCO CSV from source
    data_loader.py         # Parsing, caching, session state
    household_profiles.py  # Ward archetypes and appliance data
    analyzer.py            # Carbon intensity calculations
    visualizations.py      # Shared chart helpers
requirements.txt
DESIGN_PROCESS.md          # Full design and methodology documentation
```

## Requirements

```
streamlit>=1.40.0
pandas==2.2.0
plotly==5.18.0
streamlit-autorefresh==1.0.1
```
