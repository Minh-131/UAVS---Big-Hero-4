"""Deterministic illustrative data for the VNA SmartSearch prototype.

The generator mirrors the two web pages and supports Tết 2027 searches. None
of these records are live inventory or authorised Vietnam Airlines fares. In
production, ``flights_for_route`` and ``get_flight`` are the provider boundary
to replace with VNA-authorised schedule, offer and availability services.
"""

from __future__ import annotations

from datetime import date, timedelta


FLIGHTS = [
    {"id": "VN782-2026-02-10", "flight_number": "VN782", "origin": "SYD", "destination": "SGN", "origin_city": "Sydney", "destination_city": "Ho Chi Minh City", "date": "2026-02-10", "depart": "11:20", "arrive": "17:05", "duration": "9h 45m", "stops": 0, "price_aud": 505, "cabin": "Economy", "baggage_kg": 23, "aircraft": "A350"},
    {"id": "VN770-2026-02-11", "flight_number": "VN770", "origin": "SYD", "destination": "HAN", "origin_city": "Sydney", "destination_city": "Hanoi", "date": "2026-02-11", "depart": "10:05", "arrive": "16:40", "duration": "10h 35m", "stops": 0, "price_aud": 540, "cabin": "Economy", "baggage_kg": 23, "aircraft": "B787"},
    {"id": "VN760-2026-02-12", "flight_number": "VN760", "origin": "MEL", "destination": "HAN", "origin_city": "Melbourne", "destination_city": "Hanoi", "date": "2026-02-12", "depart": "11:00", "arrive": "18:05", "duration": "11h 05m", "stops": 0, "price_aud": 565, "cabin": "Economy", "baggage_kg": 23, "aircraft": "B787"},
]


# These parameters are fixtures, not published VNA schedules or prices.
ROUTE_SPEC = {
    ("SYD", "SGN"): {"origin_city": "Sydney", "destination_city": "Ho Chi Minh City", "duration": "8h 50m", "base": 510, "aircraft": "A350", "times": [("07:20", "VN781"), ("11:20", "VN782"), ("21:35", "VN772")]},
    ("SYD", "HAN"): {"origin_city": "Sydney", "destination_city": "Hanoi", "duration": "9h 55m", "base": 545, "aircraft": "B787", "times": [("10:05", "VN770"), ("22:10", "VN774")]},
    ("SYD", "DAD"): {"origin_city": "Sydney", "destination_city": "Da Nang", "duration": "9h 20m", "base": 565, "aircraft": "A321neo", "times": [("09:30", "VN311")]},
    ("MEL", "SGN"): {"origin_city": "Melbourne", "destination_city": "Ho Chi Minh City", "duration": "8h 25m", "base": 500, "aircraft": "A350", "times": [("12:15", "VN720"), ("23:45", "VN722")]},
    ("MEL", "HAN"): {"origin_city": "Melbourne", "destination_city": "Hanoi", "duration": "9h 15m", "base": 540, "aircraft": "B787", "times": [("11:00", "VN760"), ("23:20", "VN766")]},
    ("PER", "SGN"): {"origin_city": "Perth", "destination_city": "Ho Chi Minh City", "duration": "7h 05m", "base": 470, "aircraft": "A321neo", "times": [("01:15", "VN68"), ("14:30", "VN66")]},
    ("PER", "HAN"): {"origin_city": "Perth", "destination_city": "Hanoi", "duration": "8h 10m", "base": 510, "aircraft": "A350", "times": [("23:55", "VN72")]},
    ("PER", "DAD"): {"origin_city": "Perth", "destination_city": "Da Nang", "duration": "7h 40m", "base": 520, "aircraft": "A321neo", "times": [("02:20", "VN76")]},
    ("BNE", "SGN"): {"origin_city": "Brisbane", "destination_city": "Ho Chi Minh City", "duration": "9h 30m", "base": 540, "aircraft": "A350", "times": [("13:40", "VN726")], "stops": 1},
}


