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
