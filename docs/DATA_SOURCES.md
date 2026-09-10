# Data Sources

Large source datasets are **not** stored in this repository. They are public and
re-downloadable; storing them would bloat the repo without adding verifiability.
Derived products that are small and expensive to rebuild (spliced weather years) **are** stored,
under `data/weather_years/`.

## Solar irradiance
**NREL National Solar Radiation Database (NSRDB)**, GOES Aggregated v4.0.0, 60-minute.
Sites used: Sterling, Arlington, Albemarle, Chesapeake, King George, Richmond.
Years 2012-2020. Retrieved via https://nsrdb.nrel.gov/

Note: this project has encountered two NSRDB filename conventions for identical content
(`nsrdbGOESaggregatedv400` and `nsrdb-goes-aggregated-v4-0-0`). `lp_package/nsrdb_data.py`
matches the latter and raises on unrecognized names rather than guessing (Rule 5).

## Wind
Coastal Virginia Offshore Wind (CVOW) hourly output, 140 m hub height, wake-adjusted.
2,587.2 MW nameplate. **Two internal formats share one filename convention** -- some years
are a day-by-day matrix, others a simple timestamp+kW series. `scripts/build_hydro_*.py`
auto-detects rather than assuming.

## Load
Dominion (DOM zone) hourly load projections 2024-2048, and PJM DOM zone historical hourly.

## Prices
PJM Mid-Atlantic/APS real-time hourly LMPs, Aug 2025 - Aug 2026, via PJM Data Miner.

## Weather
NOAA GHCN daily, stations: Sterling VA, Richmond Airport, Norfolk NAS, Suffolk Lake Kilby,
Pennington Gap.

## Siting
County GIS building footprints and parking polygons: Fairfax, Arlington, Prince William, Loudoun.

## Regulatory / policy documents
- Dominion 2025 Update to the 2024 IRP, SCC Case No. PUR-2025-00184, filed 2025-10-15
- National Standard Practice Manual for BCA of DERs, 2026 edition (NASEO/NESP)
- HB 895 / SB 448 (2026), signed 2026-04-13, effective 2026-07-01

**Caution:** several documents in the source set carry a `.pdf` extension but are not PDFs
(one is plain text, one is a ZIP of JPEGs). Check content, not extension.
