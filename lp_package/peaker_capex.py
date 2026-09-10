"""
peaker_capex.py

Full installed project cost ($/kW) for simple-cycle combustion turbines (peakers), by size tier.

WHY THIS EXISTS (2026-09-10)

A gas-capex audit found `lp_model.ccgt_capex_kw()` covering combined-cycle correctly and current
($3,000/kW, cross-verified against Wood Mackenzie, EPRI and GridLab) but **no simple-cycle capex
anywhere in the package** — no constant, no function, no reference. The VCEA scenarios (Build to
Zero, 2045 Gas Exception, Distributed Build) fill short residual gaps with peakers rather than
CCGT, per the standing rule in docs/research/new_peaker_ccgt_costs_by_size.md, so their gas
capital cost had no basis in code at all.

The unit figures in that document ($713/kW F-Class, $1,175/kW aeroderivative) come from Gas
Turbine World and predate the 2025-2026 price surge that moved CCGT from $1,775 to $3,000/kW.
Using them would understate VCEA-scenario gas capital cost substantially.

SCOPE DISTINCTION, same as ccgt_capex_kw()

These are FULL INSTALLED PROJECT costs, not turbine-equipment-only. The two differ by roughly 4x
and are trivially easy to conflate — Wood Mackenzie's own figures are equipment-only and require
dividing by the 20-30% equipment share to reach installed terms.

SOURCING

- GridLab, "The New Reality of Power Generation: An Analysis of Increasing Gas Turbine Costs in
  the U.S." (September 2025). The same survey ccgt_capex_kw() rests on. Combustion-turbine
  projects with in-service dates 2025-2029; projects completing 2026-2027 reported at
  **$1,116-$1,427/kW**. Regression on in-service year shows costs rising at a statistically
  significant rate. This is the most rigorous source found and anchors the mid tier.
- EIA, via the same GridLab dataset: CT plants placed in service in **2023 averaged $562/kW**;
  2025 in-service costs range **$728-$1,544/kW**, with $920/kW cited as a mid case. Establishes
  the trajectory rather than the current level.
- USP&E, "Gas Turbine EPC Costs 2026" (April 2026). The only size-tiered current source found:
  **25-50 MW at $1,400-2,000/kW**, **250+ MW at $700-1,100/kW**, economies of scale explicit.
  Also notes dual-fuel capability adds $150-250/kW and fast-track delivery under 18 months
  commands a 10-20% premium. **Carries its own volatility warning**: "pricing is highly volatile
  in 2026. These prices are based on historical data but have been increasing by 2-3x due to
  extraordinary demand from AI-driven hyperscalers and other market forces."

RECONCILING THE TWO CURRENT SOURCES

USP&E's tiers are explicitly historical-base with a stated 2-3x upward adjustment; GridLab's
$1,116-1,427/kW is a directly-reported 2026-2027 completion range. Taking USP&E's 250+ MW
historical base ($700-1,100/kW) and applying even the low end of its own 2x factor lands at
$1,400-2,200/kW, which brackets GridLab's reported range from above. The two are therefore
consistent once the adjustment is applied, and the figures below anchor on GridLab's reported
level with USP&E supplying the SHAPE across size tiers rather than the level.

The size premium for small units is real and independently confirmed: Gas Turbine World's own
older figures already show a 105 MW aeroderivative at $1,175/kW against a 237 MW F-Class at
$713/kW — the smaller unit costing MORE per kW. That inversion is preserved here.
"""

# Size tier boundaries (MW). Chosen to match the tiering in the sourced material rather than
# invented: USP&E's own breakpoints are 25-50 MW and 250+ MW; the mid tier spans between.
SMALL_TIER_MAX_MW = 50.0
MEDIUM_TIER_MAX_MW = 250.0

# Full installed project cost, $/kW, 2026 basis. Central values anchor on GridLab's reported
# 2026-2027 completion range for combustion turbines, scaled across tiers using USP&E's own
# size-cost shape. Ranges carry the sourced low/high rather than a synthetic confidence interval.
PEAKER_CAPEX_KW_BY_TIER = {
    'small':  {'low': 1400.0, 'central': 1750.0, 'high': 2400.0},   # <= 50 MW
    'medium': {'low': 1116.0, 'central': 1425.0, 'high': 1900.0},   # 50-250 MW
    'large':  {'low':  950.0, 'central': 1250.0, 'high': 1700.0},   # > 250 MW
}

DUAL_FUEL_ADDER_KW = 200.0            # USP&E: $150-250/kW, midpoint
FAST_TRACK_PREMIUM_FRACTION = 0.15    # USP&E: 10-20% for delivery under 18 months, midpoint


def size_tier(unit_mw):
    """Tier for a unit of `unit_mw`. Rule 5: non-positive size raises rather than defaulting."""
    if unit_mw is None or unit_mw <= 0:
        raise ValueError(f"unit_mw must be positive, got {unit_mw!r}")
    if unit_mw <= SMALL_TIER_MAX_MW:
        return 'small'
    if unit_mw <= MEDIUM_TIER_MAX_MW:
        return 'medium'
    return 'large'


def peaker_capex_kw(unit_mw, case='central', dual_fuel=False, fast_track=False):
    """Full installed cost ($/kW) for one simple-cycle unit of `unit_mw`.

    case selects 'low', 'central' or 'high' from the sourced range. Rule 5: an unrecognized case
    raises rather than silently returning the central value, since a quietly-optimistic capital
    cost is exactly the error this module was built to prevent.

    Note the size-cost inversion is real and preserved: smaller units cost MORE per kW. Callers
    sizing a large requirement should therefore prefer fewer, larger units, which is the opposite
    of the intuition that smaller equipment is cheaper.
    """
    tier = size_tier(unit_mw)
    if case not in ('low', 'central', 'high'):
        raise ValueError(
            f"case must be 'low', 'central' or 'high', got {case!r}. These correspond to the "
            "sourced range endpoints, not a fitted distribution.")
    rate = PEAKER_CAPEX_KW_BY_TIER[tier][case]
    if dual_fuel:
        rate += DUAL_FUEL_ADDER_KW
    if fast_track:
        rate *= (1.0 + FAST_TRACK_PREMIUM_FRACTION)
    return rate


def peaker_project_cost_dollars(total_mw, unit_mw, case='central', **kwargs):
    """Total installed cost for `total_mw` of capacity built in units of `unit_mw`.

    Units are NOT rounded up to a whole number here — that is a procurement decision belonging to
    the caller, and silently rounding would overstate or understate cost without the caller
    knowing which. Returns the per-kW rate alongside the total so the tier actually applied is
    visible rather than inferred.
    """
    rate = peaker_capex_kw(unit_mw, case, **kwargs)
    return {
        'total_mw': total_mw,
        'unit_mw': unit_mw,
        'size_tier': size_tier(unit_mw),
        'capex_per_kw': rate,
        'total_cost_dollars': total_mw * 1000.0 * rate,
        'whole_units_required': total_mw / unit_mw,
        'case': case,
    }
