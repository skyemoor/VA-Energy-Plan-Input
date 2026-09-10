"""
test_scenario2_reserve_margin.py

Per Software Engineering Standards Rule 2 and Rule 2.4 -- the latter specifically, since this
module exists because Rule 2.4 was not previously satisfied: reserve margin had end-to-end
treatment for Scenario 1 and Scenario 3 but never for Scenario 2.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lp_package'))

import numpy as np
import pytest
import lp_model as lp
from scenario2_reserve_margin import (peak_net_demand_hour, required_gas_capacity_mw,
                                       compare_capacity_standards,
                                       DEFAULT_INSTALLED_RESERVE_MARGIN)


def synthetic_year(hours=48, peak_hour=20):
    """Small deterministic year with a known peak, so the peak-hour identification is checkable."""
    demand = np.full(hours, 15_000.0)
    demand[peak_hour] = 20_000.0
    nuclear = np.full(hours, 3_691.0)
    exist_solar = np.zeros(hours)
    solar_cf = np.zeros(hours)          # peak at hour 20: no solar contribution
    wind_cf = np.full(hours, 0.30)
    return demand, nuclear, exist_solar, solar_cf, wind_cf


class TestPeakHourMatchesScenario1Definition:
    """Guards against Scenario 2 identifying its peak hour by a parallel rule. The scenarios must
    agree on WHICH hour binds before their capacity requirements can be compared."""

    def test_finds_the_constructed_peak(self):
        demand, nuclear, exist_solar, solar_cf, wind_cf = synthetic_year(peak_hour=20)
        assert peak_net_demand_hour(demand, nuclear, exist_solar, wind_cf) == 20

    def test_definition_matches_reserve_margin_mixin(self):
        """ReserveMarginMixin.find_peak_net_demand_hour() uses
        demand - nuclear - exist_solar - CVOW_MW*wind_cf. Reproduced here directly rather than
        imported, so a change to either implementation breaks this test."""
        demand, nuclear, exist_solar, solar_cf, wind_cf = synthetic_year(peak_hour=13)
        mixin_definition = int(np.argmax(demand - nuclear - exist_solar - lp.CVOW_MW * wind_cf))
        assert peak_net_demand_hour(demand, nuclear, exist_solar, wind_cf) == mixin_definition


class TestReserveMarginStandardAppliedToScenario2:
    """The core correction: Scenario 2 must be held to the same standard as Scenarios 1 and 3."""

    def test_required_gas_credits_storage_and_applies_margin(self):
        demand, nuclear, exist_solar, solar_cf, wind_cf = synthetic_year(peak_hour=20)
        required = required_gas_capacity_mw(
            demand, nuclear, exist_solar, solar_cf, wind_cf,
            statutory_solar_mw=16_100.0,
            short_duration_storage_mw=16_000.0,
            long_duration_storage_mw=4_000.0)
        expected = ((1.177 * 20_000.0)
                    - 3_691.0
                    - lp.CVOW_MW * 0.30
                    - 0.0            # exist_solar
                    - 0.0            # solar_cf is zero at the peak hour
                    - 16_000.0 - 4_000.0)
        assert required == pytest.approx(max(0.0, expected))

    def test_floors_at_zero_when_fleet_already_satisfies_margin(self):
        """Rule 11: a negative capacity requirement has no physical meaning."""
        demand, nuclear, exist_solar, solar_cf, wind_cf = synthetic_year()
        required = required_gas_capacity_mw(
            demand, nuclear, exist_solar, solar_cf, wind_cf,
            statutory_solar_mw=16_100.0,
            short_duration_storage_mw=100_000.0,   # deliberately oversized
            long_duration_storage_mw=100_000.0)
        assert required == 0.0

    def test_larger_margin_requires_more_gas(self):
        demand, nuclear, exist_solar, solar_cf, wind_cf = synthetic_year()
        low = required_gas_capacity_mw(demand, nuclear, exist_solar, solar_cf, wind_cf,
                                        16_100.0, 4_000.0, 1_000.0,
                                        installed_reserve_margin=0.10)
        high = required_gas_capacity_mw(demand, nuclear, exist_solar, solar_cf, wind_cf,
                                         16_100.0, 4_000.0, 1_000.0,
                                         installed_reserve_margin=0.25)
        assert high > low

    def test_default_margin_is_pjm_irm(self):
        assert DEFAULT_INSTALLED_RESERVE_MARGIN == 0.177


class TestTwoStandardsAreReportedTogether:
    """Guards the reporting discipline. Appendix C.2's rule (worst hourly gap, zero storage
    credit, no margin) and the reserve-margin rule are conservative in opposite directions;
    reporting either alone hides that."""

    def test_comparison_reports_both_figures(self):
        demand, nuclear, exist_solar, solar_cf, wind_cf = synthetic_year(peak_hour=20)
        result = compare_capacity_standards(
            demand, nuclear, exist_solar, solar_cf, wind_cf,
            statutory_solar_mw=16_100.0,
            short_duration_storage_mw=16_000.0,
            long_duration_storage_mw=4_000.0)
        assert 'appendix_c2_gas_mw_zero_storage_credit_no_margin' in result
        assert 'reserve_margin_gas_mw_storage_credited' in result
        assert result['peak_net_demand_hour'] == 20
        assert result['demand_at_peak_mw'] == 20_000.0

    def test_with_large_storage_the_reserve_standard_requires_less_gas(self):
        """A real and initially counterintuitive consequence worth locking in: because the
        Statutory Floor carries 20,000 MW of storage, crediting that storage can more than offset
        the 17.7% margin. The original zero-credit rule was, in this configuration, the STRICTER
        of the two -- which is why 'Scenario 2 is under-built' was the wrong diagnosis."""
        demand, nuclear, exist_solar, solar_cf, wind_cf = synthetic_year(peak_hour=20)
        result = compare_capacity_standards(
            demand, nuclear, exist_solar, solar_cf, wind_cf,
            statutory_solar_mw=16_100.0,
            short_duration_storage_mw=16_000.0,
            long_duration_storage_mw=4_000.0)
        assert result['difference_mw'] < 0

    def test_with_small_storage_the_reserve_standard_requires_more_gas(self):
        """The opposite case, so the sign is understood to depend on storage size rather than
        being a fixed property of either rule."""
        demand, nuclear, exist_solar, solar_cf, wind_cf = synthetic_year(peak_hour=20)
        result = compare_capacity_standards(
            demand, nuclear, exist_solar, solar_cf, wind_cf,
            statutory_solar_mw=16_100.0,
            short_duration_storage_mw=500.0,
            long_duration_storage_mw=0.0)
        assert result['difference_mw'] > 0


class TestFailsLoudlyOnMissingInputs:
    """Rule 5. Each of these defaults would silently reproduce the inconsistency being corrected."""

    def test_missing_solar_raises(self):
        demand, nuclear, exist_solar, solar_cf, wind_cf = synthetic_year()
        with pytest.raises(ValueError, match='statutory_solar_mw is required'):
            required_gas_capacity_mw(demand, nuclear, exist_solar, solar_cf, wind_cf,
                                      None, 16_000.0, 4_000.0)

    def test_missing_short_duration_storage_raises(self):
        demand, nuclear, exist_solar, solar_cf, wind_cf = synthetic_year()
        with pytest.raises(ValueError, match='both required'):
            required_gas_capacity_mw(demand, nuclear, exist_solar, solar_cf, wind_cf,
                                      16_100.0, None, 4_000.0)

    def test_missing_long_duration_storage_raises(self):
        demand, nuclear, exist_solar, solar_cf, wind_cf = synthetic_year()
        with pytest.raises(ValueError, match='both required'):
            required_gas_capacity_mw(demand, nuclear, exist_solar, solar_cf, wind_cf,
                                      16_100.0, 16_000.0, None)
