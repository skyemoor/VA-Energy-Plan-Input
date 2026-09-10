import time, numpy as np, lp_model as lp, driver as drv
from distributed_physical_bounds import add_distributed_physical_bounds

# DISCLOSED SIMPLIFICATION (2026-09-09): distributed solar is PINNED at its physical siting cap
# (7,440 MW, DOM zone) rather than left free, and the D3 share constraint is made non-binding
# (share set to 0.99) so utility solar can grow freely above the 20% ratio.
# Justification: at 2045's demand (206 TWh, mean 23.6 GW) the LP will certainly drive distributed
# solar to its cap -- the first 2045 solve did exactly that, landing on 7,440.0 MW to the decimal.
# Pinning a variable we already know the answer for removes a degree of freedom and should restore
# the ~164s solve time the equality-D3 version had, without re-imposing the equality's real defect
# (capping TOTAL solar at 37,200 MW and forcing 44.5% unserved energy).
# This should be re-checked if demand assumptions change enough that the cap might not bind.
_orig = lp.solve_problem
lp.solve_problem = lambda p, o=None, m=None: _orig(p, {'time_limit': 265.0}, 'highs-ds')

t0=time.time()
demand=np.load('demand_2045fy.npy'); exist=np.load('exist_solar_2045.npy')
h=np.load('hydro_year1_2016_17_RECONSTRUCTED.npz'); scf,wcf,nuc=h['solar'],h['wind'],h['nuclear']
dcf=np.load('dist_solar_cf_2016_17.npy'); dpr=np.load('dist_price_2030fy.npy')

r = drv.run_solve(2045, 0.0, demand, exist, scf, wcf, nuc,
                  capacity_cap_mw=0.0, return_hourly=True,
                  enable_distributed_segment=True, distributed_solar_cf=dcf,
                  distributed_exogenous_price_mwh=dpr, enforce_closing_soc=True,
                  distributed_share_of_total_solar=0.99,
                  pin_build_mw={'DISTRIBUTED_SOLAR_MW': 7440.0},
                  post_build_hook=add_distributed_physical_bounds)
print(f"[{time.time()-t0:.0f}s] success={r['success']}", flush=True)
tot = r['S_mw']+r['dist_S_mw']
print(f"  TOTAL solar={tot:,.1f} MW  (utility {r['S_mw']:,.1f} + distributed {r['dist_S_mw']:,.1f})")
print(f"  Na-ion: {r['PNA_mw']:,.1f} MW / {r['ENA_mwh']:,.1f} MWh (duration {r['ENA_mwh']/max(r['PNA_mw'],1):.1f} h)")
print(f"  Iron-air: {r['EFE_mwh']:,.1f} MWh = {r['EFE_mwh']/1e6:.3f} TWh (implied power {r['EFE_mwh']/100:,.0f} MW)")
print(f"  dist Na: {r['dist_PNA_mw']:,.1f} MW / {r['dist_ENA_mwh']:,.1f} MWh")
print(f"  unserved={r['unserved_mwh']:,.1f} MWh ({r['unserved_mwh']/demand.sum()*100:.3f}% of demand)")
print(f"  curtailment={r['curt_mwh']:,.1f} MWh   objective=${r['obj']/1e9:,.2f}B/yr")
np.savez('/tmp/s2045.npz', **r['hourly'])
np.savez('/tmp/s2045_scalars.npz', **{k:v for k,v in r.items() if isinstance(v,(int,float))})
