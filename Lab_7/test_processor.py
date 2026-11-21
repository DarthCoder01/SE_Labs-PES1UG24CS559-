import math

import pytest
from hypothesis import given, strategies as st

from processor import (
    compute_passenger_density,
    lookup_concession_discount,
    parse_transit_corridor,
)

inputs = st.one_of(st.text(), st.none(), st.integers(), st.binary())


@given(inputs)
def test_parse_transit_corridor_no_crash(s):
    try:
        result = parse_transit_corridor(s)
    except Exception as exc:
        pytest.fail(f"Unexpected {type(exc).__name__} for {s!r}")
    assert result is None or isinstance(result, str)


@given(inputs)
def test_lookup_concession_discount_safe(s):
    try:
        result = lookup_concession_discount(s)
    except Exception as exc:
        pytest.fail(f"Unexpected {type(exc).__name__} for {s!r}")
    assert result is None or 0 <= result <= 1


@given(inputs)
def test_compute_passenger_density_safe(s):
    try:
        result = compute_passenger_density(s)
    except Exception as exc:
        pytest.fail(f"Unexpected {type(exc).__name__} for {s!r}")
    assert result is None or (math.isfinite(result) and result >= 0)


@given(st.integers(0, 100000), st.sampled_from(["dt", "west", "A1"]))
def test_corridor_fare(zones, origin):
    assert parse_transit_corridor(f"{origin}-up-{zones}") == (
        f"Route {origin.upper()}->UP: {zones} Zones, Fare ${2.50 + 0.75 * zones:.2f}"
    )


@given(st.sampled_from([("standard", 1), ("student", .5), ("senior", .35),
                        ("military", .2), ("child", 0)]))
def test_category_multiplier(case):
    category, expected = case
    assert lookup_concession_discount(f" {category} ") == expected


@given(st.integers(0, 100000), st.integers(1, 10000))
def test_density_value(passengers, km):
    assert compute_passenger_density(f"{passengers}/{km}") == round(passengers / km, 2)


def test_invalid_values():
    assert parse_transit_corridor(" -UP-3") is None
    assert lookup_concession_discount("visitor") is None
    for ratio in ("50/0", "-2/1", "4/-1", "nan/2", "2/inf", "1e308/1e-308"):
        assert compute_passenger_density(ratio) is None
