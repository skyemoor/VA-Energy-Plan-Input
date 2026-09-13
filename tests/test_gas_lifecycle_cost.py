"""
test_gas_lifecycle_cost.py

Full lifecycle gas costing: capital on NEW build only, fixed and variable on everything that runs.

WHY. Scenario 2 -- the whitepaper's baseline -- dispatched gas against a non-binding ceiling and
carried fuel and VOM only. Its 22,478 MW peak at 2045 appeared for free, which flatters the
baseline in the direction a reviewer will attack. But charging capital on all 22,478 MW would bill
Dominion for plant that already exists and is already paid for.
"""
import pytest

import assumptions
from gas_lifecycle_cost import (CCGT_CAPEX_KW, CT_CAPEX_KW, estimate_technology_crossover_cf,
                                gas_lifecycle_cost)
from gas_merit_order import GasMeritOrder


def s2_2045(basis='central'):
    import lp_model as lp
    return gas_lifecycle_cost(
        2045, peak_gas_mw=22_478.0,
        existing_available_mw=GasMeritOrder().total_available_mw(2045),
        generation_mwh=122.9e6,
        marginal_cost_mwh=lp.gas_cost_mwh(2045, heat_rate=lp.CCGT_HEAT_RATE) + 3.0,
        capex_basis=basis)


class TestExistingFleetIsRecognised:
    """The distinction the module exists to make."""

    def test_capital_is_charged_only_above_existing_availability(self):
        c = s2_2045()
        assert c.new_build_mw == pytest.approx(22_478.0 - c.existing_available_mw, abs=1.0)
        assert c.new_build_mw == pytest.approx(10_262, abs=50)

    def test_existing_capacity_carries_fom_but_not_capex(self):
        """An already-paid-for plant still costs money to keep available, but its capital is sunk.
        Charging capex on it would bill Dominion twice."""
        c = s2_2045()
        assert c.fom_existing_usd > 0
        assert c.annualised_capex_usd == pytest.approx(
            c.new_build_mw * 1000 * CCGT_CAPEX_KW['central'] * 0.06744, rel=0.01)

    def test_peak_below_existing_needs_no_new_build(self):
        """A real and reportable outcome, not an error -- but a NEGATIVE increment would silently
        produce a capital credit, so it clamps at zero rather than going negative."""
        c = gas_lifecycle_cost(2045, peak_gas_mw=5_000.0, existing_available_mw=12_216.0,
                               generation_mwh=10e6, marginal_cost_mwh=50.0)
        assert c.new_build_mw == 0.0
        assert c.annualised_capex_usd == 0.0


class TestCapexBand:
    """A single point figure is not defensible in a market that moved 2-3x in two years."""

    def test_central_is_2500(self):
        assert CCGT_CAPEX_KW['central'] == 2_500.0

    def test_band_brackets_the_central(self):
        assert CCGT_CAPEX_KW['low'] < CCGT_CAPEX_KW['central'] < CCGT_CAPEX_KW['high']

    def test_ct_capex_comes_from_the_sourced_tier_table(self):
        """'medium' is the 100-250 MW classic single new peaker scale -- the relevant unit size
        for filling a capacity gap."""
        assert CT_CAPEX_KW == assumptions.PEAKER_CAPEX_KW_BY_TIER['medium']

    def test_invalid_basis_raises(self):
        with pytest.raises(ValueError, match='no default worth guessing'):
            s2_2045(basis='best_guess')

    def test_capital_share_across_the_band(self):
        """BASELINE LOCKED 2026-09-13. Capital is 18-26% of the annual gas bill depending on the
        capex case -- large enough that omitting it materially understated the baseline."""
        for basis, expected in (('low', 0.182), ('central', 0.218), ('high', 0.263)):
            assert s2_2045(basis).capital_share == pytest.approx(expected, abs=0.01)


