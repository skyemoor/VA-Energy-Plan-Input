"""
distributed_physical_bounds.py

Applies real physical bounds to the distributed segment's build variables. Without these the LP
found a genuinely unbounded corner and exploited it: a 2026-09-09 gas-outage stress run built
1,433,774 MWh (1.43 TWh) of DISTRIBUTED iron-air -- roughly 60x the entire utility Na-ion fleet,
discharging 14.3 GW -- because iron-air energy capex ($18.03/kWh) is 3.6x cheaper than Na-ion's
($65.16/kWh) and FE_DURATION=100 means power is derived as energy/100, so the LP built absurd
energy capacity purely to extract power from it. Nothing in the formulation bounded distributed
storage against rooftop area, feeder capacity, or anything else physical.

Three bounds, each from a real, already-established source rather than invented here:

1. STORAGE PAIRING (1:1 power, 4-hour duration) -- this project's own convention from
   Northern_Virginia_Solar_Assessment_Methodology_and_Findings.md Section 1, which sized every
   county's parking-canopy storage as "paired battery storage at a 1:1 MW ratio, 4-hour duration."
   Implemented as two cheap constraint rows (2 nonzeros each), NOT dense rows -- charging_adequacy.py's
   four dense rows (8,760 entries each) stalled dual simplex badly, so this deliberately avoids that.

2. NO DISTRIBUTED IRON-AIR -- pinned to (0,0). Follows structurally from bound 1: FE_DURATION=100
   makes a 4-hour duration impossible for iron-air, so a 100-hour asset cannot satisfy the pairing
   rule at all. Also the physically right answer independently: iron-air is a utility-scale
   technology, not a rooftop or parking-canopy one. Pinned explicitly rather than left to emerge, so
   the reason is visible in the model rather than an accident of the arithmetic.

3. SITING CAP on distributed solar -- default 7,440 MW for the DOM zone, derived 2026-09-09 by
   re-basing the four-county NoVA assessment and extrapolating statewide. Two corrections were made
   in that derivation, both documented in this session: (a) Prince William's parking-lot figure was
   re-anchored from population density to C&I building footprint, cutting it from 1,734.7 MW to
   335.6 MW -- its original per-capita anchor imported Loudoun's data-center-driven parking anomaly,
   giving PWC a parking:C&I ratio of 6.36 versus 1.23 (Loudoun) and 0.79 (Arlington), physically
   implausible; (b) the statewide per-capita extrapolation rate (0.93 kW/capita) EXCLUDES Loudoun for
   the same reason. Revised four-county total: 4,638.6-5,399.3 MW, down 25% from 6,159.0-7,148.2.
   NOTE: 6,159 MW was the fleet basis for this project's own six-day-lookahead firming work, so that
   ~4.3% firming finding rests on a fleet now believed ~25% overstated -- flagged, not yet revisited.
"""
import numpy as np
from scipy import sparse

DISTRIBUTED_STORAGE_DURATION_HR = 4.0
DOM_ZONE_DISTRIBUTED_SOLAR_CAP_MW = 7440.0


def add_distributed_physical_bounds(problem, siting_cap_mw=DOM_ZONE_DISTRIBUTED_SOLAR_CAP_MW,
                                     duration_hr=DISTRIBUTED_STORAGE_DURATION_HR,
                                     allow_distributed_iron_air=False):
    BUILD_SCALE = problem.get('BUILD_SCALE', 1.0)
    NVAR = problem['A_ub'].shape[1]
    DISTRIBUTED_SOLAR_MW, DIST_NA_POWER, DIST_NA_ENERGY, DIST_FE_ENERGY = 4, 5, 6, 7

    # Ratio constraints: BUILD_SCALE cancels on both sides, so plain 1/-1 coefficients are correct.
    rows, cols, data, rhs = [], [], [], []
    rows += [0, 0]; cols += [DIST_NA_POWER, DISTRIBUTED_SOLAR_MW]; data += [1.0, -1.0]; rhs.append(0.0)
    rows += [1, 1]; cols += [DIST_NA_ENERGY, DIST_NA_POWER]; data += [1.0, -duration_hr]; rhs.append(0.0)
    A_new = sparse.coo_matrix((data, (rows, cols)), shape=(2, NVAR)).tocsr()

    bounds = list(problem['bounds'])
    lo, hi = bounds[DISTRIBUTED_SOLAR_MW]
    cap_scaled = siting_cap_mw / BUILD_SCALE
    bounds[DISTRIBUTED_SOLAR_MW] = (lo, cap_scaled if hi is None else min(hi, cap_scaled))
    if not allow_distributed_iron_air:
        bounds[DIST_FE_ENERGY] = (0.0, 0.0)

    new_problem = dict(problem)
    new_problem['A_ub'] = sparse.vstack([problem['A_ub'], A_new], format='csr')
    new_problem['b_ub'] = np.concatenate([problem['b_ub'], rhs])
    new_problem['bounds'] = bounds
    return new_problem
