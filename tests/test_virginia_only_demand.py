"""
test_virginia_only_demand.py

Per Software Engineering Standards Rule 2. Baselines are the filed Appendix 2B-1/2B-3 values
and the derivation worked through in
docs/methodology/Demand_Basis_and_RPS_Compliance_Working_Notes.md § 4.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lp_package'))

import numpy as np
import pytest
from virginia_only_demand import (virginia_share_of_dom_lse_sales, virginia_only_sales_gwh,
                                   to_virginia_only_load, describe_conversion,
                                   _TOTAL_DOM_LSE_SALES_GWH, _NORTH_CAROLINA_SALES_GWH)


class TestSourcedSeriesMatchTheFiling:
    """Locks the tables to the printed Appendix values."""

    def test_2b1_key_years(self):
        assert _TOTAL_DOM_LSE_SALES_GWH[2030] == 110864
        assert _TOTAL_DOM_LSE_SALES_GWH[2035] == 136645
        assert _TOTAL_DOM_LSE_SALES_GWH[2040] == 162077
        assert _TOTAL_DOM_LSE_SALES_GWH[2045] == 186462

    def test_2b3_key_years(self):
        assert _NORTH_CAROLINA_SALES_GWH[2030] == 3870
        assert _NORTH_CAROLINA_SALES_GWH[2045] == 3719

    def test_cross_check_against_demand_shape_interpolation(self):
        """Rule 6.2: the 2B-1 totals also live in demand_shape_interpolation.py (mislabelled there
        as Virginia-only). Assert they agree, so the two copies cannot silently diverge."""
        import demand_shape_interpolation as dsi
        for year in (2030, 2035, 2040, 2045):
            assert dsi._COMMERCIAL_AND_TOTAL_GWH[year][1] == _TOTAL_DOM_LSE_SALES_GWH[year]


class TestVirginiaShare:

    def test_2030_share_matches_worked_derivation(self):
        assert virginia_share_of_dom_lse_sales(2030) == pytest.approx((110864 - 3870) / 110864)
        assert virginia_share_of_dom_lse_sales(2030) == pytest.approx(0.9651, abs=0.0002)

    def test_virginia_only_sales_2030(self):
        assert virginia_only_sales_gwh(2030) == 106994

    def test_share_rises_as_nc_shrinks_relatively(self):
        """NC sales are roughly flat while Virginia grows, so Virginia's share rises."""
        assert virginia_share_of_dom_lse_sales(2045) > virginia_share_of_dom_lse_sales(2030)
        assert virginia_share_of_dom_lse_sales(2045) == pytest.approx(0.980, abs=0.001)

    def test_unsourced_year_raises_rather_than_extrapolating(self):
        with pytest.raises(KeyError, match='no sourced Virginia share'):
            virginia_share_of_dom_lse_sales(2050)


class TestHourlyConversionPreservesLosses:
    """The key property: this removes North Carolina and nothing else. The loss gross-up already
    in the raw file must survive, because scaling to a sales-basis total instead would strip it
    and leave generation need roughly 9% short."""

    def test_scales_by_the_share(self):
        raw = np.full(8760, 10_000.0)
        out = to_virginia_only_load(raw, 2030)
        assert out[0] == pytest.approx(10_000.0 * virginia_share_of_dom_lse_sales(2030))

    def test_annual_total_lands_above_virginia_sales_by_the_loss_factor(self):
        """VA-only LOAD must exceed VA-only SALES, by roughly the 9.25% loss factor."""
        raw_annual_gwh = 121_115.0
        raw = np.full(8760, raw_annual_gwh * 1000 / 8760)
        out = to_virginia_only_load(raw, 2030)
        out_annual_gwh = out.sum() / 1000
        assert out_annual_gwh == pytest.approx(116_887, rel=0.001)
        assert out_annual_gwh > virginia_only_sales_gwh(2030)
        assert out_annual_gwh / virginia_only_sales_gwh(2030) == pytest.approx(1.0925, abs=0.001)

    def test_raw_exceeds_virginia_only_load_by_the_nc_share(self):
        """The finding that losses and NC do NOT offset: raw is above VA-only load by 3.6%,
        essentially exactly NC's 3.5% share of sales."""
        conv = describe_conversion(121_115.0, 2030)
        overstatement = conv['raw_va_nc_load_gwh'] / conv['virginia_only_load_gwh'] - 1
        nc_share = _NORTH_CAROLINA_SALES_GWH[2030] / _TOTAL_DOM_LSE_SALES_GWH[2030]
        assert overstatement == pytest.approx(nc_share, abs=0.002)
        assert overstatement == pytest.approx(0.0362, abs=0.001)

    def test_two_dimensional_input_raises(self):
        with pytest.raises(ValueError, match='1-D hourly array'):
            to_virginia_only_load(np.zeros((10, 10)), 2030)


class TestDescribeConversion:

    def test_reports_the_full_derivation(self):
        conv = describe_conversion(121_115.0, 2030)
        assert conv['implied_loss_factor'] == pytest.approx(1.0925, abs=0.001)
        assert conv['virginia_only_sales_gwh'] == 106994
        assert conv['virginia_only_load_gwh'] == pytest.approx(116_887, rel=0.001)
