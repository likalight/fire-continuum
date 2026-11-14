# Project details — draft

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

The next scientific priority is a coverage- and observation-time-aware calendar using full fire-mask/quality data and an independently observed diurnal reference. This remains future work. Hotspot-only CSVs cannot establish clear-sky exposure, and the project does not claim that it already corrects for it.
