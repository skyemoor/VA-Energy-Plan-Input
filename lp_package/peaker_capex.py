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

SOURCING (updated 2026-09-10 with material found after the initial version)

The strongest derivation available anchors on the SAME Wood Mackenzie equipment figure that
ccgt_capex_kw() uses, converted to installed terms using the simple-cycle equipment share rather
than the combined-cycle one:

- Wood Mackenzie (April 2026, reported by Utility Dive): turbine EQUIPMENT-only cost reaching
  **$600/kW by end-2027**, a 195% increase since 2019.
- SecondWatt gas turbine market analysis (late August 2026 -- the most recent source found)
  states the conversion rule explicitly and warns against the exact error this module could
  otherwise make: "Do not blend the $/kW figures. The $600/kW estimate is turbine equipment only;
  Wood Mackenzie puts turbines at 20-30% of a combined-cycle project's cost **and a higher share
  of a simple-cycle one**."

That last clause is the key to deriving simple-cycle installed cost correctly. A simple-cycle
plant has no heat recovery steam generator, no steam turbine and no associated water systems, so
the turbine is a larger fraction of a smaller total. Taking the equipment share at roughly 40-50%
for simple cycle against 20-30% for combined cycle:

    combined cycle:  $600 / 0.20-0.30  =  $2,000-3,000/kW   (matches ccgt_capex_kw()'s $3,000)
    simple cycle:    $600 / 0.40-0.50  =  $1,200-1,500/kW

**That derived range lands directly on GridLab's independently-reported figure**, which is the
cross-check that makes it usable rather than merely plausible:

- GridLab, "The New Reality of Power Generation" (September 2025), with Energy Futures Group,
  Component Reliability Consultants and Halcyon. Combustion-turbine projects with in-service dates
  2025-2029; projects completing 2026-2027 reported at **$1,116-$1,427/kW**. Regression on
  in-service year shows costs rising at a statistically significant rate.
- EIA, via the same dataset: CT plants placed in service in 2023 averaged **$562/kW**; 2025
  in-service costs range **$728-$1,544/kW**. Establishes trajectory, not current level.
- USP&E, "Gas Turbine EPC Costs 2026" (April 2026), the only size-tiered current source found:
  **25-50 MW at $1,400-2,000/kW**, **250+ MW at $700-1,100/kW**. Supplies the SHAPE across size
  tiers. Carries its own volatility warning -- prices "based on historical data but have been
  increasing by 2-3x due to extraordinary demand from AI-driven hyperscalers" -- so its levels
  are not used directly. Dual-fuel adds $150-250/kW; fast-track under 18 months adds 10-20%.

Two independent derivations (Wood Mackenzie equipment-share conversion, and GridLab's reported
project filings) converging on $1,100-1,500/kW for the mid tier is what this module rests on.

MARKET CONTEXT THAT BOUNDS CONFIDENCE

These are not stable prices. Global orders reached 110 GW by end-2025 against manufacturing
capacity of 60-70 GW/year; Q2 2026 orders hit a record 38 GW, 29% above Q1. Wood Mackenzie's own
read is that an order placed now does not take delivery before 2029, and the three major OEMs now
require reservation fees to hold a manufacturing slot -- two Kentucky utilities paid GE Vernova
$25 million to reserve a turbine for 2030 commercial operation. EPRI's figure moved from
$2,000/kW to $3,000/kW in six months.

**Implication for modeling**: the 'high' case is not a tail scenario, and the central case should
not be treated as stable across a 20-year build programme. Anything relying on these figures for
a checkpoint beyond roughly 2030 should carry an explicit escalation assumption rather than
holding this level flat.
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
