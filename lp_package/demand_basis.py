"""
demand_basis.py

Class hierarchy for constructing an hourly demand series on a stated basis.

WHY A HIERARCHY (2026-09-10, Software Engineering Standards Rule 1)

Third of three hierarchies replacing free-standing functions. This absorbs
`virginia_only_demand.py` and the fiscal-year construction that was written inline inside
`run_all.py`'s demand stage -- logic that belongs in the package, not in a pipeline script (Rule
1.3: free-standing scripts are for orchestration, not for logic called more than once).

WHY "BASIS" IS THE ORGANIZING CONCEPT

Tracing this project's demand inputs found THREE distinct quantities that had been used
interchangeably, and the confusion cost real time:

    raw DOMLSE hourly file      VA + NC   LOAD    (losses included)   122,164 GWh @ 2030
    Appendix 2B-1               VA + NC   SALES   (losses excluded)   110,864 GWh @ 2030
    2B-1 less 2B-3              VA only   SALES   (losses excluded)   106,994 GWh @ 2030
    the dispatch target         VA only   LOAD    (losses included)   117,900 GWh @ 2030

Two corrections were initially assumed to offset each other. They do not, because they act on
different quantities: losses separate SALES from LOAD, North Carolina is a difference in SCOPE.
Raw exceeds Virginia-only load by 3.6%, which is essentially exactly North Carolina's 3.5% share
of sales.

The useful conclusion is favourable: the raw hourly file already carries the loss gross-up
correctly, so its only remaining error for Virginia purposes is the North Carolina inclusion.
Scaling that hourly shape to a SALES total instead -- which an earlier approach did -- strips the
losses back out and leaves generation need roughly 9% short.

A class named for its basis makes the quantity explicit at the call site. `VirginiaOnlyLoad`
cannot be mistaken for sales; a bare array can.

SCOPE IS A CHOICE, NOT A CORRECTION

VA+NC load is what Dominion physically dispatches and is defensible for pure reliability
modelling. VA-only load is what Virginia customers consume, and is consistent with § 56-585.5,
which governs Virginia, and with the compliance base in rps_compliance.py. This project uses
VA-only and states it.

THE HIERARCHY

    HourlyDemandBasis        fiscal-year construction, leap handling, column validation
      DomLseLoad             raw VA+NC load as filed
        VirginiaOnlyLoad     scaled to Virginia's own share of DOM LSE sales
"""
import numpy as np

import paths


# Appendix 2B-1: Total (DOM LSE) Sales (GWh), and Appendix 2B-3: North Carolina Sales (GWh).
# Dominion Energy Virginia, 2025 Update to the 2024 Integrated Resource Plan, filed 2025-10-15,
# SCC Case No. PUR-2025-00184. Citation C071 (2B-1). The Virginia share is COMPUTED from these two
# filed series; it is not itself a filed figure.
TOTAL_DOM_LSE_SALES_GWH = {
    2024: 90495, 2025: 95246, 2026: 95805, 2027: 98862, 2028: 102289, 2029: 106249,
    2030: 110864, 2031: 115684, 2032: 120920, 2033: 125938, 2034: 131176, 2035: 136645,
    2036: 142549, 2037: 148004, 2038: 153370, 2039: 157486, 2040: 162077, 2041: 166548,
    2042: 171265, 2043: 176399, 2044: 181729, 2045: 186462,
}
NORTH_CAROLINA_SALES_GWH = {
    2024: 3960, 2025: 4195, 2026: 4167, 2027: 3909, 2028: 3879, 2029: 3939,
    2030: 3870, 2031: 3821, 2032: 3715, 2033: 3742, 2034: 3744, 2035: 3768,
    2036: 3815, 2037: 3790, 2038: 3723, 2039: 3707, 2040: 3679, 2041: 3655,
    2042: 3768, 2043: 3582, 2044: 3617, 2045: 3719,
}

HOURS_IN_STANDARD_YEAR = 8760


