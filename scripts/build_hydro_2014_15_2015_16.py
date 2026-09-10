"""
build_hydro_2014_15_2015_16.py

Reconstructs hydro_year_2014_15.npz and hydro_year_2015_16.npz -- extends
build_hydro_2016_17.py / build_hydro_2017_18.py's own established methodology directly
(SES Rule 1): equal-weight 3-county solar blend, each normalized by its own file's peak;
CVOW wind normalized by 2,587.2 MW nameplate; April-March splicing; nuclear/exist_solar
copied from hydro_year_2018_19.npz per this project's own established convention.

2015 solar: Albemarle/Chesapeake/KingGeorgehourlyresults_2015.csv -- real SAM output,
uploaded directly by the user this session specifically to resolve an earlier, genuine
methodology mismatch (a PySAM reconstruction at standard utility tilt/tracking configs
undershot the established ~22.5% mean-CF benchmark by 30%+ and was correctly not used).
Same already-simulated "Time stamp + System power generated (kW)" structure as every
other year in this set, confirmed directly before use, not assumed from the filename.
2015 wind: 2015CVOWhourlymatrixkWhWake140mresults.csv, standard matrix format, uploaded
this session to resolve the second half of the same original gap.
"""
import pandas as pd
import numpy as np

PROJECT_DIR = '/mnt/project/'
CVOW_MW = 2587.2

SOLAR_FILES = {
    2014: {'Albermarle': 'Albermarle2014.csv', 'Chesapeake': 'Chesapeake2014.csv',
           'KingGeorge': 'KingGeorge2014.csv'},
    2015: {'Albermarle': 'Albemarlehourlyresults_2015.csv', 'Chesapeake': 'Chesapeakehourlyresults_2015.csv',
           'KingGeorge': 'KingGeorgehourlyresults_2015.csv'},
    2016: {'Albermarle': 'AlbermarleCountyhourlyinsolation2016.csv',
           'Chesapeake': 'ChesapeakeCityhourlyinsolation2016.csv',
           'KingGeorge': 'KingGeorgeCountyhourlyinsolation2016.csv'},
}

def load_solar_cf(fname):
    df = pd.read_csv(PROJECT_DIR + fname)
    col = [c for c in df.columns if c != 'Time stamp'][0]
    raw = df[col].values.astype(float)
    assert len(raw) == 8760, f"{fname}: expected 8760 rows, got {len(raw)}"
    return raw / raw.max()

def blended_solar_cf(year):
    files = SOLAR_FILES[year]
    cfs = [load_solar_cf(files[loc]) for loc in ['Albermarle', 'Chesapeake', 'KingGeorge']]
    return np.mean(cfs, axis=0)

def parse_cvow_cf(year):
    """Auto-detects which of the two known CVOW file layouts this year's file actually uses --
    confirmed directly this session that the SAME filename convention covers two genuinely
    different internal formats (2014's file is simple Time-stamp+kW, not the day-by-day matrix
    2016/2018 use), despite an identical name pattern. Checking the header rather than assuming
    a uniform format across years."""
    fname = PROJECT_DIR + f'{year}CVOWhourlymatrixkWhWake140mresults.csv'
    df = pd.read_csv(fname)
    if 'Time stamp' in df.columns and len(df.columns) == 2:
        raw_kw = df[[c for c in df.columns if c != 'Time stamp'][0]].values.astype(float)
        assert len(raw_kw) == 8760, f"{fname}: expected 8760 rows, got {len(raw_kw)}"
        return raw_kw / (CVOW_MW * 1000)
    else:
        real = df.iloc[1:].drop(columns=['Time stamp']).reset_index(drop=True)
        day_cols = [str(d) for d in range(1, 366)]
        matrix = real[day_cols].values.astype(float)
        hourly_kwh = matrix.T.flatten()
        return hourly_kwh / (CVOW_MW * 1000)

JAN_MAR_HOURS = (31 + 28 + 31) * 24

def splice_fiscal_year(arr_n, arr_n1):
    assert len(arr_n) == 8760 and len(arr_n1) == 8760
    return np.concatenate([arr_n[JAN_MAR_HOURS:], arr_n1[:JAN_MAR_HOURS]])

def build(year_n, year_n1, out_name):
    solar_fy = splice_fiscal_year(blended_solar_cf(year_n), blended_solar_cf(year_n1))
    wind_fy = splice_fiscal_year(parse_cvow_cf(year_n), parse_cvow_cf(year_n1))
    sibling = np.load('/mnt/user-data/uploads/hydro_year_2018_19.npz')
    np.savez(out_name, solar=solar_fy, wind=wind_fy, nuclear=sibling['nuclear'], exist_solar=sibling['exist_solar'])
    print(f"Built {out_name}: solar mean={solar_fy.mean():.4f} max={solar_fy.max():.4f} | "
          f"wind mean={wind_fy.mean():.4f} max={wind_fy.max():.4f}")

build(2014, 2015, 'hydro_year_2014_15_RECONSTRUCTED.npz')
build(2015, 2016, 'hydro_year_2015_16_RECONSTRUCTED.npz')
