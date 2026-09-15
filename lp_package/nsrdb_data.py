"""
nsrdb_data.py

OO structure (SES Rule 1: "when creating code where no existing OO structure is
present, consider other similar tasks... then conceptualize an OO structure") for
loading this project's NSRDB solar/weather insolation data set: six Virginia locations
(Albermarle, Arlington, Chesapeake, KingGeorge, Richmond, Sterling), 2012-2020.

Persisted per direct user instruction (2026-09-05) for reuse beyond the immediate
winter-tilt calculation -- this is exactly the kind of logic Rule 1's point #3 has in
mind ("if a second [task] needs the same calculation... move the logic into the class
hierarchy, not copy the script"), so it is built as a real, reusable structure from the
start rather than a one-off free-function script.

Two NSRDB product formats are present in the data set, with genuinely different column
sets and, critically, different GHI/DNI/DHI column ORDER (verified directly against
real file headers, not assumed) -- NSRDBFileFormat and its two concrete subclasses
isolate that difference behind one common interface, so a third format could be added
later (a new subclass) without touching any calling code.
"""

import glob
import os
import pandas as pd


class NSRDBFileFormat:
    """Base class for one NSRDB CSV product format. Concrete subclasses know their own
    format's specific column-name quirks; callers never need to know which format a
    given file uses -- they call standardize(), which always returns the same schema
    regardless of subclass."""

    #: Column names this format's own header row uses, for the fields this project
    #: needs. Subclasses override; reading is always BY NAME (never by position), since
    #: GHI/DNI/DHI column order differs between formats (SES Rule 5 -- a position-based
    #: read would silently swap DNI/DHI with no error).
    REQUIRED_COLUMNS = ('Year', 'Month', 'Day', 'Hour', 'Minute',
                         'GHI', 'DNI', 'DHI', 'Temperature', 'Wind Speed')

    #: Row index (0-based) of the real header row within the file -- both formats
    #: observed in this data set use the same layout (2 metadata rows, then header),
    #: but this is declared per-format rather than assumed shared, so a future format
    #: with a different layout only needs to override this one attribute.
    HEADER_ROW = 2

    def matches(self, filepath):
        """Returns True if this format recognizes filepath, based on its own filename
        convention. Subclasses override."""
        raise NotImplementedError

    def standardize(self, filepath):
        """Loads filepath and returns a DataFrame with this project's own common
        schema: ['datetime', 'ghi', 'dni', 'dhi', 'temperature', 'wind_speed']
        (W/m2, W/m2, W/m2, C, m/s). Raises if any required column is missing (SES
        Rule 5) rather than silently returning a partial/wrong result."""
        df = pd.read_csv(filepath, skiprows=self.HEADER_ROW)
        missing = [c for c in self.REQUIRED_COLUMNS if c not in df.columns]
        if missing:
            raise ValueError(
                f"{filepath}: missing expected column(s) {missing} for format "
                f"{type(self).__name__} -- found columns: {list(df.columns)}")
        out = pd.DataFrame({
            'datetime': pd.to_datetime(df[['Year', 'Month', 'Day', 'Hour', 'Minute']]),
            'ghi': df['GHI'].astype(float),
            'dni': df['DNI'].astype(float),
            'dhi': df['DHI'].astype(float),
            'temperature': df['Temperature'].astype(float),
            'wind_speed': df['Wind Speed'].astype(float),
        })
        if len(out) != 8760:
            raise ValueError(f"{filepath}: expected 8760 hourly rows, found {len(out)}")
        return out


class GoesAggregatedFormat(NSRDBFileFormat):
    """NSRDB GOES-aggregated v4-0-0 product. Wider column set than PSM3-2-2 (adds
    cloud type, clearsky, ozone, UV columns this project doesn't currently use), but
    the same required-column set is present under the same names."""

    def matches(self, filepath):
        # BOTH SPELLINGS. NREL's download names carry hyphens (nsrdb-goes-aggregated); this
        # project's own copies are camel-cased with the separators stripped
        # (nsrdbGOESaggregatedv400). Normalising before the test accepts either, rather than
        # renaming read-only project inputs -- and rather than guessing, which Rule 5 forbids and
        # the error below still enforces for anything genuinely unrecognised.
        name = os.path.basename(filepath).lower().replace('-', '')
        return 'nsrdbgoesaggregated' in name


