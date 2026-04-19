# Design Process Documentation

This document tracks the design decisions, methodological considerations, and development process for the Tokyo household energy flexibility dashboard project.

---

## **Process Documentation Entry - February 16, 2026**

### **Session Goal**: Set up project skeleton

### **Activities**:

1. **Initialised repository**: Created project structure — `app.py`, `README.md`, `requirements.txt`, `src/__init__.py`, `src/analyzer.py`, `src/data_loader.py`, `src/visualizations.py`.
2. **Basic Streamlit shell**: `app.py` renders a minimal page; `data_loader.py` reads a local CSV; `analyzer.py` and `visualizations.py` are placeholder modules.
3. **Requirements baseline**: `streamlit`, `pandas`, `plotly` pinned in `requirements.txt`.

---

## **Process Documentation Entry - February 21, 2026**

### **Session Goal**: Build first working Streamlit dashboard

### **Activities**:

1. **Full dashboard build-out**: Expanded `app.py` into a multi-section app with file upload, data preview, and chart views. Added 180 lines to `app.py`, 130 to `src/analyzer.py`, 178 to `src/visualizations.py`.
2. **Created pages**: Added `pages/Overview.py` (static info page) and `pages/Time_Series.py` (column-picker time series explorer).
3. **Updated README**: Added project description, setup instructions, and usage notes.

---

## **Process Documentation Entry - February 23, 2026**

### **Session Goal**: Handle TEPCO's Japanese-header CSV format correctly

### **Activities**:

1. **Japanese header parsing**: Updated `src/data_loader.py` to handle TEPCO's Japanese-language column headers — added header detection and column renaming logic.
2. **Analyzer update**: Added column-mapping logic to `src/analyzer.py` so downstream analysis works regardless of header language.
3. **Page cleanup**: Simplified `pages/Overview.py` and `pages/Time_Series.py` to use the renamed columns.
4. **Merged PR #1** (`week-6` branch → `main`).

---

## **Process Documentation Entry - February 26, 2026**

### **Session Goal**: Replace manual CSV upload with automatic TEPCO data fetching

### **Activities**:

1. **Created `src/data_fetcher.py`**: New module that fetches the latest TEPCO generation mix CSV directly from the TEPCO website. Handles HTTP request, encoding detection, and file-like object return.
2. **Refactored `src/data_loader.py`**: Integrated fetcher; added caching via `@st.cache_data`; restructured to support both fetched and session-stored DataFrames.
3. **Streamlit config**: Added `.streamlit/config.toml` with server and theme baseline settings.
4. **Removed upload dependency**: The app no longer requires a local CSV file from the user.

---

## **Process Documentation Entry - March 15, 2026**

### **Session Goal**: Add live grid monitoring page and improve home page layout

### **Activities**:

1. **Created `pages/Current_Power.py`**: New 479-line page displaying the live TEPCO fuel mix and calculated carbon intensity. Added stacked bar chart for generation breakdown, carbon intensity gauge, and auto-refresh via `streamlit-autorefresh`.
2. **Updated `pages/Overview.py`**: Expanded to 121 lines with more detailed methodology explanation and page guide.
3. **Updated `app.py`**: Revised home page layout and sidebar structure to reflect the new multi-page architecture.
4. **Streamlit pages config**: Added `.streamlit/pages.toml` to define sidebar page ordering and icons.
5. **Added `streamlit-autorefresh`** to `requirements.txt`.

---

## **Process Documentation Entry - March 21, 2026**

### **Session Goal**: Design household segmentation feature and behavioral incentive framework for dashboard

### **Activities**:

1. **Branch management**: Created `segmentation` branch for feature development work

2. **Household archetype specification**: Finalized three ward-based household profiles with demographic justification:
   - Shibuya-ku (Central Apartment Single/Couple): Low family household share, dense housing
   - Adachi-ku (Family or Elderly Household): Higher elderly population, mixed family structures
   - Setagaya-ku (Suburban Family): Larger dwellings, family-residential character
   
   Justification grounded in 2020 Population Census (Tables 6-4, 8-1) and Tokyo Statistical Yearbook housing data

