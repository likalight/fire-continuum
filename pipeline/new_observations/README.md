# New observation audit: reproducibility

Place this directory at `pipeline/new_observations/` in the existing Fire Continuum repository. Run `python pipeline/new_observations/run.py` from any working directory using the project's Python environment. Dependencies are the existing NumPy, pandas, requests, shapely, pyproj, pyhdf and h5py packages. Authorized Earthdata credentials are consumed by requests through the existing netrc mechanism; no credentials are supplied or logged by these scripts. No new terms are accepted.

Raw files and acquisition metadata go to ignored `data/raw/new-observations/`; final summaries go to `reports/new-observations/october-transfer.json` and `reports/new-observations/matched-mask-audit.json`. No production data or model is modified and nothing is auto-published. Native pixel exports retain per-pixel geolocation, mask and the complete raw QA integer. They remain in raw storage until deliberately published by the site owner.

The original study protocols are copied byte-for-byte before acquisition. `pinned-sha256.json` contains all 62 daily October sources and four full mask/geolocation inputs. Any changed science input fails verification instead of silently becoming the original experiment. Old source URLs may expire: the NASA daily directory advertised a rolling 61-day window on November 14, 2026. Reproduction after expiry requires the cached exact inputs or an authorized NASA archive request; a regenerated standard archive must be treated as a new processing experiment. Discovery is live metadata and is not a promise that source links will persist.

October was selected as the only complete calendar month in the available portion of the already declared January–October window, before inspecting its counts. Mexico and Australia are both retained regardless of outcome. Selection was fixed using 2021, fit on 2019–2021, and evaluated here without refitting. This is first new-to-us 2026 evidence for those frozen choices; it is not independent ground truth or blind validation of the full development process.

## Correct interpretation

- Thirty-one available files per instrument means source availability, not cloud-free observation completeness.
- Monthly total discrepancy and daily WAPE measure different things; do not report the smaller monthly discrepancy as daily accuracy.
- A single October cannot establish full national screening acceptance or category recall.
- The May 1 fixed-area pair is 125 minutes apart, failing the declared 30-minute time-match rule. No coverage normalization is computed.
- MODIS and VIIRS native pixel counts differ in resolution, overlap and footprint. They cannot be compared as area or distinct fire counts.
- Per-source mask legends are read from the actual files. In NOAA-20 VIIRS class 2 means sun glint; in this MODIS product it is an obsolete unprocessed class. Never merge those labels into clear nonfire or cloud.
- Algorithm-QA integers and bit-set frequencies are retained; they are not decoded into a shared quality score. The 375m VIIRS QA layout differs from the 750m VIIRS/MODIS layout. Product-specific authoritative documentation is required before semantic decoding.

## Sources

NASA FIRMS archive/processing boundary: https://firms.modaps.eosdis.nasa.gov/download/

VIIRS Collection 2 375m guide (version 1.2; direct download returned403 during this audit, indexed excerpts available): https://www.earthdata.nasa.gov/s3fs-public/2025-06/VIIRS_C2_AF-375m_User_Guide_1.2.pdf

375m algorithm theoretical basis: https://viirsland.gsfc.nasa.gov/PDF/VIIRS_activefire_375m_ATBD.pdf

MODIS Collection6/6.1 guide index: https://www.modis-fire.umd.edu/guides.html

The exact acquired products' native legend attributes and their source URLs/hashes accompany `matched-mask-audit.json`, providing the definitions used in the mask partition without borrowing a different product's class codes.
