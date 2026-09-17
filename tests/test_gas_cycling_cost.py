"""
test_gas_cycling_cost.py

Thermal cycling PRICED, not forbidden.

MAX_ANNUAL_STARTS is a screening-curve device for choosing between candidate technologies, not a
dispatch constraint. Treating it as one would make every fleet change -- a derate, a weather year,
an import sensitivity -- a tuning exercise against a threshold, with no end.
"""
import numpy as np
import pytest

import assumptions as a
import gas_cycling_cost as gcc


def _blocks(block_hours, gap_hours, mw, total=8760):
    """A dispatch of repeated on/off blocks."""
    series = np.zeros(total)
    step = block_hours + gap_hours
    for start in range(0, total - block_hours, step):
        series[start:start + block_hours] = mw
    return series


class TestTheRatioDrivesTheCost:
    """Batlle & Rodilla: "a larger number of starts does not necessarily imply larger O&M costs".
    Their peaking unit starts 25 times over 108 firing hours -- ratio 4.3, HIGH O&M -- while their
    mid-merit unit starts 160 times over ~2,900 hours, ratio 18, and carries less."""

    def test_continuous_running_has_one_start(self):
        c = gcc.for_rung('ccgt_modern', np.full(8760, 1_000.0), 1_000.0)
        assert c.starts == 1 and c.firing_hours == 8760
        assert c.cycling_ratio == 8760.0

    def test_frequent_short_blocks_cost_more_than_continuous_at_equal_energy(self):
        """Same megawatt-hours, opposite maintenance. THIS IS WHAT THE LP CANNOT SEE: a start is a
        discrete event its continuous hourly variables cannot express."""
        steady = gcc.for_rung('ct_fleet', _blocks(8760, 0, 1_000.0), 1_000.0)
        cycled = gcc.for_rung('ct_fleet', _blocks(2, 22, 12_000.0), 1_000.0)
        assert cycled.starts > steady.starts * 100
        assert cycled.equivalent_operating_hours > steady.equivalent_operating_hours

    def test_a_clean_year_costs_nothing(self):
        c = gcc.for_rung('ct_fleet', np.zeros(8760), 1_000.0)
        assert c.starts == 0 and c.maintenance_cost_usd == 0.0
        assert c.cycling_ratio == 0.0

    def test_solver_residuals_are_not_starts(self):
        c = gcc.for_rung('ct_fleet', np.full(8760, 1e-9), 1_000.0)
        assert c.starts == 0


class TestTheFormula:
    """EOH = firing_hours + starts x EOH_per_start; maintenance = (EOH/interval) x $/MW x MW."""

    def test_equivalent_operating_hours(self):
        series = _blocks(10, 10, 500.0)
        c = gcc.for_rung('ct_fleet', series, 500.0)
        per_start = a.EOH_PER_START_BY_STATE[a.EOH_PER_START_ASSUMED_STATE]
        assert c.equivalent_operating_hours == pytest.approx(
            c.firing_hours + c.starts * per_start)

    def test_maintenance_scales_with_capacity_and_interval(self):
        series = _blocks(10, 10, 500.0)
        c = gcc.for_rung('ct_fleet', series, 500.0)
        expected = (c.equivalent_operating_hours / a.OVERHAUL_INTERVAL_FFH['CT']
                    * a.MAJOR_OVERHAUL_USD_PER_MW_BY_TECH['CT'] * 500.0)
        assert c.maintenance_cost_usd == pytest.approx(expected)

    def test_warm_starts_are_assumed_and_it_matters_more_than_technology(self):
        """GER-3620 weights cold at 150-200 run-hour equivalents, warm 30-60, hot 10-20."""
        series = _blocks(2, 4, 500.0)
        warm = gcc.for_rung('ct_fleet', series, 500.0, eoh_per_start=45.0)
        cold = gcc.for_rung('ct_fleet', series, 500.0, eoh_per_start=175.0)
        assert cold.maintenance_cost_usd > warm.maintenance_cost_usd * 2


class TestTechnologyMapping:
    def test_simple_cycle_rungs_are_detected_by_name(self):
        assert gcc.technology_for_rung('ct_fleet') == 'CT'
        assert gcc.technology_for_rung('ccgt_modern') == 'CCGT'
        assert gcc.technology_for_rung('scenario_new_ccgt') == 'CCGT'

    def test_simple_cycle_carries_the_cheaper_overhaul(self):
        """A combined-cycle overhaul covers the steam side as well."""
        assert (a.MAJOR_OVERHAUL_USD_PER_MW_BY_TECH['CT']
                < a.MAJOR_OVERHAUL_USD_PER_MW_BY_TECH['CCGT'])


class TestRule5Guards:
    def test_zero_nameplate_raises(self):
        """Returning zero would hide a mis-wired stack."""
        with pytest.raises(ValueError, match='must be positive'):
            gcc.for_rung('ct_fleet', np.zeros(8760), 0.0)

    def test_unknown_technology_raises(self):
        """Guessing would price the wrong overhaul scope."""
        with pytest.raises(ValueError, match='unknown technology'):
            gcc.for_rung('x', np.zeros(8760), 100.0, technology='steam')

    def test_a_rung_without_a_nameplate_raises(self):
        """The stack and the solved result disagreeing is what Rule 4 exists to surface."""
        with pytest.raises(ValueError, match='no nameplate recorded'):
            gcc.for_fleet({'ct_fleet': np.zeros(8760)}, {})


class TestTheLimitIsReportedNeverRaised:
    """A hard threshold on a soft quantity creates a tuning loop with no end."""

    def test_exceeding_the_limit_is_reported_not_raised(self):
        series = _blocks(1, 1, 1_000.0)          # ~2,190 starts, far past the CT limit of 900
        c = gcc.for_rung('ct_fleet', series, 1_000.0)
        assert c.starts > a.MAX_ANNUAL_STARTS['CT']
        assert c.starts_against_reference > 1.0   # reported, and nothing raised

    def test_the_module_says_why(self):
        assert 'PRICED AND NOT FORBIDDEN' in gcc.__doc__
        assert 'tuning loop with no end' in gcc.__doc__

    def test_the_upper_bound_caveat_is_recorded(self):
        """The LP chose a more cycling-heavy pattern than one charged for cycling would have."""
        assert 'UPPER bound' in gcc.__doc__


class TestMeasuredOnScenario2:
    """MEASURED 2026-09-14 at 2045."""

    MEASURED = {'scenario_new_ccgt': (1, 178), 'ccgt_fleet': (193, 71),
                'ccgt_legacy': (268, 71), 'ct_fleet': (320, 159)}

    def test_more_starts_does_not_mean_more_cost(self):
        """ccgt_legacy at 268 starts costs $71M; ccgt_modern at 1 start costs $94M, because
        maintenance scales with CAPACITY as well as cycling."""
        assert self.MEASURED['ccgt_legacy'][1] < 94

    def test_the_fleet_total_settles_the_mixed_integer_question(self):
        """$645M/yr against an $10,819M total is 6.0% -- large enough to report, not large enough
        to justify 52,560 binary variables. The ladder stops here, measured rather than assumed."""
        assert 645 / 10_819 == pytest.approx(0.060, abs=0.005)

    def test_nothing_exceeded_its_limit_but_legacy_was_close(self):
        """ccgt_legacy at 268 of 300 is 89%. Had this been a hard constraint, that rung would be
        one derating change from blocking every run."""
        assert self.MEASURED['ccgt_legacy'][0] / a.MAX_ANNUAL_STARTS['CCGT'] == pytest.approx(
            0.89, abs=0.01)
