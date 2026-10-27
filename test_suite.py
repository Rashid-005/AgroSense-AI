"""
AgroSense AI - Comprehensive Automated Test Suite
Verifies all ML algorithms, Explainable AI, SQLite persistence, and API endpoints.
"""

import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ml_engine.irrigation_model import PrecisionIrrigationEngine
from ml_engine.leaf_pathology import CropDiseaseRegistry
from ml_engine.explainable_ai import ExplainableAIEngine
from ml_engine.metrics_evaluator import get_official_benchmarks
from backend.db_native import save_irrigation_record, save_pathology_scan, get_recent_history
from fastapi.testclient import TestClient
from backend.app import app


def run_tests():
    print("=" * 60)
    print("  Running AgroSense AI Automated Verification Suite")
    print("=" * 60)

    # 1. Test Precision Irrigation Engine
    print("[1/5] Testing Precision Irrigation Engine (FAO-56 & ML)...", end=" ")
    engine = PrecisionIrrigationEngine()
    et0 = engine.calculate_fao56_et0(temperature_c=28.5, humidity_pct=60.0, wind_speed_m_s=2.0)
    assert et0 > 0.0, f"Invalid ET0: {et0}"
    
    advisory = engine.calculate_irrigation_advisory(
        crop_name="maize",
        growth_stage="mid",
        soil_type="sandy",
        current_moisture_pct=8.0,
        temperature_c=34.0,
        humidity_pct=30.0,
        rainfall_forecast_mm=0.0,
        farm_area_m2=1000.0
    )
    assert advisory["should_irrigate"] is True, "Expected should_irrigate=True"
    assert advisory["urgency"] in ["MODERATE", "URGENT", "CRITICAL"], f"Unexpected urgency: {advisory['urgency']}"
    assert advisory["water_saved_liters"] > 0, "Water savings should be positive"
    print("PASSED [OK]")

    # 2. Test Leaf Pathology Diagnostic Engine
    print("[2/5] Testing Leaf Pathology Diagnostic Engine...", end=" ")
    diag = CropDiseaseRegistry.diagnose_leaf(filename="tomato_early_blight.jpg")
    assert "Early Blight" in diag["disease_name"]
    assert len(diag["organic_treatment"]) > 0
    assert len(diag["chemical_treatment"]) > 0
    assert "drip" in diag["irrigation_adjustment"].lower() or "overhead" in diag["irrigation_adjustment"].lower()
    print("PASSED [OK]")

    # 3. Test Explainable AI (Grad-CAM)
    print("[3/5] Testing Grad-CAM Explainable AI Generation...", end=" ")
    xai = ExplainableAIEngine.generate_attention_heatmap(width=400, height=300, severity="Moderate")
    assert "activation_grid" in xai
    assert len(xai["hotspots"]) > 0
    assert xai["technique"] == "Grad-CAM (Gradient-weighted Class Activation Mapping)"
    print("PASSED [OK]")

    # 4. Test Database Persistence
    print("[4/5] Testing Native SQLite Database CRUD...", end=" ")
    irr_id = save_irrigation_record({
        "crop": "Tomato",
        "soil": "Loam",
        "soil_moisture_pct": 25.0,
        "temperature_c": 29.0,
        "humidity_pct": 55.0,
        "recommended_volume_liters": 2500.0,
        "water_saved_liters": 1200.0,
        "urgency": "MODERATE",
        "optimal_window": "06:00 AM",
        "swahili_advice": "Jaribio la data"
    })
    assert irr_id > 0

    scan_id = save_pathology_scan({
        "crop": "Tomato",
        "disease_name": "Early Blight",
        "swahili_name": "Bakajani la Mapema",
        "confidence_pct": 98.2,
        "severity": "Moderate",
        "organic_treatment": ["Tiba 1"],
        "chemical_treatment": ["Tiba 2"]
    })
    assert scan_id > 0

    history = get_recent_history(5)
    assert len(history["irrigation_history"]) > 0
    assert len(history["pathology_scans"]) > 0
    print("PASSED [OK]")

    # 5. Test FastAPI HTTP Endpoints
    print("[5/5] Testing FastAPI Endpoints (/api/health, /api/calculate, /api/scan)...", end=" ")
    client = TestClient(app)
    
    # Health
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["challenge_code"] == "GP-02"
    assert r.json()["system"] == "AgroSense AI"

    # Irrigation calculation
    r = client.post("/api/irrigation/calculate", json={
        "crop_name": "tomato",
        "growth_stage": "mid",
        "soil_type": "loamy",
        "current_moisture_pct": 30.0,
        "temperature_c": 27.0,
        "humidity_pct": 65.0,
        "rainfall_forecast_mm": 0.0,
        "farm_area_m2": 500.0
    })
    assert r.status_code == 200
    assert "total_water_liters_needed" in r.json()

    # Leaf scan
    r = client.post("/api/pathology/scan", json={
        "filename_hint": "tomato_late_blight.jpg"
    })
    assert r.status_code == 200
    assert "diagnosis" in r.json()
    assert "explainable_ai" in r.json()

    # Presets
    r = client.get("/api/presets")
    assert r.status_code == 200
    assert len(r.json()) >= 3

    print("PASSED [OK]")
    print("=" * 60)
    print("  ALL 5 TEST MODULES PASSED PERFECTLY! (100% SUCCESS)")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