def _season_factor(date_str: str) -> float:
    d = date.fromisoformat(date_str)
    if d.month == 2 and 1 <= d.day <= 12:
        return 1.75
    if (d.month == 12 and d.day >= 18) or (d.month == 1 and d.day <= 5):
        return 1.55
    if d.month in (12, 1):
        return 1.35
    if d.month == 2:
        return 1.4
    if 6 <= d.month <= 8:
        return 1.3
    if d.month in (3, 9, 10):
        return 0.9
    return 1.0


def _seeded_var(seed: str) -> float:
    value = 0
    for char in seed:
        value = (value * 31 + ord(char)) % 997
    return value / 997


def _round_five(value: float) -> int:
    return int(value / 5 + 0.5) * 5


def generate_flights(origin: str, destination: str, date_str: str) -> list[dict]:
    origin, destination = origin.upper(), destination.upper()
    spec = ROUTE_SPEC.get((origin, destination))
    if not spec:
        return []
    results = []
    for depart, flight_number in spec["times"]:
        price = _round_five(spec["base"] * _season_factor(date_str) + _seeded_var(flight_number + date_str) * 90 - 30)
        results.append({
            "id": f"{flight_number}-{date_str}", "flight_number": flight_number,
            "origin": origin, "destination": destination,
            "origin_city": spec["origin_city"], "destination_city": spec["destination_city"],
            "date": date_str, "depart": depart, "arrive": "See VNA at handoff",
            "duration": spec["duration"], "stops": spec.get("stops", 0),
            "price_aud": price, "cabin": "Economy", "baggage_kg": 23,
            "aircraft": spec["aircraft"], "data_status": "illustrative_fixture",
        })
    return results


def flights_for_route(origin: str, destination: str, date_from: str | None = None, date_to: str | None = None) -> list[dict]:
    origin, destination = origin.upper(), destination.upper()
    if (origin, destination) not in ROUTE_SPEC:
        return []
    start = date.fromisoformat(date_from or "2027-02-01")
    end = date.fromisoformat(date_to) if date_to else start + timedelta(days=6)
    days = max(1, min(14, (end - start).days + 1))
    results = []
    for offset in range(days):
        results.extend(generate_flights(origin, destination, (start + timedelta(days=offset)).isoformat()))
    return results


def get_flight(flight_id: str) -> dict | None:
    flight_id = flight_id.upper()
    exact = next((item for item in FLIGHTS if item["id"] == flight_id), None)
    if exact:
        return exact
    parts = flight_id.rsplit("-", 3)
    if len(parts) != 4:
        return None
    flight_number, year, month, day = parts
    date_str = f"{year}-{month}-{day}"
    try:
        date.fromisoformat(date_str)
    except ValueError:
        return None
    for (origin, destination), spec in ROUTE_SPEC.items():
        if any(code == flight_number for _depart, code in spec["times"]):
            return next((f for f in generate_flights(origin, destination, date_str) if f["id"] == flight_id), None)
    return None


# Prototype-only personalisation scenarios; not official tier entitlements.
LOTUSMILES_DISCOUNT = {"none": 0.00, "silver": 0.05, "titanium": 0.08, "gold": 0.10, "platinum": 0.12}

BAGGAGE_OPTIONS = [
    {"code": "EXTRA20", "label": "+20kg checked", "price_aud": 60},
    {"code": "EXTRA30", "label": "+30kg checked", "price_aud": 85},
    {"code": "EXTRA40", "label": "+40kg checked (family)", "price_aud": 110},
]

CITY_NAMES = {"SYD": "Sydney", "MEL": "Melbourne", "BNE": "Brisbane", "PER": "Perth", "SGN": "Ho Chi Minh City", "HAN": "Hanoi", "DAD": "Da Nang"}

ROUTES = {
    route: {"weekly_frequency": "Illustrative; verify with authorised VNA schedule", "typical_aircraft": [spec["aircraft"]], "flight_time": spec["duration"]}
    for route, spec in ROUTE_SPEC.items()
}
