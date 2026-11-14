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
