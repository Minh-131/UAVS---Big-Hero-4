# VNA SmartSearch — Demo checklist

## Five-minute pre-flight

1. Run `python smoke_test.py` (`py smoke_test.py` on Windows).
2. Run `python run.py` and confirm the browser opens.
3. Keep `index.html` as the primary pitch demo; it needs no API key or network.
4. Test one English request, one Vietnamese-without-accents request, and the multi-origin family example.
5. Keep the VNA Rulebook and NEO screenshots open in separate tabs for judge questions.

## Features ready to demonstrate

- Whole-interface EN/VI selector plus accented/unaccented Vietnamese input.
- Multi-turn questions for missing origin, destination, date and passengers.
- Customer view by default; use the Customer | Technical selector for MCP traces.
- Route, date, passenger and budget extraction.
- Per-person and shared total budgets.
- Multi-origin family trip planning.
- Ranked flight recommendations with reasons.
- Flexible-date suggestion.
- Fare class information and baggage display.
- Lotusmiles-aware demo flow.
- Direct-channel button on each result; payment and ticketing remain outside the prototype.
- MCP technical proof: 10 tools and 3 read-only resources.

## Deliberately deferred

The following will be corrected after VNA confirms data access and integration rules:

- Verified VNA fare snapshots/live fares.
- Verified Lotusmiles benefits or member-specific offers.
- Live seat availability.
- A supported VNA booking deep link or offer/quote handoff.

Do not describe deferred items as live or production-ready during judging.

## Recommended customer demo

1. Select **VI**.
2. Enter `toi muon bay tu Sydney ve Ha Noi dip Tet 2027`.
3. When SmartSearch asks what is missing, enter `3 nguoi`.
4. Show the trip summary, results and **Tiếp tục trên Vietnam Airlines** button.
5. Select **Kỹ thuật** only after the customer journey is clear.

## Optional complex-trip demo

`Two adults from Sydney and two from Melbourne want to meet in Hanoi for Tết 2027, one-way, with a shared budget of AUD 4,000.`

Vietnamese equivalent:

`2 người từ Sydney và 2 người từ Melbourne cùng về Hà Nội dịp Tết 2027, vé một chiều, với ngân sách chung 4000 AUD.`

Then show that SmartSearch keeps the two origins separate, totals the shared budget and explains why each itinerary was selected. Describe all prices as illustrative.
