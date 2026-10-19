"""
Generate virtual EatPL training data.

Outputs:
  - merchants.csv       : 1,000 Jakarta merchants (intentionally messy raw_category)
  - sales_daily.csv     : 180,000 rows of per-hour transaction counts (00..23)
                          + per-segment counts (10_F..60_M), no amounts
                          (1,000 merchants x 180 days)
  - weather_daily.csv   : 180 days of Jakarta weather (shared across merchants)

Design notes:
  - Addresses are in Jakarta, text is in English.
  - raw_category is deliberately noisy for Practice 2 (classify).
  - sales_daily has weekday / holiday / weather effects baked in for Practice 1.
  - Determinism: fixed random seed so re-running produces the same CSVs.

Run:
  python3 generate_data.py
"""

import csv
import random
from datetime import date, timedelta
from pathlib import Path

SEED = 42
NUM_MERCHANTS = 1000
NUM_DAYS = 180
END_DATE = date(2026, 9, 30)
START_DATE = END_DATE - timedelta(days=NUM_DAYS - 1)
WEATHER_END = date(2026, 11, 30)   # weather extends past the sales window (today/future)

OUT_DIR = Path(__file__).parent

# ------------------------------------------------------------------
# Taxonomy — the "clean" categories students should land on in P2.
# ------------------------------------------------------------------
CUISINES = [
    "Indonesian", "Korean", "Japanese", "Chinese", "Western",
    "Italian", "Thai", "Fast Food", "Cafe", "Dessert", "Bakery", "Bar",
]

# Weighted so Indonesian / Cafe dominate (realistic for Jakarta).
CUISINE_WEIGHTS = [28, 7, 9, 8, 6, 6, 4, 8, 14, 4, 4, 2]

# Name templates per cuisine. '%s' slots get filled with a token.
NAME_TEMPLATES = {
    "Indonesian": [
        "Nasi Goreng Pak %s", "Warung %s", "Sate Khas %s", "Soto Betawi %s",
        "Bakso %s", "Ayam Geprek %s", "Rendang Rumah %s", "Gado-Gado %s",
    ],
    "Korean": [
        "Seoul BBQ %s", "Oppa Chicken %s", "Kimchi House %s", "Han Kook %s",
        "K-Street %s", "Bulgogi Bros %s",
    ],
    "Japanese": [
        "Tokyo Ramen %s", "Sushi Yama %s", "Sakura %s", "Donburi %s",
        "Udon Ichi %s", "Izakaya %s",
    ],
    "Chinese": [
        "Golden Wok %s", "Dragon Palace %s", "Dim Sum %s", "Mala House %s",
        "Hong Kong %s",
    ],
    "Western": [
        "Big Bob's Grill %s", "Jack's Burger %s", "Smokehouse %s",
        "Steak Factory %s", "The Diner %s",
    ],
    "Italian": [
        "Bella Italia %s", "Pizza Roma %s", "Trattoria %s", "Pasta Bar %s",
        "Dolce %s",
    ],
    "Thai": [
        "Bangkok Kitchen %s", "Thai Spicy %s", "Tom Yum %s", "Pad Thai %s",
    ],
    "Fast Food": [
        "QuickBite %s", "Burger Joint %s", "Chicken Rush %s", "Fry Lab %s",
    ],
    "Cafe": [
        "Daily Coffee %s", "Bean Lab %s", "Espresso House %s", "Kopi %s",
        "Morning Brew %s", "Latte Art %s",
    ],
    "Dessert": [
        "Sweet Dreams %s", "Ice Cream Castle %s", "Bingsu %s", "Churros %s",
    ],
    "Bakery": [
        "Baker's Daily %s", "Fresh Bread %s", "Pastry Lab %s", "Croissant %s",
    ],
    "Bar": [
        "The Wine Cellar %s", "Craft Beer %s", "Rooftop Lounge %s",
    ],
}

