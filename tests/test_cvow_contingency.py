"""
test_cvow_contingency.py

CVOW's delivered capacity and its status as a single contingency (decided 2026-09-12).

WHY IT MATTERS: docs/methodology/Reserves_Approach.md argues this project need not model
contingency reserve, because the NERC BAL-002 obligation belongs to PJM as Balancing Authority and
is met jointly across the Reserve Sharing Group. That argument concerns Virginia's SHARE of an
EXISTING requirement. It does not address Virginia ENLARGING the requirement -- which is what a new
2,050 MW single contingency would do, since BAL-002 sizes reserve to the Most Severe Single
Contingency.
"""
import pytest

import assumptions as a
import lp_model as lp


class TestDeliveredCapacityNotNameplate:
    """The point at which electricity is usable is the transmission interconnect."""

    def test_delivered_is_below_nameplate(self):
        assert a.CVOW_DELIVERED_AT_INTERCONNECT_MW < lp.CVOW_MW

    def test_delivered_is_below_the_modelled_peak(self):
        """The modelled wind CF peaks at 0.8176, giving 2,115 MW -- nameplate never occurs.
        2,050 sits just below that, consistent with a further few percent of electrical loss
        across the collector system, offshore substation and ~25 miles of export cable."""
        modelled_peak = lp.CVOW_MW * 0.8176
        assert a.CVOW_DELIVERED_AT_INTERCONNECT_MW < modelled_peak
        assert a.CVOW_DELIVERED_AT_INTERCONNECT_MW > modelled_peak * 0.95

    def test_nameplate_constant_is_unchanged(self):
        """CVOW_MW stays nameplate -- the delivered figure is a separate constant, not a
        correction to it. Overwriting nameplate would break the CF multiplication."""
        assert lp.CVOW_MW == pytest.approx(2_587.2)


class TestSingleContingencyStatus:

    def test_assumed_single_contingency(self):
        assert a.CVOW_IS_SINGLE_CONTINGENCY is True

    def test_exceeds_the_rto_synchronized_reserve_requirement(self):
        """1.37-1.58x the 1,300-1,500 MW RTO requirement, and 2.16x a nuclear unit."""
        for req in (1_300, 1_500):
            assert a.CVOW_DELIVERED_AT_INTERCONNECT_MW / req > 1.3
        assert a.CVOW_DELIVERED_AT_INTERCONNECT_MW / 950 > 2.0

    def test_the_gap_in_the_reserves_argument_is_recorded(self):
        """Sharing an existing requirement is a different question from enlarging it, and the
        Reserves_Approach argument only covers the first."""
        n = a.CVOW_MSSC_NOTE
        assert 'not merely consuming' in n or 'rather than merely consuming' in n
        assert 'not enlarging it' in n

    def test_the_unverified_configuration_is_flagged(self):
        """Multiple independent export circuits would shrink the effect. The single-point
        assumption is deliberately the conservative one."""
        assert 'configuration is unverified' in a.CVOW_MSSC_NOTE
        assert 'multiple independent circuits' in a.CVOW_MSSC_NOTE
