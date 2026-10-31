"""Lab 6 - Branch coverage tests for bus_transit_fare.py.

Run from the 'Lab 6' folder:
    coverage run --branch -m pytest BranchCoverageTest_bus_transit_fare.py
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


# ------------------------------------------------- input validation branch
def test_manifests_not_a_list_raises():
    with pytest.raises(ValueError):
        process_commute_manifest("not a list", 1.0)


def test_negative_booking_fee_raises():
    with pytest.raises(ValueError):
        process_commute_manifest([], -0.01)


def test_zero_booking_fee_is_valid():
    result = process_commute_manifest([make_manifest(
        "local", [commuter(2)], priority=True)], 0)
    assert result["total_fare"] == 4.5


# ------------------------------------------------------------ route_active
def test_inactive_route_is_skipped():
    manifests = [make_manifest("express", [commuter(3)], active=False)]
    result = process_commute_manifest(manifests, 2.0)
    assert result == {"total_fare": 0.0, "status": "ZERO_RIDERSHIP"}


def test_missing_route_active_defaults_to_inactive():
    result = process_commute_manifest([{"commuters": [commuter()]}], 1.0)
    assert result["status"] == "ZERO_RIDERSHIP"


def test_empty_manifest_list():
    result = process_commute_manifest([], 1.0)
    assert result == {"total_fare": 0.0, "status": "ZERO_RIDERSHIP"}


# -------------------------------------------------------------- route type
def test_express_regular_fare():
    result = process_commute_manifest(
        [make_manifest("express", [commuter(2)])], 1.0)
    assert result["total_fare"] == pytest.approx(8.0)  # 6.0 + 2*1.0


def test_shuttle_regular_fare():
    result = process_commute_manifest(
        [make_manifest("shuttle", [commuter(1)])], 1.0)
    assert result["total_fare"] == pytest.approx(5.0)  # 4.0 + 1*1.0


def test_unknown_route_type_is_rejected():
    result = process_commute_manifest(
        [make_manifest("ferry", [commuter(1)])], 1.0)
    assert result == {"total_fare": 0.0, "status": "ZERO_RIDERSHIP"}


def test_missing_route_type_defaults_to_local():
    manifest = {"route_active": True, "commuters": [commuter(2)]}
    result = process_commute_manifest([manifest], 1.0)
    assert result["total_fare"] == pytest.approx(4.5)


def test_missing_commuters_key_defaults_to_empty():
    result = process_commute_manifest(
        [{"route_active": True, "route_type": "local"}], 1.0)
    assert result["status"] == "ZERO_RIDERSHIP"


def test_active_route_with_no_commuters():
    result = process_commute_manifest([make_manifest("local", [])], 1.0)
    assert result["status"] == "ZERO_RIDERSHIP"


# ---------------------------------------------------------- passenger type
def test_student_discount():
    result = process_commute_manifest(
        [make_manifest("local", [commuter(2, "student")])], 1.0)
    assert result["total_fare"] == pytest.approx(1.75)  # (2.5+1.0)*0.5


def test_senior_discount():
    result = process_commute_manifest(
        [make_manifest("shuttle", [commuter(2, "senior")])], 1.0)
    assert result["total_fare"] == pytest.approx(3.5)  # (4.0+1.0)*0.7


def test_commuter_defaults_to_one_zone_regular():
    result = process_commute_manifest(
        [make_manifest("local", [{}])], 1.0)
    assert result["total_fare"] == pytest.approx(3.5)  # 2.5 + 1*1.0


def test_fare_is_rounded_to_two_decimals():
    result = process_commute_manifest(
        [make_manifest("local", [commuter(1, "senior")])], 1.0)
    assert result["total_fare"] == 2.1  # (2.5+0.5)*0.7 = 2.0999999...


# ------------------------------------------------------------------ zones
@pytest.mark.parametrize("bad_zones", [0, -1])
def test_non_positive_zones_rejected(bad_zones):
    result = process_commute_manifest(
        [make_manifest("local", [commuter(bad_zones)])], 1.0)
    assert result["status"] == "ZERO_RIDERSHIP"


# ------------------------------------------------------------ blacklisting
def test_blacklisted_on_local_route_pays_nothing_but_others_pay():
    commuters = [commuter(2, blacklisted=True), commuter(2)]
    result = process_commute_manifest(
        [make_manifest("local", commuters)], 1.0)
    assert result == {"total_fare": 4.5, "status": "COMPLETED"}


def test_blacklisted_on_express_voids_whole_manifest_fare():
    commuters = [commuter(2), commuter(1, blacklisted=True), commuter(3)]
    result = process_commute_manifest(
        [make_manifest("express", commuters)], 1.0)
    assert result == {"total_fare": 0.0, "status": "ZERO_RIDERSHIP"}


def test_blacklisted_on_express_still_charges_priority_fee():
    commuters = [commuter(2), commuter(1, blacklisted=True)]
    result = process_commute_manifest(
        [make_manifest("express", commuters, priority=True)], 2.0)
    assert result == {"total_fare": 2.0, "status": "COMPLETED"}


# --------------------------------------------------------- priority boarding
def test_priority_boarding_adds_booking_fee():
    result = process_commute_manifest(
        [make_manifest("local", [commuter(2)], priority=True)], 2.0)
    assert result["total_fare"] == pytest.approx(6.5)


def test_multiple_manifests_are_summed():
    manifests = [
        make_manifest("local", [commuter(2)]),
        make_manifest("express", [commuter(2)], priority=True),
    ]
    result = process_commute_manifest(manifests, 1.5)
    assert result["total_fare"] == pytest.approx(4.5 + 8.0 + 1.5)


# ------------------------------------------------------------ audit status
def test_five_rejections_triggers_audit():
    commuters = [commuter(0)] * 5 + [commuter(2)]
    result = process_commute_manifest(
        [make_manifest("local", commuters)], 1.0)
    assert result == {"total_fare": 4.5, "status": "AUDIT_REJECTED"}


def test_four_rejections_is_not_an_audit():
    commuters = [commuter(0)] * 4 + [commuter(2)]
    result = process_commute_manifest(
        [make_manifest("local", commuters)], 1.0)
    assert result == {"total_fare": 4.5, "status": "COMPLETED"}


# ------------------------------------------------------------- turnstiles
def test_turnstiles_none_or_empty_is_no_data():
    assert inspect_smartcard_turnstiles([]) == "NO_DATA"
    assert inspect_smartcard_turnstiles(None) == "NO_DATA"


def test_turnstile_two_consecutive_failures_jam():
    assert inspect_smartcard_turnstiles([[4, 5]]) == "TURNSTILE_JAM"


def test_turnstile_jam_found_on_later_device():
    matrix = [[0, 0, 0], [1, 4, 4]]
    assert inspect_smartcard_turnstiles(matrix) == "TURNSTILE_JAM"


def test_turnstile_streak_resets_after_good_reading():
    assert inspect_smartcard_turnstiles([[4, 0, 4, 0, 4]]) == "OPERATIONAL"


def test_turnstile_streak_does_not_carry_across_devices():
    assert inspect_smartcard_turnstiles([[0, 4], [4, 0]]) == "OPERATIONAL"


def test_turnstile_threshold_is_strictly_greater_than_three():
    assert inspect_smartcard_turnstiles([[3, 3, 3]]) == "OPERATIONAL"


def test_turnstile_device_with_no_readings():
    assert inspect_smartcard_turnstiles([[]]) == "OPERATIONAL"
