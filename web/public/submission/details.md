# Current release: a guided fire-season experience

The default homepage now provides 185 plain-language national briefings, saved places, same-date comparisons, explicit assistant tasks, downloadable reports and a compact real-event story. Technical evidence remains one click away. [Guided experience, new observations, privacy and reproducibility](guided-experience.html).

October 2026 is newly available for Mexico and Australia, with both outcomes retained. A full-mask/QA/geolocation audit in western Mexico fails the declared time-match rule and therefore does not normalize coverage. Original production model policies remain unchanged. Continuous global 2026 coverage and completed practitioner validation remain gaps.

# Scientific baseline: global evidence atlas

# Global fire history, with the failures visible

Fire Continuum processes **185 eligible NASA FIRMS country/territory entries**, using **5,550 annual CSV files** from 30 all-country archives. Each entry has a 2003–2025 calendar, its own model evaluation, exact-date analytics, a separate November 1–13, 2026 comparison and source provenance. A country can be processed successfully while its calibration fails.

[Open the global atlas](../atlas.html) · [Download the complete evaluation catalogue](../data/global/catalog.json) · [Frozen screening protocol](../data/global/evaluation-protocol.json)

## Results of this run

|National outcome|Entries|Published primary history|
|---|---:|---|
|Agreement checks passed|9|Aqua then adjusted NOAA-20|
|Limited rare-event evidence|7|Aqua then adjusted NOAA-20|
|Calibration failed checks|109|Aqua only|
|Insufficient evidence|60|Aqua only|

These are prototype screening outcomes, not NASA certification or accuracy against a ground census. The thresholds were recorded before the global results. India, Australia and Indonesia had previously been explored; this is disclosed rather than presented as a fully blind study. No thresholds were relaxed after seeing the global outcome. Entries with too little support remain in the catalogue. No failed country was removed.

## One question a judge can test

**Is this fire season unusual, and would changing the sensor change that answer?** Search for a country. Read its model status before its anomaly. Click a month, inspect the calendar and compare the Aqua and candidate conclusions. Open a failed country: its primary series stays with Aqua, while the candidate error remains visible. Finally compare November 1–13 with exactly those dates in every previous year and download the evidence.

A useful analyst next step is to investigate a period with corroborating instruments and imagery. These data do not support evacuation, dispatch, ignition forecasts or estimated damage. A different outcome after cloud/overpass matching, better independent imagery, or an independently evaluated longer record could change the conclusion. Practitioner usefulness has not yet been tested externally.

## What was processed

Eligibility requires all 23 MODIS annual country files for 2003–2025 and all seven NOAA-20 VIIRS annual files for 2019–2025 in the pinned NASA country catalogue. The 185 names are archive entries, not an assertion that every jurisdiction or land pixel is covered. Some small islands and entries lack the required file series. The catalogue identifies 238 labels overall.

The downloaded ZIPs total 4,384,631,161 bytes; selected source CSVs total 19,690,504,602 advertised uncompressed bytes. Every ZIP has a SHA-256 receipt. Every selected member is read to completion, checked for its advertised length and ZIP CRC, and hashed separately. The raw downloads remain out of Git; scripts and derived public packages are published.

The stream processor reads 75,000 rows at a time and checkpoints each country/instrument/year. It retains Aqua MODIS confidence ≥30 and NOAA-20 nominal/high observations, valid UTC dates/times and coordinates, then applies the mapped country polygon. It removes duplicate date/time/location observations within the instrument. Every exclusion and retained total is recorded; there is no invented observation coverage denominator.

Retained detections are counted separately from activity. Activity counts each occupied 1 km equal-area grid cell once per UTC day. The earliest observation represents a cell-day. Monthly browser maps aggregate these counts into 0.5° cells; a display cell is not a 0.5° fire or a burned-area estimate. Bounding-box selections snap outward and remain clipped to the country's polygon.

## Separate fitting and testing

Four quarterly factors are fitted for each country using 2019–2021. August and September 2020 are excluded because of the documented Aqua outage. A factor is the ratio of Aqua to NOAA-20 occupied cell-days in that quarter's fitting observations. It is withheld as null unless each instrument contributes at least 20 cell-days and there are at least three paired nonzero months. Null never means zero activity.

Testing uses all 48 months of 2022–2025, excluded from fitting. Full screening needs at least 200 reference Aqua cell-days and 24 months with positive historical medians. Historical categories use the same calendar month's Aqua observations from 2003–2017: at/below median, above median, and above p90. The selected year is left out when it belongs to the baseline.

The declared agreement checks are: weighted absolute percentage error (WAPE) ≤25%; absolute aggregate signed bias ≤15%; category agreement ≥80%; improvement over unadjusted cell-days; and recall ≥70% for any category with at least five reference months. At least five reference above-p90 months are required for the full pass status; otherwise passing count/category checks receive the limited-event status. WAPE is sum of absolute monthly candidate-minus-Aqua differences divided by total Aqua cell-days. It is not a confidence interval.

