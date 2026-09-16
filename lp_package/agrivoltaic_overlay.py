"""
agrivoltaic_overlay.py

Applies agrivoltaic siting to a scenario's solar build: what it costs, and what land it uses.

WHY AN OVERLAY RATHER THAN A SCENARIO PROPERTY

Agrivoltaics was carried by Scenario 3 alone, which gave that scenario a benefit stream the others
were denied by construction. It is also unphysical to model it that way: Scenario 1's 156,737 MW has
to go somewhere, and that somewhere is overwhelmingly agricultural land -- the same land Scenario
3's agrivoltaic share sits on. Modelling identical acres as dual-use in one scenario and bare ground
in another is a difference in accounting, not in the world.

So siting applies to every scenario, on the same terms.

IT CHANGES COST AND LAND, NOT COMPLIANCE

A sheep-grazed tracking array generates exactly what a conventional tracking array generates -- NREL
gives both 5.9 acres/MW and the same structures, because they ARE the same structures. Nothing about
the hourly profile changes.

That is why this is arithmetic applied to a solved build rather than a constraint inside the LP. The
carve-out had to enter the residual because it changes what is generated; this does not.

WHAT IS AND IS NOT IN SCOPE HERE

In scope: the capital premium and the land footprint, per NREL/TP-6A20-77811.

Not in scope: lease income to the farmer, forage and grazing productivity, and the wider rural
economic effects. Those are real and are covered in the agrivoltaics appendix -- but the National
Standard Practice Manual excludes job creation and economic development from benefit-cost analysis
("while these may be societal in scope, this requires a different analysis than a BCA"), and the
land impact it does recognise cannot be monetised from anything this project holds.
"""
from dataclasses import dataclass

import agrivoltaic_basis as ab


@dataclass(frozen=True)
class AgrivoltaicOverlay:
    """Cost and land for one scenario's solar build under agrivoltaic siting."""
    total_solar_mw: float
    agrivoltaic_mw: float
    conventional_mw: float
    capex_premium_usd: float
    acres_low: float
    acres_high: float

    @property
    def acres_per_mw_effective(self):
        return (self.acres_low + self.acres_high) / 2.0 / self.total_solar_mw


def apply(solar_mw, share=None, livestock='sheep'):
    """Apply agrivoltaic siting to `solar_mw` of solar build.

    `share` defaults to this project's 85% assumption. `livestock` selects the configuration:
    sheep use conventional structures, cattle need elevation and more land.

    THE SHARE APPLIES TO SOLAR INSTALLED AFTER 2026, not to the existing fleet. Plant already in the
    ground was sited without agrivoltaics in mind, and retrofitting grazing onto an existing array is
    a different proposition from designing for it -- fencing, water, access and row spacing are all
    decided at construction.
    """
    if livestock not in ('sheep', 'cattle'):
        raise ValueError(
            f'unknown livestock {livestock!r}; expected "sheep" or "cattle". They differ in both '
            'capital and land -- NREL gives 5.9 acres/MW for sheep on conventional structures '
            'against 9.8 for the reinforced mount cattle need, and says cattle "are expected to be '
            'more expensive because of the need to elevate the panels".')
    if livestock == 'cattle':
        raise NotImplementedError(
            'Cattle agrivoltaics needs an elevated-structure capital premium that this project does '
            'not hold. NREL states the direction but gives no simple-cycle equivalent of the '
            '$0.07/W-DC grazing figure. Refusing rather than reusing the sheep premium, which would '
            'understate it.')

    share = ab.AGRIVOLTAIC_SHARE_OF_TOTAL_SOLAR if share is None else share
    if not 0.0 <= share <= 1.0:
        raise ValueError(f'share must be a fraction, got {share}')

    agri_mw = solar_mw * share
    conv_mw = solar_mw - agri_mw
    # NREL's premium is per W-DC; capacity here is MW, so 1e6 W per MW.
    premium = agri_mw * 1e6 * ab.AGRIVOLTAIC_SHEEP_CAPEX_PREMIUM_USD_PER_WDC

    # Land: sheep-grazed tracking uses the same acres/MW as conventional tracking, so the total
    # footprint does not change with the share -- only who else uses it does.
    return AgrivoltaicOverlay(
        total_solar_mw=solar_mw,
        agrivoltaic_mw=agri_mw,
        conventional_mw=conv_mw,
        capex_premium_usd=premium,
        acres_low=solar_mw * ab.ACRES_PER_MW_LOW,
        acres_high=solar_mw * ab.ACRES_PER_MW_HIGH,
    )
