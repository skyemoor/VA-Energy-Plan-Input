"""
storage_accreditation.py

Computes own-data capacity credit for storage from ACTUAL DISPATCH at the peak net-demand hours,
rather than crediting nameplate power or extrapolating a literature penetration curve beyond its
validated range.

WHY (2026-09-10)

Applying the reserve-margin standard to the Statutory Floor scenario produced an 18 GW swing in
required gas capacity at 2045 (22,446 MW under zero storage credit versus 4,485 MW crediting
23,000 MW of storage at nameplate). That entire difference rests on one assumption, and this
project's own evidence argues nameplate crediting is optimistic:

  - The eight-year continuous dispatch test found reserve margin was NEVER violated on a
    nameplate-credited basis while 6.44 million MWh went unserved, because storage sat empty
    85% of hours.
  - E3's independent evaluation of PJM's capacity model states scrambling "risks overstating …
    the ELCC of energy storage resources" because storage "is likely to run out of charge"
    during multi-day events that method underrepresents.
  - PJM's own Independent Market Monitor has criticised class-level ELCC accreditation for not
    being unit specific and not incorporating hourly supply and demand matching.

WHY NOT APPENDIX A.13's ALGORITHM 2

A.13 Algorithm 2 derives storage credit from a penetration ratio, interpolating Mills (2020)
between 90% credit at zero penetration and 50% at 15% penetration, then HOLDING at the
15% value beyond that because "Mills' study did not characterize behavior beyond that point."

This project's own storage penetration (storage power / peak demand) is:

    2030   7,000 / 19,511 =  36%
    2035  13,000 / 23,325 =  56%
    2040  18,000 / 27,782 =  65%
    2045  23,000 / 28,466 =  81%

Every checkpoint is far outside the range Mills characterized. Holding at 50% across a fivefold
extrapolation is not a conservative choice; it is an unsupported one, and it happens to produce
roughly PJM's own published figure -- the figure PJM's evaluator says is too high. Algorithm 2 is
therefore not used here. This module measures availability directly instead.

METHOD

1. Compute net demand at each hour after all non-dispatchable clean generation:
       ND[t] = demand[t] - nuclear[t] - exist_solar[t] - wind_gen[t] - solar_gen[t]
   Same definition A.13 Algorithm 1 step 1 uses, so solar/wind and storage credits are
   computed against the same ranking.

2. Rank hours by ND descending; take the top N (default 10, per Algorithm 1 step 2).

3. For each such hour, compute what the storage fleet could ACTUALLY have delivered:
       available[t] = min(power_rating_mw, (soc[t] - dod_floor_mwh) / 1 hour)
   State of charge is the binding term the nameplate approach ignores. A fleet at 10% state of
   charge cannot deliver its power rating no matter how large that rating is.

4. capacity_credit = mean(available) / power_rating_mw

RELATIONSHIP TO THE CROSS-VALIDATION RULE

A.13's cross-validation step directs taking the LOWER of the own-data value and the external
published rating, disclosing the divergence rather than silently choosing the more favorable.
apply_cross_validation() implements that; it does not decide on the caller's behalf which to use
without being asked.

CRITICAL: WHICH DISPATCH YOU MEASURE DETERMINES THE ANSWER (finding, 2026-09-10)

This method must be applied to a NO-FORESIGHT dispatch. Applied to the LP's own solved dispatch
it produces the LEAST conservative possible answer, not the most.

Measured on the same 2045 fleet, same weather, same peak-hour definition:

    LP dispatch (perfect foresight)          100.0%
    Heuristic dispatch (no foresight)         31.8%

The LP series across checkpoints also moves the wrong way as penetration rises:

    2030   penetration  27%   credit  40.3%
    2035   penetration  60%   credit  60.0%
    2040   penetration 127%   credit  70.0%
    2045   penetration 228%   credit 100.0%

Capacity credit should FALL with penetration -- PJM's own fixed-tilt solar rating fell from 33%
to 7-8% for exactly that reason. Rising credit is the signature of the artifact.

The cause is perfect foresight. The LP knows precisely which hours are the peak net-demand hours
and pre-positions storage to be full for them. Measuring "availability at the peak hours" against
a dispatch that was optimized KNOWING which hours those are measures the optimizer's foresight,
not the fleet's capability -- and the larger the fleet, the more completely it can be
pre-positioned, which is why credit rises rather than falls.

Callers must therefore pass state_of_charge_mwh from a no-foresight dispatch (this project's
eight-year heuristic simulation, scripts/sim_2045_8yr.py, or an equivalent rolling-horizon
dispatch). An LP-derived figure may be reported only as an optimistic bound, and only with this
artifact stated.

IMPORTANT LIMITATION

Capacity credit falls as penetration rises -- PJM's own fixed-tilt solar rating fell from 33% to
7-8% for exactly this reason. A credit computed at one checkpoint must NOT be carried forward to
a later one with a larger fleet. compute_from_dispatch() takes one checkpoint's own dispatch and
returns that checkpoint's own credit; callers must recompute per checkpoint.
"""
import numpy as np


