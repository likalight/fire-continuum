# Challenge coverage after this release

The project answers the challenge through a working calendar and measurable harmonization, with the scope below. This is a requirement mapping, not a self-awarded judging score.

|Challenge request|Where to inspect it|Status and boundary|
|---|---|---|
|Use NASA observations meaningfully|Sources dialog, source manifests, source-specific exports|Implemented: annual FIRMS, daily NRT, MYD14A1 QA, Landsat|
|Harmonize MODIS and VIIRS|Evidence: how records connect; sensor-switch experiment|Implemented on a common occupied-cell/day metric with frozen overlap ratios; not complete sensor interchangeability|
|Early-2000s burning calendar|Explore the calendar|2003–2025 for 185 eligible country/territory entries; original Indonesia research model and new country models remain separate|
|Extend comparison to the present|Current comparison|November 1–13, 2026 month-to-date snapshot; continuous 2026 calendar remains partial|
|Compare current month with historical median|Current comparison|Matches exactly November 1–13 across years; 26 daily files verified; no full-month extrapolation|
|Select an area and period|Calendar area/year controls, map rectangle and coordinates|Original Indonesia 0.25° AOIs; 185-country 0.5° snapped AOIs, monthly and arbitrary-day analytics, derived exact-date exports and original annual NASA CSV links; compatible package import|
|Identify active months and years|Calendar, largest-month/year summary, seasonal profile|Implemented; ranks are estimates, not severity; known 2020 outage omitted from ranking|
|Identify unusual conditions and critical periods|Season briefing and seasonal-window analysis|Median/p90 categories and leave-one-year-out seasonal sensitivity; no operational forecast|
|Download analytics, visuals and hotspots|Monthly CSV, SVG, evidence ZIP, exact-date original CSV, current-period CSV|Implemented; export scope and original-versus-estimated units are explicit|
|Accessible intuitive color presentation|Numeric labels, keyboard calendar, plain-language guide, responsive views|Implemented affordances; no formal WCAG certification claimed|
|Evidence that results are credible|Held-out tests, rare-category benchmark, transfer tests, sensitivity and independent event|Independent burning corroboration at one place/date; count accuracy not established by imagery|
|Support the target audience|Focused story → calendar → recent comparison → evidence workflow|Usability testing with practitioners deferred; no agency endorsement|

## Source and scope

The official [challenge Details and Resources tabs](https://www.spaceappschallenge.org/2026/challenges/modis-and-viirs-hot-spots/?tab=details) were read live on 14 November 2026 and checked against the user-supplied full statement. Resources links to [NASA FIRMS](https://www.earthdata.nasa.gov/data/tools/firms). The challenge is not restricted to Indonesia and does not require AI. The central task remains harmonization plus an understandable regional, temporal burning-activity calendar.

## Added geographic and AI capabilities

The [geographic workbench](../atlas.html) loads 185 independently screened national histories compiled from 5,550 annual files, worldwide recent observations, arbitrary-date daily analytics, original annual source links, reusable package import/export and shareable analysis links. A local sentence-embedding assistant retrieves explanations tied to the current selection, with source citations. It is not generative chat. Its development intent fixtures pass 22/25 after tuning, with two withheld answers and one wrong-topic route; no external user accuracy is claimed.

[Global results, methods and v2 data contract](global-validation.html). [Earlier geographic and AI methods](geography-and-ai.html).

## What remains partial

Continuous 2026 history, paired clear-sky/overpass normalization, full sensor interchangeability and external practitioner validation remain incomplete. The world map switches between national calibration outcomes and recent observations; neither represents danger. Imported packages are not authenticated scientific products. Arbitrary-day analytics are implemented for available supplied-country dates, but arbitrary-day historical anomaly estimation is not inferred automatically. The 46.8% earlier short-window discrepancy remains unresolved.
