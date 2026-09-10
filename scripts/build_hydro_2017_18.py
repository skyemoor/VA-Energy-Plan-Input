"""
build_hydro_2017_18.py

Reconstructs hydro_year_2017_18.npz, the fourth previously-missing weather year requested
this session -- extends build_hydro_2016_17.py's own established methodology (SES Rule 1)
directly, not a new approach: equal-weight 3-county solar blend (Albemarle/Chesapeake/
King George), each normalized by its own file's peak; CVOW wind normalized by 2,587.2 MW
nameplate; April-March hydrological-year splicing; nuclear/exist_solar copied from the
same hydro_year_2018_19.npz sibling every other weather-year file in this project uses
(these represent a generic, weather-independent shape, not a historical-year-specific one --
per that same established pattern).

Source selection: 2017 solar uses the same `...hourlyinsolation2017.csv` family as
build_hydro_2016_17.py's own 2017 half (already verified consistent there). 2018 solar uses
the `{year}{County}hourlyresults.csv` family instead -- a DIFFERENT filename convention but
the SAME underlying structure (Time stamp + "System power generated | (kW)", already-simulated
power output) -- confirmed directly by inspecting the file, not assumed from the name alone.
This keeps the same "already-simulated, no PySAM needed" approach build_hydro_2016_17.py used,
even though PySAM is now installed and available this session -- simpler and consistent with
the established convention wins over using the newly-available tool just because it's available.
2018 wind uses the standard CVOW matrix format (parse_cvow_cf_matrix, reused unchanged).
"""
import pandas as pd
import numpy as np

PROJECT_DIR = '/mnt/project/'
CVOW_MW = 2587.2

SOLAR_FILES_2017 = {'Albermarle': 'AlbermarleCountyhourlyinsolation2017.csv',
                     'Chesapeake': 'ChesapeakeCityhourlyinsolation2017.csv',
                     'KingGeorge': 'KingGeorgeCountyhourlyinsolation2017.csv'}
SOLAR_FILES_2018 = {'Albermarle': '2018Albermarlehourlyresults.csv',
                     'Chesapeake': '2018Chesapeakehourlyresults.csv',
                     'KingGeorge': '2018KingGeorgehourlyresults.csv'}

def load_solar_cf(fname):
    df = pd.read_csv(PROJECT_DIR + fname)
    col = [c for c in df.columns if c != 'Time stamp'][0]
    raw = df[col].values.astype(float)
    assert len(raw) == 8760, f"{fname}: expected 8760 rows, got {len(raw)}"
    return raw / raw.max()

def blended_solar_cf(files_dict):
    cfs = [load_solar_cf(files_dict[loc]) for loc in ['Albermarle', 'Chesapeake', 'KingGeorge']]
    return np.mean(cfs, axis=0)

def parse_cvow_cf_matrix(year):
    fname = PROJECT_DIR + f'{year}CVOWhourlymatrixkWhWake140mresults.csv'
    df = pd.read_csv(fname)
    real = df.iloc[1:].drop(columns=['Time stamp']).reset_index(drop=True)
    day_cols = [str(d) for d in range(1, 366)]
    matrix = real[day_cols].values.astype(float)
    hourly_kwh = matrix.T.flatten()
    return hourly_kwh / (CVOW_MW * 1000)

def parse_cvow_cf_2017_corrected():
    df = pd.read_csv(PROJECT_DIR + '2017CVOWhourlyout.csv')
    raw_mwh = df['kWh'].values.astype(float)  # column name is the mislabel itself (see build_hydro_2016_17.py)
    assert len(raw_mwh) == 8760, f"expected 8760 rows, got {len(raw_mwh)}"
    return raw_mwh / CVOW_MW

JAN_MAR_HOURS = (31 + 28 + 31) * 24  # 2160, non-leap

def splice_fiscal_year(arr_year_n, arr_year_n1):
    assert len(arr_year_n) == 8760 and len(arr_year_n1) == 8760
    return np.concatenate([arr_year_n[JAN_MAR_HOURS:], arr_year_n1[:JAN_MAR_HOURS]])

def build():
    solar_fy = splice_fiscal_year(blended_solar_cf(SOLAR_FILES_2017), blended_solar_cf(SOLAR_FILES_2018))
    wind_fy = splice_fiscal_year(parse_cvow_cf_2017_corrected(), parse_cvow_cf_matrix(2018))

    sibling = np.load('/mnt/user-data/uploads/hydro_year_2018_19.npz')
    nuclear_fy = sibling['nuclear']
    exist_solar_fy = sibling['exist_solar']

    out_path = 'hydro_year_2017_18_RECONSTRUCTED.npz'
    np.savez(out_path, solar=solar_fy, wind=wind_fy, nuclear=nuclear_fy, exist_solar=exist_solar_fy)

    print(f"Built {out_path}")
    print(f"  solar_cf: min={solar_fy.min():.4f} max={solar_fy.max():.4f} mean={solar_fy.mean():.4f}")
    print(f"  wind_cf:  min={wind_fy.min():.4f} max={wind_fy.max():.4f} mean={wind_fy.mean():.4f}")
    return solar_fy, wind_fy, nuclear_fy, exist_solar_fy

if __name__ == '__main__':
    build()
