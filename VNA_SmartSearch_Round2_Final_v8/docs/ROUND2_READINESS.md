# Round 2 Readiness — Vietnam Airlines SmartSearch

This checklist maps the current deliverable to the Round 2 requirements in the
UAVS Hackathon 2026 rulebook.

## Required outputs

- **Working product/MVP:** ready in `web/index.html`; one-command launcher is
  `python3 run.py`.
- **Technical documentation:** `README.md`, `HANDOVER.md`, architecture and
  this readiness note are complete.
- **Repository link:** external action still required by the team.
- **Pitch deck:** external submission artifact still required.

## User Experience — 20 points

Evidence currently present:

- Target user: Vietnamese and international travellers in Australia planning a
  trip to Vietnam, especially around Tết.
- Explicit EN/VI interface switch with no mixed static interface.
- Vietnamese input works with or without accents.
- SmartSearch asks only for missing trip information across multiple turns.
- Two simple example prompts guide users without hard-coding a passenger count
  or budget.
- Customer view hides raw MCP/code details.
- Results contain route, date, time, stops, aircraft, fare family, reasons and
  a clear official-channel CTA.
- Responsive layout supports desktop and mobile widths.

Demo proof:

1. Select VI.
2. Enter `toi muon bay tu Sydney ve Ha Noi dip Tet 2027`.
3. Answer `3 nguoi`.
4. Show the summary, results and handoff button.

## Technical Quality — 25 points

Evidence currently present:

- Stable offline demo plus optional API-dependent experiment.
- One-command launcher for macOS, Windows and Python.
- Automated smoke test for structure, Python syntax and all ten MCP tools.
- Web and MCP fail closed when any multi-origin leg is unavailable: no missing
  fare is converted to zero and no partial budget verdict is produced.
- Duplicate origins are merged consistently in both layers; regression tests
  also cover a valid three-origin request.
- Separate UI, recommendation/MCP and fixture-data layers.
- Technical mode reveals tool traces only when requested.
- Architecture explicitly keeps payment, ticketing, PSS and GDS out of scope.
- API keys stay in environment variables and are never placed in browser code.

Do not claim that tool fixtures are a live VNA connection.

## Deployability and Scalability — 20 points

Current approach:

- Static front end can be deployed on a CDN.
- Stateless search/recommendation services can scale horizontally.
- LLM intent parsing is optional; the stable fallback avoids total outage.
- Production data access is represented by a provider boundary, allowing VNA
  to supply an authorised API without redesigning the customer interface.
- Web and Python MCP use the same deterministic Tết 2027 fixture generator;
  production replaces that provider with VNA-authorised offers.
- Payment and personal booking data stay within VNA's approved systems.

Open production dependencies:

- VNA-authorised schedule/fare interface and usage limits.
- Supported offer/quote handoff mechanism and validity window.
- Lotusmiles authentication, consent and permitted profile fields.
- Security, privacy and load testing before production.

## Market and business evidence

The product supports the direct-channel goal by:

- Extending rather than replacing NEO: NEO remains the website assistant,
  while SmartSearch demonstrates complex discovery and an external MCP path.
- Reducing search friction for natural-language and multi-origin requests.
- Making the fare explanation and direct-channel handoff visible.
- Keeping the user on a VNA-branded decision journey rather than introducing
  an OTA.
- Producing measurable funnel events in a future deployment: search started,
  recommendation viewed and official-channel handoff clicked.

Still required:

- Use only verified NEO screenshots and reproduce the exact prompts.
- Infrastructure estimate and parameterised break-even model are documented in
  `docs/OPERATING_COSTS.md`.
- Present benefits as scenarios, not guaranteed revenue.

## Demo claims

Say:

> “This is a working search-layer MVP using illustrative fixtures. With a
> VNA-authorised fare service and offer token, the same interface can hand the
> selected live offer into Vietnam Airlines' booking flow.”

Do not say:

- “These are live VNA prices.”
- “The price is locked.”
- “These seats are available.”
- “This Lotusmiles discount is official.”
- “The booking has been created.”

## Final external checklist

- [ ] Add final NEO evidence.
- [ ] Finalise and export the pitch deck.
- [x] Reconcile cost and impact assumptions with a parameterised break-even model.
- [ ] Push the exact tested files to the submission repository.
- [ ] Deploy or record a backup video.
- [ ] Run `python3 smoke_test.py` immediately before submission.
