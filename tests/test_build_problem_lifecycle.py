"""
test_build_problem_lifecycle.py

ScenarioLifecycleCost.from_build_problem_result -- the SLCOE-basis adjustment for scenarios solved
through lp_model.build_problem.

WHY IT IS A DIFFERENT ADJUSTMENT FROM SCENARIO 2's, and why confusing them would double-count
billions:

    build_scenario2_problem   dispatch-only. NO capital, NO FOM, on anything.
                              -> add capital and FOM for every asset.
    build_problem             capital AND FOM on BUILT assets already in the objective
                              (c[UTILITY_SOLAR_MW] = CRF*SOLAR_CAPEX*1000 + SOLAR_OM*1000).
                              -> add FOM on EXISTING assets only.
"""
import pytest

import lp_model as lp
from scenario_lifecycle_cost import ScenarioLifecycleCost as S


def s1(obj=26_071_685_157.7, curt=161.5e6, unserved=0.0):
    existing = [('existing_solar', lp.exist_solar_mw(2045), lp.SOLAR_CAPEX, lp.SOLAR_OM)]
    return S.from_build_problem_result(2045, {'obj': obj}, existing,
                                       curtailment_mwh=curt, unserved_mwh=unserved)


class TestNoDoubleCountingOfCapital:
    """build_problem already prices what it builds. Adding capital again would count the build
    twice, and at 165,875 MW of solar that is billions."""

    def test_no_capital_is_added(self):
        assert s1().annualised_capital_usd == 0.0

    def test_existing_assets_carry_fom_only(self):
        c = s1()
        a = c.assets[0]
        assert a.new_mw == 0.0
        assert a.fixed_om_usd == pytest.approx(a.existing_mw * 1000 * lp.SOLAR_OM, rel=1e-6)
        assert 'capital is sunk' in a.note


class TestCurtailmentIsNettedOut:
    """apply_slcr_constraint(curt_cost=5.0) exists to DISCOURAGE curtailment in dispatch, not to
    price it. Real curtailment costs something -- foregone RECs, PPA curtailment payments -- but
    not $5/MWh, and not as a cheque anyone writes."""

    def test_penalty_is_removed_from_the_objective(self):
        c = s1()
        assert c.curtailment_removed_usd == pytest.approx(161.5e6 * 5.0)
        assert c.operating_cost_usd == pytest.approx(c.objective_usd - c.curtailment_removed_usd)

    def test_the_adjustment_is_visible_in_the_summary(self):
        """A reviewer seeing 'a cost was removed from the clean scenario' needs to find the
        reasoning and the magnitude without reading the source."""
        d = s1().summary()
        assert d['curtailment_removed_usd'] > 0
        assert d['curtailment_mwh'] == pytest.approx(161.5e6)
        assert d['objective_usd'] > d['operating_cost_usd']

    def test_it_grows_with_overbuild_which_is_why_it_matters(self):
        """MEASURED 2026-09-13: Scenario 1 at 100% curtails 161.5 TWh against 202.2 TWh of demand.
        At $5/MWh that is $807M sitting in the objective as a cost nobody incurs -- and it grows
        with the overbuild, which is exactly where the sweep is most sensitive."""
        assert s1().curtailment_removed_usd == pytest.approx(807.5e6, rel=0.01)

    def test_zero_curtailment_leaves_the_total_unchanged(self):
        """Netted out of EVERY scenario, not only the clean ones. Scenario 2's happens to be zero,
        and that symmetry is the point."""
        assert s1(curt=0.0).operating_cost_usd == pytest.approx(26_071_685_157.7)


class TestUnservedIsAssertedNotAdjusted:
    """At $100,000/MWh it would dominate any total it appeared in, so a nonzero value is a failed
    solve rather than a cost."""

    def test_nonzero_unserved_raises(self):
        with pytest.raises(ValueError, match='not zero'):
            s1(unserved=500.0)

    def test_the_message_gives_the_magnitude_and_the_remedy(self):
        with pytest.raises(ValueError, match='fix the solve rather than costing it'):
            s1(unserved=1_000.0)

    def test_zero_passes(self):
        assert s1(unserved=0.0).total_annual_usd > 0


class TestMeasuredScenario1:
    """BASELINE LOCKED 2026-09-13 from the real 2045 solve with reserve margin applied."""

    def test_slcoe_basis_total(self):
        """$26.07B objective − $0.81B curtailment + $0.12B existing-solar FOM = $25.38B,
        or $125.52/MWh against 202.2 TWh."""
        c = s1()
        assert c.total_annual_usd == pytest.approx(25.38e9, rel=0.01)
        assert c.cost_per_mwh(202.2e6) == pytest.approx(125.52, rel=0.01)
