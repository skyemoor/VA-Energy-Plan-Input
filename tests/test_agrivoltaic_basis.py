"""
test_agrivoltaic_basis.py

Tests the 85%-of-total-solar agrivoltaic basis, its land footprint, farm lease income, and
Va. Code § 58.1-2636 local revenue share.

As with parking_ratio_basis, several tests lock LIMITATIONS rather than capabilities. The 85%
share is a stated assumption rather than a bottom-up result, and every figure derived from it
inherits that. A later edit that quietly drops the caveat would leave the numbers looking like
measurements.
"""
import pytest

import agrivoltaic_basis as ag


class TestSharedBasis:
    def test_share_is_eighty_five_percent_of_TOTAL_solar(self):
        """Not 90% of a non-urban subset, which is how scenario3_build.py frames it. The two
        differ by 13 points on every derived figure, so the distinction is load-bearing."""
        assert ag.AGRIVOLTAIC_SHARE_OF_TOTAL_SOLAR == 0.85

    def test_footprint_splits_the_build_correctly(self):
        f = ag.footprint(100_000.0)
        assert f.agrivoltaic_mw == pytest.approx(85_000.0)
        assert f.non_agrivoltaic_mw == pytest.approx(15_000.0)

    def test_firmed_acreage_exceeds_solar_only_but_modestly(self):
        """Storage adds real land but only ~2.5-4% -- reported separately so a reader comparing
        against another study's acres/MW knows whether storage is inside it."""
        f = ag.footprint(100_000.0)
        assert f.firmed_acres_low > f.solar_acres_low
        assert f.firmed_acres_low / f.solar_acres_low < 1.05

    def test_invalid_inputs_raise(self):
        with pytest.raises(ValueError, match='must be positive'):
            ag.footprint(0.0)
        with pytest.raises(ValueError, match='fraction'):
            ag.footprint(1000.0, agrivoltaic_share=1.5)


class TestTheAssumptionTravelsWithEveryFigure:
    def test_footprint_carries_the_assumption(self):
        assert 'STATED ALLOCATION ASSUMPTION' in ag.footprint(1000.0).assumption

    def test_assumption_names_current_practice_is_far_below(self):
        """NREL counts 13 existing Virginia agrivoltaic projects. Presenting 85% without that
        context would read as descriptive rather than aspirational."""
        s = ag.share_is_assumed()
        assert '13 existing' in s and 'not a description of current practice' in s

    def test_lease_income_inherits_the_assumption(self):
        assert ag.lease_income(ag.footprint(1000.0)).assumption == ag.share_is_assumed()


class TestLeaseIncomeAppliesBroadlyByDefault:
    """A real distinction from the appendix: a landowner is paid for hosting the array whether or
    not the siting is agrivoltaic. Restricting lease income to the agrivoltaic share would
    understate the income effect."""

    def test_default_covers_all_utility_scale_acreage(self):
        li = ag.lease_income(ag.footprint(100_000.0))
        assert 'whether or not the siting is agrivoltaic' in li.applies_to

    def test_agrivoltaic_only_is_smaller_and_says_why(self):
        f = ag.footprint(100_000.0)
        assert (ag.lease_income(f, agrivoltaic_only=True).annual_income_low
                < ag.lease_income(f).annual_income_low)
        assert 'also retains agricultural production' in ag.lease_income(f, agrivoltaic_only=True).applies_to

    def test_virginia_rates_exceed_the_national_average(self):
        assert ag.VA_LEASE_RATE_LOW > ag.NATIONAL_LEASE_RATE_HIGH

    def test_the_stability_argument_does_not_rest_on_yield(self):
        """The NSPM-relevant claim is income VARIANCE reduction. Crop yield under panels is
        contested and has no Virginia field-trial basis, so a benefit case resting on yield is
        far weaker than one resting on contracted revenue."""
        note = ag.lease_income(ag.footprint(1000.0)).income_stability_note
        assert 'VARIANCE' in note
        assert 'does not depend on agrivoltaic crop yields' in note

    def test_production_value_is_not_estimated(self):
        """Adding a speculative production figure to a well-sourced lease figure would degrade
        the latter. No field should offer one."""
        li = ag.lease_income(ag.footprint(1000.0))
        assert not any('production_value' in f or 'crop_income' in f
                       for f in li.__dataclass_fields__)


class TestRevenueShareStatute:
    """§ 58.1-2636, verified against the Code rather than assumed."""

    def test_base_rate_matches_the_statute(self):
        assert ag.REVENUE_SHARE_BASE_RATE_PER_MW == 1_400.0
        assert ag.revenue_share_rate_per_mw(2025) == 1_400.0

    def test_escalates_ten_percent_every_five_years_from_2026(self):
        assert ag.revenue_share_rate_per_mw(2026) == pytest.approx(1_540.0)
        assert ag.revenue_share_rate_per_mw(2030) == pytest.approx(1_540.0)
        assert ag.revenue_share_rate_per_mw(2031) == pytest.approx(1_694.0)
        assert ag.revenue_share_rate_per_mw(2045) == pytest.approx(2_049.74, abs=0.01)

    def test_storage_is_assessed_separately_from_generation(self):
        """§ 58.1-2636(A)(1)(ii). Easy to overlook, and at 2045 storage is roughly a third of the
        total -- omitting it understates the rural benefit by that much."""
        r = ag.revenue_share(2045, 173_780.7, 86_905.5)
        assert r.storage_revenue > 0
        assert r.storage_revenue / r.total_revenue == pytest.approx(0.33, abs=0.02)

    def test_omitting_storage_is_recorded_not_silent(self):
        assert 'storage_mw was not supplied' in ag.revenue_share(2045, 100_000.0).caveat

    def test_caveat_states_the_rate_is_a_ceiling(self):
        """'Up to' -- adopted by ordinance. Not every locality has one, and some adopt below the
        maximum, so these are upper bounds."""
        c = ag.revenue_share(2045, 1000.0, 100.0).caveat
        assert 'MAXIMUM' in c and 'ceiling' in c

    def test_caveat_flags_the_small_project_and_net_metering_exemptions(self):
        """Distributed rooftop and canopy are largely outside this mechanism -- a real asymmetry
        between the utility-scale and distributed paths."""
        c = ag.revenue_share(2045, 1000.0, 100.0).caveat
        assert 'exempt' in c and 'distributed rooftop and canopy' in c

    def test_caveat_flags_the_ac_versus_dc_ambiguity(self):
        assert 'measured in AC' in ag.revenue_share(2045, 1000.0, 100.0).caveat

    def test_2045_headline_figure(self):
        r = ag.revenue_share(2045, 173_780.7, 50_546.5 + 36_359.0)
        assert r.total_revenue / 1e6 == pytest.approx(534.3, abs=1.0)
