# Technical handbook

## The question and the units

Fire Continuum helps users inspect seasonal patterns across a change in satellite instruments. It does not estimate the number of distinct fires, burned area, damage or danger.

|Quantity|Meaning|Use|
|---|---|---|
|Original detections|Retained thermal-anomaly pixels, with original date, time, platform, confidence, FRP and version|Inspect and download observations; do not directly compare instruments as a trend|
|Occupied cell-days|At least one retained detection in a 1 km equal-area cell on one UTC day, per platform|Reduce repeat sampling and some resolution differences|
|Aqua-equivalent activity|VIIRS occupied cell-days multiplied by a fitted positive overlap ratio|Estimate a common historical activity scale; uncertainty remains|
|Median ratio|Selected activity divided by the same-month or identical-date Aqua baseline median|Describe relative detected activity; not danger or statistical significance|

**Separate claims:** independent imagery supports the presence of burning at one location/date. The regional calendar supports an above-typical activity estimate. Cross-sensor tests measure comparability. No single piece of evidence proves all three.


## User journey and scope

1. **The story:** inspect a documented Landsat fire front, reveal infrared and add later hotspot centres.
2. **Explore the calendar:** select an Indonesia study area or effective 0.25° rectangle; choose years and click a month. Read the typical peak, relative activity and sensor-category agreement.
3. **Current comparison:** November 1–13, 2026 is compared with exactly November 1–13 historically, with a 26-file date/sensor ledger. A previous November 8–12 experiment is retained separately.
4. **Evidence & methods:** search questions and open the relevant experiments. A term guide explains units and metrics.

Archive: 2003–2025. Current coverage: a pinned November 1–13 snapshot. **January–October 2026 and November 14 onward are unavailable, not zero.** Arbitrary global AOIs and a continuous 2026 archive are not implemented. Punjab and southeast Australia are separate fixed-region transfer tests.

Date controls select calendar years and a month; exact UTC day ranges are supported for original observation downloads. The main harmonized calendar remains monthly.


## Harmonization and source conventions

# Fire Continuum: method and validation

Snapshot prepared 14 November 2026. Research prototype for **Harmonization of MODIS and VIIRS Hot Spots**, NASA Space Apps 2026. Geography: Indonesia. This is a sensor-comparability experiment, not a validated census of fires.

## Sources and provenance

