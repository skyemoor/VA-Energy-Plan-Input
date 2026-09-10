"""
simulate_8yr_dispatch.py

Continuous, 8-real-weather-year dispatch simulation (not an LP) of the fixed 2030 build
against real, chronological historical weather. SoC starts at 50% only at hour 0, carries
continuously across all 70,080 hours with no resets and no forced ending value, per direct
instruction this session.

Bath County: modeled as a once-daily-cycle state machine (charge/ready/discharge), not
economically-dispatched like Na-ion -- per direct physical guidance this session (pumped
hydro doesn't ramp on/off freely; runs one full cycle a day, timed to the period it's
actually needed). Trigger to discharge: residual demand (after clean generation) rising
above its own trailing 24-hour rolling average -- lets the window fall wherever the real
daily demand shape puts it, rather than a fixed clock time, matching the "doesn't have to
be on specific day boundaries" instruction.

Na-ion: flexible, per-hour greedy dispatch (same _dispatch_one_hour pattern as
loudoun_battery_dispatch.py's own established, tested logic -- reused conceptually, not
duplicated verbatim, since this context has multiple generation sources and gas that
module's own single-source version doesn't).

Distributed segment solar: DISCLOSED APPROXIMATION -- uses the utility-scale solar CF as a
stand-in for all 8 years (real Sterling/Arlington 45-deg-tilt data only exists for the
2016-17 weather year this session). Applied consistently across all 8 years rather than
mixing real data for one year with the proxy for the other seven, to avoid an artificial
discontinuity at that boundary.
"""
import numpy as np
import pandas as pd

d = np.load('chained_8yr_weather.npz')
solar_cf, wind_cf, nuclear, exist_solar_cf_base, demand = (
    d['solar'], d['wind'], d['nuclear'], d['exist_solar'], d['demand'])
T = len(demand)

# ---- Fixed 2030 build (from the free, enforce_closing_soc=False solve) ----
UTIL_SOLAR_MW = 8126.6
DIST_SOLAR_MW = 2031.6
NA_POWER_MW = 4000.0
NA_ENERGY_MWH = 24000.0
BATH_POWER_MW = 3000.0
BATH_ENERGY_MWH = 24000.0
EXIST_SOLAR_2030_MW = 5194.8  # lp.exist_solar_mw(2030), a pure function -- no file needed
CVOW_MW = 2587.2
GAS_CAP_MW = 12224.0  # schedule_b_baseline_mw(2030) + 2862.0, already computed earlier this session

# ---- Generation ----
# BUG FOUND AND FIXED (this run): the hydro_year*.npz files' own "exist_solar" key is ALREADY an
# absolute MW value (confirmed directly: range 0-4,806 MW, not 0-1), not a capacity factor -- an
# earlier version of this script wrongly multiplied it by nameplate a second time, producing
# curtailment in the hundreds of billions of MWh. Recomputing properly instead: exist_solar_mw(2030)
# (a pure function) x THIS weather year's own real solar_cf, matching the same, correctly-scaled
# approach already used and verified earlier this session, and letting exist_solar's own shape vary
# by weather year rather than reusing one file's fixed, possibly differently-scaled shape.
# ---- Distributed segment solar: REAL Sterling/Arlington data, all 8 years (previously a disclosed
# utility-CF proxy for 7 of the 8 years -- resolved this run, real data now available for the full set) ----
dist_solar_cf = np.load('dist_solar_cf_8yr_chained_REAL.npy')
assert len(dist_solar_cf) == T, f"dist_solar_cf length {len(dist_solar_cf)} != T {T}"

util_solar_gen = UTIL_SOLAR_MW * solar_cf
dist_solar_gen = DIST_SOLAR_MW * dist_solar_cf
exist_solar_gen = EXIST_SOLAR_2030_MW * solar_cf
wind_gen = CVOW_MW * wind_cf
clean_gen = nuclear + wind_gen + util_solar_gen + dist_solar_gen + exist_solar_gen
residual_before_storage = demand - clean_gen

rolling_avg_24h = pd.Series(residual_before_storage).rolling(24, min_periods=1).mean().values

# ---- Simulation state ----
na_soc = 0.5 * NA_ENERGY_MWH
bath_soc = 0.5 * BATH_ENERGY_MWH
bath_state = 'ready'  # 'charging', 'ready' (full, waiting for trigger), 'discharging'
EPS = 1e-6

na_charge = np.zeros(T); na_discharge = np.zeros(T); na_soc_arr = np.zeros(T)
bath_charge = np.zeros(T); bath_discharge = np.zeros(T); bath_soc_arr = np.zeros(T)
gas = np.zeros(T); unserved = np.zeros(T); curtailment = np.zeros(T)

for t in range(T):
    r = residual_before_storage[t]

    # --- Bath state machine ---
    if bath_state in ('ready', 'charging') and bath_soc < BATH_ENERGY_MWH - EPS:
        c = min(BATH_POWER_MW, BATH_ENERGY_MWH - bath_soc)
        bath_soc += c
        bath_charge[t] = c
        bath_state = 'charging'
    elif bath_state == 'charging':
        bath_state = 'ready'  # just became full this hour
    if bath_state == 'ready' and r > rolling_avg_24h[t]:
        bath_state = 'discharging'
    if bath_state == 'discharging':
        dis = min(BATH_POWER_MW, bath_soc, max(0.0, r))
        bath_soc -= dis
        bath_discharge[t] = dis
        if bath_soc <= EPS or r <= rolling_avg_24h[t]:
            bath_state = 'ready'

    r_after_bath = r - bath_discharge[t] + bath_charge[t]

    # --- Na-ion: flexible greedy dispatch ---
    if r_after_bath > 0:
        dis = min(r_after_bath, NA_POWER_MW, na_soc)
        na_soc -= dis
        na_discharge[t] = dis
    elif r_after_bath < 0:
        excess = -r_after_bath
        c = min(excess, NA_POWER_MW, NA_ENERGY_MWH - na_soc)
        na_soc += c
        na_charge[t] = c

    r_after_storage = r_after_bath - na_discharge[t] + na_charge[t]

    # --- Gas, then unserved / curtailment ---
    if r_after_storage > 0:
        g = min(r_after_storage, GAS_CAP_MW)
        gas[t] = g
        unserved[t] = max(0.0, r_after_storage - g)
    else:
        curtailment[t] = -r_after_storage

    na_soc_arr[t] = na_soc
    bath_soc_arr[t] = bath_soc

print(f"Total hours simulated: {T}")
print(f"Total unserved energy: {unserved.sum():,.1f} MWh across {np.sum(unserved>0)} hours")
print(f"Total curtailment: {curtailment.sum():,.1f} MWh")
print(f"Total gas dispatched: {gas.sum():,.1f} MWh, max hourly gas: {gas.max():,.1f} MW (cap {GAS_CAP_MW})")
print(f"Hours gas at/near cap (>=99%): {np.sum(gas >= 0.99*GAS_CAP_MW)}")
if unserved.sum() > 0:
    worst = np.argmax(unserved)
    print(f"Worst unserved hour: index {worst}, {unserved[worst]:,.1f} MW")

np.savez('sim_8yr_result.npz', na_charge=na_charge, na_discharge=na_discharge, na_soc=na_soc_arr,
         bath_charge=bath_charge, bath_discharge=bath_discharge, bath_soc=bath_soc_arr,
         gas=gas, unserved=unserved, curtailment=curtailment, demand=demand, clean_gen=clean_gen)
print("Saved sim_8yr_result.npz")