# Second-token pool to give each merchant a unique-looking name.
NAME_TOKENS = [
    "Sudirman", "Menteng", "Kemang", "Senayan", "Thamrin", "PIK", "Kelapa Gading",
    "Blok M", "Pondok Indah", "Cilandak", "Kuningan", "Cikini", "Fatmawati",
    "Grogol", "Pluit", "Kebayoran", "Tebet", "Pasar Minggu", "Pancoran", "Tanah Abang",
    "Setiabudi", "Mampang", "Senopati", "Bendungan Hilir", "Cideng",
    "Ancol", "Rawamangun", "Cempaka Putih", "Matraman", "Salemba",
    "Melawai", "Dharmawangsa", "Antasari", "Pondok Labu", "Lebak Bulus",
    "Jatinegara", "Cawang", "Pulogadung", "Kemayoran",
]

# ------------------------------------------------------------------
# Raw category values for Practice 2.
#
# Design goal: these look like real-world business classifications — not
# intentionally mangled strings. Each clean cuisine has a mix of:
#   - direct labels         ("Korean", "Pizzeria")
#   - menu-type hints       ("Nasi & Mie", "Coffee & Pastry")
#   - broader umbrellas     ("Southeast Asian", "European")
#   - genuinely ambiguous   ("Dessert Cafe", "Burger & Fries")
#   - None / blank
# The point is NOT noise. The point is: the LLM must pick the closest of
# the 12 target categories using judgment, because no rule maps 1:1.
# ------------------------------------------------------------------
RAW_CATEGORY_VARIANTS = {
    "Indonesian": [
        "Indonesian", "Indonesian Restaurant", "Warung Makan",
        "Nasi & Mie", "Local Cuisine", "Southeast Asian",
        "Traditional Indonesian", "Rumah Makan", None,
    ],
    "Korean": [
        "Korean", "Korean Restaurant", "Korean BBQ",
        "Korean Grill", "K-Food", "Grill House", None,
    ],
    "Japanese": [
        "Japanese", "Japanese Restaurant", "Sushi Bar",
        "Ramen Shop", "Izakaya", "Japanese Cuisine", None,
    ],
    "Chinese": [
        "Chinese", "Chinese Restaurant", "Dim Sum House",
        "Hong Kong Style", "Chinese Cuisine", "Noodle House", None,
    ],
    "Western": [
        "Western", "Steakhouse", "American Diner",
        "Grill House", "Western Cuisine", "European", None,
    ],
    "Italian": [
        "Italian", "Italian Restaurant", "Pizzeria",
        "Pasta Bar", "Trattoria", "European", None,
    ],
    "Thai": [
        "Thai", "Thai Restaurant", "Southeast Asian",
        "Thai Cuisine", None,
    ],
    "Fast Food": [
        "Fast Food", "Quick Service", "Burger & Fries",
        "Fried Chicken", "QSR", None,
    ],
    "Cafe": [
        "Cafe", "Coffee Shop", "Coffee & Tea",
        "Coffee & Pastry", "Specialty Coffee", None,
    ],
    "Dessert": [
        "Dessert", "Dessert Shop", "Dessert Cafe",
        "Ice Cream", "Sweet Shop", None,
    ],
    "Bakery": [
        "Bakery", "Bread Shop", "Pastry Shop",
        "Boulangerie", "Patisserie", None,
    ],
    "Bar": [
        "Bar", "Pub", "Lounge", "Wine Bar", "Cocktail Bar", None,
    ],
}