3. **Appliance category modeling**: Specified typical appliance ownership and consumption patterns per household type based on dwelling size, family structure, and Japanese energy label standards:
   - Shibuya: 6-8 kWh/day (40% shiftable) - minimal appliances, no dishwasher/EV
   - Adachi: 14-16 kWh/day (35% shiftable) - standard appliances, daytime HVAC constraints
   - Setagaya: 18-22 kWh/day (55% shiftable) - full appliance suite including EV charging

4. **Action module design pattern**: Established user-selected action scenario framework following Greenchoice timing-guidance model rather than Eneco smart-meter monitoring approach (scoping boundary confirmed by professor feedback). Appliances treated as decision inputs (user indicates intended action) rather than measurement outputs (monitored consumption).

5. **Incentive framework as design references**: Analyzed four Japanese utility demand-response programs to inform behavioral design patterns:

   - **TEPCO "節電チャレンジ" (Power-saving Challenge)**: Event-style demand response where customers achieving required participation days receive benefits exchangeable for Amazon gift cards and retailer vouchers (Tokyo Electric Power Company Holdings, 2022)
   
   - **SoftBank Power Eco-Denki app**: Gamified in-app "節電チャレンジ" with rewards convertible to PayPay points, demonstrating "small action, immediate payoff" pattern (SoftBank Corp., n.d.-a; SoftBank Corp., n.d.-b)
   
   - **Hokuriku Electric Hokuriku-link/"ほくリンク"**: App-based "節電チャレンジ" and "出かけて節電" ("save power by going out") campaigns combining participation rewards with drawings for store vouchers/gift certificates (Hokuriku Electric Power Company, 2025; Hokuriku Electric Power Company, n.d.)
   
   - **Octopus Energy Japan "節電チャレンジ"**: Customer-facing flexibility events rewarding usage shifts during peak demand periods, framed through published service terms (Octopus Energy, n.d.)

   These are treated as **design references** for UI patterns (event timing, reward framing, challenge structure), not implemented features. The goal is to demonstrate how timing guidance can be paired with incentive structures already proven in the Japanese market.

6. **UI/UX specification**: Detailed screen layouts for household selector, 24-hour load profile visualization (fixed vs. shiftable layers), timing guidance windows, action comparison calculator, and illustrative incentive tracking displays

### **Key Design Decisions**:

- **Grid mix constraint**: All three households see identical TEPCO generation mix and carbon intensity data. Segmentation reflects household structure and flexibility constraints only, not geographic energy supply differences.

- **Appliance framing**: Appliances are modeled as user-selected action scenarios ("What are you planning to do?") rather than claims about actual monitoring or disaggregation. This avoids requiring smart meter data while maintaining actionability.

- **Incentive presentation**: Reward mechanisms are shown as illustrative prototypes modeling real programs to demonstrate behavioral design principles. No actual point redemption or prize distribution is implemented.

- **Lead metric**: Environmental impact (CO₂ savings) as primary decision signal, with cost savings and percentage improvement as secondary signals

- **Behavioral patterns**: Loss-aversion framing for immediate decisions ("running now wastes X"), gain-framing for cumulative progress ("you've saved Y this week")

### **Methodology Clarifications**:

- **Out of scope**: Smart meter integration, appliance-level monitoring, load disaggregation, device signature inference
- **In scope**: Timing-based shifting guidance using real TEPCO carbon intensity data, modeled household load profiles, user-driven action scenarios
- **Data transparency**: Appliance consumption values are typical estimates based on Japanese energy standards and dwelling characteristics, not individual household measurements
- **Academic framing**: Household profiles are census-justified models, not claims about actual resident behavior

### **Deliverables**: 
Complete feature specification ready for implementation, including:
- Household archetype definitions with justification
- Appliance category breakdowns per household type
- Action module interaction patterns
- Timing guidance display logic
- Incentive framing examples with citations to reference programs

