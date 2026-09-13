# Documentation index

All referenced `docs/` files are present in this package:

- `architecture.svg` — current prototype, future VNA-authorised provider and
  explicit booking/PSS/GDS/payment boundary.
- `wireframe_before_after.svg` — current web search versus SmartSearch.
- `ARCHITECTURE_NOTES.md` — explanation for presenting the diagrams.
- `OPERATING_COSTS.md` — monthly infrastructure estimate, assumptions, sources
  and parameterised break-even calculation.
- `ROUND2_READINESS.md` — mapping to Round 2 deliverables and scoring areas.

## MCP inventory — exactly 10 tools

1. `search_flights`
2. `get_fare_details`
3. `create_booking_intent`
4. `get_lotusmiles_price`
5. `suggest_flexible_dates`
6. `check_availability`
7. `get_baggage_options`
8. `compare_family_bundle`
9. `get_route_info`
10. `plan_multi_origin_trip`

The automated smoke test fails if `mcp_server/server.py` contains anything
other than exactly ten `@mcp.tool` registrations.