class HourlyDemandBasis:
    """Builds an 8,760-hour series for a fiscal year running April through March.

    Leap days are excluded explicitly by CALENDAR DATE rather than by hour offset. A fixed offset
    silently breaks on leap years -- 2040 has 8,784 hours, and an offset-based approach produced a
    shape mismatch against the 8,760-hour weather arrays before this was caught.
    """

    SOURCE_FILENAME = 'DOMLSEHourlyLoadProjections2024through2048.csv'
    HOUR_COLUMNS = [str(h) for h in range(1, 25)]

    def __init__(self, year, dataframe=None):
        self.year = year
        self._dataframe = dataframe

    def dataframe(self):
        """Loads the source file once, validating its columns.

        Filename aliasing resolves WHERE a file is, not WHAT is in it -- a differently-named
        variant of this dataset can carry a different layout (the `_formatted` variant uses
        DateTime/MWh). Checked here rather than failing deep in the reshape.
        """
        if self._dataframe is None:
            import pandas as pd
            src = paths.source_file(self.SOURCE_FILENAME)
            self._dataframe = pd.read_csv(src)
            import os
            paths.require_columns(self._dataframe, ['Year', 'Month', 'Day'] + self.HOUR_COLUMNS,
                                  os.path.basename(src))
        return self._dataframe

    def fiscal_year_hours(self):
        """April of `year` through March of `year + 1`, February 29 excluded, exactly 8,760 hours."""
        df = self.dataframe()
        first = df[(df.Year == self.year) & (df.Month >= 4)].sort_values(['Month', 'Day'])
        second = df[(df.Year == self.year + 1) & (df.Month <= 3)].sort_values(['Month', 'Day'])
        first = first[~((first.Month == 2) & (first.Day == 29))]
        second = second[~((second.Month == 2) & (second.Day == 29))]
        out = np.concatenate([first[self.HOUR_COLUMNS].values.astype(float).flatten(),
                              second[self.HOUR_COLUMNS].values.astype(float).flatten()])
        if len(out) != HOURS_IN_STANDARD_YEAR:
            raise ValueError(
                f"{self.year} fiscal year produced {len(out)} hours, expected "
                f"{HOURS_IN_STANDARD_YEAR}. A leap day may not have been excluded, which would "
                f"misalign every subsequent hour against the weather arrays.")
        return out

    def hourly_mw(self):
        raise NotImplementedError("subclass must state which basis it produces")

    def basis_description(self):
        raise NotImplementedError("subclass must state which basis it produces")


class DomLseLoad(HourlyDemandBasis):
    """Raw DOM LSE hourly LOAD, Virginia and North Carolina combined, losses included as filed."""

    def hourly_mw(self):
        return self.fiscal_year_hours()

    def basis_description(self):
        return 'DOM LSE (Virginia + North Carolina) hourly load, transmission losses included'


class VirginiaOnlyLoad(DomLseLoad):
    """Virginia-only hourly LOAD: the raw series scaled by Virginia's share of DOM LSE sales.

    This removes North Carolina load and NOTHING ELSE -- the loss gross-up already present in the
    raw file is preserved. Do not additionally scale the result to a sales-basis annual total;
    that strips the losses back out and understates generation need by roughly 9%.

    STATED APPROXIMATION: applying the share as a scalar assumes Virginia and North Carolina load
    have the same hourly SHAPE. Dominion does not publish separate hourly profiles by
    jurisdiction. The effect is bounded by NC's small share (3.5%), so even a materially different
    NC shape moves the Virginia profile very little.
    """

    def virginia_share(self):
        if self.year not in TOTAL_DOM_LSE_SALES_GWH:
            raise KeyError(
                f"no sourced Virginia share for {self.year} -- Appendices 2B-1/2B-3 cover "
                f"{min(TOTAL_DOM_LSE_SALES_GWH)}-{max(TOTAL_DOM_LSE_SALES_GWH)}. Extend only with "
                "new sourcing, not by extrapolation.")
        total = TOTAL_DOM_LSE_SALES_GWH[self.year]
        return (total - NORTH_CAROLINA_SALES_GWH[self.year]) / total

    def virginia_only_sales_gwh(self):
        """Virginia retail sales -- the § 56-585.5(A) base BEFORE its statutory exclusions.

        This is what rps_compliance.StatutoryComplianceBase expects (x1000), NOT the 2B-1 total.
        """
        if self.year not in TOTAL_DOM_LSE_SALES_GWH:
            raise KeyError(f"no sourced sales figure for {self.year}")
        return TOTAL_DOM_LSE_SALES_GWH[self.year] - NORTH_CAROLINA_SALES_GWH[self.year]

    def hourly_mw(self):
        return super().hourly_mw() * self.virginia_share()

    def basis_description(self):
        return 'Virginia-only hourly load, transmission losses included, North Carolina removed'

    def derivation(self):
        """Full derivation for reporting, so the conversion is visible rather than silent."""
        raw = super().hourly_mw()
        raw_gwh = float(raw.sum()) / 1000.0
        total_sales = TOTAL_DOM_LSE_SALES_GWH[self.year]
        return {
            'year': self.year,
            'raw_va_nc_load_gwh': raw_gwh,
            'total_dom_lse_sales_gwh': total_sales,
            'implied_loss_factor': raw_gwh / total_sales,
            'north_carolina_sales_gwh': NORTH_CAROLINA_SALES_GWH[self.year],
            'virginia_only_sales_gwh': self.virginia_only_sales_gwh(),
            'virginia_share': self.virginia_share(),
            'virginia_only_load_gwh': raw_gwh * self.virginia_share(),
            'basis': self.basis_description(),
        }