# ------------------------------------------------------------------
# Jakarta districts with rough centroid + weekday vs weekend profile.
# office_ratio = how office-heavy the area is -> lunch spike on weekdays.
# ------------------------------------------------------------------
DISTRICTS = {
    "Jakarta Pusat":   {"lat": -6.1865, "lng": 106.8343, "office_ratio": 0.75, "weight": 25},
    "Jakarta Selatan": {"lat": -6.2615, "lng": 106.8106, "office_ratio": 0.50, "weight": 30},
    "Jakarta Utara":   {"lat": -6.1388, "lng": 106.8639, "office_ratio": 0.40, "weight": 15},
    "Jakarta Barat":   {"lat": -6.1683, "lng": 106.7588, "office_ratio": 0.45, "weight": 15},
    "Jakarta Timur":   {"lat": -6.2250, "lng": 106.9004, "office_ratio": 0.35, "weight": 15},
}

# Streets are grouped by the district they actually belong to, so the street
# in an address is consistent with the merchant's district (no more "Jakarta
# Timur" merchants sitting on "Jl. Pluit Raya", which is really in the north).
DISTRICT_STREETS = {
    "Jakarta Pusat": [
        "Jl. Sudirman", "Jl. Thamrin", "Jl. Gajah Mada",
        "Jl. Hayam Wuruk", "Jl. Kebon Sirih", "Jl. Menteng Raya",
    ],
    "Jakarta Selatan": [
        "Jl. Rasuna Said", "Jl. Gatot Subroto", "Jl. Kemang Raya",
        "Jl. Senopati", "Jl. Melawai", "Jl. Fatmawati",
        "Jl. Cilandak", "Jl. Pondok Indah", "Jl. Casablanca",
    ],
    "Jakarta Utara": [
        "Jl. Pluit Raya", "Jl. Boulevard Kelapa Gading",
        "Jl. Pantai Indah Kapuk", "Jl. Yos Sudarso", "Jl. Danau Sunter Utara",
    ],
    "Jakarta Barat": [
        "Jl. Daan Mogot", "Jl. Panjang", "Jl. Kyai Tapa",
        "Jl. Puri Indah", "Jl. Letjen S. Parman",
    ],
    "Jakarta Timur": [
        "Jl. Pemuda", "Jl. Raya Bogor", "Jl. Matraman Raya",
        "Jl. Pramuka", "Jl. DI Panjaitan",
    ],
}

# ------------------------------------------------------------------
# Price tier -> avg ticket (IDR) and daily transaction range.
# ------------------------------------------------------------------
PRICE_TIERS = {
    "$":    {"avg_ticket": 25_000,  "tx_range": (60, 220)},
    "$$":   {"avg_ticket": 60_000,  "tx_range": (40, 180)},
    "$$$":  {"avg_ticket": 140_000, "tx_range": (25, 110)},
    "$$$$": {"avg_ticket": 300_000, "tx_range": (10, 60)},
}
PRICE_WEIGHTS = {"$": 35, "$$": 40, "$$$": 18, "$$$$": 7}

# Public holidays within the data window (approx).
HOLIDAYS = {
    date(2026, 4, 10),   # Idul Fitri (approx)
    date(2026, 4, 11),
    date(2026, 5, 1),    # Labour Day
    date(2026, 6, 1),    # Pancasila Day
    date(2026, 6, 17),   # Idul Adha
    date(2026, 7, 7),    # Islamic New Year
    date(2026, 8, 17),   # Independence Day
    date(2026, 9, 15),   # Prophet's Birthday
}


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------
def weighted_choice(rng, items, weights):
    return rng.choices(items, weights=weights, k=1)[0]


def jitter_coord(rng, base_lat, base_lng):
    # +/- ~0.03 deg ≈ 3 km in Jakarta.
    return (
        round(base_lat + rng.uniform(-0.03, 0.03), 6),
        round(base_lng + rng.uniform(-0.03, 0.03), 6),
    )


