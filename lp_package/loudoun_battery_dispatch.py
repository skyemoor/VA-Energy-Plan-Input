"""
loudoun_battery_dispatch.py

Simulates hour-by-hour battery state-of-charge dispatch against a LoadProfile (flattened,
worst-case demand shape) and a ScaledSolarProfile (real 9-year Sterling solar), for a given
battery power/duration/efficiency design -- charging on excess solar, discharging to cover the
deficit, tracking residual (unmet) import for every hour. This is the real dispatch simulation
loudoun_load_shape_gap_analysis.py's gap_pct computation deliberately stopped short of: gap_pct
answers "how big is the shortfall," this module answers "how much of that shortfall can a given
battery actually cover, hour by hour, given it can only discharge what it has stored."

OO STRUCTURE (Rule 1): BatteryDispatchDesign is a county/site-agnostic dataclass, same pattern as
SolarCanopyDesign/BatteryStorageDesign in loudoun_parking_canopy_and_storage.py. Takes a
LoadProfile and ScaledSolarProfile as inputs (composes with, does not duplicate, their existing
loading/scaling logic).

PHYSICAL INVARIANTS (Rule 9): DispatchResult verifies, immediately on construction: (1) SoC never
exceeds energy capacity or goes negative, (2) no simultaneous charge AND discharge in the same
hour -- not a hypothetical edge case included for completeness, but a real, previously-found bug
class in this project's own broader LP-model history (per the README's own documented "simultaneous
charge/discharge" investigation in the checkpoint_solver.py codebase this project's standards file
references) -- guarded against explicitly here too, in a from-scratch simulation that could
reintroduce the same failure mode independently.

SOURCE-CATEGORY TAGGING (Rule 8.3): DEFAULT_ROUND_TRIP_EFFICIENCY_PCT is tagged and directly reused
from VA_SLCOE_Model.xlsx's own "Assumptions & Sources" tab (row 35, sodium-ion/short-duration
storage, 90% -- the closest analog in this project's own assumptions to a Li-ion-class,
parking-canopy-colocated battery, distinct from the 80% this same model uses for its long-duration
iron-air storage), per Rule 6 (single source of truth) rather than a newly-invented figure.
"""
from dataclasses import dataclass
from typing import Optional

import pandas as pd

# Category: Third-Party Research / Modeler Assumptions (as categorized in VA_SLCOE_Model.xlsx's own
# "Assumptions & Sources" tab, row 35) -- "Model parameter (NA_RTE_CHARGE in lp_model.py) used in
# every hourly LP solve -- charge-side round-trip efficiency, consistent with typical
# lithium-ion-class battery chemistry benchmarks." Reused directly rather than re-derived, per
# Rule 6. This project's own model uses a DIFFERENT figure (80%) for its long-duration iron-air
# storage (row 39) -- callers modeling a long-duration case should override this default
# explicitly, not assume it applies uniformly across storage durations/chemistries.
DEFAULT_ROUND_TRIP_EFFICIENCY_PCT = 90.0

# Category: Modeler Assumptions -- a well-operated battery entering a known low-solar event is
# assumed pre-positioned as full as possible ahead of time (the realistic best case, not a neutral
# assumption), the same way a utility would pre-position storage ahead of a forecasted cold snap.
DEFAULT_STARTING_SOC_PCT = 100.0

# Category: Modeler Assumptions -- direct user decision this round ("The model would be run
# starting at 50% SoC and the SoC would not be reset at yearly boundaries"), for the multi-year
# incremental-buildout simulation specifically -- distinct from DEFAULT_STARTING_SOC_PCT (100%)
# above, which reflects a different, single-window "pre-positioned full ahead of a known event"
# scenario that doesn't fit a continuous run spanning years the operator can't fully anticipate.
DEFAULT_BUILDOUT_STARTING_SOC_PCT = 50.0

# Category: Third-Party Research (Loudoun County government + independent consulting estimate) --
# real, sourced Loudoun-specific aggregate power demand, decoupled entirely from the solar/battery
# fleet's own build-out schedule -- replacing an earlier, degenerate placeholder that derived load
# as a % of the SAME fleet_mw as solar/battery (which made dependable capacity mechanically,
# unavoidably 0 MW at every fleet size -- see Data_Sourcing_Log.md, "Rationale: real Loudoun load
# magnitude" entry, for the full derivation this round replaces). Source: Loudoun County's own
# June 2024 Board of Supervisors strategic report ("Data Center Capital - A Strategy for a
# Changing Paradigm"), cross-validated within the same report by an independently commissioned
# Kimley-Horn consulting estimate of 11.59 GW over the same timeframe. This is specifically a
# PROJECTED 2028 figure (not current, not 2045), calculated by extrapolating Dominion's own
# reported historical trajectory (1 GW in 2018 -> ~3.4 GW by 2023) forward -- see the log entry for
# why this anchor year/value pair, not some other point on that trajectory, was used.
LOUDOUN_LOAD_ANCHOR_YEAR = 2028
LOUDOUN_LOAD_ANCHOR_MW = 11_560.0  # 11.56 GW

