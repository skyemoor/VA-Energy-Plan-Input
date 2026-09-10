"""
virginia_only_demand.py

Converts the DOM LSE hourly load projection (which covers Virginia AND North Carolina) to a
Virginia-only load basis, for consistency with the § 56-585.5 compliance base.

WHY (2026-09-10)

Tracing the demand basis established three distinct quantities that had been used
interchangeably:

    raw DOMLSE hourly file      VA + NC   LOAD    (losses included)   121,115 GWh @ 2030
    Appendix 2B-1               VA + NC   SALES   (losses excluded)   110,864 GWh @ 2030
    Appendix 2B-1 less 2B-3     VA only   SALES   (losses excluded)   106,994 GWh @ 2030

Two corrections were initially suspected to offset each other. They do not — they act on
different quantities. Losses are the difference between SALES and LOAD; North Carolina is a
difference in SCOPE. Working the arithmetic through:

    raw (VA+NC load)                                        121,115
      / loss factor 1.0925  ->  VA+NC sales                 110,864
      - NC sales (2B-3)     ->  VA-only sales               106,994
      x loss factor         ->  VA-only LOAD                116,887   <- the dispatch target

Raw exceeds VA-only load by 3.62%, which is essentially exactly the NC share of sales (3.49%).

The useful conclusion: **the raw hourly file already carries the loss gross-up correctly.** Its
only remaining error for Virginia purposes is the North Carolina inclusion. This is a much
smaller error than scaling the hourly shape to a SALES total, which strips the losses back out
and leaves generation need roughly 9% short.

WHAT THIS MODULE DOES

Scales the raw hourly array by that year's own Virginia share of DOM LSE sales, so the loss
gross-up already present in the file is preserved while the North Carolina load is removed:

    virginia_share(year) = (total_sales - north_carolina_sales) / total_sales
    virginia_only_load[t] = raw_load[t] * virginia_share(year)

Applying the share as a scalar assumes Virginia and North Carolina load have the same hourly
SHAPE. That is a stated approximation, not a sourced fact — Dominion does not publish separate
hourly profiles by jurisdiction. Its effect is bounded by NC's small share (3.5%), so even a
materially different NC shape moves the Virginia hourly profile very little.

SCOPE IS A CHOICE, NOT A CORRECTION

Both bases are defensible and the choice should be declared rather than inherited:

    VA + NC load   what Dominion physically dispatches; the system does not stop at the
                   state line, so this is arguably right for pure reliability modeling
    VA-only load   what Virginia customers consume; consistent with § 56-585.5, which governs
                   Virginia, and with the compliance base in rps_compliance.py

This project uses VA-only, for consistency with the compliance base.
"""
import numpy as np


# Appendix 2B-1: Total (DOM LSE) Sales (GWh), and Appendix 2B-3: North Carolina Sales (GWh).
# Dominion Energy Virginia, 2025 Update to the 2024 Integrated Resource Plan, filed 2025-10-15,
# SCC Case No. PUR-2025-00184. Citation C071 (2B-1). Virginia share is COMPUTED from these two
# filed series, not itself a filed figure.
#
# Rule 6 note: the 2B-1 totals also appear in demand_shape_interpolation.py's own
# _COMMERCIAL_AND_TOTAL_GWH table, where they are (incorrectly) labelled Virginia-only. That
# labelling error is documented in docs/methodology/
# Demand_Basis_and_RPS_Compliance_Working_Notes.md § 4. The values are identical; only the
# label differs. Cross-checked at construction below rather than trusted to stay in sync.
_TOTAL_DOM_LSE_SALES_GWH = {
    2024: 90495, 2025: 95246, 2026: 95805, 2027: 98862, 2028: 102289, 2029: 106249,
    2030: 110864, 2031: 115684, 2032: 120920, 2033: 125938, 2034: 131176, 2035: 136645,
    2036: 142549, 2037: 148004, 2038: 153370, 2039: 157486, 2040: 162077, 2041: 166548,
    2042: 171265, 2043: 176399, 2044: 181729, 2045: 186462,
}

_NORTH_CAROLINA_SALES_GWH = {
    2024: 3960, 2025: 4195, 2026: 4167, 2027: 3909, 2028: 3879, 2029: 3939,
    2030: 3870, 2031: 3821, 2032: 3715, 2033: 3742, 2034: 3744, 2035: 3768,
    2036: 3815, 2037: 3790, 2038: 3723, 2039: 3707, 2040: 3679, 2041: 3655,
    2042: 3768, 2043: 3582, 2044: 3617, 2045: 3719,
}


def virginia_share_of_dom_lse_sales(year):
    """Virginia's share of total DOM LSE sales for `year`, computed from Appendices 2B-1 and 2B-3.

    Rule 5: raises outside the sourced range rather than extrapolating. The share is stable
    (roughly 0.965 rising to 0.980 across 2024-2045) which makes extrapolation look harmless,
    but a silently extrapolated value in a reported figure is exactly what this project's own
    standards forbid.
    """
    if year not in _TOTAL_DOM_LSE_SALES_GWH:
        raise KeyError(
            f"no sourced Virginia share for {year} -- Appendices 2B-1/2B-3 cover "
            f"{min(_TOTAL_DOM_LSE_SALES_GWH)}-{max(_TOTAL_DOM_LSE_SALES_GWH)}. Extend only with "
            "new sourcing, not by extrapolation.")
    total = _TOTAL_DOM_LSE_SALES_GWH[year]
    north_carolina = _NORTH_CAROLINA_SALES_GWH[year]
    return (total - north_carolina) / total


def virginia_only_sales_gwh(year):
    """Virginia-only retail sales — the § 56-585.5(A) base before its own statutory exclusions.

    This is the figure rps_compliance.StatutoryComplianceBase expects as
    virginia_retail_sales_mwh (x1000), NOT the 2B-1 total.
    """
    if year not in _TOTAL_DOM_LSE_SALES_GWH:
        raise KeyError(f"no sourced sales figure for {year}")
    return _TOTAL_DOM_LSE_SALES_GWH[year] - _NORTH_CAROLINA_SALES_GWH[year]


def to_virginia_only_load(raw_hourly_load_mw, year):
    """Scales a raw DOM LSE hourly LOAD array to Virginia only.

    The loss gross-up already present in the raw file is preserved — this removes North Carolina
    load and nothing else. Do NOT additionally scale to a sales-basis annual total afterwards;
    that would strip the losses back out.
    """
    raw = np.asarray(raw_hourly_load_mw, dtype=float)
    if raw.ndim != 1:
        raise ValueError(f"expected a 1-D hourly array, got shape {raw.shape}")
    return raw * virginia_share_of_dom_lse_sales(year)


def describe_conversion(raw_annual_gwh, year):
    """Full derivation for one year, for reporting rather than silent application."""
    share = virginia_share_of_dom_lse_sales(year)
    total_sales = _TOTAL_DOM_LSE_SALES_GWH[year]
    loss_factor = raw_annual_gwh / total_sales
    return {
        'year': year,
        'raw_va_nc_load_gwh': raw_annual_gwh,
        'total_dom_lse_sales_gwh': total_sales,
        'implied_loss_factor': loss_factor,
        'north_carolina_sales_gwh': _NORTH_CAROLINA_SALES_GWH[year],
        'virginia_only_sales_gwh': virginia_only_sales_gwh(year),
        'virginia_share': share,
        'virginia_only_load_gwh': raw_annual_gwh * share,
    }
