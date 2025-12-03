# server/seed_data.py
from server.db import Base, engine, SessionLocal
from server.models import Call, Region

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Wipe & seed minimal demo set
        db.query(Call).delete()
        db.query(Region).delete()

        # Example 112 calls (addresses + optional lat/lon)
        calls = [
            Call(call_log="Melder: mijn vriendin schreeuwt en bedreigt mij; ik ben gevlucht.",
                 address="Dam, Amsterdam", lat=52.3731, lon=4.8922),
            Call(call_log="Fiets gestolen nabij station.", address="Stationsplein, Amsterdam", lat=52.3780, lon=4.9000),
            Call(call_log="Vechpartij gemeld, meerdere personen betrokken.",
                 address="Witte de Withstraat, Rotterdam", lat=51.9149, lon=4.4699),
        ]
        db.add_all(calls)

        # Regions — small demo set across two cities, two months
        regions = [
            Region(name="Centrum A’dam", center_lat=52.3728, center_lon=4.8936,
                   crime_level=4, incident_count=38, month_year="2025-07", prevalent_crime_type="robberies"),
            Region(name="Jordaan", center_lat=52.3759, center_lon=4.8820,
                   crime_level=3, incident_count=22, month_year="2025-07", prevalent_crime_type="drugs"),
            Region(name="Centrum A’dam", center_lat=52.3728, center_lon=4.8936,
                   crime_level=5, incident_count=55, month_year="2025-08", prevalent_crime_type="violent"),
            Region(name="Bijlmer", center_lat=52.3130, center_lon=4.9720,
                   crime_level=2, incident_count=15, month_year="2025-08", prevalent_crime_type="drugs"),
            Region(name="Centrum R’dam", center_lat=51.9244, center_lon=4.4777,
                   crime_level=3, incident_count=27, month_year="2025-08", prevalent_crime_type="robberies"),
            Region(name="Katendrecht", center_lat=51.9040, center_lon=4.4880,
                   crime_level=4, incident_count=33, month_year="2025-08", prevalent_crime_type="violent"),
        ]
        db.add_all(regions)

        db.commit()
        print("✅ Seeded DB with demo calls & regions.")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
