"""
virginia_only_demand.py -- BACK-COMPATIBILITY SHIM

Superseded 2026-09-10 by `demand_basis.VirginiaOnlyLoad`. Per Rule 1 this belongs in a class
hierarchy: it shared fiscal-year construction, leap handling and column validation with logic that
had been written inline inside run_all.py's demand stage.

Retained only so existing callers do not break. New code should use the class, whose NAME states
which of the four distinct demand quantities it produces -- a bare array cannot.

The sourced Appendix 2B-1/2B-3 series and the full derivation note now live in demand_basis.py.
"""
import numpy as np

from demand_basis import (TOTAL_DOM_LSE_SALES_GWH, NORTH_CAROLINA_SALES_GWH, VirginiaOnlyLoad)

_TOTAL_DOM_LSE_SALES_GWH = TOTAL_DOM_LSE_SALES_GWH
_NORTH_CAROLINA_SALES_GWH = NORTH_CAROLINA_SALES_GWH


def virginia_share_of_dom_lse_sales(year):
    return VirginiaOnlyLoad(year).virginia_share()


def virginia_only_sales_gwh(year):
    return VirginiaOnlyLoad(year).virginia_only_sales_gwh()


def to_virginia_only_load(raw_hourly_load_mw, year):
    """Scales an ALREADY-LOADED raw array. The class loads the source file itself; this signature
    is preserved for callers that have the array in hand."""
    raw = np.asarray(raw_hourly_load_mw, dtype=float)
    if raw.ndim != 1:
        raise ValueError(f"expected a 1-D hourly array, got shape {raw.shape}")
    return raw * VirginiaOnlyLoad(year).virginia_share()


def describe_conversion(raw_annual_gwh, year):
    v = VirginiaOnlyLoad(year)
    share = v.virginia_share()
    total_sales = TOTAL_DOM_LSE_SALES_GWH[year]
    return {
        'year': year,
        'raw_va_nc_load_gwh': raw_annual_gwh,
        'total_dom_lse_sales_gwh': total_sales,
        'implied_loss_factor': raw_annual_gwh / total_sales,
        'north_carolina_sales_gwh': NORTH_CAROLINA_SALES_GWH[year],
        'virginia_only_sales_gwh': v.virginia_only_sales_gwh(),
        'virginia_share': share,
        'virginia_only_load_gwh': raw_annual_gwh * share,
    }
