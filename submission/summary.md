# Project summary — draft

**Fire Continuum: One fire history. Different satellites.**

Did burning increase—or did the satellite change? Fire Continuum helps regional analysts inspect that question before interpreting long-term hotspot trends. Using 45 NASA FIRMS annual files, our prototype builds an interactive 2003–2025 burning-activity calendar for Indonesia. Users choose an area, inspect seasons and historical anomalies, compare concurrent satellite measurements, and download analytics, visuals and original hotspot observations.

We keep MODIS Aqua, Suomi NPP VIIRS and NOAA-20 VIIRS separate, map detections to a common 1 km daily occupancy measure, and calibrate regional seasonal differences using overlap years. On later years excluded from fitting, NOAA-20 disagreement with Aqua falls from 451.0% to 13.5% WAPE; a simpler single-factor baseline gives 15.5%. These results measure agreement between satellites, not completeness against all real fires.

The interface makes the remaining limits visible: cloud and coverage effects, source changes, exploratory small-area estimates and missing 2026 archive months. A separate dated NRT snapshot shows recent observations without confusing a partial week with a full historical month. Our contribution is an auditable bridge across changing satellites, helping users interpret a long fire record with greater care.