# Category: Third-Party Research -- Dominion's own, already-sourced SYSTEMWIDE DOM Zone
# coincident-peak CAGR (from the 2025 VA/NC IRP Update filing overview deck, found and read
# directly this session -- see Data_Sourcing_Log.md). Reused here (Rule 6) as the growth rate
# applied to LOUDOUN_LOAD_ANCHOR_MW in both directions (back to 2026-2027, forward to 2045),
# rather than inventing a new rate -- an explicit, stated simplifying assumption (applying a
# systemwide average rate to a locality that has clearly been growing far faster than that
# average), not a precise Loudoun-specific forecast. The alternative of continuing Loudoun's own
# much steeper historical 2018-2028 rate (27.7% CAGR) was directly computed and rejected: naively
# extended to 2045 it implies 741 GW, implausible on its face.
LOUDOUN_LOAD_ANNUAL_GROWTH_RATE = 0.041


def compute_linear_buildout_schedule(start_year: int, end_year: int, end_fleet_mw: float,
                                      start_fleet_mw: float = 0.0) -> dict:
    """Linear interpolation of fleet_mw for every year in [start_year,
    end_year] inclusive, e.g. 2026 (0 MW) ramping to 2045 (2,908.4 MW).
    Returns {year: fleet_mw}. A standalone function (no instance state
    needed) rather than a method, matching the pattern already used for
    _solve_floor_pct_for_target_load_factor in
    loudoun_load_shape_gap_analysis.py."""
    if end_year <= start_year:
        raise ValueError(f"end_year ({end_year}) must be after start_year ({start_year}).")
    span = end_year - start_year
    return {
        year: start_fleet_mw + (end_fleet_mw - start_fleet_mw) * (year - start_year) / span
        for year in range(start_year, end_year + 1)
    }


def compute_anchored_compound_growth_schedule(start_year: int, end_year: int, anchor_year: int,
                                               anchor_value: float, annual_growth_rate: float) -> dict:
    """Compound (constant annual %) growth schedule for every year in
    [start_year, end_year] inclusive, anchored at a single real data point
    (anchor_year, anchor_value) rather than interpolated between two
    endpoints -- distinct in kind from compute_linear_buildout_schedule
    above (which IS a literal two-endpoint linear interpolation, hence
    its name). Years after anchor_year compound FORWARD from it; years
    before anchor_year compound BACKWARD (divide, rather than multiply,
    by (1 + annual_growth_rate) per year) -- e.g. with anchor_year=2028,
    anchor_value=11,560 MW, annual_growth_rate=0.041: 2026 and 2027 are
    computed by dividing back from the 2028 anchor at the SAME rate used
    to grow forward to 2045, per direct user decision (see
    Data_Sourcing_Log.md, "2026-2027 values" entry) to keep one single
    rate across the entire series rather than introduce a second,
    different rate just for the two years before the anchor.
    anchor_year need not be inside [start_year, end_year]. A standalone
    function (no instance state needed), matching the pattern already
    used for compute_linear_buildout_schedule and
    _solve_floor_pct_for_target_load_factor."""
    if end_year <= start_year:
        raise ValueError(f"end_year ({end_year}) must be after start_year ({start_year}).")
    return {
        year: anchor_value * (1 + annual_growth_rate) ** (year - anchor_year)
        for year in range(start_year, end_year + 1)
    }


def extract_hydro_year_window(solar_profile, start_year: int):
    """Extracts the Apr 1 (start_year) - Mar 31 (start_year+1) window from
    a multi-year SolarSiteProfile (which must already include both
    start_year and start_year+1's data). Matches this project's own
    already-established Apr 1 - Mar 31 fiscal-year convention (per
    standing instructions) -- and for the specific Apr2016-Mar2017 case,
    this replicates the broader model's own independently-derived "design
    weather year" window (per the README, cross-validated against two
    other severe years: 2013-14 Polar Vortex, 2012-13 acute insolation
    lull). Returns a new SolarSiteProfile wrapping just that window,
    reusing the existing class rather than building a new one."""
    from loudoun_solar_hourly_profile import SolarSiteProfile  # local import: avoids a hard
    # module-level dependency on loudoun_solar_hourly_profile from this file, matching the
    # pattern already used for scaled_solar/load_profile type hints elsewhere in this module

    window_start = pd.Timestamp(year=start_year, month=4, day=1)
    window_end = pd.Timestamp(year=start_year + 1, month=4, day=1)
    windowed_hourly = solar_profile.hourly[
        (solar_profile.hourly["timestamp"] >= window_start) & (solar_profile.hourly["timestamp"] < window_end)
    ].reset_index(drop=True)
    if len(windowed_hourly) == 0:
        raise ValueError(
            f"No hourly data found in the Apr {start_year} - Mar {start_year + 1} window -- "
            f"does the source solar_profile actually include both {start_year} and {start_year + 1}?"
        )
    return SolarSiteProfile(
        site_name=f"{solar_profile.site_name} (Apr{start_year}-Mar{start_year + 1} hydro year)",
        nameplate_kw=solar_profile.nameplate_kw, tilt_degrees=solar_profile.tilt_degrees,
        system_losses_pct=solar_profile.system_losses_pct, years=[start_year, start_year + 1],
        hourly=windowed_hourly,
    )


