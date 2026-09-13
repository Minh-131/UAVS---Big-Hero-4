"""
============================================================================
 VNA AGENTIC GATEWAY  —  MCP Server
 UAVS Hackathon 2026 · Round 2 · Team Four Pho
============================================================================

WHAT THIS IS
  A Model Context Protocol (MCP) server that lets ANY AI agent
  (Claude, ChatGPT, a travel assistant) search Vietnam Airlines flights and
  start a booking DIRECTLY with VNA — bypassing OTAs entirely.

  This is the "agentic-commerce gateway" the VNA brief asks teams to imagine:
  when travellers shift from browsing websites to asking AI agents, VNA is the
  carrier the agent can actually talk to.

GUARDRAILS (baked in, mirror the brief's constraints)
  • The gateway NEVER invents fares — it only returns fixture/feed data.
  • It NEVER charges a card. create_booking_intent returns a safe link to the
    official VNA website; a real deep link requires a VNA-issued offer token
    (the booking backend is third-party controlled and left untouched).
  • Every result is sourced; Lotusmiles pricing is clearly labelled.

TOOL TIERS (build/verify in this order — see README)
  CORE (must work):   search_flights, get_fare_details, create_booking_intent
  DIFFERENTIATOR:     get_lotusmiles_price, suggest_flexible_dates
  SUPPLEMENTARY:      check_availability, get_baggage_options,
                      compare_family_bundle, get_route_info,
                      plan_multi_origin_trip

RUN
  pip install "mcp[cli]"
  python server.py                 # stdio transport (for Claude Desktop / Inspector)
  # or test visually:
  npx @modelcontextprotocol/inspector python server.py
============================================================================
"""

from mcp.server import MCPServer
from data import (
    FLIGHTS, BAGGAGE_OPTIONS, LOTUSMILES_DISCOUNT, ROUTES, CITY_NAMES,
    flights_for_route, get_flight,
)

mcp = MCPServer(
    "vna-agentic-gateway",
    instructions=(
        "Vietnam Airlines agentic booking gateway. Use these tools to search "
        "flights, illustrate optional personalised offers, and prepare a "
        "direct booking with Vietnam Airlines. Never invent fares. Always hand "
        "off to vietnamairlines.com to complete payment."
    ),
)

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _match(f, origin, destination):
    if origin and f["origin"] != origin.upper():
        return False
    if destination and f["destination"] != destination.upper():
        return False
    return True


def _reasons(f, budget, direct_only, night):
    r = []
    if f["stops"] == 0:
        r.append("direct")
    if budget and f["price_aud"] <= budget:
        under = budget - f["price_aud"]
        r.append(f"A${under} under budget" if under >= 20 else "within budget")
    if night:
        hr = int(f["depart"].split(":")[0])
        if hr >= 20 or hr <= 4:
            r.append("overnight flight")
    return r


# ===========================================================================
# TIER 1 — CORE TOOLS
# ===========================================================================

@mcp.tool(description="Search Vietnam Airlines flights from Australia to Vietnam by route, dates, budget and preferences. Returns ranked flights with reasons.")
def search_flights(
    origin: str | None = None,
    destination: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    passengers: int = 1,
    max_price_aud: float | None = None,
    direct_only: bool = False,
    prefers_night: bool = False,
) -> dict:
    """Return flights matching the criteria, best first. Fixture data only."""
    if origin and destination:
        try:
            pool = flights_for_route(origin, destination, date_from, date_to)
        except ValueError:
            return {"error": "Dates must be YYYY-MM-DD.", "count": 0, "results": []}
    else:
        pool = [f for f in FLIGHTS if _match(f, origin, destination)]
    if direct_only:
        pool = [f for f in pool if f["stops"] == 0]
    if date_from:
        pool = [f for f in pool if f["date"] >= date_from]
    if date_to:
        pool = [f for f in pool if f["date"] <= date_to]

    scored = []
    for f in pool:
        score = 100.0
        if max_price_aud:
            if f["price_aud"] <= max_price_aud:
                score += 20
            else:
                score -= (f["price_aud"] - max_price_aud) / 10
        if f["stops"] == 0:
            score += 10
        if prefers_night:
            hr = int(f["depart"].split(":")[0])
            if hr >= 20 or hr <= 4:
                score += 12
        score += (600 - f["price_aud"]) / 20  # mild cheap-first
        item = dict(f)
        item["reasons"] = _reasons(f, max_price_aud, direct_only, prefers_night)
        item["total_aud_for_party"] = f["price_aud"] * passengers
        item["_score"] = round(score, 1)
        scored.append(item)

    scored.sort(key=lambda x: x["_score"], reverse=True)
    return {
        "query": {"origin": origin, "destination": destination, "date_from": date_from,
                  "date_to": date_to, "passengers": passengers, "max_price_aud": max_price_aud},
        "count": len(scored),
        "results": scored[:6],
        "source": "VNA fixture feed (demo)",
        "disclaimer": "Illustrative fares. Final price and availability confirmed on vietnamairlines.com.",
    }


