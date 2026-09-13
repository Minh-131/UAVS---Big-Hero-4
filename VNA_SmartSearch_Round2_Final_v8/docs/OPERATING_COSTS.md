# Infrastructure & Operating Cost — Planning Scenario

## Assumptions

- 50,000 SmartSearch sessions per month.
- Two intent/rewrite LLM calls per session: 100,000 calls per month.
- Average call: 700 input tokens and 250 output tokens.
- Prices are planning estimates in USD, excluding tax and any VNA internal API charge.
- Conversion used only for the pitch budget: **US$1 = A$1.53**. Recheck before submission.

## Monthly estimate

| Cost item | Unit price / basis | Monthly usage | Estimated monthly cost |
|---|---:|---:|---:|
| LLM intent parsing — Claude Sonnet 4.6 | US$3 / 1M input tokens; US$15 / 1M output tokens | 70M input + 25M output tokens | **US$585** |
| Recommendation/API compute | Serverless planning allowance | 100,000 sessions | **US$45** |
| Static web UI/CDN | Free-tier static hosting; allow custom-domain/overage buffer | One production site | **US$10** |
| Monitoring and logs | Planning allowance | One environment | **US$25** |
| Contingency | 15% of the above | Traffic/token variation | **US$100** |
| **Total** |  |  | **US$765 ≈ A$1,170/month** |

The LLM calculation is: `(70M × US$3) + (25M × US$15) = US$585`.
The recommendation engine itself is deterministic and lightweight; LLM cost is
the main variable. Caching common prompts, using the rule-based fallback and
shortening context can lower the realised amount.

## Cost-versus-benefit consistency

Do not claim guaranteed revenue. Use the break-even equation:

`incremental direct bookings needed = A$1,170 / avoided distribution cost per booking`.

| Illustrative avoided distribution cost per shifted booking | Break-even incremental direct bookings/month |
|---:|---:|
| A$15 | 78 |
| A$25 | 47 |
| A$40 | 30 |

These are scenario values, not VNA financial data. Replace them if VNA supplies
an approved distribution-cost assumption.

## Sources and scope

- [Anthropic API pricing](https://claude.com/pricing) — Sonnet 4.6 legacy rate shown as US$3/MTok input and US$15/MTok output when checked 13 September 2026.
- [Cloudflare developer platform](https://www.cloudflare.com/plans/developer-platform/) — free plans are available; the table still includes a small production buffer.
- No OpenAI API is required by the current stable demo. The optional AI page currently targets Anthropic; the provider can be replaced behind the intent-parsing boundary.