@dataclass
class BatteryDispatchDesign:
    """County/site-agnostic dispatch parameters, all overridable per-instance."""
    power_mw: float
    duration_hours: float
    round_trip_efficiency_pct: float = DEFAULT_ROUND_TRIP_EFFICIENCY_PCT
    starting_soc_pct: float = DEFAULT_STARTING_SOC_PCT

    @property
    def energy_capacity_mwh(self) -> float:
        return self.power_mw * self.duration_hours

    @staticmethod
    def _dispatch_one_hour(solar_mw: float, load_mw: float, current_soc: float,
                            energy_capacity: float, power_mw: float,
                            rte_fraction: float) -> tuple:
        """Pure per-hour dispatch step: given fully-resolved inputs (solar
        MW, load MW, current SoC, this hour's energy capacity and power
        rating, and RTE), computes the dispatch outcome for one hour. Has
        zero knowledge of where its inputs came from -- that's the
        caller's job (a fixed-scale lookup in simulate(), versus a
        year-aware rescaling in simulate_with_incremental_buildout()).
        Deliberately a @staticmethod, not using self.power_mw, specifically
        so callers whose power_mw varies (e.g. per build-out year) can
        pass a different value each call without needing a different
        design instance per year. Identical for every caller, extracted
        here per Rule 1 rather than duplicated.

        Returns (charge_mw, discharge_mw, curtailment_mw, residual_import_mw, new_soc).
        """
        net = load_mw - solar_mw  # positive = deficit (need battery/import), negative = excess solar
        charge_mw = 0.0
        discharge_mw = 0.0
        curtailment_mw = 0.0
        new_soc = current_soc

        if net < 0:
            excess = -net
            headroom_mwh = energy_capacity - current_soc
            # Only a rte_fraction share of what's drawn from excess solar actually lands in
            # storage -- charge_mw here is measured on the AC/grid side (how much excess solar
            # is being drawn down), capped so the resulting stored energy doesn't exceed
            # headroom, and separately capped by the battery's own power rating.
            max_charge_from_headroom = headroom_mwh / rte_fraction if rte_fraction > 0 else 0.0
            charge_mw = min(excess, power_mw, max_charge_from_headroom)
            new_soc = current_soc + charge_mw * rte_fraction
            # Curtailment: excess solar the battery couldn't absorb (power- or
            # headroom-limited), per the real View #1 spec ("hourly curtailment (replaces
            # export, which no longer exists in the corrected no-export model)"). Excess
            # solar is either used to charge the battery or curtailed -- never exported,
            # since this model has no export mechanism.
            curtailment_mw = excess - charge_mw
        elif net > 0:
            deficit = net
            discharge_mw = min(deficit, power_mw, current_soc)
            new_soc = current_soc - discharge_mw

        residual_import_mw = max(0.0, net - discharge_mw)
        return charge_mw, discharge_mw, curtailment_mw, residual_import_mw, new_soc

    def simulate(self, load_profile, scaled_solar, start: pd.Timestamp, end: pd.Timestamp) -> "DispatchResult":
        """Simulates hour-by-hour dispatch over [start, end] (inclusive),
        at this design's own fixed power_mw/duration/RTE, against a single
        fixed scaled_solar.fleet_mw for the whole window. load_profile is
        a loudoun_load_shape_gap_analysis.LoadProfile; scaled_solar is a
        loudoun_solar_hourly_profile.ScaledSolarProfile -- not type-hinted
        directly to avoid a hard import dependency in this module's own
        class definitions, matching the pattern already used in
        LoadSolarGapAnalysis.compute().

        SCALE ASSUMPTION (stated explicitly, per direct user confirmation
        after a real scale-mismatch bug was found and traced): load is
        derived as load_pct_of_peak * scaled_solar.fleet_mw, NOT the raw
        absolute DOMLSE Dominion-zone MW value directly. The raw DOMLSE
        peak (~29,587 MW for the full Dominion territory in 2045) and the
        solar/battery fleet MW (Loudoun-specific canopy capacity, e.g.
        ~1,551-1,939 MW) are at genuinely different, unrelated scales; a
        battery sized to the solar fleet compared directly against the
        real territory-wide load is trivially overwhelmed regardless of
        duration, which is what the original, buggy version of this
        method produced (a suspicious ~1.4% difference between a 4-hour
        and 100-hour battery that contradicted this project's own
        already-established finding that duration matters a great deal at
        the 63-75-hour streak lengths found earlier). This assumption --
        that Loudoun's own load peak equals the solar fleet's MW capacity
        -- is a deliberate, stated placeholder scale for this dispatch
        test specifically, not a rediscovery of Loudoun's real absolute
        load magnitude, which remains explicitly deferred per direct user
        framing ("we'll worry about actual MWh load that fits that
        profile later").
        """
        load_by_month_day_hour = load_profile.adjusted_hourly.copy()
        load_by_month_day_hour["month"] = load_by_month_day_hour["timestamp"].dt.month
        load_by_month_day_hour["day"] = load_by_month_day_hour["timestamp"].dt.day
        load_by_month_day_hour["hour"] = load_by_month_day_hour["timestamp"].dt.hour
        load_pct_lookup = load_by_month_day_hour.set_index(["month", "day", "hour"])["pct_of_peak"]

        window = scaled_solar.hourly[
            (scaled_solar.hourly["timestamp"] >= start) & (scaled_solar.hourly["timestamp"] <= end)
        ].sort_values("timestamp").reset_index(drop=True)
        if len(window) == 0:
            raise ValueError(f"No solar data found in the requested window [{start}, {end}]")

        rte_fraction = self.round_trip_efficiency_pct / 100
        energy_capacity = self.energy_capacity_mwh
        soc = self.starting_soc_pct / 100 * energy_capacity

        records = []
        for _, row in window.iterrows():
            ts = row["timestamp"]
            solar_mw = row["mw"]
            load_pct = load_pct_lookup.loc[(ts.month, ts.day, ts.hour)]
            # The scale assumption described above: load expressed as a share of the solar
            # fleet's own MW, not the raw Dominion-zone absolute value.
            load_mw = load_pct / 100 * scaled_solar.fleet_mw

            charge_mw, discharge_mw, curtailment_mw, residual_import_mw, soc = self._dispatch_one_hour(
                solar_mw=solar_mw, load_mw=load_mw, current_soc=soc,
                energy_capacity=energy_capacity, power_mw=self.power_mw, rte_fraction=rte_fraction,
            )

            records.append({
                "timestamp": ts, "load_mw": load_mw, "solar_mw": solar_mw,
                "charge_mw": charge_mw, "discharge_mw": discharge_mw,
                "curtailment_mw": curtailment_mw,
                "soc_mwh": soc, "soc_pct": soc / energy_capacity * 100 if energy_capacity > 0 else 0.0,
                "residual_import_mw": residual_import_mw,
            })

        return DispatchResult(design=self, hourly=pd.DataFrame(records), fleet_mw=scaled_solar.fleet_mw)

    def simulate_with_incremental_buildout(self, load_profile, weather_year_solar_profile,
                                            buildout_schedule: dict, loudoun_load_peak_mw_schedule: dict,
                                            weather_year_label: str,
                                            starting_soc_pct: float = DEFAULT_BUILDOUT_STARTING_SOC_PCT
                                            ) -> "IncrementalBuildoutDispatchResult":
        """Simulates a CONTINUOUS, multi-year dispatch run across every
        year in buildout_schedule, repeating weather_year_solar_profile's
        own hourly shape once per build-out year, each instance rescaled
        to that year's own fleet_mw via the existing
        SolarSiteProfile.scale_to_fleet_mw() (reused, not reimplemented,
        per Rule 1 -- this also means that method's own Rule 9
        overirradiance-tolerance check automatically re-runs every year
        as a free side benefit). SoC carries over continuously across
        every year boundary (never reset), starting at starting_soc_pct
        only in the very first build-out year -- per direct user decision.

        self is treated as the END-STATE (final-year) design: only its
        duration_hours and round_trip_efficiency_pct are held fixed across
        every year. self.power_mw is NOT used directly here -- power (and
        therefore energy capacity) scales by year via buildout_schedule
        instead, under this project's established 1:1 solar:storage
        pairing convention (fleet_mw this year == power_mw this year).

        LOAD MAGNITUDE (per direct user decision this round, replacing an
        earlier, degenerate placeholder): load_mw is derived as
        load_pct_of_peak * loudoun_load_peak_mw_schedule[year] -- a REAL,
        INDEPENDENT Loudoun load magnitude series (see
        LOUDOUN_LOAD_ANCHOR_YEAR/MW/ANNUAL_GROWTH_RATE and
        Data_Sourcing_Log.md's "Rationale: real Loudoun load magnitude"
        entry for full provenance), NOT the solar/battery fleet's own
        fleet_mw. The earlier version derived load as a % of the SAME
        fleet_mw as solar/battery, which made dependable capacity
        mechanically, unavoidably 0 MW at every fleet size regardless of
        weather year: since load and solar's ratio at any hour was then
        scale-invariant (fleet_mw canceled out of both sides), and
        Sterling's real peak output (~82.7% of its own nameplate) never
        reaches the load floor (90% of peak) at ANY scale, the battery
        never once got a charging opportunity across a full 175,200-hour,
        20-year test run (verified directly, not assumed). Note the
        expected, honest consequence of the fix: Loudoun's real load
        (~10.7-22.9 GW) vastly exceeds this project's solar/battery fleet
        (peaking at 2,908.4 MW, ~2.9 GW, even at full 2045 build-out) --
        solar can still never exceed load at this scale either, so the
        battery is still expected to never charge. This is not a bug
        recurring a third time; it is the honest, correct answer once
        real-world magnitudes are used on both sides -- Loudoun's actual
        data-center-driven load is simply far larger than any plausible
        rooftop+parking-canopy solar/battery deployment on its own, which
        is itself a legitimate, reportable finding for a transmission
        planner, not a modeling failure to keep chasing.

        Note on the returned hourly timestamps: since one weather year's
        shape is repeated once per build-out year, the "timestamp" column
        repeats across build-out years (distinguished by the separate
        "build_out_year" column) -- callers must not naively sort or
        deduplicate by timestamp alone.
        """
        load_by_month_day_hour = load_profile.adjusted_hourly.copy()
        load_by_month_day_hour["month"] = load_by_month_day_hour["timestamp"].dt.month
        load_by_month_day_hour["day"] = load_by_month_day_hour["timestamp"].dt.day
        load_by_month_day_hour["hour"] = load_by_month_day_hour["timestamp"].dt.hour
        load_pct_lookup = load_by_month_day_hour.set_index(["month", "day", "hour"])["pct_of_peak"]

        rte_fraction = self.round_trip_efficiency_pct / 100
        first_year = min(buildout_schedule.keys())
        first_year_capacity = buildout_schedule[first_year] * self.duration_hours
        soc = starting_soc_pct / 100 * first_year_capacity

        records = []
        for build_out_year in sorted(buildout_schedule.keys()):
            fleet_mw_this_year = buildout_schedule[build_out_year]
            power_mw_this_year = fleet_mw_this_year  # 1:1 solar:storage pairing convention
            energy_capacity_this_year = power_mw_this_year * self.duration_hours
            if build_out_year not in loudoun_load_peak_mw_schedule:
                raise ValueError(
                    f"build_out_year {build_out_year} is in buildout_schedule but missing from "
                    f"loudoun_load_peak_mw_schedule -- both schedules must cover the same years."
                )
            loudoun_load_peak_mw_this_year = loudoun_load_peak_mw_schedule[build_out_year]

            scaled_solar_this_year = weather_year_solar_profile.scale_to_fleet_mw(fleet_mw_this_year)

            for _, row in scaled_solar_this_year.hourly.iterrows():
                ts = row["timestamp"]
                solar_mw = row["mw"]
                load_pct = load_pct_lookup.loc[(ts.month, ts.day, ts.hour)]
                # The real, independent load magnitude described above -- NOT fleet_mw_this_year.
                load_mw = load_pct / 100 * loudoun_load_peak_mw_this_year

                charge_mw, discharge_mw, curtailment_mw, residual_import_mw, soc = self._dispatch_one_hour(
                    solar_mw=solar_mw, load_mw=load_mw, current_soc=soc,
                    energy_capacity=energy_capacity_this_year, power_mw=power_mw_this_year,
                    rte_fraction=rte_fraction,
                )

                records.append({
                    "timestamp": ts, "build_out_year": build_out_year, "fleet_mw": fleet_mw_this_year,
                    "loudoun_load_peak_mw": loudoun_load_peak_mw_this_year,
                    "load_mw": load_mw, "solar_mw": solar_mw,
                    "charge_mw": charge_mw, "discharge_mw": discharge_mw,
                    "curtailment_mw": curtailment_mw,
                    "soc_mwh": soc,
                    "soc_pct": soc / energy_capacity_this_year * 100 if energy_capacity_this_year > 0 else 0.0,
                    "residual_import_mw": residual_import_mw,
                })

        return IncrementalBuildoutDispatchResult(
            design=self, hourly=pd.DataFrame(records), weather_year_label=weather_year_label,
        )

    def find_worst_dependable_capacity_across_candidate_years(
        self, load_profile, candidate_weather_year_profiles: dict, buildout_schedule: dict,
        loudoun_load_peak_mw_schedule: dict,
        starting_soc_pct: float = DEFAULT_BUILDOUT_STARTING_SOC_PCT,
    ) -> "WorstCaseAcrossCandidateYearsResult":
        """Runs simulate_with_incremental_buildout() once per candidate
        weather year/window (keyed by label in
        candidate_weather_year_profiles, e.g. {'2018': solar_2018,
        'Apr2016-Mar2017': solar_hydro_year, ...}), and identifies the
        single worst (lowest final_year_dependable_capacity_mw) result
        across all of them -- per direct user decision to test all
        candidates rather than commit to one weakest year applied
        uniformly, since a weather year that is worst by one measure
        (e.g. total annual output) is not guaranteed to be worst at every
        fleet size across the build-out. Compares candidates on their
        FINAL build-out year specifically (the fully-built system's own
        worst case), not a single all-years-combined minimum -- see
        IncrementalBuildoutDispatchResult.dependable_capacity_by_year's
        own docstring for why an all-years-combined minimum is degenerate
        once the build-out starts at 0 MW. Every candidate's full
        per-year series remains available via all_results for the
        complete picture, regardless of which year drives this
        comparison."""
        all_results = {
            label: self.simulate_with_incremental_buildout(
                load_profile, profile, buildout_schedule, loudoun_load_peak_mw_schedule,
                weather_year_label=label, starting_soc_pct=starting_soc_pct,
            )
            for label, profile in candidate_weather_year_profiles.items()
        }
        worst_label = min(all_results, key=lambda label: all_results[label].final_year_dependable_capacity_mw)
        return WorstCaseAcrossCandidateYearsResult(all_results=all_results, worst_label=worst_label)


