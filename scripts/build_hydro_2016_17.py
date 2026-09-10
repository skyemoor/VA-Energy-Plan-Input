"""
build_hydro_2016_17.py

Reconstructs hydro_year1_2016_17.npz -- the original file this project's own scenario
checkpoint solves depend on, missing from this session's own working environment.
Extends build_new_weather_years.py's own established methodology (SES Rule 1) rather
than inventing a new approach: equal-weight 3-county solar blend (Albemarle/Chesapeake/
King George), each normalized by its own file's peak; CVOW wind normalized by 2,587.2 MW
nameplate; April-March hydrological-year splicing.

Source selection, per direct user decision (2026-09-09): solar uses the
`...hourlyinsolation{year}.csv` file family, not the alternative `..._psm322_60_{year}.csv`
family -- the insolation family is already-simulated power output (Time stamp + "System
power generated | (kW)"), structurally identical to the hourlyresults.csv convention both
existing, verified build scripts (build_new_weather_years.py, build_hydro3_2012_13_2013_14.py)
actually use; the psm322 family is raw NSRDB meteorological data that would need a PySAM
simulation step this environment doesn't have installed.

2017 wind: 2017CVOWhourlymatrixkWhWake140mresults.csv (the standard matrix format the
existing parser handles) is NOT available in this session -- only 2017CVOWhourlyout.csv,
a single unlabeled 'kWh' column. Per Weather_Year_Robustness_Approaches_and_Findings_
2026-08-23.md's own documented finding: this column's header is mislabeled -- values are
actually MWh, not kWh -- and the corrected interpretation was independently validated
there against the real matrix file (exact hour-by-hour match, correlation 1.000000).
Applying that same documented correction here, not re-deriving it. Cross-checked directly
in this session too: max value (2115.32, as MWh) / CVOW_MW (2587.2) = 0.8177, matching
that same document's independently-established ~0.8176 wake-loss ceiling almost exactly --
a second, independent confirmation.

Nuclear + exist_solar: NOT reconstructed -- extracted directly from hydro_year_2018_19.npz,
which (per build_new_weather_years.py's own code) was itself built by copying these two
arrays forward from the ORIGINAL 2016-17 file. This recovers the exact original values,
not an approximation.
"""
import pandas as pd
import numpy as np

PROJECT_DIR = '/mnt/project/'
CVOW_MW = 2587.2

SOLAR_FILES = {
    2016: {'Albermarle': 'AlbermarleCountyhourlyinsolation2016.csv',
           'Chesapeake': 'ChesapeakeCityhourlyinsolation2016.csv',
           'KingGeorge': 'KingGeorgeCountyhourlyinsolation2016.csv'},
    2017: {'Albermarle': 'AlbermarleCountyhourlyinsolation2017.csv',
           'Chesapeake': 'ChesapeakeCityhourlyinsolation2017.csv',
           'KingGeorge': 'KingGeorgeCountyhourlyinsolation2017.csv'},
}

def load_solar_cf(year, location):
    fname = PROJECT_DIR + SOLAR_FILES[year][location]
    df = pd.read_csv(fname)
    col = [c for c in df.columns if c != 'Time stamp'][0]
    raw = df[col].values.astype(float)
    assert len(raw) == 8760, f"{fname}: expected 8760 rows, got {len(raw)}"
    return raw / raw.max()

def blended_solar_cf(year):
    cfs = [load_solar_cf(year, loc) for loc in ['Albermarle', 'Chesapeake', 'KingGeorge']]
    return np.mean(cfs, axis=0)

def parse_cvow_cf_matrix(year):
    """2016: standard matrix format, same parser as build_new_weather_years.py."""
    fname = PROJECT_DIR + f'{year}CVOWhourlymatrixkWhWake140mresults.csv'
    df = pd.read_csv(fname)
    real = df.iloc[1:].drop(columns=['Time stamp']).reset_index(drop=True)
    day_cols = [str(d) for d in range(1, 366)]
    matrix = real[day_cols].values.astype(float)
    hourly_kwh = matrix.T.flatten()
    return hourly_kwh / (CVOW_MW * 1000)

def parse_cvow_cf_2017_corrected(fname=PROJECT_DIR + '2017CVOWhourlyout.csv'):
    """2017: single mislabeled column, documented correction applied (values are MWh,
    not kWh) -- see module docstring."""
    df = pd.read_csv(fname)
    raw_mwh = df['kWh'].values.astype(float)  # column name is the mislabel itself
    assert len(raw_mwh) == 8760, f"expected 8760 rows, got {len(raw_mwh)}"
    return raw_mwh / CVOW_MW

JAN_MAR_HOURS = (31 + 28 + 31) * 24  # 2160, non-leap

def splice_fiscal_year(arr_year_n, arr_year_n1):
    assert len(arr_year_n) == 8760 and len(arr_year_n1) == 8760
    return np.concatenate([arr_year_n[JAN_MAR_HOURS:], arr_year_n1[:JAN_MAR_HOURS]])

def build():
    solar_fy = splice_fiscal_year(blended_solar_cf(2016), blended_solar_cf(2017))
    wind_fy = splice_fiscal_year(parse_cvow_cf_matrix(2016), parse_cvow_cf_2017_corrected())

    sibling = np.load('/mnt/user-data/uploads/hydro_year_2018_19.npz')
    nuclear_fy = sibling['nuclear']
    exist_solar_fy = sibling['exist_solar']

    out_path = 'hydro_year1_2016_17_RECONSTRUCTED.npz'
    np.savez(out_path, solar=solar_fy, wind=wind_fy, nuclear=nuclear_fy, exist_solar=exist_solar_fy)

    print(f"Built {out_path}")
    print(f"  solar_cf: min={solar_fy.min():.4f} max={solar_fy.max():.4f} mean={solar_fy.mean():.4f}")
    print(f"  wind_cf:  min={wind_fy.min():.4f} max={wind_fy.max():.4f} mean={wind_fy.mean():.4f}")
    print(f"  nuclear:  min={nuclear_fy.min():.1f} max={nuclear_fy.max():.1f} (exact, from sibling file)")
    print(f"  exist_solar: min={exist_solar_fy.min():.1f} max={exist_solar_fy.max():.1f} (exact, from sibling file)")
    return solar_fy, wind_fy, nuclear_fy, exist_solar_fy

if __name__ == '__main__':
    build()
