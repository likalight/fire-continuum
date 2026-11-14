# Can better corrections earn our trust?

**Result:** the predeclared rule selecting corrections using 2021 raises full agreement passes from **9 to 11** across 185 countries. Six countries gain qualifying results and five lose them (qualifying includes limited rare-event evidence). This modest gain does not justify a global model replacement. The deployed atlas preserves every original model and fallback.

[Explore the correction lab](../atlas.html#correction-lab) · [All 925 trial summaries](../data/correction-study.csv) · [Full monthly evidence and fit audit, gzip JSON](../data/correction-study.json.gz) · [Frozen protocol](../data/correction-study-protocol.json)

## What failed, and why it matters

Of 109 original failed models, 80 fail a per-category recall check, 78 fail overall category agreement, 56 exceed the 25% count-error threshold and 28 exceed the 15% absolute bias threshold. These counts overlap. Low count error alone does not guarantee the same seasonal conclusion.

Of 60 unsupported countries, 58 lack sufficient quarterly training support, 32 have fewer than 200 Aqua test cell-days and 18 have fewer than 24 evaluation months with a positive historical median. These also overlap. Seven additional original models pass count/category checks but have fewer than five above-p90 months, so rare-event recovery is not established.

Categories are at/below the historical same-month median, above that median through the historical p90, and above p90. Baselines use Aqua 2003–2017. A zero median is not a usable anomaly baseline. Missing factors stay null; pooled estimates cannot bypass support requirements.

## Experiment design and limits

This is **retrospective**, not a fresh blind validation. Original 2022–2025 results and November 2026 comparisons were already inspected before designing these alternatives. We committed the finite candidate list and selection rule before running this study (Git commit `e9e6437`). No thresholds were relaxed, and no test-year winner was substituted into the selection rule.

1. Fit every candidate on 2019–2020, excluding August/September 2020's known outage.
2. Score on 2021: WAPE + (1 − category agreement). Require at least eight classifiable months and complete predictions for every candidate. Choose the lowest score in declared tie order; switch only for more than 10% improvement. Otherwise retain the original quarterly ratio.
3. Refit the chosen method on 2019–2021, with the same exclusions and frozen parameters.
4. Evaluate 48 months in 2022–2025 under the original support, count-error, bias, category-agreement, category-recall and rare-month requirements. Publish **every** candidate, every selected choice and regressions.

The code reproduces all 185 original statuses and count/bias/category metrics before accepting this report. Source package SHA-256 hashes bind each trial to the original data. A perturbation test changes all evaluation-year Aqua counts and confirms that fits, predictions and development scores are unchanged. This protects code-level separation; it cannot undo prior human inspection of the evaluation period.

## Five corrections, one unchanged test

- **Quarterly ratio:** sum of training Aqua occupied cell-days divided by NOAA-20 occupied cell-days for each quarter.
- **Annual ratio:** one annual ratio, still withheld in unsupported quarters.
- **Monthly pooling:** each calendar month's ratio shrunk toward its quarterly means using six pseudo-months. For month m in quarter q: `(sum A_m + 6 mean A_q) / (sum N_m + 6 mean N_q)`.
- **Robust quarterly ratio:** weighted median of monthly A/N, using NOAA-20 counts as weights. This minimizes training weighted absolute count error; it does not guarantee better future categories.
- **Spatial pooling:** each 0.5° display cell and quarter uses `(A_cell + 100 × national_quarter_ratio) / (N_cell + 100)`. Predictions sum cell-level adjusted NOAA-20. Unseen cells fall back to the national ratio. No contemporary Aqua is used. These remain aggregates of occupied 1 km cell-days, not coverage-normalized fire rates.

| Approach | Full pass | Limited events | Failed | Unsupported | Mean WAPE reduction (pp) |
|---|---:|---:|---:|---:|---:|
| Original quarterly ratio | 9 | 7 | 109 | 60 | +0.00 |
| Annual ratio | 4 | 8 | 113 | 60 | -3.58 |
| Monthly seasonal pooling | 14 | 8 | 103 | 60 | +0.94 |
| Robust quarterly ratio | 6 | 8 | 111 | 60 | -0.79 |
| Spatial pooling | 14 | 7 | 104 | 60 | +2.01 |
| 2021-selected rule | 11 | 6 | 108 | 60 | +0.93 |

Mean WAPE changes are equally weighted over 127 countries with computable paired errors, including some that fail other support checks. Positive means lower error. The 2021-selected rule improves count error in 42 countries, worsens it in 22, and is unchanged in 63. Its average improvement is **0.93 percentage points**, median zero; across 170 countries with at least some classifiable months (including incomplete quarterly predictions), average category agreement improves **0.83 percentage points**. The exploratory 95% country-bootstrap interval for mean WAPE improvement is **0.20–1.81 percentage points** (2,000 resamples, seed 20261114). Geographic dependence and repeated candidate comparisons limit inference; this is not external validation or a confidence interval for individual-country accuracy.

Fixed monthly and spatial candidates each reach 14 full passes. Spatial pooling improves mean count error by 2.01 percentage points and improves 94 of 127 computable comparisons, but it worsens 33 and loses three previously qualifying countries. Selecting it because its evaluation result is best would be post-evaluation model selection. Its result is a useful research lead, not a new blind success rate.

## Successes and counterexamples

The 2021-selected rule gains qualifying results in **Belize, Iran, Mexico, Portugal, Suriname and Zambia**. Portugal retains limited rare-event evidence; the other five pass the full prototype screens. It loses qualifying results in **Botswana, Brazil, Canada, Dominican Republic and Tanzania**. Full passes increase by only two because these transitions include limited-event outcomes.

- **Mexico:** selected spatial pooling reduces count error from 12.6% to 11.4% and now passes all original checks. This is a defensible retrospective improvement, not independent confirmation of actual fires.
- **India:** monthly and spatial corrections pass retrospectively; spatial count error falls from 17.7% to 12.8%. However, the 2021 rule chooses the annual correction, which worsens error to 24.1% and category agreement to 62.5%. We do not replace that choice with the test-year winner.
- **Indonesia:** spatial pooling reduces error from 13.2% to 10.4%, but still misses the category-recall requirement. There are no above-p90 reference months in this evaluation, so extreme-month recovery remains untested. These national figures differ from the earlier fixed-area recent-period experiment.
- **Brazil:** spatial pooling reduces count error from 7.7% to 7.0%, yet loses qualifying status. Better totals can still give worse seasonal decisions.

## Better data: what would resolve the remaining uncertainty?

No new observation products or independent ground truth were acquired for this study. All candidates use the identical pinned annual FIRMS corpus, confidence filters, boundaries and occupied-cell/day definition. We cannot infer why a country failed solely from a model metric.

NASA documents that VIIRS 375 m has greater response to small fires and improved nighttime detection. A ratio cannot recover every spatial or temporal difference. [NASA FIRMS product description](https://firms.modaps.eosdis.nasa.gov/content/descriptions/FIRMS_VIIRS_Firehotspots.html).

NASA also reports that MODIS orbit drift changes spatial sampling and diurnal sampling; effects on fire products remain under investigation. This makes a stationary correction less certain, but our experiment does not establish drift as the cause of a specific country's error. [NASA MODIS orbit-drift issue](https://landweb.modaps.eosdis.nasa.gov/displayissue?id=1254).

The next evidence priorities are:

1. **Full fire masks, QA and geolocation for matched swaths:** distinguish confidently observed nonfire, cloud, missing data and unprocessed pixels. Only then estimate comparable observation opportunities. Hotspot-only CSVs lack the required non-detection denominator.
2. **Time-matched comparisons:** retain acquisition times and scan geometry, compare similar observation times, and report how much data matching discards. Verify persistence with time-resolved independent observations where available. Fewer observations may reduce support rather than improve reliability.
3. **Independent imagery at the same place and dates:** confirm activity with optical imagery and complementary burned-area evidence, with cloud/temporal limitations. Burned area and active-fire detections measure different things. A few confirmed scenes do not validate national calibration.
4. **A genuinely untouched evaluation period or prospectively locked sample:** assess the declared spatial/monthly candidates with unchanged rules. Keep all failed countries and report current-period NRT transfer separately.

Aqua-only fallback avoids the unvalidated sensor splice; it does not remove Aqua's own sampling, cloud or drift limitations. This is a research atlas, not an operational warning or a census of all fires.

## Reproduce

From the repository root, with the documented Python dependencies and global packages available:

```sh
python pipeline/25_global_corrections.py
python -m pytest tests/test_global_corrections.py
```

The output JSON includes all five candidates' 48 monthly test rows per country, selection-year scores, fitted national weights and support, spatial coefficient count/hash, source package hashes, overlapping failure diagnoses and aggregate results. Spatial coefficients are reproducible from pinned source packages and the fitting code; their hash reflects the NumPy representation. The gzip JSON and CSV are generated from the same report. Creation timestamps can differ on reproduction; scientific results should not.
