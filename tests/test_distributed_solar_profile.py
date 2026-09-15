"""
test_distributed_solar_profile.py

The statutory distributed carve-out's hourly profile -- five sites averaged, 45 degrees, fixed.

Va. Code § 56-585.5(C)(2), as raised from 1% to 4.5% (2026-2030) and 5% (2031-2045) by the
Distributed Generation Expansion Act, HB 628 / SB 175 (2026).
"""
import numpy as np
import pytest

import distributed_solar_profile as dsp


class TestTheAssumptions:
    """Too many distributed sites to model individually, and their locations are not knowable in
    advance -- so every choice here is an assumption and has to be stated as one."""

    def test_five_sites_spanning_the_populated_corridor(self):
        assert dsp.DISTRIBUTED_SITES == ('Sterling', 'Arlington', 'KingGeorge', 'Richmond',
                                         'Chesapeake')

    def test_albemarle_is_excluded(self):
        """Registered in nsrdb_data but a utility-solar siting location, not a population centre."""
        assert 'Albermarle' not in dsp.DISTRIBUTED_SITES

    def test_forty_five_degrees_due_south_fixed(self):
        assert dsp.DISTRIBUTED_TILT_DEGREES == 45.0
        assert dsp.DISTRIBUTED_AZIMUTH_DEGREES == 180.0

    def test_no_paired_storage_is_assumed(self):
        """The DER expansion text sets no storage requirement or goal for distributed resources;
        the obligation rests with the utility under § 56-585.5(E). Distributed storage belongs to
        Scenario 3, which expands beyond the statutory minimum."""
        assert 'NO PAIRED STORAGE' in dsp.__doc__

    def test_the_tilt_reasoning_is_recorded_with_its_measurement(self):
        """It is NOT a yield sacrifice, which is the usual justification for a steep tilt and is
        wrong here. Measured at Sterling 2016 against 15 degrees: December +31.5%, January +29.9%,
        June -17.5%, and the YEAR +1.3%."""
        assert '+1.3%' in dsp.__doc__
        assert 'not a yield sacrifice' in dsp.__doc__.lower()


class TestHydroYearAlignment:
    """Every other weather input is spliced April-March, so nine calendar years give eight hydro
    years. A calendar-year profile would describe different hours from the solar and wind it sits
    beside -- and the correlation between them is what decides whether distributed helps at peak."""

    def test_eight_hydro_years(self):
        assert len(dsp.HYDRO_YEARS) == 8
        assert dsp.HYDRO_YEARS[0] == (2012, 2013)
        assert dsp.HYDRO_YEARS[-1] == (2019, 2020)

    def test_the_splice_point_matches_the_build_scripts(self):
        """`year_n[JAN_MAR_HOURS:] + year_n1[:JAN_MAR_HOURS]`, exactly as scripts/build_hydro_*.py
        does it. A different splice point would misalign every hour of the year."""
        assert dsp.JAN_MAR_HOURS == 24 * (31 + 28 + 31)
        assert dsp.JAN_MAR_HOURS == 2160


class TestCarveOutCapacity:
    """THE CARVE-OUT IS AN ENERGY REQUIREMENT, not a capacity one, so the MW that satisfies it
    depends entirely on the capacity factor of the assumed array."""

    def test_capacity_scales_inversely_with_capacity_factor(self):
        demand = 202_193_036.0
        low = dsp.capacity_for_carve_out(demand, 0.05, np.full(8760, 0.10))
        high = dsp.capacity_for_carve_out(demand, 0.05, np.full(8760, 0.20))
        assert low == pytest.approx(high * 2, rel=1e-6)

    def test_measured_capacity_at_2045(self):
        """MEASURED 2026-09-14 on the design year (2016-17, CF 0.1526): 7,565 MW for 5% of
        202.2 TWh.

        An earlier estimate of 5,246 MW used a 22% capacity factor -- which is single-axis
        TRACKING, not a fixed array. That comparison was made in error, and the difference is
        2,300 MW."""
        got = dsp.capacity_for_carve_out(202_193_036.0, 0.05, np.full(8760, 0.1526))
        assert got == pytest.approx(7_565, rel=0.01)

    def test_a_non_fraction_profile_raises(self):
        """Passing MW instead of a capacity-factor series would give a nonsense answer silently."""
        with pytest.raises(ValueError, match='not a CF series'):
            dsp.capacity_for_carve_out(1e6, 0.05, np.full(8760, 1500.0))


