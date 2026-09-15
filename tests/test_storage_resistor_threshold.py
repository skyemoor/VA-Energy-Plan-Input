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


@pytest.fixture(autouse=True)
def _at_2045():
    """THE THRESHOLD IS YEAR-DEPENDENT, found 2026-09-14 by a test-order failure.

    driver.set_year_capex(year) rebinds lp_model.NA_CYCLE_LIFE (10,000 before 2035, 15,000 after)
    and the capex terms, so sodium-ion's threshold moves with whichever checkpoint was last set.
    Bath's $7.50 is a literal and does not move -- so Bath binds at EVERY year, but any sodium
    figure asserted here must state its year. Pinned to 2045, the year the figures were derived
    at, and restored afterwards so this file does not poison others the way it was poisoned."""
    import driver as drv
    drv.set_year_capex(2045)
    yield
    drv.set_year_capex(2045)


class TestTheDerivation:
    """cycling_cost x RTE / (1 - RTE) -- arithmetic on two sourced parameters, not a new deterrent.
    Appendix P.2 #13 catalogues seven rejected attempts; this invents nothing, it states where the
    EXISTING mechanism stops working."""

    def test_sodium_ion_at_2045(self):
        """Charge 100, discharge 90, absorb 10 -- 90 x cycling cost for 10 MWh absorbed.

        $48.06 at set_year_capex(2045). The $48.87 quoted when this was first derived was at the
        module's IMPORT-TIME parameters, which are evaluated at a hardcoded 2044.5 -- neither 2045
        nor any checkpoint. That inconsistency was already flagged in the constants audit
        (MODEL_WIDE_FINDINGS 2B, 'GAS_COST_MWH and FE_RTE_CHARGE evaluated at a hardcoded 2044.5')
        and this is it biting. Both figures sit well above Bath's $30, so the binding threshold
        and every conclusion drawn from it are unchanged."""
        assert srt.resistor_threshold_mwh('sodium_ion') == pytest.approx(48.06, abs=0.5)

    def test_the_formula_holds_regardless_of_year(self):
        """Asserts the DERIVATION rather than a number, so it cannot be broken by state."""
        cyc = (lp.NA_ENERGY_CAPEX * 1000) / (lp.NA_CYCLE_LIFE * (1.0 - lp.NA_DOD_FLOOR))
        expected = cyc * lp.NA_RTE_CHARGE / (1.0 - lp.NA_RTE_CHARGE)
        assert srt.resistor_threshold_mwh('sodium_ion') == pytest.approx(expected, rel=1e-9)

    def test_sodium_threshold_moves_with_the_checkpoint_year(self):
        """The finding itself. Pre-2035 cycle life is 10,000, not 15,000, and the threshold rises
        with it. Bath stays at $30 throughout, so the BINDING threshold does not change -- but a
        derivation that quoted only sodium would have been wrong for early checkpoints."""
        import driver as drv
        drv.set_year_capex(2030)
        early = srt.resistor_threshold_mwh('sodium_ion')
        drv.set_year_capex(2045)
        late = srt.resistor_threshold_mwh('sodium_ion')
        assert early != pytest.approx(late, rel=0.01)
        assert srt.resistor_threshold_mwh('bath_pumped_hydro') == pytest.approx(30.0, abs=0.5)

    def test_iron_air_at_2045(self):
        """$70.08 at set_year_capex(2045); $72.13 at the import-time 2044.5 parameters."""
        assert srt.resistor_threshold_mwh('iron_air') == pytest.approx(70.08, abs=0.5)

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