def generate_merchants(rng):
    merchants = []
    district_names = list(DISTRICTS.keys())
    district_weights = [DISTRICTS[d]["weight"] for d in district_names]

    for i in range(1, NUM_MERCHANTS + 1):
        merchant_id = f"MER-{i:05d}"
        cuisine = weighted_choice(rng, CUISINES, CUISINE_WEIGHTS)
        name_template = rng.choice(NAME_TEMPLATES[cuisine])
        name = name_template % rng.choice(NAME_TOKENS)

        district = weighted_choice(rng, district_names, district_weights)
        d = DISTRICTS[district]
        lat, lng = jitter_coord(rng, d["lat"], d["lng"])
        street = rng.choice(DISTRICT_STREETS[district])
        house_no = rng.randint(1, 250)
        address = f"{street} No.{house_no}, {district}"

        # price_tier is kept INTERNAL only — it drives tx volume + avg_ticket
        # in the sales generator so the data has realistic variance, but it is
        # NOT written to merchants.csv (a card company wouldn't know this up
        # front; downstream analysis can infer avg_ticket from transactions).
        price_tier = weighted_choice(rng, list(PRICE_WEIGHTS), list(PRICE_WEIGHTS.values()))

        raw_category = rng.choice(RAW_CATEGORY_VARIANTS[cuisine])

        # Trend tag drives the sales growth curve for P1 insights (internal only).
        trend = rng.choices(
            ["growing", "stable", "declining"],
            weights=[25, 55, 20],
            k=1,
        )[0]

        # Some merchants run 24 hours (realistically fast food / cafes / warungs).
        # Internal only — detected downstream from the hourly data, not a column.
        is_24h = rng.random() < TWENTYFOUR_H_PROB.get(cuisine, 0.0)

        merchants.append({
            "merchant_id": merchant_id,
            "name": name,
            "raw_category": raw_category if raw_category is not None else "",
            "address": address,
            "district": district,
            "latitude": lat,
            "longitude": lng,
            # internal only — not written to CSV
            "_true_cuisine": cuisine,
            "_trend": trend,
            "_price_tier": price_tier,
            "_is_24h": is_24h,
        })
    return merchants


def _weather_row(rng, d):
    """One day of Jakarta weather. Nov-Mar is rainy season, Apr-Oct is dry (roughly)."""
    month = d.month
    if month in (11, 12, 1, 2, 3):
        rain_prob = 0.55
        temp_c = round(rng.uniform(24, 30), 1)
    else:
        rain_prob = 0.20
        temp_c = round(rng.uniform(26, 33), 1)
    is_rainy = rng.random() < rain_prob
    condition = rng.choice(["heavy_rain", "rain", "thunderstorm"]) if is_rainy else \
                rng.choice(["sunny", "partly_cloudy", "cloudy"])
    return {
        "date": d.isoformat(),
        "condition": condition,
        "temp_c": temp_c,
        "is_rainy": int(is_rainy),
    }


def generate_weather(rng):
    """Daily weather over the 180-day sales window."""
    return [_weather_row(rng, START_DATE + timedelta(days=i)) for i in range(NUM_DAYS)]


def generate_extra_weather(rng):
    """Weather for the dates AFTER the sales window (through WEATHER_END), so the
    'what to eat today' feature works for current / future dates too. Generated
    after the sales rows so it doesn't shift the historical data's random stream.
    These days carry the same kind of weather as any other — no special flag."""
    rows = []
    d = END_DATE + timedelta(days=1)
    while d <= WEATHER_END:
        rows.append(_weather_row(rng, d))
        d += timedelta(days=1)
    return rows


# ------------------------------------------------------------------
# Hourly transaction profiles (relative weights per hour 0..23).
#
# The raw card data is per-hour transaction COUNTS — no amounts. Each cuisine
# has a characteristic shape over the day; "_RESTAURANT" is the default
# lunch+dinner curve used by the sit-down cuisines.
# ------------------------------------------------------------------
FAMILY_CUISINES = {"Italian", "Western", "Dessert", "Bakery", "Fast Food"}

_RESTAURANT = [0, 0, 0, 0, 0, 0, 0.1, 0.2, 0.3, 0.4, 0.6,
               1.5, 3.0, 2.0, 0.8, 0.5, 0.6, 1.2, 2.8, 3.0, 2.0, 1.0, 0.4, 0.2]
