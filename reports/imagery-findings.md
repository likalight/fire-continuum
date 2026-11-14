# Six-cell independent Landsat imagery audit

## What was completed

A fixed six-cell sample now has real, georeferenced independent optical evidence: the three existing September 2019 Kalimantan review candidates and three systematically selected lower-activity comparisons. Twelve Landsat 8 Collection 2 Level 2 subsets were obtained from the public Microsoft Planetary Computer mirror of USGS data, without creating an account or accepting new terms. Full cell bounds, exact acquisition times, item identifiers, unsigned source URLs, STAC hashes and subset-array hashes are published in `imagery-audit.json`.

Each scientific figure shows the same cell before and during September: a SWIR2/NIR/red reflectance composite and a change image using the normalized burn ratio (NBR). This is a systematic **independent-imagery audit**, not completed ground-truth validation of the hotspot estimates.

## Fixed sampling and scene selection

The selection protocol was written before optical retrieval or visual inspection. The three candidate cells come from the existing published hotspot ranking. For each in rank order, choose the nearest unused 0.25° cell whose historical September Aqua median is at least five cell-days and whose September 2019 Aqua and adjusted NPP counts are both at or below that median. Ties use longitude then latitude. Comparisons are lower-activity cells; they are **not known fire-free controls**.

For each cell, search Landsat 8 in August and September 2019. Require at least 95% scene-footprint overlap. Select the lowest scene cloud fraction, then proximity to the 15th and item ID. Scene choices were never replaced based on visual outcomes. Dates differ between cells because the satellite paths and scene availability differ.

## Results

| Cell | Before → during | Paired QA-valid fraction | Fire-attribution outcome |
|---|---|---:|---|
| Candidate 1 | 5 Aug → 6 Sep | 28.38% | Inconclusive: localized disturbance-like changes, cloud gaps and ambiguous attribution |
| Candidate 2 | 14 Aug → 15 Sep | 45.04% | Inconclusive: substantial cloud and haze/smoke contamination |
| Candidate 3 | 14 Aug → 15 Sep | 93.01% | Inconclusive: visible haze despite passing pixel QA; surface-change attribution remains ambiguous |
| Comparison 1 | 5 Aug → 6 Sep | 4.17% | Inconclusive: fails the predefined 20% paired-valid engineering gate |
| Comparison 2 | 23 Aug → 8 Sep | 27.64% | Inconclusive: no unambiguous fire evidence, but limited coverage cannot establish absence |
| Comparison 3 | 14 Aug → 15 Sep | 55.50% | Inconclusive: coastal water, haze and atmospheric effects confound change |

**0 corroborated, 0 contradicted, 6 inconclusive** for cell-level fire attribution from these fixed image pairs. These outcomes are not an accuracy estimate or proof that the underlying hotspot detections are wrong. The audit does not upgrade the three review candidates into independently verified fires. The existing NASA Earth Observatory account remains separate corroboration of the broader regional event.

The useful finding is that a high proportion of QA-valid pixels can coexist with visibly hazy imagery. Candidate 3 has 93% paired QA-valid pixels, yet substantial haze remains. QA flags alone therefore cannot establish clean independent validation. Reviewers can inspect the images instead of trusting a summary score.

## Processing and interpretation

USGS surface-reflectance scaling is applied: DN × 0.0000275 − 0.2. Each cell is resampled with nearest neighbour to a 900×900 EPSG:4326 grid, approximately 31 m at this latitude. This is a display/diagnostic grid, not an area measurement or a fire perimeter. Composites use SWIR2/NIR/red reflectance divided by 0.45 and gamma 0.7; clouds/haze remain visible. The fixed display mapping is identical across scenes.

For the paired diagnostic, exclude QA_PIXEL bits 0–5 (fill, dilated cloud, cirrus, cloud, shadow, snow), any QA_RADSAT flag, zero band values and reflectances outside [0,1]. NBR = (NIR − SWIR2)/(NIR + SWIR2); the denominator must be positive. Gray change pixels are unavailable under these checks. The 20% paired-valid threshold is an engineering gate, not a statistical validity guarantee.

NBR decreases can reflect burning, vegetation removal, moisture changes, clouds, haze and other effects. The descriptive >0.1 decrease fraction is **not** a burn classifier. The primary diagnostic includes water. After initial inspection exposed water effects in comparison 3, a separate land-only median was added by excluding QA_PIXEL water bit 7 in either image; the original diagnostic was retained. This post-inspection amendment is explicitly recorded in the protocol. No sample, scene, gate or classification rule changed.

The visual review was performed by an AI assistant with knowledge of the cell roles; it was **not blinded**, and no external analyst participated. Burn scars cannot establish an active-fire timestamp. The selected pairs do not isolate burning within September from changes since August. No hotspot total, harmonization coefficient, error bound or investigation priority is validated by this audit.

## Reproduce and inspect

Run `python pipeline/18_imagery_audit.py` after installing rasterio 1.4.4 and matplotlib 3.11.2 alongside the existing scientific dependencies. `--cached` uses the saved catalog and raster subsets and verifies their published array hashes. The first run queries the public STAC API; public asset-access tokens stay in memory and are never written into outputs. Twelve raw subsets and the full STAC response remain in ignored `data/raw/`; only six scientific figures, compact provenance, protocols and results are published.

`imagery_reviews.json` records the explicit visual findings and reviewer status. `imagery-verification.json` records numerical/artifact checks. Reproducing imagery figures can change PNG hashes across plotting-library versions; raw array hashes preserve the actual input values.

Primary references: [USGS scale factors](https://www.usgs.gov/faqs/how-do-i-use-a-scale-factor-landsat-level-2-science-products), [USGS QA definitions](https://www.usgs.gov/landsat-missions/landsat-collection-2-quality-assessment-bands), [USGS Collection 2 Level 2](https://www.usgs.gov/landsat-missions/landsat-collection-2-level-2-science-products), [Planetary Computer public access](https://planetarycomputer.microsoft.com/docs/).
