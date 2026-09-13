"""
test_gas_merit_order_class.py

Baseline-locked tests for GasMeritOrder (Rule 2).

The class exists because the LP's hourly dual has zero variance at 2030: gas is marginal in every
hour and there is one gas price, so gas OUTPUT varies across the day while gas MARGINAL COST does
not. These tests lock the spread the stack produces, because that spread is the whole point -- if
it collapses, the model has silently returned to a single effective price.
"""
import pytest

import assumptions
from gas_merit_order import GasMeritOrder, GasRung


@pytest.fixture
def stack():
    return GasMeritOrder()   # defaults to net_summer


class TestTheStackProducesARealSpread:
    """The reason the class exists. Locked to baselines so a regression is visible."""

    def test_2030_spread(self, stack):
        lo, hi = stack.marginal_cost_range_mwh(2030)
        assert hi - lo == pytest.approx(26.83, abs=0.05)

    def test_2045_spread(self, stack):
        lo, hi = stack.marginal_cost_range_mwh(2045)
        assert hi - lo == pytest.approx(33.85, abs=0.05)

    def test_spread_widens_with_the_fuel_price_trajectory(self, stack):
        """Heat-rate differences multiply the fuel price, so a rising trajectory widens the stack
        in absolute terms while the ratio stays fixed."""
        s30 = stack.marginal_cost_range_mwh(2030)
        s45 = stack.marginal_cost_range_mwh(2045)
        assert (s45[1] - s45[0]) > (s30[1] - s30[0])

    def test_rungs_are_ordered_cheapest_first(self, stack):
        for year in (2030, 2045):
            costs = [r.marginal_cost_mwh(year) for r in stack.rungs(year)]
            assert costs == sorted(costs)

    def test_ct_fleet_is_the_dearest_rung(self, stack):
        """It is the price-setting rung at peak, which is why its VOM and heat rate both being
        understated mattered."""
        assert stack.rungs(2045)[-1].name == 'ct_fleet'


class TestCapacityAndRetirements:

    def test_each_basis_sums_to_its_filed_total_before_any_retirement(self):
        """BASELINE CONTEXT 2026-09-13: the new-build pool (2,862 MW) is now a rung, so the stack
        total is the filed EXISTING-fleet figure plus the pool. This checks the existing-fleet
        arithmetic on its own; the pool is checked separately below."""
        for basis, total in (('nameplate', assumptions.GAS_DOM_ZONE_NAMEPLATE_MW),
                             ('net_summer', assumptions.GAS_DOM_ZONE_NET_SUMMER_MW),
                             ('net_winter', assumptions.GAS_DOM_ZONE_NET_WINTER_MW)):
            s = GasMeritOrder(capacity_basis=basis, include_new_build=False)
            assert sum(s.rated_capacity_mw_by_rung(2030).values()) == pytest.approx(total, abs=1.5)

    def test_new_build_pool_adds_to_the_existing_fleet_total(self):
        """The pool is capacity the scenarios PERMIT, not plant that exists, so it sits on top of
        the filed fleet figure rather than inside it."""
        with_pool = GasMeritOrder().rated_capacity_mw_by_rung(2030)
        without = GasMeritOrder(include_new_build=False).rated_capacity_mw_by_rung(2030)
        assert sum(with_pool.values()) - sum(without.values()) == pytest.approx(
            assumptions.GAS_NEW_BUILD_POOL_MW, abs=0.1)

    def test_new_build_prices_identically_to_modern_ccgt(self):
        """Same heat rate, same VOM -- the same technology, differing only in whether the plant
        exists. Two rungs at one price is intentional: dispatch cannot distinguish them but
        capacity accounting must."""
        rungs = {r.name: r for r in GasMeritOrder().rungs(2045)}
        assert rungs['new_build_ccgt'].marginal_cost_mwh(2045) == pytest.approx(
            rungs['ccgt_modern'].marginal_cost_mwh(2045))

    def test_availability_derates_uniformly(self, stack):
        name = stack.rated_capacity_mw_by_rung(2030)
        avail = stack.available_capacity_mw(2030)
        for r in name:
            assert avail[r] == pytest.approx(name[r] * assumptions.GAS_AVAILABILITY_FACTOR)

    def test_bear_garden_retires_from_ccgt_fleet_in_2041(self, stack):
        """Retirements are plant-specific, so rung totals move at different times -- which is why
        capacity is summed from the per-plant table rather than pre-summed rung figures."""
        before = stack.rated_capacity_mw_by_rung(2040)['ccgt_fleet']
        after = stack.rated_capacity_mw_by_rung(2041)['ccgt_fleet']
        assert before - after == pytest.approx(628.0, abs=0.1)   # Bear Garden net summer

    def test_warren_county_retires_from_ccgt_modern_in_2044(self, stack):
        before = stack.rated_capacity_mw_by_rung(2043)['ccgt_modern']
        after = stack.rated_capacity_mw_by_rung(2044)['ccgt_modern']
        assert before - after == pytest.approx(1_370.0, abs=0.1)  # Warren County net summer

    def test_retirements_hit_different_rungs(self, stack):
        """Bear Garden is ccgt_fleet, Warren County is ccgt_modern. A single fleet-wide retirement
        figure would lose that, and the stack shape matters more than the total."""
        p = assumptions.GAS_PLANT_CAPACITY_MW
        assert p['Bear Garden'][0] != p['Warren County'][0]


