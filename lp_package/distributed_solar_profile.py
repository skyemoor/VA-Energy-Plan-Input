"""
distributed_solar_profile.py

Hourly capacity-factor profiles for the STATUTORY distributed carve-out — the sub-1 MW behind-the-
meter resources Va. Code § 56-585.5(C)(2) requires, raised from 1% to 4.5% (2026–2030) and 5%
(2031–2045) by the Distributed Generation Expansion Act, HB 628 / SB 175 (2026).

WHY AN AVERAGE RATHER THAN SITED CAPACITY

There are too many distributed sites to model individually, and their locations are not knowable in
advance. So the profile is an average across five NSRDB locations spanning the Commonwealth's
populated corridor — Sterling, Arlington, King George, Richmond and Chesapeake — which is the
representation that matches what is actually being modelled: a fleet dispersed across the state
rather than a plant somewhere in particular.

AVERAGING OUTPUT, NOT IRRADIANCE. Each site's hourly AC output is computed separately and the
outputs averaged. Averaging irradiance first and running one array would understate the smoothing
that geographic spread produces — a cloud over Richmond does not darken Sterling.

THE ARRAY: 45 DEGREES, DUE SOUTH, FIXED

Stated as an assumption, and the reasoning is not the one usually given for a steep tilt. Measured
at Sterling 2016 against a 15-degree array:

    Dec  +31.5%     Jun  -17.5%
    Jan  +29.9%     Jul  -15.8%
    Nov  +28.6%     May  -15.2%
    YEAR  +1.3%

**It is not a yield sacrifice.** At Sterling's latitude 45 degrees sits only about 6 degrees past
optimal, and the winter gain more than covers the summer loss. What changes is the SHAPE: the
December-to-June ratio moves from 0.45 to 0.71, a far more even year.

The gain lands in the three months where Virginia's peaks fall, where grid outages concentrate, and
where wholesale price differentials are widest. The loss lands in June and July, which have the most
surplus and the lowest marginal value.

NO DOUBLE-COUNTING BETWEEN THE TWO STATUTORY TRANCHES — AN ASSUMPTION, NOT A STATUTORY READING

Two provisions require small generation, and they overlap:

    § 56-585.5(C)(2)   4.5%/5% of RPS from resources of 1 MW OR LESS -- an ENERGY obligation met
                       with RECs, at least 25% low-income qualifying, remainder on or adjacent to
                       public schools.
    § 56-585.5(D)(2)   1,100 MW of the 16,100 MW at NO MORE THAN 3 MW per project, 65% third-party
                       owned -- a CAPACITY procurement obligation.

A 0.9 MW project satisfies both size limits. **The statute does not say whether one project may
count toward both**, and this model assumes it MAY NOT: the two obligations are treated as
additive, and the profile here serves C.2 only.

WHY THAT DIRECTION. Assuming no double-counting builds more, not less, so it is conservative in the
direction that matters for a whitepaper arguing the clean case is affordable -- it cannot be accused
of understating what compliance requires. If the Commission permits a project to satisfy both, the
combined obligation falls by up to 1,100 MW and every scenario's cost is slightly overstated.

D.2's 1,100 MW TRANCHE IS NOT MODELLED HERE. It sits inside the 16,100 MW the scenarios already
build, on the utility solar profile -- 22.52% capacity factor, consistent with single-axis tracking,
which is the right assumption for commercially developed ground mount at 1-3 MW. Applying this
module's fixed rooftop profile to it would understate its output by nearly half.

BOTH PROFILES COME FROM SAM PVWATTS WITH DEFAULT LOSSES -- the utility one run by the project author
on NSRDB inputs, this one through nsrdb_data.fixed_tilt_hourly_kw. Same tool, same loss assumptions;
the 22.52% against 15.26% gap is single-axis tracking against a fixed array, not a tooling
difference.

NET METERING IS A COMPENSATION MECHANISM, NOT A REQUIREMENT, and appears nowhere in § 56-585.5. It
determines what a distributed owner is PAID for exported energy, not how much distributed capacity
must exist. So it does not change the MW this module sizes, and it is absent here by design: it
belongs to Scenario 3's DER owner economics, where who builds and on what terms is the question.

For the record, since it moves during the modelled period: the SCC's NEM 2.0 proceeding cuts the
export credit for new Dominion customers from about $0.14/kWh to about $0.09553, or roughly $0.063
if SRECs transfer to the utility. Customers interconnected before the order are grandfathered. That
changes DER owner returns substantially and the system's energy balance not at all.

NO PAIRED STORAGE. The DER expansion text sets no storage requirement or goal for distributed
resources; the storage obligation rests with the utility under the separate mandate of
§ 56-585.5(E). Distributed storage appears in Scenario 3, which expands beyond the statutory
minimum, not here.

HYDRO YEARS, NOT CALENDAR YEARS. Every other weather input in this project is spliced April-March,
so nine calendar years of NSRDB data give eight hydro years. A distributed profile on calendar
boundaries would describe different hours from the solar and wind profiles it sits beside, and the
correlation between them is exactly what decides whether distributed capacity helps at peak.
"""
from typing import Dict, Optional, Sequence

