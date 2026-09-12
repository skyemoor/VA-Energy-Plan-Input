"""
test_der_revenue_stack.py

The DER owner revenue stack. Most of these lock the ABSENCES, because the point of the module is
that unmodelled streams appear at zero WITH a reason rather than being silently missing.
"""
import pytest

from der_revenue_stack import STREAM_STATUS, build_stack


class TestUnmodelledStreamsAreVisible:

    def test_all_five_streams_appear_in_output(self):
        """Reporting only the modelled stream invites a reader to treat it as the whole answer."""
        s = build_stack(2045, 'rooftop', installed_mw=1_000.0, energy_arbitrage_usd=5_000_000.0)
        assert len(s.as_lines()) == 5

    def test_behind_the_meter_is_flagged_as_the_largest_missing_stream(self):
        """For a C&I owner it usually dominates, because it displaces RETAIL (~$80-120/MWh) rather
        than wholesale (~$40). An owner reading a wholesale-only figure would not recognise their
        own project."""
        modelled, reason = STREAM_STATUS['behind_the_meter']
        assert modelled is False
        assert 'LARGEST' in reason and 'RETAIL' in reason

    def test_net_metering_records_the_statutory_cap(self):
        """§ 56-594(E) caps aggregate net metering at ~1,740 MW, which measured canopy alone
        exceeds 2.4x -- the reason Scenario 3 routes through wholesale at all."""
        _, reason = STREAM_STATUS['net_metering_credit']
        assert '56-594' in reason and '1,740 MW' in reason

    def test_energy_arbitrage_notes_it_is_the_locational_adder(self):
        """The exogenous series is congestion plus losses; the energy component reaches the segment
        through the LP energy balance. Conflating them would double-count."""
        _, reason = STREAM_STATUS['energy_arbitrage']
        assert 'LOCATIONAL adder' in reason


class TestPJMConstraintsTravelWithTheResult:

    def test_single_node_constraint_is_in_the_caveats(self):
        """Energy aggregations must sit at ONE pricing node. The model assumes a county-wide fleet
        can bid as one block, which PJM does not permit for energy."""
        s = build_stack(2045, 'canopy', 500.0, 1_000_000.0)
        assert any('SINGLE pricing node' in c for c in s.caveats)

    def test_order_2222_timeline_is_in_the_caveats(self):
        s = build_stack(2045, 'canopy', 500.0, 1_000_000.0)
        assert any('Feb 2028' in c and 'CSP' in c for c in s.caveats)

    def test_flat_scarcity_term_is_in_the_caveats(self):
        s = build_stack(2045, 'rooftop', 500.0, 1_000_000.0)
        assert any('CV 3.99%' in c for c in s.caveats)


class TestArithmeticAndFailure:

    def test_per_kw_conversion(self):
        s = build_stack(2045, 'rooftop', installed_mw=1_000.0, energy_arbitrage_usd=10_000_000.0)
        assert s.streams_usd_per_kw_year['energy_arbitrage'] == pytest.approx(10.0)

    def test_zero_installed_raises_rather_than_returning_zero(self):
        """Revenue per kW on no capacity is undefined, not zero (Rule 5)."""
        with pytest.raises(ValueError, match='undefined, not zero'):
            build_stack(2045, 'rooftop', 0.0, 1_000.0)

    def test_unknown_stream_raises(self):
        """A stream must be declared in STREAM_STATUS with a modelled flag and a reason, so it
        cannot enter the output without its status being stated."""
        with pytest.raises(ValueError, match='unknown revenue stream'):
            build_stack(2045, 'rooftop', 100.0, 1_000.0, extra_streams={'mystery': 5.0})

    def test_supplying_a_stream_removes_it_from_unmodelled(self):
        """If a later pass models capacity revenue it lands here, not in a parallel structure."""
        s = build_stack(2045, 'rooftop', 100.0, 1_000.0, extra_streams={'capacity': 50_000.0})
        assert 'capacity' in s.streams_usd_per_kw_year
        assert 'capacity' not in s.unmodelled
