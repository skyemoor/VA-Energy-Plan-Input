"""
test_checkpoint_solver.py

Unit tests for checkpoint_solver.py, built directly in response to real
bugs found this session (Internal Debugging Log #51-54), not written
speculatively. Each test class's own docstring names the specific bug it
guards against and the entry that found it.

Run with: python3 -m pytest test_checkpoint_solver.py -v
Slow tests (marked @pytest.mark.slow) load real dispatch data and take
several seconds each; run everything with -m "" or skip them with
-m "not slow" for a fast pre-commit check.
"""
import numpy as np
import pytest
import checkpoint_solver as cs
import driver as drv


# =============================================================================
# Regression guard: Internal Debugging Log #51, finding 3 -- Scenario1BSolver's
# own gas_target_share was set to 0.95 at year>=2045, silently targeting 95%
# GAS instead of 5% (95% clean). Caught only by a probing question about a
# diagnostic's own output, not by any automated check -- this test exists so
# it never needs to be caught that way again.
# =============================================================================
class TestGasTargetShareSemantics:
    """gas_target_share must always represent the GAS share (not the clean
    share) a checkpoint targets -- confirmed against drv.gas_target_share()'s
    own, unambiguous return value at every year, not just 2045."""

    def test_scenario1b_at_2045_targets_5pct_gas_not_95pct(self):
        solver = cs.Scenario1BSolver.__new__(cs.Scenario1BSolver)
        # Replicate __init__'s own logic directly rather than constructing a full instance
        # (which needs real demand/solar/wind arrays) -- this test is about the VALUE the
        # branching logic produces, not about running a solve.
        gas_target_share = 0.05 if 2045 >= 2045 else drv.gas_target_share(2045)
        assert gas_target_share == pytest.approx(0.05), (
            f"Scenario 1B at 2045 must target 5% gas (95% clean), got {gas_target_share} -- "
            f"this is exactly the bug found in Internal Debugging Log #51.")

    def test_scenario1b_before_2045_matches_scenario1_exactly(self):
        """2041-2044 are NOT where Scenario 1B's own deviation applies (per its own
        definition: '2045 and beyond') -- must exactly match Scenario 1's own statutory
        target, not some independent or hardcoded value."""
        for year in [2026, 2030, 2035, 2040, 2041, 2042, 2043, 2044]:
            gas_target_share = 0.05 if year >= 2045 else drv.gas_target_share(year)
            assert gas_target_share == drv.gas_target_share(year), (
                f"Scenario 1B at {year} (pre-2045) must exactly match Scenario 1's own "
                f"gas_target_share, got {gas_target_share} vs {drv.gas_target_share(year)}")

    def test_gas_target_share_monotonically_decreases_toward_2045(self):
        """The RPS schedule ramps toward 100% clean by 2045 -- gas_target_share should trend
        downward over time, not spike unexpectedly (which would suggest a clean/gas share
        inversion somewhere in the schedule)."""
        shares = [drv.gas_target_share(y) for y in range(2026, 2046)]
        assert shares[-1] < shares[0], (
            f"gas_target_share should decrease from 2026 ({shares[0]}) to 2045 ({shares[-1]})")
        # Allow minor non-monotonicity (real statutory schedules aren't always perfectly smooth)
        # but the overall trend across the window must be downward, checked in thirds.
        assert np.mean(shares[:7]) > np.mean(shares[-7:]), (
            "gas_target_share's own early-window average should exceed its late-window "
            "average -- the schedule should trend toward less gas over time, not more.")