DEFAULT_PEAK_HOURS_COUNT = 10
NA_DEPTH_OF_DISCHARGE_FLOOR_FRACTION = 0.20   # lp_model.NA_DOD_FLOOR


def peak_net_demand_hours(demand, nuclear, exist_solar, wind_generation_mw,
                          solar_generation_mw, hours_count=DEFAULT_PEAK_HOURS_COUNT):
    """Indices of the highest net-demand hours, per A.13 Algorithm 1 steps 1-2.

    Net demand is residual load after all non-dispatchable clean generation, which is what
    dispatchable capacity and storage must actually cover.
    """
    if hours_count < 1:
        raise ValueError(f"hours_count must be at least 1, got {hours_count}")
    net_demand = (np.asarray(demand) - np.asarray(nuclear) - np.asarray(exist_solar)
                  - np.asarray(wind_generation_mw) - np.asarray(solar_generation_mw))
    return np.argsort(net_demand)[-hours_count:][::-1]


def compute_from_dispatch(state_of_charge_mwh, power_rating_mw, peak_hour_indices,
                          depth_of_discharge_floor_fraction=0.0, energy_capacity_mwh=None):
    """Capacity credit for one storage class at one checkpoint, from its own dispatch.

    state_of_charge_mwh is the solved hourly SoC array. The credit is the mean, across the peak
    net-demand hours, of what the fleet could have delivered in that hour divided by its power
    rating -- so a fleet that is empty when it matters accredits near zero regardless of how much
    power it nominally has.

    Rule 5: power_rating_mw of zero raises rather than returning a credit, since a credit for a
    fleet that does not exist is meaningless and would silently propagate as 0/0.
    """
    if power_rating_mw is None or power_rating_mw <= 0:
        raise ValueError(
            "power_rating_mw must be positive -- a capacity credit for a fleet with no power "
            "rating has no meaning. If the intent is 'this class was not built', omit it from "
            "the accreditation rather than passing zero.")
    soc = np.asarray(state_of_charge_mwh, dtype=float)
    if energy_capacity_mwh is None:
        energy_capacity_mwh = float(soc.max()) if soc.size else 0.0
    unusable_mwh = depth_of_discharge_floor_fraction * energy_capacity_mwh

    # Deliverable in a one-hour step: limited by power rating AND by energy above the DoD floor.
    usable_energy = np.maximum(0.0, soc[peak_hour_indices] - unusable_mwh)
    deliverable_mw = np.minimum(power_rating_mw, usable_energy)
    return float(np.mean(deliverable_mw) / power_rating_mw)


def apply_cross_validation(own_data_credit, published_credit, resource_label=''):
    """A.13's cross-validation step: take the LOWER of own-data and published, and disclose.

    Returns a dict rather than a bare number so the divergence is carried alongside the adopted
    value and cannot be dropped by accident when reporting.
    """
    adopted = min(own_data_credit, published_credit)
    return {
        'resource': resource_label,
        'own_data_credit': own_data_credit,
        'published_credit': published_credit,
        'adopted_credit': adopted,
        'source_adopted': 'own_data' if own_data_credit <= published_credit else 'published',
        'divergence': published_credit - own_data_credit,
    }


def accredited_capacity_mw(power_rating_mw, capacity_credit):
    """A.13 Algorithm 1 step 5, applied to storage."""
    return power_rating_mw * capacity_credit


def storage_penetration_ratio(total_storage_power_mw, peak_demand_mw):
    """Reported alongside any credit, because credit is only interpretable against penetration --
    and because it is what shows A.13 Algorithm 2's Mills-derived curve is being asked to
    extrapolate far beyond its validated 15% range at every checkpoint in this project.
    """
    if peak_demand_mw <= 0:
        raise ValueError("peak_demand_mw must be positive")
    return total_storage_power_mw / peak_demand_mw