class Psm322Format(NSRDBFileFormat):
    """NSRDB PSM v3.2.2 product. Narrower column set than GOES-aggregated -- verified
    directly (2026-09-05) that GHI/DNI/DHI appear in a DIFFERENT ORDER than in
    GoesAggregatedFormat's own files, which is exactly why standardize() reads by
    column name rather than position."""

    def matches(self, filepath):
        name = os.path.basename(filepath).lower().replace('-', '').replace('_', '')
        return 'psm322' in name


class UnrecognizedTmyFormat(NSRDBFileFormat):
    """Matches NSRDB TMY (Typical Meteorological Year) files specifically so they can
    be explicitly excluded, not silently loaded. Confirmed directly (2026-09-05) that
    the KingGeorge TMY file is a real synthetic-year product, not a historical year --
    wrong for this project's own resilience-focused, real-severe-year methodology
    (a TMY is constructed to be typical, i.e. to exclude the atypical/severe years this
    project's chronological-persistence approach specifically cares about)."""

    def matches(self, filepath):
        return 'tmy' in os.path.basename(filepath).lower()

    def standardize(self, filepath):
        raise ValueError(
            f"{filepath} is a TMY (synthetic Typical Meteorological Year) file -- "
            f"deliberately excluded from this project's real-historical-year data set. "
            f"See class docstring.")


#: Format detection order matters: TMY must be checked before the two real formats,
#: since a TMY filename could otherwise also happen to match one of them.
_KNOWN_FORMATS = (UnrecognizedTmyFormat(), GoesAggregatedFormat(), Psm322Format())


class NSRDBLocationData:
    """Owns one location's full set of yearly NSRDB files (potentially split across
    multiple product formats -- see class-level LOCATIONS registry below) and exposes
    a single, format-agnostic load_year() method. Concrete locations are not
    subclasses (there is no location-specific BEHAVIOR difference, only different
    coordinates and file sets), so this is one concrete class parameterized by name/
    coordinates/directory, not a subclass-per-location hierarchy -- follows the same
    "don't create a class hierarchy for what's actually just different data" judgment
    this project already applies elsewhere (e.g. Scenario3Policy is a dataclass of
    values, not a subclass per policy variant).
    """

    def __init__(self, name, latitude, longitude, data_dir):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.data_dir = data_dir

    def _find_format_and_file(self, year):
        # TWO LAYOUTS SUPPORTED. The original is one directory per location, files named *_<year>.csv.
        # This project's sources are FLAT in a single directory, prefixed by site --
        # Sterling_lat_39_03336_..._2016.csv. Added 2026-09-14 rather than reshuffling the data,
        # because the files are read-only project inputs and a copy would be a second source of
        # truth for the same measurements.
        candidates = glob.glob(os.path.join(self.data_dir, f'*_{year}.csv'))
        if not candidates:
            flat_dir = os.path.dirname(self.data_dir.rstrip(os.sep))
            candidates = glob.glob(os.path.join(flat_dir, f'{self.name}_*_{year}.csv'))
        real_candidates = []
        for filepath in candidates:
            fmt = next((f for f in _KNOWN_FORMATS if f.matches(filepath)), None)
            if fmt is None:
                raise ValueError(
                    f"{filepath}: matches no known NSRDB format (SES Rule 5 -- "
                    f"refusing to guess a format for an unrecognized filename).")
            if isinstance(fmt, UnrecognizedTmyFormat):
                continue  # TMY files are never real candidates for a real year
            real_candidates.append((fmt, filepath))
        if len(real_candidates) == 0:
            raise FileNotFoundError(f"No real (non-TMY) data file found for {self.name}, year {year}")
        if len(real_candidates) > 1:
            raise ValueError(
                f"{self.name}, year {year}: multiple candidate files "
                f"{[f for _, f in real_candidates]} -- ambiguous, refusing to silently pick one.")
        return real_candidates[0]

    def load_year(self, year):
        """Returns an 8760-row hourly DataFrame for this location/year, regardless of
        which underlying NSRDB format the source file uses."""
        if year not in NSRDBLocationData.VALID_YEARS:
            raise ValueError(
                f"year={year} not in this data set's confirmed-complete range "
                f"{NSRDBLocationData.VALID_YEARS}")
        fmt, filepath = self._find_format_and_file(year)
        return fmt.standardize(filepath)

    #: Confirmed complete (all six locations, after the two 2020 files uploaded
    #: 2026-09-05 filled the KingGeorge and Sterling gaps) -- 2012-2020 inclusive.
    VALID_YEARS = tuple(range(2012, 2021))