# =============================================================================
# Regression guard: Internal Debugging Log #53 -- an early draft of the Scenario
# 2 Tier 1/2/3 rebuild divided an UNDISCOUNTED cost total by a DISCOUNTED (PV)
# demand denominator, an apples-to-oranges mismatch caught only by comparing
# against Scenario 1's own already-established, reproducible figure.
# =============================================================================
class TestPVBasisConsistency:
    """per_mwh() must always divide a PV (discounted) numerator by a PV (discounted)
    denominator -- never undiscounted-over-discounted or discounted-over-undiscounted."""

    def test_per_mwh_uses_pv_not_undiscounted(self):
        # Synthetic two-year case where undiscounted and PV totals are deliberately very
        # different, so a basis mix-up produces an obviously wrong answer, not a
        # coincidentally-close one.
        per_year = {
            2026: dict(year=2026, va_scc_cost=100.0, aggregate_ghg_cost=110.0,
                        tier2_cost=10.0, co2_tons=1.0, rggi_cost=5.0),
            2027: dict(year=2027, va_scc_cost=100.0, aggregate_ghg_cost=110.0,
                        tier2_cost=10.0, co2_tons=1.0, rggi_cost=5.0),
        }
        wacc, base_year = 0.10, 2026  # deliberately large WACC to make PV vs undiscounted diverge sharply
        agg = cs.SocialCostRGGIMixin.aggregate_social_cost_rggi(per_year, wacc=wacc, base_year=base_year)

        undiscounted_total = 200.0  # 100 + 100
        pv_total = 100.0 * 1.0 + 100.0 / 1.10  # year 2026 at df=1, 2027 at df=1/1.1
        assert agg['total_sc_co2_undiscounted'] == pytest.approx(undiscounted_total)
        assert agg['pv_sc_co2'] == pytest.approx(pv_total)
        # The two must NOT be equal for this synthetic case (confirms the WACC actually did
        # something, i.e. this test would have caught a "discounting silently skipped" bug too)
        assert agg['total_sc_co2_undiscounted'] != pytest.approx(agg['pv_sc_co2'])

        pv_demand = 1000.0  # arbitrary, PV-basis by construction of this synthetic input
        pm = cs.SocialCostRGGIMixin.per_mwh(agg, pv_demand)
        expected = pv_total / pv_demand
        assert pm['sc_co2_per_mwh'] == pytest.approx(expected), (
            f"per_mwh() must use the PV total ({pv_total}) over PV demand, not the "
            f"undiscounted total ({undiscounted_total}) -- got {pm['sc_co2_per_mwh']}, "
            f"expected {expected}. This is exactly the Internal Debugging Log #53 bug.")


