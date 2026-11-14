# Questions we can answer with evidence

**What is new compared with a hotspot map?**
The product connects sensor eras on a documented reference scale, tests whether switching sensors changes a seasonal conclusion, and carries uncertainty and provenance into the briefing. It includes a real daily observation-context example rather than treating empty hotspot lists as proof of no fire.

**Does 13.45% WAPE mean you detect 86.55% of fires?**
No. It is aggregate monthly disagreement with Aqua in Indonesia during held-out 2022–2025. Aqua is a reference instrument, not complete ground truth. The recent Kalimantan five-day result still differs by 46.8%.

**Did you select a correction to make the current result look good?**
No. Five main methods use earlier-year selection and later-year auditing; two day/night diagnostics are separate. All six alternatives increase the current gap. We keep the original result and publish the alternatives.

**What independent validation do you have?**
NASA-published Landsat 8 imagery corroborates the September 2019 southern Borneo event. It does not validate our total, anomaly size or fire boundaries. The daily Aqua masks are not independent of the Aqua instrument.

**Why not correct by the observed fraction?**
Daily compositing does not supply a clear-sky overpass denominator, and our native mask grid, local area and product differ from the hotspot comparison. Applying that fraction would manufacture a precision we have not validated.

**Can users trust the current comparison?**
Use its above-typical category cautiously: concurrent Aqua and all tested adjustments share that category. They are not independent confirmations. Counts remain uncertain, the snapshot is dated, and seven agreeing methods can still share a failure—as the 2025 replay shows.

**Does this work everywhere?**
The implemented archive covers Indonesia and a few study rectangles plus arbitrary in-country rectangles. Small-area and excluded-region transfer can fail. The architecture can ingest other countries, but global validity is not demonstrated.

**How would a land manager use this?**
Choose an area, inspect its typical peak window and sensitivity to historical years, compare a selected period against the reference, inspect sensor and observation limitations, and share or export the analysis for local review. We have not completed an external land-manager usability study and make no operational warning claim.

**What would you build next?**
Paired overpass/quality data with matched geometry and time, independently mapped events and systematically sampled controls, then prospective validation of current-period transfer. User studies would test whether the briefing improves interpretation and planning.

**Where did AI contribute?**
OpenAI Codex assisted research, code, analysis, tests and writing. The video uses synthetic narration. NASA source observations and recorded results are not generated examples.

### Did matching observation times solve the recent gap?
No. Two predefined windows left zero recent Aqua detections and failed our support gate. They did not improve the held-out error scores. We withhold their estimates and retain the published 46.8% discrepancy. Detection-only time filters cannot prove co-observation or isolate causal factors.

### What did full quality data change?
We retained native FireMask and QA for 167 daily layers across two seasons and found 17 absent dates in the 2020 archive. Explicit HDF layer dates prevent partial files being shifted onto the wrong days. The calendar separates unavailable products from cloud and non-fire classifications. It does not turn daily class fractions into clear-sky exposure or normalization.

### Is the decision brief validated by practitioners?
No. External validation has not been conducted; 0 participants. A task-based protocol is ready. We claim a functioning retrospective decision workflow, not measured usefulness, endorsement or operational reliability.

### What is your strongest measured contribution?
We test whether harmonization preserves seasonal conclusions, alongside count error. Across 240 NOAA-20 region-month comparisons, agreement with Aqua categories rises from 79.6% for simple calibration to 82.9% for the released model. This is 8 additional matching labels. Balanced accuracy declines and rare-month misses increase, so we do not claim universal superiority or ground-truth accuracy.

### Does the method work outside Indonesia?
We tested two preselected rectangles using 60 additional real NASA files. Local adaptation helps Punjab category agreement. In southeast Australia it improves count WAPE but worsens category agreement. The app shows frozen transfer and local refitting separately. Two regions do not establish global validity.

### Did Landsat independently validate your candidate locations?
No. We retrieved and inspected fixed before/during scene pairs for three candidates and three comparison cells. All six fire-attribution outcomes remain inconclusive. Haze, scene timing and ambiguous surface changes prevent stronger claims. We publish the imagery and QA so others can inspect the same evidence; the separate NASA article still corroborates the regional 2019 event.


## Do you now have a convincing independent success?
Yes: a curated Landsat image shows a coherent fire front and smoke plume at a location also detected by NOAA-20 later that UTC day. The interactive view exposes both images and point centres. The nearest pass is 3 h 47 m later, and no observation passes the ±60-minute test. The claim is event corroboration only. It does not overwrite the fixed six-cell audit or validate counts/anomaly magnitude.

## Does month-to-date solve the 46.8% disagreement?
No. November 1–13 is a different window from November 8–12. The new source ledger closes the current-month-to-date feature gap while preserving provisional processing and observation limits. A smaller discrepancy in another window is not a successful correction of the old result.

## Could an agency adopt this now?
The data contracts, reproducible pipelines, evidence exports and public code make evaluation easier. Adoption still requires practitioner tests, broader scientific validation, maintained updates, accessibility evaluation and operational ownership. Those have not been demonstrated.
