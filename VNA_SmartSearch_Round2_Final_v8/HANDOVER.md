# HANDOVER — Vietnam Airlines SmartSearch

## 1. Product position

SmartSearch is a conversational search and recommendation layer for the
Vietnam Airlines Australia digital journey. **It does not replace NEO; it
extends VNA's direct-channel capability** by handling complex trip discovery
and providing an MCP path for external AI assistants. NEO remains the VNA
website assistant; SmartSearch addresses complementary discovery and channel
coverage demonstrated by the multi-origin use case. The prototype does not
control VNA inventory or touch the reservation, payment, PSS or GDS backend.

## 2. Primary demo

Use `web/index.html`, launched with `python3 run.py`. This is the stable
offline MVP and should be used in the pitch.

Current customer-facing capabilities:

- Full-interface English/Vietnamese selector.
- English, accented Vietnamese and unaccented Vietnamese input parsing.
- Multi-turn collection of missing origin, destination, date and passengers.
- Trip summary, ranked prototype results and fare-family explanation.
- Multi-origin/shared-budget planning.
- Fail-closed route handling: if one group has no supported route, no partial
  total or budget verdict is displayed; duplicate origins are merged.
- A **Continue on Vietnam Airlines** button on each result.
- Mobile-responsive layout, loading state and new-search reset.
- Functional chat window controls: red expands; yellow restores after expansion.
- Customer view by default; optional Technical demo reveals MCP traces.

## 3. Claims and boundaries

Always call current data **illustrative prototype data**.

Do not claim that the MVP currently has:

- Live or VNA-authorised fares.
- Verified Lotusmiles discounts or personalised offers.
- Live seat availability.
- A supported price-lock or production booking deep link.
- Payment, reservation or ticket issuance capability.

The future integration path is:

1. VNA-authorised schedule/fare provider returns a time-stamped offer.
2. SmartSearch ranks and explains that offer without changing it.
3. VNA provides an `offer_id`, quote/session token or supported deep link.
4. The user continues on Vietnam Airlines.
5. VNA validates availability and price, then handles payment and ticketing.

Without step 3, a plain website link cannot guarantee the exact same price at
checkout. This is an open integration dependency, not a completed feature.

## 4. Language decision

The explicit **EN | VI** selector sets the whole interface manually. A clearly
English or Vietnamese message automatically synchronises the whole interface
before SmartSearch answers. Ambiguous short follow-ups retain the current
language. The parser independently normalises accents, so Vietnamese without
accents is understood without forcing the user to type correctly.

Switching language resets the conversation so old English and Vietnamese
messages do not remain mixed in one chat.

## 5. Technical demo decision

Raw tool names and JSON are hidden from travellers. Judges can use the
**Customer | Technical / Khách hàng | Kỹ thuật** segmented selector to reveal:

- Tool request and prototype response traces.
- The architecture boundary.
- The future VNA-authorised data and handoff position.

This supports Technical Quality scoring without weakening Customer UX.

## 6. Run and verify

```bash
python3 smoke_test.py
python3 run.py
```

Recommended bilingual test:

1. Select **VI**.
2. Enter `toi muon bay tu Sydney ve Ha Noi dip Tet 2027`.
3. SmartSearch should ask how many people are travelling.
4. Enter `3 nguoi`.
5. Confirm the trip summary, results, prototype disclosure and VNA buttons.
6. Turn on **Chế độ kỹ thuật** and confirm tool traces appear.
7. Select **EN** and confirm the chat resets in English.

Edge-case regression check:

1. Enter `2 from Brisbane and 2 from Perth to Hanoi for Tết 2027 with a shared budget of AUD 4000`.
2. Confirm SmartSearch reports Brisbane→Hanoi unavailable and shows neither a
   combined price nor a within-budget result.
3. Enter two separate Sydney groups and confirm they become one Sydney group
   with the combined passenger count.

## 7. Files and responsibilities

- `web/index.html`: pitch demo and customer experience.
- `web/index-ai.html`: optional API-dependent experiment; not primary.
- `mcp_server/server.py`: ten MCP tools for technical proof.
- `mcp_server/data.py`: shared deterministic Tết 2027 fixture provider.
- `docs/architecture.svg`: architecture and booking-backend boundary.
- `docs/wireframe_before_after.svg`: visual before/after comparison.
- `docs/OPERATING_COSTS.md`: monthly infrastructure estimate and break-even model.
- `docs/ROUND2_READINESS.md`: criteria coverage and remaining work.
- `NEO_comparison.md`: update only after the team supplies reproducible NEO
  screenshots and exact prompts.

## 8. Remaining external actions

- Add verified NEO screenshots and cite the exact test conditions.
- Finalise the pitch deck using the documented, parameterised commercial assumptions.
- Push the final source to a repository accessible to organisers.
- Deploy the stable page to a public URL or record a backup demo video.
- Ask VNA for the authorised data interface and supported offer handoff method.

These are submission, evidence or partner-integration tasks; the stable local
MVP itself is ready for demonstration.
