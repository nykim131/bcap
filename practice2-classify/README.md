# Practice 2 — Classify

Your task: label each merchant. Produce `output/practice2_result.csv` with,
per `merchant_id`:

- `category` — the clean cuisine, one of these 12:
  `Indonesian`, `Korean`, `Japanese`, `Chinese`, `Western`, `Italian`, `Thai`,
  `Fast Food`, `Cafe`, `Dessert`, `Bakery`, `Bar`
- `crowd_type` — `office` / `family` / `evening` / `mixed`
- `tags` — any of `open_24h`, `late_night`, `local_top`, `family_dining`, `group_dinner`


## Inputs

- `merchants.csv` — `name` + the messy `raw_category`.
- `practice1_result.csv` — the file Practice 1 produced (its numeric signals + the age mix).

## What to build

1. cuisine — `raw_category` does not map 1:1 to the 12 categories, so let the
   LLM decide (tool-use with an `enum` so it can't invent a category). This is the
   prompt-engineering part — iterate the prompt.
2. crowd_type — infer from the timing signals and the age mix:
   `office` = weekday-lunch heavy, `family` = weekend heavy, `evening` = evening heavy,
   `mixed` = nothing stands out. Clear cases → a rule; ambiguous ones → the LLM.
3. tags (multi-label):
   - from data (rules) — `open_24h` (active in all 24 hours), `late_night`
     (late-night heavy), `local_top` (#1 by transactions in its district)
   - from judgment (LLM) — `family_dining`, `group_dinner` (which occasions the
     cuisine + crowd fit)
