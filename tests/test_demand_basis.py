"""
test_demand_basis.py

Tests for the DemandBasis hierarchy, superseding test_virginia_only_demand.py.

The hierarchy exists because tracing this project's demand inputs found FOUR distinct quantities
used interchangeably -- VA+NC load, VA+NC sales, VA-only sales, VA-only load. A class named for
its basis makes the quantity explicit at the call site; a bare array cannot.
"""
import numpy as np
import pytest

from demand_basis import (HourlyDemandBasis, DomLseLoad, VirginiaOnlyLoad,
                          TOTAL_DOM_LSE_SALES_GWH, NORTH_CAROLINA_SALES_GWH,
                          HOURS_IN_STANDARD_YEAR)


def synthetic_source(years=(2030, 2031)):
    """Flat hourly data over real calendars for the given years.

    Uses pandas date_range rather than hand-built day loops -- the first version of this helper
    generated invalid calendars and claimed to contain a leap day when it did not, which made the
    leap-exclusion test pass vacuously. Generating real dates removes that whole class of error.
    """
    import pandas as pd
    rows = []
    for year in years:
        for d in pd.date_range(f'{year}-01-01', f'{year}-12-31', freq='D'):
            rows.append({'Year': d.year, 'Month': d.month, 'Day': d.day,
                         **{str(h): 1000.0 for h in range(1, 25)}})
    return pd.DataFrame(rows)


class TestSourcedSeriesMatchTheFiling:
    def test_2b1_key_years(self):
        assert TOTAL_DOM_LSE_SALES_GWH[2030] == 110864
        assert TOTAL_DOM_LSE_SALES_GWH[2045] == 186462

    def test_2b3_key_years(self):
        assert NORTH_CAROLINA_SALES_GWH[2030] == 3870
        assert NORTH_CAROLINA_SALES_GWH[2045] == 3719

    def test_cross_check_against_demand_shape_interpolation(self):
        """Rule 6.2: the 2B-1 totals also live in demand_shape_interpolation.py (mislabelled there
        as Virginia-only). Assert they agree so the two copies cannot silently diverge."""
        import demand_shape_interpolation as dsi
        for year in (2030, 2035, 2040, 2045):
            assert dsi._COMMERCIAL_AND_TOTAL_GWH[year][1] == TOTAL_DOM_LSE_SALES_GWH[year]


class TestFiscalYearConstructionSharedBase:
    """Tested once on the base rather than in each subclass."""

    def test_produces_exactly_8760_hours(self):
        assert len(DomLseLoad(2030, synthetic_source()).fiscal_year_hours()) == HOURS_IN_STANDARD_YEAR

    def test_leap_day_excluded_by_calendar_date_not_hour_offset(self):
        """A fixed hour offset silently breaks on leap years. Fiscal year 2039 spans April 2039
        through March 2040, so it CONTAINS February 29 2040 -- which must be dropped, or every
        subsequent hour misaligns against the 8,760-hour weather arrays.
        """
        df = synthetic_source(years=(2039, 2040))
        leap_days = df[(df.Month == 2) & (df.Day == 29)]
        assert len(leap_days) == 1, "fixture must contain exactly one leap day (2040-02-29)"
        assert leap_days.iloc[0]['Year'] == 2040
        assert len(DomLseLoad(2039, df).fiscal_year_hours()) == HOURS_IN_STANDARD_YEAR

    def test_a_year_without_a_leap_day_also_produces_8760(self):
        df = synthetic_source(years=(2030, 2031))
        assert not ((df.Month == 2) & (df.Day == 29)).any()
        assert len(DomLseLoad(2030, df).fiscal_year_hours()) == HOURS_IN_STANDARD_YEAR

    def test_base_class_refuses_to_state_a_basis(self):
        """Rule 5: the base cannot answer 'which quantity is this', so it must not pretend to."""
        with pytest.raises(NotImplementedError):
            HourlyDemandBasis(2030).hourly_mw()
        with pytest.raises(NotImplementedError):
            HourlyDemandBasis(2030).basis_description()


class TestBasisIsNamedAndDistinct:
    """The point of the hierarchy: each class states which of the four quantities it produces."""

    def test_dom_lse_load_names_its_scope_and_losses(self):
        d = DomLseLoad(2030, synthetic_source()).basis_description()
        assert 'North Carolina' in d and 'losses included' in d

    def test_virginia_only_load_names_its_scope_and_losses(self):
        d = VirginiaOnlyLoad(2030, synthetic_source()).basis_description()
        assert 'Virginia-only' in d and 'losses included' in d

    def test_virginia_only_is_smaller_than_combined(self):
        df = synthetic_source()
        assert (VirginiaOnlyLoad(2030, df).hourly_mw().sum()
                < DomLseLoad(2030, df).hourly_mw().sum())


class TestVirginiaShare:
    def test_2030_share_matches_worked_derivation(self):
        assert VirginiaOnlyLoad(2030).virginia_share() == pytest.approx((110864 - 3870) / 110864)
        assert VirginiaOnlyLoad(2030).virginia_share() == pytest.approx(0.9651, abs=0.0002)

    def test_virginia_only_sales_2030(self):
        assert VirginiaOnlyLoad(2030).virginia_only_sales_gwh() == 106994

    def test_share_rises_as_nc_shrinks_relatively(self):
        assert VirginiaOnlyLoad(2045).virginia_share() > VirginiaOnlyLoad(2030).virginia_share()

    def test_unsourced_year_raises_rather_than_extrapolating(self):
        with pytest.raises(KeyError, match='no sourced Virginia share'):
            VirginiaOnlyLoad(2050).virginia_share()


class TestLossGrossUpPreserved:
    """The key property: scaling removes North Carolina and NOTHING ELSE. Scaling to a SALES total
    instead strips the losses back out and understates generation need by roughly 9%."""

    def test_derivation_reports_the_full_chain(self):
        v = VirginiaOnlyLoad(2030, synthetic_source())
        d = v.derivation()
        assert d['virginia_only_load_gwh'] == pytest.approx(
            d['raw_va_nc_load_gwh'] * d['virginia_share'])
        assert d['virginia_only_sales_gwh'] == 106994

    def test_raw_exceeds_virginia_only_load_by_the_nc_share(self):
        """Losses and NC do NOT offset: raw is above VA-only load by ~3.6%, essentially exactly
        NC's 3.5% share of sales."""
        share = VirginiaOnlyLoad(2030).virginia_share()
        nc_share = NORTH_CAROLINA_SALES_GWH[2030] / TOTAL_DOM_LSE_SALES_GWH[2030]
        assert (1 / share - 1) == pytest.approx(nc_share, abs=0.002)
