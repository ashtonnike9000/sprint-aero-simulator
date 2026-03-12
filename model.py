"""
Sprint simulation engine.

Hill Force-Velocity model with exponential metabolic fatigue.
    F_prop = F₀(t) · max(0, 1 − v/v₀(t))
    F₀(t) = F₀_init · exp(−λt)
    v₀(t) = v₀_init · exp(−α·λ·t)
"""

import numpy as np
from scipy.optimize import brentq


def air_density(temp_c: float, alt_m: float) -> float:
    """ISA atmosphere model."""
    T = 273.15 + temp_c
    p = 101325.0 * (1.0 - 2.25577e-5 * alt_m) ** 5.25588
    return p / (287.058 * T)


def frontal_area(width: float, height: float) -> float:
    return width * height * 0.95


def simulate(mass, height, bw, f0_kg, v0, lam, alpha,
             cd, temp_c, alt_m, wind, reaction, race_dist=100, dt=0.0004):
    """
    Run a sprint simulation.

    Returns dict with arrays (t, v, x, a, fd, fp) and scalars
    (ft, vpk, vpk_t, vpk_x, vfin, rho, A).
    """
    rho = air_density(temp_c, alt_m)
    A = frontal_area(bw, height)
    F0 = f0_kg * mass
    k_base = 0.5 * rho * cd

    n = int(16.0 / dt) + 1
    t = np.linspace(0, 16.0, n)
    v = np.zeros(n)
    x = np.zeros(n)
    acc = np.zeros(n)
    fd = np.zeros(n)
    fp = np.zeros(n)

    for i in range(1, n):
        tr = t[i] - reaction
        if tr <= 0:
            continue

        F0_eff = F0 * np.exp(-lam * tr)
        v0_eff = v0 * np.exp(-alpha * lam * tr)

        posture = min(1.0, 0.55 + 0.45 * min(tr / 1.5, 1.0))
        A_eff = A * posture

        F_prop = F0_eff * max(0.0, 1.0 - v[i-1] / v0_eff)

        v_app = v[i-1] - wind
        F_drag = k_base * A_eff * v_app * abs(v_app)

        a = (F_prop - F_drag) / mass
        v[i] = max(0.0, v[i-1] + a * dt)
        x[i] = x[i-1] + v[i] * dt
        acc[i] = a
        fd[i] = F_drag
        fp[i] = F_prop

        if x[i] > race_dist + 5:
            t = t[:i+1]; v = v[:i+1]; x = x[:i+1]
            acc = acc[:i+1]; fd = fd[:i+1]; fp = fp[:i+1]
            break

    idx = np.searchsorted(x, race_dist)
    if 0 < idx < len(x) and x[idx] != x[idx-1]:
        frac = (race_dist - x[idx-1]) / (x[idx] - x[idx-1])
        ft = t[idx-1] + frac * dt
    else:
        ft = None

    mask = x <= race_dist
    vpk = float(np.max(v[mask])) if np.any(mask) else 0
    vpk_idx = int(np.argmax(v[mask])) if np.any(mask) else 0
    vpk_t = float(t[vpk_idx])
    vpk_x = float(x[vpk_idx])
    vfin = float(v[idx-1]) if 0 < idx < len(v) else 0

    return dict(t=t, v=v, x=x, a=acc, fd=fd, fp=fp,
                ft=ft, vpk=vpk, vpk_t=vpk_t, vpk_x=vpk_x, vfin=vfin,
                rho=rho, A=A)


def calibrate_f0(mass, height, bw, v0, lam, alpha,
                 cd, temp_c, alt_m, wind, reaction, target, race_dist=100):
    """Find f0_kg so the simulation finishes in target seconds."""
    def obj(f0k):
        r = simulate(mass, height, bw, f0k, v0, lam, alpha,
                     cd, temp_c, alt_m, wind, reaction, race_dist)
        return (r["ft"] or 20) - target
    try:
        return brentq(obj, 3.0, 30.0, xtol=1e-5)
    except ValueError:
        return None


def splits_at_distances(result, distances):
    """Interpolate cumulative time & instantaneous velocity at given distances."""
    times = np.interp(distances, result["x"], result["t"])
    vels = np.interp(times, result["t"], result["v"])
    return times, vels


def segment_velocities(cumulative_splits, interval=10):
    """Convert cumulative split times to average segment velocities."""
    vels = []
    for i in range(len(cumulative_splits)):
        dt = cumulative_splits[i] - (cumulative_splits[i-1] if i > 0 else 0)
        vels.append(interval / dt if dt > 0 else 0)
    return vels
