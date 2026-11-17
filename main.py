"""Forecast Twitch viewers on a game's release day, hours 2..24, from hour 1.

Model (stdlib only, deterministic, no network):
  The case file itself carries `comparables`: past big launches with a full
  hourly series over their UTC release day. For each comparable we take the
  log-ratio log(viewers_h / viewers_1) for h = 2..24.
  Only *relevant* comparables are used, chosen at run time from the target
  case's own hour-1 print p1:
    - comparable hour-1 print >= max(15000, 0.08 * p1)  (hour 1 must already
      be a real launch audience, not a pre-unlock trickle), and
    - comparable release-day peak / hour-1 <= 8  (excludes games whose
      hour 1 was still pre-unlock and then exploded 20-1000x when a single
      global unlock hit, e.g. Silksong / Helldivers 2 / Black Myth).
  Small-hour-1 games are the trap in this data: their median ratio rises
  to ~2x by hour 19 and ~100x in the tail, while big rolling-midnight
  console launches (the practice games, and GTA VI) dip to ~0.5-0.7 in
  the UTC night (hours 8-11) and recover to ~1.0-1.4 by hours 19-21.
  Per hour we take the median log-ratio across the filtered comparables
  (3-point weighted smoothing to kill single-hour noise) and a robust
  spread sigma = IQR/1.349 clipped to [0.20, 0.75]; quantiles are
      q_tau(h) = p1 * exp(median_h + z_tau * sigma_h),  z as in the baseline.
  The median is blended 60/40 with the median over the console-only
  comparables (platforms field with no PC/Stadia: PS/Xbox/Switch only),
  when at least 3 of those survive the filter: the practice games and
  GTA VI are all console-only launches, and on console-only targets the
  blend scores 0.193 vs 0.220 for the unblended median, with no loss on
  multi-platform targets (0.226 both ways).
  If fewer than 5 comparables survive the filter, fall back to the house
  persistence baseline (sigma 0.15*sqrt(h-1)).

  Leave-one-out check on practice-like comparables (hour-1 >= 20k,
  peak/hour-1 <= 8): pinball 0.227 vs 0.271 for the persistence baseline.
  House baseline practice loss is ~0.387; this model must beat it, and
  the house-model forecast, to take a paid place.
"""
import json
import math
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

INPUT_DIR = Path(os.environ.get("MAKEFUN_INPUT_DIR", "/input"))
OUTPUT_DIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
LEVELS = [0.05, 0.25, 0.5, 0.75, 0.95]
Z = [-1.645, -0.674, 0, 0.674, 1.645]


def round2(x):
    scaled = x * 100
    whole = math.floor(scaled)
    if scaled - whole >= 0.5:
        whole += 1
    value = whole / 100
    return int(value) if value == int(value) else value


def median(xs):
    s = sorted(xs)
    n = len(s)
    return s[n // 2] if n % 2 else 0.5 * (s[n // 2 - 1] + s[n // 2])


def comparable_log_ratios(case, p1):
    """Return (per_hour, per_hour_console): log-ratio lists, hours 2..24.

    per_hour: filtered comparables (see module docstring).
    per_hour_console: the subset whose platforms field names no PC/Stadia.
    """
    per_hour = [[] for _ in range(25)]
    per_con = [[] for _ in range(25)]
    thresh = max(15000.0, 0.08 * p1)
    for comp in case.get("comparables") or []:
        hourly = comp.get("hourly") or []
        ds = comp.get("day_start")
        if not ds:
            continue
        idx = None
        for i, row in enumerate(hourly):
            if row.get("from") == ds:
                idx = i
                break
        if idx is None:
            continue
        day = hourly[idx:idx + 24]
        if len(day) < 24:
            continue
        try:
            vs = [float(r["viewers"]) for r in day]
        except (KeyError, TypeError, ValueError):
            continue
        if vs[0] <= 0 or any(v <= 0 for v in vs):
            continue
        if vs[0] < thresh:
            continue
        if max(vs) / vs[0] > 8.0:
            continue
        plat = str(comp.get("platforms") or "").lower()
        console_only = "pc" not in plat and "stadia" not in plat
        for H in range(2, 25):
            per_hour[H].append(math.log(vs[H - 1] / vs[0]))
            if console_only:
                per_con[H].append(math.log(vs[H - 1] / vs[0]))
    return per_hour, per_con


def forecast_case(case, name):
    if case["levels"] != LEVELS:
        raise ValueError(f"{name} asks for levels {case['levels']}, not {LEVELS}")
    first = next((k for k in case["known"] if k["hour"] == 1), None)
    if first is None:
        raise ValueError(f"{name} has no hour-1 print")
    p1 = max(1.0, float(first["viewers"]))
    per_hour, per_con = comparable_log_ratios(case, p1)
    usable = sum(1 for h in range(2, 25) if len(per_hour[h]) >= 5)
    hours = []
    if usable >= 20:
        med = [0.0] * 25
        sig = [0.15] * 25
        for h in range(2, 25):
            xs = sorted(per_hour[h])
            m = median(xs)
            if len(per_con[h]) >= 3:
                m = 0.6 * m + 0.4 * median(per_con[h])
            med[h] = m
            q1 = xs[len(xs) // 4]
            q3 = xs[(3 * len(xs)) // 4]
            sig[h] = max(0.20, min(0.75, (q3 - q1) / 1.349))
        # 3-point weighted smoothing of the median log-ratio curve.
        sm = med[:]
        for h in range(2, 25):
            lo = med[h - 1] if h > 2 else med[h]
            hi = med[h + 1] if h < 23 else med[h]
            sm[h] = 0.25 * lo + 0.5 * med[h] + 0.25 * hi
        for row in case["forecast"]:
            h = int(row["hour"])
            qs = [round2(min(1e9, max(1.0, p1 * math.exp(sm[h] + z * sig[h])))) for z in Z]
            # Enforce non-decreasing (rounding can only tie, never invert, but be safe).
            for i in range(1, 5):
                if qs[i] < qs[i - 1]:
                    qs[i] = qs[i - 1]
            hours.append({"hour": h, "q": qs})
    else:
        # Fallback: house persistence baseline.
        for row in case["forecast"]:
            h = int(row["hour"])
            s = 0.15 * math.sqrt(h - 1)
            hours.append({"hour": h, "q": [round2(p1 * math.exp(z * s)) for z in Z]})
    return {"hours": hours}


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for path in sorted(INPUT_DIR.glob("*.in")):
        case = json.loads(path.read_text(encoding="utf-8"))
        forecast = forecast_case(case, path.name)
        (OUTPUT_DIR / f"{path.stem}.out").write_text(
            json.dumps(forecast, separators=(",", ":")) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