@dataclass
class WorstCaseAcrossCandidateYearsResult:
    all_results: dict  # {weather_year_label: IncrementalBuildoutDispatchResult}
    worst_label: str

    @property
    def worst_result(self) -> "IncrementalBuildoutDispatchResult":
        return self.all_results[self.worst_label]

    @property
    def final_year_dependable_capacity_mw(self) -> float:
        return self.worst_result.final_year_dependable_capacity_mw


@dataclass
class DispatchResult:
    design: BatteryDispatchDesign
    hourly: pd.DataFrame  # timestamp, load_mw, solar_mw, charge_mw, discharge_mw, soc_mwh, soc_pct, residual_import_mw
    fleet_mw: float  # the solar fleet MW used as load's scale reference -- see simulate()'s own docstring

    def __post_init__(self):
        self._verify_soc_within_capacity()
        self._verify_no_simultaneous_charge_and_discharge()
        self._verify_load_within_scale_assumption_bounds()
        self._verify_curtailment_non_negative()
        self._verify_energy_balance_closes_every_hour()

    def _verify_soc_within_capacity(self) -> None:
        """Physical invariant (Rule 9): SoC must never exceed the
        battery's own energy capacity or fall below zero. Raises rather
        than warns -- a dispatch result that violates this is not usable
        regardless of how plausible the rest of it looks."""
        capacity = self.design.energy_capacity_mwh
        tolerance = 1e-6
        max_soc = self.hourly["soc_mwh"].max()
        min_soc = self.hourly["soc_mwh"].min()
        if max_soc > capacity + tolerance:
            raise ValueError(f"SoC {max_soc:.4f} MWh exceeds energy capacity {capacity:.4f} MWh -- not usable.")
        if min_soc < -tolerance:
            raise ValueError(f"SoC {min_soc:.4f} MWh is negative -- not usable.")

    def _verify_no_simultaneous_charge_and_discharge(self) -> None:
        """Physical invariant (Rule 9): a real, previously-found bug class
        in this project's own broader LP-model history (simultaneous
        charge/discharge), guarded against explicitly here rather than
        assumed impossible because this is a from-scratch simulation, not
        the LP solver where it was originally found."""
        both = (self.hourly["charge_mw"] > 1e-9) & (self.hourly["discharge_mw"] > 1e-9)
        if both.any():
            bad_hours = self.hourly.loc[both, "timestamp"].tolist()
            raise ValueError(
                f"Simultaneous charge AND discharge found in {len(bad_hours)} hour(s), "
                f"e.g. {bad_hours[0]} -- not physically valid, not usable."
            )

    def _verify_load_within_scale_assumption_bounds(self) -> None:
        """Physical invariant (Rule 9), added directly in response to the
        scale-mismatch bug found and fixed this round: since load_mw is
        DERIVED as load_pct_of_peak (bounded [0,100] by construction of
        LoadProfile's own floor-clip transform) times fleet_mw, load_mw
        must never exceed fleet_mw by more than a small floating-point
        tolerance. A violation here would mean the scale-assumption
        derivation itself is broken -- e.g. the old bug's raw, absolute
        DOMLSE MW leaking through again -- not a legitimate result."""
        tolerance = 1e-6
        max_load = self.hourly["load_mw"].max()
        if max_load > self.fleet_mw + tolerance:
            raise ValueError(
                f"load_mw {max_load:.4f} exceeds fleet_mw {self.fleet_mw:.4f} -- the "
                f"load_pct_of_peak x fleet_mw scale assumption has been violated "
                f"(this is exactly the shape of the earlier scale-mismatch bug); not usable."
            )
        if (self.hourly["load_mw"] < -tolerance).any():
            raise ValueError("load_mw is negative for at least one hour -- not usable.")

    def _verify_curtailment_non_negative(self) -> None:
        """Physical invariant (Rule 9): curtailment_mw (added per the real
        View #1 spec, "hourly curtailment... as a negative bar alongside
        battery charging") can never be negative -- it represents excess
        solar the battery couldn't absorb, which is either zero (no
        excess, or the battery absorbed all of it) or positive, never a
        deficit."""
        tolerance = 1e-6
        if (self.hourly["curtailment_mw"] < -tolerance).any():
            raise ValueError("curtailment_mw is negative for at least one hour -- not usable.")

    def _verify_energy_balance_closes_every_hour(self) -> None:
        """Physical invariant (Rule 9), added alongside curtailment: every
        hour, solar + discharge + residual_import must exactly equal
        load + charge + curtailment -- energy generated or imported must
        equal energy served, stored (grid-side), or wasted, with nothing
        unaccounted for. This is a stronger, more general check than
        curtailment non-negativity alone: it verifies the entire dispatch
        loop's internal consistency in one shot (derived directly from
        simulate()'s own branch logic -- see that method's docstring for
        the derivation), not just this one new field."""
        tolerance = 1e-6
        sources = self.hourly["solar_mw"] + self.hourly["discharge_mw"] + self.hourly["residual_import_mw"]
        uses = self.hourly["load_mw"] + self.hourly["charge_mw"] + self.hourly["curtailment_mw"]
        imbalance = (sources - uses).abs()
        if (imbalance > tolerance).any():
            worst_idx = imbalance.idxmax()
            raise ValueError(
                f"Energy balance does not close at {self.hourly['timestamp'].iloc[worst_idx]}: "
                f"sources (solar+discharge+residual_import)={sources.iloc[worst_idx]:.6f} vs "
                f"uses (load+charge+curtailment)={uses.iloc[worst_idx]:.6f}, "
                f"imbalance={imbalance.iloc[worst_idx]:.6f} -- not usable."
            )

    @property
    def total_residual_import_mwh(self) -> float:
        return self.hourly["residual_import_mw"].sum()

    @property
    def min_soc_pct(self) -> float:
        return self.hourly["soc_pct"].min()

    @property
    def hours_at_zero_soc(self) -> int:
        return int((self.hourly["soc_pct"] <= 1e-6).sum())


