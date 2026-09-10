"""
loudoun_solar_hourly_profile.py

Builds an hourly, multi-year solar generation profile from real NREL SAM output for a
Sterling, VA site, and analyzes it for low-power-hour severity and duration -- the quantity
relevant to sizing transmission-capacity reduction and firming storage, per direct user framing:
"we'd be looking for low power times, as low firmed generation impacts how much we can reduce
extra transmission line capacity." A monthly/weekly energy-total view answers a different,
energy-balance question; this module answers the reliability/peak-import question instead, which
only shows up at hourly resolution.

OO STRUCTURE (Software Engineering Standards Rule 1): mirrors the pattern established in
loudoun_parking_canopy_and_storage.py for the same reason -- this analysis will very likely be
repeated for other sites/counties, the same "we will want to do this elsewhere" rationale that
motivated that module's own class hierarchy. SolarSiteProfile is the one class tied to a specific
data source/format (a directory of yearly NREL SAM CSV exports, via
from_sam_export_yearly_files()); a different export format for a future site needs only its own
classmethod, not changes to ScaledSolarProfile's analysis methods.

PHYSICAL INVARIANTS (Rule 9): ScaledSolarProfile verifies, immediately after scaling and before
any analysis method can be called against it, that scaled output never exceeds fleet nameplate
capacity by more than a small, explicitly-stated overirradiance tolerance -- raising, not warning,
on violation, since a profile that fails this check is not usable regardless of how plausible the
rest of its output looks.

SOURCE-CATEGORY TAGGING (Rule 8.3): every constant below is explicitly tagged with its category
from this project's own established 12-category taxonomy (software_engineering_standards.md Rule
8.3), not left implicit in prose.
"""
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

import pandas as pd

from loudoun_streak_finder import find_longest_threshold_streaks

# Category: Mathematical/Definitional Fact -- a physical unit-conversion/definitional constant,
# not a modeling choice.
HOURS_PER_INTERVAL_HALF_HOUR = 0.5

# Category: Modeler Assumptions -- direct, explicit user-provided input this round ("I am
# uploading Sterling solar data from a 100kW array, 15 degree incline 14% losses"), not derived,
# looked up, or assumed by the model. Recorded as documentation of provenance; the data's own kW
# values already reflect these parameters, so they are not re-applied in any calculation here --
# see Data_Sourcing_Log.md, "Hourly solar profile built from real 9-year Sterling SAM data" entry.
STERLING_NAMEPLATE_KW = 100
STERLING_TILT_DEGREES = 15
STERLING_SYSTEM_LOSSES_PCT = 14

# Category: Common Derived Data -- which years this team has actually obtained for this site.
AVAILABLE_YEARS = [2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020]

# Category: Modeler Assumptions -- a tolerance for real-world PV overirradiance (cloud-edge
# reflection can briefly push output slightly above STC-rated nameplate), used only by the Rule-9
# invariant check below, not by any energy calculation. 2% is a conservative allowance, not a
# precisely-derived figure; documented here as a stated assumption rather than an unexplained
# magic number.
OVERIRRADIANCE_TOLERANCE_PCT = 2.0

_TIMESTAMP_PATTERN = re.compile(r"^[A-Za-z]{3} \d{1,2}, \d{1,2}:\d{2} [ap]m$")
_EXPECTED_KW_COLUMN = "System power generated | (kW)"
_EXPECTED_ROWS_PER_YEAR = 17_520  # 30-minute intervals x 8,760 hours


