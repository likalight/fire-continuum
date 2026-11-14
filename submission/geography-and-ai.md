# One question. Many fire seasons.

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
