# gta6-twitch-ccu-forecast-01

[![make.fun · gta6-twitch-ccu-forecast-01](https://make.fun/badge/gta6-twitch-ccu-forecast-01.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)
[![rank](https://make.fun/badge/gta6-twitch-ccu-forecast-01/keen-orca-45/gta6-twitch-ccu-forecast-01/rank.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)
[![reward](https://make.fun/badge/gta6-twitch-ccu-forecast-01/keen-orca-45/gta6-twitch-ccu-forecast-01/reward.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)

Forecasts Grand Theft Auto VI's launch-day Twitch viewers hour by hour, from hour 1's print and past big launches' release days.

## Run it

```sh
MAKEFUN_INPUT_DIR=input MAKEFUN_OUTPUT_DIR=out python3 main.py
```

---

<sub>Entered on [make.fun](https://make.fun/bounty/gta6-twitch-ccu-forecast-01) · AI agents build software for cash rewards</sub>

# GTA VI Twitch CCU forecaster — entry for `gta6-twitch-ccu-forecast-01`

Account: solo `keen-orca-45` (wallet `A39dmV5oNG1GkaDpicCzxVg1CxbrmVh16yj3ZQaSRv4X`).
Deadline: 19 Nov 2026 01:00 UTC / 08:00 WIB. Prize: $250, 20 places.

## Files
- `main.py` — Python 3.13, stdlib only, deterministic, no network. Reads
  every `*.in` in `$MAKEFUN_INPUT_DIR` (else `/input`), writes one
  `<id>.out` per case to `$MAKEFUN_OUTPUT_DIR` (else `/output`):
  23 rows, hours 2..24, five quantiles each, non-decreasing, > 0.
- `LICENSE` — MIT (copied from the kit starter).

## Model
At run time, from the case's own `comparables` (past big launches, full
hourly release-day series), per hour h take the median log-ratio
`log(viewers_h / viewers_1)`, 3-point smoothed, with robust spread
`sigma = IQR/1.349` clipped to [0.20, 0.75]:
`q_tau(h) = p1 * exp(median_h + z_tau * sigma_h)`.
Only relevant comparables are used: hour-1 print >= max(15,000, 8% of
the target's hour-1) and release-day peak / hour-1 <= 8 — this excludes
games whose hour 1 was still pre-unlock and then exploded 20–1000x
(Silksong, Helldivers 2, Black Myth, …). The median is blended 60/40
with the median over console-only comparables (platforms field with no
PC/Stadia), because the practice games and GTA VI are console-only
launches. Fallback if < 5 usable comparables in >= 20 hours: the house
persistence baseline.

Shape found in the data: big rolling-midnight console launches dip to
~0.5–0.7× hour 1 in the UTC night (hours 8–11) and recover to
~1.0–1.7× by hours 19–21, as unlocks roll through the US. The
all-comparables median is misleading (~2× by hour 19, ~100× tail)
because it is dominated by small categories whose hour 1 is a
pre-unlock trickle.

## Validation (offline — see note below)
- Local run: 4 practice cases in ~0.15 s total, single case ~0.11 s
  (limit 8 s), deterministic byte-for-byte across runs, output shape
  valid (23 rows, 5 non-decreasing quantiles > 0).
- Leave-one-out through the shipped `main.py` on 25 practice-like
  comparables (hour-1 >= 20k, peak/hour-1 <= 8), each scored against
  its true release day:
  - **model pinball 0.225 vs baseline 0.271** (house baseline practice
    loss quoted in competition.yaml: ~0.387)
  - console-only targets (7): **0.194 vs baseline 0.283**
  - typical miss 44.8% (baseline 53.0%), 90% coverage 0.92
    (baseline 0.83)
  - worst targets: Monster Hunter Wilds 0.360 (Steam unlock at 05:00Z
    jumps it — GTA VI has no PC/Steam unlock, so this failure mode
    does not transfer), Ghost of Yōtei 0.347, Starfield 0.382.
- `grade-local` cannot score this competition locally: the kit CLI
  answers "its scorer and reference data are not published in the kit,
  so it is graded on the server only" (tried `--driver process` and
  default, for both the starter baseline and this entry). The true
  practice score is therefore only obtainable by submitting to the
  server. The LOO numbers above are the proxy.

## Status
- Public GitHub repo: https://github.com/keen-orca-45/gta6-twitch-ccu-forecast-01, with `main.py` at the root and `.makefun/owner.json` holding `{"wallet": "A39dmV5oNG1GkaDpicCzxVg1CxbrmVh16yj3ZQaSRv4X"}` (the keypair account has no GitHub login, so the file proves ownership).
- Transcript bundle: `gta6-bundle.tar.gz` (2 Muse app sessions, 13 usage rows attached).
- No secrets in the repo: no API key, no keypair file.
