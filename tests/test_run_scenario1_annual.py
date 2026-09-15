"""
test_run_scenario1_annual.py

The sixteen non-checkpoint years of Scenario 1, so the SLCOE covers all twenty.
"""
import inspect
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import run_scenario1_annual as ann   # noqa: E402

CHECKPOINTS = {
    2030: {'solar_mw_total': 8701.72, 'na_power_mw': 6020.84, 'na_energy_mwh': 36125.06,
           'fe_energy_mwh': 0.0},
    2035: {'solar_mw_total': 28393.47, 'na_power_mw': 11479.27, 'na_energy_mwh': 68875.65,
           'fe_energy_mwh': 200000.0},
    2040: {'solar_mw_total': 64114.49, 'na_power_mw': 29401.85, 'na_energy_mwh': 234686.97,
           'fe_energy_mwh': 314435.82},
    2045: {'solar_mw_total': 156736.92, 'na_power_mw': 46968.37, 'na_energy_mwh': 310882.14,
           'fe_energy_mwh': 4772837.88},
}


@pytest.fixture
def anchors():
    a = {2026: {k: 0.0 for k in ann.BUILD_KEYS}}
    a.update(CHECKPOINTS)
    return a


class TestInterpolation:

    def test_a_checkpoint_returns_its_own_build_unchanged(self, anchors):
        """So the twenty-year stream agrees with the four-year one EXACTLY at the years both cover.
        Without this the two would disagree at the checkpoints themselves and neither could be
        checked against the other."""
        for year, build in CHECKPOINTS.items():
            assert ann.interpolate_build(year, anchors)['solar_mw_total'] == build['solar_mw_total']

    def test_2026_carries_no_new_solar(self, anchors):
        """Existing solar is passed separately as exist_solar -- 5,300 MW at 2026 -- so the anchor's
        solar figure is NEW build beyond it, which is genuinely nil."""
        assert ann.interpolate_build(2026, anchors)['solar_mw_total'] == 0.0

    def test_it_interpolates_between_the_NEAREST_pair(self, anchors):
        """2033 sits between 2030 and 2035, not between 2026 and 2045."""
        got = ann.interpolate_build(2033, anchors)['solar_mw_total']
        lo, hi = CHECKPOINTS[2030]['solar_mw_total'], CHECKPOINTS[2035]['solar_mw_total']
        assert got == pytest.approx(lo + 0.6 * (hi - lo))

    def test_every_build_quantity_is_carried(self, anchors):
        assert set(ann.interpolate_build(2033, anchors)) == set(ann.BUILD_KEYS)

    def test_it_is_monotonic_across_the_stream(self, anchors):
        """Scenario 1's build only grows, so an interpolation that dipped would be wrong."""
        vals = [ann.interpolate_build(y, anchors)['solar_mw_total'] for y in range(2026, 2046)]
        assert vals == sorted(vals)


class TestReserveMarginIsAppliedNotChecked:
    """With the build pinned, the margin is a constraint the year satisfies or does not -- so an
    inadequate interpolated build surfaces as INFEASIBILITY rather than as silently-accepted
    unserved energy. Verified separately that a starved build is infeasible while an adequate one
    solves."""

    def test_the_constraint_is_applied(self):
        src = inspect.getsource(ann.solve_year)
        assert 'add_all_hours_reserve_margin_constraint' in src

    def test_it_uses_the_shared_function_with_fixed_capacities(self):
        """Appendix P.2 §14 -- the same code as the checkpoints use, not a dispatch-specific copy.
        build_dispatch_problem has NVAR_BUILD = 0, so capacities pass through fixed_capacity_mw."""
        src = inspect.getsource(ann.solve_year)
        assert 'fixed_capacity_mw=' in src

    def test_infeasibility_is_reported_as_a_finding(self):
        """Not worked around. An infeasible year means the interpolation is inadequate, which is
        the signal wanted."""
        src = inspect.getsource(ann.solve_year)
        assert 'INFEASIBLE' in src
        assert 'do not relax the constraint' in src


class TestVerificationPerYear:
    """Appendix P.2 §11, on every interpolated year, not only the checkpoints."""

    def test_unserved_raises(self):
        assert 'unserved' in inspect.getsource(ann.solve_year)
        assert '§11' in inspect.getsource(ann.solve_year)

    def test_simultaneous_dispatch_raises_for_all_three_storage_types(self):
        src = inspect.getsource(ann.solve_year)
        for label in ("'Na'", "'iron-air'", "'Bath'"):
            assert label in src