def _load_one_sam_export_year(path: str, year: int) -> pd.DataFrame:
    """Loads one year's NREL SAM export CSV. The file's own 'Time stamp'
    column has no year embedded (e.g. 'Jan 1, 12:00 am') -- the year is
    supplied by the caller and prepended before parsing, rather than
    assumed or inferred, since two different files could otherwise be
    silently mixed up. Private module helper -- see
    SolarSiteProfile.from_sam_export_yearly_files for the public entry
    point, per Rule 1 (this parsing detail belongs behind the class's own
    interface, not exposed as free-standing, independently-callable logic)."""
    df = pd.read_csv(path)
    if list(df.columns) != ["Time stamp", _EXPECTED_KW_COLUMN]:
        raise ValueError(f"Unexpected column structure in {path}: {df.columns.tolist()}")
    if len(df) != _EXPECTED_ROWS_PER_YEAR:
        raise ValueError(f"Expected {_EXPECTED_ROWS_PER_YEAR} rows (30-min intervals) in {path}, got {len(df)}")

    bad_rows = df["Time stamp"][~df["Time stamp"].str.match(_TIMESTAMP_PATTERN)]
    if len(bad_rows) > 0:
        raise ValueError(f"Unexpected timestamp format in {path}: {bad_rows.iloc[0]!r}")

    timestamps = pd.to_datetime(str(year) + " " + df["Time stamp"], format="%Y %b %d, %I:%M %p")
    return pd.DataFrame({"timestamp": timestamps, "kw": df[_EXPECTED_KW_COLUMN].astype(float)})


def _aggregate_to_hourly(df: pd.DataFrame) -> pd.DataFrame:
    """Collapses 30-minute readings to hourly by averaging the two
    half-hour kW values within each hour -- mathematically identical to
    summing their energy (kW x 0.5 hr each) and dividing back out.

    Drops any hour with no underlying data, rather than filling it with
    zero or an interpolated value. A real, confirmed case of this: the
    Sterling SAM export uses a standardized 365-day year (typical of
    TMY-style solar datasets), so Feb 29 has no source rows at all for any
    year. When the real calendar year is applied for an actual leap year
    (2012, 2016, 2020 in this dataset), pandas' hourly resample correctly
    produces NaN for those 24 hours -- genuinely no data to average, not a
    resample error. Treating these as zero would fabricate 24 fake
    "outage" hours per leap year, inflating any low-output-streak
    analysis; dropping them leaves a real, detectable time gap instead,
    which find_longest_low_output_streaks is built to handle correctly.
    See Data_Sourcing_Log.md, "Hourly solar profile built from real 9-year
    Sterling SAM data" entry, bug #2, for the full investigation."""
    hourly = df.set_index("timestamp")["kw"].resample("h").mean().reset_index()
    return hourly.dropna(subset=["kw"]).reset_index(drop=True)


