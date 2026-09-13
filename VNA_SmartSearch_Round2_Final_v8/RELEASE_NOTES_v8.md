# SmartSearch v8 — multi-origin safety fix

- Fixed a customer-visible bug where an unavailable route could produce a
  `null` subtotal, be counted as AUD 0 and lead to a false `within_budget=true`
  result.
- Multi-origin planning now fails closed: if any leg is unavailable, both web
  modes and the MCP return the affected route(s), with no grand total, budget
  verdict or headroom calculation.
- Repeated origins are merged before searching and calculating passengers, so
  `2×SYD + 2×SYD` becomes one four-passenger Sydney leg.
- Removed the web planner's numeric fallback that could turn a missing
  subtotal into zero.
- Added regression coverage for BNE→HAN, MEL→DAD, duplicate SYD origins and a
  valid three-origin request.
