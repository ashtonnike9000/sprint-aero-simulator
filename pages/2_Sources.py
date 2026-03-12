"""
Sources & References — all data origins for team validation.
"""

import streamlit as st
from athletes import ATHLETES

st.set_page_config(page_title="Sources & References", layout="wide")

st.markdown("## Sources & References")
st.markdown(
    "All athlete data, split times, and model parameters are traceable to published sources. "
    "Use the links below to verify any number in the simulator."
)

# ── Athlete Data Sources ──
st.divider()
st.subheader("Athlete Data Sources")

for name, data in ATHLETES.items():
    with st.expander(f"**{name}** — {data.get('race_label', 'N/A')}"):
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown(f"""
| Attribute | Value |
|-----------|-------|
| **Gender** | {data['gender']} |
| **Mass** | {data['mass']} kg |
| **Height** | {data['height']} m |
| **100m Time** | {data['target']}s |
| **Reaction** | {data['reaction']}s |
| **Peak Velocity** | {data.get('peak_velocity', 'N/A')} m/s |
| **Peak Location** | {data.get('peak_location', 'N/A')} |
| **Strides** | {data.get('strides') or 'N/A'} |
""")
        with col2:
            if data.get("real_splits"):
                st.markdown("**10m Cumulative Splits (s):**")
                splits = data["real_splits"]
                intervals = [splits[0]] + [splits[i] - splits[i-1] for i in range(1, len(splits))]
                rows = []
                for i, d in enumerate(range(10, 101, 10)):
                    rows.append({
                        "Distance": f"{d}m",
                        "Cumulative": f"{splits[i]:.2f}s",
                        "Interval": f"{intervals[i]:.2f}s",
                        "Avg Speed": f"{10/intervals[i]:.2f} m/s",
                    })
                st.dataframe(rows, use_container_width=True, hide_index=True)
            else:
                st.info("No published 10m splits available for this athlete.")

            if data.get("notes"):
                st.markdown(f"**Notes:** {data['notes']}")

        st.markdown("**Sources:**")
        for label, url in data.get("sources", []):
            st.markdown(f"- [{label}]({url})")

# ── Primary Data Sources ──
st.divider()
st.subheader("Primary Data Sources")
st.markdown("""
The following databases and publications were used for 10m split data:

| Source | Description | Link |
|--------|-------------|------|
| **Athletes First — Men's 100m by Athlete** | Comprehensive split database for men's 100m, updated May 2025 | [PDF](https://www.athletefirst.org/wp-content/uploads/2025/06/Mens-100m-by-athlete-20250520.pdf) |
| **Athletes First — Women's 100m by Athlete** | Comprehensive split database for women's 100m, updated March 2025 | [PDF](https://www.athletefirst.org/wp-content/uploads/2025/04/Womens-100m-by-athlete.pdf) |
| **Paris 2024 Official Results Book** | Official timing data including 10m intermediate splits for all Olympic finals | [PDF](https://www.fecodatle.com/wp-content/uploads/2024/08/R2024-Juegos-Olimpicos-Paris2024-memorias.pdf) |
| **World Athletics Biomechanics Reports** | Official biomechanics analysis from World Championships | [World Athletics](https://worldathletics.org) |
""")

