"""
Sprint Aerodynamic Drag Simulator — Main Page
"""

import math
import streamlit as st
import numpy as np
import plotly.graph_objects as go
from model import simulate, calibrate_f0
from athletes import ATHLETES, ATHLETE_NAMES

st.set_page_config(page_title="Sprint Aero Drag Simulator", page_icon="wind_blowing_face",
                   layout="wide", initial_sidebar_state="expanded")

C_BLUE = "#3B82F6"; C_RED = "#EF4444"; C_GREEN = "#22C55E"
C_AMBER = "#F59E0B"; C_GRAY = "#94A3B8"

PL = dict(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
          plot_bgcolor="rgba(15,23,42,0.8)", font=dict(family="Calibri, sans-serif"),
          legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
          margin=dict(l=60, r=30, t=50, b=60), height=520)


def fatigue_to_lam(fatigue_pct, race_time, reaction):
    """Convert user-facing fatigue % to internal lambda parameter."""
    T = max(race_time - reaction, 4.0)
    clamped = min(max(fatigue_pct, 1), 60)
    return -math.log(1.0 - clamped / 100.0) / T


# ── Sidebar ──
with st.sidebar:
    st.title("Sprint Aero Simulator")
    st.caption("Hill F-V model with metabolic fatigue — calibrated to real split data")

    st.divider()
    names = ATHLETE_NAMES + ["Custom"]
    preset = st.selectbox("Athlete Preset", names)
    p = ATHLETES.get(preset, dict(
        mass=70, height=1.75, bw=0.37, v0=12.5, lam=0.025, alpha=0.40,
        fatigue_pct=20, reaction=0.150, target=10.50, gender="M"))

    st.divider()
    st.subheader("Athlete")
    mass = st.slider("Mass (kg)", 40.0, 120.0, float(p["mass"]), 0.5)
    ht = st.slider("Height (m)", 1.40, 2.10, float(p["height"]), 0.01)
    bw = st.slider("Body width (m)", 0.25, 0.50, float(p["bw"]), 0.01)

    st.divider()
    st.subheader("Sprint Profile")
    target = st.slider("Fastest 100m time (s)", 9.00, 14.00, float(p["target"]), 0.01,
                        help="The athlete's current best 100m. The model calibrates to this.")
    fatigue_pct = st.slider("End-race fatigue (%)", 5, 45, int(p["fatigue_pct"]), 1,
                             help="How much force capacity the athlete loses by the finish. "
                                  "15-18% = elite male (minimal fade). "
                                  "20-25% = moderate. "
                                  "30%+ = heavy end-race slowdown.")
    reaction = st.slider("Reaction time (s)", 0.100, 0.300, float(p["reaction"]), 0.001)

    with st.expander("Advanced"):
        v0 = st.slider("Max muscle speed (m/s)", 10.0, 16.0, float(p["v0"]), 0.1,
                        help="Theoretical max speed with fresh muscles and no drag. "
                             "Set by calibration for presets. Higher = more room for drag to matter.")
        alpha = st.slider("Speed-ceiling decay factor", 0.20, 0.60, float(p.get("alpha", 0.40)), 0.01,
                           help="Controls how the speed ceiling drops relative to force. "
                                "Higher = more visible deceleration in the velocity curve.")

    lam = fatigue_to_lam(fatigue_pct, target, reaction)

    st.divider()
    st.subheader("Material & Drag")
    cd_base = st.slider("Cd — baseline", 0.40, 1.20, 0.80, 0.01)
    cd_new = st.slider("Cd — new material", 0.20, 1.00, 0.56, 0.01)
    cd_pct = (cd_base - cd_new) / cd_base * 100

    st.divider()
    st.subheader("Environment")
    temp_c = st.slider("Temperature (C)", -10.0, 45.0, 20.0, 0.5)
    alt_m = st.slider("Altitude (m)", 0, 2500, 0, 50)
    wind = st.slider("Wind (m/s)", -5.0, 5.0, 0.0, 0.1,
                      help="+tail / -head. IAAF record limit: +2.0")

    st.divider()
    race_dist = st.selectbox("Race distance (m)", [60, 100, 200], index=1)

# ── Simulate ──
f0k = calibrate_f0(mass, ht, bw, v0, lam, alpha, cd_base, temp_c, alt_m, wind, reaction, target, race_dist)
if f0k is None:
    f0k = 8.0
    st.sidebar.warning("Calibration failed — using default force.")

rb = simulate(mass, ht, bw, f0k, v0, lam, alpha, cd_base, temp_c, alt_m, wind, reaction, race_dist)
rn = simulate(mass, ht, bw, f0k, v0, lam, alpha, cd_new, temp_c, alt_m, wind, reaction, race_dist)

