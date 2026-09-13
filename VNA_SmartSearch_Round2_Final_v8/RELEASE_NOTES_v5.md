# SmartSearch v5 — completion note

## Completed in this version

- Web and Python MCP share the same deterministic Tết 2027 route/date/price rules.
- Python MCP was installed and tested through a real MCP client: 10 tools listed;
  `search_flights` returned Tết 2027 results successfully.
- Generated flight selections can be passed to fare, Lotusmiles, availability
  and handoff tools.
- Removed fabricated VNA checkout URLs and fake booking references. Prototype
  handoff now links only to the official Vietnam Airlines Australia home page.
- Kept the 5–12% Lotusmiles values only as clearly labelled illustrative
  personalised-offer scenarios; they are not represented as official tier
  discounts.
- Added `docs/OPERATING_COSTS.md` with a monthly cost table, formula, sources
  and parameterised break-even model.
- Added a repeatable evidence protocol to `NEO_comparison.md` for the screenshots
  the team will supply.

## Verified

- Python syntax and project structure: pass.
- Both HTML pages compile as JavaScript: pass.
- Stable web launcher returned HTTP 200: pass.
- Real MCP client: 10 tools, Tết 2027 search and official-site handoff: pass.
- Fake `/checkout?ref=` URLs remaining: none.

## Still external / team-owned

- VNA-authorised data/API and offer-token/deep-link specification.
- Final NEO screenshots from two devices with recorded test conditions.
- Public repository/deployment and final PowerPoint.