HOUR_PROFILES = {
    # Korean (BBQ) and Japanese (izakaya/sushi) are dinner-driven — modest
    # lunch, heavy evening. This is what makes them read as "evening" crowds.
    "Korean":    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.3,
                  1.0, 2.0, 1.3, 0.6, 0.4, 0.6, 1.6, 3.2, 3.5, 2.8, 1.8, 0.9, 0.4],
    "Japanese":  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.4,
                  1.2, 2.2, 1.5, 0.7, 0.5, 0.7, 1.5, 3.0, 3.3, 2.6, 1.6, 0.8, 0.3],
    "Cafe":      [0, 0, 0, 0, 0, 0, 0.3, 1.0, 1.6, 1.6, 1.6,
                  1.6, 2.0, 1.8, 1.5, 1.8, 1.8, 1.6, 1.4, 1.2, 1.0, 0.6, 0.3, 0],
    "Bakery":    [0, 0, 0, 0, 0, 0, 1.0, 2.2, 2.6, 2.2, 1.6,
                  1.4, 1.5, 1.1, 0.9, 0.9, 0.9, 1.0, 0.9, 0.6, 0.4, 0.2, 0, 0],
    "Dessert":   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                  0.4, 0.8, 1.0, 1.6, 2.2, 2.2, 1.8, 1.6, 2.0, 2.0, 1.2, 0.6, 0.2],
    "Fast Food": [0.2, 0.1, 0, 0, 0, 0, 0.2, 0.5, 0.8, 0.6, 0.8,
                  1.6, 3.0, 2.2, 1.2, 0.9, 0.9, 1.4, 2.6, 2.6, 1.8, 1.2, 0.8, 0.4],
    "Bar":       [0.8, 0.4, 0.1, 0, 0, 0, 0, 0, 0, 0, 0,
                  0, 0, 0, 0, 0, 0.3, 0.8, 1.6, 2.8, 3.0, 2.8, 2.2, 1.6],
}

# 24-hour operators (some fast food / cafes / warungs). Activity never drops to
# zero — low overnight, normal daytime peaks. Which merchants get this is decided
# internally in generate_merchants (`_is_24h`) and is NOT written to the CSV; the
# analyze/classify steps detect them purely from the data (all 24 hours > 0).
TWENTYFOUR_H_PROB = {"Fast Food": 0.35, "Cafe": 0.12, "Indonesian": 0.08}
_TWENTYFOUR = [0.4, 0.3, 0.25, 0.2, 0.25, 0.4, 0.8, 1.2, 1.3, 1.1, 1.0,
               1.6, 2.4, 1.8, 1.2, 1.0, 1.1, 1.4, 2.0, 2.0, 1.6, 1.2, 0.9, 0.6]


def distribute_hourly(rng, tx, cuisine, office_ratio, dow, is_24h=False):
    """Split a day's `tx` transactions into 24 integer per-hour counts that
    sum exactly to `tx`, following the merchant's hourly profile."""
    if is_24h:
        # Round-the-clock: every hour stays non-zero.
        weights = list(_TWENTYFOUR)
    else:
        weights = list(HOUR_PROFILES.get(cuisine, _RESTAURANT))
        is_weekend = dow >= 5
        # Office areas get a strong weekday lunch surge — but only the balanced
        # sit-down cuisines (not family-leaning ones, not the dinner/all-day
        # types that have their own profile).
        if (cuisine not in HOUR_PROFILES and cuisine not in FAMILY_CUISINES
                and office_ratio > 0.5 and not is_weekend):
            for h in (11, 12, 13):
                weights[h] *= 2.4
        # Family cuisines skew to dinner on weekends.
        if cuisine in FAMILY_CUISINES and is_weekend:
            for h in (18, 19, 20):
                weights[h] *= 1.4

    # Per-hour jitter so days aren't identically shaped.
    jittered = [w * rng.uniform(0.85, 1.15) if w > 0 else 0.0 for w in weights]
    total_w = sum(jittered)
    if total_w <= 0:
        jittered = [1.0] * 24
        total_w = 24.0

    raw = [tx * j / total_w for j in jittered]
    counts = [int(x) for x in raw]
    # Largest-remainder: hand out the leftover so counts sum to tx exactly.
    leftover = tx - sum(counts)
    order = sorted(range(24), key=lambda h: raw[h] - counts[h], reverse=True)
    for i in range(leftover):
        counts[order[i]] += 1
    return counts


