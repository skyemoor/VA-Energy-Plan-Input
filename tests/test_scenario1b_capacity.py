"""
test_scenario1b_capacity.py

Scenario 1B's gas capacity at 2045, and the reserve-margin variant it lacked.

TWO DEFECTS, both found 2026-09-14 by auditing the scenario before building its runner.
"""
import inspect

import pytest

import assumptions
import checkpoint_solver as cs
import driver as drv
import lp_model as lp
import numpy as np
import paths


def _solver(year):
    w = np.load(paths.weather_year('hydro_year1_2016_17_RECONSTRUCTED.npz'))
    d = np.load(paths.intermediate('demand_2045fy_va_only.npy'))
    return cs.Scenario1BWithReserveMargin(
        year=year, demand=d, exist_solar=lp.exist_solar_mw(year) * w['solar'],
        solar_cf=w['solar'], wind_cf=w['wind'], nuclear=w['nuclear'])


class TestTheReserveMarginVariantExists:
    """There was none. 1B solved with NO reserve margin at all while Scenarios 1 and 3 carried the
    all-hours constraint -- holding it to a looser reliability standard than the scenarios it is
    compared against. The same defect Scenario 2 had."""

    def test_it_uses_the_all_hours_mixin(self):
        assert cs.AllHoursReserveMixin in cs.Scenario1BWithReserveMargin.__mro__

    def test_it_keeps_1b_target_logic(self):
        assert cs.Scenario1BSolver in cs.Scenario1BWithReserveMargin.__mro__

    def test_the_target_is_5_percent_gas_from_2045(self):
        assert _solver(2045).gas_target_share == 0.05

    def test_before_2045_it_follows_the_rps(self):
        """1B diverges from Scenario 1 only at 2045 -- same RPS target every year through 2044.

        2044's RPS is 5% gas, which IS 1B's 2045 target. That is why 2044 must be a checkpoint for
        this scenario: its 2045 build should equal its 2044 build, and linking 2045 back to 2040
        instead produced what Appendix N.4 called 'a physically nonsensical, wildly oversized 2045
        buildout'. Compared with a tolerance because gas_target_share interpolates."""
        assert _solver(2044).gas_target_share == pytest.approx(drv.gas_target_share(2044))
        assert drv.gas_target_share(2044) == pytest.approx(0.05)


class TestTheCapacitySweepIsImplemented:
    """Appendix N.2 locked in 6,000 MW total (1,278 MW new simple-cycle CT) after sweeping capped
    capacities and costing each as LP objective PLUS externally-priced new-build capex. THE FIGURE
    WAS NEVER IMPLEMENTED -- Scenario1BSolver inherited apply_gas_cap unchanged, giving 4,722 MW."""

    def test_the_locked_figure_is_a_constant(self):
        assert assumptions.SCENARIO_1B_GAS_CAPACITY_MW == 6_000.0
        assert assumptions.SCENARIO_1B_NEW_CT_MW == 1_278.0
        assert assumptions.SCENARIO_1B_NEW_CT_CAPEX_KW == 2_000.0

    def test_the_arithmetic_closes(self):
        """6,000 total = 4,722 existing-plus-pool + 1,278 new. That the two figures reconcile
        exactly is what confirms N.2's 'new build' column is measured beyond 4,722, not beyond the
        1,860 MW of surviving plant."""
        inherited = drv.schedule_b_baseline_mw(2045) + assumptions.GAS_NEW_BUILD_POOL_MW
        assert inherited == pytest.approx(4_722.0)
        assert inherited + assumptions.SCENARIO_1B_NEW_CT_MW == pytest.approx(
            assumptions.SCENARIO_1B_GAS_CAPACITY_MW)

    def test_the_cap_applies_from_2045(self):
        assert _solver(2045).apply_gas_cap() == 6_000.0

    def test_before_2045_the_inherited_cap_is_unchanged(self):
        """Identical to Scenario 1 through 2044, so the cap must be too."""
        # 10,253 = the 7,391 MW baseline at 2044 + the 2,862 MW pool. WAS 12,224 on a flat 9,362,
        # corrected 2026-09-14: the reference table states Schedule B as "same as Schedule A"
        # through 2044, and Schedule A steps down at 2041 and 2044 for Bear Garden and Warren
        # County. This is 1B's own 2044 checkpoint, which sets its capacity requirement.
        assert _solver(2044).apply_gas_cap() == pytest.approx(10_253.0)

    def test_it_exceeds_scenario_1s_cap_at_2045(self):
        """Scenario 1 is bound at 4,722 MW; 1B builds beyond it. If these were equal, 1B's relaxed
        target would have no capacity to exercise it with -- which is exactly what N.4 measured."""
        assert _solver(2045).apply_gas_cap() > drv.schedule_b_baseline_mw(2045) + 2_862.0

    def test_the_omission_is_documented_where_it_bit(self):
        """Rule 10.3: a future reader must not 'simplify' this back to the inherited cap."""
        src = inspect.getsource(cs.Scenario1BSolver.apply_gas_cap)
        assert '1.63%' in src
        assert 'artifact of the omission' in src


