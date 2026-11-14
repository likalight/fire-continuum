# A simpler way to read the fire season

[Open the guided experience](../) · [Detailed atlas](../atlas.html) · [Original research workspace](../#evidence-hub)

The default screen now asks one question: **Is there more burning here than usual?** Choose a country and dates; read the plain-language answer beside the clickable calendar. The interface changes how the evidence is presented. It does not improve sensor accuracy or remove scientific limitations.

## The three-step experience

1. **Place:** choose any of 185 country/territory records.
2. **Dates:** click a month in the calendar or select the latest November 1–13 snapshot. The calendar initially shows recent years; “Show 2003–2026” exposes the full available history. Gray missing months are never filled with zeros. Calendar months support arrow-key navigation, with exact descriptions for screen readers.
3. **Answer:** read a percentage above/below the same-period historical median, with the place, dates, baseline definition and material limitation alongside it. A missing baseline or outage produces no percentage. The usual three-month peak is visible; its seasonal chart expands on request.

“Why this answer?” opens exact values, the source policy, sensor disagreement, year-by-year records and NASA source receipts. The main screen also downloads the report, same-month comparison CSV and complete calendar SVG, and copies a link that restores the place and dates. Exported graphics include dates, missingness, source policy and interpretation limits. Every calendar/CSV row omits its own year from the 2003–2017 baseline, where applicable.

Four navigation choices replace the long feature page: **Explore**, **See an example**, **Saved places**, and **How it works**. The imagery case is a three-step Look/Compare/Check explanation. Methods, correction experiments, the full-mask audit and the voluntary feedback form remain accessible without crowding the initial task. The evidence assistant is optional under “Ask a question,” not a floating overlay over the result.

“Smaller area or custom dates” opens the existing regional map and date tools within the app, with an explicit country-versus-region boundary and a back button. These tools retain their original availability: 2003–2025 plus the separate November snapshot. They do not silently inherit the national October extension. The initial regional date is stated before the map; recent selections open the historical November 2025 view with a separate control for the November 2026 snapshot.

## A short demonstration

- Open the homepage: point out the one question and the place/date controls.
- Select Mexico, then October 2026: the answer is **1.2% above usual**, from 412 Aqua cell-days versus a historical median of 407. This is a small descriptive difference, not proof of a significant increase; current-period accuracy remains unvalidated.
- Open “Why this answer?” to inspect the exact values and Aqua-only policy. The failed adjustment is not substituted into the headline.
- Show “See an example,” reveal the same-scene infrared image, then “3. Check” for its timing and spatial limits.
- Download the report or CSV. No account or AI model is required for these calculations.

## What works

- **185 national briefings:** all historical packages are preserved. Lightweight precomputed summaries make country switching and November comparisons quick. The default snapshot is explicitly November 1–13, 2026, not live.
- **Seasonal context:** a 12-month median profile and the highest consecutive three-month window, using Aqua 2003–2017. The selected historical year is excluded from its own baseline and peak calculation. Anomaly categories use median/p90, not severity or danger.
- **Historical months and evidence:** 2003–2025, the known 2020 August/September outage withheld from the headline comparison, sensor-specific numerical views, source links and hash receipts.
- **Saved places:** up to six country IDs in localStorage, with open/remove actions and a same-date comparison against each country's own historical baseline. No account, cross-device sync, automatic alerts or background monitoring.
- **Briefings:** downloadable HTML includes selected dates, measurements, sources, limits and a link that restores the same place and period. Share links contain only country/period parameters.
- **Task-capable assistant:** explicit supported commands open the current comparison or sensor views, save the selected place, compare saved places, open the event story or download a briefing. Actions are deterministic functions; existing local MiniLM semantic retrieval handles explanation topics. No generative model fabricates scientific quantities. Commands naming another country require selecting it first. Unknown tasks do not execute.
- **Real-event story:** a natural-color/infrared reveal of the same Landsat scene, followed by the regional seasonal context and timing limitations. This preserves the curated Borneo event and all original failed imagery checks.
- **Usability test:** a voluntary three-task form with a timer and local JSON export. No data are sent to the team. It is a testing instrument, not completed usability validation.

## New observations: October 2026

We obtained and checked all 62 daily files (31 dates × two instruments) for October 1–31, 2026. Mexico and Australia now offer that complete October in the guided historical-month selector. The detailed atlas retains its original availability contract; the extension is not silently injected into its daily shards.

Annual 2026 FIRMS country files were not advertised in the checked catalogue and the attempted Mexico/Australia annual paths returned 404. Daily NRT directories exposed September 15–November 14 only. Therefore January–August and continuous global 2026 coverage remain incomplete. We did not fill absent months with zeros.

The October window was selected from availability before inspecting its counts. Original quarterly and previously 2021-selected models were frozen; no new fitting or post-result substitution occurred. Inputs and frozen coefficient hashes are checked in reproducible code. This is first evaluation on a newly inspected period, not blind validation of the entire development process or independent ground truth.

|Country|Aqua occupied cell-days|Original quarterly prediction|Original monthly difference|Previously selected prediction|Selected monthly difference|Selected daily WAPE|
|---|---:|---:|---:|---:|---:|---:|
|Mexico|412|441.89|7.3%|482.03|17.0%|51.9%|
|Australia|9,672|13,288.43|37.4%|13,288.43|37.4%|38.0%|

Both instruments give the same descriptive seasonal category in both countries, but the count discrepancies remain. Daily WAPE sums absolute daily errors; monthly totals can cancel errors of opposing signs. One month does not establish rare-category recall or change a national pass/fail status. NRT-to-standard-processing transfer remains a limitation. Mexico's main briefing retains Aqua-only policy; Australia retains its documented original quarterly model, with current accuracy explicitly unvalidated.

[Full October daily evidence and source receipts](../data/october-transfer.json) · [Mexico October briefing](../?place=mexico&period=history&year=2026&month=10) · [Australia October briefing](../?place=australia&period=history&year=2026&month=10)

## Full masks and quality: what absent hotspots can hide

For a predeclared western Mexico box (105–103°W, 20–22°N) on May 1, 2026, we acquired MYD14 + MYD03 and VJ114IMG + VJ103IMG. The full masks, geolocation and raw algorithm QA were retained, including pixels that are not hotspots.

|Native-pixel category|Aqua, 22:05 UTC|NOAA-20, 20:00 UTC|
|---|---:|---:|
|Cloud|80|78|
|Clear nonfire land|44,738|42,864|
|Sun glint|0|264,467|
|Fire, all confidence|51|80|
|Water|941|4,099|
|Total pixel centres in fixed box|45,810|311,588|

Product class legends differ: NOAA-20 class 2 is sun glint, while the MODIS legend calls class 2 obsolete/unprocessed. The pipeline does not relabel glint as cloud or clear nonfire. Raw QA values are preserved without inventing a common quality score. Resolution and footprint differ, so native pixel counts are not comparable area fractions or distinct fires.

The passes are **125 minutes apart**, failing the declared **30-minute** matching rule. No alternative location/date was substituted. We therefore **did not estimate a matched observation denominator or normalize the fire record by coverage**. The audit is useful evidence about observation conditions, not validation of October totals. Geolocation was cross-checked against sparse fire coordinates from each product (220 Aqua and 2,155 VIIRS points; exact coordinate agreement in this check).

[Mask audit, class legends and hashes](../data/matched-mask-audit.json) · [Aqua native pixels + QA](../data/aqua-mexico-may01-native-pixels.json.gz) · [NOAA-20 native pixels + QA](../data/noaa20-mexico-may01-native-pixels.json.gz)

## Reproduce and inspect

`python pipeline/26_guided_briefs.py` builds all 185 compact summaries from the unchanged pinned packages and daily shards. `pipeline/new_observations/README.md` documents acquisition and analysis for the October and full-mask audits. Raw input products require authorized Earthdata access and are not committed; public derived data, source URLs, hashes and protocols permit inspection. The rolling NRT retention window may make later re-download unavailable. Pinned input hashes fail closed if upstream contents change.

Tests cover all 185 briefings against original package values, exact-date baselines, missing sensors, outage behavior, source hashes, October daily reconciliation, command negation, saved-place input validation and unavailable 2026 months. Browser checks exercise tasks, exports, saved comparisons, historical deep links and narrow layouts.

## Privacy and remaining limits

Saved country IDs remain on this browser. Questions are processed locally. The AI model and static site assets are downloaded from the published site; standard hosting requests still occur. Feedback is downloaded only on the participant's action, with no automatic submission. Removing a saved place removes it from the browser list; clearing site storage removes all saved places.

Practitioner validation has not been performed. The testing form is ready for voluntary use; no participant results, time savings or adoption claims are invented. Whole-year 2026, globally matched observation coverage and full sensor interchangeability remain unresolved. The app provides historical research context, not operational warnings or forecasts.
