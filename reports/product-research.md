# Product research and practical priorities

Audit date: 14 November 2026. Read-only repository review plus official NASA/CONAE/Space Apps sources. Recommendations are design judgments, not measured user findings. External practitioner validation remains deferred at the project owner's request.

## Product position

The target task is: choose an area and period, understand whether detected burning activity differs from its historical pattern, inspect whether the comparison survives the observing-system differences, and export enough evidence for another person to review it.

NASA FIRMS already provides recent hotspot maps, alerts, formats and services. Fire Continuum's defensible added value should be historical comparability, seasonal context and traceable conclusions. A new globe, generic chatbot, more unvalidated forecast curves or larger headline count does not establish that value. [NASA FIRMS capabilities](https://firms.modaps.eosdis.nasa.gov/).

CONAE describes the challenge in terms of integrating incompatible records and enabling region, active-period and recent-versus-historical comparisons. The user interface should make those questions quick to answer. [Official challenge proposer](https://www.argentina.gob.ar/noticias/desafio-nasa-space-apps-challenge-2026-crea-soluciones-para-monitorear-incendios-con-datos).

## Priority 1: A current-period mode with an auditable availability strip

User action: select "This month so far" or the saved recent window, then see exact dates and same-date historical context. Use the most recent verified closed UTC day; if it is too recent for reliable source completeness, state the additional settling rule. Do not call a 13-day source ledger "complete satellite coverage."

Required data work: retrieve daily Aqua and NOAA-20 files from the beginning of the month, verify file identity/date/schema/hash, apply frozen filters and coefficients, and construct identical date masks for every historical year. Publish one row per day/sensor, including unavailable sources. If a date is absent, either withhold the aggregate or use a clearly labelled common-date subset; never silently count the gap as zero. Keep NRT-versus-standard differences explicit.

The NASA daily archive provides a plausible route without inventing an API. Official directories describe Earthdata token authentication; existing account access must be tested, not assumed. No new credential or terms flow should be hidden in the product. [NASA data access](https://firms.modaps.eosdis.nasa.gov/content/active_fire/), [MODIS daily archive](https://nrt3.modaps.eosdis.nasa.gov/archive/FIRMS/modis-c6.1), [NOAA-20 daily archive](https://nrt3.modaps.eosdis.nasa.gov/archive/FIRMS/noaa-20-viirs-c2).

Acceptance: selected dates are reproduced by exported evidence; all requested dates appear in the ledger; historical comparison uses exactly the same dates; missing-day fixture never yields a false zero; no live or complete coverage label; original published recent window remains reproducible. This closes a literal challenge gap more directly than another optional analytical panel.

## Priority 2: A focused analysis workspace with a plain-language answer

Keep the opening demonstration short, then offer three named tasks: compare a season, check a recent period, or inspect evidence. The analysis workspace should keep effective area, period, metric and snapshot visible together. Present the selected conclusion, comparison baseline and most relevant limitation before detailed calibration methods.

Add low-complexity affordances using existing data: a ranked list of highest-activity months/years for the selected AOI, a selectable same-calendar-month historical comparison, and a compact numeric/table alternative to the heatmap. Reuse the frozen calculation; do not create new explanatory claims. A selectable secondary period should use the same scale and baseline; clearly distinguish raw detections, occupied cell-days and calibrated estimates.

Original detections answer the literal hotspot-count request; occupied cell-days reduce pixel/deduplication effects; calibrated values are estimated activity on the Aqua scale. Put these three definitions at the metric control. An example should show why the numbers differ without implying that all MODIS/VIIRS disagreement has disappeared.

Acceptance: a new viewer can identify area, dates, units, baseline and evidence status from the main result without opening research details; keyboard users can reach equivalent numeric values; all panels update to the same selection; fixed case cards remain clearly separate; benchmarks retain their failures. Do not market this as proven easier to use until an actual task study occurs.

## Priority 3: One reproducible briefing pack for the chosen analysis

Combine the existing HTML brief, analytics CSV, calendar SVG and a concise provenance manifest under one export action. Include effective snapped AOI, date range, metric definitions, per-sensor provenance, source hashes, frozen model identity, snapshot timestamp and known limitations. Include original hotspotCSV for the selected scope, with clear size/progress feedback if a multi-month export is supported.

The implementation can use a static HTML dossier with embedded tables/visual plus linked source files, or a ZIP assembled locally in the browser. A single action should produce a portable result, not trigger many separate downloads unexpectedly. No cloud account, subscription, email or practitioner contact is needed.

Acceptance: selected-range analytics match screen totals; original records preserve sensor/date/confidence/version; downloaded conclusions survive reopening offline; all source URLs are absolute; unavailable periods remain labelled; the manifest distinguishes measured observations, estimates and unresolved validation. If full-range original point data are not bundled, state exactly which month/file is included.

## Evidence-led demo sequence

Within the submission's short presentation, show a real fixed-place/fixed-time sensor discrepancy, the harmonized comparison, an observing-quality boundary, then the supported conclusion and portable brief. A judge should see a completed task. The detailed benchmark and imagery audit are reachable evidence, not a prerequisite for understanding the project.

The current strong scientific counterexample is that a locally adapted Australian model improves WAPE while worsening category agreement. This demonstrates why "better numerical fit" alone is insufficient. It is our own published result, not a claim about actual ground truth or a competitor's performance. The current weakness is incomplete independent attribution: the six-cell imagery sample remains inconclusive. Keep that visible rather than using unrelated imagery as validation.

## Research boundaries and sources

The challenge page and central judging guide failed to load during this audit. The full user-provided challenge statement supplies requirements. An official-domain 2026 local-event page corroborates the five criterion names; no claim is made that a 2025 guideline is the authoritative 2026 rubric. [2026 official-domain criteria](https://www.spaceappschallenge.org/2026/local-events/ajmer/).

NASA documents changing time of agricultural burning in northern India. That motivates inspecting time-resolved observations, but neither the article nor our time-filter experiment proves the cause of our Indonesia sensor gap. [NASA timing account](https://science.nasa.gov/earth/earth-observatory/new-timing-for-stubble-burning-in-india/).

Do not infer winning probability from public repository descriptions. Do not promise global coverage from two transfer rectangles, forecast skill from seasonal history, independent accuracy from inter-sensor agreement, or real-world effectiveness from unit-test counts.
