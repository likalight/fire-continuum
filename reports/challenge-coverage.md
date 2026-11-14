# Challenge coverage audit

Audit date: 14 November 2026. Scope: read-only inspection of the current repository and the full challenge statement supplied by the user. This is a code/data coverage audit, not a fresh browser accessibility certification or independent reproduction of every scientific result. It describes the implementation at audit time; active work may supersede individual gaps.

## What the challenge actually asks

The supplied statement has two connected deliverables: harmonize MODIS/VIIRS hotspot observations so historical patterns are meaningfully comparable, then expose that record through a web application with region/date selection, burning calendar, historical/recent comparisons and downloadable analytics/visuals. It seeks help identifying critical periods and unusual activity. It does not require an AI model, precise ignition forecasts, evacuation recommendations, global coverage on day one, or a live API.

CONAE's official explanation confirms the emphasis on combining differing satellite records, selecting a region, identifying active months/years and comparing recent with historical observations. [CONAE challenge explanation](https://www.argentina.gob.ar/noticias/desafio-nasa-space-apps-challenge-2026-crea-soluciones-para-monitorear-incendios-con-datos).

The direct challenge and central judging-guide URLs returned errors during this audit. The full user-supplied brief was therefore used as the requirement source. A 2026 local-event page hosted on the official Space Apps domain lists Impact, Creativity, Validity, Relevance and Presentation, consistent with the user's Singapore organizer message. This is not evidence of an unpublished global scoring formula. [Official 2026 local-event criteria](https://www.spaceappschallenge.org/2026/local-events/ajmer/).

## Requirement-to-evidence matrix

| Requirement or consideration | Status at audit | Implemented evidence | Remaining gap / correct claim |
|---|---|---|---|
| Meaningful NASA data use | Implemented | 45 annual Indonesia files, 60 external-region files, NRT snapshots, full local MYD14A1 FireMask/QA, independent Landsat subsets; manifests and hashes | Source products and local processing must remain distinguishable; NASA does not endorse the application |
| Combine MODIS history with VIIRS continuity | Implemented, bounded | One primary sensor per period, shared occupied-cell/day grid, frozen regional/quarter calibration | Sensor identity still affects some decisions. Do not claim complete interchangeability or elimination of sensitivity/overpass differences |
| Early-2000s historical record | Implemented | Main calendar 2003–2025; Aqua reference baseline 2003–2017 | 2003 is a defensible first full Aqua calendar year. Do not relabel this as 2000 onward |
| Calendar through present | Partial | Separately dated 8–12 November 2026 snapshot and same-date comparisons | Main calendar ends 2025. January–October 2026 and most November dates are not populated. A snapshot is not a continuous present-day calendar |
| Current month against historical median | Partial | Recent five-day window compared with identical historical dates; no partial/full-month mixing | Not month-to-date. Add Nov 1–latest verified day only after complete source-date ledger is acquired. Unavailable dates must stay explicit |
| Historical patterns, unusual conditions | Implemented, descriptive | Monthly medians/p90, seasonal profiles, raw-versus-adjusted comparisons, case sensitivity | Descriptive categories are not significance tests, fire danger or forecasts |
| Critical periods | Implemented, retrospective | Historical maximum consecutive three-month window and leave-one-year-out sensitivity; annual peak-window benchmark | Not actual ignition timing or validated prospective warning; annual circular profiles are not dated cross-year events |
| Region/AOI selection | Implemented within declared geography | Indonesia presets, coordinates, two-corner map rectangle, shareable state | Main analysis snaps outward to 0.25°; disclose effective bounds. Punjab/Australia are separate fixed-region viewers, not arbitrary global AOIs |
| Specific date range | Partial | Start/end calendar years plus selected month; date-matched recent fixed window | No arbitrary day range. Full chosen range is not equivalent to selected-month hotspot export |
| Number of detected hotspots | Implemented alongside derived metric | Raw filtered detection mode and original point CSV; selected observation count is visible | Harmonized default is estimated Aqua-equivalent occupied 1 km cell-days, not harmonized individual hotspot count. Explain this transformation explicitly at the metric switch |
| Download analytics | Implemented | Monthly analysis CSV, recent CSV, benchmark/transfer/quality ledgers | Package selected state, units, effective AOI, model/source versions and caveats together to prevent detached CSV misinterpretation |
| Download original hotspots | Partial across range | Selected-month primary-sensor filtered original observations, with confidence/time/version/FRP | Year-range control does not export all those months. Label selected month clearly or add range export with honest size/progress limits |
| Download visualizations | Implemented | Calendar SVG and HTML briefs | Export must carry metric, date/area and source/caveat context; current SVG is not a full reproducibility bundle |
| Accessible intuitive calendar/color | Partly checked | Sequential color ramp, numeric detail, ARIA month labels, keyboard arrows, focus styles, mobile checks | No formal WCAG/color-vision certification. Provide a numeric/table alternative; do not rely on color alone for interpretation |
| Scientific validation | Implemented, bounded | Excluded-year count metrics, simple-method baseline, decision confusion matrices, sample retention, transfer tests, sensitivity/replay | Cross-sensor agreement is not ground truth. Some tests reuse previously inspected years. Improvement in WAPE can worsen category agreement |
| Independent evidence | Partial | Published regional Landsat event; fixed six-cell imagery audit with comparison cells, QA/source provenance | Six-cell fire attribution remains inconclusive. Do not present sample as verified count accuracy or all three candidates independently confirmed |
| Observation completeness | Partial | Full native mask/QA for a small fixed historical rectangle, 17 missing dates exposed | No paired MODIS/VIIRS clear-sky exposure normalization; no extrapolation of local mask fractions to other AOIs/current days |
| Target-user value | Plausible workflow; unvalidated | Four-question retrospective briefing, investigation candidates, exports; prepared task protocol | External practitioner testing remains deferred, 0 participants. No quantified time savings or agency endorsement |
| Presentation/submission | Supporting materials implemented | Public app, walkthrough, thirty-second video, summary/details/Q&A | Official submission must remain separate; avoid scoring the project against unseen entries or promising awards |

