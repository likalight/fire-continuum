# Fire Continuum

**One fire history. Different satellites.**

A NASA Space Apps 2026 prototype for [Harmonization of MODIS and VIIRS Hot Spots](https://www.spaceappschallenge.org/2026/challenges/modis-and-viirs-hot-spots/?tab=details). Fire analysts need to distinguish a change in burning from a change in the observing satellite. Fire Continuum makes that distinction inspectable through Indonesia's monthly burning-activity calendar, original observations and an explicit sensor-switch experiment.

**App:** https://likalight.github.io/fire-continuum/

## What works

- Indonesia, island study areas or a custom rectangle; 2003–2025 monthly calendar and map.
- Raw detections, common-grid cell-days and empirically harmonized activity, with one primary platform per period.
- Same-month historical medians, seasonal profiles, animation and concurrent-sensor comparisons.
- Monthly analytics CSV, filtered original hotspot CSV and calendar SVG downloads.
- Source URLs, hashes, version audit, exact method and held-out validation.
- Separate dated November 2026 NRT snapshot; missing archive months are not filled with zeros.

## Evidence

45 NASA FIRMS annual country files supply MODIS Aqua, Suomi NPP VIIRS and NOAA-20 VIIRS observations. On held-out 2022–2025 national months, the NOAA-20 adjustment reduces WAPE against Aqua from **451.04% to 13.45%**. NPP gives **434.09% to 13.70%** over 2018–2025. These are cross-sensor agreement scores, **not accuracy against all fires on the ground**. Small-area performance, cloud/coverage correction and independent ground validation remain unresolved.

Read [the complete method](reports/method.md), [validation values](reports/validation.json), [input audit](reports/input_audit.json), [export reconciliation](reports/export_verification.json), and [source manifest](reports/source_manifest.json).

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
python -m pytest tests -q
cd web
npm ci
npm run dev
# Production:
npm run build
```

The annual archive download is approximately 493 MB and is ignored by Git. Rebuilding the historical assets is independent of the optional recent feed. `reports/boundary_metadata.json` pins the recent feed's country-mask URL. Files are mutable upstream; the manifest pins the hashes of this submission's downloaded snapshot. The downloader checks advertised sizes; verify hashes against the submitted manifest when reproducing this exact snapshot.

The app is static TypeScript/Vite/MapLibre. Approximately 40 MB of derived data includes 276 on-demand hotspot downloads; the browser initially fetches the 1.34 MB compressed history, metadata and recent snapshot rather than every monthly file. This exceeds the earlier SinkingCities 25 MB target to retain original point-download fidelity. No credentials, raw annual archives or server are deployed. GitHub Actions builds and publishes to Pages.

## Attribution and status

[NASA FIRMS](https://www.earthdata.nasa.gov/data/tools/firms), [annual archive](https://firms.modaps.eosdis.nasa.gov/country/), and [field definitions](https://www.earthdata.nasa.gov/data/tools/firms/active-fire-data-attributes-modis-viirs). We acknowledge LANCE FIRMS, operated by NASA ESDIS with funding from NASA Headquarters. Basemap © OpenStreetMap contributors. Recent-feed mask: geoBoundaries/OSM, ODbL 1.0. NASA does not endorse the project.

Code is MIT licensed; data retain their source terms. OpenAI Codex assisted research, implementation, analysis and writing. This is a hackathon research prototype, not an operational warning service. Submission text and presentation outlines in `submission/` are drafts; no official challenge submission has been made by this repository.
