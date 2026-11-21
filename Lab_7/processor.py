"""Bus fare calculations. Each function returns None for invalid input."""

import math


def parse_transit_corridor(corridor_code):
    if not isinstance(corridor_code, str):
        return None
    try:
        orig, dest, zones_str = (part.strip() for part in corridor_code.split("-"))
        zones = int(zones_str)
    except ValueError:
        return None
    if not orig or not dest or zones < 0:
        return None
    # Integer cents keep the fare exact even for large zone counts.
    dollars, cents = divmod(250 + 75 * zones, 100)
    return f"Route {orig.upper()}->{dest.upper()}: {zones} Zones, Fare ${dollars}.{cents:02d}"


def lookup_concession_discount(category_name):
    if not isinstance(category_name, str):
        return None
    discounts = {"STANDARD": 1.0, "STUDENT": 0.50, "SENIOR": 0.35,
                 "MILITARY": 0.20, "CHILD": 0.0}
    return discounts.get(category_name.strip().upper())


def compute_passenger_density(occupancy_ratio_str):
    if not isinstance(occupancy_ratio_str, str):
        return None
    try:
        passengers, km = map(float, occupancy_ratio_str.split("/"))
    except ValueError:
        return None
    if not (math.isfinite(passengers) and passengers >= 0 and math.isfinite(km) and km > 0):
        return None
    density = passengers / km
    return round(density, 2) if math.isfinite(density) else None


def main():
    print("==== Running parse_transit_corridor ====")
    c_input = input("Enter corridor (e.g. DT-UP-3): ")
    print(parse_transit_corridor(c_input) or "Invalid corridor.")

    print("\n==== Running lookup_concession_discount ====")
    cat_input = input("Enter concession category (e.g. STUDENT, SENIOR): ")
    multiplier = lookup_concession_discount(cat_input)
    print("Multiplier:", multiplier if multiplier is not None else "Unknown category.")

    print("\n==== Running compute_passenger_density ====")
    d_input = input("Enter passengers/km (e.g. 50/10.0): ")
    density = compute_passenger_density(d_input)
    print("Density:", density if density is not None else "Invalid ratio. Use a nonnegative count and positive distance.")

if __name__ == "__main__":
    main()