# ------------------------------------------------------------------
# Customer demographic segments (6 age bands x 2 genders = 12).
#
# A card company DOES know its cardholders' age/gender, but our synthetic raw
# data isn't modelled at transaction level — so we bake a per-day breakdown of
# transactions by segment straight into sales_daily.csv. It wobbles day to day
# (jitter); the analyze step averages it to find each merchant's main customer
# segment. "10" = ages 10-19 ... "60" = 60 and over.
# ------------------------------------------------------------------
CUSTOMER_SEGMENTS = [
    "10_F", "10_M", "20_F", "20_M", "30_F", "30_M",
    "40_F", "40_M", "50_F", "50_M", "60_F", "60_M",
]

_DEMO_DEFAULT = [0.5, 0.5, 1.2, 1.2, 1.5, 1.5, 1.3, 1.3, 0.9, 0.9, 0.6, 0.6]

# Relative weight per segment, by cuisine (same order as CUSTOMER_SEGMENTS).
DEMO_PROFILES = {
    "Bar":        [0.0, 0.0, 1.8, 2.2, 1.8, 2.4, 0.9, 1.1, 0.3, 0.4, 0.1, 0.1],
    "Cafe":       [1.0, 0.5, 3.0, 1.5, 2.5, 1.3, 1.2, 0.7, 0.5, 0.3, 0.2, 0.1],
    "Dessert":    [2.2, 1.2, 3.0, 1.4, 1.6, 0.8, 0.9, 0.5, 0.4, 0.2, 0.2, 0.1],
    "Bakery":     [1.0, 0.6, 1.8, 1.0, 2.4, 1.2, 2.0, 1.0, 1.0, 0.6, 0.6, 0.4],
    "Fast Food":  [2.2, 2.5, 2.0, 2.2, 1.3, 1.4, 0.9, 1.0, 0.4, 0.5, 0.2, 0.3],
    "Korean":     [0.8, 0.7, 2.5, 2.2, 2.2, 2.0, 1.2, 1.1, 0.5, 0.5, 0.2, 0.2],
    "Japanese":   [0.6, 0.6, 2.0, 2.0, 2.2, 2.2, 1.5, 1.5, 0.7, 0.7, 0.3, 0.3],
    "Italian":    [0.9, 0.6, 2.6, 1.6, 2.4, 1.8, 1.3, 1.0, 0.6, 0.5, 0.3, 0.2],
    "Western":    [0.6, 0.6, 1.6, 1.6, 2.0, 2.0, 1.8, 1.8, 1.0, 1.0, 0.5, 0.5],
    "Indonesian": [0.8, 0.9, 1.5, 1.6, 1.6, 1.7, 1.5, 1.6, 1.1, 1.2, 0.8, 0.9],
    "Chinese":    [0.6, 0.7, 1.2, 1.3, 1.6, 1.7, 1.8, 1.9, 1.3, 1.4, 0.9, 1.0],
    "Thai":       [0.9, 0.7, 2.4, 1.8, 2.0, 1.6, 1.1, 0.9, 0.5, 0.4, 0.2, 0.2],
}


