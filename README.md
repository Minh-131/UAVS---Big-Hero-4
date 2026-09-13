# Vietnam Airlines SmartSearch

SmartSearch is a bilingual conversational search companion for the Vietnam
Airlines Australia journey. **It does not replace NEO; it extends VNA's
direct-channel capability** with complex trip discovery and a future MCP path
for external AI assistants. Travellers can describe a trip naturally;
SmartSearch collects missing details, explains illustrative options and hands
the traveller to the official Vietnam Airlines website. It does not process
payment, issue tickets or access a third-party booking backend.

## Run the stable demo

The recommended demo needs only Python 3. It does not need an API key or an
internet connection.

```bash
python3 smoke_test.py
node web_logic_test.js            # optional logic regression test
python3 run.py
```

- macOS: double-click `start_demo.command`.
- Windows: double-click `start_demo.bat`.
- If the browser does not open, visit `http://127.0.0.1:8000/index.html`.
- Press `Control + C` in the terminal to stop the server.

You may also open `web/index.html` directly for a quick offline preview.

## What the customer can do

- Switch the complete interface between **English** and **Tiếng Việt**.
- Write in English, Vietnamese with accents or Vietnamese without accents.
- Start with a short request; SmartSearch asks only for missing origin,
  destination, travel window and passenger count.
- See a clear trip summary before results.
- Compare ranked illustrative options, fare families and an estimated
  all-inclusive price breakdown.
- Plan groups departing from multiple Australian cities on a shared budget.
- Stop safely if any requested leg is unavailable: no partial itinerary, false
  total or budget verdict is shown. Repeated origin cities are combined.
- Continue to the official Vietnam Airlines website from each result.
- Start over at any time with **New search / Tìm chuyến mới**.
- Expand the chat for a focused view, then restore it with the two functional
  window controls in the chat header.

The language selector sets the interface manually. If the customer clearly
writes in the other language, SmartSearch synchronises the complete interface
before answering. Ambiguous short follow-ups keep the current language. Input
parsing is accent-insensitive, so `toi muon bay tu Sydney ve Ha Noi dip Tet
2027` is still understood correctly.

## Customer view and Technical demo

Customer view is the default. It hides MCP names, raw request objects and JSON
responses. This keeps the experience suitable for ordinary travellers.

The **Customer | Technical / Khách hàng | Kỹ thuật** segmented selector reveals the tool traces and
architecture explanation for judges. This proves how the prototype works
without exposing implementation details in the normal customer journey.

Every result shows both the per-traveller amount and the party total. The
transparency panel states that mandatory taxes/charges are included and that
SmartSearch adds no booking or service fee. Because the current data is
illustrative, it does not claim a live or locked VNA price. In production, an
authorised VNA `offer_id` and expiry must be carried to checkout to preserve
the same live total during its validity window.

## Data and booking boundary

The repository currently uses deterministic illustrative fixtures so the MVP
can be demonstrated reliably. The web and Python MCP now use the same route,
date and price-generation rules for Tết 2027. The displayed fare breakdown, Lotusmiles
scenario, seat availability and handoff are not live VNA transactions.

The web and MCP both reject an incomplete multi-origin plan as a whole. A
missing leg is never treated as AUD 0, and repeated origins are merged before
passenger totals are calculated.

In a production integration, the fixture provider would be replaced by a
VNA-authorised schedule/fare service. A VNA-supported deep link, `offer_id` or
quote/session token would be required to carry the selected live offer into
the VNA booking flow. Vietnam Airlines remains responsible for validating the
fare and availability, taking payment and issuing the ticket.

## Project structure

```text
vna-project/
├── run.py                       stable local launcher
├── smoke_test.py                pre-demo validation
├── start_demo.command           macOS launcher
├── start_demo.bat               Windows launcher
├── DEMO_CHECKLIST.md            presentation checklist
├── HANDOVER.md                  status and continuation guide
├── NEO_comparison.md            comparison evidence placeholder
├── web/
│   ├── index.html               primary bilingual customer demo
│   ├── index-ai.html            optional experimental AI mode
│   └── proxy.py                 optional Anthropic proxy
├── mcp_server/
│   ├── server.py                Python MCP server with 10 tools
│   ├── data.py                  illustrative fixtures
│   └── requirements.txt
└── docs/
    ├── architecture.svg
    ├── wireframe_before_after.svg
    ├── OPERATING_COSTS.md
    ├── ARCHITECTURE_NOTES.md
    ├── README.md
    └── ROUND2_READINESS.md
```

## Optional AI mode

The stable demo is recommended for judging. The optional page requires an
Anthropic API key and network access:

```bash
export ANTHROPIC_API_KEY="your-key"
python3 web/proxy.py
```

In another terminal:

```bash
python3 run.py --ai
```

If the optional agent is unavailable, use the stable demo. Never place an API
key inside either HTML file or commit it to the repository.

## Run the Python MCP server

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r mcp_server/requirements.txt
cd mcp_server
python server.py
```

The server uses stdio transport, exposes ten tools and waits silently for an
MCP client. This is expected behaviour. The normal web demo is launched
separately with `python3 run.py`.

## Before submission

Run `python3 smoke_test.py`, follow `DEMO_CHECKLIST.md`, review
`docs/ROUND2_READINESS.md`, then publish the repository and demo link through
the official submission channel.
