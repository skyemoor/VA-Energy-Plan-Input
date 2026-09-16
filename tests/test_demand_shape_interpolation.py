"""
test_demand_shape_interpolation.py

Hourly demand for any year 2026-2045, for the intermediate-year dispatch-only re-solves an SLCOE
needs.

THE MODULE WAS UNUSABLE UNTIL 2026-09-13. _load_base_shape() read a hardcoded path to a
`_formatted` variant carrying DateTime/MWh columns -- a file not present in the repository -- so it
raised on every call. paths.py already warned that this dataset's aliases mean "same dataset,
different filename, NOT same layout", and the layout actually available is wide: Year, Month, Day,
1..24. An orphaned-module check found it referenced only by a test.
"""
import numpy as np
import pytest

import demand_shape_interpolation as dsi


class TestBaseShapeLoads:

    def test_it_loads_from_the_layout_we_actually_have(self):
        s = dsi._load_base_shape()
        assert len(s) == 8760

    def test_it_normalises_to_exactly_one(self):
        assert dsi._load_base_shape().sum() == pytest.approx(1.0, abs=1e-12)

    def test_it_is_not_already_flat(self):
        """If the base shape were flat, the whole flattening mechanism would be a no-op and the
        module would be doing nothing."""
        s = dsi._load_base_shape()
        assert s.max() > s.min() * 1.5

    def test_hours_stay_in_chronological_order(self):
        """Melting the wide layout preserves order only if sorted on (Month, Day, hour). Sorting on
        the melted column LABEL would interleave hour 10 between 1 and 2, since the labels are
        strings -- and the result would look like a plausible load shape."""
        s = dsi._load_base_shape()
        daily_peak_hour = [int(np.argmax(s[d * 24:(d + 1) * 24])) for d in range(365)]
        # A correctly ordered shape peaks in the afternoon/evening on most days. A string-sorted
        # one would scatter the peak across the day.
        afternoon = sum(1 for h in daily_peak_hour if 11 <= h <= 21)
        assert afternoon > 250, f'only {afternoon}/365 days peak in the afternoon -- check ordering'


class TestFlattening:
    """Data centres run a near-constant 24x7x365 profile, and their share of DOM LSE sales grows
    through the horizon -- so the true hourly shape should genuinely flatten over time, not just
    scale up. A static shape for 2045 would understate how flat 2045's load really is."""

    def test_alpha_rises_across_the_horizon(self):
        assert dsi.data_center_flattening_alpha(2026) < dsi.data_center_flattening_alpha(2045)

    def test_alpha_is_floored_at_zero(self):
        """Years at or below the 2023 baseline get no adjustment, not a negative one -- which would
        imply un-flattening, and the project has no basis to model that."""
        assert dsi.data_center_flattening_alpha(2018) >= 0.0

    def test_flattening_reduces_the_peak(self):
        """The measurable consequence: the same annual energy in a flatter shape has a lower peak."""
        early = dsi.flattened_hourly_demand(2026, 100_000.0)
        late = dsi.flattened_hourly_demand(2045, 100_000.0)
        assert late.max() < early.max()
        assert late.sum() == pytest.approx(early.sum())

    def test_annual_total_is_matched_exactly(self):
        """The total is PASSED IN, not looked up -- so this function has no silent dependency on
        which demand vintage the caller uses. That was a deliberate design decision, and it is why
        the module's own _COMMERCIAL_AND_TOTAL_GWH table (a different, lower vintage) does not
        contaminate callers."""
        for total in (100_000.0, 202_193.0):
            assert dsi.flattened_hourly_demand(2040, total).sum() / 1000 == pytest.approx(total)

    def test_shape_stays_positive(self):
        assert dsi.flattened_hourly_demand(2045, 202_193.0).min() > 0


class TestFailsLoudly:
    def test_missing_base_year_raises_with_the_available_years(self):
        saved = dsi.BASE_SHAPE_YEAR
        dsi._BASE_SHAPE_NORMALIZED = None
        try:
            dsi.BASE_SHAPE_YEAR = 1999
            with pytest.raises(ValueError, match='available'):
                dsi._load_base_shape()
        finally:
            dsi.BASE_SHAPE_YEAR = saved
            dsi._BASE_SHAPE_NORMALIZED = None


class TestItIsSupersededAndWhy:
    """Confirmed 2026-09-13. The module ages a SINGLE fixed shape forward; the demand stage now
    builds every year directly from Dominion's own projections, which carry a different shape per
    year and already flatten."""

    def test_the_source_projection_flattens_on_its_own(self):
        """Dominion's forecast embeds data-centre growth, so the load factor rises without any
        adjustment from this module."""
        import demand_basis as db
        lfs = {}
        for y in (2030, 2037, 2045):
            a = db.VirginiaOnlyGeneration(y).hourly_mw()
            lfs[y] = a.mean() / a.max()
        assert lfs[2030] < lfs[2037] < lfs[2045]
        assert lfs[2045] == pytest.approx(0.794, abs=0.01)

    def test_applying_the_module_would_make_the_shape_LESS_flat(self):
        """The measurement that settles it: the module reaches LF 0.712 at 2045, against the source
        projection's own 0.794. The adjustment runs backwards, because the input it was designed
        for no longer arrives unflattened."""
        import demand_basis as db
        source = db.VirginiaOnlyGeneration(2045).hourly_mw()
        adjusted = dsi.flattened_hourly_demand(2045, source.sum() / 1000)
        assert adjusted.mean() / adjusted.max() < source.mean() / source.max()
        assert adjusted.max() > source.max()

    def test_the_source_covers_every_year_so_no_interpolation_is_needed(self):
        """2026-2045 with a full year of hours each -- the intermediate years an SLCOE needs come
        from the same place the checkpoints do."""
        import demand_basis as db
        for y in (2026, 2031, 2042):
            assert len(db.VirginiaOnlyGeneration(y).hourly_mw()) == 8760

    def test_the_supersession_is_documented_in_the_module(self):
        """Rule 10.3: a future reader must not wire it in believing it is the missing piece."""
        assert 'SUPERSEDED 2026-09-13' in dsi.__doc__
        assert 'DO NOT WIRE IT INTO A SOLVE PATH' in dsi.__doc__
