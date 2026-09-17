"""
test_distributed_profile_cache.py

The committed distributed-solar profile, and why it is committed.

A fresh clone has no NSRDB source CSVs -- they are large, public and deliberately not in the repo --
so anything needing the distributed profile failed on a missing PJMMap.webp, the marker used to
locate the data root. DATA_SOURCES.md's own rule covers this: large source data stays out, but
"derived products that are small and expensive to rebuild ARE stored".
"""
import os

import numpy as np
import pytest

import distributed_solar_profile as dsp
import paths


def _source_data_available():
    try:
        paths.source_file('PJMMap.webp')
        return True
    except Exception:
        return False


class TestTheCacheIsPresentAndComplete:
    def test_the_file_exists(self):
        assert os.path.exists(paths.weather_year(dsp.CACHED_PROFILE_FILE))

    def test_it_covers_all_eight_hydro_years(self):
        with np.load(paths.weather_year(dsp.CACHED_PROFILE_FILE)) as data:
            assert sorted(data.files) == [f'hy{y}' for y in range(2012, 2020)]

    @pytest.mark.parametrize('first_year,capacity_factor', [
        (2012, 0.1499), (2013, 0.1524), (2014, 0.1497), (2015, 0.1501),
        (2016, 0.1526), (2017, 0.1521), (2018, 0.1420), (2019, 0.1465)])
    def test_each_year_matches_its_recorded_capacity_factor(self, first_year, capacity_factor):
        profile = dsp.hydro_year_profile(first_year)
        assert len(profile) == 8760
        assert profile.mean() == pytest.approx(capacity_factor, abs=0.0001)

    def test_the_design_year_is_the_highest_of_the_eight(self):
        """So an eight-year robustness run sees about 7% less distributed output than a design-year
        solve assumes."""
        means = [dsp.hydro_year_profile(y).mean() for y in range(2012, 2020)]
        assert max(means) == pytest.approx(dsp.hydro_year_profile(2016).mean())
        assert (max(means) - min(means)) / max(means) == pytest.approx(0.07, abs=0.01)


class TestTheCacheIsACacheNotAReplacement:
    """The NSRDB path remains the definition. This is a cache of it, and they must agree."""

    @pytest.mark.skipif(not _source_data_available(),
                        reason='NSRDB source data absent -- the very case the cache exists for')
    def test_cached_and_computed_agree(self):
        cached = dsp.hydro_year_profile(2016)
        computed = dsp.hydro_year_profile(2016, _cache={})
        assert np.allclose(cached, computed)

    def test_a_non_default_site_list_always_computes(self):
        """The cache holds the five-site average and nothing else, so a different site list must
        not silently receive it."""
        import inspect
        source = inspect.getsource(dsp.hydro_year_profile)
        assert 'sites is DISTRIBUTED_SITES' in source

    def test_an_explicit_cache_argument_always_computes(self):
        """A caller passing _cache is building several years and wants the shared intermediate."""
        import inspect
        assert '_cache is None' in inspect.getsource(dsp.hydro_year_profile)


class TestWhyItIsCommitted:
    def test_it_is_small(self):
        """260 KB against hundreds of megabytes of NSRDB source."""
        size_kb = os.path.getsize(paths.weather_year(dsp.CACHED_PROFILE_FILE)) / 1024
        assert size_kb < 512

    def test_the_reason_is_recorded_at_the_constant(self):
        import inspect
        source = inspect.getsource(dsp)
        assert 'expensive to rebuild' in source
        assert 'PJMMap.webp' in source
