# server/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from server.db import Base

class Call(Base):
    __tablename__ = "calls"
    id = Column(Integer, primary_key=True, index=True)
    call_log = Column(String, nullable=False)
    address = Column(String, nullable=False)
    # Optional direct geo to avoid external geocoding
    lat = Column(Float, nullable=True)
    lon = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Region(Base):
    __tablename__ = "regions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)                 # e.g., neighborhood name
    center_lat = Column(Float, nullable=False)
    center_lon = Column(Float, nullable=False)
    crime_level = Column(Integer, nullable=False)         # 1..5
    incident_count = Column(Integer, nullable=False)
    month_year = Column(String, nullable=False)           # e.g., "2025-08"
    prevalent_crime_type = Column(String, nullable=False) # e.g., "drugs", "robberies", "violent"
