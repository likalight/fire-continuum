# Month-to-date evidence: 1–13 November 2026

This closes the previous fixed five-day snapshot gap with a pinned month-to-date observation comparison. All 26 expected NASA daily source tables were downloaded and validated: Aqua/MODIS and NOAA-20/VIIRS for each UTC date from 1 through 13 November 2026. The global input files total 71,749,633 bytes. Their presence does **not** establish complete observations, cloud-free coverage or detection of all burning. The 13th is a completed UTC date, but late NRT delivery and processing changes remain possible. This is a saved snapshot, not a continuously refreshed service.

The original Indonesia coefficients were frozen before calculation. Historical sources were checked against their recorded SHA-256 hashes. The baseline is Aqua on the same 1–13 November dates in 2003–2017. The separate audit uses 2022–2025, excluded from original calibration, with all five predefined regions reported. No region or date window was chosen to improve the observed result. Previously seen project results mean this new diagnostic is exploratory, not an untouched final benchmark.

## What the data support

Indonesia has 2,710 retained Aqua detections and 19,122 retained NOAA-20 detections. After one occupied 1 km cell per UTC day is retained, these become 2,625 Aqua and 13,558 NOAA-20 cell-days. The original frozen model estimates **2,253.7 Aqua-equivalent cell-days** from NOAA-20, 14.1% below the concurrent Aqua count. These are different quantities; none is a count of distinct fires or area burned.

Both sensors place Indonesia **above its same-date historical median**, but below the historical 90th percentile. The median is 558 Aqua cell-days and the 90th percentile is 3,706.6. Both classifications persist when any single date is omitted from both current and historical windows. That is a sensitivity check, not a confidence interval or independent validation.

| Fixed region | Current Aqua cell-days | Frozen NOAA-20 estimate | Aqua / estimate categories | Same-date held-out WAPE | All-month 1–13 audit category agreement |
| --- | ---: | ---: | --- | ---: | ---: |
| Indonesia | 2,625 | 2,253.7 | Above typical / Above typical | 14.7% | 46/48 |
| Sumatra | 207 | 214.1 | Above typical / Above typical | 16.6% | 47/48 |
| Kalimantan | 696 | 620.6 | Above typical / Above typical | 16.0% | 41/48 |
| Java | 28 | 72.3 | Above typical / Unusually high | 158.9% | 18/48 |
| Papua | 890 | 595.0 | Unusually high / Unusually high | 33.3% | 40/48 |

Same-date WAPE has only four held-out annual windows. The broader 48-window WAPE for Indonesia is 16.3%; those windows cover days 1–13 in every month of 2022–2025. Java remains a clear failure: the calibrated estimate and Aqua disagree on the current category, and the held-out error is large. Papua agrees on category despite a substantial magnitude difference. Publish these failures alongside the national result.

The 14.1% current Indonesia difference must not be described as a correction that reduced the old 46.8% five-day discrepancy: the dates changed from 8–12 November to 1–13 November. The original coefficients did not change. Longer aggregation can change the result; this analysis does not isolate why.

## Provenance and reuse

Run `pipeline/20_month_to_date.py` with the existing authorized Earthdata environment. Raw global daily files remain ignored. Downloads are pinned with receipts and hashes; a changed historical source or frozen model causes an error. Missing or invalid daily files withhold calculation instead of becoming zero observations. The source ledger records every requested sensor/date and validates that nonempty tables contain only that date. A valid empty table is still not evidence of clear-sky zero burning.

Public outputs are `month-to-date.json`, `month-to-date-history.json.gz`, `month-to-date-detections.csv.gz` and `month-to-date-protocol.json`. The CSV preserves original latitude, longitude, acquisition date/time, confidence, product version, satellite and sensor. Acquisition times are normalized to HHMM for consistent ordering. Sparse history uses the same column layout as the original recent comparison. The `snapshot_sha256` field aliases the compressed original-point export hash.

NASA identifies these current products as NRT. Historical country archives can differ in processing version and upstream country assignment; application of the same Indonesia mask cannot reverse already excluded coastal detections. No global observation denominator, cloud correction, burned-area confirmation or independently proven fire attribution is added by this comparison.

Official access documentation: [NASA FIRMS data access](https://firms.modaps.eosdis.nasa.gov/content/active_fire/), [MODIS global daily archive](https://nrt3.modaps.eosdis.nasa.gov/archive/FIRMS/modis-c6.1/Global/), [NOAA-20 global daily archive](https://nrt3.modaps.eosdis.nasa.gov/archive/FIRMS/noaa-20-viirs-c2/Global/). Exact source URLs and file hashes are in the published JSON ledger.