### **Next Implementation Steps**:
1. Create `src/household_profiles.py` with household and appliance data structures
2. Create new page `pages/Household_Actions.py` for action module
3. Implement carbon intensity window calculations (best/worst times)
4. Add household selector component to sidebar
5. Build action comparison calculator (now vs. optimal window)
6. Design illustrative incentive display components

### **References Added**:
- Tokyo Electric Power Company Holdings (2022) - 節電チャレンジ program structure
- SoftBank Corp. (n.d.-a, n.d.-b) - Eco-Denki app challenges
- Hokuriku Electric Power Company (2025, n.d.) - Hokuriku-link programs
- Octopus Energy (n.d.) - 節電チャレンジ service terms

---

## **Process Documentation Entry - March 26, 2026**

### **Session Goal**: Implement household segmentation and action module from March 21 design spec

### **Activities**:

1. **Created `src/household_profiles.py`**: 517-line module defining the three ward-based household archetypes (Shibuya, Adachi, Setagaya) with appliance data structures, daily consumption estimates, shiftable load percentages, and carbon intensity calculation helpers.
2. **Created `pages/Household_Actions.py`**: 520-line page with household selector, appliance picker, timing guidance windows, and action impact calculator. First working implementation of the March 21 design spec.

---

## **Process Documentation Entry - March 31, 2026**

### **Session Goal**: Refactor and fix Household Actions UI; begin process documentation

### **Activities**:

1. **Rewrote `pages/Household_Actions.py`**: Major restructure (603 changed lines) — simplified component hierarchy, fixed layout bugs, improved timing window display and CO₂ comparison calculator readability.
2. **Updated `src/household_profiles.py`**: Added missing appliance entries and corrected consumption values.
3. **Created `DESIGN_PROCESS.md`**: Wrote initial process documentation covering the March 21 design session, data source justifications, and key terminology.

---

## **Process Documentation Entry - April 12, 2026**

### **Session Goal**: UI polish pass on Household Actions page

### **Activities**:

1. **Revised `pages/Household_Actions.py`**: 326 changed lines — improved visual hierarchy, added Power-Saving Challenge section, refined timing window cards, better metric formatting.
2. **Expanded `src/household_profiles.py`**: 158 changed lines — fleshed out appliance details for all three households, added helper functions for best/worst hour calculations.
3. **Updated `.streamlit/config.toml`**: Adjusted theme colors and layout settings.

---

## **Data Sources and Justification**

This section documents the specific primary sources used to ground household archetypes and appliance consumption values.

### **Census Data (Household Composition)**

**Source**: 総務省統計局 (Statistics Bureau of Japan). *令和2年国勢調査 人口等基本集計* (2020 Population Census, Basic Complete Tabulation on Population and Households). Released 2021-11-30; ward-level data published 2022-07-22.
URL: https://www.e-stat.go.jp/stat-search/files?toukei=00200521&tstat=000001049104

**Tables cited**:
- **Table 6-4**: 一般世帯の家族類型 (General households by family type by municipality) — single-person and family household shares per ward
- **Table 8-1**: 年齢・男女別人口 (Population by age and sex) — elderly population shares

**Ward-level justification**:

| Ward | 2020 Census Population | Household Character | Profile Basis |
|---|---|---|---|
| Shibuya-ku | 243,883 | ~62% single-person households (among highest in 23 wards) | Compact apartment, single/couple |
| Adachi-ku | 695,043 | ~24% aged 65+; above-average multi-generational and elderly-only household share | Mixed family/elderly, higher daytime consumption |
| Setagaya-ku | ~917,000 | Tokyo's most populous ward; largest absolute count of family households; above-average dwelling floor area | Suburban family, larger dwelling + EV |

### **Appliance Consumption Values (METI Top Runner Programme)**

**Source**: 経済産業省 (Ministry of Economy, Trade and Industry, METI) / 省エネルギーセンター (Energy Conservation Center Japan, ECCJ). *トップランナー制度 (Top Runner Programme): Energy Conservation Act Judgment Standards.*
URL: https://www.eccj.or.jp/toprunner/

