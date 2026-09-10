"""
test_rps_compliance.py

Baseline-locked tests for rps_compliance.py, per Software_Engineering_Standards Rule 2.

Baselines are drawn from the statute itself (docs/statutes/56-585.5.md) and from this project's
own established figures, not from synthetic values. Each test class names what it guards against.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lp_package'))

import pytest
import driver
from rps_compliance import (StatutoryComplianceBase, StatutoryRPSObligation, compare_bases,
                            deficiency_payment_rate_per_mwh,
                            ACCELERATED_CLEAN_ENERGY_BUYER_THRESHOLD_MW,
                            IN_COMMONWEALTH_REC_MINIMUM_SHARE)


class TestStatutoryScheduleMatchesCode:
    """Guards against drift between this module and the statutory table. Rule 6: the schedule is
    referenced from driver, not duplicated, so these lock the reference to the printed statute."""

    def test_key_years_match_statute(self):
        # docs/statutes/56-585.5.md § C.1.a, Phase II column
        assert driver.RPS_CLEAN_PCT_PHASE_II[2030] == 0.41
        assert driver.RPS_CLEAN_PCT_PHASE_II[2035] == 0.59
        assert driver.RPS_CLEAN_PCT_PHASE_II[2040] == 0.79
        assert driver.RPS_CLEAN_PCT_PHASE_II[2045] == 1.00

    def test_beyond_2045_is_one_hundred_percent(self):
        """'2045 and thereafter' per the statute's own row label."""
        base = StatutoryComplianceBase(2046, 100_000_000.0, 0.0, 0.0)
        assert StatutoryRPSObligation(base, 0.0).required_percentage() == 1.00

    def test_statutory_thresholds(self):
        assert ACCELERATED_CLEAN_ENERGY_BUYER_THRESHOLD_MW == 25.0   # § 56-585.5(A)
        assert IN_COMMONWEALTH_REC_MINIMUM_SHARE == 0.75             # § 56-585.5(C)(3)


class TestComplianceBaseExclusions:
    """Guards the central finding: § 56-585.5(A) excludes in-Commonwealth nuclear and certified
    ACEB load. Omitting either overstates the obligation — nuclear alone by roughly 30%."""

    def build_2030_base(self, aceb_mwh=0.0):
        # Virginia-only 2030 sales derived in the working notes as 2B-1 total less 2B-3 NC:
        # 110,864 - 3,870 = 106,994 GWh. Nuclear approximated at ~32,000 GWh pending an
        # actual-generation figure (working notes, open item 3).
        return StatutoryComplianceBase(
            year=2030,
            virginia_retail_sales_mwh=106_994_000.0,
            in_commonwealth_nuclear_generation_mwh=32_000_000.0,
            accelerated_clean_energy_buyer_load_mwh=aceb_mwh)

    def test_nuclear_exclusion_materially_shrinks_the_base(self):
        base = self.build_2030_base()
        assert base.total_electric_energy_mwh() == pytest.approx(74_994_000.0)
        breakdown = base.exclusion_breakdown()
        assert breakdown['nuclear_excluded_share'] == pytest.approx(0.299, abs=0.01)
        assert breakdown['base_as_share_of_sales'] == pytest.approx(0.701, abs=0.01)

    def test_aceb_participation_further_shrinks_the_base(self):
        """ACEB is the largest behavioral lever: data centers over 25 MW that self-procure leave
        the compliance base entirely (§ G)."""
        no_participation = self.build_2030_base(aceb_mwh=0.0)
        heavy_participation = self.build_2030_base(aceb_mwh=20_000_000.0)
        assert (heavy_participation.total_electric_energy_mwh()
                < no_participation.total_electric_energy_mwh())
        assert heavy_participation.total_electric_energy_mwh() == pytest.approx(54_994_000.0)

    def test_base_floors_at_zero_not_negative(self):
        base = StatutoryComplianceBase(2030, 100_000.0, 90_000.0, 50_000.0)
        assert base.total_electric_energy_mwh() == 0.0

    def test_missing_nuclear_raises_rather_than_defaulting_to_zero(self):
        with pytest.raises(ValueError, match='in_commonwealth_nuclear_generation_mwh is required'):
            StatutoryComplianceBase(2030, 106_994_000.0, None, 0.0)

    def test_missing_aceb_raises_rather_than_defaulting(self):
        with pytest.raises(ValueError, match='accelerated_clean_energy_buyer_load_mwh is required'):
            StatutoryComplianceBase(2030, 106_994_000.0, 32_000_000.0, None)

    def test_zero_sales_raises(self):
        with pytest.raises(ValueError, match='virginia_retail_sales_mwh is required'):
            StatutoryComplianceBase(2030, 0.0, 0.0, 0.0)