def merchant_demo_weights(rng, cuisine, office_ratio):
    """Per-merchant segment weighting, kept **coherent with the merchant's crowd
    nature** so demographics reinforce crowd_type (office = working age, family =
    multi-generational, evening = adults) rather than being random noise. Adds
    per-merchant jitter so merchants of the same cuisine still vary.
    """
    base = list(DEMO_PROFILES.get(cuisine, _DEMO_DEFAULT))
    # Age-band index groups (CUSTOMER_SEGMENTS order).
    adults_20_40 = [2, 3, 4, 5, 6, 7]              # 20s + 30s + 40s
    family_spread = [0, 1, 6, 7, 8, 9, 10, 11]     # 10s (kids) + 40/50/60s
    if cuisine in FAMILY_CUISINES:
        for i in family_spread:
            base[i] *= 1.5
    elif cuisine in {"Bar", "Korean", "Japanese"}:
        for i in adults_20_40:
            base[i] *= 1.4
    elif office_ratio > 0.5:
        for i in adults_20_40:
            base[i] *= 1.5
    return [w * rng.uniform(0.6, 1.4) for w in base]


def distribute_demographic(rng, tx, weights):
    """Split a day's `tx` transactions across the 12 customer segments, summing
    exactly to `tx`. `weights` is the merchant's own segment weighting; per-day
    jitter makes the mix wobble day to day."""
    jittered = [w * rng.uniform(0.80, 1.20) if w > 0 else 0.0 for w in weights]
    total_w = sum(jittered)
    if total_w <= 0:
        jittered = [1.0] * 12
        total_w = 12.0
    raw = [tx * j / total_w for j in jittered]
    counts = [int(x) for x in raw]
    leftover = tx - sum(counts)
    order = sorted(range(12), key=lambda i: raw[i] - counts[i], reverse=True)
    for i in range(leftover):
        counts[order[i]] += 1
    return counts


def daily_sales_for_merchant(rng, merchant, weather_by_date):
    """Produce 180 daily rows for a single merchant with realistic patterns."""
    tier = PRICE_TIERS[merchant["_price_tier"]]
    tx_lo, tx_hi = tier["tx_range"]
    base_tx = rng.randint(tx_lo, tx_hi)   # merchant's own daily baseline volume
    office_ratio = DISTRICTS[merchant["district"]]["office_ratio"]
    cuisine = merchant["_true_cuisine"]
    trend = merchant["_trend"]
    is_24h = merchant["_is_24h"]
    demo_weights = merchant_demo_weights(rng, cuisine, office_ratio)

    rows = []
    for i in range(NUM_DAYS):
        d = START_DATE + timedelta(days=i)
        weather = weather_by_date[d.isoformat()]
        dow = d.weekday()  # Mon=0 .. Sun=6

        # Trend factor across the 180-day window.
        progress = i / max(NUM_DAYS - 1, 1)
        if trend == "growing":
            trend_mult = 0.85 + 0.35 * progress        # 0.85 -> 1.20
        elif trend == "declining":
            trend_mult = 1.15 - 0.35 * progress        # 1.15 -> 0.80
        else:
            trend_mult = 1.0 + rng.uniform(-0.05, 0.05)

        # Weekday pattern — Fri/Sat spike, Mon dip.
        weekday_mult = {0: 0.85, 1: 0.90, 2: 0.95, 3: 1.00, 4: 1.20, 5: 1.30, 6: 1.10}[dow]

        # Weekend behavior depends on the neighborhood AND cuisine:
        # - Family cuisines (Italian/Western/Dessert/Bakery/Fast Food) draw a
        #   strong weekend crowd everywhere.
        # - Office-heavy areas dip on weekends for everything else.
        # - Residential non-family stays near its natural weekend level.
        if dow >= 5:
            if cuisine in FAMILY_CUISINES:
                weekday_mult *= 1.60          # family cuisines: strong weekend draw everywhere
            elif office_ratio > 0.5:
                weekday_mult *= 0.55          # office-area non-family: weekend dip
            # residential non-family: weekend stays near its natural level

        # Holiday effect.
        is_holiday = d in HOLIDAYS
        if is_holiday:
            if cuisine in ("Bakery", "Cafe", "Dessert"):
                holiday_mult = 1.15
            elif cuisine in ("Western", "Italian", "Japanese", "Korean"):
                holiday_mult = 1.35
            else:
                holiday_mult = 1.20
        else:
            holiday_mult = 1.0

        # Weather effect.
        if weather["is_rainy"]:
            if cuisine in ("Indonesian", "Chinese", "Thai"):   # warm soup / rice
                weather_mult = 1.15
            elif cuisine in ("Cafe", "Bakery"):
                weather_mult = 1.10
            elif cuisine in ("Dessert", "Fast Food"):
                weather_mult = 0.80
            else:
                weather_mult = 0.95
        else:
            weather_mult = 1.0

        noise = rng.uniform(0.90, 1.10)

        tx = int(base_tx * trend_mult * weekday_mult * holiday_mult * weather_mult * noise)
        tx = max(tx, 1)

        # Two breakdowns of the same daily total, both summing to `tx`:
        #  - by hour (00..23): the cuisine's hourly profile + office/family tilt
        #  - by customer segment (10_F..60_M): the cuisine's demographic profile
        # No amount, no stored daily total — everything derivable (daily total,
        # dayparts, day-of-week, main customer segment) is produced later in the
        # analyze step (Practice 1).
        hourly = distribute_hourly(rng, tx, cuisine, office_ratio, dow, is_24h)
        demo = distribute_demographic(rng, tx, demo_weights)

        row = {"merchant_id": merchant["merchant_id"], "date": d.isoformat()}
        for h in range(24):
            row[f"{h:02d}"] = hourly[h]
        for idx, seg in enumerate(CUSTOMER_SEGMENTS):
            row[seg] = demo[idx]
        rows.append(row)
    return rows


