# Practice 4 — What-to-eat (API)

Your task: given a user's context (district, meal, date), recommend 3 places
with reasons. This is the "오늘 뭐먹지 / what should I eat today" feature.

## The idea

Your Python code narrows the field to a handful of candidates deterministically;
the LLM only picks 3 of them and explains why, using that day's weather. That
keeps it fast and makes hallucinated merchants impossible.

## Data

Use the same SQLite database as Practice 3 (merchants + Practice 1 output + Practice 2
output + weather). Candidate selection is one SQL query; the day's weather is a lookup.
The weather data runs past the sales window, so "today" / upcoming dates work.

## Endpoint to build

`POST /recommend` `{ "district", "meal": "lunch"|"dinner", "date": "YYYY-MM-DD" }`:

1. Candidates (deterministic, in Python): district match + the merchant actually
   serves that meal (lunch/dinner share ≥ 0.30) → take the top ~30 by popularity.
2. LLM picks 3 from the candidates — enum-bound to the candidate ids so it
   cannot invent a merchant — each with a one-sentence reason that reflects the
   weather & temperature and the merchant's `crowd_type` / `tags`.
3. Prefer variety across the 3 (different categories).
