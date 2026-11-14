# Daily observation context

NASA MYD14A1 Collection 6.1 supplies daily fire-mask composites, including pixels absent from hotspot-only CSV files. Three authenticated Earthdata granules cover 14–21 September in 2019 and 2020. We retain all ten classes for the same 14,386 native sinusoidal grid-cell centres in 113–114° E, 3–2° S. The rectangle and dates were specified before computing these counts.

On 17 September 2019, 7,110 cells (49.4%) have a cloud classification and three have a fire classification. On 14 September, 239 have a fire classification and none have the cloud classification. This shows the importance of observation context; it does not establish how many fires the cloud concealed or isolate the cause of the count difference. The 2020 comparison includes days with zero classified fire cells; those days are not assumed fire-free.

The daily product combines overlapping swaths. Non-fire classification can take precedence over cloud in the composite. Consequently the complement of the cloud fraction is not a count of clear-sky overpasses, and a cloud fraction of zero does not mean the whole day was cloud-free. No normalization divides FIRMS activity by these fractions. Low-confidence fire classes remain separate in the downloadable table.

The same MODIS instrument supplies these masks and the reference hotspots. This is observation context, not independent fire validation. The Landsat case remains the separate-instrument corroboration. The local mask rectangle is smaller than the Kalimantan calendar study area, and the native sinusoidal grid differs from the EPSG:6933 cell-day grid.

## Checks

- Every daily slice partitions exactly the same 14,386 pixels; all classes sum to that total.
- Coordinate selection matches an independent PROJ inverse transform at every native pixel.
- Dates form two complete eight-day intervals, without duplicates.
- Cached reproduction verifies the three source SHA-256 hashes.
- No masks, counts or parameters modify the released calibration or recent comparison.

## Present-day access check

A NASA CMR query on 14 November 2026 for 8–12 November returned an Aqua MYD14A1 granule starting 1 November (ending 8 November), but no NOAA-20 VJ114A1 granules for this rectangle. This does not supply paired full-window daily coverage. We do not claim the current 46.8% disagreement has been corrected.

## Sources and reproduction

[NASA MYD14A1.061](https://doi.org/10.5067/MODIS/MYD14A1.061), [NASA daily mask specification](https://ladsweb.modaps.eosdis.nasa.gov/filespec/MODIS/6/MYD14A1), `observation-context.json` and `observation_protocol.json`.

Run `python pipeline/12_observation_context.py`. Downloads require existing authorized Earthdata credentials; the script does not print them. After downloading, `--cached` verifies pinned inputs and rebuilds without network access. Raw HDF files remain ignored. The published CSV and JSON contain derived class counts and source provenance.