We use 45 public [NASA FIRMS annual country files](https://firms.modaps.eosdis.nasa.gov/country/): MODIS 2003–2025, VIIRS Suomi NPP 2012–2025, and VIIRS NOAA-20/JPSS-1 2018–2025. The [annual catalog](https://firms.modaps.eosdis.nasa.gov/data/country/yearly_summary_files.txt) supplies filenames, sizes and modification dates. `sources.json` records each URL, advertised size, locally calculated SHA-256 and retrieval time. Hashes identify our local inputs; NASA did not provide the hashes. `input_audit.json` records retained counts, dates and source version values. Different versions occur across this record; we do not describe the entire record as a single collection.

Field interpretation follows [NASA's MODIS/VIIRS attribute definitions](https://www.earthdata.nasa.gov/data/tools/firms/active-fire-data-attributes-modis-viirs). A hotspot is a detected thermal-anomaly pixel. It is neither a distinct fire nor a burned-area measurement. Coordinates locate a pixel center, not an exact fire perimeter. Industrial, volcanic and other thermal sources remain included.

## Processing

1. Keep **Aqua only** from MODIS. Terra is excluded rather than adding morning and afternoon platforms. Aqua, Suomi NPP and NOAA-20 remain separate. Choosing afternoon platforms reduces a major observation-schedule difference, but does not align every overpass or correct sampling frequency.
2. Retain MODIS confidence >=30; retain VIIRS nominal/high (`n`/`h` in annual files; `nominal`/`high` in the recent feed). These are different sensor-specific screens, not identical detection probabilities. Drop exact duplicate latitude/longitude/date/time/satellite records.
3. Project coordinates from EPSG:4326 to EPSG:6933. Floor projected x and y divided by 1,000 to define a global-origin equal-area 1 km grid. Count an occupied grid cell once per UTC date per platform, combining day and night. The result is **active cell-days**, not burned square kilometres. This suppresses repeated observations and part of the resolution difference; it does not turn VIIRS into a physical MODIS measurement.
4. Assign each active cell-day to the 0.25-degree display cell of its earliest-time retained detection. At cell boundaries this representative-point convention can shift a contribution between neighboring display cells. Original detection counts use their original coordinates. Consequently a small-area point count and an active-cell measure need not have identical boundary membership.
5. Fit positive multiplicative ratios separately for three longitude sectors (<108 E, 108–120 E, >=120 E) and four calendar quarters. Each ratio is `sum(Aqua active cell-days) / sum(VIIRS active cell-days)` in training months. Multiplication preserves zeros; no intercept or fabricated hotspot is introduced.
6. Suomi NPP fits 2013–2017 and is tested on **2018–2025**. NOAA-20 fits 2019–2021 and is tested on **2022–2025**. Freeze the fitted ratios before evaluating later years. Partial launch years 2012 (NPP) and 2018 (NOAA-20) do not enter fitting or the primary VIIRS record.
7. Display a single primary source per period: Aqua 2003–2012, NPP 2013–2021, NOAA-20 2022–2025. Do not sum overlapping platforms. Adjusted units are **Aqua-equivalent active 1 km cell-days**. Original detections and unadjusted cell-days remain available for comparison.

The start year is 2003, the first full calendar year after Aqua's 2002 launch; this prototype does not extend the combined record to Terra's 2000 start. All dates and day aggregation are UTC. At Indonesia's latitudes 0.25 degrees is approximately 28 km; the display grid itself is not equal-area.

## Held-out results

| Comparison with Aqua | Fit years | Test years | Months | Before WAPE | After WAPE |
|---|---|---|---:|---:|---:|
| Suomi NPP | 2013–2017 | 2018–2025 | 96 | 434.09% | 13.70% |
| NOAA-20 | 2019–2021 | 2022–2025 | 48 | 451.04% | 13.45% |

WAPE = `sum(abs(estimate - reference)) / sum(reference)`, evaluated on national monthly totals. “Before” already uses the common 1 km cell-day grid; it is not the original raw-pixel count. Large pre-adjustment values mean VIIRS observes substantially more occupied cells than Aqua. They do not mean NASA's VIIRS data are wrong.

Regional-sector after-adjustment WAPE spans 14.82–17.72% for NPP and 14.10–17.87% for NOAA-20. National aggregation can cancel opposite regional biases. The scores are **not 86.5% fire accuracy**, a per-month confidence interval, or independent ground truth. Aqua itself misses events and has observation gaps. The experiment shows empirical agreement with Aqua's scale on later years. A simpler single national factor, fitted on exactly the same training years, gives held-out WAPE of 17.35% for NPP and 15.46% for NOAA-20. The regional-quarter method improves these to 13.70% and 13.45% respectively. This is one baseline comparison, not proof of superiority to all alternatives. See `ablation.json`.

The browser data was independently summed back to all 1,620 sector/month/sensor ledger rows. All 276 monthly point-download counts match the ledger. Held-out WAPE recomputed from the browser export matches the pipeline result. See `reports/export_verification.json` and `reports/validation.json` in the repository.

## Calendar, anomalies and exports

The seasonal baseline now uses only Aqua observations for each calendar month during 2003–2017 in the chosen area, excluding the selected year. This replaces the original mixed-sensor baseline. Raw/unadjusted views no longer show a cross-sensor anomaly ratio. The displayed anomaly is a ratio to that median. It is descriptive, not a forecast or statistical significance test. The briefing always uses adjusted activity and the consistent Aqua baseline, regardless of the calendar view. Harmonized historical estimates still depend on the calibration's transferability. Calendar colors use a logarithmic scale over the displayed years. Map colors rescale per selected month and must not be compared visually across months as an absolute scale.

User-selected rectangles snap outward to 0.25 degrees. Historical points are already assigned to Indonesia by FIRMS. Sector-level calibration has not been validated for every arbitrary small rectangle. Empty cells mean no retained detections in the available input, not verified absence of fire. The CSV analytics include source platform, raw count, cell-days, adjusted estimate, Aqua reference and selected bounds. The hotspot CSV contains filtered original observations from the primary platform for the selected month; it does not adjust individual point positions or intensities.

## Recent observations and gaps

Annual history ends December 2025. The separately dated seven-day FIRMS NRT snapshot is retrieved by `03_recent.py`; it is **not a live service**, complete 2026 archive or complete current month. Both global-file date spans and retrieval time are stored in `recent.json`. Recent records are masked to Indonesia using geoBoundaries/OSM (ODbL 1.0); that border assignment may differ from FIRMS annual country files. Recent counts remain unharmonized and are never appended to a historical full-month calendar cell.

[NASA reports cessation of new Suomi NPP observations on 2 November 2026](https://www.earthdata.nasa.gov/data/alerts-outages/reminder-new-suomi-npp-observations-cease-november-2-2026). The need for an explicit sensor handover is therefore current, but our NOAA-20 choice is not a claim of perpetual future availability.

## Unresolved limitations and next validation

- Hotspot-only files provide no clear-sky, cloud-mask, swath or overpass denominator. Cloud and observation gaps are not corrected.
- No exact time-of-day matching; combining UTC-day detections only partially addresses sampling differences. Diurnal fire cycles remain a confounder.
- Collection/version transitions, scan-angle effects, geolocation differences, fire size and intensity are not individually modeled.
- Ratios can hide real differences in the small/low-intensity sources detected by VIIRS. They are a reference-scale index, not a reconstruction of every fire.
- Quarter boundaries can produce artificial steps. Additional empirical conversion-range tests failed to establish universal nominal coverage; no per-AOI guarantee is claimed.
- Global expansion, 2026 full-archive ingestion, independent fire-perimeter/ground validation and coverage normalization remain future work. Single-factor ablation, rolling temporal tests, spatial exclusion tests and six processing sensitivities are now reported in validation-v2.md / robustness.json / sensitivity.json.

We acknowledge data from LANCE FIRMS, operated by NASA's Earth Science Data and Information System with funding from NASA Headquarters. Source data retain their source terms. NASA does not endorse this project.

## Additional evidence and changed claims

See [validation-v2.md](https://github.com/likalight/fire-continuum/blob/main/reports/validation-v2.md) for year-level, spatial-transfer, range-coverage and sensitivity results, including failures. The Kalimantan September 2019 case uses a separate NASA-published Landsat observation to corroborate event existence only. See [case-study.md](https://github.com/likalight/fire-continuum/blob/main/reports/case-study.md). The original harmonization coefficients remain unchanged.


## Independent known-event case

# A real fire, seen by a different instrument

The 15 September 2019 Landsat 8 scene provides a defensible positive demonstration of burning in a small part of southern Borneo. The displayed shortwave-infrared composite shows a coherent bright front, while the same geographic window in natural color shows a pale plume extending westward. NOAA-20 observations acquired later that UTC date fall along and near the visible front. NASA Earth Observatory independently described active fires in this Landsat scene and used bands 7/6/2 to highlight them in its [Smoke Blankets Borneo article](https://science.nasa.gov/earth/earth-observatory/smoke-blankets-borneo-145614/).

This corroborates **burning at this place and date**. It does **not** validate the regional anomaly, hotspot counts, calibration accuracy, burned area, or individual FIRMS detections. This example was deliberately selected after inspecting imagery from a known event; it is not a representative accuracy test.

## Exact observations

- Landsat scene: `LC08_L2SP_118062_20190915_02_T1`, OLI, **02:34:50.651419 UTC**.
- Bounds: **113.85–113.95°E, 3.10–3.00°S**, north up, EPSG:4326.
- Display: 360 × 360 grid, approximately 31 m spacing; actual band subsets, no generated imagery.
- Bright front: near 113.927°E, 3.025°S, with a longer bright edge continuing southward. This approximate visual location is not a digitized perimeter or a ground-truth annotation.
- Nearest FIRMS pass: **NOAA-20, 06:22 UTC**, 16 nominal/high-confidence observations in the crop, **227.16 minutes later**.
- The predefined **±60-minute** comparison contains **zero** observations. The time window was not widened to obtain a match.

| Platform | Same-date observations in crop | UTC times | Closest offset after Landsat |
|---|---:|---|---:|
| MODIS Aqua | 2 | 17:20 | 14 h 45 m |
| VIIRS S-NPP | 27 | 18:16 | 15 h 41 m |
| MODIS Terra | 4 | 14:22 | 11 h 47 m |
| VIIRS NOAA-20 | 51 | 06:22, 17:24, 17:25 | 3 h 47 m |

These are sensor observations, not separate fires. The table preserves satellite identity; the counts must not be added together as a fire total. The transparent overlay contains only the nearest NOAA-20 pass and represents point centres, not pixel footprints or fire perimeters. Fire evolution and footprint differences can explain spatial offsets between acquisitions.

## Display and quality limits

Natural color uses Landsat bands 4/3/2; shortwave infrared uses 7/6/2. Both use the same fixed display transform: `clip((DN × 0.0000275 − 0.2) / 0.45, 0, 1) ** 0.7`. Scaling follows [USGS Level 2 documentation](https://www.usgs.gov/faqs/how-do-i-use-a-scale-factor-landsat-level-2-science-products). Cropping preserves the original subset's pixel boundaries; there is no cosmetic sharpening, generated fill, or selective masking.

The displayed data are Collection 2 Level 2, accessed through the public Planetary Computer mirror. They support a qualitative visual interpretation; this pipeline does not apply a Level 1 active-fire algorithm to Level 2 surface reflectance. Burning pixels contain emitted radiation, and atmospheric correction and saturation can distort their values. The bright colors are not temperature, fire intensity, or a quantitative burn classification.

QA_PIXEL flags cloud or related conditions in about **0.0031%** of the crop, while **0.1852%** carries a SWIR saturation flag. Nevertheless, natural-color imagery is visibly smoke-obscured. This is a useful reminder that low QA cloud coverage does not imply clear ground visibility. [USGS documents these QA flags](https://www.usgs.gov/landsat-missions/landsat-collection-2-quality-assessment-bands); they do not measure fire extent. Clouds, haze and saturated pixels remain visible in the composites rather than disappearing from the evidence.

## Selection history and reproducibility

The protocol was written before the three-region imagery inspection. This was a retrospective demonstration from the outset: east-river and north-fields were inspected, then west-river was selected because its bright front and plume were visually clearer. The final crop was chosen after inspection. The public Level 1 catalog search returned no applicable Landsat 8 scene; this limitation and all three inspected regions are recorded in `confirmed-case-search-log.json`.

The prior fixed six-cell NBR audit is preserved unchanged: **0 corroborated, 0 contradicted, 6 inconclusive**. A curated active-burning illustration does not retroactively improve that audit or provide a success rate. Review here is AI-assisted and non-blinded, with no independent practitioner review.

Run `python pipeline/19_confirmed_case.py --cached` after the FIRMS archives and pinned Landsat subset are present. Without `--cached`, the pipeline can retrieve the same public Landsat subset. The script checks the scene acquisition time, verifies FIRMS archives against their download manifest, pins array and output hashes, retains exact source CSV lines, publishes unsigned asset URLs, and reports all acquisition times. The original model and its coefficients are untouched.

Published artifacts are `confirmed-case.json`, `confirmed-case-natural.png`, `confirmed-case-swir.png`, `confirmed-case-overlay.png`, `confirmed-case-panel.png`, and downloadable point CSV/GeoJSON. The scene, processing, QA diagnostics, exact dates, limits and provenance are embedded in the JSON.


## Current month-to-date comparison

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


## Decision benchmark

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


## External-region transfer

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


## Original six-cell audit

# Six-cell independent Landsat imagery audit

## What was completed

A fixed six-cell sample now has real, georeferenced independent optical evidence: the three existing September 2019 Kalimantan review candidates and three systematically selected lower-activity comparisons. Twelve Landsat 8 Collection 2 Level 2 subsets were obtained from the public Microsoft Planetary Computer mirror of USGS data, without creating an account or accepting new terms. Full cell bounds, exact acquisition times, item identifiers, unsigned source URLs, STAC hashes and subset-array hashes are published in `imagery-audit.json`.

Each scientific figure shows the same cell before and during September: a SWIR2/NIR/red reflectance composite and a change image using the normalized burn ratio (NBR). This is a systematic **independent-imagery audit**, not completed ground-truth validation of the hotspot estimates.

## Fixed sampling and scene selection

The selection protocol was written before optical retrieval or visual inspection. The three candidate cells come from the existing published hotspot ranking. For each in rank order, choose the nearest unused 0.25° cell whose historical September Aqua median is at least five cell-days and whose September 2019 Aqua and adjusted NPP counts are both at or below that median. Ties use longitude then latitude. Comparisons are lower-activity cells; they are **not known fire-free controls**.

For each cell, search Landsat 8 in August and September 2019. Require at least 95% scene-footprint overlap. Select the lowest scene cloud fraction, then proximity to the 15th and item ID. Scene choices were never replaced based on visual outcomes. Dates differ between cells because the satellite paths and scene availability differ.

## Results

| Cell | Before → during | Paired QA-valid fraction | Fire-attribution outcome |
|---|---|---:|---|
| Candidate 1 | 5 Aug → 6 Sep | 28.38% | Inconclusive: localized disturbance-like changes, cloud gaps and ambiguous attribution |
| Candidate 2 | 14 Aug → 15 Sep | 45.04% | Inconclusive: substantial cloud and haze/smoke contamination |
| Candidate 3 | 14 Aug → 15 Sep | 93.01% | Inconclusive: visible haze despite passing pixel QA; surface-change attribution remains ambiguous |
| Comparison 1 | 5 Aug → 6 Sep | 4.17% | Inconclusive: fails the predefined 20% paired-valid engineering gate |
| Comparison 2 | 23 Aug → 8 Sep | 27.64% | Inconclusive: no unambiguous fire evidence, but limited coverage cannot establish absence |
| Comparison 3 | 14 Aug → 15 Sep | 55.50% | Inconclusive: coastal water, haze and atmospheric effects confound change |

**0 corroborated, 0 contradicted, 6 inconclusive** for cell-level fire attribution from these fixed image pairs. These outcomes are not an accuracy estimate or proof that the underlying hotspot detections are wrong. The audit does not upgrade the three review candidates into independently verified fires. The existing NASA Earth Observatory account remains separate corroboration of the broader regional event.

The useful finding is that a high proportion of QA-valid pixels can coexist with visibly hazy imagery. Candidate 3 has 93% paired QA-valid pixels, yet substantial haze remains. QA flags alone therefore cannot establish clean independent validation. Reviewers can inspect the images instead of trusting a summary score.

## Processing and interpretation

USGS surface-reflectance scaling is applied: DN × 0.0000275 − 0.2. Each cell is resampled with nearest neighbour to a 900×900 EPSG:4326 grid, approximately 31 m at this latitude. This is a display/diagnostic grid, not an area measurement or a fire perimeter. Composites use SWIR2/NIR/red reflectance divided by 0.45 and gamma 0.7; clouds/haze remain visible. The fixed display mapping is identical across scenes.

For the paired diagnostic, exclude QA_PIXEL bits 0–5 (fill, dilated cloud, cirrus, cloud, shadow, snow), any QA_RADSAT flag, zero band values and reflectances outside [0,1]. NBR = (NIR − SWIR2)/(NIR + SWIR2); the denominator must be positive. Gray change pixels are unavailable under these checks. The 20% paired-valid threshold is an engineering gate, not a statistical validity guarantee.

NBR decreases can reflect burning, vegetation removal, moisture changes, clouds, haze and other effects. The descriptive >0.1 decrease fraction is **not** a burn classifier. The primary diagnostic includes water. After initial inspection exposed water effects in comparison 3, a separate land-only median was added by excluding QA_PIXEL water bit 7 in either image; the original diagnostic was retained. This post-inspection amendment is explicitly recorded in the protocol. No sample, scene, gate or classification rule changed.

The visual review was performed by an AI assistant with knowledge of the cell roles; it was **not blinded**, and no external analyst participated. Burn scars cannot establish an active-fire timestamp. The selected pairs do not isolate burning within September from changes since August. No hotspot total, harmonization coefficient, error bound or investigation priority is validated by this audit.

## Reproduce and inspect

Run `python pipeline/18_imagery_audit.py` after installing rasterio 1.4.4 and matplotlib 3.11.2 alongside the existing scientific dependencies. `--cached` uses the saved catalog and raster subsets and verifies their published array hashes. The first run queries the public STAC API; public asset-access tokens stay in memory and are never written into outputs. Twelve raw subsets and the full STAC response remain in ignored `data/raw/`; only six scientific figures, compact provenance, protocols and results are published.

`imagery_reviews.json` records the explicit visual findings and reviewer status. `imagery-verification.json` records numerical/artifact checks. Reproducing imagery figures can change PNG hashes across plotting-library versions; raw array hashes preserve the actual input values.

Primary references: [USGS scale factors](https://www.usgs.gov/faqs/how-do-i-use-a-scale-factor-landsat-level-2-science-products), [USGS QA definitions](https://www.usgs.gov/landsat-missions/landsat-collection-2-quality-assessment-bands), [USGS Collection 2 Level 2](https://www.usgs.gov/landsat-missions/landsat-collection-2-level-2-science-products), [Planetary Computer public access](https://planetarycomputer.microsoft.com/docs/).


## Observation masks and time matching

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


## Exports and reproducibility

The **analysis ZIP** contains monthly analytics for the chosen year range, original primary-platform observations for the selected month, a calendar SVG, effective bounds and selected state, units, the frozen model, source manifest and SHA-256 hashes. The distinction between the selected-month points and the full-range monthly analytics is explicit in README.txt and analysis.json.

The **exact-date original-observation CSV** uses the currently selected effective rectangle and the stated inclusive UTC dates. It retrieves one primary-platform file per month, applies date/coordinate filters, retains original fields and never sums platforms. Errors/cancellation do not produce a partial file. A 150 MB browser limit directs larger jobs to the Python pipeline.

The **month-to-date CSV** retains Aqua and NOAA-20 columns separately. Its original-observation CSV retains a sensor column. No single combined fire count is produced.

Source hashes identify the retrieved input bytes; hashes do not prove scientific accuracy. The project uses MIT-licensed code; original source data retain their own terms. NASA/USGS and FIRMS attribution remains required by the source context.

### Reproduce

```text
python -m pytest tests -q
npm --prefix web ci
npm --prefix web test
npm --prefix web run build
python pipeline/19_confirmed_case.py --cached
python pipeline/20_month_to_date.py
```

Read each pipeline's arguments and source requirements before running. The case pipeline uses optional imagery dependencies from requirements-imagery.txt. Daily NASA files require an authorized Earthdata session; credentials are never published. Raw archives are ignored by Git. Full pipeline order and initial downloads are documented in the repository README.

### Public contracts

- `../data/metadata.json`: frozen model and original validation.
- `../data/history.json.gz`: sparse historical display aggregates; see the pipeline for field schema and representative-point conventions.
- `../data/month-to-date.json`: date window, source ledger, baseline, diagnostic tests, model and derived-file hashes.
- `../data/month-to-date-history.json.gz`: nine-column sparse arrays; column names are carried in month-to-date.json.
- `../data/confirmed-case.json`: scene identity, fixed bounds, observation offsets, display assets, separate event claim and source hashes.
- `analysis.json` inside each user export: versioned `fire-continuum-analysis-pack-v1` selected-state contract.

Sparse zero counts are counts of retained detections in available inputs. They must not be reinterpreted as complete clear-sky observation or proof of no burning.


## What would be needed for agency use

The prototype is inspectable and reproducible, but adoption has not been established. The next validation gates are concrete:

1. A task-based study with fire analysts or land managers: comprehension, correct rejection of unsupported conclusions and practical usefulness. **Deferred; zero participants.**
2. Prospective NRT-to-standard comparisons after final products arrive, with a frozen protocol and freshness/outage monitoring.
3. Paired observation-opportunity masks for both sensors before estimating coverage-normalized activity.
4. Broader geographic and regime coverage, external reference labels and uncertainty appropriate to each decision, with explicit failure cases.
5. Production engineering: data update service, versioned releases, operational monitoring, accessibility evaluation, performance budgets and maintenance ownership.

No NASA endorsement, agency adoption, measured time savings, operational forecasting performance or global accuracy is claimed. A curated visual success is not representative validation.
