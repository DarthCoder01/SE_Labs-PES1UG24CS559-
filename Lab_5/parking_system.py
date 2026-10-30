"""Campus parking permit manager.

Issues permits for vehicles in zones A to C, revokes them, checks for
expired permits and flags vehicles that should not be parked in a zone.
"""
import json
import secrets
import sys
from datetime import date, datetime, timedelta

ZONES = ("A", "B", "C")
DATE_FORMAT = "%Y-%m-%d"
PERMIT_VALIDITY_DAYS = 180

# Shared in-memory permit store: {plate: {"zone", "permit", "expiry"}}
permits = {}


def _clean_plate(vehicle_plate):
    """Return a normalised plate, or raise ValueError if it is invalid."""
    if not isinstance(vehicle_plate, str) or not vehicle_plate.strip():
        raise ValueError("Vehicle plate must be a non-empty string")
    return vehicle_plate.strip().upper()


def register_permit(vehicle_plate, zone_id, zone_records=None):
    """Issue a permit and return its number.

    Raises ValueError for an empty plate or an unknown zone.
    """
    plate = _clean_plate(vehicle_plate)
    if zone_id not in ZONES:
        raise ValueError(f"Unknown zone {zone_id!r}; expected one of {ZONES}")
    if zone_records is None:
        zone_records = []

    # secrets (not random) so permit numbers are not predictable
    permit_no = "P" + str(secrets.randbelow(90000) + 10000)
    expiry = datetime.now() + timedelta(days=PERMIT_VALIDITY_DAYS)
    permits[plate] = {
        "zone": zone_id,
        "permit": permit_no,
        "expiry": expiry.strftime(DATE_FORMAT),
    }
    zone_records.append((plate, zone_id))
    return permit_no


def revoke_permit(vehicle_plate):
    """Remove a permit. Return True if one existed, else False."""
    if not isinstance(vehicle_plate, str):
        return False
    return permits.pop(vehicle_plate.strip().upper(), None) is not None


def is_expired(vehicle_plate):
    """Return True if the plate has no valid, in-date permit."""
    permit = permits.get(vehicle_plate)
    if permit is None:
        return True
    try:
        expiry = datetime.strptime(permit["expiry"], DATE_FORMAT).date()
    except (KeyError, ValueError):
        return True  # unreadable expiry: fail closed, treat as expired
    return expiry < date.today()


def scan_zone(zone_id, plates_seen):
    """Return the plates that should not be parked in zone_id."""
    return [
        plate
        for plate in plates_seen
        if plate not in permits
        or permits[plate]["zone"] != zone_id
        or is_expired(plate)
    ]


def load_permit_database(file="permits.json"):
    """Load permits from a JSON file; start empty if unreadable."""
    loaded = {}
    try:
        with open(file, encoding="utf-8") as handle:
            loaded = json.load(handle)
    except FileNotFoundError:
        pass  # first run: no database yet
    except (OSError, json.JSONDecodeError) as err:
        print(f"Warning: could not read {file}: {err}", file=sys.stderr)
    permits.clear()
    permits.update(loaded)


def save_permit_database(file="permits.json"):
    """Write all permits to a JSON file."""
    with open(file, "w", encoding="utf-8") as handle:
        json.dump(permits, handle, indent=2)


def set_expiry(vehicle_plate, date_text):
    """Set a permit's expiry; date_text must be YYYY-MM-DD."""
    if vehicle_plate not in permits:
        raise KeyError(f"No permit for plate {vehicle_plate!r}")
    datetime.strptime(date_text, DATE_FORMAT)  # raises ValueError if bad
    permits[vehicle_plate]["expiry"] = date_text


def main():
    """Run the demo."""
    load_permit_database()
    for plate, zone in [
        ("KA01AB1234", "A"),
        ("KA05XY9999", "Z"),
        ("", "B"),
        (None, "C"),
    ]:
        try:
            register_permit(plate, zone)
        except ValueError as err:
            print("Rejected:", err)
    try:
        set_expiry("KA01AB1234", "2020-01-01")
    except (KeyError, ValueError) as err:
        print("Could not set expiry:", err)
    revoke_permit("MH12ZZ0000")
    print("Flagged in zone A:",
          scan_zone("A", ["KA01AB1234", "KA05XY9999", "TN09QQ1111"]))
    plate = input("Plate to revoke (Enter to skip): ").strip()
    if plate and not revoke_permit(plate):
        print("No permit found for", plate)
    save_permit_database()
    print("Permits on file:", len(permits))


if __name__ == "__main__":
    main()
