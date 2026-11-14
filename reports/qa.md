# Verification — 14 November 2026

- Python scientific checks: 5 tests passed (ratio calibration, metrics, invalid inputs, source-period assignment, sector/quarter boundaries).
- Browser exports independently reconcile to 1,620 monthly/sector/sensor ledger rows and all 276 monthly point files. National held-out WAPE recomputed from browser assets agrees to floating-point tolerance.
- Production TypeScript/Vite build passes. Vite reports a bundle-size advisory for MapLibre; initial data is separate from on-demand point downloads.
- GitHub Actions production build and Pages deployment succeeded under `likalight/fire-continuum`.
- Public browser: all 276 calendar months render; September 2023 shows 7,923 adjusted national cell-days and a rendered map. Concurrent NOAA-20 comparison labels 2023 as held out.
- Region selection: Sumatra September 2023 shows 1,525 adjusted cell-days and 12,458 original detections. Custom bounds snap outward; invalid coordinates produce a visible error.
- Browser-downloaded Sumatra hotspot CSV contains exactly 12,458 rows, all inside the selected rectangle. Monthly analytics CSV contains 276 rows and agrees with that month's point count. Exported calendar SVG parses successfully.
- Source dialog includes annual provenance, method, calibration, version audit, attribution and AI-assistance disclosure.
- Mobile viewport check at 390 × 844: stacked controls and calendar fit, with no document horizontal overflow. Desktop calendar/map and recent snapshot render. No production-page JavaScript errors were captured; earlier localhost development-fetch errors were confined to the local preview.

This verifies implementation and internal consistency, not independent ground-truth fire accuracy. The remaining scientific and coverage limits are in `method.md`.

## Evidence and briefing release — 14 November 2026

- Ten Python scientific tests and five frontend briefing tests pass; the production CI run 43572799106 passed both suites and deployed commit 66d9fb5.
- Public default briefing: Kalimantan September 2019, 1.93 times the Aqua historical median; concurrent Aqua is 2.15 times. The 15-year baseline, Aug–Oct peak window and held-out-year label are displayed.
- High-confidence case variant changes the verdict to threshold crossed; the original variant stays above typical but below the extreme threshold. NOAA-20 diagnostics display 100% coverage over only 24 evaluation months, with the short-record limitation. NPP displays 79.2% coverage.
- All five guided steps, Back, Finish and Exit work. Mobile tour scroll settles on the case image; the panel remains usable at 390 × 844. No document horizontal overflow was measured.
- Downloaded HTML briefing contains exact adjusted value 12089.7984, Aqua 13503, median 6269, p90 14577.8, n=15, bounds and source links.
- Raw calendar mode suppresses the cross-sensor anomaly ratio while explicitly retaining a harmonized briefing. Selecting September 2005 excludes that year (n=14) and says Aqua-only period. An empty custom rectangle shows insufficient baseline and peak window not established.
- Selected case hotspot CSV downloads successfully with 106,138 detections. No production JavaScript errors were captured.
- These checks verify behavior, not independent accuracy of regional fire totals. Landsat corroborates the event and broad timing only.

## Recent same-date comparison — 14 November 2026

- Six new Python checks bring the suite to 16 passing tests: settled-date selection, rejecting unsuitable windows, deterministic cell-day deduplication, browser/scientific aggregate reconciliation, direct point-to-cell counts and zero-baseline handling. Ten frontend tests pass, including all five region results and day-omission classifications. Production build and initial release CI run 43574132444 passed.
- Public default Kalimantan view shows 8–12 November 2026, 2.70 times the Aqua historical median after adjustment, concurrent Aqua 1.84 times, and 5/5 category-preserving day omissions. The selected September 2019 historical briefing remains separate.
- Downloaded same-date CSV has 24 rows (2003–2026), identical November 8–12 dates in each year, blank unavailable pre-2019 NOAA-20 values, current 79 Aqua cell-days and 115.9782 adjusted NOAA-20 cell-days. Current raw detections are 85 Aqua and 941 NOAA-20. The HTML briefing includes the recent dates, source snapshot identity, 48-window error and NRT/coverage limitations.
- Java/Bali shows 4/5 sensitivity checks, 101.2% all-month-window WAPE and 224.9% same-calendar-window WAPE. Expanded tables show the category disagreement when 8 November is omitted. An empty custom rectangle displays insufficient baseline and no supported anomaly.
- All six guide steps work, including the recent comparison and final failed-validation step; Finish closes the guide. Desktop layout checked at 1280 × 900; mobile 390 × 844 has no document horizontal overflow.
- Browser review caught a date-label formatting error (full end date used where end day belongs). Corrected it and added an assertion for days 8–12. Current 46.8% count disagreement is now explicitly stated beside category agreement.

## Correction trials and timing audit — 14 November 2026

- Twenty-two scientific tests and fourteen frontend tests pass. Release CI run 43575823021 successfully built and deployed commit 106df43. Replaying the pinned day/night source files with --cached reproduced the exact audit SHA-256.
- Live Kalimantan audit shows all seven methods; original current disagreement is 46.8%, and the development-selected local model is 80.3%. All seven retain the above-typical current category. The numerical result has not been silently replaced.
- The 2025 replay displays 52 observed Aqua cell-days and the original adjusted estimate of 27.6, exposing the different categories. Changing to Sumatra updates the trial results; custom bounds display unavailable local validation.
- Downloaded evidence JSON contains the original current result, selected area/bounds, exact source snapshot, model audit results and two refreshed source manifests. The downloaded HTML briefing includes correction history, 46.8% and 80.3%, the non-blind-audit limitation and Aqua timing context.
- Live timing panel shows approximate daytime detection medians of Aqua 13:33/15:40 and NOAA-20 13:31/13:38 in 2019/2026, explicitly labeled as a fixed Kalimantan detected-point sample.
- Mobile 390 x 844 has no document horizontal overflow; correction cards and download control are readable, with tables in contained horizontal scrollers. No production JavaScript errors were captured.
