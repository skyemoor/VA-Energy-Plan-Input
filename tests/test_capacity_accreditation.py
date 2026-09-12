"""
test_capacity_accreditation.py

Tests for the CapacityAccreditation hierarchy, consolidating what were two separate suites
(test_storage_accreditation.py and test_scenario2_reserve_margin.py) against two free-standing
function modules.

Those modules each defined their own peak-hour finder, differing only in whether one or several
indices were returned -- the duplication a shared base removes. Testing the hierarchy means the
shared behaviour is tested once rather than twice, and the subclass tests cover only what is
genuinely subclass-specific.
"""
import numpy as np
import pytest

import assumptions
import lp_model as lp
from capacity_accreditation import (PeakHourAnalysis, StorageCapacityCredit,
                                    ReserveMarginRequirement)


def flat_year(hours=48, peak_hour=20, peak_mw=20_000.0, base_mw=15_000.0):
    demand = np.full(hours, base_mw)
    demand[peak_hour] = peak_mw
    return (demand, np.full(hours, 3_691.0), np.zeros(hours),
            np.full(hours, 0.30), np.zeros(hours))


class TestPeakHourAnalysisSharedBase:
    """Tested ONCE here rather than separately in each subclass's suite."""

    def test_peak_hour_and_peak_hours_agree_on_the_binding_hour(self):
        d, nuc, ex, wcf, scf = flat_year(peak_hour=20)
        a = PeakHourAnalysis(d, nuc, ex, wind_cf=wcf, solar_cf=scf)
        assert a.peak_hour() == 20
        assert a.peak_hours(1)[0] == 20

    def test_net_demand_subtracts_all_nondispatchable_clean(self):
        """Hour 0 has higher gross demand but more clean generation, so hour 1 must bind."""
        a = PeakHourAnalysis(np.array([1000.0, 900.0]), np.array([400.0, 100.0]),
                             np.zeros(2), wind_generation_mw=np.zeros(2),
                             solar_generation_mw=np.array([300.0, 0.0]))
        assert a.peak_hour() == 1

    def test_wind_capacity_factor_is_scaled_by_cvow_nameplate(self):
        """Matches ReserveMarginMixin.find_hour_of_maximum_net_demand, so the scenarios agree on which
        hour binds before their requirements can be compared."""
        d, nuc, ex, wcf, scf = flat_year()
        a = PeakHourAnalysis(d, nuc, ex, wind_cf=wcf)
        assert a.wind_mw[0] == pytest.approx(lp.CVOW_MW * 0.30)

    def test_supplying_both_forms_of_the_same_resource_raises(self):
        d, nuc, ex, wcf, scf = flat_year()
        with pytest.raises(ValueError, match='EITHER wind_cf OR'):
            PeakHourAnalysis(d, nuc, ex, wind_cf=wcf, wind_generation_mw=np.zeros(len(d)))

    def test_default_peak_hours_count_is_sourced_from_assumptions(self):
        d, nuc, ex, wcf, scf = flat_year(hours=100)
        a = PeakHourAnalysis(d, nuc, ex, wind_cf=wcf)
        assert len(a.peak_hours()) == assumptions.CAPACITY_CREDIT_PEAK_HOURS_COUNT

    def test_zero_hours_count_raises(self):
        d, nuc, ex, wcf, scf = flat_year()
        with pytest.raises(ValueError, match='at least 1'):
            PeakHourAnalysis(d, nuc, ex, wind_cf=wcf).peak_hours(0)


class TestStorageCapacityCredit:

    def build(self, soc_value, power=1_000.0, foresight=False, capacity=10_000.0, floor=0.0):
        d, nuc, ex, wcf, scf = flat_year(hours=48)
        return StorageCapacityCredit(
            d, nuc, ex, wind_cf=wcf, solar_cf=scf,
            state_of_charge_mwh=np.full(48, soc_value), power_rating_mw=power,
            dispatch_has_foresight=foresight, energy_capacity_mwh=capacity,
            depth_of_discharge_floor_fraction=floor)

    def test_full_storage_accredits_at_one(self):
        assert self.build(10_000.0).credit(3) == pytest.approx(1.0)

    def test_empty_storage_accredits_at_zero(self):
        assert self.build(0.0).credit(3) == pytest.approx(0.0)

    def test_energy_limited_fleet_accredits_below_nameplate(self):
        """1,000 MW rating but 250 MWh available: it can deliver 250 MW for one hour."""
        assert self.build(250.0).credit(1) == pytest.approx(0.25)

    def test_depth_of_discharge_floor_reduces_usable_energy(self):
        assert self.build(1_000.0, capacity=1_000.0, floor=0.20).credit(1) == pytest.approx(0.80)

    def test_zero_power_rating_raises(self):
        with pytest.raises(ValueError, match='must be positive'):
            self.build(1_000.0, power=0.0)