class TestWhatThisInvalidates:
    def test_appendix_n4s_headline_was_measured_at_the_wrong_capacity(self):
        """N.4: 'gas dispatch still pins the physical gas-fleet capacity cap exactly (4,722 MW)'
        -- which is N.2's own 'existing only' row, costing $10,065.2M against $9,469.3M at 6,000 MW.
        N.4 solved the configuration N.2 explicitly rejected, so its 1.63% and its conclusion that
        'the 5% statutory ceiling is largely moot' both need re-measuring."""
        assert 4_722.0 < assumptions.SCENARIO_1B_GAS_CAPACITY_MW


class TestRetainOverhaulPlanIsWired:
    """driver.select_overhaul_retain had no caller since it was written -- real, sourced machinery
    nobody had connected. The module-level orphan check could not see it, because driver.py is
    imported everywhere and is never itself orphaned."""

    def test_the_plan_is_available_from_2045(self):
        assert _solver(2045).retain_and_overhaul_plan() is not None

    def test_it_is_none_before_2045(self):
        """Before 2045, 1B's capacity is Scenario 1's and there is nothing extra to retain."""
        assert _solver(2044).retain_and_overhaul_plan() is None

    def test_it_reproduces_N2s_locked_figure_independently(self):
        """THE CROSS-CHECK THAT MATTERS. Two pieces of work that never met agree exactly:

            6,000 target − 1,860 Schedule B survivors − 2,862 POOL = 1,278 MW residual
            N.2's capacity sweep, by a different route entirely:     1,278 MW new CT

        That is the strongest available evidence the 6,000 MW target is right."""
        p = _solver(2045).retain_and_overhaul_plan()
        assert p['residual_gap_mw'] == pytest.approx(assumptions.SCENARIO_1B_NEW_CT_MW)
        assert p['residual_gap_mw'] == pytest.approx(1_278.0)

    def test_both_continuous_and_discrete_are_reported(self):
        """F-Class units are 237 MW, so a 1,278 MW residual takes six -- 1,422 MW, overshooting by
        144. N.2's sweep treated capacity as continuous; this is the buildable version. Which
        applies depends on whether the question is cost or procurement, so both are given."""
        p = _solver(2045).retain_and_overhaul_plan()
        assert p['new_build_mw_continuous'] == pytest.approx(1_278.0)
        assert p['new_build_mw_discrete'] == pytest.approx(1_422.0)
        assert p['new_build_units'] == 6

    def test_the_four_oldest_plants_are_flagged_for_overhaul(self):
        """Gordonsville 1994, Elizabeth River 1992, Darbytown 1990, Gravel Neck 1989 -- all
        'near/beyond nominal 30-45yr CT life' per the POOL annotations, and all needing capital
        work rather than simply being retained."""
        p = _solver(2045).retain_and_overhaul_plan()
        assert set(p['needing_overhaul']) == {'Gordonsville', 'Elizabeth River', 'Darbytown',
                                              'Gravel Neck'}

    def test_cum_mw_includes_newbuild_which_reads_as_an_inconsistency(self):
        """select_overhaul_retain's cum_mw is TOTAL delivered capacity, not the selected plants:
        2,862 MW of plant is reported as 4,284. That looks wrong until the newbuild term is
        noticed, which is why the plan reports the components separately."""
        import driver as drv
        r = drv.select_overhaul_retain(4_140.0)
        assert sum(x[1] for x in r['selected']) == pytest.approx(2_862.0)
        assert r['cum_mw'] == pytest.approx(4_284.0)
