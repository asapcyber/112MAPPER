# seed_groningen_city_safety.py
import sqlite3
import random
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "city-safety.db"

random.seed(1122025)

# --- Neighbourhoods (synthetic lat/lon + base risk) ---
# lat/lon roughly around Groningen; adjust to match your map centering if needed
NEIGHBORHOODS = {
    "Binnenstad":        {"lat": 53.2194, "lon": 6.5665, "base_risk": 0.85},
    "Oosterpoort":       {"lat": 53.2130, "lon": 6.5770, "base_risk": 0.75},
    "Oosterparkwijk":    {"lat": 53.2250, "lon": 6.5860, "base_risk": 0.80},
    "Korrewegwijk":      {"lat": 53.2330, "lon": 6.5710, "base_risk": 0.78},
    "De Hoogte":         {"lat": 53.2350, "lon": 6.5660, "base_risk": 0.70},
    "Selwerd":           {"lat": 53.2365, "lon": 6.5530, "base_risk": 0.68},
    "Paddepoel":         {"lat": 53.2400, "lon": 6.5400, "base_risk": 0.65},
    "Vinkhuizen":        {"lat": 53.2275, "lon": 6.5250, "base_risk": 0.60},
    "Hoogkerk":          {"lat": 53.2120, "lon": 6.4950, "base_risk": 0.55},
    "Reitdiep":          {"lat": 53.2340, "lon": 6.5280, "base_risk": 0.50},
    "Beijum":            {"lat": 53.2500, "lon": 6.6000, "base_risk": 0.72},
    "Lewenborg":         {"lat": 53.2400, "lon": 6.6350, "base_risk": 0.70},
    "De Hunze":          {"lat": 53.2390, "lon": 6.6080, "base_risk": 0.60},
    "Ulgersmaborg":      {"lat": 53.2360, "lon": 6.6200, "base_risk": 0.62},
    "Oosterhoogebrug":   {"lat": 53.2310, "lon": 6.6160, "base_risk": 0.58},
    "Helpman":           {"lat": 53.2050, "lon": 6.5750, "base_risk": 0.66},
    "Coendersborg":      {"lat": 53.2040, "lon": 6.5900, "base_risk": 0.60},
    "Hoornsemeer":       {"lat": 53.1970, "lon": 6.5600, "base_risk": 0.55},
    "Corpus den Hoorn":  {"lat": 53.2030, "lon": 6.5450, "base_risk": 0.57},
    "De Wijert":         {"lat": 53.2055, "lon": 6.5680, "base_risk": 0.59},
    "De Linie":          {"lat": 53.2105, "lon": 6.5700, "base_risk": 0.63},
    "De Held":           {"lat": 53.2260, "lon": 6.5150, "base_risk": 0.52},
    "Peizerweg":         {"lat": 53.2150, "lon": 6.5250, "base_risk": 0.58},
    "Europapark":        {"lat": 53.2090, "lon": 6.5870, "base_risk": 0.64},
    "Eemskanaalzone":    {"lat": 53.2135, "lon": 6.6000, "base_risk": 0.61},
    "Noorderplantsoen":  {"lat": 53.2260, "lon": 6.5590, "base_risk": 0.50},
    "Zeeheldenbuurt":    {"lat": 53.2155, "lon": 6.5520, "base_risk": 0.56},
    "Oranjebuurt":       {"lat": 53.2220, "lon": 6.5525, "base_risk": 0.54},
    "Professorenbuurt":  {"lat": 53.2225, "lon": 6.5660, "base_risk": 0.58},
}

MONTHS = [
    f"{year}-{month:02d}"
    for year in (2023, 2024)
    for month in range(1, 13)
]

CRIME_TYPES = ["Geweld", "Overlast", "Diefstal", "Drugs", "Vermissing"]

# Roughly: some neighbourhoods with more E33 (mental health) burden
E33_MULTIPLIER = {
    "Binnenstad": 1.2,
    "Oosterparkwijk": 1.25,
    "Beijum": 1.2,
    "Lewenborg": 1.15,
    "Korrewegwijk": 1.15,
    "Selwerd": 1.1,
    "Ulgersmaborg": 1.1,
}


def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_schema(conn: sqlite3.Connection):
    cur = conn.cursor()

    # Regions table: aggregated stats per month per neighbourhood
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS Regions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            month_year TEXT NOT NULL,
            crime_level INTEGER NOT NULL,
            incident_count INTEGER NOT NULL,
            crime_type TEXT NOT NULL,
            e33_rate REAL NOT NULL,
            lat REAL NOT NULL,
            lon REAL NOT NULL
        )
        """
    )

    # Calls table: individual synthetic 112 incidents
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS Calls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            call_log TEXT NOT NULL,
            address TEXT NOT NULL,
            region_name TEXT NOT NULL,
            month_year TEXT NOT NULL,
            crime_type TEXT NOT NULL,
            is_e33 INTEGER NOT NULL,
            lat REAL NOT NULL,
            lon REAL NOT NULL
        )
        """
    )

    conn.commit()