class TestForesightMustBeDeclared:
    """The 2026-09-10 finding, enforced structurally rather than documented.

    Own-data credit from an LP dispatch gave 100.0% against 31.8% from a no-foresight heuristic on
    the same fleet, and rose with penetration when it should fall. The old function interface let a
    caller pass any array without stating which kind it was.
    """

    def test_dispatch_has_foresight_is_required_not_defaulted(self):
        d, nuc, ex, wcf, scf = flat_year()
        with pytest.raises(TypeError):
            StorageCapacityCredit(d, nuc, ex, wind_cf=wcf,
                                  state_of_charge_mwh=np.ones(48), power_rating_mw=100.0)

    def test_cross_validation_carries_a_warning_when_foresight_present(self):
        d, nuc, ex, wcf, scf = flat_year()
        c = StorageCapacityCredit(d, nuc, ex, wind_cf=wcf, state_of_charge_mwh=np.full(48, 5_000.0),
                                  power_rating_mw=100.0, dispatch_has_foresight=True,
                                  energy_capacity_mwh=5_000.0)
        assert c.cross_validated(0.50)['foresight_warning'] is not None

    def test_no_warning_when_dispatch_has_no_foresight(self):
        d, nuc, ex, wcf, scf = flat_year()
        c = StorageCapacityCredit(d, nuc, ex, wind_cf=wcf, state_of_charge_mwh=np.full(48, 5_000.0),
                                  power_rating_mw=100.0, dispatch_has_foresight=False,
                                  energy_capacity_mwh=5_000.0)
        assert c.cross_validated(0.50)['foresight_warning'] is None

    def test_cross_validation_adopts_the_lower_value(self):
        """This rule is what stopped the 100% foresight artifact being adopted."""
        d, nuc, ex, wcf, scf = flat_year()
        full = StorageCapacityCredit(d, nuc, ex, wind_cf=wcf,
                                     state_of_charge_mwh=np.full(48, 5_000.0),
                                     power_rating_mw=100.0, dispatch_has_foresight=True,
                                     energy_capacity_mwh=5_000.0)
        r = full.cross_validated(0.50)
        assert r['own_data_credit'] == pytest.approx(1.0)
        assert r['adopted_credit'] == pytest.approx(0.50)
        assert r['source_adopted'] == 'published'


class TestReserveMarginRequirement:

    def build(self, firm_mw, irm=None):
        d, nuc, ex, wcf, scf = flat_year(peak_hour=20)
        return ReserveMarginRequirement(d, nuc, ex, wind_cf=wcf, solar_cf=scf,
                                        firm_capacity_mw=firm_mw, installed_reserve_margin=irm)

    def test_required_capacity_applies_the_margin(self):
        assert self.build(0.0).required_capacity_mw() == pytest.approx(1.177 * 20_000.0)

    def test_shortfall_floors_at_zero(self):
        assert self.build(200_000.0).dispatchable_shortfall_mw() == 0.0

    def test_larger_margin_requires_more_capacity(self):
        assert (self.build(5_000.0, irm=0.25).dispatchable_shortfall_mw()
                > self.build(5_000.0, irm=0.10).dispatchable_shortfall_mw())

    def test_default_margin_is_pjm_irm_from_assumptions(self):
        assert assumptions.INSTALLED_RESERVE_MARGIN == 0.177


class TestTwoStandardsReportedTogether:
    """Appendix C.2's zero-credit rule and the reserve-margin rule are conservative in OPPOSITE
    directions; reporting either alone hides that. The sign of the difference depends on how much
    firm capacity exists, which is why both directions are locked."""

    def build(self, firm_mw):
        d, nuc, ex, wcf, scf = flat_year(peak_hour=20)
        return ReserveMarginRequirement(d, nuc, ex, wind_cf=wcf, solar_cf=scf,
                                        firm_capacity_mw=firm_mw)

    def test_both_figures_present(self):
        r = self.build(20_000.0).compare_standards()
        assert 'appendix_c2_gas_mw_zero_storage_credit_no_margin' in r
        assert 'reserve_margin_gas_mw_storage_credited' in r
        assert r['peak_net_demand_hour'] == 20

    def test_large_firm_capacity_makes_reserve_standard_less_demanding(self):
        """Counterintuitive and real: crediting 20 GW of storage more than offsets a 17.7% margin,
        so the zero-credit rule is the STRICTER of the two here. 'Scenario 2 is under-built' was
        the wrong diagnosis."""
        assert self.build(20_000.0).compare_standards()['difference_mw'] < 0

    def test_small_firm_capacity_makes_reserve_standard_more_demanding(self):
        assert self.build(500.0).compare_standards()['difference_mw'] > 0
