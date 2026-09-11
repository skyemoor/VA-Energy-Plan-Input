#!/usr/bin/env python3
"""
inspect_richmond_surfaces.py

Summarises a Richmond City paved-surfaces extract locally, so only the small printed summary needs
transferring.

Richmond's surfaces layer carries multiple subtypes and, like its Structures layer, no obvious
location or type label. This is the same shape of problem Loudoun's Road Casings extract posed --
roads, driveways and parking lots under one RD_TYPE code, requiring a filter to type 2 -- so the
approach follows that precedent rather than inventing one.

WHAT THIS ANSWERS

  1. CONTAINMENT, via FIPS. Richmond City is 760, Henrico 087, Chesterfield 041. The Structures
     extract overdrew by only 2.2%, so expect similar here.

  2. WHICH SUBTYPE IS PARKING, via SHAPE not size. Roads are long and thin; parking lots are
     compact. Shape__Length^2 / Shape__Area is a dimensionless compactness ratio -- about 16 for a
     perfect square, ~20 for a typical rectangle, and rising steeply for linear features (a road
     100x wider than it is long scores over 400). This discriminates road from lot without knowing
     the legend, and without a size threshold, which would confuse a large road segment with a
     large lot.

     This matters because the Structures layer's subtype was assumed C&I by analogy with Prince
     William's StructureType=3 and turned out to be accessory buildings (median 200 sqft). Shape
     is evidence; a subtype number matching another county's schema is not.

  3. UNITS, by the same empirical check used for Fairfax and Richmond Structures: report the
     largest polygon as acres-under-sqft and acres-under-sqm, and take the plausible one.

  4. THE QUALIFYING TOTAL, at the >=6,000 sqft threshold used for every other county's parking --
     Loudoun's own data-dictionary definition of a Type 2 feature ("over 200 ft long, for 20
     spaces or more", ~300 sqft/space including aisles).

BEFORE RELYING ON THE SHAPE HEURISTIC: Richmond's ArcGIS REST endpoint may publish the subtype
field's coded-value domain, which would give the real labels rather than an inference. If the
layer URL is known, appending ?f=pjson returns field definitions including domains. Prefer that.

Usage:
    python3 inspect_richmond_surfaces.py <path-to-richmond-surfaces.csv>
"""
import sys

import pandas as pd

RICHMOND_CITY_FIPS = 760
NEIGHBOUR_FIPS = {41: 'Chesterfield', 87: 'Henrico', 760: 'Richmond City'}
SQFT_PER_ACRE = 43_560
MIN_QUALIFYING_LOT_SQFT = 6_000     # same threshold as Loudoun, Fairfax and Arlington

# Compactness = perimeter^2 / area. Dimensionless, so it is unit-agnostic.
#   circle 12.6 | square 16 | 2:1 rectangle 18 | 4:1 rectangle 25 | 20:1 road segment 88
# A lot digitised with islands and irregular edges runs higher than a clean rectangle, so this is
# a soft indicator across a population, not a per-polygon classifier.
COMPACT_THRESHOLD = 40


def main(path):
    df = pd.read_csv(path, low_memory=False)
    print(f"rows: {len(df):,}")
    print(f"columns: {list(df.columns)}\n")

    area_col = next((c for c in ('Shape__Area', 'Shape_Area', 'SHAPE_Area') if c in df.columns), None)
    len_col = next((c for c in ('Shape__Length', 'Shape_Length', 'SHAPE_Length') if c in df.columns), None)
    if area_col is None:
        print("no recognised area column; stopping")
        return

    # --- 1. Containment ---------------------------------------------------------------
    if 'FIPS' in df.columns:
        print("=== 1. JURISDICTION (FIPS) ===")
        for fips, n in df['FIPS'].value_counts().items():
            label = NEIGHBOUR_FIPS.get(int(fips), f'other ({int(fips)})')
            print(f"    {int(fips):>4}  {label:<16} {n:>8,} rows  ({n/len(df)*100:5.1f}%)")
        df = df[df['FIPS'] == RICHMOND_CITY_FIPS]
        print(f"\n    Richmond City only: {len(df):,} rows\n")
    else:
        print("=== 1. no FIPS column -- containment unresolved; figures below include any overdraw\n")

    subtype_col = next((c for c in ('Subtype', 'SubType', 'SUBTYPE', 'Type') if c in df.columns), None)
    if subtype_col is None:
        print("no subtype column found; reporting whole-layer totals only")
        subtype_col = None

    # --- 2. Which subtype is parking, by shape ---------------------------------------
    if subtype_col and len_col:
        df = df[df[area_col] > 0].copy()
        df['compactness'] = df[len_col] ** 2 / df[area_col]
        print("=== 2. SUBTYPE SHAPE PROFILE ===")
        print("    compactness = perimeter^2 / area. square=16, 4:1 rectangle=25, road segment=88+")
        print("    PARKING should be COMPACT (low) and LARGE. ROADS should be ELONGATED (high).")
        print(f"    {'subtype':>10} {'rows':>9} {'med compact':>12} {'med area':>11} "
              f"{'med len':>10} {'total area':>16}")
        for st, grp in df.groupby(subtype_col):
            print(f"    {str(st):>10} {len(grp):>9,} {grp['compactness'].median():>12.1f} "
                  f"{grp[area_col].median():>11,.0f} {grp[len_col].median():>10,.0f} "
                  f"{grp[area_col].sum():>16,.0f}")
        print("\n    likely parking = lowest median compactness with substantial total area")

    # --- 3. Units ---------------------------------------------------------------------
    largest = df[area_col].max()
    print(f"\n=== 3. UNITS CHECK ===")
    print(f"    largest polygon: {largest:,.0f}")
    print(f"      as sqft -> {largest/SQFT_PER_ACRE:8.2f} acres")
    print(f"      as sqm  -> {largest*10.7639/SQFT_PER_ACRE:8.2f} acres")
    print("    Loudoun's own largest real parking polygon was 92.8 acres, so a large figure is")
    print("    not automatically an error here -- but 200+ acres for one polygon is implausible.")

    # --- 4. Qualifying totals per subtype ---------------------------------------------
    print(f"\n=== 4. QUALIFYING TOTALS (>= {MIN_QUALIFYING_LOT_SQFT:,} sqft, the threshold used")
    print("    for Loudoun, Fairfax and Arlington) ===")
    groups = df.groupby(subtype_col) if subtype_col else [('all', df)]
    for st, grp in groups:
        q = grp[grp[area_col] >= MIN_QUALIFYING_LOT_SQFT]
        if len(q) == 0:
            continue
        print(f"    subtype {str(st):>6}: {len(q):>7,} polygons, {q[area_col].sum():>15,.0f} sqft "
              f"({q[area_col].sum()/SQFT_PER_ACRE:>9,.1f} acres)")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1])
