# Date-matched recent comparison

Snapshot retrieved 14 November 2026 at 07:10 UTC. Comparison: **8–12 November 2026, inclusive UTC**, versus those same five calendar dates in past years. The full-month calendar remains 2003–2025. Other 2026 dates are unavailable, not zero.

## Window and processing

The protocol was written before computing the new comparisons; prior monthly diagnostics and raw snapshot totals had already been inspected. We discard the first shared source-file date and dates whose midnight end is less than 24 hours before retrieval. This conservative delivery buffer is not a completeness guarantee. The resulting five-day window is determined by source dates, not by its fire activity.

We apply the same geoBoundaries country mask to historical and current points, the existing sensor-specific confidence filters, and EPSG:6933 occupied 1 km cells per UTC day. The earliest acquisition time assigns each occupied cell to a 0.25-degree display cell; coordinate tie breaks are deterministic. Historical country archives may already omit coastal records that cannot be recovered by applying a shared mask. All thermal-source types are retained.

NOAA-20 is the current primary source; Aqua is a concurrent comparison, never added to it. Original sector/quarter coefficients fitted in 2019–2021 remain frozen. The historical reference is Aqua on the same dates in 2003–2017 (15 observations). Median and p90 use linear interpolation; categories require a positive median and strictly exceed thresholds. A seven-year NOAA-20-only comparison is supplementary, with a different baseline, not a substitute selected after seeing results.

## Tests on years excluded from fitting

The model trained on monthly totals was tested on days 8–12 of all 12 months in 2022–2025: 48 short windows per region. The November dates are separately evaluated across four held-out years. WAPE is sum of absolute adjusted-minus-Aqua differences divided by sum of Aqua activity. It is not accuracy against true fires, a significance level, or an error bound for the current period.

| Study area | 48-window WAPE | Same November dates, four years | Category agreement, 48 windows |
|---|---:|---:|---:|
| Indonesia | 22.4% | 21.0% | 44/48 |
| Sumatra | 37.4% | 27.4% | 45/48 |
| Kalimantan | 29.4% | 29.3% | 40/48 |
| Java & Bali | 101.2% | 224.9% | 23/48 |
| Papua | 42.9% | 52.3% | 37/48 |

Category agreement compares each instrument against the same 2003–2017 Aqua baseline for each calendar window. It does not establish agreement on exact counts. Windows within a year are not independent samples. All regions and failures are retained.

The single-factor baseline gives 29.3% WAPE for Kalimantan's 48 windows, slightly better than the original regional/seasonal fit's 29.4%. For the four November windows it gives 35.2%, versus 29.3% for the original model. We retained the original model rather than selecting whichever wins this diagnostic.

## Current Kalimantan result

- Adjusted NOAA-20: **115.9782 Aqua-equivalent cell-days**, versus a historical Aqua median of **43**, or **2.70×**.
- Concurrent Aqua: **79 observed cell-days**, or **1.84×** the same median.
- Historical p90: **175.6**. Both are **above typical**, below that threshold.
- The two counts still differ by about **46.8% relative to Aqua**, despite agreeing on a category. This is a provisional comparison, not a precise current fire total.
- Removing each of the five dates from both current and historical windows preserves both original categories in **5/5 checks**. This is sensitivity analysis, not a confidence probability.

The Java/Bali and Papua categories survive only 4/5 day-omission checks. The app exposes those changes, including sensor disagreement after removing 8 November in Java/Bali. Arbitrary rectangles have no dedicated held-out calibration diagnostic and remain exploratory.

## Evidence boundary

[NASA FIRMS distinguishes NRT and standard processing](https://firms.modaps.eosdis.nasa.gov/content/academy/data_api/firms_api_use.html). The historical backtests compare archived products with archived products. They **do not validate NRT-to-standard processing continuity**. Current Aqua agreement is a cross-sensor check, not independent ground truth.

Cloud, overpass and instrument-availability denominators are unavailable in these hotspot-only records. A date with no detection is not evidence of no fire or of successful clear-sky observation. A 24-hour delivery buffer cannot repair missing or obscured observations. No full-month extrapolation, fire forecast, operational warning or severity label is issued.

## Reproduction and export

Run `pipeline/09_recent_comparison.py` after the annual archive, original calibration and saved recent snapshot are available. It uses the saved snapshot rather than silently refreshing it. `pipeline/03_recent.py` explicitly refreshes the upstream feed; doing so changes the evidence and requires rerunning and reviewing this analysis. Fixed fixture assertions in the tests pin this release's dates and results.

- `recent_protocol.json`: prespecified window and validation rules.
- `recent_window_counts.csv`: regional counts for every processed historical short window.
- `recent_input_audit.json`: input identity and mask/filter accounting.
- `recent-comparison.json`: all region results, coefficients' training/test periods, source and snapshot hashes, sensitivity and limits.
- `web/public/data/recent-history.json.gz`: sparse per-day display cells for browser aggregation, including all matching historical dates. No unavailable pre-2019 NOAA-20 period is presented as observed zero in exports.

The season briefing includes the recent comparison for the selected area; changing a historical month does not change the recent window. The guided demo has a sixth step so the recent comparison and remaining validation failures both remain visible. The downloadable same-date CSV includes exact dates and distinguishes NRT from archive observations. Neither export adds overlapping sensors together.
