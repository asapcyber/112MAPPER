# server/models.py
from sqlalchemy import Column, Integer, Float, String, Boolean
from .db import Base

class Call(Base):
    __tablename__ = "calls"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String, index=True)
    transcript = Column(String)
    lat = Column(Float)
    lon = Column(Float)
    # Optional: whether this call was E33-related
    is_e33 = Column(Boolean, default=False)


class Region(Base):
    __tablename__ = "regions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)          # should match buurt name in GeoJSON
    center_lat = Column(Float)
    center_lon = Column(Float)
    crime_level = Column(Integer)              # 1–5
    incident_count = Column(Integer)           # total incidents
    e33_count = Column(Integer, default=0)     # subset of incidents that are E33
    month_year = Column(String, index=True)    # e.g. "2025-07"
    prevalent_crime_type = Column(String)      # e.g. "drugs", "robberies", "violent", "other"