class TestTechnologyCrossover:

    def test_crossover_across_the_band(self):
        """BASELINE LOCKED 2026-09-13: 23.7% / 28.1% / 33.2% at low / central / high.

        CORRECTS AN EARLIER ESTIMATE OF 41%, which used $3,000/kW CCGT against a guessed $1,200/kW
        CT and omitted FOM entirely."""
        for basis, expected in (('low', 0.237), ('central', 0.281), ('high', 0.332)):
            assert estimate_technology_crossover_cf(2045, basis, basis) == pytest.approx(
                expected, abs=0.01)

    def test_mismatched_bases_move_the_crossover_enormously(self):
        """The reason both bases are explicit arguments. Pairing CCGT 'high' with CT 'low' gives
        51.0%; the reverse gives 5.9%. A crossover reported without stating both bases is
        uninterpretable."""
        assert estimate_technology_crossover_cf(2045, 'high', 'low') > 0.45
        assert estimate_technology_crossover_cf(2045, 'low', 'high') < 0.10

    def test_scenario2_fleet_average_sits_above_the_crossover(self):
        """122.9 TWh from 22,478 MW is a 62.4% fleet-average capacity factor, comfortably above
        even the high-case crossover -- so CCGT is right ON AVERAGE for Scenario 2's gas.

        That says nothing about the MARGINAL units serving evening peaks, which run far below the
        average and would be better served by CT. An average cannot answer a marginal question,
        which is why the LP must make the choice endogenously."""
        fleet_cf = 122.9e6 / (22_478.0 * 8760)
        assert fleet_cf == pytest.approx(0.624, abs=0.01)
        assert fleet_cf > estimate_technology_crossover_cf(2045, 'high', 'high')

    def test_no_crossover_raises_rather_than_returning_a_number(self):
        """If CCGT were not cheaper on marginal cost there would be no capacity factor at which its
        higher capital is repaid, and any returned figure would be meaningless."""
        with pytest.raises(ValueError, match='no capacity factor at which'):
            estimate_technology_crossover_cf(2045, ccgt_marginal_mwh=90.0, ct_marginal_mwh=50.0)


class TestConstantsLiveInAssumptions:
    """Rule 6.1 and 6.3, after a violation found 2026-09-13.

    CCGT_CAPEX_KW was added to gas_lifecycle_cost.py on 2026-09-12 without checking assumptions.py
    first. It collided with lp_model.CCGT_CAPEX_KW -- a SUPERSEDED SCALAR of $1,775/kW, kept under
    a _DO_NOT_USE_SUPERSEDED name and then re-aliased to the plain name one line later, which undid
    the rename entirely. Two live constants, one name, one a scalar and one a dict; whichever
    module a caller imported from decided which they got.
    """

    def test_bands_are_defined_in_assumptions(self):
        assert hasattr(assumptions, 'CCGT_CAPEX_KW_BY_CASE')
        assert hasattr(assumptions, 'CT_CAPEX_KW_BY_CASE')

    def test_this_module_re_exports_rather_than_redefining(self):
        assert CCGT_CAPEX_KW is assumptions.CCGT_CAPEX_KW_BY_CASE

    def test_the_superseded_scalar_no_longer_has_a_plain_alias(self):
        """The warning name is retained; the plain alias that defeated it is gone."""
        import lp_model
        assert not hasattr(lp_model, 'CCGT_CAPEX_KW'), 'the ambiguous alias has returned'
        assert hasattr(lp_model, 'CCGT_CAPEX_KW_DO_NOT_USE_SUPERSEDED')

    def test_named_by_case_to_avoid_the_collision(self):
        """Rule 7.2: a longer self-documenting name over a shorter ambiguous one. _BY_CASE also
        signals a dict rather than a scalar, which was half the original confusion."""
        assert 'BY_CASE' in 'CCGT_CAPEX_KW_BY_CASE'
        assert isinstance(assumptions.CCGT_CAPEX_KW_BY_CASE, dict)