| Appliance | Standard | Benchmark | Modeled kWh/day |
|---|---|---|---|
| Room Air Conditioner (2.8 kW wall-mount) | H20.04.24 (2008), APF ≥ 6.0 | ~720 kWh/year at Tokyo Zone 6 | 1.2–4.0 kWh (varies by household) |
| Refrigerator (2-door class) | H18.07.05 (2006) | 350-L: ~290 kWh/year; 500-L: ~380 kWh/year | 1.0–1.5 kWh/day |
| Heat Pump Water Heater (EcoCute) | H24.09.11 (2012), COP ≥ 3.0 | 370-L: ~1,090 kWh/year; 460-L: ~1,300 kWh/year | 2.5–3.0 kWh/day |
| Rice Cooker | H17.06.13 (2005) | ~0.15–0.25 kWh/cook + ~0.15 kWh warm-hold (4 h) | 0.5 kWh/day |

**Note on modeling**: Actual in-use consumption of older appliance stock is typically 1.2–1.5× the Top Runner target value. Modeled values reflect this real-world usage premium, appropriate for households with pre-2020 stock appliances.

### **EV Charging Value**

Setagaya EV charge value of 6.0 kWh/session modeled as a ~20% top-up of a 40 kWh battery pack (representative: Nissan Leaf 40 kWh ZE1, the most common battery EV in the Japanese residential fleet as of 2022), equivalent to approximately 40 km of daily commute range.

---

## **Key Terminology for Academic Documentation**

When writing about this in thesis/report, use:

- **"Design references"** not "implemented features" (for incentives)
- **"Modeled household profiles"** not "actual households"
- **"Typical appliance consumption"** not "measured consumption"
- **"User-selected action scenarios"** not "monitored appliances"
- **"Illustrative incentive framework"** not "rewards system"

---

## **Process Documentation Entry - April 19, 2026**

### **Session Goal**: Dependency fix, git history cleanup, and dashboard scope reduction

### **Activities**:

1. **Fixed Pillow build failure**: `pillow==10.4.0` has no pre-built wheel for Python 3.13 and fails to compile from source. Root cause was `streamlit==1.31.0` pinning `pillow<11`. Upgraded streamlit to `>=1.40.0` (resolved to 1.56.0), which lifts the constraint and allows Pillow 11+ (which ships Python 3.13 wheels) to install without compilation.

2. **Git identity correction**: All prior commits were authored under the account `hectar-bugs / hectar@kingofthecurve.org`. Updated local git config to `hectar-glitches / hectar@gmail.com` and used `git filter-branch --env-filter` to rewrite `GIT_AUTHOR_*` and `GIT_COMMITTER_*` on all 10 commits across all 7 branches. Force-pushed all branches to remote; `main` required a `git fetch` first due to a stale remote-tracking ref.

3. **Removed Time Series page**: `pages/Time_Series.py` was a generic column-picker data explorer — a leftover from the earlier "Data Analyzer Dashboard" phase. It had no connection to carbon intensity or household timing guidance and was removed as dead weight.

4. **Rewrote Overview page**: Replaced the generic data statistics view with a purpose-driven page explaining what the app is, the core questions it answers, how carbon intensity is derived from the TEPCO fuel mix, what each page does, and what the dashboard does not claim. Uses only native Streamlit elements — no custom HTML.

5. **Simplified app.py (Home page)**: Removed CSV upload, scatter plots, column information tables, and the generic feature list. The home page now serves purely as a data loader: one "Fetch latest TEPCO data" button in the sidebar, a row count and date range display on load, and a two-card "where to go next" prompt pointing to Current Power Mix and Household Actions.

### **Key Design Decisions**:

- **CSV upload removed**: The app is scoped to live TEPCO data only. Manual CSV upload was a generic data-tool feature inconsistent with the app's purpose.
- **Time Series removed**: The two remaining pages (Current Power Mix, Household Actions) cover the full user journey. A generic time series explorer added no value for the "is now a good time?" question.
- **Overview as About page**: Kept as a static methodology and transparency page. Distinct from Home (which is functional) — Overview explains why the app works the way it does and what its limitations are.

