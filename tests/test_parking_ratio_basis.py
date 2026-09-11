"""
test_parking_ratio_basis.py

Tests parking_ratio_basis.py, which replaces per-capita parking extrapolation with a
C&I-footprint ratio typed by development pattern.

Several tests here lock LIMITATIONS rather than capabilities -- that no confidence interval is
offered, that a development type cannot be defaulted, that the basis warning travels with every
result. Those are the properties most likely to be eroded by a well-meaning later edit, and the
ones whose loss would do the most damage: a two-anchor estimate presented without its caveat is
worse than no estimate.
"""
import pytest

import parking_ratio_basis as prb


class TestAnchorsAreTheTwoRealMeasurements:
    """Only two Virginia jurisdictions have BOTH a measured C&I footprint and a measured parking
    area. Every other combination is blocked structurally: Loudoun and Richmond have parking but
    no usable C&I classification; Chesapeake and Prince William have C&I but publish no parking
    layer."""

    def test_exactly_two_anchors_one_per_type(self):
        assert len(prb.ANCHORS) == 2
        assert set(prb.ANCHORS) == {prb.SURFACE_PARKED, prb.STRUCTURED}

    def test_fairfax_anchors_surface_parked(self):
        a = prb.ANCHORS[prb.SURFACE_PARKED]
        assert a.name == 'Fairfax County'
        assert a.ratio == pytest.approx(3.97, abs=0.02)

    def test_arlington_anchors_structured(self):
        a = prb.ANCHORS[prb.STRUCTURED]
        assert a.name == 'Arlington County'
        assert a.ratio == pytest.approx(0.86, abs=0.02)

    def test_the_two_types_differ_by_roughly_four_and_a_half_times(self):
        """The spread is the whole reason type classification matters more than anything else in
        this module -- misclassifying a jurisdiction dominates every other source of error."""
        ratio = prb.ratio_for_type(prb.SURFACE_PARKED) / prb.ratio_for_type(prb.STRUCTURED)
        assert 4.0 < ratio < 5.0

    def test_fairfax_parking_is_the_CORRECTED_unfiltered_figure(self):
        """1,777 acres across paved and unpaved, not the superseded 1,298 acres from paved-only
        filtered at 6,000 sqft. Fairfax fragments its lots, so that threshold discarded real
        parking area rather than excluding noise."""
        a = prb.ANCHORS[prb.SURFACE_PARKED]
        assert a.parking_sqft / prb.SQFT_PER_ACRE == pytest.approx(1_777, abs=5)
        assert 'UNPAVED' in a.parking_source


class TestTypeCannotBeGuessed:
    """Rule 5. With a 4.6x spread between types, a default would silently dominate the error in
    any figure produced."""

    def test_unknown_type_raises(self):
        with pytest.raises(ValueError, match='unknown development type'):
            prb.ratio_for_type('suburban-ish')

    def test_the_error_explains_why_there_is_no_default(self):
        with pytest.raises(ValueError, match='4.6x'):
            prb.ratio_for_type('')

    def test_estimate_requires_an_explicit_type(self):
        with pytest.raises(TypeError):
            prb.estimate_parking_from_ci('Somewhere', 10_000_000.0)


class TestEstimation:
    def test_hand_computed_surface_parked(self):
        e = prb.estimate_parking_from_ci('Test', 10_000_000.0, prb.SURFACE_PARKED)
        assert e.estimated_parking_sqft == pytest.approx(10_000_000.0 * 3.97, rel=0.01)
        assert e.anchor_used == 'Fairfax County'

    def test_structured_yields_far_less_parking_for_the_same_floorspace(self):
        surface = prb.estimate_parking_from_ci('A', 10_000_000.0, prb.SURFACE_PARKED)
        structured = prb.estimate_parking_from_ci('B', 10_000_000.0, prb.STRUCTURED)
        assert structured.estimated_parking_sqft < surface.estimated_parking_sqft / 4

    def test_zero_or_negative_footprint_raises(self):
        with pytest.raises(ValueError, match='must be positive'):
            prb.estimate_parking_from_ci('Test', 0.0, prb.SURFACE_PARKED)


class TestLimitationsTravelWithEveryResult:
    """The properties most likely to be lost to a later tidy-up, and the most damaging to lose."""

    def test_every_estimate_carries_the_basis_warning(self):
        e = prb.estimate_parking_from_ci('Test', 1_000_000.0, prb.SURFACE_PARKED)
        assert e.warning
        assert 'single anchor per development type' in e.warning

    def test_warning_states_no_confidence_interval_should_be_inferred(self):
        """With one anchor per type there is no within-type variance. Offering an interval would
        imply a sample that does not exist."""
        w = prb.basis_warning()
        assert 'no confidence interval' in w and 'none should be inferred' in w

    def test_warning_states_no_site_survey(self):
        assert 'No site survey' in prb.basis_warning()
        assert 'shading' in prb.basis_warning()

    def test_no_result_field_offers_a_range(self):
        """A later edit adding low/high fields would imply a distribution from two points."""
        e = prb.estimate_parking_from_ci('Test', 1_000_000.0, prb.SURFACE_PARKED)
        for forbidden in ('low', 'high', 'confidence', 'p05', 'p95', 'std'):
            assert not any(forbidden in f for f in e.__dataclass_fields__), (
                f"a field containing {forbidden!r} implies a distribution that two anchors "
                f"cannot support")


class TestMeasuredAndEstimatedStaySeparable:
    def test_measured_is_flagged(self):
        m = prb.measured('Richmond City', 136_264_994.0)
        assert m.is_measured is True
        assert m.anchor_used == 'none -- measured directly'

    def test_estimated_is_flagged(self):
        e = prb.estimate_parking_from_ci('Test', 1_000_000.0, prb.STRUCTURED)
        assert e.is_measured is False

    def test_measured_still_carries_the_site_survey_caveat(self):
        """Measurement removes the extrapolation uncertainty, not the shading one."""
        m = prb.measured('Richmond City', 136_264_994.0)
        assert 'no extrapolation' in m.warning
        assert 'No site survey' in m.warning

    def test_richmond_measured_acres_match_the_recorded_figure(self):
        m = prb.measured('Richmond City', 136_264_994.0)
        assert m.estimated_parking_acres == pytest.approx(3_128, abs=5)
