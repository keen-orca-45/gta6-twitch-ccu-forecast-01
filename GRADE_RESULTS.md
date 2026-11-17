# Grade / validation results — gta6-twitch-ccu-forecast-01 entry
# Generated 2026-11-17 (WIB), entry v2 (console blend alpha=0.4)

## grade-local (kit CLI)
Command (from inside the kit):
  node cli/makefun.mjs grade-local --kit . --bot ../gta6-entry/main.py [--driver process]
Result for BOTH the starter baseline and this entry:
  "makefun grade-local: gta6-twitch-ccu-forecast-01 is a program/v1
   competition: its scorer and reference data are not published in the
   kit, so it is graded on the server only"
Docker is also not installed in this VM. So NO per-case practice score
is obtainable locally; the true practice score only comes from a server
submission (not done here, per task).

## Local run (practice cases p00..p03)
  MAKEFUN_INPUT_DIR=<kit>/input MAKEFUN_OUTPUT_DIR=/tmp/gta/out1 python3 main.py
  - 4 cases in ~0.15 s total; single case (p02) ~0.11 s (limit 8 s)
  - deterministic byte-for-byte across two runs (diff clean)
  - output shape valid: 23 rows, hours 2..24, 5 non-decreasing quantiles > 0
  - median ratios (median / hour-1 print):
      p00 Wolverine (p1=23,357):  h2 0.81, h11 0.82, h20 1.71, h24 1.45
      p01 RDR2      (p1=116,550): h2 0.81, h11 0.82, h20 1.71, h24 1.45
      p02 GoW Rag.  (p1=269,517): h2 0.81, h11 0.82, h20 1.71, h24 1.45
      p03 Spider-Man (p1=119,087): h2 0.81, h11 0.82, h20 1.71, h24 1.45
    (same ratios for all four: the filtered comparable pool is the same
     38 games in every practice case, and the relative filter threshold
     max(15k, 8% of p1) admits the same set for p1 23k-270k)

## Leave-one-out through shipped main.py (25 practice-like comparables,
## hour-1 >= 20k, peak/hour-1 <= 8; each target's comparables = the other 37)
  model pinball    0.2254
  baseline pinball 0.2710
  console-only targets (7): model 0.1936 vs baseline 0.2828
  typical miss: model 44.8% vs baseline 53.0%
  90% coverage: model 0.92 vs baseline 0.83
  worst model targets: Starfield 0.382, Monster Hunter Wilds 0.360,
  Ghost of Yotei 0.347, AC Shadows 0.327
  House baseline practice loss (competition.yaml): ~0.387

## Analysis summary
- All-comparables median ratio: h2 0.87, h10 0.91, h19 2.40, h24 2.04 —
  dominated by small categories whose hour 1 is a pre-unlock trickle
  (peak/hour-1 up to 2000x).
- Big (p1>=100k) comparables: dip to ~0.53 at h10-11, recover to
  ~1.0-1.3 at h19-21.
- Practice games: Wolverine p1 23,357; RDR2 116,550; GoW Ragnarok
  269,517; Spider-Man 2 119,087 — all console, rolling midnight local,
  no early access. GTA VI unlocks NZ 2026-11-18 11:00Z, Europe 23:00Z,
  UK 00:00Z, US East 05:00Z, US West 08:00Z.