### **Scope at end of session**:
- `app.py` — Home / data loader
- `pages/Overview.py` — About / methodology
- `pages/Current_Power.py` — Live grid mix and carbon intensity
- `pages/Household_Actions.py` — Household profiles, timing windows, action impact calculator

---

## **Design Philosophy**

This project demonstrates how publicly available grid data (TEPCO carbon intensity) can be combined with census-justified household modeling to provide actionable timing guidance for energy flexibility. The approach prioritizes:

1. **Transparency**: Clear documentation of data sources and modeling assumptions
2. **Actionability**: User-driven decisions based on environmental signals
3. **Academic rigor**: Census-grounded archetypes and cited design references
4. **Real-world relevance**: UI patterns informed by actual Japanese utility programs
5. **Appropriate scope**: Focus on timing guidance rather than monitoring claims

---

## **Capstone Work Product Evaluation - April 19, 2026**

### **Work Product**: Deployed Streamlit dashboard for Tokyo residents in Shibuya-ku, Adachi-ku, and Setagaya-ku

This section records the evaluation of the dashboard against the Capstone Work Product requirements and the scoping decisions that followed.

### **Audience**

The intended audience is residents of the three modeled wards — Shibuya-ku, Adachi-ku, and Setagaya-ku — who want to make better-timed decisions about flexible household electricity use. This is a general-public audience, not a policy or technical one. The ward framing is purposely specific: a resident who recognises their household type (single apartment, family household, or larger suburban dwelling with EV) can navigate to the matching profile and receive relevant guidance without any background knowledge. The depth of the app — appliance-level CO₂ estimates, ward-specific flexibility percentages — is appropriate for this audience because it is surfaced through plain-language comparisons ("running now vs. waiting"), not exposed as raw numbers.

### **Scoping Decisions**

**Cold-start usability — confirmed not an issue.**
The `pages/Current_Power.py` page calls `load_data()` automatically if no session data exists, meaning the app is fully functional for a user who navigates directly to any page without first pressing the home page fetch button. The manual fetch button on the home page is a convenience for forcing a data refresh, not a prerequisite for using the app. No onboarding friction was identified.

**Power-Saving Challenge persistence — explicitly out of scope.**
Persisting challenge progress across sessions requires a backend database and user authentication. This introduces hosting cost, data privacy obligations under Japanese law (Act on the Protection of Personal Information), and maintenance overhead disproportionate to the project scope. The challenge feature is intentionally framed as a behavioral design reference — demonstrating how a real utility demand-response program could be structured — rather than a live points system. This is consistent with the project's overall approach of using Japanese utility programs (TEPCO 節電チャレンジ, SoftBank Eco-Denki, Hokuriku-link, Octopus Energy Japan) as design references rather than implemented features.

**Separation of work product from process documentation.**
The deployed app contains no Minerva-specific framing (no HC/LO references, no academic citations visible to users). The academic grounding — census justification, METI Top Runner sourcing, emissions factor methodology — lives entirely in this process documentation. This separation is intentional and consistent with the Capstone Work Product requirement: the app speaks to its real-world audience; the documentation speaks to the academic evaluation.

### **Relationship to Minerva Learning**

The dashboard sits atop several areas developed across the degree:
- **Data pipeline design**: live API ingestion, caching, session state management across a multi-page app
- **Quantitative modeling**: emissions factor calculation from fuel-mix proportions, appliance energy estimates grounded in published standards
- **Behavioral design**: loss-aversion and gain-framing patterns drawn from demand-response literature and Japanese utility programs
- **Demographic grounding**: ward-level census segmentation to justify household archetypes rather than arbitrary user personas
- **Scope discipline**: deliberate decisions about what to exclude (smart meter integration, persistent tracking, CSV upload) to maintain a focused and honest work product
