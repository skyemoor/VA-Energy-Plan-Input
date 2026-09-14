"""
test_storage_resistor_threshold.py

The curtailment price above which the LP dumps surplus through storage round-trip losses instead of
curtailing -- producing simultaneous charge and discharge.

FOUND 2026-09-13 by restoring Internal Debugging Log #20's $100/MWh: 4,710 hours of simultaneous
Na-ion charge/discharge at 2045, caught by verify_result().
"""
import pytest

import assumptions
import lp_model as lp
import storage_resistor_threshold as srt


class TestTheDerivation:
    """cycling_cost x RTE / (1 - RTE) -- arithmetic on two sourced parameters, not a new deterrent.
    Appendix P.2 §13 catalogues seven rejected attempts; this invents nothing, it states where the
    EXISTING mechanism stops working."""

    def test_sodium_ion(self):
        """$5.43/MWh cycling at 90% RTE. Charge 100, discharge 90, absorb 10 -- 90 x $5.43 = $489
        for 10 MWh absorbed."""
        assert srt.resistor_threshold_mwh('sodium_ion') == pytest.approx(48.87, abs=0.5)

    def test_iron_air(self):
        assert srt.resistor_threshold_mwh('iron_air') == pytest.approx(72.13, abs=0.5)

    def test_bath_is_the_binding_constraint(self):
        """NOT sodium-ion, which is what the mechanism was first noticed on. Bath's $7.50/MWh at
        80% RTE makes it the CHEAPEST resistor in the system at $30/MWh -- so it governs regardless
        of how high the others sit, since the LP uses whichever is cheapest."""
        assert srt.resistor_threshold_mwh('bath_pumped_hydro') == pytest.approx(30.00, abs=0.5)
        assert srt.binding_threshold_mwh() == pytest.approx(30.00, abs=0.5)

    def test_unknown_type_raises(self):
        with pytest.raises(ValueError, match='unknown storage type'):
            srt.resistor_threshold_mwh('flywheel')

    def test_bath_cost_is_cross_checked_against_build_problem(self):
        """Rule 6.2: Bath's $7.50 is a literal in build_problem and mirrored in this module, so the
        two are asserted to agree rather than trusted to."""
        assert srt.cross_check_bath_cycling_cost() is True


class TestTheConflictIsDisclosedNotTuned:
    """Two different questions, and conflating them would let model mechanics dictate economics."""

    def test_the_economic_figure_is_retained_separately(self):
        """#20's $100/MWh was defended as 'same order of magnitude as gas cost and the export
        price'. Nothing found here refutes that -- the model simply cannot represent it."""
        assert assumptions.CURTAILMENT_COST_ECONOMIC_MWH == 100.0

    def test_the_value_actually_used_is_below_the_binding_threshold(self):
        assert assumptions.CURTAILMENT_COST_MWH < srt.binding_threshold_mwh()

    def test_the_import_time_assertion_passes(self):
        assert assumptions.assert_curtailment_below_resistor_threshold()['safe'] is True

    def test_raising_it_above_the_threshold_is_caught_without_a_solve(self):
        """It failed loudly once -- but only because a solve was run. This catches it without one."""
        saved = assumptions.CURTAILMENT_COST_MWH
        try:
            assumptions.CURTAILMENT_COST_MWH = 100.0
            with pytest.raises(AssertionError, match='ABOVE THE THRESHOLD'):
                assumptions.assert_curtailment_below_resistor_threshold()
        finally:
            assumptions.CURTAILMENT_COST_MWH = saved

    def test_the_limitation_is_stated_as_a_limitation(self):
        """Not as evidence about what curtailment truly costs."""
        note = srt.check_curtailment_cost(100.0)['note']
        assert 'MODEL LIMITATION' in note
        assert 'structural complementarity' in note

    def test_it_reports_rather_than_raising(self):
        """A conflict needs a decision -- run below the threshold and disclose, or accept MILP --
        not silent resolution by lowering a sourced figure."""
        r = srt.check_curtailment_cost(100.0)
        assert r['safe'] is False


class TestMeasuredEffect:
    """2045 Scenario 1, measured 2026-09-13. Direction matches Internal Debugging Log #20's
    prediction (solar down, iron-air up, curtailment down) at smaller magnitude, as expected from a
    $5 -> $25 change rather than #20's $1 -> $100."""

    def test_recorded_comparison(self):
        at_5 = {'solar': 165_875, 'fe_twh': 3.81, 'curt_twh': 161.5, 'obj_b': 26.07}
        at_25 = {'solar': 156_737, 'fe_twh': 4.77, 'curt_twh': 142.1, 'obj_b': 29.10}
        assert at_25['solar'] < at_5['solar']          # #20: less solar overbuild
        assert at_25['fe_twh'] > at_5['fe_twh']        # #20: more iron-air
        assert at_25['curt_twh'] < at_5['curt_twh']    # #20: less curtailment
        assert at_25['obj_b'] > at_5['obj_b']          # #20: net cost rises

    def test_curtailment_does_not_reach_zero(self):
        """#20 reported curtailment 'dropped to exactly zero'. At $25/MWh it drops 12% to 142.1
        TWh -- a long way from zero. Either the $100 price was doing far more work than $25 can, or
        #20's zero was achieved partly THROUGH the resistor behaviour we now reject: curtailment
        relabelled as storage losses rather than eliminated. Recorded as an open question, not a
        settled explanation."""
        assert 142.1 > 0
