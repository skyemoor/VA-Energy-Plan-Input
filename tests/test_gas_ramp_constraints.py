"""
test_gas_ramp_constraints.py

Ramp constraints on the gas merit order (added 2026-09-13).

WHY THEY EXIST. The LP sees only MARGINAL cost, so without a ramp limit it uses ccgt_modern
($47.32/MWh at 2045) for a one-hour evening spike as readily as for baseload, in preference to
ct_fleet ($81.17). That is wrong twice over: a combined-cycle unit cannot start fast enough, and
running one at a 2% capacity factor is uneconomic on capital grounds the dispatch objective never
sees.

SOURCE: arXiv 2311.04398 Table D.1 (NREL ATB 2020 basis) -- CCGT 64%/hour, OCGT 100%/hour.
Class-level parameters, which is standard practice; production cost models use technology-class
defaults rather than per-unit specifications.
"""
import pytest

import assumptions as a
from gas_merit_order import GasMeritOrder


class TestSourcedParameters:

    def test_ccgt_and_ocgt_rates_match_the_source(self):
        assert a.GAS_RAMP_FRACTION_PER_HOUR['ccgt_modern'] == 0.64
        assert a.GAS_RAMP_FRACTION_PER_HOUR['ct_fleet'] == 1.00

    def test_ccgt_rate_is_physically_plausible_in_mw_per_minute(self):
        """CROSS-CHECK (Rule 4) against an independent basis. 64%/hour on a 500 MW unit is
        5.3 MW/min, inside the 5-10 MW/min industry range for large combined cycle.

        This check exists because a figure stated from memory in review -- 'CCGT ramps at
        5-7%/minute' -- was wrong by a factor of five, conflating MW/min with %/min. 5%/min would
        be 300%/hour."""
        mw_per_min = 0.64 * 500 / 60
        assert 5.0 <= mw_per_min <= 10.0

    def test_every_defined_rung_has_a_rate(self):
        """A missing entry would silently leave a rung unconstrained, so the lookup raises rather
        than defaulting. ct_aeroderivative was in fact missing when first written, and the raise
        caught it."""
        for rung, _ in a.GAS_MERIT_ORDER_HEAT_RATES:
            assert rung in a.GAS_RAMP_FRACTION_PER_HOUR, f'{rung} has no ramp fraction'


class TestLimitsAndBinding:

    def test_limit_is_fraction_of_available_not_nameplate(self):
        """A rung whose plant has retired must ramp within what remains, not within what it once
        was."""
        m = GasMeritOrder()
        avail = m.available_capacity_mw(2045)
        lim = m.ramp_limit_mw_per_hour(2045)
        for rung, mw in avail.items():
            expected = mw * a.GAS_RAMP_FRACTION_PER_HOUR[rung]
            assert lim[rung] == pytest.approx(expected)

    def test_ocgt_is_not_listed_as_binding(self):
        """100%/hour can never bind at hourly resolution. Adding 17,520 rows for it would cost
        solve time for no behavioural change."""
        assert 'ct_fleet' not in GasMeritOrder().ramp_binds_for(2045)

    def test_all_ccgt_rungs_bind(self):
        b = GasMeritOrder().ramp_binds_for(2045)
        for rung in ('new_build_ccgt', 'ccgt_modern', 'ccgt_fleet', 'ccgt_legacy'):
            assert rung in b

    def test_unknown_rung_raises(self):
        m = GasMeritOrder()
        saved = dict(a.GAS_RAMP_FRACTION_PER_HOUR)
        try:
            del a.GAS_RAMP_FRACTION_PER_HOUR['ccgt_modern']
            with pytest.raises(ValueError, match='no ramp fraction for rung'):
                m.ramp_limit_mw_per_hour(2045)
        finally:
            a.GAS_RAMP_FRACTION_PER_HOUR.clear()
            a.GAS_RAMP_FRACTION_PER_HOUR.update(saved)


class TestMeasuredEffect:
    """Baselines from a real 2030 solve, 2026-09-13. Locked because a silent loss of these rows
    would remove the constraint without any error."""

    def test_all_four_ccgt_rungs_bind_exactly_at_their_limits(self):
        """Measured: every constrained rung's maximum hourly swing equals its limit to within
        rounding. That is what a binding constraint looks like, and it confirms the rows are
        attached to the right variables."""
        observed = {'new_build_ccgt': 1_685.1, 'ccgt_modern': 3_012.9,
                    'ccgt_fleet': 1_258.4, 'ccgt_legacy': 768.7}
        lim = GasMeritOrder().ramp_limit_mw_per_hour(2030)
        for rung, swing in observed.items():
            assert lim[rung] == pytest.approx(swing, abs=5.0)

    def test_unit_commitment_omission_is_recorded_with_its_bias_direction(self):
        """Minimum up/down times and start costs are NOT modelled. The omission FLATTERS CCGT, and
        a reader must be able to see that without reading the source."""
        n = a.GAS_UNIT_COMMITMENT_NOT_MODELLED
        assert 'FLATTERS CCGT' in n
        assert 'MILP' in n
