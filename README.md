# Global Earthquake Activity | Power BI

An event-level analysis of **USGS Earthquake Catalog earthquakes of magnitude 5.0 or greater in 2024–2025**. The Power BI report compares monthly patterns and explores magnitude, depth, and location with KPI cards, slicers, and drill interaction.

> Data snapshot: 4 November 2026. The catalog can be revised; rerunning the script may produce different results.

## Dashboard

Power BI report and exported preview links will be added after the report is built and checked.

## Questions and findings

- **How many events meet the chosen definition?** The extract contains **3,636 unique events**, including **1,507 in 2024** and **2,129 in 2025**. The larger 2025 catalog count does not by itself establish a change in global earthquake risk or detection-adjusted seismicity.
- **How strong were the events?** **244** reached M6.0+ and **26** reached M7.0+. The highest preferred catalog magnitude is **8.8**, for the [29 July 2025 Kamchatka Peninsula event](https://earthquake.usgs.gov/earthquakes/eventpage/us6000qw60).
- **How deep were they?** **3,043** are below 70 km depth, **478** are 70–299 km, and **115** are 300 km or deeper. Median depth is **10.3 km**. These are simple analysis bands, not risk categories.
- **When did this extract peak?** July 2025 has **413** events, the largest month in this two-year selection. The dashboard allows the viewer to examine other months and magnitudes.

## Data and reproducibility

Source: [USGS Earthquake Catalog API](https://earthquake.usgs.gov/fdsnws/event/1/) (ComCat), queried with `starttime=2024-01-01`, `endtime=2026-01-01`, `minmagnitude=5`, `eventtype=earthquake`, `format=csv`, and ascending origin time. [Query URL](https://earthquake.usgs.gov/fdsnws/event/1/query?format=csv&starttime=2024-01-01&endtime=2026-01-01&minmagnitude=5&eventtype=earthquake&orderby=time-asc). USGS asks that its data be credited; see its [data-use guidance](https://www.usgs.gov/faqs/are-usgs-reportspublications-copyrighted).

The curated [event-level CSV](earthquakes_2024_2025_m5plus.csv) includes event ID, UTC time/date, year/month, latitude/longitude, magnitude and type, depth, place, status, and derived magnitude/depth bands. The [build script](build_dataset.py) uses only Python's standard library. Run `python build_dataset.py` to download a fresh source extract and regenerate the CSV and [validation summary](validation_summary.json).

Validation performed for this snapshot:

- USGS count endpoint = CSV rows = unique event IDs = **3,636**.
- Every event is an `earthquake` with preferred magnitude at least 5.0 and origin time in 2024–2025 UTC.
- All latitude/longitude values are in valid ranges; no `place` values are missing; all 3,636 events are marked `reviewed` in this extract.
- Year counts sum to the total, as do the magnitude and depth bands.

## Metric definitions and caveats

- **Event count:** distinct USGS event IDs in the selected query, as captured on 4 November 2026.
- **M6+ / M7+:** event count where the catalog's preferred `mag` is at least 6.0 / 7.0. Preferred magnitude types vary (`mww`, `mb`, etc.), so the analysis does not treat them as identical physical measurements.
- **Depth:** USGS `depth` in kilometres. Dashboard bands: `<70`, `70–<300`, `>=300` km. Median is across all selected events.
- **Month:** UTC origin time, not local time or USGS update time.
- Event counts are **not** normalized for population, exposure, observational completeness, or network changes. An event's magnitude, depth, or inclusion can change when USGS revises the catalog. This report is a descriptive portfolio case study, not a hazard forecast or safety tool.

## Skills shown

Public API extraction, data validation, documented transformation, reproducible Python, KPI definition, Power BI report design, filter and drill interaction, and honest interpretation of observational data.

Credit: U.S. Geological Survey.
