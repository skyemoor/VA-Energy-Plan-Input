"""
scenario2_reserve_margin.py

Applies the SAME reserve-margin standard to the Statutory Floor scenario (code: S2) that
Scenario 1 (Build to Zero) and Scenario 3 (Distributed Build) already use, so that the
scenarios' capacity requirements are comparable.

WHY THIS EXISTS (2026-09-10)

Scenario 2 was never wrong on its own terms, but it was not comparable to the others.
Investigating the class hierarchy found:

  Scenario1Solver -> composed with ReserveMarginMixin as Scenario1WithReserveMargin
  Scenario3Solver -> composed with ReserveMarginMixin as Scenario3WithReserveMargin
  Scenario2Solver -> CheckpointSolver + SocialCostRGGIMixin only. No composition exists.

and build_scenario2_problem() contains no reserve, IRM, or margin logic at all (verified by
direct search, not assumed from the class definition).

But Scenario 2 is not simply missing a capacity standard. Appendix C.2 states it sizes gas
"directly to cover each checkpoint's worst single hourly gap, crediting storage with zero
contribution." So the two scenarios are conservative in OPPOSITE directions:

  Scenario 1: capacity >= (1 + IRM) x demand at peak, storage CREDITED at power rating
  Scenario 2: gas capacity = worst hourly gap, storage credited at ZERO, no margin

Neither is indefensible. They are simply not the same standard, and a cost comparison between
them therefore compares two different reliability requirements as though they were one. That is
the defect this module corrects -- not "Scenario 2 is under-built," which would have been the
wrong diagnosis.

WHAT THIS DOES

Computes the gas capacity Scenario 2 requires under Scenario 1's own reserve-margin standard,
crediting resources exactly as driver.add_reserve_margin_constraint() does at the peak
net-demand hour:

    required_gas_mw = (1 + IRM) x demand[t_peak]
                      - nuclear[t_peak]
                      - CVOW_MW x wind_cf[t_peak]
                      - solar_mw x solar_cf[t_peak]
                      - storage power ratings

Reporting both this figure and Appendix C.2's own zero-storage-credit figure makes the
difference between the two standards visible rather than buried in a cost delta.

WHAT THIS DELIBERATELY DOES NOT DO

It does not add a constraint row to build_scenario2_problem(). In Scenario 2 solar and storage
are fixed statutory inputs, not decision variables (Appendix C.1) -- the only free capacity
quantity is gas, and gas capacity is derived after the solve from the dispatch peak rather than
chosen by the LP. A constraint row would have nothing to act on. The correct intervention point
is the capacity calculation, which is here.
"""
import numpy as np
import lp_model as lp


DEFAULT_INSTALLED_RESERVE_MARGIN = 0.177


def peak_net_demand_hour(demand, nuclear, exist_solar, wind_cf):
    """Same definition ReserveMarginMixin.find_peak_net_demand_hour() uses, so that Scenario 2's
    peak hour is identified identically to Scenario 1's rather than by a parallel rule."""
    net_demand = demand - nuclear - exist_solar - lp.CVOW_MW * wind_cf
    return int(np.argmax(net_demand))


def required_gas_capacity_mw(demand, nuclear, exist_solar, solar_cf, wind_cf,
                             statutory_solar_mw, short_duration_storage_mw,
                             long_duration_storage_mw, bath_county_mw=0.0,
                             installed_reserve_margin=DEFAULT_INSTALLED_RESERVE_MARGIN):
    """Gas capacity Scenario 2 needs under Scenario 1's reserve-margin standard.

    Storage is credited at its full power rating, matching driver.add_reserve_margin_constraint()
    and this project's own adopted capacity-credit methodology (Appendix A.13.1), NOT at the zero
    credit Appendix C.2 uses. That difference is the point of this function: it is what makes the
    scenarios comparable.

    Floored at zero -- a fleet that already satisfies the margin without gas needs no gas, and a
    negative requirement has no physical meaning (Rule 11).
    """
    if statutory_solar_mw is None:
        raise ValueError(
            "statutory_solar_mw is required. Scenario 2's solar is a fixed statutory input "
            "(§ 56-585.5(D)(2), 16,100 MW by 2035, ramped) -- passing None would silently credit "
            "zero solar at the peak hour and overstate the gas requirement.")
    if short_duration_storage_mw is None or long_duration_storage_mw is None:
        raise ValueError(
            "short_duration_storage_mw and long_duration_storage_mw are both required "
            "(§ 56-585.5(E)(2) and (E)(4)). Rule 5 -- defaulting either to zero would reproduce "
            "Appendix C.2's own zero-storage-credit assumption, which is precisely the "
            "inconsistency this function exists to remove.")

    t_peak = peak_net_demand_hour(demand, nuclear, exist_solar, wind_cf)
    required_capacity = (1.0 + installed_reserve_margin) * demand[t_peak]
    credited = (nuclear[t_peak]
                + lp.CVOW_MW * wind_cf[t_peak]
                + exist_solar[t_peak]
                + statutory_solar_mw * solar_cf[t_peak]
                + short_duration_storage_mw
                + long_duration_storage_mw
                + bath_county_mw)
    return max(0.0, required_capacity - credited)


def compare_capacity_standards(demand, nuclear, exist_solar, solar_cf, wind_cf,
                               statutory_solar_mw, short_duration_storage_mw,
                               long_duration_storage_mw, bath_county_mw=0.0,
                               installed_reserve_margin=DEFAULT_INSTALLED_RESERVE_MARGIN):
    """Reports Scenario 2's gas requirement under both standards side by side.

    This is the intended entry point. Reporting only the reserve-margin figure would hide that
    Scenario 2's original rule was conservative in a different direction; reporting only the
    original figure leaves the scenarios incomparable.
    """
    t_peak = peak_net_demand_hour(demand, nuclear, exist_solar, wind_cf)

    clean_at_peak = (nuclear[t_peak] + lp.CVOW_MW * wind_cf[t_peak] + exist_solar[t_peak]
                     + statutory_solar_mw * solar_cf[t_peak])
    # Appendix C.2's own rule: worst single hourly gap, storage credited at zero.
    appendix_c2_gas_mw = max(0.0, demand[t_peak] - clean_at_peak)

    reserve_margin_gas_mw = required_gas_capacity_mw(
        demand, nuclear, exist_solar, solar_cf, wind_cf, statutory_solar_mw,
        short_duration_storage_mw, long_duration_storage_mw, bath_county_mw,
        installed_reserve_margin)

    return {
        'peak_net_demand_hour': t_peak,
        'demand_at_peak_mw': float(demand[t_peak]),
        'clean_generation_at_peak_mw': float(clean_at_peak),
        'storage_power_credited_mw': float(short_duration_storage_mw + long_duration_storage_mw
                                            + bath_county_mw),
        'appendix_c2_gas_mw_zero_storage_credit_no_margin': float(appendix_c2_gas_mw),
        'reserve_margin_gas_mw_storage_credited': float(reserve_margin_gas_mw),
        'difference_mw': float(reserve_margin_gas_mw - appendix_c2_gas_mw),
        'installed_reserve_margin': installed_reserve_margin,
    }