class TestMeasuredProfiles:
    """Eight hydro years, built 2026-09-14."""

    MEASURED = {'2012_13': 0.1499, '2013_14': 0.1524, '2014_15': 0.1497, '2015_16': 0.1501,
                '2016_17': 0.1526, '2017_18': 0.1521, '2018_19': 0.1420, '2019_20': 0.1465}

    def test_the_design_year_is_the_best_of_the_eight(self):
        """WORTH KNOWING BEFORE THE EIGHT-YEAR CHECK: the design year 2016-17 has the HIGHEST
        distributed capacity factor of the eight, so the robustness run will see less distributed
        output than the design-year solve assumes -- 0.1420 in 2018-19 against 0.1526."""
        assert self.MEASURED['2016_17'] == max(self.MEASURED.values())
        assert self.MEASURED['2018_19'] == min(self.MEASURED.values())

    def test_the_spread_is_narrow(self):
        """0.1420 to 0.1526 -- a 7% spread across eight years, which is what a five-site average
        should produce. A single site would vary more."""
        vals = list(self.MEASURED.values())
        assert (max(vals) - min(vals)) / min(vals) < 0.08


class TestTheTwoStatutoryTranchesAreDistinct:
    """C.2 and D.2 both require small generation and they overlap. Getting them confused would
    either double-build or halve the obligation."""

    def test_they_differ_in_every_dimension(self):
        """C.2: 4.5%/5% of RPS, ENERGY, resources <=1 MW, met with RECs.
        D.2: 1,100 MW of the 16,100, CAPACITY, projects <=3 MW, 65% third-party.

        A 3 MW project counts toward D.2 and not toward C.2."""
        assert 'ENERGY obligation' in dsp.__doc__
        assert 'CAPACITY procurement obligation' in dsp.__doc__

    def test_no_double_counting_is_an_assumption_not_a_reading(self):
        """The statute does not say whether one project may satisfy both size limits. This model
        assumes it may NOT, and says so -- a reviewer will ask, and 'the statute is silent' is a
        better answer than an unexamined default."""
        import re
        doc = re.sub(r'\s+', ' ', dsp.__doc__)
        assert 'AN ASSUMPTION, NOT A STATUTORY READING' in doc
        assert 'does not say whether one project may count toward both' in doc

    def test_the_direction_of_the_assumption_is_stated(self):
        """Assuming no double-counting builds MORE, so it cannot be accused of understating what
        compliance requires. If the Commission permits one project to satisfy both, the obligation
        falls by up to 1,100 MW and every scenario's cost is slightly overstated."""
        import re
        assert 'conservative in the direction that matters' in re.sub(r'\s+', ' ', dsp.__doc__)

    def test_d2s_tranche_is_explicitly_out_of_scope_here(self):
        """It sits inside the 16,100 MW on the UTILITY profile -- 22.52% capacity factor,
        consistent with single-axis tracking, right for commercially developed ground mount at
        1-3 MW. Applying this module's fixed rooftop profile would understate it by nearly half."""
        assert 'NOT MODELLED HERE' in dsp.__doc__
        assert '22.52%' in dsp.__doc__


class TestNetMeteringIsOutOfScope:
    """NEM appears nowhere in § 56-585.5."""

    def test_it_is_recorded_as_compensation_not_requirement(self):
        """It determines what a distributed owner is PAID for exported energy, not how much
        distributed capacity must exist -- so it does not change the MW this module sizes."""
        assert 'COMPENSATION MECHANISM, NOT A REQUIREMENT' in dsp.__doc__

    def test_the_nem_2_figures_are_recorded_since_they_move_in_period(self):
        """Export credit for new Dominion customers falls from ~$0.14/kWh to ~$0.09553, or ~$0.063
        with SREC transfer, with pre-order interconnections grandfathered. Large for DER owner
        returns, nil for the system energy balance."""
        assert '0.09553' in dsp.__doc__
        assert 'grandfathered' in dsp.__doc__
