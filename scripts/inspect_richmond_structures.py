#!/usr/bin/env python3
"""
inspect_richmond_structures.py

Summarises a Richmond City Structures extract locally, so a large file does not need uploading --
only the small printed summary does.

Answers the three open questions about this dataset:

  1. CONTAINMENT. The map interface exports a rectangular extent, and Richmond is an irregular
     independent city surrounded by Henrico and Chesterfield, so a bounding box will sweep in
     neighbouring jurisdictions. The FIPS field resolves this exactly: Richmond City is 760,
     Henrico 087, Chesterfield 041. Filtering beats a boundary clip here because it uses the
     data's own authoritative attribution rather than a geometric guess.

  2. WHAT SUBTYPE MEANS. Subtype 3 was assumed C&I by analogy with Prince William's
     StructureType=3. That analogy is unverified, and a three-row sample pointed the other way:
     the Subtype 3 row was SMALLER (272.8) than both Subtype 1 rows (1,227.9 and 565.3). If 3
     were commercial it should skew larger, not smaller. This prints the size distribution per
     subtype so the legend can be inferred from the data rather than assumed from a number.

  3. UNITS. Shape__Area uses Fairfax's double-underscore convention, and Fairfax's was square
     feet -- confirmed empirically there by checking whether the largest polygon was plausible as
     sqft but implausible as square metres. The same check is applied here rather than inheriting
     the assumption.

Usage:
    python3 inspect_richmond_structures.py <path-to-richmond-structures.csv>
"""
import sys

import pandas as pd

RICHMOND_CITY_FIPS = 760
NEIGHBOUR_FIPS = {41: 'Chesterfield', 87: 'Henrico', 760: 'Richmond City'}
SQFT_PER_ACRE = 43_560


def main(path):
    df = pd.read_csv(path)
    print(f"rows: {len(df):,}    columns: {list(df.columns)}\n")

    # --- 1. Containment ------------------------------------------------------------------
    if 'FIPS' not in df.columns:
        print("NO FIPS COLUMN -- containment cannot be resolved this way. Stopping.")
        return
    print("=== 1. JURISDICTION (FIPS) ===")
    for fips, n in df['FIPS'].value_counts().items():
        label = NEIGHBOUR_FIPS.get(int(fips), f'other ({int(fips)})')
        print(f"    {int(fips):>4}  {label:<16} {n:>8,} rows  ({n/len(df)*100:5.1f}%)")
    richmond = df[df['FIPS'] == RICHMOND_CITY_FIPS]
    print(f"\n    Richmond City only: {len(richmond):,} rows "
          f"({len(df) - len(richmond):,} dropped as out-of-jurisdiction)\n")

    area_col = next((c for c in ('Shape__Area', 'Shape_Area', 'SHAPE_Area') if c in df.columns), None)
    if area_col is None:
        print("no recognised area column; stopping")
        return

    # --- 2. What Subtype means ----------------------------------------------------------
    print("=== 2. SUBTYPE SIZE DISTRIBUTION (Richmond only) ===")
    print("    If one subtype is C&I it should be FAR fewer rows with a MUCH larger median.")
    print(f"    {'subtype':>8} {'rows':>9} {'median':>12} {'mean':>12} {'max':>14} {'total':>16}")
    for subtype, grp in richmond.groupby('Subtype')[area_col]:
        print(f"    {subtype:>8} {len(grp):>9,} {grp.median():>12,.0f} {grp.mean():>12,.0f} "
              f"{grp.max():>14,.0f} {grp.sum():>16,.0f}")

    # --- 3. Units -----------------------------------------------------------------------
    print("\n=== 3. UNITS CHECK ===")
    largest = richmond[area_col].max()
    print(f"    largest polygon: {largest:,.0f}")
    print(f"      as sqft -> {largest/SQFT_PER_ACRE:8.2f} acres")
    print(f"      as sqm  -> {largest*10.7639/SQFT_PER_ACRE:8.2f} acres")
    print("    The plausible one is the unit. A single building above ~20 acres is implausible;")
    print("    Fairfax's own max was ~16 acres as sqft and ~173 acres as sqm, which settled it there.")

    # --- 4. The figures the extrapolation needs ----------------------------------------
    print("\n=== 4. FIGURES NEEDED FOR THE REFERENCE BASIS ===")
    print("    (assuming sqft; apply the >=600 sqft rooftop floor used for the other counties)")
    for subtype, grp in richmond.groupby('Subtype')[area_col]:
        eligible = grp[grp >= 600]
        print(f"    subtype {subtype}: {len(eligible):,} buildings >=600 sqft, "
              f"{eligible.sum():,.0f} sqft total ({eligible.sum()/SQFT_PER_ACRE:,.1f} acres)")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1])
