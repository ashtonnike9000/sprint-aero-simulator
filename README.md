# Sprint Aerodynamic Drag Simulator

Interactive tool for estimating how aerodynamic drag coefficient (Cd) reduction affects 100m sprint performance.

**[Live App →](https://sprint-aero-simulator.streamlit.app)** *(deploy via Streamlit Community Cloud)*

## What It Does

- Models a 100m sprint using the **Hill Force-Velocity relationship** with **exponential metabolic fatigue**
- Compares two drag coefficients side-by-side (baseline vs new material)
- Shows velocity curves, time savings, drag forces, acceleration profiles, and 10m splits
- Pre-loaded with **10 athlete presets** calibrated against real timing-gate data
- Includes a **Model Validation** page comparing simulated vs actual 10m segment velocities
- **Sources** page with links to every data point for team verification

## Athletes Included

| Athlete | PB | Source Race | Split Data |
|---------|-----|------------|-----------|
| Noah Lyles | 9.79s | Paris 2024 Final | ✅ |
| Kishane Thompson | 9.79s | Paris 2024 Final | ✅ |
| Fred Kerley | 9.81s | Paris 2024 Final | ✅ |
| Kenny Bednarek | 9.88s | Paris 2024 Final | ✅ |
| Christian Coleman | 9.76s | Doha 2019 Final | ✅ |
| Usain Bolt | 9.58s | Berlin 2009 WR | ✅ |
| Sha'Carri Richardson | 10.65s | Estimated | Peak only |
| Melissa Jefferson | 10.61s | Paris 2024 Final | ✅ |
| Twanisha Terry | 10.83s | Prefontaine 2023 | ✅ |
| Florence Griffith-Joyner | 10.49s | Estimated | — |

## Physics Model

```
m · dv/dt = F_prop(v, t) − F_drag(v)

F_prop = F₀(t) · max(0, 1 − v/v₀(t))      Hill force-velocity
F₀(t) = F₀_init · exp(−λt)                 Force decay (fatigue)
v₀(t) = v₀_init · exp(−α·λ·t)              Speed ceiling decay

F_drag = ½ρ · Cd · A_eff(t) · (v − wind)²   Aerodynamic drag
```

Parameters (v₀, λ, α) are **fitted to real 10m split data** via Nelder-Mead optimization.
F₀ is auto-calibrated to match the target race time using Brent's method.

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy to Streamlit Community Cloud

1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo → select `app.py` → Deploy

## Data Sources

- **Athletes First** — 10m split databases for men's & women's 100m
- **Paris 2024 Official Results Book** — Olympic final timing data
- **World Athletics** — Biomechanics reports from World Championships
- **IAAF Berlin 2009 Report** — Bolt's 9.58 WR analysis

See the **Sources** page in the app for full citations and links.

## Model Validation

Typical fit quality: **RMSE 0.12–0.21 m/s** across all athletes with split data.
See the **Model Validation** page for per-athlete breakdowns showing simulated vs actual velocity profiles.