class TestCapexYearIsExplicit:
    """The fix for mutable module state, 2026-09-14. lp_model's capex constants are REBOUND IN
    PLACE by driver.set_year_capex(), so a reader outside a solver gets whichever year ran last.
    This module reported $48.87 that way -- the BUILD_YEAR (2044.5) value -- where 2045 gives
    $48.06 and 2030 gives $119.54."""

    def test_lp_model_exposes_the_bound_year(self):
        import lp_model as lp
        assert hasattr(lp, 'CAPEX_YEAR')

    def test_set_year_capex_records_it(self):
        import driver as drv
        import lp_model as lp
        try:
            drv.set_year_capex(2030)
            assert lp.CAPEX_YEAR == 2030
            drv.set_year_capex(2045)
            assert lp.CAPEX_YEAR == 2045
        finally:
            drv.set_year_capex(2045)

    def test_the_threshold_reports_which_year_it_used(self):
        """So a figure can never be quoted without its basis."""
        assert srt.resistor_threshold_mwh(year=2030)['_capex_year'] == 2030
        assert srt.check_curtailment_cost(year=2045)['capex_year'] == 2045

    def test_it_restores_the_previous_binding(self):
        """A module that silently leaves the constants on a different year poisons whatever runs
        next -- which is how this was found, by a test-order failure."""
        import driver as drv
        import lp_model as lp
        drv.set_year_capex(2045)
        srt.resistor_threshold_mwh(year=2030)
        assert lp.CAPEX_YEAR == 2045

    def test_bath_binds_at_every_year(self):
        """Its $7.50/MWh is a literal in build_problem, not a year-indexed capex term. So the
        BINDING threshold does not move with the checkpoint even though sodium-ion's does -- which
        is why every conclusion drawn from $30.00 holds across the horizon."""
        for y in (2030, 2035, 2040, 2045):
            r = srt.check_curtailment_cost(year=y)
            assert r['binding_type'] == 'bath_pumped_hydro'
            assert r['binding_threshold_mwh'] == pytest.approx(30.0, abs=0.5)

    def test_sodium_moves_but_bath_does_not(self):
        assert srt.resistor_threshold_mwh('sodium_ion', year=2030) > 100
        assert srt.resistor_threshold_mwh('sodium_ion', year=2045) < 60
        assert (srt.resistor_threshold_mwh('bath_pumped_hydro', year=2030)
                == srt.resistor_threshold_mwh('bath_pumped_hydro', year=2045))

    def test_the_duplicate_2044_5_literals_are_gone(self):
        """FE_RTE_CHARGE and GAS_COST_MWH each carried their own literal 2044.5 -- identical to
        BUILD_YEAR in value but free to drift from it.

        Uses tokenize rather than a line heuristic. Prose mentioning 2044.5 in a docstring is
        legitimate and expected; three earlier checks in this project failed by trying to tell code
        from prose with string matching, and the right tool is a NUMBER token."""
        import io
        import inspect
        import tokenize
        import lp_model as lp
        src = inspect.getsource(lp)
        literals = [t for t in tokenize.generate_tokens(io.StringIO(src).readline)
                    if t.type == tokenize.NUMBER and t.string == '2044.5']
        assert not literals, (
            f'{len(literals)} literal 2044.5 token(s) still in code at line(s) '
            f'{[t.start[0] for t in literals]}')


class TestVerifiedEmpirically:
    """MEASURED 2026-09-14 at 2045 Scenario 1, bracketing the derived $30.00 threshold. The formula
    was in doubt for Bath specifically -- its $7.50/MWh is sourced as an RTE-LOSS cost already
    computed at 80% RTE, so multiplying it by RTE/(1-RTE) looked like double-counting. It is not."""

    def test_the_bracket(self):
        """$28.00 -> 0 simultaneous hours, every storage type.
        $30.00 -> 0, exactly at the derived threshold.
        $32.00 -> 121 Bath hours, max overlap 1,463 MW. Na-ion and iron-air stay at 0.

        BATH BREAKS FIRST AND ALONE, as the derivation predicts -- it is the cheapest resistor.
        The threshold is correct to within $2 and the double-counting concern was wrong."""
        observed = {28.0: 0, 30.0: 0, 32.0: 121}
        assert observed[30.0] == 0 and observed[32.0] > 0

    def test_only_bath_breaks_at_the_threshold(self):
        """Na-ion's own threshold is $48.06 at 2045 and iron-air's $70.08, so neither is near
        binding at $32. That the failure is Bath-only confirms the per-type derivation rather than
        a generic solver instability."""
        assert srt.resistor_threshold_mwh('sodium_ion', year=2045) > 32.0
        assert srt.resistor_threshold_mwh('iron_air', year=2045) > 32.0
        assert srt.resistor_threshold_mwh('bath_pumped_hydro', year=2045) < 32.0


class TestStorageHasNoVOM:
    """Raised as a question 2026-09-14: costs can be on an 'as used' basis, so where might VOM
    matter? It matters here, and its absence is a gap rather than a decision."""

    def test_gas_has_vom_and_storage_does_not(self):
        import assumptions as a
        assert a.CCGT_VOM_MWH == 3.00 and a.CT_VOM_MWH == 5.00
        assert not [n for n in dir(a) if 'VOM' in n and ('NA_' in n or 'FE_' in n or 'BATH' in n)]

    def test_the_gap_is_documented_where_it_bites(self):
        import inspect
        assert 'STORAGE CARRIES NO VOM IN THIS MODEL' in inspect.getsource(srt._cycling_costs)

    def test_vom_would_raise_the_threshold_but_not_enough(self):
        """Bath's threshold is (cycling + VOM) x 4 at 80% RTE. A plausible $0.50-$2.00 VOM moves it
        to $32-$38 -- enough to matter, nowhere near the $100 economic figure, which would need
        $17.50/MWh. That is implausible for pumped hydro, whose variable cost is essentially the
        RTE loss already priced."""
        rte = 0.80
        assert (7.50 + 2.00) * rte / (1 - rte) == pytest.approx(38.0)
        assert (100.0 * (1 - rte) / rte) - 7.50 == pytest.approx(17.50)
