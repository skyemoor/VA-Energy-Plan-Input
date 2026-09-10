"""
scenario2_reserve_margin.py -- BACK-COMPATIBILITY SHIM

Superseded 2026-09-10 by `capacity_accreditation.ReserveMarginRequirement`. Per Rule 1 this
belongs in a class hierarchy: its peak-hour identification duplicated
`storage_accreditation.py`'s under a different name.

Retained only so existing callers do not break. New code should use the class directly.
"""
import assumptions
from capacity_accreditation import PeakHourAnalysis, ReserveMarginRequirement

DEFAULT_INSTALLED_RESERVE_MARGIN = assumptions.INSTALLED_RESERVE_MARGIN


def peak_net_demand_hour(demand, nuclear, exist_solar, wind_cf):
    return PeakHourAnalysis(demand, nuclear, exist_solar, wind_cf=wind_cf).peak_hour()


def _build(demand, nuclear, exist_solar, solar_cf, wind_cf, statutory_solar_mw,
           short_duration_storage_mw, long_duration_storage_mw, bath_county_mw,
           installed_reserve_margin):
    import numpy as np
    if statutory_solar_mw is None:
        raise ValueError(
            "statutory_solar_mw is required. Scenario 2's solar is a fixed statutory input "
            "(SS 56-585.5(D)(2), 16,100 MW by 2035, ramped) -- passing None would silently credit "
            "zero solar at the peak hour and overstate the gas requirement.")
    if short_duration_storage_mw is None or long_duration_storage_mw is None:
        raise ValueError(
            "short_duration_storage_mw and long_duration_storage_mw are both required "
            "(SS 56-585.5(E)(2) and (E)(4)). Rule 5 -- defaulting either to zero would reproduce "
            "Appendix C.2's own zero-storage-credit assumption, which is precisely the "
            "inconsistency this exists to remove.")
    return ReserveMarginRequirement(
        demand, nuclear, exist_solar, wind_cf=wind_cf,
        solar_generation_mw=statutory_solar_mw * np.asarray(solar_cf, dtype=float),
        firm_capacity_mw=short_duration_storage_mw + long_duration_storage_mw + bath_county_mw,
        installed_reserve_margin=installed_reserve_margin)


def required_gas_capacity_mw(demand, nuclear, exist_solar, solar_cf, wind_cf,
                             statutory_solar_mw, short_duration_storage_mw,
                             long_duration_storage_mw, bath_county_mw=0.0,
                             installed_reserve_margin=DEFAULT_INSTALLED_RESERVE_MARGIN):
    return _build(demand, nuclear, exist_solar, solar_cf, wind_cf, statutory_solar_mw,
                  short_duration_storage_mw, long_duration_storage_mw, bath_county_mw,
                  installed_reserve_margin).dispatchable_shortfall_mw()


def compare_capacity_standards(demand, nuclear, exist_solar, solar_cf, wind_cf,
                               statutory_solar_mw, short_duration_storage_mw,
                               long_duration_storage_mw, bath_county_mw=0.0,
                               installed_reserve_margin=DEFAULT_INSTALLED_RESERVE_MARGIN):
    r = _build(demand, nuclear, exist_solar, solar_cf, wind_cf, statutory_solar_mw,
               short_duration_storage_mw, long_duration_storage_mw, bath_county_mw,
               installed_reserve_margin).compare_standards()
    r['storage_power_credited_mw'] = r.pop('firm_capacity_credited_mw')
    return r
