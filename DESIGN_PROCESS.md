# Design Process Documentation

This document tracks the design decisions, methodological considerations, and development process for the Tokyo household energy flexibility dashboard project.

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

## **Key Terminology for Academic Documentation**

When writing about this in thesis/report, use:

- **"Design references"** not "implemented features" (for incentives)
- **"Modeled household profiles"** not "actual households"
- **"Typical appliance consumption"** not "measured consumption"
- **"User-selected action scenarios"** not "monitored appliances"
- **"Illustrative incentive framework"** not "rewards system"
- **"Census-justified archetypes"** not "representative samples"

This maintains academic honesty while showing understanding of real-world behavioral design patterns.

---

## **Design Philosophy**

This project demonstrates how publicly available grid data (TEPCO carbon intensity) can be combined with census-justified household modeling to provide actionable timing guidance for energy flexibility. The approach prioritizes:

1. **Transparency**: Clear documentation of data sources and modeling assumptions
2. **Actionability**: User-driven decisions based on environmental signals
3. **Academic rigor**: Census-grounded archetypes and cited design references
4. **Real-world relevance**: UI patterns informed by actual Japanese utility programs
5. **Appropriate scope**: Focus on timing guidance rather than monitoring claims