def write_csv(path, rows, columns):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=columns)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in columns})


def main():
    rng = random.Random(SEED)

    print(f"Generating {NUM_MERCHANTS} merchants ...")
    merchants = generate_merchants(rng)

    print(f"Generating {NUM_DAYS} days of weather ...")
    weather = generate_weather(rng)
    weather_by_date = {w["date"]: w for w in weather}

    print(f"Generating {NUM_MERCHANTS * NUM_DAYS:,} daily sales rows ...")
    sales_rows = []
    for m in merchants:
        sales_rows.extend(daily_sales_for_merchant(rng, m, weather_by_date))

    # Append weather for dates past the sales window (Oct–Nov) AFTER sales so the
    # historical data's random stream — and thus sales_daily.csv — is unchanged.
    weather += generate_extra_weather(rng)

    # Public merchants.csv — only what a card company actually has from
    # merchant registration. No price_tier (derive from avg_ticket), no
    # rating/review (that's review-site data), no seats/opening-hours.
    merchant_cols = [
        "merchant_id", "name", "raw_category", "address", "district",
        "latitude", "longitude",
    ]
    write_csv(OUT_DIR / "merchants.csv", merchants, merchant_cols)

    weather_cols = ["date", "condition", "temp_c", "is_rainy"]
    write_csv(OUT_DIR / "weather_daily.csv", weather, weather_cols)

    # Raw card data: per-hour transaction counts (00..23) + per-segment counts
    # (10_F..60_M). Daily total, dayparts, day-of-week and the main customer
    # segment are all derivable and are produced in the analyze step.
    sales_cols = (["merchant_id", "date"]
                  + [f"{h:02d}" for h in range(24)]
                  + CUSTOMER_SEGMENTS)
    write_csv(OUT_DIR / "sales_daily.csv", sales_rows, sales_cols)

    print("Done.")
    print(f"  merchants.csv       -> {len(merchants):,} rows")
    print(f"  weather_daily.csv   -> {len(weather):,} rows")
    print(f"  sales_daily.csv     -> {len(sales_rows):,} rows")


if __name__ == "__main__":
    main()
