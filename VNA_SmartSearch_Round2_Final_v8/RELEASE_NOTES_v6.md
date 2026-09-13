# SmartSearch v6 — Vietnamese multi-origin correction

- Correctly binds each passenger group to its own departure city.
- Supports `2 người từ`, `hai người đi từ`, `hai người bay từ` and Vietnamese
  without accents, while preserving the same English result.
- Prevents the Vietnamese verb `bay` from being mistaken for the number `bảy`.
- Displays the customer-friendly flight number while retaining a unique dated
  fixture ID internally.
- Adds a repeatable JavaScript regression test covering Vietnamese and English.
- Disables local browser caching so Safari/Chrome does not reopen an older page.

Expected result for the main complex prompt:

- Sydney → Hanoi: 2 passengers.
- Melbourne → Hanoi: 2 passengers.
- Combined total: 4 passengers.

