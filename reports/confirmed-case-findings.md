# A real fire, seen by a different instrument

The 15 September 2019 Landsat 8 scene provides a defensible positive demonstration of burning in a small part of southern Borneo. The displayed shortwave-infrared composite shows a coherent bright front, while the same geographic window in natural color shows a pale plume extending westward. NOAA-20 observations acquired later that UTC date fall along and near the visible front. NASA Earth Observatory independently described active fires in this Landsat scene and used bands 7/6/2 to highlight them in its [Smoke Blankets Borneo article](https://science.nasa.gov/earth/earth-observatory/smoke-blankets-borneo-145614/).

This corroborates **burning at this place and date**. It does **not** validate the regional anomaly, hotspot counts, calibration accuracy, burned area, or individual FIRMS detections. This example was deliberately selected after inspecting imagery from a known event; it is not a representative accuracy test.

## Exact observations

- Landsat scene: `LC08_L2SP_118062_20190915_02_T1`, OLI, **02:34:50.651419 UTC**.
- Bounds: **113.85–113.95°E, 3.10–3.00°S**, north up, EPSG:4326.
- Display: 360 × 360 grid, approximately 31 m spacing; actual band subsets, no generated imagery.
- Bright front: near 113.927°E, 3.025°S, with a longer bright edge continuing southward. This approximate visual location is not a digitized perimeter or a ground-truth annotation.
- Nearest FIRMS pass: **NOAA-20, 06:22 UTC**, 16 nominal/high-confidence observations in the crop, **227.16 minutes later**.
- The predefined **±60-minute** comparison contains **zero** observations. The time window was not widened to obtain a match.

| Platform | Same-date observations in crop | UTC times | Closest offset after Landsat |
|---|---:|---|---:|
| MODIS Aqua | 2 | 17:20 | 14 h 45 m |
| VIIRS S-NPP | 27 | 18:16 | 15 h 41 m |
| MODIS Terra | 4 | 14:22 | 11 h 47 m |
| VIIRS NOAA-20 | 51 | 06:22, 17:24, 17:25 | 3 h 47 m |

These are sensor observations, not separate fires. The table preserves satellite identity; the counts must not be added together as a fire total. The transparent overlay contains only the nearest NOAA-20 pass and represents point centres, not pixel footprints or fire perimeters. Fire evolution and footprint differences can explain spatial offsets between acquisitions.

## Display and quality limits

Natural color uses Landsat bands 4/3/2; shortwave infrared uses 7/6/2. Both use the same fixed display transform: `clip((DN × 0.0000275 − 0.2) / 0.45, 0, 1) ** 0.7`. Scaling follows [USGS Level 2 documentation](https://www.usgs.gov/faqs/how-do-i-use-a-scale-factor-landsat-level-2-science-products). Cropping preserves the original subset's pixel boundaries; there is no cosmetic sharpening, generated fill, or selective masking.

The displayed data are Collection 2 Level 2, accessed through the public Planetary Computer mirror. They support a qualitative visual interpretation; this pipeline does not apply a Level 1 active-fire algorithm to Level 2 surface reflectance. Burning pixels contain emitted radiation, and atmospheric correction and saturation can distort their values. The bright colors are not temperature, fire intensity, or a quantitative burn classification.

QA_PIXEL flags cloud or related conditions in about **0.0031%** of the crop, while **0.1852%** carries a SWIR saturation flag. Nevertheless, natural-color imagery is visibly smoke-obscured. This is a useful reminder that low QA cloud coverage does not imply clear ground visibility. [USGS documents these QA flags](https://www.usgs.gov/landsat-missions/landsat-collection-2-quality-assessment-bands); they do not measure fire extent. Clouds, haze and saturated pixels remain visible in the composites rather than disappearing from the evidence.

## Selection history and reproducibility

The protocol was written before the three-region imagery inspection. This was a retrospective demonstration from the outset: east-river and north-fields were inspected, then west-river was selected because its bright front and plume were visually clearer. The final crop was chosen after inspection. The public Level 1 catalog search returned no applicable Landsat 8 scene; this limitation and all three inspected regions are recorded in `confirmed-case-search-log.json`.

The prior fixed six-cell NBR audit is preserved unchanged: **0 corroborated, 0 contradicted, 6 inconclusive**. A curated active-burning illustration does not retroactively improve that audit or provide a success rate. Review here is AI-assisted and non-blinded, with no independent practitioner review.

Run `python pipeline/19_confirmed_case.py --cached` after the FIRMS archives and pinned Landsat subset are present. Without `--cached`, the pipeline can retrieve the same public Landsat subset. The script checks the scene acquisition time, verifies FIRMS archives against their download manifest, pins array and output hashes, retains exact source CSV lines, publishes unsigned asset URLs, and reports all acquisition times. The original model and its coefficients are untouched.

Published artifacts are `confirmed-case.json`, `confirmed-case-natural.png`, `confirmed-case-swir.png`, `confirmed-case-overlay.png`, `confirmed-case-panel.png`, and downloadable point CSV/GeoJSON. The scene, processing, QA diagnostics, exact dates, limits and provenance are embedded in the JSON.