@mcp.tool(description="Get full fare detail for one flight by its flight id (e.g. VN782).")
def get_fare_details(flight_id: str) -> dict:
    f = get_flight(flight_id)
    if not f:
        return {"error": f"Flight {flight_id} not found in the VNA feed.",
                "hint": "Call search_flights first to get valid flight ids."}
    return {
        "flight": f,
        "fare_breakdown": {
            "base_fare_aud": f["price_aud"],
            "included_baggage_kg": f["baggage_kg"],
            "cabin": f["cabin"],
        },
        "source": "VNA fixture feed (demo)",
    }


@mcp.tool(description="Start a DIRECT booking with Vietnam Airlines. Returns a handoff link to vietnamairlines.com to complete payment. This gateway never charges a card.")
def create_booking_intent(flight_id: str, passengers: int = 1,
                          lotusmiles_tier: str = "none") -> dict:
    f = get_flight(flight_id)
    if not f:
        return {"error": f"Flight {flight_id} not found."}
    rate = LOTUSMILES_DISCOUNT.get(lotusmiles_tier.lower(), 0.0)
    per_person = round(f["price_aud"] * (1 - rate))
    total = per_person * passengers
    return {
        "handoff_status": "prototype_only",
        "flight_id": f["id"],
        "route": f'{f["origin"]}→{f["destination"]}',
        "date": f["date"],
        "passengers": passengers,
        "price_per_person_aud": per_person,
        "total_aud": total,
        "lotusmiles_tier": lotusmiles_tier,
        "handoff_url": "https://www.vietnamairlines.com/au/en/home",
        "note": "Safe prototype link to the official VNA site. Production requires a VNA-issued offer/session token; this gateway never creates a booking, charges a card or touches the booking backend.",
    }


# ===========================================================================
# TIER 2 — DIFFERENTIATOR TOOLS (Lotusmiles + flexible dates)
# ===========================================================================

@mcp.tool(description="Show a prototype personalised-offer scenario for a Lotusmiles tier. Rates are illustrative, not official tier entitlements.")
def get_lotusmiles_price(flight_id: str, lotusmiles_tier: str = "gold") -> dict:
    f = get_flight(flight_id)
    if not f:
        return {"error": f"Flight {flight_id} not found."}
    rate = LOTUSMILES_DISCOUNT.get(lotusmiles_tier.lower())
    if rate is None:
        return {"error": f"Unknown tier '{lotusmiles_tier}'.",
                "valid_tiers": list(LOTUSMILES_DISCOUNT.keys())}
    member = round(f["price_aud"] * (1 - rate))
    return {
        "flight_id": f["id"],
        "standard_price_aud": f["price_aud"],
        "lotusmiles_tier": lotusmiles_tier,
        "member_price_aud": member,
        "you_save_aud": f["price_aud"] - member,
        "note": "Illustrative personalised-offer scenario only; 5–12% is not claimed as an official tier entitlement.",
    }


