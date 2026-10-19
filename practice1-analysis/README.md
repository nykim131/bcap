# Practice 1 — Analysis

Your task: turn the raw card-transaction data into the per-merchant metrics a
"merchant detail" page would need.

## The situation

A card company only sees transactions. You are handed two files:

- [`../data/merchants.csv`](../data) — 1,000 merchants:
  `merchant_id, name, raw_category, address, district, latitude, longitude`.
- [`../data/sales_daily.csv`](../data) — 180,000 rows (1,000 merchants × 180 days,
  2026-04-04 → 2026-09-30). Each row is one merchant-day:
  - `merchant_id, date`
  - 24 per-hour transaction counts `00` … `23`
  - 12 customer-segment counts `10_F` … `60_M` (age band × gender)


## What you must produce

`output/practice1_result.csv` — one lean row per `merchant_id` 

example:
- Key metrics — total transactions, active days, active hours (how many of the 24
  hours ever see a transaction), average per active day
- Trend — monthly transaction totals, a growth %, and a label (growing / stable / declining)
- Weekday pattern — each weekday's share of the week's transactions (the 7 sum to ~100%)
- Dayparts — each part of the day's share of transactions (you choose the hour ranges; they sum to ~100%)
- Weekday / weekend / weekday-lunch counts — these feed Practice 2's crowd_type
- Customer pattern — the merchant's main age×gender segment + the full
  distribution (aggregate the per-segment counts across all days)
- Popularity — rank & percentile by transactions within the same district
- Highlights — busiest & quietest day