class TestDeficiencyPaymentCeiling:
    """Guards § 56-585.5(D)(5), the economic ceiling on compliance cost. This is why the
    statutory and physical bases can diverge in practice: a utility facing physical build costs
    above this rate can lawfully pay the deficiency instead."""

    def test_base_rate_at_base_year(self):
        assert deficiency_payment_rate_per_mwh(2021) == pytest.approx(45.0)

    def test_escalates_one_percent_annually(self):
        assert deficiency_payment_rate_per_mwh(2022) == pytest.approx(45.45)
        assert deficiency_payment_rate_per_mwh(2045) == pytest.approx(45.0 * 1.01 ** 24)

    def test_2045_ceiling_is_far_below_modeled_physical_cost(self):
        """The finding this enables: the 2045 physical SLCOE was modeled near $133/MWh
        (provisional). The statutory ceiling is roughly a third of that."""
        ceiling = deficiency_payment_rate_per_mwh(2045)
        assert ceiling < 60.0
        assert ceiling < 133.5 / 2

    def test_three_statutory_rates(self):
        assert deficiency_payment_rate_per_mwh(2021, 'standard') == pytest.approx(45.0)
        assert deficiency_payment_rate_per_mwh(2021, 'sub_one_mw') == pytest.approx(75.0)
        assert deficiency_payment_rate_per_mwh(2021, 'geothermal') == pytest.approx(100.0)

    def test_unknown_rate_category_raises(self):
        with pytest.raises(ValueError, match='unrecognized rate_category'):
            deficiency_payment_rate_per_mwh(2030, 'offshore_wind')

    def test_year_before_base_year_raises(self):
        with pytest.raises(ValueError, match='precedes the deficiency'):
            deficiency_payment_rate_per_mwh(2020)


class TestObligationAndCarveOuts:

    def build_2030_obligation(self, eligible_mwh):
        base = StatutoryComplianceBase(2030, 106_994_000.0, 32_000_000.0, 0.0)
        return StatutoryRPSObligation(base, eligible_mwh)

    def test_required_rec_is_percentage_of_adjusted_base_not_sales(self):
        """The core distinction: 41% applies to the post-exclusion base, not raw sales."""
        obligation = self.build_2030_obligation(0.0)
        assert obligation.required_rec_mwh() == pytest.approx(0.41 * 74_994_000.0)
        # Materially less than 41% of unadjusted sales
        assert obligation.required_rec_mwh() < 0.41 * 106_994_000.0

    def test_shortfall_floors_at_zero_when_generation_exceeds_requirement(self):
        obligation = self.build_2030_obligation(999_000_000.0)
        assert obligation.shortfall_mwh() == 0.0
        assert obligation.deficiency_payment_dollars() == 0.0

    def test_distributed_carve_out_shares_by_window(self):
        """§ 56-585.5(C)(2): 4.5% for 2026-2030, 5% for 2031-2045."""
        base_2030 = StatutoryComplianceBase(2030, 106_994_000.0, 32_000_000.0, 0.0)
        base_2035 = StatutoryComplianceBase(2035, 106_994_000.0, 32_000_000.0, 0.0)
        o30 = StatutoryRPSObligation(base_2030, 0.0)
        o35 = StatutoryRPSObligation(base_2035, 0.0)
        assert o30.distributed_carve_out_mwh() == pytest.approx(0.045 * o30.required_rec_mwh())
        assert o35.distributed_carve_out_mwh() == pytest.approx(0.05 * o35.required_rec_mwh())

    def test_phase_one_raises_rather_than_using_phase_two_percentages(self):
        base = StatutoryComplianceBase(2030, 106_994_000.0, 32_000_000.0, 0.0)
        with pytest.raises(NotImplementedError, match='Phase I percentages differ'):
            StatutoryRPSObligation(base, 0.0, utility_phase='I')


class TestDualBasisComparison:
    """Guards the reporting discipline: the two bases must be reported together, and the GAP
    between them is the finding."""

    def test_gap_is_positive_at_2045_physical_exceeds_statutory(self):
        """At 2045 the physical basis is the stricter of the two — it requires new clean build
        to cover load that existing nuclear already serves."""
        base = StatutoryComplianceBase(2045, 180_000_000.0, 32_000_000.0, 0.0)
        obligation = StatutoryRPSObligation(base, 0.0)
        physical_requirement_mwh = 205_902_000.0   # raw DOMLSE 2045 load, session figure
        comparison = compare_bases(obligation, physical_requirement_mwh)
        assert comparison['statutory_rps_obligation_mwh'] == pytest.approx(148_000_000.0)
        assert comparison['gap_mwh'] > 0
        assert comparison['statutory_as_share_of_physical'] < 1.0

    def test_comparison_reports_the_deficiency_ceiling(self):
        base = StatutoryComplianceBase(2045, 180_000_000.0, 32_000_000.0, 0.0)
        comparison = compare_bases(StatutoryRPSObligation(base, 0.0), 205_902_000.0)
        assert comparison['deficiency_payment_ceiling_per_mwh'] == pytest.approx(45.0 * 1.01 ** 24)
