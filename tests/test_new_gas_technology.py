"""
test_new_gas_technology.py

How each scenario builds new gas capacity, and whether the evidence supports its declaration.
"""
import numpy as np
import pytest

import checkpoint_solver as cs


class TestEachScenarioDeclaresItsOwn:
    """Same construction as gas_retirement_schedule, and for the same reason: silent inheritance is
    the failure mode. The standing simple-cycle rule carves out Scenario 2 explicitly, and that
    carve-out was DROPPED in a document merge -- leaving the rule reading as universal."""

    def test_the_base_class_refuses_to_guess(self):
        with pytest.raises(NotImplementedError, match='must declare how new gas capacity is built'):
            cs.CheckpointSolver.new_gas_technology(None)

    @pytest.mark.parametrize('name,expected', [
        ('Scenario1Solver', 'simple_cycle'),      # 100% clean: gas fills residual gaps
        ('Scenario1BSolver', 'simple_cycle'),     # 5% gas -- the declaration most worth testing
        ('Scenario2Solver', 'combined_cycle'),    # carved out by the rule's own text, and measured
        ('Scenario3Solver', 'simple_cycle'),      # as Scenario 1, different siting
    ])
    def test_each_declares(self, name, expected):
        k = getattr(cs, name)
        assert 'new_gas_technology' in vars(k), f'{name} inherits instead of declaring'
        assert k.new_gas_technology(k) == expected


class TestTheDiagnosticMeasuresRatherThanRecommends:
    """The rule's rationale -- shortfalls are "short-duration (a few hours at a time) gap-filling
    needs" -- is a PREDICTION. Scenario 2 falsified it. So the premise is measured."""

    def test_a_peaky_shortfall_reads_as_peaking(self):
        u = np.zeros(8760)
        for start in range(0, 8000, 400):
            u[start:start + 3] = 500.0          # 3-hour blocks, well spaced
        p = cs.CheckpointSolver.shortfall_duty_profile(None, u)
        assert p['median_run_hours'] == 3.0
        assert p['median_run_suggests_peaking'] is True
        assert p['shortfall_share_of_year'] < 0.10

    def test_a_sustained_shortfall_does_not(self):
        u = np.zeros(8760)
        u[1000:3000] = 4_000.0                  # one 2,000-hour block
        p = cs.CheckpointSolver.shortfall_duty_profile(None, u)
        assert p['median_run_hours'] == 2000.0
        assert p['median_run_suggests_peaking'] is False

    def test_a_clean_year_reports_no_duty(self):
        p = cs.CheckpointSolver.shortfall_duty_profile(None, np.zeros(8760))
        assert p['shortfall_hours'] == 0 and p['event_count'] == 0
        assert p['median_run_suggests_peaking'] is False


class TestTheMaskingCaveat:
    """SCENARIO 2 IS WHY THIS EXISTS. Its shortfall has a median run of 3 hours at every tranche,
    which reads as peaking duty -- but that flat profile is an ARTIFACT of the existing simple-cycle
    fleet filling the bottom of the gap. Remove that fleet and the profile becomes a staircase,
    12-16 hours at the base: genuine combined-cycle duty."""

    def _s2_2045(self):
        u = np.zeros(8760)
        for start in range(0, 8700, 6):         # frequent short blocks, 65% of the year
            u[start:start + 4] = 5_000.0
        return u

    def test_saturation_is_detected(self):
        p = cs.CheckpointSolver.shortfall_duty_profile(
            None, self._s2_2045(), ct_fleet_mwh=3546.0 * 8760, ct_fleet_mw=3546.0)
        assert p['ct_capacity_factor'] == pytest.approx(1.0)
        assert p['existing_ct_saturated'] is True

    def test_a_short_median_run_is_flagged_as_possibly_masked(self):
        """The two measurements together, not either alone. A saturated fleet is serving load that
        wants combined-cycle plant AND hiding the duty shape above it."""
        p = cs.CheckpointSolver.shortfall_duty_profile(
            None, self._s2_2045(), ct_fleet_mwh=3546.0 * 8760, ct_fleet_mw=3546.0)
        assert p['median_run_suggests_peaking'] is True
        assert p['median_run_may_be_masked'] is True

    def test_an_unsaturated_fleet_leaves_the_run_length_readable(self):
        p = cs.CheckpointSolver.shortfall_duty_profile(
            None, self._s2_2045(), ct_fleet_mwh=3546.0 * 8760 * 0.15, ct_fleet_mw=3546.0)
        assert p['existing_ct_saturated'] is False
        assert p['median_run_may_be_masked'] is False

    def test_no_threshold_decides_the_technology(self):
        """Three sizing criteria built on this project's 28.1% crossover during 2026-09-14 proved to
        have no authority -- the crossover is a NEW-BUILD decision and existing plant has sunk
        capital. The diagnostic reports; the declaration is made elsewhere."""
        p = cs.CheckpointSolver.shortfall_duty_profile(None, np.zeros(8760))
        assert 'recommended_technology' not in p
        assert 'crossover' not in ' '.join(p.keys())


class TestScenario2MeasuredEvidence:
    """MEASURED 2026-09-14 at 2045, gas bounded by the real fleet."""

    def test_the_evidence_and_the_declaration_agree_for_the_right_reason(self):
        """Run length says peaking; share of year and capacity factor say otherwise. The
        combined-cycle declaration is right because the new capacity DISPLACES the existing fleet
        from baseload duty rather than serving the 3-hour blocks."""
        assert 5671 / 8760 == pytest.approx(0.647, abs=0.01)
        assert cs.Scenario2Solver.new_gas_technology(cs.Scenario2Solver) == 'combined_cycle'
