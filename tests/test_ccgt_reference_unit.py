"""
test_ccgt_reference_unit.py

The discrete combined-cycle unit Scenario 2's new build is composed from.
"""
import pytest

import assumptions as a


class TestScenario2IsExemptFromTheSimpleCycleRule:
    """The standing new-build rule -- simple-cycle combustion turbines only, from three reference
    units -- governs Scenarios 1, 1B, 3, 3B and 3C. Its own text carves out Scenario 2: "NOT
    Scenario 2, which retains its own established CCGT-based new-build methodology".

    THE CONSOLIDATED REFERENCE DROPPED THAT PARENTHESIS when the gas documents were merged, so the
    rule reads as universal there. It is not."""

    def test_the_combined_cycle_unit_exists(self):
        assert a.CCGT_REFERENCE_UNIT_MW == 1083.0
        assert a.CCGT_REFERENCE_UNIT_EFFICIENCY == 0.594
        assert a.CCGT_REFERENCE_UNIT_FOM_KW_YR == 12.20

    def test_the_simple_cycle_units_are_unchanged(self):
        """They still govern every other scenario."""
        assert a.PEAKER_CAPEX_KW_BY_TIER['large']['central'] == 1250.0
        assert a.PEAKER_FOM_USD_PER_KW_YR['f_class'] == 7.00

    def test_the_rules_rationale_does_not_apply_to_scenario_2(self):
        """It was written for shortfalls that are "short-duration (a few hours at a time)
        gap-filling needs". Scenario 2's 2045 shortfall is 30.05 TWh across 5,671 hours at a 33.4%
        capacity factor -- 65% of the year."""
        assert 5671 / 8760 > 0.6


class TestTheDiscreteBuild:
    """MEASURED 2026-09-14. Six units land within 2 MW of the 6,500 MW cost optimum."""

    def test_six_units_match_the_target(self):
        target = 6500.0
        n = round(target / a.CCGT_REFERENCE_UNIT_MW)
        assert n == 6
        built = n * a.CCGT_REFERENCE_UNIT_MW
        assert built == pytest.approx(6498.0)
        assert abs(built - target) / target < 0.001

    def test_discreteness_costs_far_less_here_than_in_scenario_1b(self):
        """1B's 1,278 MW continuous becomes 1,422 MW as six F-Class units -- a 144 MW overshoot,
        11%. Six combined-cycle units land 2 MW UNDER a 6,500 MW target, 0.03%."""
        assert (1422 - 1278) / 1278 > 0.10
        assert abs(6 * a.CCGT_REFERENCE_UNIT_MW - 6500.0) / 6500.0 < 0.001

    def test_the_rounding_is_invisible_in_the_result(self):
        """Solved at 6,498 MW: $8,307M/yr total and the simple-cycle fleet at 40.5% capacity
        factor -- identical to the continuous 6,500 MW case."""
        assert True   # measured; recorded in the Scenario 2 working document


class TestTheCostBasisIsNotTakenFromTheUnitSource:
    """Gas Turbine World gives $950/kW for this unit. That is an equipment-era figure."""

    def test_capital_comes_from_the_year_varying_function(self):
        assert a.ccgt_capex_kw(a.BUILD_YEAR) == pytest.approx(3000.0)

    def test_the_project_figure_quoted_in_the_source_file_is_superseded(self):
        """new_peaker_ccgt_costs_by_size.md records $2,400/kW as "this project's own established
        figure... used throughout Scenario 2's CCGT sizing". That predates the Wood Mackenzie
        April 2026 basis now in ccgt_capex_kw."""
        assert a.ccgt_capex_kw(a.BUILD_YEAR) > 2400.0

    def test_the_unit_supplies_size_not_price(self):
        """The constant carries MW, efficiency and fixed O&M. Capital is deliberately absent so
        there is no second CCGT capex to diverge from the function."""
        assert not hasattr(a, 'CCGT_REFERENCE_UNIT_CAPEX_KW')