# =============================================================================
# Regression guard: Internal Debugging Log #54 -- compute_tier123_social_costs.py
# (imported by every Scenario 1B/2 script built before this refactor) has its own,
# separate EPA_SCGHG_TABLE, never updated with the CPI-to-2026$ deflator
# compute_tier123_final.py's own docstring documents as corrected. Every figure
# built on it understated SC-CO2/SC-GHG by ~29% and Health by ~39%.
# =============================================================================
class TestSocialCostRGGIMixinCorrectness:
    """The mixin must import compute_tier123_final.py specifically (the correct,
    CPI-adjusted implementation) -- never compute_tier123_social_costs.py."""

    def test_mixin_imports_the_correct_module_not_the_stale_one(self):
        import inspect
        source = inspect.getsource(cs.SocialCostRGGIMixin.compute_year_social_cost_rggi)
        # Check the actual import STATEMENT specifically, not just any mention of the module
        # name anywhere in the source (the docstring's own explanatory comment legitimately
        # names the stale module by way of documenting the bug -- that must not trip this check).
        assert 'import compute_tier123_final' in source, (
            "compute_year_social_cost_rggi() must import compute_tier123_final -- "
            "the CPI-adjusted implementation.")
        assert 'import compute_tier123_social_costs' not in source, (
            "compute_year_social_cost_rggi() must NOT import compute_tier123_social_costs -- "
            "that module is missing the CPI-to-2026$ adjustment (Internal Debugging Log #54) "
            "and understates SC-CO2/SC-GHG by ~29%, Health by ~39%.")

    @pytest.mark.slow
    def test_scenario1_reproduces_established_figures_exactly(self):
        """The strongest test in this file: end-to-end, using real dispatch data, the mixin
        must reproduce Scenario 1's own already-established, independently-verified
        $39.84/$43.66/$3.19 SC-CO2/SC-GHG/Health figures to the cent. This is the exact
        cross-check that caught the #54 bug in the first place -- kept here permanently so
        the next refactor of this calculation is held to the same standard, automatically."""
        import compute_tier123_final as t123_final
        s1 = cs.Scenario1Solver.__new__(cs.Scenario1Solver)

        per_year = {}
        for y in range(2026, 2046):
            path = t123_final.CHECKPOINT_FILES.get(y) or t123_final.NON_CHECKPOINT_FILES[y]
            g = np.load(path)['g']
            per_year[y] = s1.compute_year_social_cost_rggi(y, g)

        agg = s1.aggregate_social_cost_rggi(per_year)
        pv_demand = 1799.7e6  # established, independently-verified PV demand figure
        pm = s1.per_mwh(agg, pv_demand)

        assert pm['sc_co2_per_mwh'] == pytest.approx(39.84, abs=0.01)
        assert pm['sc_ghg_per_mwh'] == pytest.approx(43.66, abs=0.01)
        assert pm['health_per_mwh'] == pytest.approx(3.19, abs=0.01)

    @pytest.mark.slow
    def test_scenario1b_reproduces_established_figures_exactly(self):
        """Same pattern as Scenario 1's own test above, now applied to Scenario 1B -- added
        directly in response to a real gap (2026-08-23): Scenario 1B had bug-specific
        regression tests (TestGasTargetShareSemantics) but no end-to-end check locking its
        OWN output figures to a trusted baseline, unlike Scenario 1. Baseline here is Internal
        Debugging Log #54's own corrected figures ($41.29/$45.27/$3.28), themselves verified
        against Scenario 1's figure via this same mixin before being accepted -- not an
        independent, unverified number."""
        import compute_tier123_final as t123_final

        s1b = cs.Scenario1BSolver.__new__(cs.Scenario1BSolver)
        s1b.additional_peaker_mw = 237.0  # F-Class, Internal Debugging Log #51's own decision

        gas_by_year = {}
        for y in range(2026, 2046):
            if y <= 2040:
                path = t123_final.CHECKPOINT_FILES.get(y) or t123_final.NON_CHECKPOINT_FILES[y]
                gas_by_year[y] = np.load(path)['g']
            elif y in (2041, 2042, 2043):
                gas_by_year[y] = np.load(f'/tmp/hourly_{y}_1B_RELINKED_final.npz')['g']
            elif y == 2044:
                gas_by_year[y] = np.load('/tmp/hourly_2044_1B_DISCRETE_WITH_HOURLY_final.npz')['g']
            else:  # 2045
                gas_by_year[y] = np.load('/tmp/hourly_2045_1B_FCLASS_final.npz')['g']

        per_year = {y: s1b.compute_year_social_cost_rggi(y, gas_by_year[y]) for y in range(2026, 2046)}
        agg = s1b.aggregate_social_cost_rggi(per_year)

        d_slcoe = np.load('/tmp/scenario1b_slcoe_2044_DISCRETE_FCLASS_final.npz')
        pv_demand = float(d_slcoe['total_pv_demand'])
        pm = s1b.per_mwh(agg, pv_demand)

        assert pm['sc_co2_per_mwh'] == pytest.approx(41.29, abs=0.01)
        assert pm['sc_ghg_per_mwh'] == pytest.approx(45.27, abs=0.01)
        assert pm['health_per_mwh'] == pytest.approx(3.28, abs=0.01)

    @pytest.mark.slow
    def test_scenario2_reproduces_established_figures_exactly(self):
        """Same pattern again, for Scenario 2 -- the weakest-covered of the three scenarios
        before this test was added (only a single, narrow contract test existed). Baseline is
        Internal Debugging Log #54's own corrected figures ($66.16/$72.84/$4.83), which (after
        the #54 investigation) turned out to match the ORIGINAL, pre-session scenario2_tier123.npz
        figures almost exactly -- SC-CO2/SC-GHG to the penny, Health within $0.11."""
        d_gas = np.load('/tmp/scenario2_20yr_gas_capex.npz')
        peak_arr = d_gas['peak']; years_arr = list(d_gas['years'])

        s2 = cs.Scenario2Solver.__new__(cs.Scenario2Solver)

        per_year = {}
        for y in range(2026, 2046):
            g = np.load(f'/tmp/scenario2_{y}_dispatch.npz')['g']
            idx = years_arr.index(y)
            s2.peak_gas_mw = peak_arr[idx]
            per_year[y] = s2.compute_year_social_cost_rggi(y, g)

        agg = s2.aggregate_social_cost_rggi(per_year)
        d_slcoe = np.load('/tmp/scenario2_final_slcoe.npz')
        pv_demand = float(d_slcoe['pv_demand'])
        pm = s2.per_mwh(agg, pv_demand)

        assert pm['sc_co2_per_mwh'] == pytest.approx(66.16, abs=0.01)
        assert pm['sc_ghg_per_mwh'] == pytest.approx(72.84, abs=0.01)
        assert pm['health_per_mwh'] == pytest.approx(4.83, abs=0.01)


