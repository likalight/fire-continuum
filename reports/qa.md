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
