# Practice 3 — NL Search (API)

Your task: build one API that answers merchant search written in plain
language. The user types *"popular Korean restaurants in Jakarta Selatan"*; you
return a ranked list of merchants.

## The idea

Use the LLM as a parser, not a search engine. It turns the sentence into
structured filters; your Python code does the actual filtering & ranking over
the merchant data. (If the LLM were allowed to "search", it could invent results.)

## Data — load into SQLite, then query with SQL

From here you move from CSVs to a database. Load these into SQLite (you write the
loader), then answer with SQL (`JOIN` / `WHERE` / `ORDER BY`) instead of joining
CSVs in Python:

- `merchants.csv` — identity
- `practice1_result.csv` — Practice 1 output (analytics)
- `practice2_result.csv` — Practice 2 output (category / crowd_type / tags)
- `weather_daily.csv` — used by Practice 4

## Endpoints to build

- `POST /search` `{ "query": "..." }` — the LLM infers `{ categories[], districts[], sort_by }`,
  enum-constrained to the 12 cuisines / 5 districts / `name|popular|trending`; then your
  Python filters & ranks. Return at most 20 results + the parsed filters.
- `GET /merchants?category&district&sort_by&limit` — plain filtered listing.
- `GET /merchants/{id}` — the merchant + its Practice 1 analytics (for a detail page).

Sorting: `popular` = total transactions, `trending` = growth %, `name` = alphabetical.
