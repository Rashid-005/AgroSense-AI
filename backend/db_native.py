"""
NeuralStorm AI - Native Zero-Dependency SQLite Engine
Uses Python's built-in sqlite3 standard library.
Requires ZERO external packages. Guaranteed to run on any computer out-of-the-box.
"""

import sqlite3
import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "neuralstorm.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Farms Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS farms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        owner TEXT DEFAULT 'Shamba Demo',
        location TEXT DEFAULT 'Zanzibar, Tanzania',
        soil_type TEXT DEFAULT 'loamy',
        crop_type TEXT DEFAULT 'tomato',
        area_m2 REAL DEFAULT 1000.0,
        created_at TEXT
    )
    """)

    # Irrigation Records Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS irrigation_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        farm_id INTEGER,
        crop TEXT NOT NULL,
        soil TEXT NOT NULL,
        soil_moisture_pct REAL NOT NULL,
        temperature_c REAL NOT NULL,
        humidity_pct REAL NOT NULL,
        recommended_volume_liters REAL NOT NULL,
        water_saved_liters REAL DEFAULT 0.0,
        urgency TEXT DEFAULT 'NONE',
        optimal_window TEXT DEFAULT '06:00 AM - 08:30 AM',
        swahili_advice TEXT,
        created_at TEXT,
        FOREIGN KEY (farm_id) REFERENCES farms(id)
    )
    """)

    # Pathology Scans Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pathology_scans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        farm_id INTEGER,
        crop TEXT NOT NULL,
        disease_name TEXT NOT NULL,
        swahili_name TEXT NOT NULL,
        confidence_pct REAL NOT NULL,
        severity TEXT DEFAULT 'Moderate',
        affected_area_pct REAL DEFAULT 0.0,
        organic_treatment TEXT,
        chemical_treatment TEXT,
        irrigation_adjustment TEXT,
        image_filename TEXT,
        created_at TEXT,
        FOREIGN KEY (farm_id) REFERENCES farms(id)
    )
    """)

    conn.commit()
    conn.close()


def save_irrigation_record(data: Dict[str, Any]) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
    INSERT INTO irrigation_records (
        farm_id, crop, soil, soil_moisture_pct, temperature_c, humidity_pct,
        recommended_volume_liters, water_saved_liters, urgency, optimal_window,
        swahili_advice, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("farm_id"),
        data.get("crop", "Tomato"),
        data.get("soil", "Loam"),
        data.get("soil_moisture_pct", 35.0),
        data.get("temperature_c", 28.0),
        data.get("humidity_pct", 60.0),
        data.get("recommended_volume_liters", 0.0),
        data.get("water_saved_liters", 0.0),
        data.get("urgency", "NONE"),
        data.get("optimal_window", "06:00 AM - 08:30 AM"),
        data.get("swahili_advice", ""),
        now_str
    ))
    record_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return record_id


def save_pathology_scan(data: Dict[str, Any]) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
    INSERT INTO pathology_scans (
        farm_id, crop, disease_name, swahili_name, confidence_pct, severity,
        affected_area_pct, organic_treatment, chemical_treatment,
        irrigation_adjustment, image_filename, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("farm_id"),
        data.get("crop", "Tomato"),
        data.get("disease_name", ""),
        data.get("swahili_name", ""),
        data.get("confidence_pct", 95.0),
        data.get("severity", "Moderate"),
        data.get("affected_area_pct", 0.0),
        json.dumps(data.get("organic_treatment", [])),
        json.dumps(data.get("chemical_treatment", [])),
        data.get("irrigation_adjustment", ""),
        data.get("image_filename", ""),
        now_str
    ))
    record_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return record_id


def get_recent_history(limit: int = 10) -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM irrigation_records ORDER BY id DESC LIMIT ?", (limit,))
    irrigations = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("SELECT * FROM pathology_scans ORDER BY id DESC LIMIT ?", (limit,))
    scans = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    total_saved = sum(item.get("water_saved_liters", 0.0) for item in irrigations)
    return {
        "irrigation_history": irrigations,
        "pathology_scans": scans,
        "total_water_saved_liters": round(total_saved, 1)
    }


# Auto-initialize database schema
init_db()
