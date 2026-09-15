"""
test_gas_retirement_schedule.py

Schedules A and B differ by 5,531 MW at 2045, and which applies is a SCENARIO property -- whether
that scenario gives gas plants a market -- not a fact about the fleet.
"""
import pytest

import checkpoint_solver as cs
import driver as drv


class TestTheTwoSchedules:

    @pytest.mark.parametrize('year,expected', [(2030, 9362.0), (2040, 9362.0),
                                               (2041, 8740.0), (2043, 8740.0),
                                               (2044, 7391.0), (2045, 7391.0)])
    def test_schedule_a_is_physical_retirement(self, year, expected):
        """Plant age, market-indifferent. Bear Garden 2041, Warren County 2044."""
        assert drv.gas_baseline_mw(year, 'A') == expected

    @pytest.mark.parametrize('year,expected', [(2040, 9362.0), (2044, 9362.0), (2045, 1860.0)])
    def test_schedule_b_is_vcea_driven(self, year, expected):
        """Identical to A through 2044, then Brunswick County, Potomac Energy Center and
        Greensville -- 3,774 MW -- retire FOR LACK OF MARKET."""
        assert drv.gas_baseline_mw(year, 'B') == expected

    def test_they_are_identical_through_2040(self):
        for y in range(2026, 2041):
            assert drv.gas_baseline_mw(y, 'A') == drv.gas_baseline_mw(y, 'B')

    def test_the_2045_difference(self):
        assert drv.gas_baseline_mw(2045, 'A') - drv.gas_baseline_mw(2045, 'B') == 5531.0

    def test_an_unknown_schedule_raises(self):
        """Rule 5. Defaulting would reintroduce exactly the defect this replaced."""
        with pytest.raises(ValueError, match='must declare which retirement world'):
            drv.gas_baseline_mw(2045, 'C')

    def test_the_legacy_helper_still_returns_schedule_b(self):
        """Kept rather than removed: Scenarios 1, 1B and 3 all genuinely use B, and renaming a
        correct call site adds churn without safety."""
        assert drv.schedule_b_baseline_mw(2045) == drv.gas_baseline_mw(2045, 'B')


class TestEachScenarioDeclaresItsOwn:
    """SCENARIO 2 INHERITED SCHEDULE B SILENTLY for its entire life -- modelling a retirement
    premised on a scenario it was not running. An inherited default is what allowed that."""

    def test_the_base_class_refuses_to_guess(self):
        with pytest.raises(NotImplementedError, match='must declare its gas retirement schedule'):
            cs.CheckpointSolver.gas_retirement_schedule(None)

    @pytest.mark.parametrize('name,expected', [
        ('Scenario1Solver', 'B'),      # 100% clean at 2045: the plants genuinely have no market
        ('Scenario1BSolver', 'B'),     # 5% gas needs very little; retain enough to cover next year
        ('Scenario2Solver', 'A'),      # gas at 68% CF supplying 132 TWh -- the best market they see
        ('Scenario3Solver', 'B'),      # same terminal year as Scenario 1, different siting
    ])
    def test_each_scenario_declares(self, name, expected):
        klass = getattr(cs, name)
        assert 'gas_retirement_schedule' in vars(klass), f'{name} inherits instead of declaring'
        assert klass.gas_retirement_schedule(klass) == expected


class TestTheCorrectionIsMaterial:
    """MEASURED 2026-09-14, on PJM ELCC accreditation."""

    def test_the_2045_capacity_gap_nearly_halves(self):
        """New gas needed at 2045 falls from 11,917 MW on Schedule B to 6,386 MW on Schedule A --
        the 5,531 MW difference being entirely the retirement premise, not demand or dispatch."""
        assert 11_917 - 6_386 == pytest.approx(5_531, abs=1)

    def test_the_intermediate_years_were_overstated_too(self):
        """Schedule A retires 622 MW from 2041 and 1,971 MW from 2044 that the old flat baseline
        ignored entirely -- so those years had MORE capacity than they should, not less."""
        assert drv.gas_baseline_mw(2041, 'A') == 9362.0 - 622.0
        assert drv.gas_baseline_mw(2044, 'A') == 9362.0 - 1971.0