@mcp.tool(description="For a flexible traveller, find the cheapest nearby dates around a target window on a route. Answers 'which day is cheapest to fly?'.")
def suggest_flexible_dates(origin: str, destination: str,
                           around_date: str, window_days: int = 4) -> dict:
    from datetime import date
    o, d = origin.upper(), destination.upper()
    try:
        y, m, dd = map(int, around_date.split("-"))
        target = date(y, m, dd)
    except Exception:
        return {"error": "around_date must be YYYY-MM-DD."}
    start = (target.fromordinal(target.toordinal() - window_days)).isoformat()
    end = (target.fromordinal(target.toordinal() + window_days)).isoformat()
    options = []
    for f in flights_for_route(o, d, start, end):
        fy, fm, fd = map(int, f["date"].split("-"))
        off = abs((date(fy, fm, fd) - target).days)
        if off <= window_days:
            options.append({"date": f["date"], "flight_id": f["id"],
                            "price_aud": f["price_aud"], "days_off": off,
                            "depart": f["depart"]})
    options.sort(key=lambda x: x["price_aud"])
    if not options:
        return {"route": f"{o}→{d}", "message": "No fixtures in that window.",
                "suggestion": "Widen window_days or try another route."}
    cheapest = options[0]
    return {
        "route": f"{o}→{d}",
        "around": around_date,
        "cheapest": cheapest,
        "all_options": options,
        "insight": f'Flying {cheapest["date"]} ({cheapest["days_off"]} day(s) off) is cheapest at A${cheapest["price_aud"]}.',
    }


# ===========================================================================
# TIER 3 — SUPPLEMENTARY TOOLS
# (working, but keep light; extend if time permits)
# ===========================================================================

@mcp.tool(description="Check seat availability for a flight and party size (demo returns fixture availability).")
def check_availability(flight_id: str, passengers: int = 1) -> dict:
    f = get_flight(flight_id)
    if not f:
        return {"error": f"Flight {flight_id} not found."}
    # demo heuristic: cheaper/popular flights have fewer seats left
    seats_left = 40 if f["price_aud"] > 520 else (12 if f["price_aud"] > 470 else 6)
    return {
        "flight_id": f["id"],
        "seats_left": seats_left,
        "can_seat_party": seats_left >= passengers,
        "note": "Demo availability. Live seat map confirmed on vietnamairlines.com.",
    }


@mcp.tool(description="List extra baggage add-on options and prices for a flight. Useful for VFR travellers carrying gifts home.")
def get_baggage_options(flight_id: str) -> dict:
    f = get_flight(flight_id)
    if not f:
        return {"error": f"Flight {flight_id} not found."}
    return {
        "flight_id": f["id"],
        "included_baggage_kg": f["baggage_kg"],
        "add_ons": BAGGAGE_OPTIONS,
        "note": "Baggage is informational, priced by VNA. Not a competitive claim.",
    }


@mcp.tool(description="Build a family bundle for a group booking: total fare, group baggage suggestion and adjacent-seating note. Designed for multi-passenger VFR trips.")
def compare_family_bundle(flight_id: str, passengers: int = 4,
                          lotusmiles_tier: str = "none") -> dict:
    f = get_flight(flight_id)
    if not f:
        return {"error": f"Flight {flight_id} not found."}
    rate = LOTUSMILES_DISCOUNT.get(lotusmiles_tier.lower(), 0.0)
    per_person = round(f["price_aud"] * (1 - rate))
    fares = per_person * passengers
    bag = BAGGAGE_OPTIONS[-1]  # family +40kg
    return {
        "flight_id": f["id"],
        "passengers": passengers,
        "fare_per_person_aud": per_person,
        "fares_total_aud": fares,
        "suggested_group_baggage": bag,
        "bundle_total_aud": fares + bag["price_aud"],
        "adjacent_seating": "Group seat-together request supported at handoff.",
        "lotusmiles_tier": lotusmiles_tier,
    }


@mcp.tool(description="Get network info for a route: weekly frequency, aircraft, flight time.")
def get_route_info(origin: str, destination: str) -> dict:
    key = (origin.upper(), destination.upper())
    info = ROUTES.get(key)
    if not info:
        return {"error": f"No route {origin}→{destination} in the VNA network feed.",
                "available_routes": [f"{o}→{d}" for (o, d) in ROUTES.keys()]}
    return {
        "route": f"{origin.upper()}→{destination.upper()}",
        "from_city": CITY_NAMES.get(origin.upper()),
        "to_city": CITY_NAMES.get(destination.upper()),
        **info,
    }


