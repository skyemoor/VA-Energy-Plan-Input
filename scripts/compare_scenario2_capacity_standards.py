import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath('/home/claude/repo/lp_package/driver.py')))
import numpy as np, pandas as pd
import driver as drv, lp_model as lp
from scenario2_reserve_margin import compare_capacity_standards

df = pd.read_csv('/mnt/project/DOMLSEHourlyLoadProjections2024through2048.csv')
hrs = [str(h) for h in range(1, 25)]
JM = (31 + 28 + 31) * 24

def fiscal_year_demand(y):
    """April Y through March Y+1, Feb 29 excluded so every year is exactly 8,760 hours.
    Selected by calendar date rather than hour offset -- a fixed offset silently breaks on
    leap years (2040 has 8,784 hours), which is the leap-year hazard recorded in
    docs/methodology/Demand_Basis_and_RPS_Compliance_Working_Notes.md, open item 6."""
    first = df[(df.Year == y) & (df.Month >= 4)].sort_values(['Month','Day'])
    second = df[(df.Year == y+1) & (df.Month <= 3)].sort_values(['Month','Day'])
    second = second[~((second.Month == 2) & (second.Day == 29))]
    first = first[~((first.Month == 2) & (first.Day == 29))]
    out = np.concatenate([first[hrs].values.astype(float).flatten(),
                          second[hrs].values.astype(float).flatten()])
    assert len(out) == 8760, f"{y} fiscal year produced {len(out)} hours, expected 8760"
    return out

w = np.load('../data/weather_years/hydro_year1_2016_17_RECONSTRUCTED.npz')

def statutory_solar_mw(year):
    """S2 solar: linear to 16,100 MW by 2035 per 56-585.5(D)(2), flat thereafter.
    2026 treated as zero-build start, matching the project's own interpolation convention."""
    if year >= 2035:
        return 16100.0
    return 16100.0 * (year - 2026) / (2035 - 2026)

BATH_MW = 3000.0
print(f"{'Year':<6} {'PeakMW':>9} {'C2 rule':>10} {'ReserveMgn':>11} {'Diff':>9} {'Storage':>9}")
print('-' * 60)
rows = []
for year in (2030, 2035, 2040, 2045):
    demand = fiscal_year_demand(year)
    exist = lp.exist_solar_mw(year) * w['solar']
    r = compare_capacity_standards(
        demand, w['nuclear'], exist, w['solar'], w['wind'],
        statutory_solar_mw=statutory_solar_mw(year),
        short_duration_storage_mw=drv.vcea_short_duration_floor_mw(year),
        long_duration_storage_mw=drv.vcea_long_duration_floor_mw(year),
        bath_county_mw=BATH_MW)
    rows.append((year, r))
    print(f"{year:<6} {r['demand_at_peak_mw']:>9,.0f} "
          f"{r['appendix_c2_gas_mw_zero_storage_credit_no_margin']:>10,.0f} "
          f"{r['reserve_margin_gas_mw_storage_credited']:>11,.0f} "
          f"{r['difference_mw']:>+9,.0f} {r['storage_power_credited_mw']:>9,.0f}")
print()
print("Negative Diff = the reserve-margin standard requires LESS gas than Appendix C.2's rule,")
print("because crediting storage more than offsets the 17.7% margin.")
