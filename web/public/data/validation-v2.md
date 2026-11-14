# Additional validation and its consequences

14 November 2026. The original national results had already been seen. The additional protocol was written before these new runs; this is an audit of an existing prototype, not an untouched final benchmark. All predeclared configurations are reported. The original 1 km method remains unchanged.

## Time and activity level

The original national aggregate WAPE is 13.70% for NPP and 13.45% for NOAA-20 against Aqua. NPP annual WAPE ranges from 7.4% in 2019 to 43.1% in 2020. NOAA-20 annual WAPE ranges from 10.1% in 2025 to 21.0% in 2022. A good aggregate score does not establish uniform performance across years. Quiet/high activity strata are defined by the training Aqua 25th/75th percentiles; all results, rolling three-year fits and whole-year bootstrap intervals are in `robustness.json`.

## Transfer to an excluded region

For each study rectangle, all its cells are excluded from every training year, then sector-quarter ratios are refitted outside the region. The omitted rectangle is evaluated on the original later test years. This is a harder transfer experiment than evaluating later years inside a region that contributed training data.

| Excluded study rectangle | NPP WAPE | NOAA-20 WAPE |
|---|---:|---:|
| Sumatra | 35.9% | 56.0% |
| Kalimantan | 51.8% | 58.4% |
| Java & Bali | 161.0% | 133.0% |
| Papua | 25.7% | 32.3% |
| Sulawesi | 18.0% | 13.3% |

**Consequence:** We cannot claim universal geographic transfer. The app remains an Indonesia study prototype. Custom small areas are labelled exploratory. These numbers do not replace original-fit local performance; the experiment deliberately changes the training geography.

## Empirical conversion ranges

Freeze the original factors. NPP residual calibration uses 2018–2021; range evaluation uses 2022–2025. NOAA-20 residual calibration uses 2022–2023; evaluation uses 2024–2025. A 90% finite-sample quantile of `abs(Aqua - estimate)/(estimate + 1)` sets a symmetric error radius, with lower endpoints clipped to zero.

NPP national reference coverage is **79.2% over 48 months**, below its nominal 90% target. NOAA-20 coverage is **100% over 24 months**, a short evaluation period; interval width is reported beside coverage. Regional results differ. Serial dependence and distribution shifts prevent unconditional guarantees.

**Consequence:** The interface reports these diagnostics and their failures. It does not put a misleading universal 90% uncertainty band on arbitrary selected areas or claim a range covers all real fires. The whole-year bootstrap interval is uncertainty in aggregate WAPE, not a prediction interval for an individual month.

## Grid and filter sensitivity

Every configuration is refitted on the original training years, then evaluated on the original later years. The original configuration exactly reproduces the first pipeline's WAPE.

| Configuration | NPP national WAPE | NOAA-20 national WAPE |
|---|---:|---:|
| 500 m grid | 12.0% | 15.5% |
| Original 1 km grid | 13.7% | 13.5% |
| 2 km grid | 16.2% | 13.7% |
| High confidence only | 23.3% | 18.1% |
| Vegetation source type only | 13.3% | 13.4% |
| Daytime only | 14.8% | 13.8% |

Definitions differ between rows. Lower cross-sensor disagreement is not proof of more accurate complete fire counts. Confidence categories are not equivalent probabilities across sensors. No new model was selected by choosing the best test score.

## Case and decision stability

The Kalimantan September 2019 case and following-year comparison were selected in the protocol because NASA published a separate Landsat observation, not because they produced a favorable anomaly result. The region is the study rectangle [108 E, -5 N, 120 E, 4.5 N], restricted to NASA's Indonesia country archive.

Under the original method, September 2019 gives 12,089.8 adjusted NPP cell-days versus 13,503 Aqua observed cell-days. The September Aqua 2003–2017 median is 6,269; its interpolated 90th percentile is 14,577.8. Both readings are above typical and below that extreme threshold. The September 2020 estimates are 940.8 adjusted and 1,042 Aqua; neither indicates a fire-free month.

All six variants retain the above-median classification in both sensors. Only the high-confidence variant crosses the 90th-percentile threshold in both sensors. **Above-typical activity is stable across these tests; an unusually-high classification depends on the filter.** Six variants are not six independent experiments and do not imply a calibrated probability of truth.

The interactive briefing compares adjusted activity and the concurrent Aqua observation with the same single-sensor Aqua baseline. Baseline years are 2003–2017 excluding the selected year; at least ten years and a positive median are required. Historical early-year briefings are retrospective, not forecasts made with information available at that time. Aqua-only years do not count self-agreement as independent cross-sensor corroboration.

## Reproduce

```sh
python pipeline/05_robust_validation.py
python pipeline/06_sensitivity.py
python pipeline/07_case_evidence.py
python pipeline/08_case_weeks.py
python -m pytest tests -q
cd web
npm test
npm run build
```

`05` uses the compact original history. `06` and `08` need the original annual files. `07` retrieves the NASA-published image and records its hash. No competitor code, data, models or assets are used in these analyses.
