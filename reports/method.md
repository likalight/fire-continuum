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
