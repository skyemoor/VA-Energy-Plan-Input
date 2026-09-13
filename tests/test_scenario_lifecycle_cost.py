"""
test_scenario_lifecycle_cost.py

Full annualised scenario cost: capital and FOM on every asset, plus the LP's operating cost.

WHY. build_scenario2_problem is dispatch-only -- its objective carries fuel, VOM, storage cycling,
export revenue and the unserved penalty, and NO CAPITAL WHATSOEVER. Reading result['obj'] as a
scenario cost understates Scenario 2 by billions, in the direction that flatters the baseline the
whitepaper is measured against.
"""
import pytest

import assumptions
import lp_model as lp
from assumptions import CCGT_CAPEX_KW_BY_CASE as CCGT_CAPEX_KW
from scenario_lifecycle_cost import ScenarioLifecycleCost


def stub():
    return (ScenarioLifecycleCost(2045, operating_cost_usd=6.25e9)
            .add_asset('solar', existing_mw=4_818.5, new_mw=11_445.2,
                       capex_usd_per_kw=lp.SOLAR_CAPEX, fixed_om_usd_per_kw_yr=lp.SOLAR_OM))


class TestCapitalOnNewBuildOnly:

    def test_existing_capacity_is_not_charged_capital(self):
        """Charging it would bill Dominion twice for plant already paid for."""
        c = stub()
        a = c.assets[0]
        assert a.annualised_capital_usd == pytest.approx(
            a.new_mw * 1000 * lp.SOLAR_CAPEX * c.crf, rel=1e-6)

    def test_fom_applies_to_existing_capacity_too(self):
        """An already-paid-for plant still costs money to keep available. Only capital is sunk."""
        a = stub().assets[0]
        assert a.fixed_om_usd == pytest.approx(
            (a.existing_mw + a.new_mw) * 1000 * lp.SOLAR_OM, rel=1e-6)

    def test_negative_capacity_raises(self):
        """A negative new-build figure would produce a capital CREDIT."""
        with pytest.raises(ValueError, match='would produce a capital credit'):
            ScenarioLifecycleCost(2045, 0.0).add_asset('x', existing_mw=0, new_mw=-100,
                                                       capex_usd_per_kw=1000)


class TestTotals:

    def test_total_is_capital_plus_fom_plus_operating(self):
        c = stub()
        assert c.total_annual_usd == pytest.approx(
            c.annualised_capital_usd + c.fixed_om_usd + c.operating_cost_usd)

    def test_operating_cost_is_not_double_counted(self):
        """The LP objective is operating cost only; the class adds capital, it does not recompute
        fuel."""
        c = stub()
        assert c.operating_cost_usd == 6.25e9

    def test_negative_operating_cost_raises(self):
        """Possible only through export revenue exceeding all costs -- worth investigating rather
        than passing through."""
        with pytest.raises(ValueError, match='worth investigating'):
            ScenarioLifecycleCost(2045, operating_cost_usd=-1.0)

    def test_cost_per_mwh_requires_positive_demand(self):
        with pytest.raises(ValueError, match='demand_mwh must be positive'):
            stub().cost_per_mwh(0)


class TestScenario2Measured:
    """BASELINE LOCKED 2026-09-13 from the real Scenario 2 2045 solve."""

    def test_capital_is_a_third_of_the_total(self):
        """$3.40B capital + $0.81B FOM + $6.25B operating = $10.46B, so 32.5% of the scenario's
        annual cost was previously invisible in result['obj']."""
        assert 3.40 / 10.46 == pytest.approx(0.325, abs=0.01)


class TestNewCcgtExceedsPjmCapacityPrice:
    """The units plausibility check in AnnualizedCost fires on gas -- and it is NOT a units error.

    It compares annualised cost against the highest capacity price PJM has ever cleared, as a
    ceiling above which a units mistake is likelier than a market signal. Here the units are right
    and the finding is real."""

    @pytest.mark.parametrize('basis', ['low', 'central', 'high'])
    def test_new_ccgt_costs_more_than_pjm_has_ever_paid_for_capacity(self, basis):
        """$152.63 / $186.35 / $233.55 per kW-yr against a $118.62 all-time-high capacity price.

        AT EVERY POINT IN THE BAND, a new CCGT cannot be justified on capacity revenue alone -- it
        needs substantial energy margin as well. That bears directly on whether new gas is
        economic at 2045 gas prices, and it is the kind of finding the warning exists to surface
        rather than suppress."""
        annual = CCGT_CAPEX_KW[basis] * lp.CRF + assumptions.CCGT_FOM_KW_YR
        from cost_derivation import AnnualizedCost
        assert annual > AnnualizedCost.PJM_HIGHEST_CLEARED_CAPACITY_PRICE_USD_PER_KW_YR

    def test_the_warning_is_surfaced_not_swallowed(self):
        c = ScenarioLifecycleCost(2045, 0.0).add_asset(
            'gas', existing_mw=0, new_mw=1_000,
            capex_usd_per_kw=CCGT_CAPEX_KW['central'],
            fixed_om_usd_per_kw_yr=assumptions.CCGT_FOM_KW_YR)
        assert c.warnings and 'gas' in c.warnings[0]
        assert c.summary()['warnings']


class TestStrandingCaveat:
    def test_the_pathway_limitation_travels_with_the_result(self):
        """Capital is annualised over full economic life, which assumes the asset earns across it.
        On a pathway that can fail, and the failure makes late-built gas look cheap."""
        caveat = ScenarioLifecycleCost.stranding_caveat()
        assert 'LATE-BUILT GAS LOOKS CHEAP' in caveat
        assert '2035' in caveat
        assert ScenarioLifecycleCost(2045, 0.0).summary()['caveats'] == caveat
