"""Lab 6 - Line (code) coverage tests for bus_transit_fare.py.

Run from the 'Lab 6' folder:
    coverage run -m pytest CodeCoverageTest_bus_transit_fare.py
    coverage report -m
"""
import pytest

from bus_transit_fare import (
    inspect_smartcard_turnstiles,
    process_commute_manifest,
)


def make_manifest(route_type="local", commuters=None, active=True,
                  priority=False):
    """Build a manifest dict with sensible defaults."""
    return {
        "route_active": active,
        "route_type": route_type,
        "priority_boarding": priority,
        "commuters": commuters if commuters is not None else [],
    }


def commuter(zones=1, ptype="regular", blacklisted=False):
    """Build a commuter dict."""
    return {"zones": zones, "type": ptype, "blacklisted": blacklisted}


# ---------------------------------------------------------------- example
def test_single_regular_local_ride():
    manifests = [make_manifest("local", [commuter(2)])]
    result = process_commute_manifest(manifests, 2.0)
    assert result["total_fare"] == 4.5
    assert result["status"] == "COMPLETED"


# ------------------------------------------------------------ validation
def test_manifests_not_a_list_raises():
    with pytest.raises(ValueError):
        process_commute_manifest("not a list", 1.0)


# ------------------------------------------------------------ route types
def test_inactive_route_is_skipped():
    manifests = [make_manifest("express", [commuter(3)], active=False)]
    result = process_commute_manifest(manifests, 2.0)
    assert result == {"total_fare": 0.0, "status": "ZERO_RIDERSHIP"}


def test_express_regular_fare():
    result = process_commute_manifest(
        [make_manifest("express", [commuter(2)])], 1.0)
    assert result["total_fare"] == pytest.approx(8.0)


def test_shuttle_regular_fare():
    result = process_commute_manifest(
        [make_manifest("shuttle", [commuter(1)])], 1.0)
    assert result["total_fare"] == pytest.approx(5.0)


def test_unknown_route_type_is_rejected():
    result = process_commute_manifest(
        [make_manifest("ferry", [commuter(1)])], 1.0)
    assert result["status"] == "ZERO_RIDERSHIP"


# --------------------------------------------------------- passenger types
def test_student_discount():
    result = process_commute_manifest(
        [make_manifest("local", [commuter(2, "student")])], 1.0)
    assert result["total_fare"] == pytest.approx(1.75)


def test_senior_discount():
    result = process_commute_manifest(
        [make_manifest("shuttle", [commuter(2, "senior")])], 1.0)
    assert result["total_fare"] == pytest.approx(3.5)


def test_non_positive_zones_rejected():
    result = process_commute_manifest(
        [make_manifest("local", [commuter(0)])], 1.0)
    assert result["status"] == "ZERO_RIDERSHIP"


# ------------------------------------------------------------ blacklisting
def test_blacklisted_on_local_route_pays_nothing():
    result = process_commute_manifest(
        [make_manifest("local", [commuter(2, blacklisted=True),
                                 commuter(2)])], 1.0)
    assert result["total_fare"] == pytest.approx(4.5)


def test_blacklisted_on_express_voids_manifest_fare():
    commuters = [commuter(2), commuter(1, blacklisted=True)]
    result = process_commute_manifest(
        [make_manifest("express", commuters)], 1.0)
    assert result["status"] == "ZERO_RIDERSHIP"


# ----------------------------------------------------- booking and status
def test_priority_boarding_adds_booking_fee():
    result = process_commute_manifest(
        [make_manifest("local", [commuter(2)], priority=True)], 2.0)
    assert result["total_fare"] == pytest.approx(6.5)


def test_five_rejections_triggers_audit():
    commuters = [commuter(0)] * 5 + [commuter(2)]
    result = process_commute_manifest(
        [make_manifest("local", commuters)], 1.0)
    assert result["status"] == "AUDIT_REJECTED"


# -------------------------------------------------------------- turnstiles
def test_turnstiles_empty_is_no_data():
    assert inspect_smartcard_turnstiles([]) == "NO_DATA"


def test_turnstile_two_consecutive_failures_jam():
    assert inspect_smartcard_turnstiles([[4, 5]]) == "TURNSTILE_JAM"


def test_turnstile_operational():
    assert inspect_smartcard_turnstiles([[4, 0, 4]]) == "OPERATIONAL"
