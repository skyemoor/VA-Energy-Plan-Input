"""
Continuous 8-real-weather-year dispatch of the FIXED 2045 build (solved this session, full year,
100% clean, zero unserved on its 2016-17 design year). SoC starts at 50% at hour 0 only, then
free-floats across all 70,080 hours -- never reset at year boundaries, no forced ending value.
2045 has NO gas, so storage and clean generation must cover everything or load is unserved.
"""
import numpy as np, pandas as pd

# --- Fixed 2045 build ---
UTIL_SOLAR, DIST_SOLAR = 166340.7, 7440.0
NA_POW, NA_EN = 50546.5, 363380.2
FE_EN = 3635866.8; FE_POW = FE_EN/100.0          # FE_DURATION=100
DNA_POW, DNA_EN = 7440.0, 29760.0
BATH_POW, BATH_EN = 3000.0, 24000.0
EXIST_SOLAR_2045, CVOW_MW = 4818.5, 2587.2
NA_RTE, FE_RTE, BATH_RTE = 0.90, 0.80, 0.80
NA_FLOOR = 0.20   # DoD floor, per lp_model

d = np.load('chained_8yr_weather.npz')
scf, wcf, nuc = d['solar'], d['wind'], d['nuclear']
dcf = np.load('dist_solar_cf_8yr_chained_REAL.npy')
demand = np.tile(np.load('demand_2045fy.npy'), 8)
T = len(demand)

clean = (nuc + CVOW_MW*wcf + (UTIL_SOLAR+EXIST_SOLAR_2045)*scf + DIST_SOLAR*dcf)
resid = demand - clean
roll = pd.Series(resid).rolling(24, min_periods=1).mean().values

bath, na, fe, dna = 0.5*BATH_EN, 0.5*NA_EN, 0.5*FE_EN, 0.5*DNA_EN
bstate = 'ready'
uns = np.zeros(T); curt = np.zeros(T)
na_soc = np.zeros(T); fe_soc = np.zeros(T); bath_soc = np.zeros(T)
EPS = 1e-6

for t in range(T):
    r = resid[t]
    # Bath: once-daily cycle state machine (unchanged from the 2030 sim)
    bc = bd = 0.0
    if bstate in ('ready','charging') and bath < BATH_EN-EPS and r < 0:
        bc = min(BATH_POW, (BATH_EN-bath)/BATH_RTE, -r); bath += bc*BATH_RTE; bstate='charging'
    elif bstate=='charging': bstate='ready'
    if bstate=='ready' and r > roll[t]: bstate='discharging'
    if bstate=='discharging':
        bd = min(BATH_POW, bath, max(0.0,r)); bath -= bd
        if bath<=EPS or r<=roll[t]: bstate='ready'
    r2 = r - bd + bc

    if r2 > 0:   # deficit: Na first (fast), then distributed Na, then iron-air (long-duration backstop)
        nd = min(r2, NA_POW, max(0.0, na - NA_FLOOR*NA_EN)); na -= nd; r2 -= nd
        dnd = min(r2, DNA_POW, max(0.0, dna - NA_FLOOR*DNA_EN)); dna -= dnd; r2 -= dnd
        fd = min(r2, FE_POW, fe); fe -= fd; r2 -= fd
        uns[t] = max(0.0, r2)
    elif r2 < 0: # surplus: charge Na, then distributed, then iron-air; curtail the rest
        ex = -r2
        nc = min(ex, NA_POW, (NA_EN-na)/NA_RTE); na += nc*NA_RTE; ex -= nc
        dnc = min(ex, DNA_POW, (DNA_EN-dna)/NA_RTE); dna += dnc*NA_RTE; ex -= dnc
        fc = min(ex, FE_POW, (FE_EN-fe)/FE_RTE); fe += fc*FE_RTE; ex -= fc
        curt[t] = ex
    na_soc[t], fe_soc[t], bath_soc[t] = na, fe, bath

yrs = ['2012-13','2013-14','2014-15','2015-16','2016-17','2017-18','2018-19','2019-20']
print(f"Total unserved: {uns.sum():,.0f} MWh across {(uns>0).sum():,} hours ({(uns>0).mean()*100:.2f}% of hours)")
print(f"Total curtailment: {curt.sum()/1e6:,.1f} TWh")
print(f"\nBy hydro year:")
for i,y in enumerate(yrs):
    s=slice(i*8760,(i+1)*8760)
    print(f"  {y}: unserved {uns[s].sum():>12,.0f} MWh ({(uns[s]>0).sum():>4} hrs) | "
          f"FE SoC end {fe_soc[s][-1]/FE_EN*100:5.1f}% | FE SoC min {fe_soc[s].min()/FE_EN*100:5.1f}%")
print(f"\nIron-air SoC: start 50.0% -> end {fe_soc[-1]/FE_EN*100:.1f}% | min over 8 yrs {fe_soc.min()/FE_EN*100:.1f}%")
print(f"Na-ion SoC:   min {na_soc.min()/NA_EN*100:.1f}% (DoD floor 20%)")
np.savez('/tmp/sim2045_8yr.npz', uns=uns, curt=curt, na_soc=na_soc, fe_soc=fe_soc, bath_soc=bath_soc)
