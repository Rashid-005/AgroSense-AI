"""
AgroSense AI - Live Meteorological & Weather Forecasting Service (GP-02)
Integrates Open-Meteo Global Satellite & Terrestrial Weather Telemetry.
Zero API Key required, 100% open access.
"""

import urllib.request
import json
from typing import Dict, Any, Optional


class LiveWeatherService:
    KNOWN_LOCATIONS = {
        "zanzibar": {"name": "Zanzibar, Tanzania", "lat": -6.1659, "lon": 39.2026},
        "dar_es_salaam": {"name": "Dar es Salaam, Tanzania", "lat": -6.7924, "lon": 39.2083},
        "arusha": {"name": "Arusha, Tanzania", "lat": -3.3869, "lon": 36.6830},
        "mbeya": {"name": "Mbeya, Tanzania", "lat": -8.9094, "lon": 33.4608},
        "hyderabad": {"name": "Hyderabad, India (JNTUH)", "lat": 17.3850, "lon": 78.4867},
        "nairobi": {"name": "Nairobi, Kenya", "lat": -1.2921, "lon": 36.8219}
    }

    @classmethod
    def fetch_live_weather(
        cls,
        location_key: str = "zanzibar",
        lat: Optional[float] = None,
        lon: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Fetches real-time temperature, humidity, and 24h precipitation forecast from Open-Meteo.
        """
        loc_name = "Custom Farm GPS"
        if lat is None or lon is None:
            key = location_key.lower().strip()
            loc_data = cls.KNOWN_LOCATIONS.get(key, cls.KNOWN_LOCATIONS["zanzibar"])
            lat = loc_data["lat"]
            lon = loc_data["lon"]
            loc_name = loc_data["name"]

        api_url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}&"
            f"current=temperature_2m,relative_humidity_2m,wind_speed_10m&"
            f"daily=precipitation_sum,temperature_2m_max,temperature_2m_min&"
            f"timezone=auto"
        )

        try:
            req = urllib.request.Request(api_url, headers={"User-Agent": "AgroSenseAI/1.0"})
            with urllib.request.urlopen(req, timeout=4.0) as resp:
                data = json.loads(resp.read().decode())

            current = data.get("current", {})
            daily = data.get("daily", {})

            temp = round(float(current.get("temperature_2m", 26.0)), 1)
            humidity = round(float(current.get("relative_humidity_2m", 65.0)), 0)
            wind = round(float(current.get("wind_speed_10m", 2.0)), 1)

            precip_list = daily.get("precipitation_sum", [0.0])
            rain_24h = round(float(precip_list[0]) if precip_list else 0.0, 1)

            return {
                "success": True,
                "location": loc_name,
                "latitude": lat,
                "longitude": lon,
                "temperature_c": temp,
                "humidity_pct": humidity,
                "rainfall_forecast_mm": rain_24h,
                "wind_speed_m_s": wind,
                "source": "Open-Meteo Live Satellite Telemetry",
                "is_live": True
            }

        except Exception as e:
            # Resilient fallback to regional climate baseline
            return {
                "success": False,
                "location": loc_name,
                "latitude": lat,
                "longitude": lon,
                "temperature_c": 27.5,
                "humidity_pct": 68.0,
                "rainfall_forecast_mm": 0.0,
                "wind_speed_m_s": 2.2,
                "source": "AgroClimatic Baseline (Offline Fallback)",
                "is_live": False,
                "error": str(e)
            }