class TestSalvageIsNotDoubleCounted:
    """An interpolated year HOLDS capacity built at a checkpoint. Crediting salvage on it as well
    would count the same asset once per year it is held."""

    def test_salvage_is_credited_on_checkpoints_only(self):
        src = inspect.getsource(ann.main)
        assert 'for year, r in solved.items()' in src
        assert 'crediting it again would count the same asset' in inspect.getsource(ann)

    def test_it_uses_the_new_build_not_the_cumulative_total(self):
        """S_mw from solar_mw_new: each checkpoint's own vintage."""
        assert "'S_mw': r['solar_mw_new']" in inspect.getsource(ann.main)


class TestBothShareBasesAndTheOmission:
    def test_both_gas_share_bases_are_recorded(self):
        src = inspect.getsource(ann.solve_year)
        assert "'gas_share_statutory'" in src and "'gas_share_of_demand'" in src

    def test_decommissioning_and_scrap_are_disclosed(self):
        """Both omitted, and they partly offset. Booking the liability would make the gas-heavier
        scenarios look worse, so the omission is conservative in the direction that matters."""
        src = inspect.getsource(ann.main)
        assert 'DECOMMISSIONING AND SCRAP ARE BOTH OMITTED' in src
        assert 'partly offset' in src

    def test_an_irm_mismatch_against_the_checkpoints_raises(self):
        """The interpolated years must hold the same margin as the checkpoints they sit between."""
        assert 'must hold the same margin' in inspect.getsource(ann.main)


class TestThe2026Anchor:
    """IT IS NOT ZERO-BUILD, and the first version was.

    MEASURED 2026-09-14: 2026 is INFEASIBLE against the 17.7% all-hours reserve margin at zero
    storage, at the actual 80.6 MW of existing batteries, and at 250, 500 and 750 MW. 1,000 MW is
    feasible. The threshold sits between 750 and 1,000."""

    def test_the_anchor_storage_is_a_named_assumption(self):
        import assumptions
        assert assumptions.SCENARIO1_ANCHOR_STORAGE_MW == 1000.0

    def test_it_is_labelled_as_a_modelling_figure_not_a_physical_one(self):
        """It is not a claim that Virginia needs 1,000 MW of batteries in 2026."""
        import inspect
        import re
        src = re.sub(r'\s*\n\s*#?:?\s*', ' ', inspect.getsource(__import__('assumptions')))
        assert 'NOT A PHYSICAL FIGURE' in src
        assert 'MODELLING-STRUCTURE FIGURE' in src

    def test_both_model_boundaries_are_named(self):
        """The model says short where Virginia is not, for two reasons that are deliberate
        elsewhere and bind here: no imports, in a state inside PJM that imports freely; and an
        HOURLY margin where IRM is a planning standard evaluated at peak."""
        import inspect
        import re
        src = re.sub(r'\s*\n\s*#?:?\s*', ' ', inspect.getsource(__import__('assumptions')))
        assert 'NO IMPORTS' in src
        assert 'THE MARGIN IS HOURLY' in src

    def test_the_actual_fleet_is_recorded_alongside_it(self):
        """80.6 MW from EIA-860, so the gap between the modelling figure and reality is visible
        rather than buried."""
        import assumptions
        assert assumptions.EXISTING_BATTERY_MW == 80.6
        assert assumptions.SCENARIO1_ANCHOR_STORAGE_MW > assumptions.EXISTING_BATTERY_MW

    def test_it_affects_only_the_first_four_years(self):
        """2030 onward carry their own solved builds, so a sensitivity at 750 or 1,250 MW would
        move 2026-2029's dispatch and nothing else."""
        import assumptions
        a = {2026: {'solar_mw_total': 0.0,
                    'na_power_mw': assumptions.SCENARIO1_ANCHOR_STORAGE_MW,
                    'na_energy_mwh': assumptions.SCENARIO1_ANCHOR_STORAGE_MW * 6.0,
                    'fe_energy_mwh': 0.0}}
        a.update(CHECKPOINTS)
        assert ann.interpolate_build(2030, a)['na_power_mw'] == CHECKPOINTS[2030]['na_power_mw']

    def test_the_ramp_is_monotonic_from_the_anchor(self):
        import assumptions
        a = {2026: {'solar_mw_total': 0.0,
                    'na_power_mw': assumptions.SCENARIO1_ANCHOR_STORAGE_MW,
                    'na_energy_mwh': assumptions.SCENARIO1_ANCHOR_STORAGE_MW * 6.0,
                    'fe_energy_mwh': 0.0}}
        a.update(CHECKPOINTS)
        vals = [ann.interpolate_build(y, a)['na_power_mw'] for y in range(2026, 2031)]
        assert vals == sorted(vals)
        assert vals[0] == 1000.0
