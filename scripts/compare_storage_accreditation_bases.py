import sys; sys.path.insert(0, '/home/claude/repo/lp_package')
"""Compares own-data storage accreditation computed from LP dispatch (perfect foresight)
against the same computation on no-foresight heuristic dispatch. The contrast is the point:
see lp_package/storage_accreditation.py for the finding this script produced."""
import numpy as np, pandas as pd
from storage_accreditation import (peak_net_demand_hours, compute_from_dispatch,
                                    apply_cross_validation, storage_penetration_ratio,
                                    NA_DEPTH_OF_DISCHARGE_FLOOR_FRACTION as DOD)

FILES = {2030:'VA_2030_Scenario1_hourly_FINAL.csv', 2035:'VA_2035_Scenario1_hourly_FINAL.csv',
         2040:'VA_2040_Scenario1_hourly_FINAL.csv', 2045:'VA_2045_TRUE_FINAL_ZeroCurt_hourly.csv'}
PJM_4HR = 0.50

print("=== A. Own-data credit from LP dispatch (PERFECT FORESIGHT) ===")
print(f"{'Year':<6} {'NaPowerMW':>10} {'Pen%':>7} {'OwnCredit':>10}")
print('-'*38)
for year, fn in FILES.items():
    df = pd.read_csv(f'../results/hourly_dispatch/{fn}')
    dem, nuc = df['demand_mw'].values, df['nuclear_mw'].values
    wind, sol = df['wind_mw'].values, df['solar_total_mw'].values
    na_soc = df['na_soc_mwh'].values
    if 'na_discharge_mw' in df.columns:
        na_power = max(df['na_discharge_mw'].max(), df['na_charge_mw'].max())
    else:
        na_power = np.abs(df['na_net_mw'].values).max()
    idx = peak_net_demand_hours(dem, nuc, np.zeros(len(df)), wind, sol)
    credit = compute_from_dispatch(na_soc, na_power, idx, DOD, na_soc.max())
    pen = storage_penetration_ratio(na_power, dem.max())
    print(f"{year:<6} {na_power:>10,.0f} {pen*100:>6.1f}% {credit:>10.1%}")

print()
print("=== B. Own-data credit from 8-year heuristic dispatch (NO FORESIGHT), 2045 fleet ===")
sim = np.load('/tmp/sim2045_8yr.npz')
w = np.load('../data/weather_years/chained_8yr_weather.npz') if False else None
wch = np.load('/home/claude/work/chained_8yr_weather.npz')
dist = np.load('/home/claude/work/dist_solar_cf_8yr_chained_REAL.npy')
demand = np.tile(np.load('/home/claude/work/demand_2045fy.npy'), 8)
UTIL, DISTS, EXIST, CVOW = 166340.7, 7440.0, 4818.5, 2587.2
NA_POW, NA_EN = 50546.5, 363380.2
solar_gen = (UTIL + EXIST) * wch['solar'] + DISTS * dist
wind_gen = CVOW * wch['wind']
idx = peak_net_demand_hours(demand, wch['nuclear'], np.zeros(len(demand)), wind_gen, solar_gen)
credit_hz = compute_from_dispatch(sim['na_soc'], NA_POW, idx, DOD, NA_EN)
pen_hz = storage_penetration_ratio(NA_POW, demand.max())
print(f"  Na power {NA_POW:,.0f} MW | penetration {pen_hz*100:.1f}% | own-data credit {credit_hz:.1%}")
cv = apply_cross_validation(credit_hz, PJM_4HR, 'Na-ion 2045')
print(f"  cross-validated: own {cv['own_data_credit']:.1%} vs PJM {cv['published_credit']:.0%} "
      f"-> adopted {cv['adopted_credit']:.1%} (source: {cv['source_adopted']})")
