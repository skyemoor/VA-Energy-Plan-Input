# Methodology: Deriving gas_allowed_frac for Any Checkpoint

**Update note:** Since this document was first written, export has been
removed from `build_problem()` entirely (see the appendix's A.9 for full
detail), and a data-verified existing gas fleet capacity cap (Schedule A/B)
is now applied alongside `gas_allowed_frac` at every checkpoint -- both
change the mechanics described below. The core numerical-search approach
still applies, but two things are materially different: (1) with export
gone, one of the three sources of demand-side/generation-side divergence
this document originally cited no longer applies, though storage
round-trip loss and curtailment still do, so a clean closed-form derivation
still isn't available; (2) with the capacity cap now also active, the
capacity constraint can become the binding limit on gas dispatch instead
of `gas_allowed_frac` itself -- when this happens, changing `frac` further
has no effect on the resulting share at all (confirmed directly: two
different frac values, 0.2915 and 0.3642, produced the identical resulting
share once capacity was the true binding constraint) -- worth checking for
this condition before continuing to iterate on frac if refinement seems to
stop responding.

## Why this can't be computed algebraically in one step

`gas_allowed_frac` is a generation-side LP input (the code's constraint bounds
gas as a share of nuclear+exist_solar+wind+new_solar, EXCLUDING storage
discharge). The actual RPS requirement is a demand-side target (clean share
of non-nuclear DEMAND). These only coincide exactly with zero storage
round-trip loss and zero curtailment -- neither of which holds here (export
itself is no longer a factor, per the update note above, but the other two
still create the same basic circularity).
The relationship between the two also depends on the LP's own solved output,
creating circularity that rules out a clean closed-form derivation.

## The working method: numerical search via linear extrapolation

1. Compute the target: `target = 1 - rps_clean_pct` (e.g., 0.41 clean at
   2030 -> target = 0.59 demand-side gas share of non-nuclear demand)
2. Get a smart starting guess: use the ratio (converged_frac/target) from
   the nearest already-solved checkpoint as a multiplier against the new
   target. This has consistently landed within ~10-15 percentage points of
   the true answer across all three checkpoints solved so far.
3. Solve once, check the actual resulting demand-side share (sum hourly `g`
   dispatch / non-nuclear demand -- NOT the `gascum` variable directly,
   watch units: `gascum` accumulates in GWh via a /1000 factor per hour,
   while raw `g[t]` is in MWh).
4. Get a second point (adjust the guess based on gap direction and rough
   local slope, ~1.7-2.9 has been typical -- wider range than before now
   that the capacity cap also interacts with this slope).
5. Linear-interpolate between the two closest, bracketing points -- this has
   converged to within 0.0001-0.0005 of the target on the first or second
   refinement in most cases, though slightly less tight than before the
   capacity cap was added (occasional 0.002-0.004 residual gaps now seen).
6. **NEW: if step 4/5 shows the resulting share unchanged across two
   different frac values, stop iterating on frac** -- this means the
   existing-fleet capacity cap, not the RPS percentage, is now the true
   binding constraint at this checkpoint, and no frac adjustment will
   change the outcome. This is itself an important finding (a genuine
   capacity shortfall), not just a converged answer -- see A.8.6 in the
   appendix for the standard response (overhaul/retain existing near-EOL
   plants, then new simple-cycle build if needed).

## Known convergence points (see derived_values_scenario1_checkpoints.csv)

**Superseded, export-enabled, uncapped values (pre-A.8/A.9):** Ratio
(converged_frac/target) was NOT stable across checkpoints -- 0.6149 (2030),
0.7100 (2035), 0.7738 (2040). These values no longer apply as starting
points now that export is removed and the capacity cap is active --
re-derive from scratch, or use the most recent post-A.9 converged values
as starting points instead once available.

## Timing

**Updated:** each solve now takes roughly 260-290 seconds (up from the
earlier 100-150 seconds), following the addition of curtailment/unserved-
energy variables (see A.11 in the appendix). Investigated and ruled out
cost-coefficient conditioning as the primary cause; the added
variables/constraints themselves are the more likely driver. Budget
accordingly -- 2-3 solves per checkpoint now means roughly 13-15 minutes
total when deriving a new gas_allowed_frac value, not 5-8.
