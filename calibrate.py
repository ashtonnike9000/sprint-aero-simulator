"""
Calibrate model parameters to match real 10m split data.

Uses a coarser dt for speed, then validates with fine dt.
Run: python3 calibrate.py
"""

import numpy as np
from scipy.optimize import minimize, brentq
from athletes import ATHLETES

CD = 0.80; TEMP = 20.0; ALT = 0; INTERVAL = 10

def air_density(tc, alt):
    return 101325*(1-2.25577e-5*alt)**5.25588/(287.058*(273.15+tc))

def sim_fast(mass, ht, bw, f0k, v0, lam, alpha, cd, wind, rxn, rd=100, dt=0.002):
    """Stripped-down fast simulation for calibration (larger dt, no array storage)."""
    rho = air_density(TEMP, ALT)
    A = bw * ht * 0.95
    F0 = f0k * mass
    k = 0.5 * rho * cd
    v = 0.0; x = 0.0; t = 0.0
    vpk = 0.0; vpk_t = 0.0; vpk_x = 0.0
    # record times at 10m marks
    next_mark = INTERVAL
    cum_times = []
    velocities_at_marks = []

    while t < 16.0:
        tr = t - rxn
        if tr > 0:
            F0e = F0 * np.exp(-lam * tr)
            v0e = v0 * np.exp(-alpha * lam * tr)
            pos = min(1.0, 0.55 + 0.45 * min(tr / 1.5, 1.0))
            Ae = A * pos
            Fp = F0e * max(0.0, 1.0 - v / v0e)
            va = v - wind
            Fd = k * Ae * va * abs(va)
            a = (Fp - Fd) / mass
            v = max(0.0, v + a * dt)
            x += v * dt
            if v > vpk:
                vpk = v; vpk_t = t; vpk_x = x

        t += dt
        if x >= next_mark and next_mark <= rd:
            cum_times.append(t)
            velocities_at_marks.append(v)
            next_mark += INTERVAL
        if x > rd + 2:
            break

    ft = cum_times[-1] if len(cum_times) == rd // INTERVAL else None
    vfin = velocities_at_marks[-1] if velocities_at_marks else 0
    return ft, vpk, vpk_t, vpk_x, vfin, cum_times, velocities_at_marks

def cal_fast(mass, ht, bw, v0, lam, alpha, cd, wind, rxn, tgt):
    def obj(f0k):
        ft, *_ = sim_fast(mass, ht, bw, f0k, v0, lam, alpha, cd, wind, rxn)
        return (ft or 20) - tgt
    try:
        return brentq(obj, 3.0, 30.0, xtol=1e-4)
    except ValueError:
        return None

def seg_vels(splits):
    v = []
    for i in range(len(splits)):
        dt = splits[i] - (splits[i-1] if i > 0 else 0)
        v.append(INTERVAL / dt if dt > 0 else 0)
    return np.array(v)

def fit_athlete(name, data):
    splits = data["real_splits"]
    if splits is None:
        return None
    real_vels = seg_vels(splits)
    tgt = splits[-1]
    wind = data.get("race_wind", 0.0)
    rxn = data["real_reaction"]

    def objective(params):
        v0, lam, alpha = params
        if v0 < 10 or v0 > 16 or lam < 0.003 or lam > 0.10 or alpha < 0.05 or alpha > 0.8:
            return 1e6
        f0k = cal_fast(data["mass"], data["height"], data["bw"], v0, lam, alpha, CD, wind, rxn, tgt)
        if f0k is None:
            return 1e6
        ft, vpk, _, _, vfin, cum, _ = sim_fast(data["mass"], data["height"], data["bw"],
                                                 f0k, v0, lam, alpha, CD, wind, rxn)
        if ft is None or len(cum) < 10:
            return 1e6
        sim_vels = seg_vels(cum)
        return float(np.sqrt(np.mean((sim_vels - real_vels)**2)))

    x0 = [data["v0"], data["lam"], data["alpha"]]
    best = minimize(objective, x0, method="Nelder-Mead",
                    options={"maxiter": 800, "xatol": 0.005, "fatol": 0.002})
    return best

if __name__ == "__main__":
    print("Calibrating model parameters against real 10m splits...\n")
    print(f"{'Athlete':<24} {'v0':>5} {'lam':>7} {'alpha':>6} {'f0/kg':>6} {'RMSE':>7} {'Peak':>6} {'Drop':>6}")
    print("-" * 80)

    for name, data in ATHLETES.items():
        if data["real_splits"] is None:
            print(f"{name:<24}  (no split data — skipped)")
            continue

        result = fit_athlete(name, data)
        if result is None:
            continue

        v0, lam, alpha = result.x
        wind = data.get("race_wind", 0.0)
        rxn = data["real_reaction"]
        tgt = data["real_splits"][-1]
        f0k = cal_fast(data["mass"], data["height"], data["bw"], v0, lam, alpha, CD, wind, rxn, tgt)
        ft, vpk, vpk_t, vpk_x, vfin, cum, _ = sim_fast(
            data["mass"], data["height"], data["bw"], f0k, v0, lam, alpha, CD, wind, rxn)

        drop = vpk - vfin
        print(f"{name:<24} {v0:5.2f} {lam:7.4f} {alpha:6.3f} {f0k:6.2f} "
              f"{result.fun:7.3f} {vpk:6.2f} {drop:6.2f}")

        real_vels = seg_vels(data["real_splits"])
        sim_vels = seg_vels(cum) if len(cum) == 10 else [0]*10

        print(f"  {'Dist':>6}  {'Real':>7}  {'Sim':>7}  {'Err':>6}")
        for i, d in enumerate(range(10, 101, 10)):
            rv = real_vels[i]
            sv = sim_vels[i] if i < len(sim_vels) else 0
            print(f"  {d:>4}m  {rv:7.2f}  {sv:7.2f}  {sv-rv:+6.2f}")
        print(f"\n  → v0={v0:.2f}, lam={lam:.4f}, alpha={alpha:.3f}\n")