@mcp.tool(description="Plan multiple origin groups meeting at one Vietnam destination and check a shared total budget.")
def plan_multi_origin_trip(
    groups: list[dict],
    destination: str,
    date_from: str | None = None,
    date_to: str | None = None,
    total_budget_aud: float | None = None,
    lotusmiles_tier: str = "none",
) -> dict:
    if len(groups) < 1:
        return {"error": "Provide at least one origin group."}
    if len(groups) > 4:
        return {"error": "The demo supports up to four origin groups."}

    # Merge repeated origins so 2×SYD + 2×SYD becomes one 4-passenger group.
    merged: dict[str, int] = {}
    for group in groups:
        origin = str(group.get("origin", "")).upper()
        try:
            passengers = int(group.get("passengers", 0))
        except (TypeError, ValueError):
            passengers = 0
        if not origin or passengers < 1:
            return {"error": f"Invalid passenger group for {origin or 'unknown origin'}."}
        merged[origin] = merged.get(origin, 0) + passengers
    normalised_groups = [
        {"origin": origin, "passengers": passengers}
        for origin, passengers in merged.items()
    ]

    rate = LOTUSMILES_DISCOUNT.get(lotusmiles_tier.lower(), 0.0)
    legs = []
    unavailable_routes = []
    for group in normalised_groups:
        origin = group["origin"]
        passengers = group["passengers"]
        result = search_flights(
            origin=origin,
            destination=destination,
            date_from=date_from,
            date_to=date_to,
            passengers=passengers,
        )
        if not result["results"]:
            unavailable_routes.append({
                "origin": origin,
                "destination": destination.upper(),
                "passengers": passengers,
            })
            continue
        best = result["results"][0]
        per_person = round(best["price_aud"] * (1 - rate))
        legs.append({
            "origin": origin,
            "passengers": passengers,
            "flight_id": best["id"],
            "date": best["date"],
            "price_per_person_aud": per_person,
            "subtotal_aud": per_person * passengers,
        })

    if unavailable_routes:
        return {
            "error": "route_unavailable",
            "message": "At least one requested route is unavailable in the prototype data; no total or budget result was calculated.",
            "unavailable_routes": unavailable_routes,
            "normalised_groups": normalised_groups,
            "grand_total_aud": None,
            "within_budget": None,
            "budget_headroom_aud": None,
            "source": "VNA fixture feed (demo)",
        }

    total = sum(leg["subtotal_aud"] for leg in legs)
    return {
        "destination": destination.upper(),
        "legs": legs,
        "normalised_groups": normalised_groups,
        "total_passengers": sum(leg["passengers"] for leg in legs),
        "grand_total_aud": total,
        "shared_budget_aud": total_budget_aud,
        "within_budget": total <= total_budget_aud if total_budget_aud else None,
        "budget_headroom_aud": total_budget_aud - total if total_budget_aud else None,
        "source": "VNA fixture feed (demo)",
    }


# ===========================================================================
# RESOURCES — read-only context the agent can pull
# ===========================================================================

@mcp.resource("vna://routes", description="Vietnam Airlines Australia–Vietnam route network.")
def routes_resource() -> str:
    lines = ["Prototype Australia to Vietnam route scenarios (verify with authorised VNA schedule):"]
    for (o, d), info in ROUTES.items():
        lines.append(f'  {o}→{d} ({CITY_NAMES[o]}→{CITY_NAMES[d]}): '
                     f'{info["flight_time"]}; {info["weekly_frequency"]}')
    return "\n".join(lines)


@mcp.resource("vna://lotusmiles-benefits", description="Prototype Lotusmiles personalisation scenarios; not official tier entitlements.")
def lotusmiles_resource() -> str:
    lines = ["Illustrative personalised-offer scenarios (not official Lotusmiles tier entitlements):"]
    for tier, rate in LOTUSMILES_DISCOUNT.items():
        if rate > 0:
            lines.append(f"  {tier.title()}: {int(rate*100)}% off base fare")
    return "\n".join(lines)


@mcp.resource("vna://baggage-policy", description="Baggage allowance and add-on options.")
def baggage_resource() -> str:
    lines = ["Vietnam Airlines baggage:", "  Included: 23kg checked (economy).", "  Add-ons:"]
    for b in BAGGAGE_OPTIONS:
        lines.append(f'    {b["label"]}: A${b["price_aud"]}')
    return "\n".join(lines)


# ===========================================================================
if __name__ == "__main__":
    # stdio transport works with Claude Desktop and the MCP Inspector.
    # For a remote/deployed gateway, use: mcp.run(transport="streamable-http")
    mcp.run()