# ── Model References ──
st.divider()
st.subheader("Physics Model References")
st.markdown("""
| Reference | Contribution | Link |
|-----------|-------------|------|
| **Hill, A.V. (1938)** | Force-velocity relationship of muscle contraction | [Proc. Royal Society B, 126, 136-195](https://doi.org/10.1098/rspb.1938.0050) |
| **Volkov & Lapin (1979)** | Velocity curve analysis in sprint running — basis for the acceleration/fatigue model shape | *Med Sci Sports*, 11(4), 332-337 |
| **Samozino et al. (2016)** | Sprint force-velocity profiling methodology | [Scand J Med Sci Sports, 26(6)](https://doi.org/10.1111/sms.12490) |
| **Morin & Samozino (2016)** | Interpreting sprint power-force-velocity profiles | [IJSPP, 11(2)](https://doi.org/10.1123/ijspp.2015-0638) |
| **Haugen, Breitschädel & Seiler (2019)** | Sprint mechanical variables in elite athletes: force-velocity profiles | [PLoS ONE, 14(7), e0215551](https://pubmed.ncbi.nlm.nih.gov/31339890/) |
| **Graubner & Nixdorf (2011)** | Biomechanical analysis of sprint/hurdles at 2009 IAAF WC | [New Studies in Athletics, 26(1), 19-53](https://worldathletics.org/news/news/biomechanical-analysis-of-the-sprint-and-hurd) |
| **Čoh (2019)** | Usain Bolt biomechanical model — 2D kinematics at max velocity | [FACTA UNIV. Phys Ed Sport, 17(1), 1-13](https://doi.org/10.22190/FUPES190304003C) |
| **IAAF Berlin 2009 Report** | Official biomechanics report on men's 100m WR race | [PDF (Sprint Men)](https://worldathletics.org/download/download?filename=76ade5f9-75a0-4fda-b9bf-1b30be6f60d2.pdf&urlslug=1+-+Biomechanics+Report+WC+Berlin+2009+Sprint+Men) |
| **Healy, Kenny & Harrison (2022)** | Profiling elite male 100m: vLoss = 3.3% avg across 82 elite sprinters | [J Sport Health Sci, 11(1), 75-84](https://pubmed.ncbi.nlm.nih.gov/35151419/) |
| **Tomazin, Morin et al. (2012)** | Fatigue after 100-400m treadmill sprints: MVC unchanged after 100m | [Eur J Appl Physiol, 112(3), 1027-36](https://doi.org/10.1007/s00421-011-2058-1) |
| **Nagahara & Girard (2020)** | Spatiotemporal and GRF changes during decelerated sprinting | [Scand J Med Sci Sports, 31(5)](https://pubmed.ncbi.nlm.nih.gov/33217086/) |
| **Morin et al. (2011)** | Force application technique degrades more than raw force during fatigue | [J Biomech, 44(15), 2719-23](https://doi.org/10.1016/j.jbiomech.2011.07.020) |
""")

# ── Drag Model References ──
st.divider()
st.subheader("Aerodynamic Drag References")
st.markdown("""
| Reference | Contribution |
|-----------|-------------|
| **Schlichting (1979)** | Boundary Layer Theory — cylinder drag coefficient (Cd ≈ 0.8 for bare cylinder at Re ~10⁵) |
| **Pugh (1971)** | Oxygen intake in sprint running — early estimate of 7.5% air resistance contribution |
| **Davies (1980)** | Effect of air resistance on sprint performance |
| **Arsac & Locatelli (2002)** | Modeling air resistance in sprint running — frontal area and Cd estimation |

### Key Assumptions
- **Cd = 0.80** (baseline): Bare cylinder at sprint Reynolds numbers (~2×10⁵)
- **Cd = 0.56** (new material): 30% reduction from surface texture modification
- **Frontal area**: `width × height × 0.95` (ellipse approximation of torso cross-section)
- **Air density**: ISA standard atmosphere model with temperature and altitude correction
""")

# ── Calibration Method ──
st.divider()
st.subheader("Parameter Calibration Method")
st.markdown(r"""
Model parameters (v₀, λ, α) for each athlete were optimized using **Nelder-Mead simplex** to
minimize RMSE between simulated and actual 10m segment velocities:

$$\text{RMSE} = \sqrt{\frac{1}{10}\sum_{i=1}^{10}\left(v_{\text{sim},i} - v_{\text{real},i}\right)^2}$$

For each trial set of (v₀, λ, α), the force parameter F₀ was auto-calibrated via **Brent's method**
to exactly match the athlete's total race time. This ensures the model gets both the *shape*
(from v₀, λ, α) and the *total time* (from F₀) correct.

**Typical fit quality:** RMSE = 0.12–0.21 m/s across all validated athletes
(see **Model Validation** page for per-athlete breakdowns).
""")

# ── Data Gaps ──
st.divider()
st.subheader("Known Data Gaps & Estimates")
st.markdown("""
| Item | Status |
|------|--------|
| **Sha'Carri Richardson 10m splits** | Not published for her PB (10.65s). Parameters estimated from Paris 2024 laser data (peak 11.26 m/s). |
| **Florence Griffith-Joyner splits** | No electronic 10m splits exist from 1988. Parameters estimated from race video analysis. |
| **Jefferson & Terry body mass** | Not publicly reported. Values estimated from visual comparison to athletes of similar build. |
| **Wind conditions** | Splits sourced from specific races with known wind readings. Model defaults to 0.0 m/s. |
""")
