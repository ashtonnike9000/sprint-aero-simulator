"""
Athlete presets with sourced biometric and race data.

Each preset contains:
  - Physical: mass, height, body width (for frontal area)
  - Model params: v0, lam, alpha (calibrated to match real split profiles)
  - fatigue_pct: user-facing fatigue slider value (% force lost by finish)
  - Race data: real 10m cumulative splits, reaction time, wind, event details
  - Sources: URLs and citations

Model parameters were fit by minimizing RMSE between simulated and actual
10m segment velocities, with f0_kg auto-calibrated to match total race time.
"""

import math

def _fatigue_pct(lam, target, reaction):
    """Derive user-facing fatigue % from internal lambda."""
    return round((1 - math.exp(-lam * (target - reaction))) * 100)


ATHLETES = {

    # ──────────────────────────────────────────────
    # MEN
    # ──────────────────────────────────────────────

    "Noah Lyles": dict(
        gender="M",
        mass=77.0, height=1.80, bw=0.38,
        v0=13.62, lam=0.0218, alpha=0.417,
        fatigue_pct=19,  # _fatigue_pct(0.0218, 9.79, 0.178)
        reaction=0.178,
        target=9.79,
        race_label="Paris 2024 Olympics Final",
        race_date="2024-08-04",
        race_wind=1.0,
        real_splits=[1.95, 2.98, 3.90, 4.76, 5.61, 6.44, 7.26, 8.09, 8.93, 9.79],
        real_reaction=0.178,
        peak_velocity=12.20,
        peak_location="60-70m",
        strides=44.0,
        notes="Characteristic slow starter with exceptional closing speed (60-90m). "
              "Olympic gold by 0.005s over Thompson. Works with biomechanist Ralph Mann.",
        sources=[
            ("World Athletics Profile", "https://worldathletics.org/athletes/_/14536762"),
            ("Paris 2024 Results Book (splits)", "https://www.fecodatle.com/wp-content/uploads/2024/08/R2024-Juegos-Olimpicos-Paris2024-memorias.pdf"),
            ("Athletes First Split Database", "https://www.athletefirst.org/wp-content/uploads/2025/06/Mens-100m-by-athlete-20250520.pdf"),
            ("Newsweek — Nike/Eaton velocity analysis", "https://www.newsweek.com/noah-lyles-100m-olympics-data-how-win-1934533"),
        ],
    ),

    "Kishane Thompson": dict(
        gender="M",
        mass=85.0, height=1.85, bw=0.40,
        v0=13.29, lam=0.0194, alpha=0.404,
        fatigue_pct=17,
        reaction=0.176,
        target=9.79,
        race_label="Paris 2024 Olympics Final",
        race_date="2024-08-04",
        race_wind=1.0,
        real_splits=[1.90, 2.93, 3.84, 4.72, 5.56, 6.41, 7.24, 8.07, 8.92, 9.79],
        real_reaction=0.176,
        peak_velocity=12.05,
        peak_location="60-80m",
        strides=None,
        notes="Silver medal Paris 2024, lost by 0.005s. Strong mid-race speed, "
              "sustained peak from 60-80m. PB 9.75 at 2025 Jamaican Trials.",
        sources=[
            ("World Athletics Profile", "https://worldathletics.org/athletes/-/14738009"),
            ("Paris 2024 Results Book", "https://www.fecodatle.com/wp-content/uploads/2024/08/R2024-Juegos-Olimpicos-Paris2024-memorias.pdf"),
            ("Athletes First Split DB (Xiamen 2023)", "https://athletefirst.org/wp-content/uploads/2023/10/M100m-by-meeting-Sep-23.pdf"),
            ("Wikipedia", "https://en.wikipedia.org/wiki/Kishane_Thompson"),
        ],
    ),

    "Fred Kerley": dict(
        gender="M",
        mass=93.0, height=1.91, bw=0.42,
        v0=13.44, lam=0.0211, alpha=0.401,
        fatigue_pct=19,
        reaction=0.108,
        target=9.81,
        race_label="Paris 2024 Olympics Final",
        race_date="2024-08-04",
        race_wind=1.0,
        real_splits=[1.87, 2.92, 3.85, 4.73, 5.58, 6.41, 7.25, 8.09, 8.94, 9.81],
        real_reaction=0.108,
        peak_velocity=12.05,
        peak_location="50-60m",
        strides=43.0,
        notes="Bronze medal Paris 2024. Exceptionally fast reaction (0.108s, fastest in field). "
              "PB 9.76s (2022 USA Champs). Tall power sprinter.",
        sources=[
            ("World Athletics Profile", "https://worldathletics.org/athletes/-/14504382"),
            ("Paris 2024 Results Book", "https://www.fecodatle.com/wp-content/uploads/2024/08/R2024-Juegos-Olimpicos-Paris2024-memorias.pdf"),
            ("Athletes First Split Database", "https://www.athletefirst.org/wp-content/uploads/2025/06/Mens-100m-by-athlete-20250520.pdf"),
            ("Wikipedia", "https://en.wikipedia.org/wiki/Fred_Kerley"),
        ],
    ),

    "Kenny Bednarek": dict(
        gender="M",
        mass=86.0, height=1.88, bw=0.40,
        v0=13.49, lam=0.0256, alpha=0.410,
        fatigue_pct=22,
        reaction=0.163,
        target=9.88,
        race_label="Paris 2024 Olympics Final",
        race_date="2024-08-04",
        race_wind=1.0,
        real_splits=[1.91, 2.96, 3.88, 4.75, 5.61, 6.46, 7.29, 8.14, 9.00, 9.88],
        real_reaction=0.163,
        peak_velocity=12.05,
        peak_location="60-70m",
        strides=44.2,
        notes="5th place Paris 2024 final. PB 9.79s (2025 USA Champs). "
              "Shows noticeable deceleration in final 20m.",
        sources=[
            ("World Athletics Profile", "https://worldathletics.org/athletes/united-states/kenneth-bednarek-14715244"),
            ("Paris 2024 Results Book", "https://www.fecodatle.com/wp-content/uploads/2024/08/R2024-Juegos-Olimpicos-Paris2024-memorias.pdf"),
            ("Athletes First Split Database", "https://www.athletefirst.org/wp-content/uploads/2025/06/Mens-100m-by-athlete-20250520.pdf"),
            ("PB confirmation (Olympics.com)", "https://www.olympics.com/en/news/usa-track-field-championships-2025-kenny-bednarek-soars-to-100m-title-with-personal-best-9-79-for-first-national-crown"),
        ],
    ),

    "Christian Coleman": dict(
        gender="M",
        mass=72.0, height=1.75, bw=0.36,
        v0=13.08, lam=0.0204, alpha=0.377,
        fatigue_pct=18,
        reaction=0.128,
        target=9.76,
        race_label="2019 World Championships Final, Doha",
        race_date="2019-09-28",
        race_wind=0.6,
        real_splits=[1.83, 2.85, 3.77, 4.64, 5.48, 6.32, 7.16, 8.01, 8.88, 9.76],
        real_reaction=0.128,
        peak_velocity=11.90,
        peak_location="40-70m",
        strides=47.0,
        notes="World champion 2019. Fast starter with high stride frequency. "
              "Smaller build but explosive. Sustained peak over 30m (40-70m).",
        sources=[
            ("World Athletics Profile", "https://worldathletics.org/athletes/united-states/christian-coleman-14541956"),
            ("Athletes First Split Database", "https://www.athletefirst.org/wp-content/uploads/2025/06/Mens-100m-by-athlete-20250520.pdf"),
            ("2017 WC Biomechanics Report", "https://worldathletics.org/download/download?filename=26370fd8-c843-448b-960e-5a3620884ac0.pdf&urlSlug=biomechanical-fast-analysis-of-mens-100m"),
            ("Wikipedia", "https://en.wikipedia.org/wiki/Christian_Coleman"),
        ],
    ),

    "Usain Bolt (9.58 WR)": dict(
        gender="M",
        mass=94.0, height=1.95, bw=0.43,
        v0=13.48, lam=0.0185, alpha=0.338,
        fatigue_pct=16,
        reaction=0.146,
        target=9.58,
        race_label="2009 World Championships Final, Berlin",
        race_date="2009-08-16",
        race_wind=0.9,
        real_splits=[1.89, 2.88, 3.78, 4.64, 5.47, 6.29, 7.10, 7.92, 8.75, 9.58],
        real_reaction=0.146,
        peak_velocity=12.35,
        peak_location="60-70m",
        strides=41.0,
        notes="World record holder. Minimal deceleration — peak speed sustained. "
              "Longest stride of any 100m champion (~2.44m). Contact time 0.086s, "
              "GRF 3957N (4.1x BW), stride length 2.70m at peak (Coh, 2019).",
        sources=[
            ("World Athletics Profile", "https://worldathletics.org/athletes/jamaica/usain-bolt-14201641"),
            ("IAAF Biomechanics Report Berlin 2009 (Sprint Men)", "https://worldathletics.org/download/download?filename=76ade5f9-75a0-4fda-b9bf-1b30be6f60d2.pdf&urlslug=1+-+Biomechanics+Report+WC+Berlin+2009+Sprint+Men"),
            ("Graubner & Nixdorf (2011) — New Studies in Athletics, 26(1), 19-53", "https://worldathletics.org/news/news/biomechanical-analysis-of-the-sprint-and-hurd"),
            ("Coh (2019) — Usain Bolt biomechanical model, FACTA UNIV.", "https://doi.org/10.22190/FUPES190304003C"),
            ("Wikipedia", "https://en.wikipedia.org/wiki/Usain_Bolt"),
        ],
    ),

    # ──────────────────────────────────────────────
    # WOMEN
    # ──────────────────────────────────────────────

    "Sha'Carri Richardson": dict(
        gender="F",
        mass=52.0, height=1.55, bw=0.33,
        v0=12.00, lam=0.030, alpha=0.39,
        fatigue_pct=27,
        reaction=0.155,
        target=10.65,
        race_label="Best estimated from Paris 2024 / US Trials data",
        race_date="2024",
        race_wind=0.0,
        real_splits=None,
        real_reaction=0.155,
        peak_velocity=11.26,
        peak_location="~55-65m",
        strides=None,
        notes="Paris 2024 laser measurement: peak 11.26 m/s. "
              "Won 2023 World Championship (10.65s). Small build but explosive power.",
        sources=[
            ("World Athletics Profile", "https://worldathletics.org/athletes/united-states/sha-carri-richardson-14703726"),
            ("Paris 2024 laser speed data (NYT)", "https://www.nytimes.com/interactive/2024/08/03/sports/olympics/100-meters-final-time.html"),
            ("Wikipedia", "https://en.wikipedia.org/wiki/Sha%27Carri_Richardson"),
        ],
    ),

    "Melissa Jefferson": dict(
        gender="F",
        mass=55.0, height=1.60, bw=0.33,
        v0=12.12, lam=0.0282, alpha=0.391,
        fatigue_pct=26,
        reaction=0.144,
        target=10.61,
        race_label="Paris 2024 Olympics Final (splits from 10.92 race); PB 10.61 (2025 Worlds)",
        race_date="2024-08-03",
        race_wind=-0.1,
        real_splits=[1.99, 3.13, 4.15, 5.12, 6.07, 7.02, 7.99, 8.95, 9.92, 10.92],
        real_reaction=0.144,
        peak_velocity=10.53,
        peak_location="40-60m",
        strides=None,
        notes="2025 World Championship gold (10.61s). Bronze medal Paris 2024 (10.92s). "
              "Mass estimated — not publicly reported.",
        sources=[
            ("World Athletics Profile", "https://worldathletics.org/athletes/united-states/melissa-jefferson-14647878"),
            ("Athletes First Women's Split Database", "https://www.athletefirst.org/wp-content/uploads/2025/04/Womens-100m-by-athlete.pdf"),
            ("Paris 2024 Results Book", "https://www.fecodatle.com/wp-content/uploads/2024/08/R2024-Juegos-Olimpicos-Paris2024-memorias.pdf"),
            ("Wikipedia", "https://en.wikipedia.org/wiki/Melissa_Jefferson_(athlete)"),
        ],
    ),

    "Twanisha Terry": dict(
        gender="F",
        mass=57.0, height=1.65, bw=0.34,
        v0=12.14, lam=0.0272, alpha=0.391,
        fatigue_pct=25,
        reaction=0.134,
        target=10.83,
        race_label="2023 Prefontaine Classic Final, Eugene",
        race_date="2023-09-16",
        race_wind=0.8,
        real_splits=[2.02, 3.14, 4.15, 5.11, 6.06, 6.99, 7.94, 8.89, 9.85, 10.83],
        real_reaction=0.134,
        peak_velocity=10.75,
        peak_location="50-60m",
        strides=None,
        notes="PB 10.83s (Prefontaine 2023). 5th in Paris 2024 final (10.97s). "
              "Mass estimated — not publicly reported.",
        sources=[
            ("World Athletics Profile", "https://worldathletics.org/athletes/united-states/twanisha-terry-14553598"),
            ("Athletes First Women's Split Database", "https://www.athletefirst.org/wp-content/uploads/2025/04/Womens-100m-by-athlete.pdf"),
            ("Paris 2024 Results Book", "https://www.fecodatle.com/wp-content/uploads/2024/08/R2024-Juegos-Olimpicos-Paris2024-memorias.pdf"),
            ("Wikipedia", "https://en.wikipedia.org/wiki/Twanisha_Terry"),
        ],
    ),

    "Florence Griffith-Joyner": dict(
        gender="F",
        mass=59.0, height=1.70, bw=0.34,
        v0=12.40, lam=0.025, alpha=0.38,
        fatigue_pct=23,
        reaction=0.130,
        target=10.49,
        race_label="1988 US Olympic Trials, Indianapolis (WR)",
        race_date="1988-07-16",
        race_wind=0.0,
        real_splits=None,
        real_reaction=0.130,
        peak_velocity=None,
        peak_location=None,
        strides=None,
        notes="World record holder (10.49s). Limited biomechanics data from 1988. "
              "Parameters estimated from race video analysis.",
        sources=[
            ("World Athletics Profile", "https://worldathletics.org/athletes/united-states/florence-griffith-joyner-14245240"),
            ("Wikipedia", "https://en.wikipedia.org/wiki/Florence_Griffith-Joyner"),
        ],
    ),
}

ATHLETE_NAMES = list(ATHLETES.keys())
MEN = [k for k, v in ATHLETES.items() if v["gender"] == "M"]
WOMEN = [k for k, v in ATHLETES.items() if v["gender"] == "F"]
