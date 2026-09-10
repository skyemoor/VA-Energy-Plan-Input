"""
storage_accreditation.py -- BACK-COMPATIBILITY SHIM

Superseded 2026-09-10 by `capacity_accreditation.StorageCapacityCredit`. Per Software Engineering
Standards Rule 1, this logic belongs in a class hierarchy: it shared its peak-hour identification
with `scenario2_reserve_margin.py`, which defined the same thing under a different name.

Retained only so existing callers do not break. New code should use the class directly, which also
REQUIRES stating whether the dispatch has foresight -- a question this function-level interface
allowed callers to skip, and which changes the answer threefold.
"""
import numpy as np

import assumptions
from capacity_accreditation import PeakHourAnalysis, StorageCapacityCredit

DEFAULT_PEAK_HOURS_COUNT = assumptions.CAPACITY_CREDIT_PEAK_HOURS_COUNT
NA_DEPTH_OF_DISCHARGE_FLOOR_FRACTION = assumptions.NA_DOD_FLOOR


def peak_net_demand_hours(demand, nuclear, exist_solar, wind_generation_mw,
                          solar_generation_mw, hours_count=DEFAULT_PEAK_HOURS_COUNT):
    return PeakHourAnalysis(demand, nuclear, exist_solar,
                            wind_generation_mw=wind_generation_mw,
                            solar_generation_mw=solar_generation_mw).peak_hours(hours_count)


def compute_from_dispatch(state_of_charge_mwh, power_rating_mw, peak_hour_indices,
                          depth_of_discharge_floor_fraction=0.0, energy_capacity_mwh=None):
    """Preserves the original signature, which takes pre-computed peak indices."""
    if power_rating_mw is None or power_rating_mw <= 0:
        raise ValueError(
            "power_rating_mw must be positive -- a capacity credit for a fleet with no power "
            "rating has no meaning. If the intent is 'this class was not built', omit it from "
            "the accreditation rather than passing zero.")
    soc = np.asarray(state_of_charge_mwh, dtype=float)
    capacity = energy_capacity_mwh if energy_capacity_mwh is not None else float(soc.max())
    usable = np.maximum(0.0, soc[peak_hour_indices]
                        - depth_of_discharge_floor_fraction * capacity)
    return float(np.mean(np.minimum(power_rating_mw, usable)) / power_rating_mw)


def apply_cross_validation(own_data_credit, published_credit, resource_label=''):
    return {
        'resource': resource_label,
        'own_data_credit': own_data_credit,
        'published_credit': published_credit,
        'adopted_credit': min(own_data_credit, published_credit),
        'source_adopted': 'own_data' if own_data_credit <= published_credit else 'published',
        'divergence': published_credit - own_data_credit,
    }


def accredited_capacity_mw(power_rating_mw, capacity_credit):
    return power_rating_mw * capacity_credit


def storage_penetration_ratio(total_storage_power_mw, peak_demand_mw):
    if peak_demand_mw <= 0:
        raise ValueError("peak_demand_mw must be positive")
    return total_storage_power_mw / peak_demand_mw
