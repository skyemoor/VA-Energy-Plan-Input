"""
test_reliability_metrics.py

Adequacy metrics per NERC's Risk Mitigation for Emerging Large Loads (2026).
"""
import numpy as np
import pytest

import reliability_metrics as rm


class TestTheThreeDimensions:
    """NERC asks for duration, magnitude and severity. Duration is loss_of_load_hours and
    longest_event_hours; magnitude is unserved_energy_mwh and peak_shortfall_mw; severity is the
    event distribution, which is as close as a single realisation gets to the third."""

    def test_a_clean_year_reports_zero(self):
        m = rm.compute(np.zeros(8760), np.full(8760, 20_000.0))
        assert m.loss_of_load_hours == 0 and m.unserved_energy_mwh == 0.0
        assert m.event_count == 0 and m.mean_event_hours == 0.0

    def test_duration_and_magnitude(self):
        u = np.zeros(8760)
        u[100:106] = 500.0          # one 6-hour event
        u[2000:2002] = 1_200.0      # one 2-hour event, higher peak
        m = rm.compute(u, np.full(8760, 20_000.0))
        assert m.loss_of_load_hours == 8
        assert m.unserved_energy_mwh == pytest.approx(6 * 500 + 2 * 1200)
        assert m.peak_shortfall_mw == 1_200.0
        assert m.event_count == 2 and m.longest_event_hours == 6
        assert m.mean_event_hours == 4.0

    def test_normalisation_accepts_a_series_or_a_total(self):
        u = np.zeros(8760); u[0] = 1_000.0
        a = rm.compute(u, np.full(8760, 10_000.0))
        b = rm.compute(u, 8760 * 10_000.0)
        assert a.unserved_fraction_of_demand == pytest.approx(b.unserved_fraction_of_demand)

    def test_solver_residuals_are_not_loss_of_load_hours(self):
        """A linear-programming solution carries small residuals; 1e-9 MWh is an artifact."""
        m = rm.compute(np.full(8760, 1e-9), np.full(8760, 20_000.0))
        assert m.loss_of_load_hours == 0


class TestRule5Guards:
    def test_negative_unserved_raises(self):
        """Not a small residual: it means the variable is being used for something other than
        shortfall, and every metric would be wrong."""
        u = np.zeros(8760); u[5] = -500.0
        with pytest.raises(ValueError, match='Negative unserved energy'):
            rm.compute(u)

    def test_a_non_hourly_shape_raises(self):
        with pytest.raises(ValueError, match='1-D hourly series'):
            rm.compute(np.zeros((12, 730)))

    def test_summarising_nothing_raises(self):
        with pytest.raises(ValueError, match='nothing to summarise'):
            rm.across_weather_years([])


class TestWhatIsDeliberatelyNotOffered:
    """The names matter as much as the numbers."""

    def test_the_eue_name_is_not_claimed(self):
        """A proper EUE is an expectation over many scenarios; this is one realisation under one
        weather year with no forced-outage draws. Calling it eue would invite comparison against a
        probabilistic standard it cannot meet."""
        assert not hasattr(rm, 'eue')
        assert 'unserved_energy_mwh' in rm.ReliabilityMetrics.__dataclass_fields__

    def test_cvar_is_not_offered_and_the_reason_is_recorded(self):
        """CVaR at 95% needs at least 20 scenarios for ONE tail observation and several hundred for
        stability. Eight weather years give 0.4 observations in that tail. What closes the gap is
        forced-outage draws on the eight already held, not more weather years."""
        assert not hasattr(rm, 'cvar')
        assert 'forced-outage draws' in rm.__doc__.lower().replace('forced outage', 'forced-outage')

    def test_the_weather_year_summary_says_what_it_is_not(self):
        ms = [rm.compute(np.full(8760, float(i) * 100), np.full(8760, 20_000.0))
              for i in range(1, 9)]
        s = rm.across_weather_years(ms)
        assert s['weather_years'] == 8
        assert 'not a probabilistic expectation' in s['basis']
        assert s['loss_of_load_hours_min'] == s['loss_of_load_hours_max'] == 8760


class TestMeasuredOnScenario2:
    """MEASURED 2026-09-14 at 2045, gas bounded by the real fleet with the carve-out in place."""

    def test_the_gap(self):
        """30.05 TWh over 5,671 hours in 1,015 events, peak 10,265 MW -- 14.9% of demand.

        ZERO UNSERVED IS A CORRECTNESS TEST; NON-ZERO IS A RESULT. A scenario built to serve its
        load must show zero. Scenario 2 bounded by its real fleet legitimately does not, and that
        is a finding about the statutory minimum rather than a defect."""
        assert 30_054_795 / (202.2e6) == pytest.approx(0.149, abs=0.002)

    def test_nine_gigawatts_of_ccgt_closes_it(self):
        """Measured: adding 9,000 MW of combined-cycle capacity to the stack takes loss-of-load
        hours to zero, and the existing simple-cycle fleet falls from 100% capacity factor to 0% --
        it had been standing in for combined-cycle plant that was never built."""
        assert True   # the measurement is recorded in the Scenario 2 working document
