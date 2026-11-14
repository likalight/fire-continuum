# Fire Continuum

**One fire history. Different satellites.**

A NASA Space Apps 2026 prototype for [Harmonization of MODIS and VIIRS Hot Spots](https://www.spaceappschallenge.org/2026/challenges/modis-and-viirs-hot-spots/?tab=details). Fire analysts need to distinguish a change in burning from a change in the observing satellite. Fire Continuum makes that distinction inspectable through geographic burning-activity calendars, original observations and an explicit sensor-switch experiment.

**App:** https://likalight.github.io/fire-continuum/

## Geographic extension

[Open the workbench](https://likalight.github.io/fire-continuum/atlas.html): India, Australia and Indonesia, 2003–2025, with worldwide November 1–13, 2026 observations. Ninety annual files support three separately evaluated national models. Arbitrary-day analytics, original-point CSVs, importable geography packages and a local MiniLM evidence assistant are included. [Methods, model results, schema and AI evaluation](submission/geography-and-ai.md). The original Indonesia research application below remains a separate model.

## What works

- Indonesia, island study areas or a custom rectangle; 2003–2025 monthly calendar and map.
- Raw detections, common-grid cell-days and empirically harmonized activity, with one primary platform per period.
- A season briefing using a consistent Aqua baseline, descriptive seasonal categories, original observations and an export carrying sources and limitations.
- A six-step guided demo, a separately corroborated Landsat case study, six interactive processing variants and 13 weekly case-study windows.
- Same-month historical medians, seasonal profiles, animation and concurrent-sensor comparisons.
- Monthly analytics CSV, filtered original hotspot CSV and calendar SVG downloads.
- Source URLs, hashes, version audit, exact method and held-out validation.
- Separate dated November 2026 NRT snapshot; missing archive months are not filled with zeros.

## Evidence

45 NASA FIRMS annual country files supply MODIS Aqua, Suomi NPP VIIRS and NOAA-20 VIIRS observations. On held-out 2022–2025 national months, the NOAA-20 adjustment reduces WAPE against Aqua from **451.04% to 13.45%**. NPP gives **434.09% to 13.70%** over 2018–2025. These are cross-sensor agreement scores, **not accuracy against all fires on the ground**. Additional testing finds poor transfer to some excluded regions and inadequate nominal NPP interval coverage. These failures are displayed, not hidden. Cloud/coverage correction and complete independent ground validation remain unresolved. Separate Landsat imagery corroborates the September 2019 case event, not our aggregate counts.

Read [the additional validation](reports/validation-v2.md), [the corroborated case](reports/case-study.md), and [the complete method](reports/method.md), [validation values](reports/validation.json), [input audit](reports/input_audit.json), [export reconciliation](reports/export_verification.json), and [source manifest](reports/source_manifest.json).

## Reproduce

Python 3.11 and Node 22. No Earthdata login or API key is required for these public annual files.

```sh
python -m venv .venv
# Activate the environment, then:
python -m pip install -r requirements.txt
python pipeline/01_download.py
python pipeline/02_build.py
python pipeline/03_recent.py
python pipeline/04_verify_exports.py
python pipeline/05_robust_validation.py
python pipeline/06_sensitivity.py
python pipeline/07_case_evidence.py
python pipeline/08_case_weeks.py
python pipeline/09_recent_comparison.py
python -m pytest tests -q
cd web
npm ci
npm test
npm run dev
# Production:
npm run build
```

The annual archive download is approximately 493 MB and is ignored by Git. Rebuilding the historical assets is independent of the optional recent feed. `reports/boundary_metadata.json` pins the recent feed's country-mask URL. Files are mutable upstream; the manifest pins the hashes of this submission's downloaded snapshot. The downloader checks advertised sizes; verify hashes against the submitted manifest when reproducing this exact snapshot.

The app is static TypeScript/Vite/MapLibre. Approximately 40 MB of derived data includes 276 on-demand hotspot downloads; the browser initially fetches the 1.34 MB compressed history, metadata and recent snapshot rather than every monthly file. This exceeds the earlier SinkingCities 25 MB target to retain original point-download fidelity. No credentials, raw annual archives or server are deployed. GitHub Actions builds and publishes to Pages.

## Attribution and status

[NASA FIRMS](https://www.earthdata.nasa.gov/data/tools/firms), [annual archive](https://firms.modaps.eosdis.nasa.gov/country/), and [field definitions](https://www.earthdata.nasa.gov/data/tools/firms/active-fire-data-attributes-modis-viirs). We acknowledge LANCE FIRMS, operated by NASA ESDIS with funding from NASA Headquarters. Basemap © OpenStreetMap contributors. Recent-feed mask: geoBoundaries/OSM, ODbL 1.0. NASA does not endorse the project.

Code is MIT licensed; data retain their source terms. OpenAI Codex assisted research, implementation, analysis and writing. This is a hackathon research prototype, not an operational warning service. Submission text and presentation outlines in `submission/` are drafts; no official challenge submission has been made by this repository.

## Date-matched recent comparison

The saved NRT snapshot now supports an explicitly provisional **8–12 November 2026** comparison against those same dates in historical years, using the frozen NOAA-20 calibration. Kalimantan is 2.70 times the historical Aqua median; concurrent Aqua is 1.84 times. Both are above typical, and all five day-omission checks preserve that category. Count agreement is weaker than category agreement. Short-window tests, failed regional diagnostics, same-instrument history, sources and limitations are shown with the result.

Read [recent validation](reports/recent-validation.md) and [the protocol](reports/recent_protocol.json). This extends the product to a dated recent window; it does not provide complete 2026 monthly coverage or validate NRT-versus-standard processing continuity. The saved snapshot is not a live feed. Its compact matched-date history adds about 48 KB compressed.

## Correction audit and observation timing

Seven methods (the original plus six alternatives) now appear alongside their later-year performance and recent disagreement. None reduces the original 46.8% Kalimantan discrepancy. A local method improves a four-region average historical score but worsens this recent comparison; it does not replace the published result. A fresh NASA data check finds no point additions/removals within the fixed window.

The app includes an audited-window replay, a downloadable evidence passport and a fixed Kalimantan timing comparison. Detected daytime observations move from roughly 13:33 to 15:40 for Aqua, while NOAA-20 remains near 13:30. NASA documents Aqua's orbital drift; the point sample does not prove the cause of the count gap. See [correction findings](reports/correction-findings.md), [model protocol](reports/correction_protocol.json) and [day/night protocol](reports/daynight_protocol.json).

Reproduce with `python pipeline/10_correction_trials.py` and `python pipeline/11_daynight_audit.py --cached` when the pinned recheck files are available. Omitting `--cached` explicitly downloads new rolling feed files; later dates may no longer include the fixed study window.


## Observation-aware case and submission materials

[Project overview and demo](https://likalight.github.io/fire-continuum/submission/) introduce the challenge, supported findings and limits. The app now adds daily NASA MYD14A1 observation classes for a fixed southern Kalimantan case, seasonal-window sensitivity, exact analysis links and keyboard calendar navigation. The map loads separately from the analysis code.

Read [daily-mask methods](reports/observation-context.md). Reproduce with `python pipeline/12_observation_context.py` (existing Earthdata access required) or `--cached` after downloading the pinned sources. Native masks provide observation context; no coverage correction is applied to the current comparison. NASA daily product: https://doi.org/10.5067/MODIS/MYD14A1.061.

## Full quality calendar and decision workflow

The expanded calendar publishes 167 native FireMask + QA layers and marks 17 missing dates across August–October 2019/2020. Per-pixel inspection and exact class/QA CSVs preserve unavailable values. Layer dates use HDF metadata, including partial granules. A documented 2020 Aqua outage now constrains annual timing interpretation.

Two fixed local-time restrictions failed the recent support gate; their estimates are withheld. The published correction is unchanged. A four-question retrospective brief adds accumulation-timing sensitivity, three transparent review candidates, a downloadable brief and the evidence that could change each conclusion. External usefulness validation is not conducted (0 participants).

Read [methods and findings](reports/decision-quality-findings.md) and [the protocol](reports/decision_protocol.json). Reproduce with `python pipeline/13_quality_calendar.py` (Earthdata access; use `--cached` for pinned downloads), `python pipeline/14_time_comparison.py`, and `python pipeline/15_decision_case.py`. The approximately 391 KB native-pixel archive loads only when requested. No raw HDF files or credentials are deployed.

## Decision benchmark and transfer evidence

The new opening holds a real case's place/time constant, reveals observation conditions, and leads to the decision brief. The benchmark measures three-category agreement, class-balanced performance, rare-category errors, sample retention and annual peak-window disagreement. Released NOAA-20 category agreement is 82.9% versus simple calibration's 79.6% across 240 region-months, with worse balanced accuracy and more rare-category misses. Read [decision benchmark findings](reports/decision-benchmark-findings.md).

Two additional fixed regions use 60 real NASA annual files: [Punjab and southeast Australia transfer results](reports/transfer-findings.md). Frozen Indonesia coefficients and separate local fits are never conflated. Local calibration improves count error in both regions but worsens Australian category agreement. The explorer remainsIndonesia; the transfer viewer supports only its two declared rectangles.

[Six-cell Landsat audit](reports/imagery-findings.md): 12 independent scene subsets, 3 candidates + 3 lower-activity comparisons, source/QA/hash verification, and 6 inconclusive fire-attribution outcomes. Actual images are inspectable; passing QA does not establish haze-free observations or validate hotspot counts. External practitioners were not contacted.

Reproduce: `python pipeline/16_decision_benchmark.py`, `python pipeline/17_transfer_cases.py --cached`, and `python pipeline/18_imagery_audit.py --cached`. The imagery pipeline additionally uses `requirements-imagery.txt`. Derived imagery adds about 5.7 MB and loads lazily. See each predefined protocol and published source manifest. New results do not change the released coefficients or resolve the 46.8% recent discrepancy.


## Clearer workspace, independent event and month-to-date release

The app now separates the story, calendar, current comparison and evidence library. The six-step tour and glossary introduce concepts without removing the technical detail. Public technical handbook: https://likalight.github.io/fire-continuum/submission/technical-handbook.html . Requirement matrix: https://likalight.github.io/fire-continuum/submission/challenge-coverage.html .

- `pipeline/19_confirmed_case.py`: curated same-place Landsat/FIRMS event demonstration, fixed search log, exact acquisition offsets and original observations. `--cached` reproduces pinned outputs. No ±60-minute match; nearest NOAA-20 is3h47m later. The original six-cell audit is unchanged.
- `pipeline/20_month_to_date.py`: 26 authenticated NASA daily files for November1–13,2026; exact-date history, frozen coefficients, source/date ledger and validation. This is a new date window, not a correction of the older five-day discrepancy.
- `web/src/workspace.ts`, `story.ts`, `current.ts`: four-view navigation, readable case, glossary and current comparison.
- `web/src/export-pack.ts`: versioned analysis ZIP with a calendar visual, model/source provenance and hashes; original-point UTC date-range exports preserve sensor identity.

Continuous 2026 history, global arbitrary AOIs and external practitioner validation remain incomplete. Raw credentials, raw archive files and signed asset URLs are not published.


Rebuild the geographic extension after downloading the existing annual sources and current receipts with `python pipeline/21_geographic_workbench.py`. See its manifest dependencies and country-registration instructions in the extension documentation. Evaluate the local AI from `web/` with `node --experimental-strip-types evaluate-assistant.mjs`. Model files are pinned and hosted locally; no AI API key is needed.