ftb = rb["ft"]; ftn = rn["ft"]
saved = (ftb - ftn) if ftb and ftn else 0
pct = saved / ftb * 100 if ftb else 0

# ── Header ──
st.markdown("## Sprint Aerodynamic Drag Simulator")
sel_label = f"**{preset}** — " if preset != "Custom" else ""
st.markdown(
    f"{sel_label}Cd {cd_base:.2f} to {cd_new:.2f} ({cd_pct:.0f}% reduction) | "
    f"Air density {rb['rho']:.3f} kg/m3 | Frontal area {rb['A']:.3f} m2 | "
    f"Wind {wind:+.1f} m/s"
)

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Baseline", f"{ftb:.3f}s" if ftb else "--")
c2.metric("New Material", f"{ftn:.3f}s" if ftn else "--")
c3.metric("Time Saved", f"{saved*1000:.1f} ms", f"{pct:.2f}%")
c4.metric("Peak Speed", f"{rb['vpk']:.2f} m/s", f"{rb['vpk']*2.237:.1f} mph")
c5.metric("Speed @ Finish", f"{rb['vfin']:.2f} m/s")
drop = rb["vpk"] - rb["vfin"]
c6.metric("End-Race Drop", f"-{drop:.2f} m/s", f"-{drop/rb['vpk']*100:.1f}%" if rb["vpk"] else "")

st.divider()

# ── Tabs ──
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Velocity vs Time", "Velocity vs Distance",
    "Time Savings", "Drag Force", "Acceleration", "Splits",
])

tlim = (ftb or 12) + 0.5

with tab1:
    fig = go.Figure()
    mb = rb["t"] <= tlim; mn = rn["t"] <= tlim
    fig.add_trace(go.Scatter(x=rb["t"][mb], y=rb["v"][mb],
                              name=f"Baseline (Cd={cd_base})", line=dict(color=C_BLUE, width=2.5)))
    fig.add_trace(go.Scatter(x=rn["t"][mn], y=rn["v"][mn],
                              name=f"New (Cd={cd_new})", line=dict(color=C_RED, width=2.5, dash="dash")))
    pi = np.argmax(rb["v"][mb])
    fig.add_trace(go.Scatter(x=[rb["t"][mb][pi]], y=[rb["v"][mb][pi]],
                              mode="markers+text",
                              text=[f"Peak: {rb['v'][mb][pi]:.2f} m/s"],
                              textposition="top center", marker=dict(color=C_AMBER, size=10),
                              showlegend=False))
    if ftb: fig.add_vline(x=ftb, line_dash="dot", line_color=C_BLUE, opacity=0.3,
                           annotation_text=f"{ftb:.3f}s")
    if ftn: fig.add_vline(x=ftn, line_dash="dot", line_color=C_RED, opacity=0.3,
                           annotation_text=f"{ftn:.3f}s")
    fig.update_layout(title="Velocity vs Time", xaxis_title="Time (s)",
                       yaxis_title="Velocity (m/s)", **PL)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    fig = go.Figure()
    mb2 = rb["x"] <= race_dist * 1.01; mn2 = rn["x"] <= race_dist * 1.01
    fig.add_trace(go.Scatter(x=rb["x"][mb2], y=rb["v"][mb2],
                              name="Baseline", line=dict(color=C_BLUE, width=2.5)))
    fig.add_trace(go.Scatter(x=rn["x"][mn2], y=rn["v"][mn2],
                              name="New material", line=dict(color=C_RED, width=2.5, dash="dash")))
    pkx = rb["x"][mb2][np.argmax(rb["v"][mb2])]
    fig.add_vline(x=pkx, line_dash="dot", line_color=C_AMBER, opacity=0.4,
                   annotation_text=f"Peak @ {pkx:.0f}m")
    fig.update_layout(title="Velocity vs Distance", xaxis_title="Distance (m)",
                       yaxis_title="Velocity (m/s)", **PL)
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    dp = np.arange(0, race_dist + 0.5, 0.5)
    tb_d = np.interp(dp, rb["x"], rb["t"])
    tn_d = np.interp(dp, rn["x"], rn["t"])
    cms = (tb_d - tn_d) * 1000
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dp, y=cms, name="Time saved",
                              line=dict(color=C_GREEN, width=3),
                              fill="tozeroy", fillcolor="rgba(34,197,94,0.15)"))
    for dm in [10, int(race_dist/2), race_dist]:
        if dm <= race_dist:
            ii = np.argmin(np.abs(dp - dm))
            fig.add_annotation(x=dm, y=cms[ii], text=f"<b>{cms[ii]:.0f} ms</b><br>at {dm}m",
                                showarrow=True, arrowhead=2, ax=-40, ay=-30, font=dict(size=12))
    fig.update_layout(title="Cumulative Time Savings", xaxis_title="Distance (m)",
                       yaxis_title="Time Saved (ms)", **PL)
    fig.update_yaxes(rangemode="tozero")
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    dd = np.linspace(0, race_dist, 500)
    tdb = np.interp(dd, rb["x"], rb["t"]); tdn = np.interp(dd, rn["x"], rn["t"])
    fdb = np.interp(tdb, rb["t"], rb["fd"]); fdn = np.interp(tdn, rn["t"], rn["fd"])
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dd, y=fdb, name=f"Drag Cd={cd_base}", line=dict(color=C_BLUE, width=2.5)))
    fig.add_trace(go.Scatter(x=dd, y=fdn, name=f"Drag Cd={cd_new}", line=dict(color=C_RED, width=2.5, dash="dash")))
    fig.add_trace(go.Scatter(x=np.concatenate([dd, dd[::-1]]),
                              y=np.concatenate([fdb, fdn[::-1]]),
                              fill="toself", fillcolor="rgba(34,197,94,0.12)",
                              line=dict(width=0), name="Drag saved"))
    fig.update_layout(title="Drag Force", xaxis_title="Distance (m)",
                       yaxis_title="Force (N)", **PL)
    fig.update_yaxes(rangemode="tozero")
    st.plotly_chart(fig, use_container_width=True)