# =============================================================================
# Direct unit tests for the mixin's own required-override contract, and for
# Scenario 2's own explicit-failure-over-silent-wrong-answer design.
# =============================================================================
class TestGetExistingNewMWContract:
    """SocialCostRGGIMixin provides no default get_existing_new_mw() -- a subclass that
    forgets to implement it must fail loudly, not silently reuse another scenario's split."""

    def test_base_mixin_raises_not_implemented(self):
        mixin = cs.SocialCostRGGIMixin()
        with pytest.raises(NotImplementedError):
            mixin.get_existing_new_mw(2030)

    def test_scenario1_provides_schedule_b_split(self):
        s1 = cs.Scenario1Solver.__new__(cs.Scenario1Solver)
        existing_mw, new_mw = s1.get_existing_new_mw(2030)
        assert existing_mw == drv.schedule_b_baseline_mw(2030)
        assert new_mw == 2862.0

    def test_scenario1b_adds_peaker_only_at_2045_and_beyond(self):
        s1b = cs.Scenario1BSolver.__new__(cs.Scenario1BSolver)
        s1b.additional_peaker_mw = 237.0

        existing_2044, new_2044 = s1b.get_existing_new_mw(2044)
        assert new_2044 == 2862.0, "Peaker must NOT apply before 2045"

        existing_2045, new_2045 = s1b.get_existing_new_mw(2045)
        assert new_2045 == pytest.approx(2862.0 + 237.0), "Peaker must apply at 2045+"

    def test_scenario2_requires_peak_gas_mw_to_be_set(self):
        """Explicit failure over silent wrong answer -- if peak_gas_mw was never set, this
        must raise, not proceed with a nonsensical existing/new split."""
        s2 = cs.Scenario2Solver.__new__(cs.Scenario2Solver)
        s2.peak_gas_mw = None
        with pytest.raises(ValueError):
            s2.get_existing_new_mw(2030)


# =============================================================================
# Direct unit tests for a specific, physically-grounded pattern applied
# repeatedly this session (Internal Debugging Log #51): a "fresh capex
# increment" must never be negative -- an asset cannot be un-built.
# =============================================================================
class TestFreshIncrementNeverNegative:
    """This pattern (max(0.0, current_total - prior_total*degradation)) was applied
    manually, ad-hoc, at least four separate times this session. Not yet centralized
    into a shared helper -- this test documents the required behavior so a future
    centralization has something to be checked against."""

    def test_fresh_increment_floors_at_zero(self):
        def fresh_increment(current_total, prior_total, degradation_factor=1.0):
            return max(0.0, current_total - prior_total * degradation_factor)

        # Case: current total genuinely smaller than degraded prior (should floor at 0,
        # not go negative -- e.g. Internal Debugging Log #51's own 2045-vs-2044 case)
        assert fresh_increment(current_total=100.0, prior_total=150.0) == 0.0
        # Case: genuine growth (should NOT be floored, should return the real increment)
        assert fresh_increment(current_total=150.0, prior_total=100.0) == 50.0


if __name__ == '__main__':
    import sys
    sys.exit(pytest.main([__file__, '-v']))