import os

import numpy as np

#: The five NSRDB locations averaged. They span the populated corridor from the northern suburbs to
#: Hampton Roads: Sterling 39.03N, Arlington 38.85N, King George 38.33N, Richmond 37.51N,
#: Chesapeake 36.61N. Albemarle is registered in nsrdb_data but excluded -- it is a utility-solar
#: siting location, not a population centre.
DISTRIBUTED_SITES = ('Sterling', 'Arlington', 'KingGeorge', 'Richmond', 'Chesapeake')

#: Measured capacity factor of the design year (2016-17), five sites averaged at 45 degrees.
#: THE HIGHEST OF THE EIGHT hydro years, which range 0.1420 to 0.1526 -- so a robustness run
#: sees about 7% less distributed output than a design-year solve assumes.
DESIGN_YEAR_CAPACITY_FACTOR = 0.1526

#: Fixed array, due south. See the module docstring for why 45 rather than latitude-optimal.
DISTRIBUTED_TILT_DEGREES = 45.0
DISTRIBUTED_AZIMUTH_DEGREES = 180.0

#: Hydro years available, each spliced April(n)-March(n+1) from two calendar years.
HYDRO_YEARS = ((2012, 2013), (2013, 2014), (2014, 2015), (2015, 2016),
               (2016, 2017), (2017, 2018), (2018, 2019), (2019, 2020))

#: Hours from 1 January to 31 March inclusive -- the splice point. A hydro year is
#: `year_n[JAN_MAR_HOURS:] + year_n1[:JAN_MAR_HOURS]`, matching scripts/build_hydro_*.py exactly.
JAN_MAR_HOURS = 24 * (31 + 28 + 31)


def _configure_data_root():
    """Points nsrdb_data at this project's source directory.

    An explicit step by that module's own design -- it carries no built-in assumption about where
    the data lives.
    """
    import os

    import nsrdb_data as nd
    import paths
    nd.configure_data_root(os.path.dirname(paths.source_file('PJMMap.webp')))
    return nd


def site_profile(site, calendar_year, nameplate_kw=1000.0):
    """One site's hourly capacity factor for one CALENDAR year."""
    nd = _configure_data_root()
    kw = nd.fixed_tilt_hourly_kw(
        site, calendar_year, nameplate_kw=nameplate_kw,
        tilt_degrees=DISTRIBUTED_TILT_DEGREES, azimuth_degrees=DISTRIBUTED_AZIMUTH_DEGREES)
    return kw / nameplate_kw


def averaged_calendar_year(calendar_year, sites=DISTRIBUTED_SITES):
    """Five-site average hourly capacity factor for one CALENDAR year.

    Averages OUTPUT, per the module docstring -- each site is run separately and the results
    averaged, so geographic smoothing is represented rather than averaged away.
    """
    profiles = [site_profile(s, calendar_year) for s in sites]
    lengths = {len(p) for p in profiles}
    if lengths != {8760}:
        raise ValueError(
            f'{calendar_year}: site profiles have lengths {sorted(lengths)}, expected 8760 each. '
            'Averaging arrays of different lengths would silently misalign hours across sites.')
    return np.mean(profiles, axis=0)


#: Committed derived product holding all eight hydro-year profiles, keyed `hy<first_year>`.
#: DATA_SOURCES.md's standing rule: large source data is not committed because it is public and
#: re-downloadable, but "derived products that are small and expensive to rebuild ARE stored".
#: These are 260 KB and take forty PVWatts runs over NSRDB files that are hundreds of megabytes.
CACHED_PROFILE_FILE = 'distributed_solar_cf_45deg_8yr.npz'


