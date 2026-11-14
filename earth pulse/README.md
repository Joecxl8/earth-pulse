# EARTH PULSE — Discovering Earth's Changing Patterns Through NASA Data

* **Team Name:** NOVAFLUX
* **Team Owner:** Joe Manu Thomas
* **Local Event:** Pala, India
* **Official Challenge:** *Be An Earth System Trend Detective!* (2026 NASA Space Apps Challenge)

## 1. Executive Summary & Research Question

Earth's interconnected climate system is constantly changing, yet the same global forcing can cause environmental variables to trend at vastly different rates—or even in opposite directions—depending on regional surface physics. Plotting raw numbers on a generic weather dashboard cannot separate long-term climate signals from natural year-to-year noise (such as ENSO cycles or extreme monsoon bursts).

**EARTH PULSE** is a scientific trend-detection workstation that answers the challenge's four core investigative questions (**What** is changing, **Where**, **By how much**, and **Whether the change is statistically significant**):

> **Headline Research Question:** *Over the 44-year satellite/reanalysis era (1981–2024, 528 monthly records), how do multi-decadal trends in 2 m air temperature (`T2M`, `T2M_MAX`), radiative skin temperature (`TS`), bias-corrected precipitation (`PRECTOTCORR`), and relative humidity (`RH2M`) diverge between a humid tropical monsoon foothills ecosystem (**Pala, Kerala**: `9.71°N, 76.68°E`) and an arid desert ecosystem (**Jaisalmer, Rajasthan**: `26.92°N, 70.91°E`) across Annual (`Jan–Dec`), Southwest Monsoon (`JJAS: Jun–Sep`), and Pre-Monsoon (`MAM: Mar–May`) windows?*

## 2. How EARTH PULSE Answers the 4 Challenge Questions

| Detective Question | How EARTH PULSE Solves It Scientifically | 
| ----- | ----- | 
| **1. What is changing?** | Evaluates 5 NASA MERRA-2 parameters (`T2M`, `PRECTOTCORR`, `T2M_MAX`, `TS`, `RH2M`) while enforcing strict physical guardrails between **2 m thermodynamic air temperature (`T2M`)**, **radiative Earth skin temperature (`TS`)**, **orbital MODIS LST**, and **derived vegetation indices (`NDVI`)**. | 
| **2. Where is it changing?** | Features 3 comparative case studies (*Pala, Kerala vs. Jaisalmer, Rajasthan*; *Kottayam, Kerala vs. Dammam, Saudi Arabia*; *Munnar Western Ghats vs. Kochi Coast*) plus click-anywhere global coordinate testing on a zero-dependency **HTML5 Canvas GIS & 3D Orthographic Globe Engine** displaying exact $0.5^\circ \times 0.625^\circ$ ($\sim 55\text{ km}$) MERRA-2 grid footprints. | 
| **3. By how much?** | Computes the non-parametric **Theil–Sen Robust Slope Estimator** ($\text{units/decade}$) across all $\binom{44}{2} = 946$ pairwise year combinations with **ranked 95% confidence intervals**, alongside Ordinary Least Squares (OLS) regression overlays to demonstrate how Sen's slope resists extreme outliers like the **2018 Kerala floods**. | 
| **4. Is it significant?** | Runs the **two-sided tie-corrected Mann–Kendall Trend Test** ($\alpha = 0.05$) on de-seasonalized Annual (`12-mo`), SW Monsoon (`JJAS, 4-mo`), and Pre-Monsoon (`MAM, 3-mo`) series, reporting exact $p$-values, Kendall's $\tau$, $S$-statistics, and $Z$-scores. | 

## 3. Authentic NASA Data & Space Agency Partner References

* **Primary NASA Data Pipeline:** Live **NASA Langley Research Center POWER API** (`https://power.larc.nasa.gov/api/temporal/monthly/point`) serving **NASA GMAO MERRA-2** assimilation model outputs (`1981–2024`, spatial resolution $0.5^\circ \times 0.625^\circ$).
* **Exact Calendar-Month Precipitation Conversion:** Because NASA POWER serves monthly `PRECTOTCORR` in $\text{mm/day}$, EARTH PULSE multiplies each monthly value by the exact number of calendar days in that month (accounting for leap years) before summing Annual (`Jan–Dec`), Monsoon (`JJAS`), and Pre-Monsoon (`MAM`) totals in $\text{mm}$.
* **Space Agency Partner Context (ISRO):** Contextualizes Western Ghats and Indian Southwest Monsoon (`JJAS`) hydroclimatic variability alongside **ISRO (Indian Space Research Organisation) MOSDAC & Bhuvan** meteorological and land-surface observations (`https://www.mosdac.gov.in/`).
* **Statistical Integrity:** A Mann–Kendall $p\text{-value} < 0.05$ confirms a non-random monotonic trend over 1981–2024; isolating greenhouse forcing from local irrigation or urbanization requires coupled physical attribution modeling (**correlation** $\neq$ **causation**).

## 4. Repository Structure & Quick Start

```
earth-pulse/
├── index.html                  # Complete zero-dependency NASA Space Apps web workstation
├── _headers                    # Netlify HTTP security headers configuration
├── scripts/
│   └── build_data.py           # Pure Python standard-library NASA POWER fetcher & Mann-Kendall engine
└── README.md                   # Project documentation & official Space Apps submission guide answers
```

## 5. Use of Super Intelligence (SI) & Open-Source Disclosure (Per Official Submission Guide Page 9)

* **Super Intelligence (SI) Disclosure:** In accordance with Page 9 of the *2026 NASA Space Apps Project Submission Guide*, Team NOVAFLUX discloses that **Gemini (Large Language Model)** was used as a learning mentor, statistical reference assistant, and code/UI scaffolding partner for HTML5 Canvas rendering and documentation formatting. All research questions, regional case study designs (*Pala, Kerala vs. Jaisalmer, Rajasthan*), data retrieval pipelines, and Mann–Kendall / Theil–Sen statistical calculations are grounded in authentic NASA POWER MERRA-2 datasets. No NASA logos, flags, or mission identifiers were generated or modified by SI.
* **Open-Source Libraries & Fonts:** Fira Sans, Overpass, and JetBrains Mono (SIL Open Font License via Google Fonts); Tailwind CSS (MIT License).