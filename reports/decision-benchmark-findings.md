# Decision-level benchmark findings

The follow-up protocol was recorded before computing these metrics, after earlier Indonesia count-based results were seen. Evaluation years are excluded from fitting, but this is not an untouched final benchmark. Models remain frozen. The benchmark includes Sumatra, Kalimantan, Java/Bali, Papua and Sulawesi study rectangles; overlapping rectangles and repeated months are not independent observations.

Aqua calendar-month medians and p90 from 2003–2017 define three descriptive categories. The four methods are intentionally unharmonized VIIRS detections, common-grid occupied cell-days, a single national training ratio, and the released sector-quarter calibration. Aqua is a reference instrument, not ground truth. The labels do not represent significance, danger or distinct fires.

| Sensor | Comparisons | Simple category agreement | Released agreement | Simple balanced accuracy | Released balanced accuracy |
|---|---:|---:|---:|---:|---:|
| NOAA-20 | 240 | 79.6% | 82.9% | 78.7% | 70.6% |
| Suomi NPP | 470 | 73.0% | 75.7% | 76.7% | 71.2% |

The incremental NOAA-20 gain is 8 additional matching region-month labels: 191 to 199 of 240. It is not a 3.3% improvement in ground-truth fire accuracy. Balanced accuracy gives equal weight to each reference class present; it declines with the released method.

Rare-category result: of 6 NOAA-20 audit months categorized above p90 by Aqua, the released method misses 3; simple calibration misses 1. Released false above-p90 labels decline from 22 to 15, but precision remains only 3/18 (16.7%). NPP misses 6 of 17 reference above-p90 months versus 2 for simple calibration. These small samples and trade-offs prevent an operational alert claim.

The shared retrospective count-support gate retains 195/240 NOAA-20 comparisons (81.25%) and 380/470 NPP comparisons (80.85%). It requires baseline median >=5 and concurrent Aqua/VIIRS >=20 occupied cell-days. Supported agreement is 86.7% NOAA-20 and 82.6% NPP, with the withheld denominator equally prominent. This is not clear-sky coverage, and the gate cannot operate unchanged after Aqua retires.

Annual cyclic three-month peak-window start agreement improves from 70% to 75% for NOAA-20 with released versus simple calibration, but declines from 77.1% to 71.4% for NPP. Mean circular start error is 0.30 versus 0.50 months for NOAA-20 and 0.40 versus 0.34 for NPP. These windows are retrospective summaries, not onset dates or forecasts.

Known Aqua outage months August–September 2020 are excluded from NPP decision comparisons, and the entire 2020 year is excluded from the annual-window test. Baseline coverage for all other dates remains unknown. Existing coefficients and the recent 46.8% discrepancy are unchanged.

Reproduce: `python pipeline/16_decision_benchmark.py`, using pinned `history.json.gz` and `metadata.json`. `decision_benchmark_protocol.json` defines every rule. `decision-benchmark.json` contains input hashes, confusion matrices, regional results and all 710 records; the web CSV carries each estimate and category. Tests check boundaries, circular ties, class imbalance, support gates, exclusions and published-score reconciliation.
