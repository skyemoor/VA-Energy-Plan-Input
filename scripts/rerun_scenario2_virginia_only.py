import sys, time; sys.path.insert(0,'/home/claude/repo/lp_package')
import numpy as np, pandas as pd
import lp_model as lp, driver as drv
from scenario2_reserve_margin import compare_capacity_standards
from virginia_only_demand import to_virginia_only_load, describe_conversion

df = pd.read_csv('/mnt/project/DOMLSEHourlyLoadProjections2024through2048.csv')
hrs=[str(h) for h in range(1,25)]
def fy(y):
    a=df[(df.Year==y)&(df.Month>=4)].sort_values(['Month','Day'])
    b=df[(df.Year==y+1)&(df.Month<=3)].sort_values(['Month','Day'])
    a=a[~((a.Month==2)&(a.Day==29))]; b=b[~((b.Month==2)&(b.Day==29))]
    o=np.concatenate([a[hrs].values.astype(float).flatten(), b[hrs].values.astype(float).flatten()])
    assert len(o)==8760; return o

w = np.load('/home/claude/repo/data/weather_years/hydro_year1_2016_17_RECONSTRUCTED.npz')
solar_cf, wind_cf, nuclear = w['solar'], w['wind'], w['nuclear']

def statutory_solar_mw(year):
    return 16100.0 if year>=2035 else 16100.0*(year-2026)/(2035-2026)

print(f"{'Yr':<6} {'solarMW':>9} {'NaMW':>8} {'FeMW':>7} {'CCGT_MW':>9} {'gasTWh':>8} {'curtTWh':>8} {'unsvd':>8} {'secs':>6}")
print('-'*74)
out={}
for year in (2030, 2035, 2040):
    t0=time.time()
    demand = to_virginia_only_load(fy(year), year)   # VA-only load basis, losses retained
    exist = lp.exist_solar_mw(year)*solar_cf
    sol_mw = statutory_solar_mw(year)
    na_mw = drv.vcea_short_duration_floor_mw(year)
    fe_mw = drv.vcea_long_duration_floor_mw(year)
    # CCGT sized per Appendix C.2: worst hourly gap, zero storage credit
    cmp = compare_capacity_standards(demand, nuclear, exist, solar_cf, wind_cf,
            sol_mw, na_mw, fe_mw, bath_county_mw=3000.0)
    ccgt = cmp['appendix_c2_gas_mw_zero_storage_credit_no_margin']
    drv.set_year_capex(year)
    p = lp.build_scenario2_problem(solar_cf, wind_cf, nuclear, exist, demand,
            vcea_solar_mw=sol_mw, ccgt_mw=ccgt, na_power_mw=na_mw, na_duration_hr=6.0,
            fe_power_mw=fe_mw, fe_duration_hr=100.0,
            gas_price_mwh=lp.gas_cost_mwh(year, heat_rate=lp.CCGT_HEAT_RATE)
                if hasattr(lp,'CCGT_HEAT_RATE') else lp.gas_cost_mwh(year),
            ccgt_vom_mwh=2.0, verbose=False)
    r = lp.solve_problem(p)
    IDX=p['IDX']; NB,NPH=p['hv_params']; T=p['T']
    hv=lambda t,k: NB+t*NPH+IDX[k]
    gas=sum(r.x[hv(t,'g')] for t in range(T))
    curt=sum(r.x[hv(t,'curt')] for t in range(T))
    uns=sum(r.x[hv(t,'unserved')] for t in range(T))
    out[year]=dict(solar=sol_mw,na=na_mw,fe=fe_mw,ccgt=ccgt,gas=gas,curt=curt,uns=uns,
                   na_soc=np.array([r.x[hv(t,'nsoc')] for t in range(T)]),
                   fe_soc=np.array([r.x[hv(t,'fsoc')] for t in range(T)]), demand=demand,
                   exist=exist, success=r.success)
    print(f"{year:<6} {sol_mw:>9,.0f} {na_mw:>8,.0f} {fe_mw:>7,.0f} {ccgt:>9,.0f} "
          f"{gas/1e6:>8.1f} {curt/1e6:>8.2f} {uns:>8,.0f} {time.time()-t0:>6.0f}")
np.savez('/tmp/s2_rerun_va.npz', **{f'{y}_{k}':v for y,d in out.items()
         for k,v in d.items() if isinstance(v,np.ndarray)})
import pickle; pickle.dump({y:{k:v for k,v in d.items() if not isinstance(v,np.ndarray)}
                            for y,d in out.items()}, open('/tmp/s2_scalars_va.pkl','wb'))
