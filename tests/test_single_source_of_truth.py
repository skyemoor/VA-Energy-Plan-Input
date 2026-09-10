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
import dlc_assumptions
import large_ci_curtailment_assumptions


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


class TestDomainAssumptionModulesSourceFromCore:
    """The _assumptions modules keep their DERIVATIONS but not their primitive inputs. Established
    2026-09-10: assumptions.py is the policy-adjustable surface, so anything a modeler or
    legislator would vary belongs there regardless of domain."""

    def test_large_ci_program_terms(self):
        import assumptions
        assert large_ci_curtailment_assumptions.COMPENSATION_USD_PER_KW_YEAR == assumptions.LARGE_CI_COMPENSATION_USD_PER_KW_YEAR
        assert large_ci_curtailment_assumptions.ELIGIBILITY_THRESHOLD_KW == assumptions.LARGE_CI_ELIGIBILITY_THRESHOLD_KW

    def test_dlc_primitive_inputs(self):
        import assumptions
        assert dlc_assumptions.EV_EFFICIENCY_KWH_PER_MILE == assumptions.EV_EFFICIENCY_KWH_PER_MILE
        assert dlc_assumptions.LEVEL2_CHARGER_POWER_KW == assumptions.LEVEL2_CHARGER_POWER_KW
        assert dlc_assumptions.EVENT_WINDOW_HOURS == assumptions.EV_CHARGER_REWARDS_EVENT_WINDOW_HOURS
        assert dlc_assumptions.ANNUAL_INCENTIVE_USD_PER_PARTICIPANT == assumptions.EV_CHARGER_REWARDS_ANNUAL_INCENTIVE_USD

    def test_derived_values_stay_derived(self):
        """Derived values must recompute from their inputs, not be moved to assumptions.py where
        they would look adjustable while silently disagreeing with those inputs."""
        expected = (dlc_assumptions.VIRGINIA_ANNUAL_VMT_PER_DRIVER_MILES / 365.0
                    * dlc_assumptions.EV_EFFICIENCY_KWH_PER_MILE
                    / dlc_assumptions.LEVEL2_CHARGER_POWER_KW)
        assert dlc_assumptions.ACTIVE_CHARGING_SESSION_HOURS == expected

    def test_dlc_avoided_cost_is_annualized_not_raw_capex(self):
        """Guards the units defect found 2026-09-10: raw capex ($1,175/$713 per kW) was used as
        annual avoided capacity cost. PJM capacity has never cleared near $713/kW-yr."""
        assert 80 < dlc_assumptions.AERODERIVATIVE_AVOIDED_COST_USD_PER_KW_YR < 95
        assert 45 < dlc_assumptions.F_CLASS_AVOIDED_COST_USD_PER_KW_YR < 55

    def test_entry_82_baseline_capex_is_named_as_historical(self):
        """The entry #82 peaker figures are a historical baseline, not current cost. The name must
        say so, so a future reader cannot swap in current figures without noticing they would
        change an established, cited result."""
        assert hasattr(large_ci_curtailment_assumptions, 'AERODERIVATIVE_CAPEX_USD_PER_KW_ENTRY82_BASELINE')
        assert hasattr(large_ci_curtailment_assumptions, 'F_CLASS_CAPEX_USD_PER_KW_ENTRY82_BASELINE')