def _cached_hydro_year(first_calendar_year):
    """The committed profile for this hydro year, or None when the cache file is absent.

    WHY THIS EXISTS. Without it, every caller needing a distributed profile needs the NSRDB source
    CSVs -- and a fresh clone does not have them, so `sweep_scenario2_gas_sizing.py` failed on a
    missing PJMMap.webp, which is the marker used to locate the data root. Reproducing a 260 KB
    derived product from hundreds of megabytes of public data on every clone is the wrong trade.

    The NSRDB path stays as the fallback and remains the definition; this is a cache of it.
    """
    import paths

    path = paths.weather_year(CACHED_PROFILE_FILE)
    if not os.path.exists(path):
        return None
    with np.load(path) as data:
        key = f'hy{first_calendar_year}'
        if key not in data:
            raise KeyError(
                f'{CACHED_PROFILE_FILE} exists but has no entry for hydro year '
                f'{first_calendar_year} (keys: {sorted(data.files)}). A partial cache is worse '
                'than none -- rebuild it rather than falling through to the NSRDB path, which '
                'would silently use a different derivation for some years and not others.')
        return data[key].copy()


def hydro_year_profile(first_calendar_year, sites=DISTRIBUTED_SITES, _cache=None):
    """Five-site average for one HYDRO year, spliced April(n)-March(n+1).

    Reads the committed cache when it covers this year and the default sites are in use, and falls
    back to computing from NSRDB otherwise. A non-default `sites` list always computes, since the
    cache holds the five-site average and nothing else.

    `_cache` optionally maps calendar year -> averaged profile, so a caller building all eight
    hydro years computes each calendar year once rather than twice. Forty PVWatts runs instead of
    eighty.
    """
    if sites is DISTRIBUTED_SITES and _cache is None:
        cached = _cached_hydro_year(first_calendar_year)
        if cached is not None:
            return cached
        # RULE 5. Falling through here lands in the NSRDB path, which fails on a missing
        # PJMMap.webp -- a map image that has nothing to do with solar profiles and sends the
        # reader looking for the wrong thing. That is how this defect presented twice. Say what is
        # actually missing, and what to do about it, before the misleading error can happen.
        import paths

        if paths.source_dir_marker_or_none() is None:
            raise FileNotFoundError(
                f'{CACHED_PROFILE_FILE} is not in data/weather_years, and the NSRDB source data '
                'needed to rebuild it is not present either.\n'
                '  The cache is a committed derived product (260 KB) -- `git pull` should bring '
                'it.\n'
                '  To rebuild from source instead, see docs/DATA_SOURCES.md for the NSRDB files '
                'and place them in data/source.')
    cache = {} if _cache is None else _cache
    for y in (first_calendar_year, first_calendar_year + 1):
        if y not in cache:
            cache[y] = averaged_calendar_year(y, sites)
    return np.concatenate([cache[first_calendar_year][JAN_MAR_HOURS:],
                           cache[first_calendar_year + 1][:JAN_MAR_HOURS]])


def all_hydro_years(sites=DISTRIBUTED_SITES) -> Dict[str, np.ndarray]:
    """Every hydro year, keyed as the weather files are: '2012_13', '2013_14', and so on."""
    cache: Dict[int, np.ndarray] = {}
    out = {}
    for first, second in HYDRO_YEARS:
        out[f'{first}_{str(second)[2:]}'] = hydro_year_profile(first, sites, _cache=cache)
    return out


def capacity_for_carve_out(annual_demand_mwh, carve_out_share, profile):
    """Nameplate MW of distributed solar needed to meet `carve_out_share` of annual demand.

    THE CARVE-OUT IS AN ENERGY REQUIREMENT, not a capacity one: the statute sets a share of the RPS
    requirement to be met from sub-1 MW resources. So the MW that satisfies it depends entirely on
    the capacity factor of the assumed array -- which is why the 45-degree assumption has to be
    stated wherever this figure appears.
    """
    cf = float(np.mean(profile))
    if not 0.0 < cf < 1.0:
        raise ValueError(f'capacity factor {cf} is not a fraction; the profile is not a CF series.')
    return annual_demand_mwh * carve_out_share / (8760.0 * cf)
