"""
test_foresight_bracket.py

Tests the foresight bracketing adopted 2026-09-11 for Scenario 3 distributed arbitrage value.

Several tests lock SCOPE and CAVEATS rather than arithmetic. The bracket is defensible precisely
because it introduces no tunable parameter and because its limits travel with every result -- both
properties are easy to erode in a later edit, and either loss would turn a sound method into an
overclaim.
"""
import numpy as np
import pytest

import foresight_bracket as fb


class TestBracketArithmetic:

    def test_no_lookahead_value_is_discharge_revenue_less_charge_cost(self):
        price = [10.0, 50.0]
        assert fb.arbitrage_value_no_lookahead(price, [1.0, 0.0], [0.0, 1.0]) == pytest.approx(40.0)

    def test_length_mismatch_raises(self):
        with pytest.raises(ValueError, match='length mismatch'):
            fb.arbitrage_value_no_lookahead([1.0, 2.0], [1.0], [0.0, 1.0])

    def test_perfect_foresight_exceeds_a_naive_dispatch_on_the_same_prices(self):
        rng = np.random.default_rng(0)
        price = rng.uniform(0, 100, 8760)
        charge = np.zeros(8760); discharge = np.zeros(8760)
        charge[::4] = 1.0; discharge[1::4] = 1.0     # arbitrary, foresight-free schedule
        lo = fb.arbitrage_value_no_lookahead(price, charge, discharge)
        hi = fb.arbitrage_value_perfect_foresight(price, power_mw=1.0, energy_mwh=4.0)
        assert hi > lo

    def test_zero_power_or_energy_yields_zero(self):
        price = np.linspace(0, 100, 100)
        assert fb.arbitrage_value_perfect_foresight(price, 0.0, 4.0) == 0.0
        assert fb.arbitrage_value_perfect_foresight(price, 1.0, 0.0) == 0.0

    def test_bracket_reports_the_gap(self):
        """Physically plausible fixture: roughly daily cycling, not every-other-hour."""
        price = np.zeros(8760)
        charge = np.zeros(8760); discharge = np.zeros(8760)
        for day in range(365):
            h = day * 24
            price[h:h + 24] = 50.0
            price[h + 2:h + 6] = 10.0       # cheap overnight
            price[h + 17:h + 20] = 90.0     # dear evening
            charge[h + 2:h + 6] = 1.0
            discharge[h + 17:h + 20] = 1.0
        b = fb.bracket(2045, price, charge, discharge, power_mw=1.0, energy_mwh=4.0)
        assert b.lower_bound_usd > 0, 'fixture should be a profitable dispatch'
        assert 0.0 <= b.gap_fraction <= 1.0
        assert b.upper_bound_usd >= b.lower_bound_usd

    def test_value_destroying_dispatch_is_flagged_not_reported_as_a_percentage(self):
        """A no-lookahead operator can buy into a rising market and sell into a falling one. When
        the lower bound is negative, gap_fraction exceeds 1 and the result should be read as 'the
        signal is worse than not operating', not as a percentage shortfall."""
        price = np.tile([10.0, 90.0], 4380)
        charge = np.zeros(8760); discharge = np.zeros(8760)
        charge[1::2] = 1.0      # charges at $90
        discharge[::2] = 0.5    # discharges at $10
        b = fb.bracket(2045, price, charge, discharge, power_mw=1.0, energy_mwh=4.0)
        assert b.lower_bound_is_value_destroying is True
        assert b.gap_fraction > 1.0

    def test_envelope_allows_at_least_the_realised_cycling(self):
        """Found 2026-09-11: with a fixed cycle default, a dispatch cycling more than the default
        inverted the bracket and bracket() raised on legitimate input. The envelope must allow at
        least what actually happened, or the gap measures cycling rather than foresight."""
        price = np.tile([10.0, 90.0], 4380)
        charge = np.tile([1.0, 0.0], 4380)      # 4,380 cycles -- far above any default
        discharge = np.tile([0.0, 0.5], 4380)
        b = fb.bracket(2045, price, charge, discharge, power_mw=1.0, energy_mwh=4.0)
        assert b.envelope_cycles_per_year >= b.realised_cycles_per_year
        assert b.upper_bound_usd >= b.lower_bound_usd

    def test_inverted_bracket_raises_rather_than_reporting_a_negative_gap(self):
        """The upper bound is an envelope and cannot legitimately fall below a realised dispatch.
        If it does, the two were computed on different inputs -- which is the failure this catches."""
        price = np.full(100, 10.0)
        charge = np.zeros(100); discharge = np.full(100, 1000.0)   # implausible realised dispatch
        with pytest.raises(ValueError, match='below no-lookahead bound'):
            fb.bracket(2045, price, charge, discharge, power_mw=1.0, energy_mwh=4.0)


