# Observation quality, time matching and decision case

This follow-up was specified after earlier calibration results and the 16-day mask pilot, before the new computations. It is exploratory, not an untouched final benchmark. See `decision_protocol.json` for fixed dates, gates and selection rules.

## Full masks and quality

24 NASA MYD14A1.061 granules cover the requested August–October 2019 and 2020 periods for 113–114° E, 3–2° S. Of 184 requested dates, 167 have daily layers and 17 (17 August–2 September 2020) are absent. Every available date retains all FireMask and QA values for 14,386 selected native sinusoidal cells, without resampling. The 391 KB gzip pixel archive uses 255 only as an outside-rectangle sentinel. The daily CSV and JSON use empty/null values for absent days, never zero counts.

Dates MUST come from the HDF `Dates` attribute. For example, A2020241 has an eight-day StartDate/EndDate range but contains only 3 and 4 September. Deriving dates by adding slice offsets to StartDate would incorrectly assign these observations to 28 and 29 August. A regression test preserves the correct mapping.

QA bits 0–1 retain water/coast/land/missing; bit 2 is the representative classification's day/night flag. Missing QA can carry a zero day/night bit; it must not be interpreted as a night observation. Daily class proportions do not measure clear-sky overpass exposure. We neither divide hotspots by these proportions nor claim paired MODIS/VIIRS coverage normalization. Zero cloud in a daily composite does not establish a cloud-free day.

NASA documents the Aqua FMU/SSR outage beginning 16 August 2020, with recovery on 2 September. Direct-broadcast observations existed during the outage, so an archive gap does not establish that the instrument never observed. Our selected daily archive still lacks 17 dates. The UI flags 2020 annual timing as coverage-affected, and warns about affected-period comparisons.

Sources: [NASA MYD14A1 specification](https://ladsweb.modaps.eosdis.nasa.gov/filespec/MODIS/6/MYD14A1), [NASA outage](https://landweb.modaps.eosdis.nasa.gov/displayissue?id=262), [product DOI](https://doi.org/10.5067/MODIS/MYD14A1.061). Full granule URLs, hashes and layer dates are in `quality-calendar.json`.

## Time-matching experiment

Restrict approximate local mean solar time (UTC minutes + longitude × 4, modulo 1440) before occupied-cell/day deduplication. Fixed windows: unrestricted, 12:00–15:00, 13:00–14:00. Use 8–12 of every month, regional quarterly ratios fitted on 2019–2021, and 48 excluded-year windows in 2022–2025. These are new regional five-day models, distinct from the released sector/monthly calibration.

| Restriction | Held-out WAPE | Recent Aqua | Recent NOAA-20 | Current support |
|---|---:|---:|---:|---|
| All detected times | 37.81% | 79 | 718 | Pass |
| 12:00–15:00 | 38.98% | 0 | 474 | Fail |
| 13:00–14:00 | 101.16% | 0 | 344 | Fail |

Current window: 8–12 November 2026. The predefined gate requires both sensors to retain ≥20 cell-days and ≥50% of their unrestricted totals. Failed gates produce null estimates and disagreements, not artificial agreement from empty samples. Zero retained detections is not zero overpasses. Different time restrictions also change the quantity being measured, so their errors are not interchangeable estimates of the same target. No causal partition of orbit drift, sensitivity and burning behaviour is established. The released model and its 46.8% discrepancy remain unchanged.

The all-time experimental control estimates 170.09 Aqua-equivalent cell-days, a 115.3% discrepancy; it is not the released estimate of 115.98 with 46.8% discrepancy. All model results, hourly detection histograms, input hashes and individual audit windows are retained in `time-comparison.json` and `time-window-counts.csv`.

JAXA's 10-minute Himawari wildfire product is an independent time-resolved candidate. No product data were obtained. Separate registration and public-release conditions remain unresolved; no account or terms acceptance was performed. [Access conditions](https://www.eorc.jaxa.jp/ptree/registration_top.html), [product guide](https://www.eorc.jaxa.jp/ptree/userguide.html).

## Decision case

Fixed question: what deserves retrospective imagery review in Kalimantan in September 2019?

- Earlier burning: not established. The date at which 10% of full-year observed activity accumulates is 9 August for Aqua and 6 August for adjusted NPP, respectively 17 and 14 days later than the 2003–2017 Aqua median of 23 July. The 5% and 20% markers also shift later. These are retrospective accumulation markers, not ignition dates, operational onset or a forecast. Baseline observation completeness remains unknown. The 2020 marker is explicitly coverage-affected and cannot support an earlier-season claim.
- Unusual period: both sensors support above-median September activity. The default values remain below historical p90. All six processing variants retain the above-median conclusion; the stricter-confidence variant alone moves both sensors above p90. An extreme label is method-sensitive.
- Where to review: screen 0.25° cells with median reference activity ≥5 and both Aqua and adjusted NPP above the cell's September p90. Rank by the smaller excess above the median and retain three centres ≥0.5° apart. Publish every threshold, eligible count, cell bounds and values. This is exploratory regional calibration applied locally, not validated local accuracy, severity, exposure or response priority. Each button opens the exact cell/month in the explorer.
- What could change the conclusion: co-observed clear-sky data, local calibration failures, independent imagery and real analyst evaluation. Landsat corroborates the regional event, not each candidate cell or numerical counts. The small daily-mask rectangle cannot normalize the larger regional brief.

External usefulness validation: **not conducted, 0 participants**, by user instruction. A task-based evaluation protocol is prepared in `submission/analyst-evaluation.txt`; it contains no invented results or endorsements.

## Reproduction

Use existing raw annual files and pinned recheck files from preceding pipelines. `python pipeline/13_quality_calendar.py` queries CMR and downloads the HDF products using existing Earthdata credentials; credentials never enter outputs. `--cached` uses published source identities and verifies hashes. Run `python pipeline/14_time_comparison.py` and `python pipeline/15_decision_case.py` for the timing and decision reports. Never refresh the rolling feed to reproduce the fixed November window: it may no longer contain those dates. Data files retain NASA source terms.

Tests reconcile every published pixel with summary counts/QA, verify partial-granule dates and unavailable-day semantics, test local-time wraparound and support gates, and check candidate eligibility/separation and coverage warnings. Browser tests verify rendering and interpretation boundaries. External ground-truth and usefulness validation remain incomplete.
