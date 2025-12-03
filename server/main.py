# server/main.py
from __future__ import annotations
import math
from typing import List, Optional, Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import select
from server.db import Base, engine, SessionLocal
from server.models import Call, Region

app = FastAPI(title="City Safety Map API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten for prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

# ---------------------- Schemas ----------------------
class CallOut(BaseModel):
    id: int
    call_log: str
    address: str
    lat: Optional[float] = None
    lon: Optional[float] = None
    class Config:
        from_attributes = True

class RegionOut(BaseModel):
    id: int
    name: str
    center_lat: float
    center_lon: float
    crime_level: int
    incident_count: int
    month_year: str
    prevalent_crime_type: str
    class Config:
        from_attributes = True

# ---------------------- Utils ----------------------
def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0088
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dlmb/2)**2
    return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1-a)))

# ---------------------- Endpoints ----------------------
@app.get("/health")
def health():
    return {"ok": True}

@app.get("/calls", response_model=List[CallOut])
def list_calls():
    db = SessionLocal()
    try:
        rows = db.execute(select(Call).order_by(Call.id.desc())).scalars().all()
        return rows
    finally:
        db.close()

@app.get("/calls/{call_id}", response_model=CallOut)
def get_call(call_id: int):
    db = SessionLocal()
    try:
        row = db.get(Call, call_id)
        if not row:
            raise HTTPException(404, "Call not found")
        return row
    finally:
        db.close()

@app.get("/regions", response_model=List[RegionOut])
def list_regions(
    month_year: Optional[str] = None,
    crime_type: Optional[str] = None
):
    db = SessionLocal()
    try:
        stmt = select(Region)
        if month_year:
            stmt = stmt.filter(Region.month_year == month_year)
        if crime_type:
            stmt = stmt.filter(Region.prevalent_crime_type == crime_type)
        rows = db.execute(stmt).scalars().all()
        return rows
    finally:
        db.close()

@app.get("/regions/near", response_model=List[RegionOut])
def regions_near(
    lat: float,
    lon: float,
    radius_km: float = 3.0,
    month_year: Optional[str] = None,
    crime_type: Optional[str] = None
):
    db = SessionLocal()
    try:
        stmt = select(Region)
        if month_year:
            stmt = stmt.filter(Region.month_year == month_year)
        if crime_type:
            stmt = stmt.filter(Region.prevalent_crime_type == crime_type)
        rows = db.execute(stmt).scalars().all()

        nearby = []
        for r in rows:
            d = haversine_km(lat, lon, r.center_lat, r.center_lon)
            if d <= radius_km:
                nearby.append(r)
        # fallback: if none within radius, return closest 6
        if not nearby and rows:
            ranked = sorted(rows, key=lambda x: haversine_km(lat, lon, x.center_lat, x.center_lon))
            nearby = ranked[:6]
        return nearby
    finally:
        db.close()
