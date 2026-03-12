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
        fatigue_pct=20, reaction=0.150, target=10.50, gender="M",
        race_wind=0.0))

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
                             help="Internal force-capacity decay over the race duration. "
                                  "This is NOT the same as observable speed loss — elite sprinters "
                                  "only lose 2-5% of peak speed (Healy et al., 2022, n=82), but the "
                                  "underlying force capacity decays more because the Hill F-V "
                                  "relationship buffers the effect. "
                                  "Preset values are calibrated to real split data.")
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
    wind = st.slider("Race-day wind (m/s)", -5.0, 5.0,
                      float(p.get("race_wind", 0.0)), 0.1,
                      help="+tail / -head. IAAF record limit: +2.0. "
                           "Defaults to the wind from the athlete's reference race. "
                           "Changing this lets you see how the material comparison "
                           "plays out in different wind conditions — the athlete's "
                           "strength stays fixed.")

    st.divider()
    race_dist = st.selectbox("Race distance (m)", [60, 100, 200], index=1)

# ── Calibrate F0 using the ORIGINAL race conditions ──
# The athlete's muscles don't change with wind — F0 is locked to the
# conditions under which they actually ran their target time.
cal_wind = float(p.get("race_wind", 0.0))
f0k = calibrate_f0(mass, ht, bw, v0, lam, alpha, cd_base, temp_c, alt_m, cal_wind, reaction, target, race_dist)
if f0k is None:
    f0k = 8.0
    st.sidebar.warning("Calibration failed — using default force.")

# ── Simulate both materials under the user-selected wind ──
rb = simulate(mass, ht, bw, f0k, v0, lam, alpha, cd_base, temp_c, alt_m, wind, reaction, race_dist)
rn = simulate(mass, ht, bw, f0k, v0, lam, alpha, cd_new, temp_c, alt_m, wind, reaction, race_dist)

ftb = rb["ft"]; ftn = rn["ft"]
saved = (ftb - ftn) if ftb and ftn else 0
pct = saved / ftb * 100 if ftb else 0

# ── Header ──
st.markdown("## Sprint Aerodynamic Drag Simulator")
sel_label = f"**{preset}** — " if preset != "Custom" else ""
wind_note = f"Wind {wind:+.1f} m/s"
if abs(cal_wind - wind) > 0.05:
    wind_note += f" (calibrated at {cal_wind:+.1f})"