@dataclass
class SolarSiteProfile:
    """The one class tied to a specific data source/format (Rule 1). A
    different site or export format needs only its own classmethod like
    from_sam_export_yearly_files below, producing this same
    SolarSiteProfile shape -- ScaledSolarProfile's analysis methods never
    need to change."""
    site_name: str
    nameplate_kw: float
    tilt_degrees: float
    system_losses_pct: float
    years: List[int]
    hourly: pd.DataFrame  # columns: timestamp, kw

    @classmethod
    def from_sam_export_yearly_files(
        cls, directory: str, site_name: str,
        nameplate_kw: float = STERLING_NAMEPLATE_KW,
        tilt_degrees: float = STERLING_TILT_DEGREES,
        system_losses_pct: float = STERLING_SYSTEM_LOSSES_PCT,
        years: Optional[List[int]] = None,
        filename_pattern: str = "SterlingSolar{year}.csv",
    ) -> "SolarSiteProfile":
        """Loads and concatenates one year-per-file NREL SAM export set
        into one continuous, chronologically-sorted, hourly multi-year
        series. filename_pattern is itself a parameter (Rule 8.1: a
        revisitable decision, not hardcoded), so a future site with a
        different naming convention doesn't require a code change here,
        only a different argument."""
        years = years or AVAILABLE_YEARS
        frames = []
        for year in years:
            path = str(Path(directory) / filename_pattern.format(year=year))
            frames.append(_load_one_sam_export_year(path, year))
        raw = pd.concat(frames, ignore_index=True).sort_values("timestamp").reset_index(drop=True)
        hourly = _aggregate_to_hourly(raw)
        return cls(
            site_name=site_name, nameplate_kw=nameplate_kw, tilt_degrees=tilt_degrees,
            system_losses_pct=system_losses_pct, years=years, hourly=hourly,
        )

    @classmethod
    def from_nsrdb_pysam(
        cls, site_name: str, nsrdb_locations: dict, tilt_degrees: float,
        years: Optional[List[int]] = None, nameplate_kw: float = STERLING_NAMEPLATE_KW,
        system_losses_pct: float = STERLING_SYSTEM_LOSSES_PCT,
    ) -> "SolarSiteProfile":
        """ADDED 2026-09-05, extending this class rather than a new free-standing script
        (SES Rule 1) -- same reasoning as from_sam_export_yearly_files's own docstring:
        a different data source needs only its own classmethod, not a change to
        ScaledSolarProfile's analysis methods, nor to any downstream consumer of a
        SolarSiteProfile (find_optimal_blended_split, etc.).

        Runs real NSRDB irradiance data (via nsrdb_data.py's own OO structure) through
        PySAM's PVWatts model at the given tilt, for one or more real NSRDB locations
        (nsrdb_locations: {location_name: (lat, lon)}), and AVERAGES the resulting
        hourly kW series across all given locations -- direct user framing, 2026-09-04:
        "I suggested adding Arlington to give at least one more insolation data point
        to average out passing cloud cover." Averaging (not summing) preserves this as
        a single 100kW-reference-system shape, consistent with the existing
        from_sam_export_yearly_files convention scale_to_fleet_mw() expects.

        array_type=0 (fixed open rack) and azimuth=180 (true south) match this
        project's own existing Sterling SAM-export convention exactly (verified
        directly against the original export's own stated parameters) -- only tilt
        varies between call sites of this classmethod."""
        import PySAM.Pvwattsv8 as pvwatts
        import numpy as np
        import nsrdb_data as nd

        years = years or AVAILABLE_YEARS
        per_location_hourly = []
        for location_name, (lat, lon) in nsrdb_locations.items():
            for year in years:
                weather = nd.LOCATIONS[location_name].load_year(year)
                model = pvwatts.new()
                model.SolarResource.solar_resource_data = {
                    'lat': lat, 'lon': lon, 'tz': -5, 'elev': 100,
                    'year': [year] * 8760,
                    'month': weather['datetime'].dt.month.tolist(),
                    'day': weather['datetime'].dt.day.tolist(),
                    'hour': weather['datetime'].dt.hour.tolist(),
                    'minute': [0] * 8760,
                    'dn': weather['dni'].tolist(), 'df': weather['dhi'].tolist(),
                    'gh': weather['ghi'].tolist(),
                    'wspd': weather['wind_speed'].tolist(),
                    'tdry': weather['temperature'].tolist(),
                }
                model.SystemDesign.system_capacity = nameplate_kw
                model.SystemDesign.dc_ac_ratio = 1.0 / (1 - system_losses_pct / 100.0)
                model.SystemDesign.losses = system_losses_pct
                model.SystemDesign.array_type = 0
                model.SystemDesign.tilt = tilt_degrees
                model.SystemDesign.azimuth = 180
                model.execute()
                gen_kw = np.array(model.Outputs.ac) / 1000.0
                if len(gen_kw) != 8760:
                    raise ValueError(
                        f"{location_name} {year}: PySAM returned {len(gen_kw)} hours, "
                        f"expected 8760 -- refusing to silently misalign timestamps.")
                per_location_hourly.append(pd.DataFrame({
                    'timestamp': weather['datetime'], 'kw': gen_kw,
                    'location': location_name, 'year': year,
                }))

        combined = pd.concat(per_location_hourly, ignore_index=True)
        # Average across locations at each real timestamp -- not a positional average,
        # since different locations' rows for the same (year, month, day, hour) must
        # align by actual timestamp, not row order (SES Rule 5: a positional average
        # would silently misalign if any location's row count/order ever differed).
        averaged = combined.groupby('timestamp', as_index=False)['kw'].mean()
        averaged = averaged.sort_values('timestamp').reset_index(drop=True)

        return cls(
            site_name=site_name, nameplate_kw=nameplate_kw, tilt_degrees=tilt_degrees,
            system_losses_pct=system_losses_pct, years=years,
            hourly=averaged[['timestamp', 'kw']],
        )

    @classmethod
    def combine_weighted(cls, site_name: str, profiles_and_mw: List[tuple]) -> "SolarSiteProfile":
        """ADDED 2026-09-05, extending this class (SES Rule 1) rather than a new
        free-standing combining script. Takes [(SolarSiteProfile, target_mw), ...] --
        each already representing its own segment's real shape (e.g. rooftop at its
        own tilt, canopy at its own, different tilt) -- scales each to its own real MW
        share via the existing scale_to_fleet_mw(), sums the resulting MW series
        (aligned by real timestamp, not row position, for the same reason as
        from_nsrdb_pysam above), and returns the sum wrapped back into a SolarSiteProfile
        whose own nameplate_kw equals the TRUE COMBINED total MW (in kW terms) --
        so that a downstream caller's own further scale_to_fleet_mw(x) call (e.g.
        find_optimal_blended_split's internal storage-split grid search) correctly,
        proportionally rescales the ALREADY-COMBINED shape, not a single segment's
        shape alone.

        Different segments' hourly timestamps are not assumed pre-aligned (each may
        have been built from a different tilt/location-average pass) -- alignment is
        done explicitly via merge on timestamp, raising if any segment is missing an
        hour any other segment has (SES Rule 5), rather than silently dropping
        misaligned hours via an inner join's own default behavior going unnoticed."""
        if len(profiles_and_mw) < 2:
            raise ValueError("combine_weighted needs at least 2 (profile, mw) pairs -- "
                              "a single segment should just call scale_to_fleet_mw directly.")

        scaled_frames = []
        for profile, target_mw in profiles_and_mw:
            scaled = profile.scale_to_fleet_mw(target_mw)
            scaled_frames.append(scaled.hourly.rename(columns={'mw': f'mw_{profile.site_name}'}))

        merged = scaled_frames[0]
        for frame in scaled_frames[1:]:
            before_rows = len(merged)
            merged = merged.merge(frame, on='timestamp', how='inner')
            if len(merged) != before_rows:
                raise ValueError(
                    "combine_weighted: segments do not share identical timestamps -- "
                    f"merge dropped rows ({before_rows} -> {len(merged)}). Refusing to "
                    "silently combine misaligned segments.")

        mw_columns = [c for c in merged.columns if c.startswith('mw_')]
        merged['mw'] = merged[mw_columns].sum(axis=1)
        total_mw = sum(mw for _, mw in profiles_and_mw)

        return cls(
            site_name=site_name, nameplate_kw=total_mw * 1000, tilt_degrees=float('nan'),
            # tilt_degrees is genuinely undefined for a combined multi-tilt profile --
            # NaN, not a fabricated single number, per Rule 5.
            system_losses_pct=float('nan'), years=list(set(
                y for p, _ in profiles_and_mw for y in p.years)),
            hourly=merged[['timestamp']].assign(kw=merged['mw'] * 1000),
            # CORRECTED after direct verification caught a real unit bug: the 'kw'
            # column must hold genuine kW values, not MW values reused under the 'kw'
            # name. scale_to_fleet_mw()'s own arithmetic always does a final /1000
            # (kW-reference-system -> MW-at-target-fleet-size conversion) -- storing
            # already-MW values there caused a second, silent /1000 when this combined
            # profile was later re-scaled inside find_optimal_blended_split, producing
            # a result 1000x too small. Verified directly (not assumed) after the fix:
            # re-scaling to the same total_mw this profile already represents now
            # correctly reproduces the same hourly values (scale_factor=1.0 round-trip).
        )

    def scale_to_fleet_mw(self, fleet_mw: float) -> "ScaledSolarProfile":
        """Scales this site's profile SHAPE (not absolute value) up to a
        given fleet MW capacity. Only the shape (relative variation over
        time) is assumed to transfer; fleet-level losses, inverter
        clipping, and inter-site diversity at true fleet scale are not
        modeled here."""
        scale_factor = (fleet_mw * 1_000) / self.nameplate_kw
        scaled_hourly = self.hourly.copy()
        scaled_hourly["mw"] = scaled_hourly["kw"] * scale_factor / 1_000
        return ScaledSolarProfile(
            source_site_name=self.site_name, fleet_mw=fleet_mw,
            nameplate_kw=self.nameplate_kw, hourly=scaled_hourly[["timestamp", "mw"]],
        )