class TestVOMIsRungSpecific:

    def test_ct_vom_exceeds_ccgt_vom(self, stack):
        """NREL ATB: NGCT $5.00 vs NGCC $2.00 (2022); OCGT $4.49 vs CCGT $1.61 (2020). Using
        CCGT's figure for peakers understated their marginal cost."""
        assert assumptions.CT_VOM_MWH > assumptions.CCGT_VOM_MWH

    def test_ct_rung_carries_the_ct_vom(self, stack):
        ct = [r for r in stack.rungs(2045) if r.name == 'ct_fleet'][0]
        assert ct.vom_mwh == assumptions.CT_VOM_MWH

    def test_ccgt_rungs_carry_the_ccgt_vom(self, stack):
        for r in stack.rungs(2045):
            if r.name.startswith('ccgt'):
                assert r.vom_mwh == assumptions.CCGT_VOM_MWH


class TestFailsLoudly:
    """Rule 5."""

    def test_invalid_availability_raises(self):
        with pytest.raises(ValueError, match='availability_factor must be'):
            GasMeritOrder(availability_factor=0.0)
        with pytest.raises(ValueError, match='availability_factor must be'):
            GasMeritOrder(availability_factor=1.5)

    def test_output_beyond_the_stack_raises_rather_than_clamping(self, stack):
        """Silently returning the dearest rung would hide an infeasibility -- something above the
        stack must serve it, and neither imports nor scarcity are modelled."""
        with pytest.raises(ValueError, match='exceeds available stack capacity'):
            stack.marginal_rung_at_output(2045, 99_999.0)

    def test_negative_output_raises(self, stack):
        with pytest.raises(ValueError, match='non-negative'):
            stack.marginal_rung_at_output(2045, -1.0)

    def test_marginal_rung_identifies_the_price_setting_step(self, stack):
        # BASELINE MOVED 2026-09-13: new_build_ccgt now sorts first, tied on cost with
        # ccgt_modern. The assertion is on COST rather than name, since which of two equally
        # priced rungs sorts first is an implementation detail and not the behaviour under test.
        cheap = stack.marginal_rung_at_output(2045, 100.0)
        dear = stack.marginal_rung_at_output(2045, 8_000.0)
        assert cheap.name in ('new_build_ccgt', 'ccgt_modern')
        assert dear.marginal_cost_mwh(2045) > cheap.marginal_cost_mwh(2045)


class TestEmptyRungsAreDropped:
    def test_fully_retired_rung_is_not_returned(self):
        """A zero-capacity step is a trap for a caller iterating to find the marginal unit."""
        # ccgt_fleet now also holds Martinsville LFG (1 MW), so all three must retire.
        s = GasMeritOrder(retirement_years={'Bear Garden': 2030, 'Possum Point': 2030,
                                            'Martinsville LFG Generator': 2030})
        assert 'ccgt_fleet' not in [r.name for r in s.rungs(2035)]
        assert 'ccgt_fleet' in [r.name for r in s.rungs(2035, include_empty=True)]


