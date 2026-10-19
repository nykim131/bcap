# EatPL Indonesia — Training Practices

A hands-on course for building an Indonesian-flavored EatPL. Students build the full stack from raw data to an LLM-powered recommendation API in 4 practices.


## Data (shared across all practices)

Everything lives in [`data/`](./data). `generate_data.py` is deterministic (seed = 42) so students can re-run it anytime.

| file | rows | what it is |
|---|---|---|
| `merchants.csv` | 1,000 | Jakarta merchants with messy `raw_category` — Practice 2 cleans this. |
| `sales_daily.csv` | 180,000 | One row per merchant-day (180 days). Per-hour transaction counts (`00`–`23`) + per-segment counts (`10_F`–`60_M`, age × gender). No amounts; day-of-week / dayparts / totals are derived in Practice 1. |
| `weather_daily.csv` | 241 | Daily Jakarta weather through 2026-11-30 (past the sales window, so "today" works). Practice 4 joins against this. |

Regenerate at any time:

```bash
cd data
python3 generate_data.py
```

## Target taxonomy (12 cuisines, fixed)

```
Indonesian  Korean  Japanese  Chinese  Western  Italian
Thai        Fast Food  Cafe   Dessert  Bakery   Bar
```

5 Jakarta districts: `Jakarta Pusat`, `Jakarta Selatan`, `Jakarta Utara`, `Jakarta Barat`, `Jakarta Timur`.


## The 4 practices

| # | folder | theme | you build |
|---|---|---|---|
| 1 | [`practice1-analysis`](./practice1-analysis) | Analysis | Aggregated metrics for a merchant detail page. |
| 2 | [`practice2-classify`](./practice2-classify) | Classify | Per merchant: a clean `category` (LLM into 1 of 12 — prompt engineering), a `crowd_type` (rules on timing + age, LLM for the ambiguous ones), and `tags`. Deciding what's a rule vs the LLM is part of the task. |
| 3 | [`practice3-nl-search`](./practice3-nl-search) | NL Search | An API that answers "Find Korean restaurants in Jakarta Pusat" via LLM + structured search. LLM parses NL query → structured filters (categories, districts, sort_by). Python does the search.|
| 4 | [`practice4-what-to-eat`](./practice4-what-to-eat) | What-to-eat | A weather-aware "pick my lunch" API, LLM-driven. Python picks ~30 candidates. LLM picks 3 of them with reasons.|


## Suggested timeline (per 1-day session)

| time | block |
|---|---|
| 09:30 – 10:30 | Orientation + walk through the data. |
| 10:30 – 12:00 | Practice 1 — Analysis. |
| 13:00 – 14:30 | Practice 2 — Classify. |
| 14:30 – 16:00 | Practice 3 — NL Search (LLM). |
| 16:00 – 17:30 | Practice 4 — What-to-eat (LLM + weather). |
| 17:30 – 18:00 | Share and critique each team's results. |

