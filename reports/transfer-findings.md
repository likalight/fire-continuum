# Two external-region transfer tests

The rectangles, sources, fits, support gate and scores were fixed in `transfer-protocol.json` before external data were downloaded or evaluated. Earlier Indonesia results had already been seen. This is a disclosed follow-up experiment, not an untouched final benchmark.

## Scope and data

The fixed Punjab study rectangle is [73.8,29.5,76.9,32.6]; the southeast Australia rectangle is [147,-38,153,-30]. These are exact analysis rectangles intersected with NASA's annual country-file selection, not state borders. Punjab provides an agricultural-burning context and southeastern Australia a context with documented major wildfire episodes. **Neither label classifies every hotspot.** Prescribed burns, other agricultural activity and non-vegetation heat sources can contribute. In particular, the Australian audit years' peak is March–May, not proof of an extreme summer wildfire episode.

60 real NASA FIRMS annual country files (1,613,455,866 bytes) supply Aqua MODIS 2003–2025 and NOAA-20 VIIRS 2019–2025. Each has a public URL, advertised size, download time and SHA256 hash. Raw files are ignored by Git. No new account, purchase or agreement was required.

Sources and context:

- [NASA FIRMS annual archive](https://firms.modaps.eosdis.nasa.gov/country/)
- [NASA: Smokier and Smokier Skies in India](https://science.nasa.gov/earth/earth-observatory/smokier-and-smokier-skies-in-india-144181/)
- [NASA: Fires and Smoke Engulf Southeastern Australia](https://science.nasa.gov/earth/earth-observatory/fires-and-smoke-engulf-southeastern-australia-146110/)

Aqua confidence ≥30 and NOAA-20 nominal/high observations are retained. Exact duplicate observations are removed. Locations are projected to EPSG:6933 1 km cells, occupied at most once per sensor per UTC day. Raw filtered NOAA-20 detections are retained as a deliberately unharmonized comparison. All numbers represent satellite activity observations, not distinct fires, ignition times or burned area.

## What is transferred and what is refitted

**Frozen transfer:** the released Indonesia sector/quarter NOAA-20 coefficients are applied unchanged. Its existing longitude rule maps Punjab to sector0 and Australia to sector2; there is no seasonal shift, parameter tuning or local fitting. This is extrapolation outside the fitted geography.

**Local adaptation:** a separate quarterly ratio of summed Aqua occupied cell-days to NOAA-20 occupied cell-days is fitted on each external region's 2019–2021 observations. August and September 2020 are excluded conservatively because of the documented Aqua archive outage. The frozen Indonesia model is not retroactively changed. Local adaptation uses additional regional data and a different training quality restriction; it is not zero-shot transfer and does not replace the published method.

Both are evaluated on all 48 months in 2022–2025, excluded from local fitting. All four comparators and every month are published.

## Results against concurrent Aqua

Categories use each calendar month's 15-year Aqua baseline (2003–2017): at/below median, above median through p90, or above p90. These are descriptive satellite categories, not ground truth or significance tests.

| Region / method | Category agreement | WAPE | Mean peak-start error |
|---|---:|---:|---:|
| Punjab: raw VIIRS detections | 12/48 (25.0%) | 402.6% | 2.75 months |
| Punjab: unadjusted occupied cells | 13/48 (27.1%) | 313.1% | 2.75 months |
| Punjab: frozen Indonesia model | 29/48 (60.4%) | 35.9% | 2.75 months |
| Punjab: separately fitted local model | 34/48 (70.8%) | 22.6% | 1.25 months |
| Southeast Australia: raw VIIRS detections | 2/48 (4.2%) | 598.8% | 0.00 months |
| Southeast Australia: unadjusted occupied cells | 6/48 (12.5%) | 293.3% | 0.00 months |
| Southeast Australia: frozen Indonesia model | 35/48 (72.9%) | 44.1% | 0.00 months |
| Southeast Australia: separately fitted local model | 32/48 (66.7%) | 27.1% | 0.00 months |

**The important counterexample:** Australian local adaptation improves count error from 44.1% to 27.1% but reduces category agreement from 72.9% to 66.7%. Better aggregate magnitude agreement does not guarantee better threshold decisions. Both remain comparisons with Aqua, whose observing coverage and sensitivity are not complete truth.

The three-month seasonal window is the highest-sum consecutive circular window in each audit year's twelve-month profile. Earliest start wins exact ties. Circular start-month distance is reported. This is a profile statistic, not a dated cross-year event or forecast. Punjab's locally adapted result matches Aqua's October start in 2024, where the frozen transfer picks April; it still differs by five months in 2025. Australia matches the Aqua March start in all four years even without calibration. No universal seasonal improvement is claimed.

## Withholding and usable support

The predefined retrospective support gate requires concurrent Aqua and NOAA-20 occupied counts ≥20 and baseline median ≥5. **Because it uses concurrent Aqua, it is an evaluation diagnostic, not an operational confidence gate for a future VIIRS-only period.**

Punjab retains 38/48 months (79.2%); local-model category agreement is 28/38 (73.7%) on that subset. Ten months are withheld from this diagnostic, but remain visible in the all-month evaluation. Australia retains 47/48 (97.9%); frozen agreement is 34/47 (72.3%) and local agreement is 31/47 (66.0%). One month is withheld. Retention and accuracy must always be shown together.

## Limits

Annual archive availability does not establish clear-sky observation completeness. Zero reported detections is not no fire. Full masks/QA were not collected for these external rectangles. Known 2020 outage months are marked. No operational warning, independent ground-truth accuracy, classification of burning causes, global coverage or external practitioner usefulness validation is claimed. The exact two regions were selected before outcomes and have not been changed to improve results.

## Reproduce and inspect

Run `python pipeline/17_transfer_cases.py` to retrieve the catalog, verify/download all 60 files and build the report. Run `python pipeline/17_transfer_cases.py --cached` to require pinned local files and verify their hashes. The public `transfer-cases.json` contains both regions, all monthly values, baseline samples, fits, source manifests and scores. `transfer-months.csv` includes all four estimates and categorical labels. `reports/transfer-monthly-counts.csv` preserves the sensor-separated count ledger.

Six tests check category boundaries, support thresholds, circular/tied peaks, absence of test-year and known-outage leakage into the local fit, original sensor/confidence filters with same-day deduplication, and reconciliation of every report score with its published monthly records. Source files remain separately hashed and untouched.
