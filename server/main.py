# server/main.py
from __future__ import annotations

import math
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .db import SessionLocal
from .models import Call, Region

# ---------------------------------------------------------------------
# DB dependency
# ---------------------------------------------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Rough distance in km between two lat/lon points."""
    R = 6371.0
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(d_lon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# ---------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------
app = FastAPI(title="Groningen Crime Map API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # in prod: tighten this to your frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok"}

# ---------------------------------------------------------------------
# Calls
# ---------------------------------------------------------------------
@app.get("/calls")
def get_calls(db: Session = Depends(get_db)):
    rows = db.query(Call).all()
    return [
        {
            "id": c.id,
            "address": c.address,
            "transcript": c.transcript,
            "lat": c.lat,
            "lon": c.lon,
            "is_e33": bool(c.is_e33),
        }
        for c in rows
    ]

# ---------------------------------------------------------------------
# Regions near (for choropleth)
# ---------------------------------------------------------------------
@app.get("/regions/near")
def get_regions_near(
    lat: float = Query(...),
    lon: float = Query(...),
    radius_km: float = Query(5.0, gt=0.0),
    month_year: Optional[str] = Query(None),
    crime_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(Region)

    if month_year:
        q = q.filter(Region.month_year == month_year)

    if crime_type:
        q = q.filter(Region.prevalent_crime_type == crime_type)

    regions = q.all()

    # distance filter
    result = []
    for r in regions:
        d = haversine_km(lat, lon, r.center_lat, r.center_lon)
        if d <= radius_km:
            e33_pct = (r.e33_count / r.incident_count) if r.incident_count else 0.0
            result.append(
                {
                    "id": r.id,
                    "name": r.name,
                    "center_lat": r.center_lat,
                    "center_lon": r.center_lon,
                    "crime_level": r.crime_level,
                    "incident_count": r.incident_count,
                    "e33_count": r.e33_count,
                    "e33_percent": round(e33_pct, 3),
                    "month_year": r.month_year,
                    "prevalent_crime_type": r.prevalent_crime_type,
                }
            )

    if not result:
        # Not an error, just empty
        return []

    return result
