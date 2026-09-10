"""
test_single_source_of_truth.py

Rule 6 enforcement. Guards against a module redefining a value that assumptions.py already owns,
which is how RESILIENCE_TILT_PCT silently diverged for six days (assumptions.py 0.0 against
lp_model.py 0.03) and how storage_accreditation.py briefly carried its own 0.20 duplicate of
NA_DOD_FLOOR on 2026-09-10.

Tests IDENTITY where the object allows it, not just equality -- two objects that happen to be
equal today can diverge tomorrow; two names bound to the same object cannot.
"""
import assumptions
import peaker_capex
import storage_accreditation
import scenario2_reserve_margin
import distributed_physical_bounds
import charging_adequacy
import gas_outage_stress
import rps_compliance


class TestModulesSourceFromAssumptions:

    def test_peaker_tier_table_is_the_same_object(self):
        assert peaker_capex.PEAKER_CAPEX_KW_BY_TIER is assumptions.PEAKER_CAPEX_KW_BY_TIER

    def test_storage_accreditation_dod_floor(self):
        assert storage_accreditation.NA_DEPTH_OF_DISCHARGE_FLOOR_FRACTION == assumptions.NA_DOD_FLOOR

    def test_reserve_margin(self):
        assert scenario2_reserve_margin.DEFAULT_INSTALLED_RESERVE_MARGIN == assumptions.INSTALLED_RESERVE_MARGIN

    def test_distributed_bounds(self):
        assert distributed_physical_bounds.DOM_ZONE_DISTRIBUTED_SOLAR_CAP_MW == assumptions.DOM_ZONE_DISTRIBUTED_SOLAR_CAP_MW
        assert distributed_physical_bounds.DISTRIBUTED_STORAGE_DURATION_HR == assumptions.DISTRIBUTED_STORAGE_DURATION_HR

    def test_cycling_requirements(self):
        assert charging_adequacy.DEFAULT_NA_CYCLES_PER_YEAR == assumptions.NA_CYCLES_PER_YEAR_REQUIREMENT
        assert charging_adequacy.DEFAULT_FE_CYCLES_PER_YEAR == assumptions.FE_CYCLES_PER_YEAR_REQUIREMENT

    def test_stress_window(self):
        assert gas_outage_stress.SIX_DAY_WINDOW_HOURS == assumptions.GAS_OUTAGE_STRESS_WINDOW_HOURS


class TestStatutoryParametersAreMutableButMarked:
    """Statutory values are deliberately adjustable so a proposed amendment to § 56-585.5 can be
    modelled -- Scenario 1B relaxes the 2045 requirement from 100% to 95%, which is a legislative
    recommendation rather than current law. This confirms they live in assumptions.py (so they CAN
    be changed in one place) and that the caution accompanies them."""

    def test_statutory_values_present_in_assumptions(self):
        for name in ('DEFICIENCY_PAYMENT_BASE_RATE_PER_MWH',
                     'ACCELERATED_CLEAN_ENERGY_BUYER_THRESHOLD_MW',
                     'IN_COMMONWEALTH_REC_MINIMUM_SHARE',
                     'STATUTORY_SOLAR_TARGET_MW'):
            assert hasattr(assumptions, name), f"{name} missing from assumptions.py"

    def test_rps_compliance_reads_them_rather_than_redefining(self):
        assert rps_compliance.DEFICIENCY_PAYMENT_BASE_RATE_PER_MWH == assumptions.DEFICIENCY_PAYMENT_BASE_RATE_PER_MWH
        assert rps_compliance.ACCELERATED_CLEAN_ENERGY_BUYER_THRESHOLD_MW == assumptions.ACCELERATED_CLEAN_ENERGY_BUYER_THRESHOLD_MW

    def test_caution_precedes_the_statutory_block(self):
        """The block must carry its warning -- a mutable statutory value with no caution is how a
        hypothetical-amendment result gets reported as compliance with existing law."""
        import inspect, os
        src = open(os.path.join(os.path.dirname(inspect.getfile(assumptions)), 'assumptions.py')).read()
        block = src[src.index('STATUTORY PARAMETERS'):src.index('DEFICIENCY_PAYMENT_BASE_RATE_PER_MWH')]
        assert 'READ BEFORE CHANGING' in block
        assert 'HYPOTHETICAL AMENDMENT' in block
        assert 'never as compliance with existing law' in block