@dataclass
class DurationCurvePoint:
    pct_of_hours_at_or_below: float
    mw_threshold: float


@dataclass
class LowOutputStreak:
    start: pd.Timestamp
    end: pd.Timestamp
    length_hours: int
    mw_threshold_used: float


@dataclass
class ScaledSolarProfile:
    """The fleet-scaled result and its analysis methods. County-agnostic
    in the same sense as the parking module's design classes -- built from
    a SolarSiteProfile plus a target fleet_mw, with no dependency on how
    that source profile was loaded."""
    source_site_name: str
    fleet_mw: float
    nameplate_kw: float
    hourly: pd.DataFrame  # columns: timestamp, mw

    def __post_init__(self):
        self._verify_output_does_not_exceed_fleet_capacity()

    def _verify_output_does_not_exceed_fleet_capacity(self) -> None:
        """Physical invariant (Rule 9): scaled output must never exceed
        fleet nameplate capacity by more than OVERIRRADIANCE_TOLERANCE_PCT
        -- checked automatically on construction and raising immediately
        on violation, not inspected manually or assumed from a
        plausible-looking result. A profile that fails this check is not
        usable regardless of how the rest of its output looks."""
        max_allowed = self.fleet_mw * (1 + OVERIRRADIANCE_TOLERANCE_PCT / 100)
        actual_max = self.hourly["mw"].max()
        if actual_max > max_allowed:
            raise ValueError(
                f"Scaled output {actual_max:.2f} MW exceeds fleet capacity "
                f"{self.fleet_mw:.2f} MW by more than the "
                f"{OVERIRRADIANCE_TOLERANCE_PCT}% overirradiance tolerance "
                f"({max_allowed:.2f} MW) -- this profile is not usable "
                f"until the scaling or source data is investigated."
            )

    def compute_duration_curve(self, n_points: int = 101) -> List[DurationCurvePoint]:
        """Standard power-systems duration curve: for each percentile of
        hours, the MW output level at or below which that percentage of
        all hours falls. n_points=101 gives every integer percentile
        0-100."""
        sorted_mw = self.hourly["mw"].sort_values().reset_index(drop=True)
        n = len(sorted_mw)
        points = []
        for i in range(n_points):
            pct = i / (n_points - 1) * 100
            idx = min(int(round(pct / 100 * (n - 1))), n - 1)
            points.append(DurationCurvePoint(pct_of_hours_at_or_below=pct, mw_threshold=sorted_mw.iloc[idx]))
        return points

    def compute_month_hour_heatmap(self) -> pd.DataFrame:
        """Mean MW output by (month, hour-of-day), averaged across all
        available years -- separates structural low-power hours (every
        night, short winter days) from weather-driven ones, which vary
        year to year and wash out of a pure average."""
        df = self.hourly.copy()
        df["month"] = df["timestamp"].dt.month
        df["hour"] = df["timestamp"].dt.hour
        return df.pivot_table(index="month", columns="hour", values="mw", aggfunc="mean")

    def find_longest_low_output_streaks(self, mw_threshold: float, top_n: int = 10) -> List[LowOutputStreak]:
        """Finds the longest consecutive runs of hours at or below
        mw_threshold -- the metric that actually drives storage DURATION
        requirements, as distinct from simply identifying which single
        month or week has the lowest total.

        Delegates to the shared find_longest_threshold_streaks (Rule 1:
        this algorithm is also needed, unchanged, by
        loudoun_load_shape_gap_analysis.py, so it was extracted into
        loudoun_streak_finder.py rather than being duplicated). See
        Data_Sourcing_Log.md, "Hourly solar profile built from real
        9-year Sterling SAM data" entry, bug #1, for the original
        gap-detection case that shared helper's own docstring documents.
        """
        generic_streaks = find_longest_threshold_streaks(
            self.hourly, value_col="mw", threshold=mw_threshold,
            top_n=top_n, condition="at_or_below",
        )
        return [
            LowOutputStreak(start=s.start, end=s.end, length_hours=s.length_hours,
                             mw_threshold_used=s.threshold_used)
            for s in generic_streaks
        ]