class TestSeasonalBasis:
    """Three rating bases, all retained. Mixing nameplate with net summer created a phantom
    1,167 MW discrepancy on 2026-09-11 and produced two wrong hypotheses before the units were
    checked. The class makes the basis an explicit constructor choice for that reason."""

    def test_winter_exceeds_summer_by_about_eleven_percent(self):
        """Cold dense air raises compressor mass flow. Matters because the DOM zone now peaks in
        WINTER, so net summer may be the wrong derate for the binding hour."""
        ratio = assumptions.GAS_DOM_ZONE_NET_WINTER_MW / assumptions.GAS_DOM_ZONE_NET_SUMMER_MW
        assert ratio == pytest.approx(1.114, abs=0.005)

    def test_summer_is_below_nameplate(self):
        assert assumptions.GAS_DOM_ZONE_NET_SUMMER_MW < assumptions.GAS_DOM_ZONE_NAMEPLATE_MW

    def test_basis_changes_available_capacity(self):
        summer = GasMeritOrder(capacity_basis='net_summer').total_available_mw(2030)
        winter = GasMeritOrder(capacity_basis='net_winter').total_available_mw(2030)
        assert winter > summer

    def test_invalid_basis_raises_rather_than_defaulting(self):
        """Rule 5. There is no basis worth guessing -- each is wrong in a different direction."""
        with pytest.raises(ValueError, match='capacity_basis must be one of'):
            GasMeritOrder(capacity_basis='summer')

    def test_deliverability_caveat_is_recorded(self):
        """Winter CAPABILITY is not winter DELIVERABILITY -- pipeline constraints and heating-load
        competition are not modelled, and cut against using net winter uncaveated."""
        n = assumptions.GAS_SEASONAL_BASIS_NOTE
        assert 'not winter DELIVERABILITY' in n
        assert 'pipeline constraints' in n


class TestScopeIsDomZoneMerchant:

    def test_ipp_plants_are_included(self):
        """Potomac Energy Center sits by the Loudoun data centres and will run whenever prices
        allow; Doswell, Marsh Run and Louisa serve zonal load too."""
        p = assumptions.GAS_PLANT_CAPACITY_MW
        for name in ('Marsh Run Generation Facility', 'Louisa Generation Facility'):
            assert name in p

    def test_apco_territory_is_excluded(self):
        """Clinch River, Wolf Hills and Buchanan are in Appalachian Power's zone, not DOM."""
        p = assumptions.GAS_PLANT_CAPACITY_MW
        for name in ('Clinch River', 'Wolf Hills Energy', 'Buchanan Generation LLC'):
            assert name not in p

    def test_chp_is_excluded(self):
        """Industrial and IPP CHP run to serve host steam loads, not economic dispatch. Including
        them would imply a dispatch decision their operators do not make."""
        p = assumptions.GAS_PLANT_CAPACITY_MW
        for name in ('Hopewell Cogeneration', 'Celanese Acetate LLC', 'Virginia Tech Power Plant'):
            assert name not in p


class TestScenarioCapReconciliation:
    """Two independent gas limits were applied with whichever bound first governing, and nobody
    deciding which should. reconcile_with_scenario_cap() makes that visible."""

    def test_reconciliation_reports_which_limit_binds(self):
        import driver as drv
        m = GasMeritOrder()
        r = m.reconcile_with_scenario_cap(2030, drv.schedule_b_baseline_mw(2030) + 2862.0, 2862.0)
        assert r['binding'] in ('stack', 'scenario_cap')
        assert r['scenario_existing_cap_mw'] == pytest.approx(9362.0)

    def test_the_direction_flips_between_checkpoints(self):
        """2030-2040 the stack binds; 2045 the cap does. The cause is that they use DIFFERENT
        RETIREMENT SCHEDULES -- the stack applies Schedule A (Bear Garden 2041, Warren County
        2044), schedule_b_baseline_mw applies Schedule B's VCEA-driven 2045 drop to 1,860 MW. One
        model, two retirement futures."""
        import driver as drv
        m = GasMeritOrder()
        b = {y: m.reconcile_with_scenario_cap(y, drv.schedule_b_baseline_mw(y) + 2862.0,
                                              2862.0)['binding']
             for y in (2030, 2045)}
        assert b[2030] != b[2045], 'the flip is the finding; if it stops flipping, check why'

    def test_new_build_without_a_rung_is_flagged(self):
        """Before 2026-09-13 the pool had no rung and could not dispatch. The flag stays so a
        future change that drops the rung is visible rather than silent."""
        import driver as drv
        m = GasMeritOrder(include_new_build=False)
        r = m.reconcile_with_scenario_cap(2030, 12_224.0, 2862.0)
        assert r['new_build_has_no_rung'] is True
        assert 'NO RUNG' in r['note']

    def test_doswell_mismatch_is_documented(self):
        """Schedule B's 2045 figure of 1,860 MW is Chesterfield + Doswell + Possum Point, and
        Doswell is an IPP. It is in this stack's DOM-zone scope but not in a Dominion-owned
        schedule, so the two are not counting the same fleet."""
        import re
        from gas_merit_order import GasMeritOrder as G
        src = re.sub(r'\s*\n\s*#?\s*', ' ', open(G.__module__ and
                     __import__('gas_merit_order').__file__).read())
        assert 'DOSWELL IS AN IPP' in src