with tab5:
    fig = go.Figure()
    mt_b = rb["t"] <= tlim; mt_n = rn["t"] <= tlim
    fig.add_trace(go.Scatter(x=rb["t"][mt_b], y=rb["a"][mt_b], name="Baseline",
                              line=dict(color=C_BLUE, width=2)))
    fig.add_trace(go.Scatter(x=rn["t"][mt_n], y=rn["a"][mt_n], name="New material",
                              line=dict(color=C_RED, width=2, dash="dash")))
    fig.add_hline(y=0, line_dash="dot", line_color=C_GRAY, opacity=0.5)
    fig.update_layout(title="Acceleration (negative = decelerating from fatigue)",
                       xaxis_title="Time (s)", yaxis_title="Acceleration (m/s2)", **PL)
    st.plotly_chart(fig, use_container_width=True)
    st.info("When acceleration goes **negative**, the athlete's fatiguing muscles "
            "can no longer overcome drag. With reduced Cd, the crossover happens later.")

with tab6:
    dists = list(range(10, int(race_dist)+1, 10))
    rows = []
    for d in dists:
        tbd = float(np.interp(d, rb["x"], rb["t"]))
        tnd = float(np.interp(d, rn["x"], rn["t"]))
        vbd = float(np.interp(tbd, rb["t"], rb["v"]))
        vnd = float(np.interp(tnd, rn["t"], rn["v"]))
        rows.append({"Distance": f"{d}m", "Baseline": f"{tbd:.3f}s", "New": f"{tnd:.3f}s",
                      "Saved": f"{(tbd-tnd)*1000:.1f} ms",
                      "Speed (base)": f"{vbd:.2f} m/s ({vbd*2.237:.1f} mph)",
                      "Speed (new)": f"{vnd:.2f} m/s ({vnd*2.237:.1f} mph)"})
    st.dataframe(rows, use_container_width=True, hide_index=True)

# ── Model Info ──
st.divider()
with st.expander("Model Details & Equations"):
    st.markdown(r"""
### Equation of Motion
$$m \frac{dv}{dt} = F_{\text{prop}}(v, t) \;-\; F_{\text{drag}}(v)$$

### Propulsive Force -- Hill F-V with Metabolic Fatigue
$$F_{\text{prop}} = F_0(t) \cdot \max\!\left(0,\; 1 - \frac{v}{v_0(t)}\right)$$
$$F_0(t) = F_{0,\text{init}} \cdot e^{-\lambda t} \qquad v_0(t) = v_{0,\text{init}} \cdot e^{-\alpha \lambda t}$$

The "End-race fatigue %" slider controls how much force capacity is lost by the finish:
$$\text{fatigue \%} = \left(1 - e^{-\lambda \cdot T_{\text{race}}}\right) \times 100$$

### Aerodynamic Drag
$$F_{\text{drag}} = \tfrac{1}{2}\,\rho \cdot C_d \cdot A_{\text{eff}}(t) \cdot (v - v_{\text{wind}})^2$$

### Calibration
Model parameters are fit to **real 10m split data** from World Athletics
and the Athletes First database (see the **Model Validation** page). The force parameter
is auto-calibrated to match the athlete's best race time.
    """)
