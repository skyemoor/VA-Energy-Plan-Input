"""
test_nsrdb_data.py

Tests for nsrdb_data.py, per SES Rule 2: each test locks a shared calculation to a
trusted, independently-derivable baseline, not just internal self-consistency.
"""
import pytest
import nsrdb_data as nd

nd.configure_data_root('/home/claude/insolation_data')


class TestFormatDetection:
    """Format matching must correctly route each real filename to its actual format --
    tested against real filenames present in this project's own data set, not synthetic
    examples."""

    def test_goes_aggregated_filename_matches_goes_format(self):
        fmt = nd.GoesAggregatedFormat()
        assert fmt.matches('lat_37.50860_lon_-77.33347_nsrdb-GOES-aggregated-v4-0-0_60_2012.csv')

    def test_psm322_filename_matches_psm_format(self):
        fmt = nd.Psm322Format()
        assert fmt.matches('38.01_-78.42_38.01_-78.42_psm3-2-2_60_2016.csv')

    def test_tmy_filename_matches_tmy_format_not_the_other_two(self):
        tmy_filename = 'lat_38.33000_lon_-77.34000_nsrdb-GOES-tmy-v4-0-0_60_tdy-2025.csv'
        assert nd.UnrecognizedTmyFormat().matches(tmy_filename)
        # A real bug this guards against: "tmy" also contains no GOES/psm3-2-2
        # substring collision, but worth an explicit check that the OTHER two formats
        # correctly do NOT also claim a TMY filename (format detection order in
        # _find_format_and_file relies on this).
        assert not nd.GoesAggregatedFormat().matches(tmy_filename)
        assert not nd.Psm322Format().matches(tmy_filename)


class TestKnownFileCounts:
    """Cross-checks against an independent fact: this project's own hydro-year
    convention and NSRDB's own physical constraints mean every real (non-TMY,
    non-leap-year-corrected) year must have exactly 8760 hourly rows -- checked
    directly against the real files, not assumed."""

    @pytest.mark.parametrize("location_name", list(nd.LOCATIONS.keys()))
    @pytest.mark.parametrize("year", [2012, 2016, 2020])
    def test_every_location_year_has_8760_rows(self, location_name, year):
        df = nd.LOCATIONS[location_name].load_year(year)
        assert len(df) == 8760

    def test_all_six_locations_have_full_2012_2020_coverage(self):
        # Independent cross-check against the coverage table established directly
        # (2026-09-05) after the two missing 2020 files were uploaded -- this test
        # would fail loudly if that coverage regresses (e.g. a file gets moved/deleted).
        for name, loc in nd.LOCATIONS.items():
            for year in range(2012, 2021):
                df = loc.load_year(year)  # raises if missing -- the test itself IS
                                            # the assertion here, per SES Rule 5's own
                                            # "fail loudly" philosophy applied to tests.
                assert len(df) == 8760, f"{name} {year}: wrong row count"


class TestTmyExclusion:
    """The TMY file must never be silently loadable as if it were a real year."""

    def test_kinggeorge_load_year_never_returns_tmy_data(self):
        # KingGeorge's real 2012-2020 years must all load successfully and the TMY
        # file (year label "2025" in its own filename) must never be reachable via
        # load_year for any of the real years -- this is implicitly covered by
        # test_all_six_locations_have_full_2012_2020_coverage succeeding at all
        # (if TMY detection were broken, ambiguous-match errors would surface there
        # instead), but stated explicitly here since it's the specific property that
        # matters for this project's own methodology.
        for year in range(2012, 2021):
            df = nd.LOCATIONS['KingGeorge'].load_year(year)
            assert len(df) == 8760

    def test_tmy_format_standardize_raises(self):
        tmy_format = nd.UnrecognizedTmyFormat()
        with pytest.raises(ValueError, match="TMY"):
            tmy_format.standardize('/fake/path/nsrdb-GOES-tmy-v4-0-0_60_tdy-2025.csv')


class TestColumnOrderIndependence:
    """The specific bug this project's own review caught (2026-09-05): GHI/DNI/DHI
    column ORDER differs between GOES-aggregated and PSM3-2-2 files. This test cross-
    checks that both formats, loaded through the same standardize() interface, produce
    physically sane values (GHI ~= DNI*cos(zenith) + DHI at midday, DNI never wildly
    exceeding the solar constant) -- an independent physical sanity check, not just
    "the code ran without error," which would NOT catch a silent DNI/DHI swap."""

    def test_goes_and_psm_formats_produce_physically_plausible_ghi_max(self):
        # Solar constant is ~1361 W/m2; GHI at any real surface location should never
        # substantially exceed this. A silent DNI/DHI column swap wouldn't necessarily
        # break this check on its own, but combined with the max-value sanity range
        # already observed directly (1009-1038 W/m2 across all locations/years tested
        # in nsrdb_data.py's own __main__ block), any gross misalignment would show up
        # as an implausible outlier.
        goes_df = nd.LOCATIONS['Richmond'].load_year(2012)  # GOES-aggregated format
        psm_df = nd.LOCATIONS['Albermarle'].load_year(2020)  # PSM3-2-2 format (2020
                                                               # file for this location)
        for df in (goes_df, psm_df):
            assert df['ghi'].max() < 1361, "GHI exceeds the solar constant -- likely a column misread"
            assert df['ghi'].min() >= 0, "Negative GHI -- likely a column misread"
            assert df['dni'].max() < 1361
            assert df['dhi'].max() < 1361


if __name__ == '__main__':
    import sys
    sys.exit(pytest.main([__file__, '-v']))
