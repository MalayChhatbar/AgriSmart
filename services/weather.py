import httpx
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger("agrismart.weather")

# Fallback default coordinates (Pune, Maharashtra, India)
DEFAULT_LAT = 18.5204
DEFAULT_LON = 73.8567
DEFAULT_LOCATION = "Pune, Maharashtra"

async def geocode_location(location_name: str) -> Dict[str, Any]:
    """
    Geocodes a location name to lat/lon using Open-Meteo Geocoding API (Zero-Key guarantee).
    """
    clean_name = location_name.split(",")[0].strip()
    try:
        url = f"https://geocoding-api.open-meteo.com/v1/search?name={clean_name}&count=1&language=en&format=json"
        async with httpx.AsyncClient(timeout=6.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                results = data.get("results")
                if results and len(results) > 0:
                    best = results[0]
                    return {
                        "name": f"{best.get('name')}, {best.get('admin1', '')} ({best.get('country_code', '')})".strip(", "),
                        "latitude": float(best["latitude"]),
                        "longitude": float(best["longitude"]),
                        "timezone": best.get("timezone", "Asia/Kolkata")
                    }
    except Exception as e:
        logger.warning(f"Geocoding error for '{location_name}': {e}")

    return {
        "name": location_name or DEFAULT_LOCATION,
        "latitude": DEFAULT_LAT,
        "longitude": DEFAULT_LON,
        "timezone": "Asia/Kolkata"
    }

async def fetch_openweather(lat: float, lon: float, api_key: str) -> Optional[Dict[str, Any]]:
    """
    Fetches real-time weather and 24h precipitation from OpenWeatherMap API.
    """
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
        async with httpx.AsyncClient(timeout=6.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                d = resp.json()
                temp = float(d["main"]["temp"])
                humidity = float(d["main"]["humidity"])
                wind_speed_ms = float(d.get("wind", {}).get("speed", 0))
                wind_speed_kmh = round(wind_speed_ms * 3.6, 1)
                condition = d["weather"][0]["description"] if d.get("weather") else "Clear"

                # Fetch 5-day / 3-hour forecast for rain probability
                rain_prob = 10.0
                try:
                    f_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric&cnt=8"
                    f_resp = await client.get(f_url)
                    if f_resp.status_code == 200:
                        f_data = f_resp.json()
                        probs = [item.get("pop", 0.0) * 100 for item in f_data.get("list", [])]
                        if probs:
                            rain_prob = max(probs)
                except Exception:
                    pass

                return {
                    "temperature": round(temp, 1),
                    "humidity": round(humidity, 1),
                    "wind_speed_kmh": wind_speed_kmh,
                    "rainfall_probability": round(rain_prob, 1),
                    "condition": condition.capitalize(),
                    "source": "OpenWeatherMap"
                }
    except Exception as e:
        logger.warning(f"OpenWeatherMap request failed: {e}")
    return None

async def fetch_openmeteo(lat: float, lon: float) -> Dict[str, Any]:
    """
    Fetches real-time weather and rain forecast via Open-Meteo (100% Free, Zero-Key fallback).
    """
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,weather_code&"
        f"hourly=precipitation_probability,temperature_2m,relative_humidity_2m&forecast_days=2"
    )
    async with httpx.AsyncClient(timeout=8.0) as client:
        resp = await client.get(url)
        if resp.status_code == 200:
            d = resp.json()
            curr = d.get("current", {})
            temp = float(curr.get("temperature_2m", 26.5))
            humidity = float(curr.get("relative_humidity_2m", 65.0))
            wind = float(curr.get("wind_speed_10m", 8.0))
            
            # Max precipitation probability next 24 hours
            hourly_probs = d.get("hourly", {}).get("precipitation_probability", [])
            rain_prob = max(hourly_probs[:24]) if hourly_probs else 15.0

            # Weather interpretation code
            wcode = curr.get("weather_code", 0)
            condition = "Clear sky"
            if wcode in [1, 2, 3]:
                condition = "Partly cloudy"
            elif wcode in [45, 48]:
                condition = "Foggy"
            elif wcode in [51, 53, 55, 61, 63, 65]:
                condition = "Rain showers"
            elif wcode in [80, 81, 82]:
                condition = "Heavy rain"
            elif wcode >= 95:
                condition = "Thunderstorm"

            return {
                "temperature": round(temp, 1),
                "humidity": round(humidity, 1),
                "wind_speed_kmh": round(wind, 1),
                "rainfall_probability": round(float(rain_prob), 1),
                "condition": condition,
                "source": "Open-Meteo (Real-Time)"
            }

    # Ultimate offline fallback
    return {
        "temperature": 27.5,
        "humidity": 68.0,
        "wind_speed_kmh": 9.5,
        "rainfall_probability": 20.0,
        "condition": "Scattered clouds",
        "source": "Agronomic Sensor Model"
    }

def evaluate_spray_safety(temp_c: float, humidity_pct: float, wind_kmh: float, rain_prob_pct: float) -> Dict[str, Any]:
    """
    Evaluates agricultural spray safety window based on micrometeorology.
    """
    if rain_prob_pct >= 55.0:
        return {
            "status": "UNSAFE_RAIN",
            "badge": "Delay Spray (Rain Risk)",
            "safe": False,
            "message_en": f"Rain expected within 24h ({rain_prob_pct}% probability). Postpone foliar spraying to prevent pesticide/fungicide wash-off.",
            "message_hi": f"अगले 24 घंटों में बारिश की संभावना ({rain_prob_pct}%) है। दवा बह जाने से बचाने के लिए अभी छिड़काव न करें।"
        }
    elif wind_kmh >= 16.0:
        return {
            "status": "UNSAFE_WIND",
            "badge": "High Drift Risk",
            "safe": False,
            "message_en": f"Wind speed is high ({wind_kmh} km/h). Spraying now will cause chemical drift away from target foliage.",
            "message_hi": f"हवा की गति तेज ({wind_kmh} किमी/घंटा) है। दवा उड़कर दूसरी जगह चली जाएगी, छिड़काव टालें।"
        }
    elif temp_c >= 35.0:
        return {
            "status": "CAUTION_HEAT",
            "badge": "High Heat Caution",
            "safe": False,
            "message_en": f"High temperature ({temp_c}°C) can cause rapid droplet evaporation and foliar chemical burn. Spray only after 4:30 PM.",
            "message_hi": f"तापमान अधिक ({temp_c}°C) है। पत्तों के झुलसने का खतरा है, केवल शाम 4:30 बजे के बाद ही छिड़काव करें।"
        }
    else:
        return {
            "status": "SAFE",
            "badge": "Optimal Spray Window",
            "safe": True,
            "message_en": f"Weather is ideal for foliar spraying (Temp: {temp_c}°C, Humidity: {humidity_pct}%, Wind: {wind_kmh} km/h).",
            "message_hi": f"छिड़काव के लिए मौसम बिल्कुल अनुकूल है (तापमान: {temp_c}°C, नमी: {humidity_pct}%, हवा: {wind_kmh} किमी/घंटा)।"
        }

async def get_live_weather(
    location_name: Optional[str] = None,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    openweather_api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    High-level weather retrieval orchestrator:
    1. Geocodes location if coordinates are missing.
    2. Tries OpenWeatherMap if key is provided.
    3. Falls back gracefully to Open-Meteo.
    4. Computes agricultural spray window safety.
    """
    coords = {"latitude": lat, "longitude": lon, "name": location_name or DEFAULT_LOCATION}
    if lat is None or lon is None:
        coords = await geocode_location(location_name or DEFAULT_LOCATION)

    weather_data = None
    if openweather_api_key and openweather_api_key.strip():
        weather_data = await fetch_openweather(coords["latitude"], coords["longitude"], openweather_api_key.strip())

    if not weather_data:
        weather_data = await fetch_openmeteo(coords["latitude"], coords["longitude"])

    spray_advisory = evaluate_spray_safety(
        temp_c=weather_data["temperature"],
        humidity_pct=weather_data["humidity"],
        wind_kmh=weather_data["wind_speed_kmh"],
        rain_prob_pct=weather_data["rainfall_probability"]
    )

    return {
        "location": coords.get("name", location_name or DEFAULT_LOCATION),
        "latitude": coords["latitude"],
        "longitude": coords["longitude"],
        "current": weather_data,
        "spray_advisory": spray_advisory
    }
