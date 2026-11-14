# Correction trials and observation timing

**None of the six tested alternatives reduces the original 46.8% current Kalimantan discrepancy.** Refreshed NASA files contain the same detections in the fixed 8–12 November 2026 window. The result supports a categorical conclusion—above the historical same-date median—more consistently than it supports a precise current count. Original estimates remain visible and unchanged.

## Chronological comparison

The first five methods were specified before their new results were computed. Candidate formulas were fitted using 2019–2021, selected on 2022–2023 macro-average WAPE across Sumatra, Kalimantan, Java/Bali and Papua, then refitted through 2023 and audited on 2024–2025. Original-model diagnostics for those years were already known, so this is an additional controlled comparison, not an untouched blind test. The current window did not select or fit any method.

The development-selected method is a local monthly seasonal ratio. Macro-average audit WAPE falls from **64.3% to 44.6%**, a **30.7% relative reduction** across four equally weighted study-area scores. This is not a national error score. Kalimantan's own audit WAPE slightly worsens, from **31.2% to 32.6%**. In the current window, disagreement rises to **80.3%**. A better average historical score does not validate transfer to this recent period.

| Method | Kalimantan audit WAPE, 24 windows in 2024–2025 | Current disagreement relative to 79 Aqua cell-days |
|---|---:|---:|
| Original sector/season | 31.2% | 46.8% |
| Updated sector/season | 31.1% | 49.5% |
| Local monthly/season, selected on earlier years | 32.6% | 80.3% |
| Local five-day/season | 34.7% | 98.7% |
| Equal blend of local fits | 33.7% | 89.5% |
| Sector plus day/night | 30.2% | 52.4% |
| Local plus day/night | 33.9% | 88.3% |

The two day/night experiments were specified after seeing the first trial. Their rules were fixed before inspecting their results and fitted through 2023, with 2024–2025 evaluation. They do not enter or retroactively change the first trial's method selection. Day/night attribution uses the official flag of each cell/day's earliest detection, after deduplicating across both components. This preserves the original count definition; it does not count the same cell/day twice. No training-support fallback was required.

The local monthly method passes the prespecified historical engineering guardrails. Those guardrails are not confidence levels and do not establish NRT transfer. The release therefore presents research alternatives alongside the original published model rather than silently replacing a recent estimate with an unvalidated new one.

## Refreshed data

The official FIRMS global seven-day MODIS and NOAA-20 files were downloaded again on 14 November. Within the fixed window and Indonesia mask, **581 Aqua detections and 4,775 NOAA-20 detections** match the saved observations, with **zero additions and zero removals**. All saved points matched official day/night flags. These national raw-detection totals are not the smaller Kalimantan occupied-cell counts.

The exact checks use coordinate/date/acquisition-time keys, with coordinates rounded to six decimal places (finer than source precision). They do not imply that missing fires were observed. Full source URLs, timestamps, hashes and product versions are in `daynight-audit.json`. The new downloads remain NRT; this experiment did not obtain paired standard-processed data for the current window. [NASA describes the NRT product and its geolocation/reprocessing limits](https://modaps.modaps.eosdis.nasa.gov/services/about/products/viirs-land-c2-nrt/vnp14imgtdl_nrt.html).

## The changing reference instrument

For the earliest daytime detections of occupied cells in Kalimantan on 8–12 November, approximate mean local solar times are:

| Sample year | Aqua median | NOAA-20 median |
|---|---:|---:|
| 2019 | 13:33 | 13:31 |
| 2026 | 15:40 | 13:38 |

Mean local solar time is computed as UTC acquisition hour plus longitude/15. These are detection-weighted samples, not equator-crossing times, complete overpass inventories, or exposure denominators. Different detected locations and fire timing can affect the sample. Nighttime differences also exist in the underlying result file.

[NASA documents Aqua's free drift to later equatorial crossing times](https://science.nasa.gov/mission/aqua/). Our observed timing difference is consistent with that context. It is a **plausible contributor**, not proof of the cause or magnitude of the 46.8% gap. It would be unjustified to force contemporary VIIRS to match contemporary Aqua and call that a validated improvement in fire accuracy.

VIIRS also responds to smaller fires more readily than MODIS; a VIIRS-only observation is not automatically false. [NASA's VIIRS product description](https://firms.modaps.eosdis.nasa.gov/content/descriptions/FIRMS_VIIRS_Firehotspots.html) explains this sensitivity difference.

## What can be defended

- All seven tested adjustments place the current Kalimantan window above the fixed 2003–2017 Aqua median and below its p90. Current Aqua gives the same category.
- This agreement is a robustness diagnostic over correlated models, not seven independent confirmations or a probability.
- No tested correction demonstrably resolves current-period count disagreement. Cloud/overpass coverage and drift-related sampling remain unresolved.
- The NRT-to-archive comparison is provisional. Historical agreement is not ground-truth fire accuracy.

The app exposes every candidate, a replay of excluded historical November windows, a fixed Kalimantan timing example and a downloadable evidence report. The HTML season briefing carries the correction limitations. Arbitrary custom areas do not inherit preset local-model validation.

## Reproduction

Run `pipeline/10_correction_trials.py` using the existing archive and short-window assets. Run `pipeline/11_daynight_audit.py` to explicitly refresh the official seven-day sources and audit the saved window. The latter fails if saved points cannot be matched for official day/night attribution; it does not guess labels. Use `--cached` to replay the pinned local recheck files with SHA-256 verification, preserving their source retrieval times. The rolling feed may no longer contain these dates later, so exact reproduction requires those locally archived files, which are ignored by Git.

The scripts preserve all published original results. `correction_protocol.json` and `daynight_protocol.json` document the order of the experiments. `correction-trials.json`, `daynight-audit.json` and `daynight_counts.csv` expose the numerical evidence. Unit checks cover chronological isolation, promotion guardrails, day/night count conservation, replay behavior and custom-area limitations.