@dataclass
class IncrementalBuildoutDispatchResult:
    """Result of simulate_with_incremental_buildout(). Distinct from
    DispatchResult (not a subclass/reuse of it) because its physical
    invariants are genuinely different in shape: fleet_mw (and therefore
    energy capacity) varies PER ROW here, tracked in the hourly
    dataframe's own "fleet_mw" and "build_out_year" columns, rather than
    being one fixed scalar for the whole run -- forcing every capacity-
    and load-bound check to be evaluated row-by-row against that row's own
    fleet_mw, not a single self.fleet_mw. Keeping this as its own class
    (rather than force-fitting a per-row concept into DispatchResult's
    single-fleet_mw shape) follows the same principle just established for
    the _dispatch_one_hour extraction: don't merge two genuinely different
    shapes of data into one structure just because they're similar.
    """
    design: BatteryDispatchDesign
    hourly: pd.DataFrame  # timestamp, build_out_year, fleet_mw, load_mw, solar_mw, charge_mw,
                           # discharge_mw, curtailment_mw, soc_mwh, soc_pct, residual_import_mw
    weather_year_label: str

    def __post_init__(self):
        self._verify_soc_within_capacity_per_row()
        self._verify_no_simultaneous_charge_and_discharge()
        self._verify_load_within_loudoun_load_peak_bounds_per_row()
        self._verify_curtailment_non_negative()
        self._verify_energy_balance_closes_every_hour()

    def _verify_soc_within_capacity_per_row(self) -> None:
        """Physical invariant (Rule 9), per-row version: SoC must never
        exceed THAT ROW's OWN energy capacity (fleet_mw for that row's
        build-out year x design.duration_hours) or fall below zero --
        checked row-by-row since capacity itself varies by year here,
        unlike DispatchResult's single-fleet_mw version of this check."""
        tolerance = 1e-6
        capacity_per_row = self.hourly["fleet_mw"] * self.design.duration_hours
        over_capacity = self.hourly["soc_mwh"] > capacity_per_row + tolerance
        if over_capacity.any():
            bad_idx = self.hourly[over_capacity].index[0]
            raise ValueError(
                f"SoC {self.hourly['soc_mwh'].iloc[bad_idx]:.4f} MWh exceeds that row's own "
                f"energy capacity {capacity_per_row.iloc[bad_idx]:.4f} MWh at "
                f"{self.hourly['timestamp'].iloc[bad_idx]} (build_out_year="
                f"{self.hourly['build_out_year'].iloc[bad_idx]}) -- not usable."
            )
        if (self.hourly["soc_mwh"] < -tolerance).any():
            raise ValueError("soc_mwh is negative for at least one row -- not usable.")

    def _verify_no_simultaneous_charge_and_discharge(self) -> None:
        """Same check as DispatchResult's own version (Rule 9) -- not
        fleet_mw-dependent, so identical here."""
        both = (self.hourly["charge_mw"] > 1e-9) & (self.hourly["discharge_mw"] > 1e-9)
        if both.any():
            bad_idx = self.hourly[both].index[0]
            raise ValueError(
                f"Simultaneous charge AND discharge at {self.hourly['timestamp'].iloc[bad_idx]} "
                f"(build_out_year={self.hourly['build_out_year'].iloc[bad_idx]}) -- not usable."
            )

    def _verify_load_within_loudoun_load_peak_bounds_per_row(self) -> None:
        """Physical invariant (Rule 9), updated this round: since load_mw
        is now derived as load_pct_of_peak * loudoun_load_peak_mw (a real,
        independent Loudoun load magnitude series -- see
        simulate_with_incremental_buildout's own docstring), the bound
        check is against THAT ROW's OWN loudoun_load_peak_mw, not
        fleet_mw (fleet_mw is the solar/battery side's own scale now,
        genuinely decoupled from load's scale -- checking load against it
        would be checking the wrong quantity entirely, not just a stale
        variable name). Checked row-by-row since both series vary by
        build-out year."""
        tolerance = 1e-6
        over_load_peak = self.hourly["load_mw"] > self.hourly["loudoun_load_peak_mw"] + tolerance
        if over_load_peak.any():
            bad_idx = self.hourly[over_load_peak].index[0]
            raise ValueError(
                f"load_mw {self.hourly['load_mw'].iloc[bad_idx]:.4f} exceeds that row's own "
                f"loudoun_load_peak_mw {self.hourly['loudoun_load_peak_mw'].iloc[bad_idx]:.4f} at "
                f"{self.hourly['timestamp'].iloc[bad_idx]} (build_out_year="
                f"{self.hourly['build_out_year'].iloc[bad_idx]}) -- not usable."
            )
        if (self.hourly["load_mw"] < -tolerance).any():
            raise ValueError("load_mw is negative for at least one row -- not usable.")

    def _verify_curtailment_non_negative(self) -> None:
        """Same check as DispatchResult's own version (Rule 9) -- not
        fleet_mw-dependent, so identical here."""
        tolerance = 1e-6
        if (self.hourly["curtailment_mw"] < -tolerance).any():
            raise ValueError("curtailment_mw is negative for at least one row -- not usable.")

    def _verify_energy_balance_closes_every_hour(self) -> None:
        """Same check as DispatchResult's own version (Rule 9) -- already
        row-by-row by construction, so identical here."""
        tolerance = 1e-6
        sources = self.hourly["solar_mw"] + self.hourly["discharge_mw"] + self.hourly["residual_import_mw"]
        uses = self.hourly["load_mw"] + self.hourly["charge_mw"] + self.hourly["curtailment_mw"]
        imbalance = (sources - uses).abs()
        if (imbalance > tolerance).any():
            worst_idx = imbalance.idxmax()
            raise ValueError(
                f"Energy balance does not close at {self.hourly['timestamp'].iloc[worst_idx]} "
                f"(build_out_year={self.hourly['build_out_year'].iloc[worst_idx]}): "
                f"sources={sources.iloc[worst_idx]:.6f} vs uses={uses.iloc[worst_idx]:.6f} -- not usable."
            )

    @property
    def dependable_capacity_by_year(self) -> pd.Series:
        """For EACH build-out year separately, the lowest hourly value of
        (solar_mw + discharge_mw) within THAT year's own hours only --
        indexed by build_out_year. Replaces an earlier, degenerate
        single-number version of this property that took the minimum
        across the ENTIRE multi-year run: since the buildout starts at
        0 MW by construction, that single-number version always,
        mechanically returned exactly 0.00 MW (the trivial first-hour-of-
        the-zero-fleet-starting-year), regardless of how the system
        performs in any later, meaningfully-built-out year -- a real gap
        in the metric's design, not a data problem, caught only once real
        data made the degenerate result obvious. Per-year evaluation
        avoids this: each year's own worst hour is judged only against
        that year's own build-out, so a trivial starting condition in
        year 1 can no longer dominate every other year's real result.
        An absolute MW figure per year, not a percentage."""
        contribution = self.hourly["solar_mw"] + self.hourly["discharge_mw"]
        return contribution.groupby(self.hourly["build_out_year"]).min()

    @property
    def dependable_capacity_hour_by_year(self) -> pd.DataFrame:
        """For each build-out year, the specific row (timestamp and full
        detail) at which that year's own dependable-capacity minimum
        occurs -- for direct inspection/reporting, not just the bare
        numbers. One row per build-out year, indexed by build_out_year."""
        df = self.hourly.copy()
        df["_contribution"] = df["solar_mw"] + df["discharge_mw"]
        idx_per_year = df.groupby("build_out_year")["_contribution"].idxmin()
        return df.loc[idx_per_year].drop(columns="_contribution").set_index("build_out_year")

    @property
    def final_year_dependable_capacity_mw(self) -> float:
        """Convenience accessor: the dependable capacity of the LAST
        (final, fully-built) build-out year specifically -- the fully-
        built system's own worst-case performance, which is what's
        actually relevant for 'how much can we rely on once this is
        fully built.' A deliberate, stated choice of which year to use as
        the headline figure (proposed, not yet separately confirmed
        beyond the general per-year fix) -- the full dependable_capacity_by_year
        series above remains available for the complete year-by-year
        picture regardless of this choice."""
        final_year = self.hourly["build_out_year"].max()
        return self.dependable_capacity_by_year.loc[final_year]