def clear_existing(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute("DELETE FROM Regions")
    cur.execute("DELETE FROM Calls")
    conn.commit()


def pick_crime_type(base_risk: float) -> str:
    # Slight bias: higher-risk areas more 'Geweld' / 'Drugs'
    r = random.random()
    if base_risk >= 0.75:
        if r < 0.35:
            return "Geweld"
        elif r < 0.60:
            return "Overlast"
        elif r < 0.80:
            return "Diefstal"
        elif r < 0.93:
            return "Drugs"
        else:
            return "Vermissing"
    elif base_risk >= 0.60:
        if r < 0.25:
            return "Geweld"
        elif r < 0.55:
            return "Overlast"
        elif r < 0.80:
            return "Diefstal"
        elif r < 0.90:
            return "Drugs"
        else:
            return "Vermissing"
    else:
        if r < 0.15:
            return "Geweld"
        elif r < 0.55:
            return "Overlast"
        elif r < 0.80:
            return "Diefstal"
        elif r < 0.90:
            return "Drugs"
        else:
            return "Vermissing"


def generate_region_row(name: str, info: dict, month_year: str):
    base = info["base_risk"]

    # Crime level 1–10 roughly scaled by base risk and a bit of noise
    crime_level = max(1, min(10, int(round(base * 10 + random.uniform(-2, 2)))))

    # Incident count 10–200, scaled
    base_incidents = int(40 + base * 120 + random.uniform(-20, 20))
    incident_count = max(10, base_incidents)

    crime_type = pick_crime_type(base)

    # E33 rate: between 3% and 18%, scaled by multiplier and risk
    mult = E33_MULTIPLIER.get(name, 1.0)
    e33_rate = max(0.03, min(0.18, 0.05 + base * 0.10 * mult + random.uniform(-0.02, 0.02)))

    lat = info["lat"] + random.uniform(-0.0015, 0.0015)
    lon = info["lon"] + random.uniform(-0.0020, 0.0020)

    return {
        "name": name,
        "month_year": month_year,
        "crime_level": crime_level,
        "incident_count": incident_count,
        "crime_type": crime_type,
        "e33_rate": e33_rate,
        "lat": lat,
        "lon": lon,
    }


# Templates for synthetic Dutch 112 calls
CALL_TEMPLATES = {
    "Geweld": [
        "Melding van vechtpartij in de buurt van {addr}. Verdachte is agressief en schreeuwt.",
        "Buurman meldt dat iemand wordt geslagen in {addr}. Veel geschreeuw en dreiging.",
        "Meerdere personen ruzie op straat bij {addr}. Slachtoffer lijkt gewond.",
    ],
    "Overlast": [
        "Bewoner meldt ernstige geluidsoverlast in {addr}, groep jongeren schreeuwt en slaat met dingen.",
        "Klacht over buurtbewoners die al uren schreeuwen en ruzie maken bij {addr}.",
        "Omwonenden melden aanhoudende overlast bij {addr}, vermoedelijk alcoholgebruik.",
    ],
    "Diefstal": [
        "Melding van inbraak(poging) bij woning in {addr}. Verdachte is mogelijk nog in de buurt.",
        "Getuige ziet iemand fietsen stelen bij {addr}. Verdachte rijdt net weg.",
        "Winkelier meldt winkeldiefstal in de omgeving van {addr}.",
    ],
    "Drugs": [
        "Mogelijke drugshandel gesignaleerd bij {addr}. Auto's rijden af en aan.",
        "Bewoner ruikt sterke wietlucht in portiek bij {addr}, vermoedelijk hennepplantage.",
        "Melding van dealplek in de buurt van {addr}, bekende verdachten aanwezig.",
    ],
    "Vermissing": [
        "Melding van vermiste tiener, voor het laatst gezien bij {addr}.",
        "Persoon met verward gedrag vertrokken vanuit {addr} en niet teruggekeerd.",
        "Oudere persoon met dementie vermist, woonachtig bij {addr}.",
    ],
}

# E33-related phrases we sometimes add
E33_SNIPPETS = [
    "Persoon lijkt verward en spreekt onsamenhangend.",
    "Melder geeft aan dat betrokkene psychische problemen heeft.",
    "Er is een risico op zelfbeschadiging volgens de melder.",
    "Melder zegt dat betrokkene onder behandeling is bij de GGZ.",
    "Betrokkene dreigt zichzelf iets aan te doen.",
]


def make_address(region_name: str) -> str:
    # Very simple synthetic address
    street_parts = {
        "Binnenstad": "Grote Markt",
        "Oosterpoort": "Oosterweg",
        "Oosterparkwijk": "Oosterparkstraat",
        "Korrewegwijk": "Korreweg",
        "De Hoogte": "Molukkenstraat",
        "Selwerd": "Eikenlaan",
        "Paddepoel": "Dierenriemstraat",
        "Vinkhuizen": "Paterswoldseweg",
        "Hoogkerk": "Zuiderweg",
        "Reitdiep": "Reitdiephaven",
        "Beijum": "Claremaheerd",
        "Lewenborg": "Bottemaheerd",
        "De Hunze": "Hunzelaan",
        "Ulgersmaborg": "Ulgersmaweg",
        "Oosterhoogebrug": "Oosterhoogebrugstraat",
        "Helpman": "Helper Brink",
        "Coendersborg": "Coendersweg",
        "Hoornsemeer": "Piccardthof",
        "Corpus den Hoorn": "Laan Corpus den Hoorn",
        "De Wijert": "Van Iddekingeweg",
        "De Linie": "Sontweg",
        "De Held": "De Heldring",
        "Peizerweg": "Peizerweg",
        "Europapark": "Helperzoom",
        "Eemskanaalzone": "Osloweg",
        "Noorderplantsoen": "Noorderbinnensingel",
        "Zeeheldenbuurt": "Trompstraat",
        "Oranjebuurt": "Oranjesingel",
        "Professorenbuurt": "Professor Rankestraat",
    }
    street = street_parts.get(region_name, "Onbekende Straat")
    nr = random.randint(1, 180)
    return f"{street} {nr}, Groningen"


def generate_calls_for_region_month(region_row, approx_calls=6):
    """
    Generate ~N synthetic calls for one region+month combination.
    approx_calls can be scaled by incident_count.
    """
    name = region_row["name"]
    month_year = region_row["month_year"]
    crime_type = region_row["crime_type"]
    e33_rate = region_row["e33_rate"]
    lat = region_row["lat"]
    lon = region_row["lon"]

    # More incidents -> more generated calls
    base_inc = region_row["incident_count"]
    n_calls = max(3, min(20, int(base_inc / 20) + random.randint(-2, 3)))

    template_list = CALL_TEMPLATES.get(crime_type, CALL_TEMPLATES["Overlast"])
    calls = []

    year, month = map(int, month_year.split("-"))
    for _ in range(n_calls):
        addr = make_address(name)
        template = random.choice(template_list)
        text = template.format(addr=addr)

        # Decide if this call is E33-ish
        is_e33 = 1 if random.random() < (e33_rate * 1.2) else 0
        if is_e33:
            snippet = random.choice(E33_SNIPPETS)
            text = f"{text} {snippet}"

        # small jitter around region centroid
        jitter_lat = lat + random.uniform(-0.0020, 0.0020)
        jitter_lon = lon + random.uniform(-0.0030, 0.0030)

        calls.append({
            "call_log": text,
            "address": addr,
            "region_name": name,
            "month_year": month_year,
            "crime_type": crime_type,
            "is_e33": is_e33,
            "lat": jitter_lat,
            "lon": jitter_lon,
        })

    return calls


def main():
    print(f"Using DB at {DB_PATH}")
    conn = connect()
    ensure_schema(conn)
    clear_existing(conn)

    cur = conn.cursor()

    all_calls = []
    region_rows = []

    for name, info in NEIGHBORHOODS.items():
        for month_year in MONTHS:
            region_data = generate_region_row(name, info, month_year)
            region_rows.append(region_data)

            calls = generate_calls_for_region_month(region_data)
            all_calls.extend(calls)

    # Insert regions
    cur.executemany(
        """
        INSERT INTO Regions (name, month_year, crime_level, incident_count, crime_type, e33_rate, lat, lon)
        VALUES (:name, :month_year, :crime_level, :incident_count, :crime_type, :e33_rate, :lat, :lon)
        """,
        region_rows,
    )

    # Insert calls
    cur.executemany(
        """
        INSERT INTO Calls (call_log, address, region_name, month_year, crime_type, is_e33, lat, lon)
        VALUES (:call_log, :address, :region_name, :month_year, :crime_type, :is_e33, :lat, :lon)
        """,
        all_calls,
    )

    conn.commit()
    conn.close()

    print(f"Seeded {len(region_rows)} region-month rows and {len(all_calls)} calls.")


if __name__ == "__main__":
    main()
