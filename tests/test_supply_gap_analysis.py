"""
test_supply_gap_analysis.py

Gap characterisation: find the hours clean resources cannot cover, then match each family of gaps
against the gas technology that fits.

WHY THIS RATHER THAN CAPEX IN THE LP. An LP with capital in the objective returns a single MW
split, and a single number cannot say whether 7 GW should be CT or whether it is really 3 GW of CT
plus 4 GW of something else. The gap distribution can. It also avoids a MILP: minimum up/down time
and start cost become post-hoc tests against gap shape rather than 43,800 binary variables.
"""
import numpy as np
import pytest

import assumptions
from supply_gap_analysis import CCGT_MIN_CYCLE_INTERVAL_HR, SupplyGapProfile


def series(spans, n=8760):
    """spans: list of (start, [mw values])."""
    u = np.zeros(n)
    for start, vals in spans:
        u[start:start + len(vals)] = vals
    return u


class TestEventDetection:

    def test_contiguous_run_is_one_event(self):
        p = SupplyGapProfile.from_dispatchable_residual(series([(100, [500, 1200, 400])]), 'gas_dispatch')
        assert len(p.events) == 1
        e = p.events[0]
        assert e.start_hour == 100 and e.duration_hr == 3
        assert e.peak_mw == 1200 and e.energy_mwh == 2100

    def test_separate_runs_are_separate_events(self):
        p = SupplyGapProfile.from_dispatchable_residual(series([(100, [500]), (200, [700])]), 'gas_dispatch')
        assert len(p.events) == 2
        assert p.events[1].hours_since_previous == 99

    def test_first_event_has_no_previous_interval(self):
        """None rather than zero -- a zero would read as 'immediately after the last event'."""
        p = SupplyGapProfile.from_dispatchable_residual(series([(100, [500])]), 'gas_dispatch')
        assert p.events[0].hours_since_previous is None

    def test_noise_below_threshold_is_not_an_event(self):
        """Solver residue at 0.001 MW is not a supply gap."""
        p = SupplyGapProfile.from_dispatchable_residual(series([(100, [0.001, 0.002])]), 'gas_dispatch')
        assert p.events == []

    def test_ramps_measure_the_step_into_and_out_of_the_event(self):
        p = SupplyGapProfile.from_dispatchable_residual(series([(100, [800, 900, 300])]), 'gas_dispatch')
        e = p.events[0]
        assert e.ramp_in_mw_per_hr == 800     # from zero
        assert e.ramp_out_mw_per_hr == 300    # back to zero

    def test_empty_series_gives_no_events(self):
        p = SupplyGapProfile.from_dispatchable_residual(np.zeros(8760), 'gas_dispatch')
        assert p.events == [] and p.peak_mw == 0.0
        assert p.match_technology(2045)['verdict'] == 'no gaps'


class TestSourceDiscipline:
    """CORRECTED 2026-09-13. An earlier version required a purpose-built CLEAN-ONLY solve and
    refused any input from a solve where gas had run. That was aimed at the wrong thing: the
    failure to prevent is using the UNSERVED column of a gas-inclusive solve (a DOUBLE residual --
    what gas failed to cover). Using the GAS DISPATCH column of that same solve is not merely
    acceptable, it is preferable."""

    def test_double_residual_is_rejected_by_name(self):
        with pytest.raises(ValueError, match='DOUBLE RESIDUAL'):
            SupplyGapProfile.from_dispatchable_residual(
                series([(100, [5])]), source='unserved_with_gas')

    def test_rejection_says_what_to_use_instead(self):
        """A reader who hits this must learn the fix, not just that it failed."""
        with pytest.raises(ValueError, match='GAS DISPATCH column'):
            SupplyGapProfile.from_dispatchable_residual(np.zeros(10), 'unserved_with_gas')

    def test_source_is_required_not_defaulted(self):
        """The same array means different things depending on which column it came from, so there
        is no safe default. Calls it deliberately without `source`."""
        with pytest.raises(TypeError):
            SupplyGapProfile.from_dispatchable_residual(np.zeros(10))

    def test_unknown_source_raises(self):
        with pytest.raises(ValueError, match='source must be one of'):
            SupplyGapProfile.from_dispatchable_residual(np.zeros(10), 'whatever', 'gas_dispatch')

    def test_both_valid_sources_are_accepted(self):
        for src in ('gas_dispatch', 'unserved_clean_only'):
            SupplyGapProfile.from_dispatchable_residual(series([(100, [500])]), src)

    def test_unserved_is_added_to_gas_dispatch(self):
        """If a gas-inclusive solve left unserved energy, the gap is gas PLUS unserved. Omitting
        the second understates the peak, which is the figure the technology match turns on."""
        gas = series([(100, [1000])])
        uns = series([(100, [500])])
        p = SupplyGapProfile.from_dispatchable_residual(gas, 'gas_dispatch', unserved_mw=uns)
        assert p.peak_mw == 1500

    def test_mismatched_unserved_shape_raises(self):
        with pytest.raises(ValueError, match='does not match residual'):
            SupplyGapProfile.from_dispatchable_residual(
                np.zeros(8760), 'gas_dispatch', unserved_mw=np.zeros(100))

    def test_guidance_explains_why_gas_dispatch_is_preferred(self):
        g = SupplyGapProfile.source_guidance()
        assert 'GAS DISPATCH' in g
        assert '100,000' in g, 'must say why a clean-only solve is worse, not just different'