st.markdown(
    f"{sel_label}Cd {cd_base:.2f} to {cd_new:.2f} ({cd_pct:.0f}% reduction) | "
    f"Air density {rb['rho']:.3f} kg/m3 | Frontal area {rb['A']:.3f} m2 | "
    f"{wind_note}"
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
### 1. Equation of Motion

$$m \frac{dv}{dt} = F_{\text{prop}}(v, t) \;-\; F_{\text{drag}}(v)$$

**What it is:** Newton's second law applied to a sprinter. At every instant, the athlete's
acceleration equals the net force (propulsion minus drag) divided by body mass.

**Why it makes sense:** A sprinter is essentially a force battle. Their muscles push them
forward, air resistance pushes back. Whoever is "winning" at any moment determines whether
the athlete is speeding up or slowing down. This is the governing equation that the
simulator solves thousands of times per second to build the full velocity curve.

---

### 2. Propulsive Force — Hill Force-Velocity Relationship

$$F_{\text{prop}} = F_0(t) \cdot \max\!\left(0,\; 1 - \frac{v}{v_0(t)}\right)$$

| Symbol | What it is |
|--------|-----------|
| $F_0(t)$ | Maximum force the athlete can produce at zero speed (like pushing off the blocks) |
| $v_0(t)$ | Theoretical max speed if there were no drag and no fatigue |
| $v$ | Current speed |

**What it is:** The Hill equation is a foundational model from muscle physiology (A.V. Hill, 1938).
It says that the faster a muscle is already contracting, the less additional force it can produce.
At zero speed (blocks), force is maximal. As the athlete approaches top speed, the force they
can apply to the ground drops toward zero.

**Why it makes sense:** Think of pedaling a bike — in a low gear (slow), you can push hard.
In a high gear (fast), you can barely push at all. Muscles work the same way. This is why
sprinters accelerate explosively out of the blocks but the rate of speed gain tapers off
as they approach top speed. The force doesn't just vanish at some arbitrary point — it
*continuously* decreases as speed builds, which matches what we see in real sprint data.

---

### 3. Metabolic Fatigue — Why Athletes Slow Down

$$F_0(t) = F_{0,\text{init}} \cdot e^{-\lambda t}$$
$$v_0(t) = v_{0,\text{init}} \cdot e^{-\alpha \lambda t}$$

| Symbol | What it is |
|--------|-----------|
| $\lambda$ | Fatigue rate — how fast the athlete's force-velocity capacity decays |
| $\alpha$ | Speed-ceiling decay factor — how much the speed ceiling drops relative to force |

**What it is:** Over the course of a 100m, the athlete's phosphocreatine (PCr) stores deplete
and hydrogen ions accumulate in the muscles. We model this as an exponential decay of both
the maximum force ($F_0$) and the theoretical max speed ($v_0$) the athlete can produce.

**Why it makes sense:** Every 100m race shows the same pattern: explosive acceleration,
a peak around 50-70m, then a slight slowdown to the finish. Even Usain Bolt slowed down in the
last 20m of his 9.58 world record.

**What the research says about 100m fatigue:**

- **Observable speed loss is small.** Healy et al. (2022) studied 82 elite male sprinters
  (9.58-10.59s) and found average speed loss from peak to finish of just **3.3% +/- 1.2%**.
  Bolt shows ~1.8%, most Olympic finalists show 2-4%.

- **Maximal voluntary force is NOT impaired after a 100m.** Tomazin, Morin et al. (2012)
  measured neuromuscular function before and after 100m, 200m, and 400m treadmill sprints.
  MVC (knee extensor torque) was unchanged after the 100m — force loss was only detectable
  after the 400m. This suggests the 100m deceleration is not caused by raw strength loss.

- **What DOES cause the slowdown?** Nagahara & Girard (2020) found that during deceleration,
  propulsive force drops ~3.5%, stride frequency drops ~3.5%, but *net anteroposterior force*
  drops ~64%. The issue is the athlete's ability to **apply force horizontally at high speed**
  — a coordination/technique degradation, not a strength deficit. Morin & Samozino showed
  that "force application technique" (the ratio of horizontal to total force) deteriorates
  far more (~19%) than total force production (~6%) during fatigue.

**How our model handles this:** The exponential decay of both $F_0$ and $v_0$ is a
*lumped approximation* — it doesn't distinguish between raw force loss, speed-ceiling
reduction, and coordination breakdown. But the combined effect correctly reproduces the
observed 2-5% speed decline because the Hill F-V relationship buffers the parameter decay:
even a ~16-20% internal capacity loss translates to only ~2-4% speed loss, since slowing
slightly lets the athlete apply more force at the lower speed.

**The fatigue slider** controls this internal capacity decay:

$$\text{fatigue \%} = \left(1 - e^{-\lambda \cdot T_{\text{race}}}\right) \times 100$$

The preset values (16-27%) are calibrated against real split data. The actual speed loss
you'll see in the dashboard metrics (the "End-Race Drop" number) matches the 2-5% range
from the literature.

---

### 4. Aerodynamic Drag — The Force We're Trying to Reduce

$$F_{\text{drag}} = \tfrac{1}{2}\,\rho \cdot C_d \cdot A_{\text{eff}}(t) \cdot (v - v_{\text{wind}})^2$$

| Symbol | What it is |
|--------|-----------|
| $\rho$ | Air density (kg/m3) — depends on temperature and altitude |
| $C_d$ | Drag coefficient — how "slippery" the shape/surface is (this is what the material changes) |
| $A_{\text{eff}}(t)$ | Effective frontal area — how much body surface the air "sees" head-on |
| $v - v_{\text{wind}}$ | Speed relative to the air (tailwind reduces it, headwind increases it) |

**What it is:** The standard aerodynamic drag equation from fluid dynamics. The force of air
resistance grows with the *square* of speed — so at 12 m/s it's four times larger than at 6 m/s.

**Why it makes sense:** Drag matters more and more as the athlete gets faster. In the first
10m (low speed), drag is negligible — maybe 2-3 N. By 60m (near peak speed of ~12 m/s),
drag reaches 30-50 N depending on the athlete's size. That's equivalent to running with a
3-5 kg weight pulling you back. Because of the squared relationship, even a modest Cd
reduction (0.80 to 0.56 = 30%) meaningfully reduces the drag force at top speed, which is
exactly where races are won and lost.

**Frontal area ramp:** The model also accounts for the athlete's posture change — they start
in a crouch (blocks, ~55% of full frontal area) and rise to upright running posture over
the first ~1.5 seconds. This means drag grows not just from speed but also from the body
"unfolding" into the wind.

---

### 5. Air Density — Why Altitude and Temperature Matter

$$\rho = \frac{p}{R \cdot T}$$

where pressure $p$ follows the ISA standard atmosphere model adjusted for altitude,
$R$ = 287.058 J/(kg K), and $T$ is absolute temperature.

**Why it makes sense:** Thinner air means less drag. Mexico City (2,240m altitude) has air
density ~20% lower than sea level, which is one reason sprint times tend to be faster at
altitude. Hot days also reduce air density slightly. The simulator accounts for both so you
can model different race venues realistically.

---

### 6. Calibration — Tying the Model to Real Data

Model parameters ($v_0$, $\lambda$, $\alpha$) for each athlete preset are optimized against
**real 10m timing-gate data** using Nelder-Mead optimization — the algorithm adjusts the
parameters until the simulated velocity at each 10m mark matches the actual data as closely
as possible.

Once those shape parameters are set, the force parameter $F_0$ is auto-calibrated using
**Brent's root-finding method** to exactly match the athlete's best race time.

**Why this two-step approach:** The shape parameters ($v_0$, $\lambda$, $\alpha$) control
*how* the athlete runs — their acceleration curve, where they peak, how much they fade.
The force parameter ($F_0$) controls *how fast* they go overall. By fitting shape first
(to split data) and then scaling force (to total time), we get a model that reproduces both
the *profile* and the *result* of a real race. Typical fit quality is RMSE 0.12-0.21 m/s
across all validated athletes (see the **Model Validation** page).

---

### 7. Why This Matters for Material Testing

The key insight: **the same model runs twice** — once with the baseline Cd (bare cylinder,
0.80) and once with the new material Cd (0.56). Everything else stays identical. So the
time difference isolates the effect of the material alone.

Because the model captures realistic sprint dynamics (acceleration phase where drag barely
matters, peak speed phase where drag is highest, deceleration phase where reduced drag
extends the athlete's ability to maintain speed), the estimated time savings are
physically grounded rather than just a back-of-envelope percentage.
    """)
