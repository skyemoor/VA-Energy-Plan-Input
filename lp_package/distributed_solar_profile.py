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

import numpy as np

#: The five NSRDB locations averaged. They span the populated corridor from the northern suburbs to
#: Hampton Roads: Sterling 39.03N, Arlington 38.85N, King George 38.33N, Richmond 37.51N,
#: Chesapeake 36.61N. Albemarle is registered in nsrdb_data but excluded -- it is a utility-solar
#: siting location, not a population centre.
DISTRIBUTED_SITES = ('Sterling', 'Arlington', 'KingGeorge', 'Richmond', 'Chesapeake')

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


def hydro_year_profile(first_calendar_year, sites=DISTRIBUTED_SITES, _cache=None):
    """Five-site average for one HYDRO year, spliced April(n)-March(n+1).

    `_cache` optionally maps calendar year -> averaged profile, so a caller building all eight
    hydro years computes each calendar year once rather than twice. Forty PVWatts runs instead of
    eighty.
    """
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
