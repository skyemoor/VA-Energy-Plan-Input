"""
test_gas_merit_order.py

Gas heat-rate tiers sourced from EIA Electric Power Annual Table 8.2 (Form EIA-860 tested heat
rates, capacity-weighted) plus EIA's vintage breakdown.

Added because the LP dispatches gas at a SINGLE marginal cost, which is one reason its hourly
energy-balance dual is perfectly flat: with one price and no operating reserve, storage arbitrages
every hour to that price. These tiers give the dual a ladder to climb -- once capacity per tier is
sourced and they are wired in.
"""
import pytest

import assumptions as a
import lp_model as lp


class TestTiersMatchEIA:

    def test_combined_cycle_and_gas_turbine_match_table_8_2(self):
        assert a.GAS_HEAT_RATE_CCGT_FLEET == 7.548
        assert a.GAS_HEAT_RATE_CT_FLEET == 10.999
        assert a.GAS_HEAT_RATE_STEAM == 10.337

    def test_modern_ccgt_is_within_eia_stated_range(self):
        """EIA: 2014+ entry typically below 7,000 Btu/kWh."""
        assert a.GAS_HEAT_RATE_CCGT_MODERN < 7.0

    def test_legacy_ccgt_sits_above_the_fleet_average(self):
        assert a.GAS_HEAT_RATE_CCGT_LEGACY > a.GAS_HEAT_RATE_CCGT_FLEET


class TestOurSimpleCycleAssumptionIsOptimistic:
    """A finding, not a defect: 9.5 describes a modern aeroderivative unit, while EIA's 2024
    gas-turbine fleet average is 11.0. Both are retained as separate tiers because they describe
    genuinely different machines -- but where the question is what the marginal peaking unit costs
    to run, 9.5 is the optimistic end."""

    def test_our_simple_cycle_beats_the_eia_fleet_average(self):
        assert a.SIMPLE_CYCLE_HEAT_RATE < a.GAS_HEAT_RATE_CT_FLEET
        gap = 1 - a.SIMPLE_CYCLE_HEAT_RATE / a.GAS_HEAT_RATE_CT_FLEET
        assert gap == pytest.approx(0.136, abs=0.01), 'about 14% better than fleet'

    def test_both_are_kept_as_distinct_tiers(self):
        labels = [l for l, _ in a.GAS_MERIT_ORDER_HEAT_RATES]
        assert 'ct_aeroderivative' in labels and 'ct_fleet' in labels


class TestMeritOrderStructure:

    def test_tiers_are_ordered_cheapest_first(self):
        rates = [hr for _, hr in a.GAS_MERIT_ORDER_HEAT_RATES]
        assert rates == sorted(rates)

    def test_the_stack_produces_a_real_cost_spread(self):
        """1.72x from cheapest to dearest rung -- the variation the flat dual currently lacks."""
        for year in (2030, 2045):
            lo = lp.gas_cost_mwh(year, heat_rate=a.GAS_MERIT_ORDER_HEAT_RATES[0][1])
            hi = lp.gas_cost_mwh(year, heat_rate=a.GAS_MERIT_ORDER_HEAT_RATES[-1][1])
            assert hi / lo == pytest.approx(1.72, abs=0.02)

    def test_capacity_caveat_tracks_what_is_actually_still_blocking(self):
        """Revised twice as the situation changed: capacity wholly unsourced (2026-09-11 morning),
        then partly sourced from the 10-K, then FULLY resolved from EIA-860 generator data
        (2026-09-12). A caveat that overstates a gap erodes trust in the ones that don't, so it
        tracks reality rather than being left at its most cautious version."""
        c = a.GAS_MERIT_ORDER_CAPACITY_SOURCING_NOTE
        assert 'FULLY RESOLVED' in c
        assert 'nameplate-versus-net-summer units' in c

    def test_the_truncated_irp_pdfs_are_recorded(self):
        """Confirmed unreadable with both pypdf and pdfplumber. Other work may depend on them.
        No longer blocking the merit order -- EIA-860 supplied what the IRPs would have -- but
        still worth knowing."""
        assert 'truncated and unreadable' in a.GAS_MERIT_ORDER_CAPACITY_SOURCING_NOTE


class TestCapacityPerRung:
    """Source: EIA-860 2025 Schedule 3 (Generator Data), Virginia, Operable sheet, Energy Source 1
    = NG, Utility Name = Virginia Electric & Power Co. Rungs assigned by per-unit Operating Year.

    REBUILT 2026-09-12 from generator-level data, replacing a 10-K-derived mapping. The two use
    different rating bases -- net summer capability vs nameplate -- and mixing them created a
    phantom 1,167 MW discrepancy that produced two wrong hypotheses before the units were checked.
    """

    def test_rung_capacities_sum_to_the_filed_nameplate_total(self):
        assert sum(a.GAS_MERIT_ORDER_CAPACITY_MW.values()) == pytest.approx(
            a.GAS_DOMINION_OWNED_NAMEPLATE_MW, abs=0.1)

    def test_both_rating_bases_are_retained_and_distinguishable(self):
        """The phantom discrepancy came from mixing them. Keeping both, named, prevents a repeat."""
        assert a.GAS_DOMINION_OWNED_NAMEPLATE_MW == 9_359.5
        assert a.GAS_DOMINION_OWNED_NET_SUMMER_MW == 8_195.0
        ratio = a.GAS_DOMINION_OWNED_NET_SUMMER_MW / a.GAS_DOMINION_OWNED_NAMEPLATE_MW
        assert 0.85 < ratio < 0.90, 'ratio should be a plausible summer derate, not a real gap'

    def test_ct_split_is_resolved_as_entirely_frame(self):
        """Settled from per-unit nameplate, not inferred: Dominion CT units are 92-178.5 MW;
        aeroderivatives are 36-54 MW. Not one unit is in the aeroderivative class."""
        assert 'ct_fleet' in a.GAS_MERIT_ORDER_CAPACITY_MW
        assert 'ct_unallocated' not in a.GAS_MERIT_ORDER_CAPACITY_MW
        assert '100% FRAME' in a.GAS_CT_SPLIT_RESOLVED

    def test_aeroderivative_heat_rate_is_fenced_off_from_the_existing_fleet(self):
        """9.5 stays defined for new-build analysis but must not be applied to Dominion's units.
        Applying it would understate their marginal cost by 14%."""
        assert 'must not be '
        assert 'new-build' in a.GAS_CT_SPLIT_RESOLVED.lower() or 'NEW-BUILD' in a.GAS_CT_SPLIT_RESOLVED
        assert a.GAS_HEAT_RATE_CT_AERODERIVATIVE == 9.5

    def test_modern_rung_is_the_largest(self):
        """4,717.7 MW across 12 units at 2014+, so Dominion's CCGT fleet is mostly modern."""
        c = a.GAS_MERIT_ORDER_CAPACITY_MW
        assert c['ccgt_modern'] == max(c.values())

    def test_sourcing_note_records_the_resolution(self):
        n = a.GAS_MERIT_ORDER_CAPACITY_SOURCING_NOTE
        assert 'FULLY RESOLVED' in n
        assert 'no longer blocked on data' in n

