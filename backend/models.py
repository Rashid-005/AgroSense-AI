"""
NeuralStorm AI - Database Schema Models
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class Farm(Base):
    __tablename__ = "farms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    owner = Column(String(100), default="Shamba Demo")
    location = Column(String(100), default="Zanzibar, Tanzania")
    soil_type = Column(String(50), default="loamy")
    crop_type = Column(String(50), default="tomato")
    area_m2 = Column(Float, default=1000.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    irrigations = relationship("IrrigationRecord", back_populates="farm", cascade="all, delete-orphan")
    scans = relationship("PathologyScan", back_populates="farm", cascade="all, delete-orphan")


class IrrigationRecord(Base):
    __tablename__ = "irrigation_records"

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=True)
    crop = Column(String(50), nullable=False)
    soil = Column(String(50), nullable=False)
    soil_moisture_pct = Column(Float, nullable=False)
    temperature_c = Column(Float, nullable=False)
    humidity_pct = Column(Float, nullable=False)
    recommended_volume_liters = Column(Float, nullable=False)
    water_saved_liters = Column(Float, default=0.0)
    urgency = Column(String(30), default="NONE")
    optimal_window = Column(String(50), default="06:00 AM - 08:30 AM")
    swahili_advice = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    farm = relationship("Farm", back_populates="irrigations")


class PathologyScan(Base):
    __tablename__ = "pathology_scans"

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=True)
    crop = Column(String(50), nullable=False)
    disease_name = Column(String(100), nullable=False)
    swahili_name = Column(String(100), nullable=False)
    confidence_pct = Column(Float, nullable=False)
    severity = Column(String(30), default="Moderate")
    affected_area_pct = Column(Float, default=0.0)
    organic_treatment = Column(Text, nullable=True)
    chemical_treatment = Column(Text, nullable=True)
    irrigation_adjustment = Column(Text, nullable=True)
    image_filename = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    farm = relationship("Farm", back_populates="scans")
