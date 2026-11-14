# Challenge coverage after this release

The project answers the challenge through a working calendar and measurable harmonization, with the scope below. This is a requirement mapping, not a self-awarded judging score.

|Challenge request|Where to inspect it|Status and boundary|
|---|---|---|
|Use NASA observations meaningfully|Sources dialog, source manifests, source-specific exports|Implemented: annual FIRMS, daily NRT, MYD14A1 QA, Landsat|
|Harmonize MODIS and VIIRS|Evidence: how records connect; sensor-switch experiment|Implemented on a common occupied-cell/day metric with frozen overlap ratios; not complete sensor interchangeability|
|Early-2000s burning calendar|Explore the calendar|2003–2025 Indonesia; raw detections and harmonized derived activity are separate|
|Extend comparison to the present|Current comparison|November 1–13, 2026 month-to-date snapshot; continuous 2026 calendar remains partial|
|Compare current month with historical median|Current comparison|Matches exactly November 1–13 across years; 26 daily files verified; no full-month extrapolation|
|Select an area and period|Calendar area/year controls, map rectangle and coordinates|Indonesia presets or snapped 0.25° AOI; monthly calendar, exact-day original-point exports|
|Identify active months and years|Calendar, largest-month/year summary, seasonal profile|Implemented; ranks are estimates, not severity; known 2020 outage omitted from ranking|
|Identify unusual conditions and critical periods|Season briefing and seasonal-window analysis|Median/p90 categories and leave-one-year-out seasonal sensitivity; no operational forecast|
|Download analytics, visuals and hotspots|Monthly CSV, SVG, evidence ZIP, exact-date original CSV, current-period CSV|Implemented; export scope and original-versus-estimated units are explicit|
|Accessible intuitive color presentation|Numeric labels, keyboard calendar, plain-language guide, responsive views|Implemented affordances; no formal WCAG certification claimed|
|Evidence that results are credible|Held-out tests, rare-category benchmark, transfer tests, sensitivity and independent event|Independent burning corroboration at one place/date; count accuracy not established by imagery|
|Support the target audience|Focused story → calendar → recent comparison → evidence workflow|Usability testing with practitioners deferred; no agency endorsement|

## Source and scope

The full challenge statement supplied by the user is the requirement source. CONAE's official description independently supports the focus on multi-sensor records, a calendar, selected regions and historical/current comparisons. [CONAE challenge explanation](https://www.argentina.gob.ar/noticias/desafio-nasa-space-apps-challenge-2026-crea-soluciones-para-monitorear-incendios-con-datos).

The direct official challenge page could not be retrieved during this research pass. The project does not claim that a live API, AI predictions or worldwide coverage are mandatory, nor that every possible capability is complete.

## What remains partial

A continuous 2026 archive, arbitrary global areas, arbitrary-day harmonized analytics, paired clear-sky normalization and external practitioner validation remain unimplemented. Those gaps are documented rather than hidden behind a “complete” label.