## Why the data distinctions are necessary

NASA's current FIRMS service provides maps, alerts, download formats and web services. It distributes global NRT observations within roughly three hours of satellite observation; that does not mean continuous observation of every place. Recreating those existing capabilities is weaker differentiation than making historical cross-sensor comparison and its limits understandable. [NASA FIRMS](https://firms.modaps.eosdis.nasa.gov/).

NASA publishes rolling 24/48-hour and 7-day downloads, a recent daily archive and older archive access. NRT records may later be replaced by standard processing; NASA recommends standard products for scientific analysis. Aqua's available record begins in July 2002, supporting a 2003 first full-year baseline. Current NOAA-20 and NOAA-21 availability does not automatically validate either as a substitute for earlier records. [NASA active-fire data access](https://firms.modaps.eosdis.nasa.gov/content/active_fire/).

MYD14A1 includes per-layer Dates, FireMask classifications and QA. Daily class fractions do not enumerate all observing opportunities. Keeping those distinctions is stronger scientific practice than assuming an empty hotspot table establishes no fire. [NASA MYD14A1 specification](https://ladsweb.modaps.eosdis.nasa.gov/filespec/MODIS/6/MYD14A1).

## Judging interpretation without invented scores

Impact is supported by a clear analysis task but not yet a measured practitioner benefit. Creativity is strongest when the product makes a misleading sensor comparison visibly understandable. Validity is supported by reproducible inputs, fixed rules and visible failure cases, with independent fire attribution still incomplete. Relevance is strong historically but only partial for current-month/continuous present coverage. Presentation improves when these facts form one understandable journey rather than a long catalogue of diagnostics. No numeric self-awarded score is justified.