#: This project's own registry of the six locations in this data set. Coordinates are
#: each location's own internal file-header values (authoritative), NOT necessarily
#: matching every filename exactly -- e.g. KingGeorge's 2020 file's own filename
#: ("38_31_-77_33...") does not match its internal header (38.33/-77.34), which DOES
#: match the rest of that location's series; the header was trusted, not the filename.
#: Sterling's 2020 file's own internal header (39.05, -77.42) differs slightly
#: (~0.02 deg, ~1-2 km) from the rest of the Sterling series (39.03336, -77.40713) --
#: almost certainly NSRDB grid-cell snapping differing slightly between separate data
#: pulls, not a different physical location; disclosed here, not silently smoothed over.
LOCATIONS = {
    'Albermarle': NSRDBLocationData('Albermarle', 38.01, -78.42, None),
    'Arlington': NSRDBLocationData('Arlington', 38.849, -77.04403, None),
    'Chesapeake': NSRDBLocationData('Chesapeake', 36.61, -76.22, None),
    'KingGeorge': NSRDBLocationData('KingGeorge', 38.33, -77.34, None),
    'Richmond': NSRDBLocationData('Richmond', 37.5086, -77.33347, None),
    'Sterling': NSRDBLocationData('Sterling', 39.03336, -77.40713, None),
}


def configure_data_root(data_root):
    """Sets each registered location's data_dir to <data_root>/<location name>. Kept
    as an explicit configuration step (not hardcoded into LOCATIONS above) so this
    module has no built-in assumption about where the data lives on disk -- the
    calling context (this session's own working directory today, this project's own
    persisted-outputs path once copied there) supplies it explicitly."""
    for name, loc in LOCATIONS.items():
        loc.data_dir = os.path.join(data_root, name)


if __name__ == '__main__':
    configure_data_root('/home/claude/insolation_data')
    print(f"{'Location':<12}{'Year':<6}{'Rows':<7}{'Mean GHI':<10}{'Max GHI':<9}")
    for name, loc in LOCATIONS.items():
        for yr in (2012, 2020):
            df = loc.load_year(yr)
            print(f"{name:<12}{yr:<6}{len(df):<7}{df['ghi'].mean():<10.1f}{df['ghi'].max():<9.1f}")


def fixed_tilt_hourly_kw(location_name, year, nameplate_kw, tilt_degrees, azimuth_degrees=180.0,
                         system_losses_pct=14.0):
    """Hourly AC output, kW, for a FIXED-TILT array at one NSRDB location and calendar year.

    THE SHARED PVWATTS CALL. Extracted here 2026-09-14 from loudoun_solar_hourly_profile, so that
    module and distributed_solar_profile both depend on the DATA LAYER rather than on each other --
    statewide work should not import a county module to reach PySAM.

    `array_type = 0` is fixed open rack. Tracking is deliberately not offered: every caller models
    fixed arrays, and a tracking option here would invite someone to compare a tracking capacity
    factor against a fixed one. Virginia utility solar runs 22-25% on single-axis tracking and a
    fixed array does not, which is a comparison that has already been made in error once.

    Returns an array of exactly 8,760 hourly values and RAISES otherwise, rather than padding or
    truncating: a length mismatch means the timestamps have shifted, and silently realigning them
    would corrupt every hour-of-day and seasonal result downstream.
    """
    import numpy as np
    import PySAM.Pvwattsv8 as pvwatts

    if location_name not in LOCATIONS:
        raise ValueError(f'unknown NSRDB location {location_name!r}; known: {sorted(LOCATIONS)}')
    loc = LOCATIONS[location_name]
    weather = loc.load_year(year)

    model = pvwatts.new()
    model.SolarResource.solar_resource_data = {
        'lat': loc.latitude, 'lon': loc.longitude, 'tz': -5, 'elev': 100,
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
    model.SystemDesign.azimuth = azimuth_degrees
    model.execute()

    gen_kw = np.array(model.Outputs.ac) / 1000.0
    if len(gen_kw) != 8760:
        raise ValueError(
            f'{location_name} {year}: PySAM returned {len(gen_kw)} hours, expected 8760 -- '
            'refusing to silently misalign timestamps.')
    return gen_kw
