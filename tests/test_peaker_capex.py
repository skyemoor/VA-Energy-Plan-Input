"""Baseline-locked tests for peaker_capex.py, per Rule 2. Baselines are the sourced figures
documented in the module docstring (GridLab September 2025, EIA, USP&E April 2026)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lp_package'))
import pytest
from peaker_capex import (size_tier, peaker_capex_kw, peaker_project_cost_dollars,
                          PEAKER_CAPEX_KW_BY_TIER, DUAL_FUEL_ADDER_KW,
                          FAST_TRACK_PREMIUM_FRACTION, SMALL_TIER_MAX_MW, MEDIUM_TIER_MAX_MW)


class TestSizeTiers:
    def test_boundaries_match_sourced_tiering(self):
        assert SMALL_TIER_MAX_MW == 50.0      # USP&E 25-50 MW tier
        assert MEDIUM_TIER_MAX_MW == 250.0    # USP&E 250+ MW tier
    def test_tier_assignment(self):
        assert size_tier(30) == 'small'
        assert size_tier(50) == 'small'
        assert size_tier(105) == 'medium'     # aeroderivative
        assert size_tier(237) == 'medium'     # F-Class
        assert size_tier(418) == 'large'      # H-Class
    def test_nonpositive_raises(self):
        with pytest.raises(ValueError, match='must be positive'):
            size_tier(0)


class TestSizeCostInversionPreserved:
    """Smaller units cost MORE per kW. Independently confirmed by Gas Turbine World's own older
    figures (105 MW aeroderivative $1,175/kW vs 237 MW F-Class $713/kW) and by USP&E's tiers.
    Locking it because it inverts the usual intuition and a future edit might 'correct' it."""
    def test_small_costs_more_per_kw_than_large(self):
        assert peaker_capex_kw(30) > peaker_capex_kw(105) > peaker_capex_kw(418)
    def test_inversion_holds_in_every_case(self):
        for case in ('low', 'central', 'high'):
            assert peaker_capex_kw(30, case) > peaker_capex_kw(418, case)


class TestSourcedLevels:
    def test_medium_low_anchors_on_gridlab_reported_range(self):
        """GridLab Sept 2025: CT projects completing 2026-2027 reported at $1,116-$1,427/kW."""
        assert PEAKER_CAPEX_KW_BY_TIER['medium']['low'] == 1116.0
        assert PEAKER_CAPEX_KW_BY_TIER['medium']['central'] == pytest.approx(1425.0)
    def test_all_tiers_exceed_the_2023_eia_baseline(self):
        """EIA: CT placed in service 2023 averaged $562/kW. Every current figure must exceed it."""
        for tier in PEAKER_CAPEX_KW_BY_TIER.values():
            assert tier['low'] > 562.0
    def test_peaker_central_is_below_ccgt(self):
        """Simple-cycle should cost less per kW installed than CCGT's $3,000/kW."""
        import lp_model
        assert peaker_capex_kw(237) < lp_model.ccgt_capex_kw(2030)


class TestAddersAndCases:
    def test_dual_fuel_adder(self):
        assert peaker_capex_kw(237, dual_fuel=True) - peaker_capex_kw(237) == pytest.approx(DUAL_FUEL_ADDER_KW)
    def test_fast_track_premium(self):
        assert peaker_capex_kw(237, fast_track=True) == pytest.approx(
            peaker_capex_kw(237) * (1 + FAST_TRACK_PREMIUM_FRACTION))
    def test_unknown_case_raises_rather_than_defaulting(self):
        with pytest.raises(ValueError, match="must be 'low', 'central' or 'high'"):
            peaker_capex_kw(237, case='expected')


class TestProjectCost:
    def test_reports_tier_and_rate_alongside_total(self):
        r = peaker_project_cost_dollars(2503.0, 237.0)
        assert r['size_tier'] == 'medium'
        assert r['whole_units_required'] == pytest.approx(2503.0 / 237.0)
        assert r['total_cost_dollars'] == pytest.approx(2503.0 * 1000 * r['capex_per_kw'])
    def test_does_not_silently_round_units(self):
        """Rounding is a procurement decision for the caller; silently rounding would move cost
        without the caller knowing which direction."""
        r = peaker_project_cost_dollars(2503.0, 237.0)
        assert r['whole_units_required'] != int(r['whole_units_required'])
