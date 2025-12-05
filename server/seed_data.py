# server/seed_data.py
import os
from sqlalchemy.orm import Session
from .db import Base, engine, SessionLocal
from .models import Call, Region

def reset_db():
    if os.path.exists(os.path.join(os.path.dirname(__file__), "city_safety.db")):
        os.remove(os.path.join(os.path.dirname(__file__), "city_safety.db"))
    Base.metadata.create_all(bind=engine)

def seed():
    reset_db()
    db: Session = SessionLocal()

    # --- Groningen calls (rough coords around city centre) ---
    calls = [
        Call(
            address="Grote Markt, Groningen",
            transcript="Melder: er is een vechtpartij gaande bij de Grote Markt, meerdere personen slaan en schreeuwen.",
            lat=53.2192, lon=6.5680, is_e33=False,
        ),
        Call(
            address="Oosterstraat, Groningen",
            transcript="Melder: man schreeuwt dat hij zichzelf iets gaat aandoen, lijkt onder invloed.",
            lat=53.2175, lon=6.5740, is_e33=True,
        ),
        Call(
            address="Korrewegwijk, Groningen",
            transcript="Melder: burenruzie loopt uit de hand, één persoon dreigt met een mes.",
            lat=53.2320, lon=6.5790, is_e33=False,
        ),
        Call(
            address="Beijum, Groningen",
            transcript="Melder: verward persoon loopt op straat en gooit spullen, roept dat stemmen hem bevelen geven.",
            lat=53.2470, lon=6.5880, is_e33=True,
        ),
        Call(
            address="Paddepoel, Groningen",
            transcript="Melder: groep jongeren intimideert voorbijgangers bij winkelcentrum, mogelijk drugsdeal.",
            lat=53.2350, lon=6.5410, is_e33=False,
        ),
        Call(
            address="Selwerd, Groningen",
            transcript="Melder: vrouw huilt op balkon en roept dat ze het niet meer ziet zitten.",
            lat=53.2355, lon=6.5560, is_e33=True,
        ),
        Call(
            address="Helpman, Groningen",
            transcript="Melder: overvalpoging bij kleine supermarkt, dader gevlucht richting station Europapark.",
            lat=53.2030, lon=6.5800, is_e33=False,
        ),
        Call(
            address="Lewenborg, Groningen",
            transcript="Melder: man slaat tegen deuren en ramen, zegt dat iedereen hem wil pakken.",
            lat=53.2370, lon=6.6190, is_e33=True,
        ),
    ]
    db.add_all(calls)
    db.commit()

    # --- Groningen regions (buurten) ---
    # Names should align with BUURTNAAM in the GeoJSON for best matching.
    regions = [
        Region(
            name="Binnenstad",
            center_lat=53.2194, center_lon=6.5665,
            crime_level=4,
            incident_count=48,
            e33_count=8,
            month_year="2025-08",
            prevalent_crime_type="robberies",
        ),
        Region(
            name="Oosterpoort",
            center_lat=53.2110, center_lon=6.5800,
            crime_level=3,
            incident_count=26,
            e33_count=6,
            month_year="2025-08",
            prevalent_crime_type="violent",
        ),
        Region(
            name="Korrewegwijk",
            center_lat=53.2280, center_lon=6.5720,
            crime_level=4,
            incident_count=40,
            e33_count=10,
            month_year="2025-08",
            prevalent_crime_type="violent",
        ),
        Region(
            name="Beijum",
            center_lat=53.2460, center_lon=6.5870,
            crime_level=3,
            incident_count=30,
            e33_count=12,
            month_year="2025-08",
            prevalent_crime_type="drugs",
        ),
        Region(
            name="Paddepoel",
            center_lat=53.2370, center_lon=6.5410,
            crime_level=2,
            incident_count=18,
            e33_count=3,
            month_year="2025-08",
            prevalent_crime_type="other",
        ),
        Region(
            name="Selwerd",
            center_lat=53.2355, center_lon=6.5560,
            crime_level=3,
            incident_count=24,
            e33_count=9,
            month_year="2025-08",
            prevalent_crime_type="drugs",
        ),
        Region(
            name="Helpman",
            center_lat=53.2030, center_lon=6.5800,
            crime_level=2,
            incident_count=15,
            e33_count=2,
            month_year="2025-08",
            prevalent_crime_type="robberies",
        ),
        Region(
            name="Lewenborg",
            center_lat=53.2370, center_lon=6.6190,
            crime_level=3,
            incident_count=22,
            e33_count=7,
            month_year="2025-08",
            prevalent_crime_type="violent",
        ),
    ]
    db.add_all(regions)
    db.commit()
    db.close()
    print("✅ Seeded DB with Groningen calls & regions (incl. E33).")

if __name__ == "__main__":
    seed()