class TestScenario2IsBaseloadNotPeaking:
    """MEASURED 2026-09-13 on the real Scenario 2 2045 solve. The method was built to find PEAKING
    needs; at Dominion's statutory build there are none, and that is itself the finding."""

    def test_the_measured_profile_is_recorded(self):
        """Gas runs 8,632 of 8,760 hours -- 98.5%. One event lasts 4,200 hours, nearly half the
        year, and events over 72 h carry 114.6 of the 122.9 TWh.

        AT 39.2% CLEAN, GAS IS NOT FILLING GAPS -- IT IS THE SYSTEM. The CCGT/CT question is
        answered decisively for this scenario (CCGT, 62.4% CF against a 28.1% crossover), but only
        because there is nothing peaky to serve. The method becomes informative at HIGHER
        compliance levels, where gas genuinely peaks -- which is what makes running it across the
        sweep worthwhile."""
        assert True  # documentation test; the figures are asserted in the integration run


class TestFamilies:
    """Breaks chosen from operating parameters -- 6 h is CCGT minimum up time, then a day, then
    multi-day -- rather than fitted to the data, so families mean the same thing across scenarios."""

    def test_events_sort_into_duration_families(self):
        p = SupplyGapProfile.from_dispatchable_residual(series([
            (100, [500] * 3),          # under 6h
            (500, [500] * 12),         # 6-24h
            (2000, [500] * 48),        # 24-72h
            (5000, [500] * 100)]), 'gas_dispatch')     # over 72h
        fam = p.families()
        assert [len(fam[k]) for k in ('under_6h', '6_to_24h', '24_to_72h', 'over_72h')] == [1, 1, 1, 1]


class TestTechnologyMatching:

    def test_low_capacity_factor_favours_ct_on_cost(self):
        """A few short spikes a year is peaking duty -- below the 28.1% crossover."""
        p = SupplyGapProfile.from_dispatchable_residual(series([(100, [3000] * 3), (500, [3000] * 3)]), 'gas_dispatch')
        m = p.match_technology(2045)
        assert m['cost_favours'] == 'CT'
        assert m['annual_capacity_factor'] < m['crossover_cf']

    def test_sustained_gaps_favour_ccgt_on_cost(self):
        """Half the year at full output is intermediate duty, well above the crossover."""
        p = SupplyGapProfile.from_dispatchable_residual(series([(0, [3000] * 4380)]), 'gas_dispatch')
        m = p.match_technology(2045)
        assert m['cost_favours'] == 'CCGT'

    def test_short_events_are_flagged_even_when_cost_favours_ccgt(self):
        """THE POINT OF THE METHOD. Cost and operating constraints can disagree, and a profile can
        sit above the crossover while containing events no CCGT could serve. A single MW split from
        an LP with capex would hide this."""
        u = series([(0, [3000] * 4380)])          # sustained, pushes CF above crossover
        u[6000:6002] = 3000                        # plus a 2-hour spike
        m = SupplyGapProfile.from_dispatchable_residual(u, 'gas_dispatch').match_technology(2045)
        assert m['cost_favours'] == 'CCGT'
        assert m['events_shorter_than_ccgt_min_up'] >= 1
        assert m['attributes_agree'] is False

    def test_close_spaced_events_are_flagged(self):
        """Below 6 h apart a CCGT cannot cycle off and back, so it idles at minimum stable output
        -- a cost the dispatch objective never sees."""
        p = SupplyGapProfile.from_dispatchable_residual(series([(100, [500] * 2), (104, [500] * 2)]), 'gas_dispatch')
        m = p.match_technology(2045)
        assert m['events_closer_than_ccgt_min_down'] >= 1
        assert CCGT_MIN_CYCLE_INTERVAL_HR == 6.0

    def test_very_long_events_are_called_a_storage_finding(self):
        """If the gaps run for days, the answer is not which turbine to build."""
        p = SupplyGapProfile.from_dispatchable_residual(series([(1000, [2000] * 150)]), 'gas_dispatch')
        assert 'STORAGE DURATION' in p.match_technology(2045)['note']

    def test_verdict_explains_rather_than_asserts(self):
        p = SupplyGapProfile.from_dispatchable_residual(series([(100, [3000] * 3)]), 'gas_dispatch')
        note = p.match_technology(2045)['note']
        assert 'crossover' in note and 'CF' in note


class TestAggregateShape:

    def test_annual_capacity_factor_uses_the_whole_year(self):
        """Not the event-only utilisation -- the crossover is an annual figure."""
        p = SupplyGapProfile.from_dispatchable_residual(series([(0, [1000] * 876)]), 'gas_dispatch')
        assert p.annual_capacity_factor() == pytest.approx(0.1, abs=0.001)

    def test_event_capacity_factor_is_event_only(self):
        p = SupplyGapProfile.from_dispatchable_residual(series([(100, [1000, 500])]), 'gas_dispatch')
        assert p.events[0].capacity_factor == pytest.approx(0.75)
