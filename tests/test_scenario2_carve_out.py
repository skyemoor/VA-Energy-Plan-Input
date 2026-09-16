"""
test_scenario2_carve_out.py

The C.2 distributed carve-out inside Scenario 2.

SCENARIO 2'S LOGIC IS ITS OWN. It splits a FIXED total, because the 16,100 MW cap is what defines
the scenario. Scenarios 1, 1B and 3 build to meet a compliance target, so the carve-out there is a
FLOOR on distributed within whatever total the LP chooses -- not a slice of a fixed number.
"""
import numpy as np
import pytest

import assumptions as a
import checkpoint_solver as cs
import demand_basis as db
import lp_model as lp
import paths
import rps_compliance as rc


def _solver(year):
    w = np.load(paths.weather_year('hydro_year1_2016_17_RECONSTRUCTED.npz'))
    return cs.Scenario2Solver(
        year=year, demand=db.VirginiaOnlyGeneration(year).hourly_mw(),
        exist_solar=lp.exist_solar_mw(year) * w['solar'], solar_cf=w['solar'],
        wind_cf=w['wind'], nuclear=w['nuclear'], vcea_solar_mw=16_100.0)


class TestTheStatutorySchedule:
    """Va. Code 56-585.5(C)(1)(a), Phase II column."""

    def test_dominion_is_phase_ii(self):
        """I FIRST USED THE PHASE I COLUMN, which is the smaller utilities: 45% against 59% at
        2035, 80% against 100% at 2045."""
        assert rc.phase_ii_rps_share(2035) == 0.59
        assert rc.phase_ii_rps_share(2045) == 1.00

    def test_it_is_tabulated_not_interpolated(self):
        """I ALSO INTERPOLATED between milestone years. The schedule is not linear -- Phase II steps
        3 points a year to 2030 then 4 from 2031, and Phase I repeats 53% at both 2036 and 2037.
        Interpolation gives plausible wrong numbers at every year between."""
        assert rc.phase_ii_rps_share(2030) == 0.41
        assert rc.phase_ii_rps_share(2031) == 0.45      # a 4-point step, not 3
        assert len(rc.PHASE_II_RPS_SCHEDULE) == 25

    def test_it_holds_at_100_percent_after_2045(self):
        assert rc.phase_ii_rps_share(2050) == 1.00

    def test_extrapolating_backwards_raises(self):
        """Rule 5. The Code sets no obligation before 2021."""
        with pytest.raises(ValueError, match='precedes the statutory schedule'):
            rc.phase_ii_rps_share(2019)


class TestTheBase:
    def test_energy_sold_divides_by_the_loss_factor(self):
        """Va. Code 56-585.5(C): the requirement is a percentage of energy SOLD in the previous
        calendar year. Sold means metered, so the generation series divides by 1.0925.

        THE SAME SERIES IS USED UNDIVIDED FOR DISPATCH, because the hourly file already carries the
        gross-up. Same number, opposite treatment, both correct."""
        assert a.TRANSMISSION_LOSS_FACTOR == 1.0925

    def test_it_uses_the_prior_year(self):
        """'in the previous calendar year' -- which matters in a growing system: the 2045
        requirement rests on 2044's energy."""
        import inspect
        assert 'year - 1' in inspect.getsource(cs.Scenario2Solver.carve_out_mw)

    def test_it_is_not_circular(self):
        """The base is energy sold, which the demand series gives independently of what the
        scenario builds -- so the carve-out is computable even though Scenario 2 does not meet the
        RPS at all."""
        assert _solver(2045).carve_out_mw() > 0


class TestTheSplitAppliesToNewBuild:
    """CAUGHT BY THE RESULT MOVING THE WRONG WAY. Splitting the 16,100 MW itself and passing both
    parts to the builder added the existing fleet on top -- total solar 20,918 MW rather than
    16,100 -- and clean share ROSE when it should have fallen. Had it moved the right way by a
    plausible amount, it would have been accepted."""

    def test_vcea_new_solar_mw_is_already_net_of_existing(self):
        assert a.vcea_new_solar_mw(2045, 16_100.0) == pytest.approx(11_445, abs=1)
        assert lp.exist_solar_mw(2045) == pytest.approx(4_819, abs=1)

    def test_the_split_sums_to_new_build(self):
        for year in (2030, 2035, 2040, 2045):
            nb = a.vcea_new_solar_mw(year, 16_100.0)
            dist, util = _solver(year).solar_split_mw(new_build_mw=nb)
            assert dist + util == pytest.approx(nb)

    def test_the_carve_out_cannot_exceed_new_build(self):
        """If it did, the obligation could not be met from new build alone -- which the cap
        assumption forbids."""
        for year in (2030, 2045):
            nb = a.vcea_new_solar_mw(year, 16_100.0)
            dist, _ = _solver(year).solar_split_mw(new_build_mw=nb)
            assert dist <= nb


class TestMeasuredTrajectory:
    """MEASURED 2026-09-14."""

    EXPECTED = {2030: 1_432, 2035: 2_856, 2040: 4_924, 2045: 6_862}

    @pytest.mark.parametrize('year', sorted(EXPECTED))
    def test_carve_out_capacity(self, year):
        assert _solver(year).carve_out_mw() == pytest.approx(self.EXPECTED[year], rel=0.01)

    def test_it_reaches_60_percent_of_new_build_by_2045(self):
        """6,862 of 11,445 MW, leaving 4,583 MW of utility-scale new build. The two statutory
        obligations genuinely squeeze each other under the cap assumption."""
        nb = a.vcea_new_solar_mw(2045, 16_100.0)
        assert self.EXPECTED[2045] / nb == pytest.approx(0.60, abs=0.01)

    def test_it_lowers_the_clean_share(self):
        """MEASURED: 34.7% to 32.5% at 2045, gas 127 to 136 TWh. Distributed delivers a 0.1526
        capacity factor against utility tracking's 0.2252, so 6,862 MW gives 9.2 TWh where the same
        capacity tracking would give 13.5 -- about 4.4 TWh lost."""
        import distributed_solar_profile as dsp
        assert dsp.DESIGN_YEAR_CAPACITY_FACTOR < 0.2252


class TestTheCapIsAnAssumption:
    def test_it_is_labelled_as_one(self):
        assert a.SCENARIO2_TOTAL_SOLAR_CAP_MW == 16_100.0
        assert 'assumed to hold' in a.SCENARIO2_SOLAR_CAP_IS_AN_ASSUMPTION

    def test_the_reason_the_code_does_not_settle_it(self):
        """D.2 is a one-time capacity target due 2035; C.2 is a growing annual energy obligation
        reaching about 6,862 MW equivalent by 2045. The Code does not say whether the excess is
        built on top of the target or absorbed within it."""
        assert 'does not say' in a.SCENARIO2_SOLAR_CAP_IS_AN_ASSUMPTION

    def test_the_consequence_is_recorded(self):
        """Holding the cap means utility-scale falls from about 13,244 MW at 2035 to 9,238 MW at
        2045 -- not a choice a utility would make voluntarily."""
        import re
        src = re.sub(r'\s+', ' ', open(a.__file__).read())
        assert 'not a choice a utility would make voluntarily' in src