class TestScopeIsEnforced:
    """The bracket bounds arbitrage value. It does NOT bound reliability contribution -- Shen et
    al. show a precautionary operator may exceed perfect foresight on that metric, so perfect
    foresight is not a ceiling there."""

    def test_scope_limit_is_in_the_caveats_that_travel_with_every_result(self):
        price = np.tile([10.0, 90.0], 50)
        b = fb.bracket(2045, price, np.zeros(100), np.zeros(100), 1.0, 4.0)
        assert any('ARBITRAGE VALUE ONLY' in c for c in b.caveats)
        assert any('not a ceiling on that metric' in c for c in b.caveats)

    def test_module_documents_why_it_must_not_be_used_for_accreditation(self):
        src = open(fb.__file__).read()
        assert 'must not be used for capacity accreditation' in src
        assert 'PRECAUTIONARY' in src


class TestCaveatsCannotBeSilentlyDropped:

    def test_all_five_caveats_are_attached(self):
        price = np.tile([10.0, 90.0], 50)
        b = fb.bracket(2045, price, np.zeros(100), np.zeros(100), 1.0, 4.0)
        assert len(b.caveats) == 5

    def test_upper_bound_is_labelled_theoretical(self):
        assert any('not\nintended to represent' in c.replace('  ', ' ') or
                   'not intended to represent an estimate of the most likely value' in c
                   for c in fb.BRACKET_CAVEATS)

    def test_lower_bound_is_labelled_conservative(self):
        assert any('likely to underestimate' in c for c in fb.BRACKET_CAVEATS)

    def test_heterogeneity_is_stated_so_the_range_is_not_read_as_an_error_bar(self):
        assert any('not an error bar on a single operator' in c for c in fb.BRACKET_CAVEATS)

    def test_the_width_is_named_as_the_finding(self):
        assert any('WIDTH is itself the finding' in c for c in fb.BRACKET_CAVEATS)


class TestNoTunableParameterWasIntroduced:
    """The property that makes this defensible: there is no capacity reference and no
    price-response curve, so there is nothing for a reviewer to name as arbitrary. Round-trip
    efficiency and depth-of-discharge floor are physical constants already used elsewhere in the
    project, not choices made for this method."""

    def test_cycles_per_year_reuses_an_existing_project_constant(self):
        """Not a new knob: assumptions.NA_CYCLES_PER_YEAR_REQUIREMENT is already used by
        charging_adequacy.py. Reusing it preserves the no-new-parameter property."""
        import assumptions, numpy as np
        price = np.tile([10.0, 90.0], 4380)
        default = fb.arbitrage_value_perfect_foresight(price, 1.0, 4.0)
        explicit = fb.arbitrage_value_perfect_foresight(
            price, 1.0, 4.0, cycles_per_year=assumptions.NA_CYCLES_PER_YEAR_REQUIREMENT)
        assert default == explicit

    def test_single_cycle_defect_stays_fixed(self):
        """The first version computed one cycle across the whole year, so a daily-cycling naive
        dispatch beat the supposed ceiling. Locked so it cannot regress."""
        import numpy as np
        price = np.tile([10.0, 90.0], 4380)
        one_cycle = fb.arbitrage_value_perfect_foresight(price, 1.0, 4.0, cycles_per_year=1)
        many = fb.arbitrage_value_perfect_foresight(price, 1.0, 4.0)
        assert many > one_cycle * 100

    def test_bracket_takes_no_shape_or_threshold_parameter(self):
        import inspect
        params = set(inspect.signature(fb.bracket).parameters)
        for forbidden in ('capacity_reference', 'price_curve', 'scarcity_scale', 'threshold',
                          'knee', 'elasticity'):
            assert forbidden not in params

    def test_the_upper_bound_is_documented_as_deliberately_unreachable(self):
        """It ignores state-of-charge chronology, which overstates. That is the bound's job, and
        saying so prevents it being mistaken for a dispatch simulation."""
        src = open(fb.__file__).read()
        assert 'DELIBERATE and appropriate' in src
        assert 'It is an upper envelope.' in src