Every country publishes training support, factors, annual test errors, a confusion matrix, category support and recall, rare-month misses, status reasons and all test rows. A calendar fallback never replaces candidate error with the trivially perfect Aqua-versus-itself score. The original Indonesia research model and three earlier geographic packages remain separately reproducible and are not interchangeable with this global release.

## Geographic audit

All 185 archive labels have explicit audited Natural Earth mappings. France uses the metropolitan France/Corsica map unit; French Guiana and Reunion use separate map units. This avoids counting French overseas geometry in multiple entries. Kosovo and Palestine use stable Natural Earth identifiers, not guessed ISO codes. Egypt's invalid geometry is repaired with `shapely.make_valid`; the processed geometry hash is recorded. Fiji, Russia, New Zealand and the United States use a longitude-wrapped map camera. Analysis selections crossing the antimeridian must be split.

Pinned country geometry: [Natural Earth countries](https://raw.githubusercontent.com/nvkelso/natural-earth-vector/9380cca83db5f9aef52d5e762765100745f84b27/geojson/ne_10m_admin_0_countries.geojson). Pinned overseas units: [Natural Earth map units](https://raw.githubusercontent.com/nvkelso/natural-earth-vector/117488dc884bad03366ff727eca013e434615127/geojson/ne_10m_admin_0_map_units.geojson). Natural Earth is public domain. Its boundaries need not exactly match NASA's archive allocation; the input audit publishes boundary exclusions and cannot recover observations omitted upstream.

## Current period and observation limits

The recent comparison uses the separate 26-file November 1–13, 2026 NRT snapshot and matches those 13 dates in each historical year. Both instruments remain separately visible, with candidate coefficients withheld where unsupported. Four historical November windows provide a same-date diagnostic; this is not independent NRT validation. The snapshot is not a live feed, and the rest of 2026 is unavailable. The original November 8–12 Kalimantan 46.8% discrepancy remains unresolved; changing the window or model does not prove it has been corrected.

No detection does not establish no burning. Full FireMask/QA coverage exists only for the earlier fixed case rectangle, not all 185 histories. Global clouds, smoke, overpass frequency and sensor sensitivity are not normalized. Aqua is a reference instrument with its own omissions and changes over time.

## Data packages, exports and reproducibility

`fire-continuum-geography-v2` retains the v1 monthly/daily row layouts and adds `primary_policy`, nullable unsupported factors, status/support/recall, input exclusion audits and `map_bounds`. Primary policy is `aqua_only` or `aqua_then_adjusted_noaa20`. Imports cannot stitch a null coefficient. Imported claims are user-supplied and are not authenticated by this application.

Country packages contain all 276 monthly totals, spatial rows, source SHA-256 hashes, quarterly factors, test results and the current snapshot. Annual daily shards power arbitrary UTC date windows; available windows are 2003–2025 or the separate November 1–13, 2026 interval. An arbitrary-date total does not automatically claim an arbitrary-date historical anomaly. Each country loads on demand.

Download analysis CSV, calendar SVG, reusable package JSON, exact-date analysis JSON, same-date comparison JSON or the all-country evaluation CSV. Original NASA annual CSVs are linked directly and are full-year country files, not date/area-filtered point downloads. Original MODIS files contain both Terra and Aqua; this analysis retains Aqua. The original Indonesia research app preserves its filtered point-export workflow. No overlapping satellites are summed into a trend or global anomaly.

Reproduction prerequisites: the pinned 26 NRT source files in `reports/month-to-date-sources.json` must be present under `data/raw/`; their hashes are checked. They were obtained through the earlier Earthdata-authorized month-to-date pipeline. Rolling NASA NRT endpoints may cease retaining old files; the derived pinned snapshot remains published. The boundary loader retrieves the exact pinned Natural Earth commits when missing. Reproduce the global archives and compilation with `python pipeline/22_global_archives.py`, `python pipeline/23_global_process.py`, then `python pipeline/24_global_publish.py`. The publisher requires all 5,550 checkpoints and reconciles daily, monthly and retained-source totals before completing. Source inventory, archive receipts, label mapping, frozen protocol, source manifest and reconciliation are in `reports/global-*`. Run `python -m pytest tests -q`, `npm --prefix web test` and `npm --prefix web run build`.

## How the supplied NASA portals help

[Data.nasa.gov](https://data.nasa.gov/) is a metadata catalogue that links to the actual archives. [API.nasa.gov](https://api.nasa.gov/) is an API directory; a generic API key does not replace an archive's access requirements. [Earthdata Search](https://search.earthdata.nasa.gov/) is the relevant route to complete science granules. The actual hotspot observations here come from [NASA FIRMS](https://firms.modaps.eosdis.nasa.gov/download/).

The valuable next data expansion is paired MODIS MYD14 and NOAA-20 VJ114IMG fire masks and quality, not extra unrelated APIs. [MODIS documentation](https://www.earthdata.nasa.gov/s3fs-public/2023-09/MODIS_C6_C6.1_Fire_User_Guide_1.0.pdf) distinguishes cloud, unknown and other mask states; [the VJ114IMG catalogue](https://data.nasa.gov/dataset/viirs-jpss1-active-fires-6-min-l2-swath-375m-v002-747d6) identifies the fire-mask product. These are research directions, not globally ingested coverage in this release. [MCD64 burned area](https://modis-land.gsfc.nasa.gov/burn.html) uses active-fire information as well as reflectance, so it is complementary evidence rather than completely independent validation of those same active-fire inputs.


---

# Earlier experiments and implementation history

The following sections preserve prior model results and have narrower geographic scope. The global release above is the current atlas.

# Project details

Challenge: [Harmonization of MODIS and VIIRS Hot Spots](https://www.spaceappschallenge.org/2026/challenges/modis-and-viirs-hot-spots/?tab=details).

Public demo: https://likalight.github.io/fire-continuum/

Source: https://github.com/likalight/fire-continuum

## Approach

Our initial geography is Indonesia, with island study areas and custom rectangular selections. The calendar covers 2003–2025, using Aqua through 2012, Suomi NPP in 2013–2021, and NOAA-20 in 2022–2025. Original detections, a common-grid activity index and adjusted activity can be compared. A separate experiment displays concurrent sensors in the same year, avoiding comparisons that confound a sensor change with a change in weather or burning year.

NASA data: [FIRMS annual country archives](https://firms.modaps.eosdis.nasa.gov/country/), containing MODIS and VIIRS hotspot observations; 45 files are individually attributed in the source manifest. NASA [active-fire definitions](https://www.earthdata.nasa.gov/data/tools/firms/active-fire-data-attributes-modis-viirs) guide interpretation. The separate current snapshot uses FIRMS seven-day Aqua and NOAA-20 NRT files. These observations drive every calendar cell, map, seasonal profile and validation comparison.

Processing uses Python, pandas, NumPy and pyproj. We retain MODIS Aqua confidence >=30 and VIIRS nominal/high, remove duplicate records, and count occupied equal-area 1 km cells per UTC date. VIIRS-to-Aqua ratios are fitted in three longitude sectors and four calendar quarters. Suomi NPP training is 2013–2017; test is 2018–2025. NOAA-20 training is 2019–2021; test is 2022–2025. Full method, factors, validation, simple-factor baseline and reconciliation reports are public.

Frontend: TypeScript, Vite and MapLibre; static deployment on GitHub Pages. No account or API key is needed to explore the precomputed data. Downloads include selected-area monthly analytics, primary-platform original hotspot CSVs and a calendar SVG. OSM provides the basemap. geoBoundaries/OSM supplies an ODbL country mask for the recent feed.

## Validity and limits

National monthly held-out WAPE is 13.70% (NPP) and 13.45% (NOAA-20) against Aqua. A single calibration factor yields 17.35% and 15.46%, respectively. The app also shows regional residuals and selected-area/year comparisons. All 276 monthly point downloads reconcile with the processing ledger, and browser-export aggregates reproduce the held-out scores.

This is an empirical reference-scale index, not distinct fire counts or burned area. Cloud/clear-sky and overpass coverage are not corrected. Confidence categories differ across sensors; collection versions change. Hotspots include industrial and volcanic sources. Small custom areas remain exploratory. The record does not contain complete 2026 archive months, and the recent snapshot is not continuously updated. Global coverage, coverage-aware normalization and independent ground/fire-perimeter validation are future work.

## Attribution and AI use

We acknowledge LANCE FIRMS, operated by NASA ESDIS with NASA Headquarters funding. NASA does not endorse the project. Code: MIT. Source datasets retain their own terms. OpenAI Codex assisted research, code, analysis and writing. Numerical claims come from the supplied reproducible pipeline and NASA input files, not generated example data.

This text is a draft for the team to submit; it is not evidence that an official submission has been completed.

## Additional validation and case study

The revised app includes year-level diagnostics, five region-exclusion tests, whole-year bootstrap intervals, rolling three-year fits, independently evaluated empirical conversion ranges and six refitted grid/filter variants. These are additional diagnostics after the original national results were known, not an untouched final benchmark. NPP range coverage misses its nominal target, and some spatial transfer errors are large; both are exposed in the UI.

The case is Kalimantan September 2019, outside NPP's 2013–2017 fit period, with the following year as a comparison. NASA Earth Observatory's “Smoke Blankets Borneo” supplies a separate Landsat 8 OLI observation dated 15 September 2019. It corroborates event occurrence, not complete count accuracy. The image is credited and displayed unchanged. An interactive test shows that above-median activity persists across six processing variants while the extreme label changes with the confidence filter.

The season briefing now uses only the same-month Aqua 2003–2017 baseline, excluding the selected year. It compares the adjusted primary observation and concurrent Aqua category on that common scale. Historical categories are descriptive, not predictions or risk levels. A six-step guided route links the published event, the sensor comparison, the sensitivity test, the exportable briefing and the failed validation tests. See reports/validation-v2.md and reports/case-study.md.

## Continuity into the present

A provisional 8–12 November 2026 comparison now matches the exact UTC dates in historical years, rather than comparing a partial month against full months. Original NOAA-20 coefficients are frozen from 2019–2021. Forty-eight held-out five-day windows and four exact November windows quantify short-window disagreement, with all regional failures exposed. Kalimantan gives 2.70 times the 15-year Aqua median after adjustment; concurrent Aqua gives 1.84 times. Both descriptive categories survive all five day-omission checks. NRT processing and observational completeness remain unvalidated. The recent result, source dates and limits accompany the season briefing, downloadable analytics and guided demo. See reports/recent-validation.md.

## Correction audit and sensor timing

The recent comparison is stress-tested with six additional corrections. None reduces current Kalimantan disagreement. Methods are evaluated using chronological fit, selection and later audit periods; known prior diagnostics are disclosed. A local calibration improves the macro-average across four regions while worsening Kalimantan's recent count agreement. The prototype preserves the original and exposes all alternatives rather than claiming a solved harmonization problem.

A judge can replay an excluded historical November window, inspect changes in the category, and download an evidence passport containing source identity, model results and unresolved limits. A separate NASA feed recheck finds no changed points in the fixed analysis window. Approximate daytime detection times in the Kalimantan sample show Aqua much later than NOAA-20 in 2026, consistent with NASA's documented orbital drift. This suggests a sampling issue to investigate, not a demonstrated causal correction.

The app now retains full daily fire-mask/QA subsets and tests predefined detection-time restrictions. Paired clear-sky exposure and an independently observed diurnal reference remain future work. Hotspot-only CSVs cannot establish clear-sky exposure, and the project does not claim that it already corrects for it.


## Daily observation context and seasonal planning

The initial 16-day pilot has expanded to 24 NASA LP DAAC MYD14A1.061 granules for August–October 2019 and 2020: 167 available daily layers and 17 explicitly unavailable dates. We retain all ten classes for a fixed 113–114° E, 3–2° S rectangle (14,386 native grid cells). Daily counts preserve cloud, non-fire and missing classifications. Full native FireMask and QA arrays are downloadable and inspectable by pixel; each HDF Dates attribute maps the layers correctly, including partial granules. The selected archive lacks 17 August–2 September 2020, consistent with NASA’s documented Aqua outage. Counts remain null on missing days. The 2020 annual timing marker is coverage-affected and cannot support an earlier-burning claim. The mask is a daily composite, not a clear-sky overpass denominator; it does not normalize FIRMS counts or independently validate the MODIS reference. Coordinate selection matches an independent PROJ transform, and every available day's classes sum to the same grid total. Source granules, hashes, protocol and CSV are public.

The seasonal planner identifies the three-month window with the largest sum of historical Aqua monthly medians and checks whether its start month changes when individual baseline years are omitted. The selected year is excluded from the 2003–2017 baseline when applicable. This is descriptive planning context, not a forecast probability.

Shareable links reproduce the area, selected year/month, displayed date range and data view. Calendar arrow-key navigation supports keyboard analysis. The map library loads separately so numerical analysis can render first.

## Public supporting materials

Project overview: https://likalight.github.io/fire-continuum/submission/

App: https://likalight.github.io/fire-continuum/

Source code: https://github.com/likalight/fire-continuum

A 30-second video uses actual app screens with captions and synthetic narration. OpenAI Codex assisted research, implementation, analysis and writing. No official Space Apps portal submission is implied by publishing these materials.

## Time-aware tests and a decision-focused case

Two predefined local-time restrictions (12:00–15:00 and 13:00–14:00) were fitted on 2019–2021 and audited on 48 five-day windows in 2022–2025. Held-out WAPE was 38.98% and 101.16%, versus 37.81% for a separate unrestricted regional control. Neither restriction improved the score; both retained zero recent Aqua detections and failed the count/retention gate. Their current estimates are withheld. These models differ from the released correction: its 46.8% gap remains unchanged. Zero retained detections does not establish zero overpasses or identify the cause of disagreement. Independent Himawari time-series validation was researched but not completed; access and public-release conditions remain unresolved.

The fixed September 2019 decision brief answers four questions: earlier burning, unusual activity, where to inspect, and what could change the conclusion. The retrospective 10%-of-annual-activity marker is 9 August for Aqua and 6 August for adjusted NPP, 17 and 14 days later than the historical Aqua median. It is not an ignition/onset date or a forecast. Three transparent 0.25° imagery-review candidates open directly in the explorer; their ranking is exploratory, not a severity or operational priority score. A downloadable decision brief carries these limits and sources.

External usefulness validation has not been conducted (0 participants), as requested by the project owner. A task-based analyst evaluation plan is prepared without invented outcomes. The six-step guided demo includes the quality calendar, rejected time correction and explicit decision questions. See reports/decision-quality-findings.md and reports/decision_protocol.json for reproducible methods and every limitation.

## Decision benchmark, external regions and systematic imagery audit

The opening starts with a documented event and a plain-language path into the calendar. Four workspace views separate story, historical exploration, current comparison and technical evidence. The three-stage sensor-switch experiment remains in the evidence library; the guided walkthrough has six chapters.

The decision benchmark tests 710 region-month comparisons across five Indonesian study rectangles (470 NPP, 240 NOAA-20). Against Aqua categories, NOAA-20 agreement improves from 79.6% for simple calibration to 82.9% for the released method. Balanced accuracy worsens from 78.7% to 70.6%; 3 of 6 rare Aqua above-p90 months are missed versus 1 for simple calibration. NPP shows the same trade-off. All methods, confusion matrices, sample retention, regional results and critical-window errors are downloadable. This follow-up uses periods excluded from fitting whose earlier count results had already been inspected; it is not a blind benchmark. See reports/decision-benchmark-findings.md.

Two regions were fixed before their outputs were inspected: Punjab [73.8,29.5,76.9,32.6] and southeast Australia [147,-38,153,-30]. Sixty additional public NASA annual archives (1.61 GB) supply Aqua 2003–2025 and NOAA-20 2019–2025. Frozen Indonesia coefficients are transferred literally, without hemisphere or seasonal adjustments. Separate local quarterly coefficients use 2019–2021, excluding known Aqua outage months; evaluation uses 2022–2025. Punjab category agreement improves 60.4% to 70.8% with local adaptation. Australian WAPE improves 44.1% to 27.1%, while category agreement worsens 72.9% to 66.7%. Both experiments are displayed with monthly inspection and exports. These two bounded cases do not establish global coverage or universal transferability. See reports/transfer-findings.md.

A fixed sample of three Kalimantan review candidates and three lower-activity comparisons now has real Landsat 8 Collection 2 Level 2 August/September scene pairs. Independent OLI reflectance is accessed through the public Microsoft Planetary Computer mirror, with USGS scaling, QA_PIXEL and QA_RADSAT masks, exact georeferencing and input/subset hashes. The published SWIR2/NIR/red panels retain visible clouds/haze; paired NBR decreases are masked for QA-invalid pixels. Five cells pass the engineering QA gate, but all six fire-attribution reviews remain inconclusive. Scene timing, haze and non-fire causes of spectral change prevent treating the pairs as confirmed ground truth. Comparison cells are not assumed fire-free. Review is AI-assisted and non-blinded; practitioner validation is deferred. See reports/imagery-findings.md and the live independent-imagery viewer.

NASA/USGS Landsat data: https://doi.org/10.5066/P9OGBGM6. Source metadata and unsigned public asset URLs are retained. Reproduce with pipeline/16_decision_benchmark.py, pipeline/17_transfer_cases.py (--cached for pinned files), and pipeline/18_imagery_audit.py (--cached for pinned scene subsets; optional requirements-imagery.txt). Raw annual files, raster subsets and access tokens are not published. Code tests, pixel/QA checks, browser review and source hashes support reproducibility, not a claim of independently validated operational accuracy.


## Curated independent success and improved task flow

A separately labelled, retrospectively selected known-event demonstration uses Landsat scene LC08_L2SP_118062_20190915_02_T1 at 02:34:50 UTC, within [113.85,-3.10,113.95,-3.00]. Natural color shows a pale westward plume; a 7/6/2 SWIR display reveals a coherent bright front. Sixteen NOAA-20 observation centres at 06:22 UTC follow the same area, 227.16 minutes later. Zero observations pass the predefined ±60-minute timing check. This corroborates burning at a place/date, not simultaneity, individual count accuracy, fire perimeter or harmonization accuracy. The original six inconclusive reviews are unchanged. A selection log, raw observation CSV/GeoJSON, exact scene provenance, hashes and all temporal offsets are published. See reports/confirmed-case-findings.md.

The app now provides four focused views, a six-step tour, a searchable evidence library, a plain-language glossary and a technical handbook. The calendar surfaces the largest estimated month and complete year in the chosen range, excluding known outage periods from those rankings. Short answers precede expandable methodological details. All earlier experiments remain accessible through stable section links.

## November month-to-date: real daily sources

The pinned current comparison covers 1–13 November 2026 inclusive, the last completed UTC date at retrieval. All 26 expected Aqua/NOAA-20 daily global files were downloaded with the existing Earthdata authorization and checked for actual acquisition dates, schema, sizes, hash and sensor identity. Terra records in the MODIS daily files are excluded. No extra 24-hour settling period is imposed; delayed NRT deliveries remain possible. File availability does not establish complete observation coverage.

The same 13 dates in 2003–2017 supply the Aqua baseline. Frozen original 2019–2021 NOAA-20 coefficients are retained. Standard-archive evaluation uses 2022–2025: 48 all-month 13-day windows and four November 1–13 windows. In Kalimantan, current Aqua records 696 occupied cell-days versus an adjusted NOAA-20 estimate of 620.6; the baseline median is 103, so both categories are above typical. Their magnitude differs by 10.8% relative to Aqua. This is a new date window, not evidence that a correction reduced the earlier November 8–12 gap of 46.8%. Java retains a category disagreement. All outcomes, exact values and thirteen day-omission checks are published.

## Reusable exports and explicit requirements

An analysis ZIP contains selected-range monthly CSV, selected-month original points, calendar SVG, selected-state/units/limits JSON, source manifest, frozen model, input audit and SHA-256 verification. A separate exact-date CSV supports inclusive UTC dates across months and years for the effective selected rectangle; it uses one primary platform per period. Progress, cancellation, schema checks and a 150 MB browser memory bound prevent silent partial output. Original point coordinates/intensities are never individually harmonized. The MTD original-point export retains separate sensor identity.

The public technical handbook documents all processing and evidence levels. A challenge coverage matrix distinguishes implemented features from partial continuous-2026 coverage, bounded geography, monthly harmonized analysis, unknown paired observation coverage and deferred practitioner validation. Code is MIT licensed; source data retain their own terms. External users have not tested usefulness; no NASA adoption, endorsement or measured operational benefit is claimed.


## Geographic workbench and local AI extension

Full extension documentation follows.

Fire Continuum now separates a reusable geographic workbench from its original Indonesia research case. Indonesia was a prototype choice, not a challenge requirement. The workbench loads India, Australia and Indonesia histories, worldwide recent observations, exact-date analytics and an evidence assistant.

[Open the geographic workbench](../atlas.html) · [Original evidence story](../#confirmed-case) · [Requirement assessment](challenge-coverage.html)

## What NASA actually asks

The official [challenge Details](https://www.spaceappschallenge.org/2026/challenges/modis-and-viirs-hot-spots/?tab=details) and Resources tabs were read in the live browser on 14 November 2026 and checked against the supplied full challenge statement. The problem is to make MODIS and VIIRS burning activity comparable across time, then make that record understandable through a web calendar, selectable regions and dates, seasonal peaks, unusual periods, historical/current comparisons and downloadable results. The Resources tab links to [NASA FIRMS](https://www.earthdata.nasa.gov/data/tools/firms).

The brief does not restrict the project to Indonesia and does not require AI. A chatbot alone would not address the harmonization problem. Our assistant helps explain the existing measurements and their limitations; it does not create measurements.

## Geographic coverage and source availability

Three country packages contain 2003–2025 monthly and daily observations. Each uses 23 Aqua annual files and seven NOAA-20 annual files (2019–2025): 90 annual files in total. Each original file is checked against its saved SHA-256 before processing. Packages record source filenames, URLs, versions, hashes, retained counts, model parameters and evaluation rows.

The worldwide map is a separate 1–13 November 2026 UTC snapshot from 26 saved daily NASA files. Aqua and NOAA-20 counts remain separate. Its domain is ±180° longitude and ±86° latitude. It has no worldwide historical anomaly estimate. The existence of every expected source file does not establish clear-sky or overpass completeness. Other 2026 dates are unavailable, not zero activity.

Country filtering uses the same Natural Earth 1:10m administrative polygon for historical country files and global recent files. Natural Earth boundaries are public domain; the exact downloaded boundary file is hashed. Country archives can already omit coastal or border observations before this mask, which applying an identical polygon cannot recover. These cartographic outlines are analytical masks, not an adjudication of territorial claims.

[Coverage, package hashes and recent source ledger](../data/world/catalog.json) · [NASA archive and NRT distinction](https://firms.modaps.eosdis.nasa.gov/download/)

## How the geographic model works

1. Retain MODIS **Aqua only**, confidence ≥30; retain VIIRS **NOAA-20 only**, nominal/high confidence. Preserve coordinates, UTC date/time, satellite, confidence, FRP, day/night, source type and collection/version in original-point exports. Include all retained thermal-source types; the product is not a wildfire-only census.
2. Remove duplicate coordinate/date/time/platform records. Project centres into EPSG:6933 and count each occupied 1 km grid cell once per UTC day. If multiple centres occupy a cell-day, earliest acquisition time, then longitude and latitude, determines its representative display location.
3. Aggregate into 0.5° display cells. Map rectangles snap outward to this grid; printed effective coordinates govern analysis and downloads. These are display bins, not 0.5° satellite pixels. A selected region is still clipped to the loaded country polygon.
4. Fit four country-quarter coefficients: **sum(Aqua cell-days) / sum(NOAA-20 cell-days)** over 2019–2021. Exclude August and September 2020 because of the known Aqua outage. Do not fit on 2022–2025.
5. Use one primary source: Aqua through 2021; adjusted NOAA-20 from 2022. Never add overlapping platforms into a historical trend. The original Indonesia research model, including its Suomi NPP period and six processing variants, remains separate and unchanged.
6. For each calendar month, compare against Aqua values for that month in 2003–2017, excluding the selected year if it belongs to that baseline. Median and linearly interpolated p90 define descriptive categories: at/below median, above median, above p90. A nonpositive median withholds a ratio/category. This is retrospective context, not a causal attribution or prediction.
7. The usual peak is the consecutive three-month window with the largest sum of monthly baseline medians, allowing a year-boundary wrap. It is a historical descriptive season. A country's dominant season can conceal contrasting regional seasons; select an area to explore that variation.

**Known missing observation support:** August–September 2020 remain visibly flagged in the calendar and excluded from fitting and largest-month rankings. Full FireMask/quality data exist only for the original fixed Indonesia study rectangle. No countrywide cloud or overpass normalization is applied.

## Evaluation and claims we can defend

The following compare adjusted NOAA-20 with concurrent Aqua across 48 national months in 2022–2025. WAPE is sum of absolute monthly differences divided by sum of Aqua activity. It is aggregate disagreement, not a per-month confidence interval and not ground-truth accuracy.

|Country|Count disagreement, WAPE|Same descriptive category|Aqua above-p90 months missed|
|---|---:|---:|---:|
|Indonesia|13.22%|95.83%|0 / 0 — no rare cases tested|
|India|17.66%|81.25%|1 / 17|
|Australia|8.71%|89.58%|1 / 5|

These are new national models using a different spatial mask and source schedule from the original experiments. They must not be presented as a direct improvement over the old Indonesia figures or the earlier Punjab/southeast-Australia transfer tests. Those original results remain published. Although the fitting years are separate, earlier transfer outcomes had already been inspected; this is an exploratory extension, not an untouched final benchmark.

The interface recomputes the same diagnostics for selected cells using fixed national coefficients. This does not independently validate every arbitrary small region. Original-point exports and daily/monthly aggregations are reconciled by automated tests. Aqua remains a reference instrument with its own omissions.

Independent imagery has a narrower role: the 15 September 2019 Borneo Landsat front and smoke corroborate burning at a place/date, with 16 NOAA-20 centres 3 h 47 m later. This does not verify the number of fires, simultaneous detection or calibration. The six original inconclusive imagery reviews remain separate.

## Exact dates, current comparison and exports

Historical exact-date windows use daily rows, inclusive UTC dates and one primary platform per period. Invalid dates and windows crossing into unprovided 2026 dates are rejected. The recent comparison uses exactly November 1–13 in every year, not 13 current days against a complete historical month. It exposes both concurrent platforms, historical values, the median/p90, and count disagreement over the four corresponding 2022–2025 windows. Four archive windows do not validate preliminary NRT processing.

Independent recomputation of the supplied national packages gives the following current-period ratios. These are observations with unresolved coverage/timing differences, not a claim that the archive model transfers accurately to NRT:

|November 1–13, 2026|Adjusted NOAA-20 / median|Concurrent Aqua / median|Descriptive outcome|
|---|---:|---:|---|
|India|0.50×|1.10×|Different categories; sensor-sensitive|
|Australia|1.38×|1.23×|Both above typical|
|Indonesia|4.18×|4.65×|Both above typical|

[Exact recent-period values and historical comparisons](geographic-recent-check.json). These national figures are not the original Kalimantan study-area figures.

Downloads include monthly analytics CSV, original monthly or exact-date observation CSV, calendar SVG, reusable geography JSON, arbitrary-date analysis JSON, same-date comparison JSON and assistant answers with sources. Original point downloads are limited to 24 source months per request. They retain source identity and are never individually multiplied by a calibration factor. Share links retain country, bounds, selected month, calendar year range and metric. Imported packages must be shared separately.

The earlier Kalimantan 46.8% November 8–12 discrepancy remains unresolved. Its separate November 1–13 comparison has a 10.8% gap, but a changed window is not a successful correction of the original gap. Geographic-model results are another separate experiment.

## Contract

The import format is `fire-continuum-geography-v1`. Download any supplied package to inspect a complete real example. `years` is the inclusive endpoint pair `[2003,2025]`; `grid_degrees` is `0.5`; `bounds` is west/south/east/north. Each monthly row contains:

```text
year, month, x_half_degree, y_half_degree,
aqua_detections, aqua_cell_days, noaa20_detections, noaa20_cell_days
```

The cell southwest corner is `(x_half_degree/2, y_half_degree/2)`. Values are nonnegative integers; active cell-days cannot exceed detection counts. NOAA-20 fields before 2019 must be zero, indicating an unavailable platform, which the app renders as unavailable rather than a measured zero. The package needs four ordered positive quarterly factors, sources, evaluation metadata, recent data and explicit limitations. Duplicate cell/month rows, invalid coordinates, unsupported years and invalid counts are rejected. Maximum input size is 25 MB; expanded text is bounded at 120 MB after decompression. This is schema validation, not independent source authentication.

Imports stay on the device. Imported source claims and validation are labelled unverified. Monthly exploration works; externally hosted daily/original-point shards are intentionally not fetched from a user-supplied URL. Exact-date and recent-history buttons explain that those features require the supplied source shards. Treat imported coefficients and metadata as untrusted scientific assertions until independently reproduced.

To add a country reproducibly: acquire Aqua 2003–2025 and NOAA-20 2019–2025 annual files, record and verify their source hashes in the download manifests, add its Natural Earth ADM0_A3 mapping to `COUNTRIES` in `pipeline/21_geographic_workbench.py`, run that compiler, inspect all excluded-year results and rare-category misses, then register the package in the catalogue and geography selector. The compiler currently requires these complete years and positive overlap support; sparse or incomplete regions require an explicit availability-aware schema extension. The import contract is generic, but that is not equivalent to already having global historical data.

## Evidence assistant: real AI, bounded answers

The assistant uses [Xenova/all-MiniLM-L6-v2](https://huggingface.co/Xenova/all-MiniLM-L6-v2), a quantized sentence-embedding model under Apache-2.0. Revision: `751bff37182d3f1213fa05d7196b954e230abad9`. The model artifact is 22,972,370 bytes, plus tokenizer/configuration and the separately loaded inference runtime. Files are self-hosted with [source URLs and SHA-256 hashes](../models/minilm/manifest.json).

[Transformers.js](https://huggingface.co/docs/transformers.js/pipelines) 4.3.2 runs the model in a browser worker through ONNX Runtime Web 1.31.0-dev.20260914-8d85527a0. Mean-pooled, normalized 384-dimensional embeddings match the question to authored evidence-topic examples using cosine similarity. A fixed 0.42 threshold withholds unsupported matches. Similarity is not calibrated confidence. Query matching does not calculate observations, anomalies or validation statistics.

Answers are deterministic text populated from the selected analysis and linked evidence. Once the geographic same-date comparison is computed, the assistant can explain that selected recent result, including category disagreement; changing the area clears that context. This is **semantic retrieval, not open-ended generative chat**. It cannot run commands, change source measurements, retrieve arbitrary private documents, predict future fire locations or provide operational decisions. Model files load from the site; questions are not sent to an AI service. Normal map/network requests still occur. If inference cannot load or exceeds its timeout, clearly labelled keyword evidence search remains available.

The development evaluation contains 25 authored question fixtures and two scope guards. Initial semantic routing passed 17/25; after expanding intent examples it passed 22/25. The final result still includes two withheld supported questions and one selected-period question routed to the seasonal explanation. These are **development fixtures reused during tuning**, not external-user accuracy or held-out validation. Three unrelated questions were withheld and both scope guards fired. Source-cited deterministic answers limit fabricated measurements, but a wrong topic can still be unhelpful. Users should inspect the selected context and cited evidence. External practitioner testing remains deferred, with zero participants.

Reproduce the model check from `web/` with `node --experimental-strip-types evaluate-assistant.mjs`. Model and runtime licenses are distributed alongside their artifacts. The report preserves both initial and final development results. A chatbot is supplementary; credible measurements, understandable comparisons and reproducible exports carry the scientific claim.

## What remains incomplete

Continuous 2026 history, worldwide calibrated history, paired clear-sky/overpass normalization, robust treatment of all sensor drift and timing effects, and external practitioner usefulness validation remain incomplete. The workbench is a substantially broader research prototype, not globally validated monitoring infrastructure. No NASA endorsement, adoption or competition result is claimed.


## Engineering and browser verification

The release passes 60 Python data/scientific tests and 44 frontend tests, plus TypeScript compilation and a production build. A separate artifact-integrity test verifies the pinned AI and runtime bytes. The production dependency audit reports no known vulnerabilities at the time checked. Passing engineering tests does not establish scientific ground truth.

Browser checks exercised all three country packages, worldwide recent counts, exact-date calculation, the same-date comparison, local AI topic matching, an unrelated-question abstention, and the deployed AI. An actual downloaded India November 2023 observation CSV was independently read and reconciled: 58,496 records. At a narrow viewport, DOM measurements showed one map/brief column and no horizontal page overflow; a complete mobile visual/accessibility audit was not completed.

The file-import chooser could not be automated because the browser extension did not have file-URL access. No extension permission was changed. Browser automation subsequently stopped because it could not confidently determine the active URL. The schema/round-trip data checks pass, but the browser file-import flow and final clipboard interaction are not claimed as fully verified. The final selected-current-context enhancement is covered by a unit test; it was added after UI automation stopped. The existing 30-second film illustrates the original evidence story; the live workbench and this chapter document the geographic/AI extension.
