import os
import json
import logging
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any, List
from datetime import datetime

from pydantic import BaseModel
from fastapi import FastAPI, UploadFile, File, Form, Query, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Model Engine (Plug-and-play adapter layer for teammate & default model)
from model_engine.engine import predict_crop_disease, get_model_engine
from model_engine.config import ACTIVE_ADAPTER, TEAMMATE_ONNX_PATH, TEAMMATE_LABELS_PATH

# Database & Services
from db.database import (
    init_db,
    get_setting,
    set_setting,
    get_all_settings,
    save_settings_bulk,
    get_farm_profile,
    update_farm_profile,
    save_scan,
    get_scans,
    delete_scan,
    clear_all_scans,
    save_chat_message,
    get_chat_history
)
from services.weather import get_live_weather, evaluate_spray_safety
from services.agent import generate_dynamic_remedy, run_conversational_agent
from app.services.crop_recommendation import recommend_crop
from app.services.advisory import (
    calculate_irrigation,
    calculate_weather_disease_risk,
    compute_sustainability_score,
    generate_farmer_assistant_reply,
    run_agentic_advisor_cycle,
    get_simulated_iot_telemetry
)

logger = logging.getLogger("agrismart.app")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite database on startup
    await init_db()
    logger.info("AgriSmart AI SQLite database initialized.")
    yield

app = FastAPI(
    title="AgriSmart AI — Intelligent Agriculture Platform",
    description="Dual-model crop disease detection, NVIDIA NIM AI advisory agent, live weather risk assessment, and plug-and-play ONNX model engine",
    version="2.5.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return "AgriSmart AI Server Running. Navigate to /docs for API schema."

# ─── CORE TASK: PLUG-AND-PLAY CROP DISEASE DIAGNOSIS ───
@app.post("/predict")
@app.post("/api/predict")
async def predict_endpoint(
    file: UploadFile = File(...),
    crop_hint: Optional[str] = Form(None),
    crop: Optional[str] = Form(None),
    soil_type: Optional[str] = Form(None),
    location: Optional[str] = Form(None)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be an image.")

    scan_id = f"scan-{int(datetime.now().timestamp() * 1000)}"
    temp_path = f"temp_upload_{scan_id}_{file.filename}"

    try:
        content = await file.read()
        with open(temp_path, "wb") as f:
            f.write(content)
        
        # Save last test image for debugging/verification
        os.makedirs("data", exist_ok=True)
        with open("data/last_test_image.jpg", "wb") as f:
            f.write(content)

        # 1. Run Plug-and-Play Model Engine
        effective_hint = crop_hint or crop
        model_pred = predict_crop_disease(temp_path, crop_hint=effective_hint)

        # 2. Retrieve Farm Profile & API Key from SQLite
        farm_profile = await get_farm_profile()
        farm_loc = location or farm_profile.get("farm_location", "Pune, Maharashtra")
        farm_soil = soil_type or farm_profile.get("soil_type", "Loamy")

        nvidia_key = await get_setting("nvidia_api_key")
        deepseek_key = await get_setting("deepseek_api_key")
        openweather_key = await get_setting("openweather_api_key")
        chosen_ai_key = nvidia_key or deepseek_key

        # 3. Retrieve Real-Time Weather Context (Open-Meteo zero-key fallback)
        weather_ctx = await get_live_weather(
            location_name=farm_loc,
            lat=farm_profile.get("latitude"),
            lon=farm_profile.get("longitude"),
            openweather_api_key=openweather_key
        )

        # 4. Generate Dynamic Remedies via NVIDIA NIM (or offline agronomic knowledge base)
        remedy_data = await generate_dynamic_remedy(
            plant=model_pred.plant,
            disease=model_pred.disease,
            weather_ctx=weather_ctx,
            soil_type=farm_soil,
            api_key=chosen_ai_key
        )

        # 5. Synthesize Environmental Spray Advice
        curr_w = weather_ctx.get("current", {})
        spray = weather_ctx.get("spray_advisory", {})
        env_advice = (
            f"Local farm conditions in {weather_ctx['location']}: "
            f"Temp {curr_w.get('temperature')}°C, Humidity {curr_w.get('humidity')}%, "
            f"Rain chance {curr_w.get('rainfall_probability')}%. "
            f"{spray.get('message_en', '')}"
        )

        # 6. Format Complete Unified Diagnosis Response
        is_healthy = model_pred.is_healthy
        clean_disease_name = model_pred.disease.replace("___", " - ").replace("_", " ")

        diagnosis_result = {
            "id": scan_id,
            "timestamp": datetime.now().isoformat(),
            "imageUrl": f"/static/scans/{file.filename}" if os.path.exists(STATIC_DIR) else file.filename,
            "plant": model_pred.plant,
            "plantName": model_pred.plant,
            "disease": model_pred.disease,
            "diseaseName": f"{model_pred.plant} (Healthy)" if is_healthy else clean_disease_name,
            "confidence": round(model_pred.confidence, 4),
            "tier": model_pred.tier,
            "tierLabel": model_pred.tier_label,
            "isHealthy": is_healthy,
            "status": "Healthy" if is_healthy else "Infected",
            "whyItHappens": {
                "pathogen": remedy_data.get("pathogen", "Identified Pathogen"),
                "favorableConditions": remedy_data.get("favorable_conditions", f"Temperature around {curr_w.get('temperature', 26)}°C and high humidity."),
                "biology": remedy_data.get("biology", "Characteristic leaf infection observed on foliar surfaces.")
            },
            "remedies": {
                "organic": remedy_data.get("organic_remedies", []),
                "chemical": remedy_data.get("chemical_remedies", []),
                "cultural": remedy_data.get("cultural_remedies", [])
            },
            "sprayAdvisory": remedy_data.get("spray_window_advice", spray.get("message_en", "")),
            "environmentalAdvice": env_advice,
            "top3": model_pred.top3,
            "top3Candidates": model_pred.top3,
            "sourceAdapter": model_pred.adapter_source,
            "liveWeather": weather_ctx
        }

        # 7. Asynchronously Persist Scan to SQLite Database
        try:
            await save_scan(diagnosis_result)
        except Exception as db_err:
            logger.warning(f"Failed to persist scan to SQLite: {db_err}")

        return diagnosis_result

    except Exception as e:
        logger.error(f"Prediction error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass

# ─── WEATHER & SPRAY WINDOW ADVISORY ───
@app.get("/api/weather")
async def get_weather_endpoint(
    location: Optional[str] = Query(None),
    lat: Optional[float] = Query(None),
    lon: Optional[float] = Query(None)
):
    """
    Returns live weather, precipitation probability, and agricultural spray safety advisory.
    Uses OpenWeatherMap if key is stored, or falls back to Open-Meteo (zero-key guarantee).
    """
    farm = await get_farm_profile()
    target_loc = location or farm.get("farm_location", "Pune, Maharashtra")
    target_lat = lat or farm.get("latitude")
    target_lon = lon or farm.get("longitude")
    ow_key = await get_setting("openweather_api_key")

    weather_data = await get_live_weather(
        location_name=target_loc,
        lat=target_lat,
        lon=target_lon,
        openweather_api_key=ow_key
    )
    return weather_data

# ─── SETTINGS & FARM PROFILE (BYOK & STORAGE) ───
class SettingsPayload(BaseModel):
    nvidia_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    deepseek_api_key: Optional[str] = None
    openweather_api_key: Optional[str] = None
    ai_model: Optional[str] = "deepseek-ai/deepseek-v3"
    farmer_name: Optional[str] = None
    farm_location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    primary_crop: Optional[str] = None
    soil_type: Optional[str] = None
    irrigation_type: Optional[str] = None
    language: Optional[str] = "en"
    dark_mode: Optional[bool] = None

@app.get("/api/settings")
async def get_settings_endpoint():
    """Returns stored application settings and farm profile."""
    all_s = await get_all_settings()
    profile = await get_farm_profile()
    return {
        "settings": {
            "nvidia_api_key": all_s.get("nvidia_api_key", ""),
            "deepseek_api_key": all_s.get("deepseek_api_key", ""),
            "gemini_api_key": all_s.get("gemini_api_key", ""),
            "openweather_api_key": all_s.get("openweather_api_key", ""),
            "ai_model": all_s.get("ai_model", "deepseek-ai/deepseek-v3"),
            "language": all_s.get("language", "en"),
            "dark_mode": all_s.get("dark_mode", "false") == "true"
        },
        "farm_profile": profile
    }

@app.post("/api/settings")
async def save_settings_endpoint(payload: SettingsPayload):
    """Updates API keys, model preferences, and farm profile in SQLite."""
    settings_dict = {}
    if payload.nvidia_api_key is not None:
        settings_dict["nvidia_api_key"] = payload.nvidia_api_key
    if payload.deepseek_api_key is not None:
        settings_dict["deepseek_api_key"] = payload.deepseek_api_key
    if payload.gemini_api_key is not None:
        settings_dict["gemini_api_key"] = payload.gemini_api_key
    if payload.openweather_api_key is not None:
        settings_dict["openweather_api_key"] = payload.openweather_api_key
    if payload.ai_model is not None:
        settings_dict["ai_model"] = payload.ai_model
    if payload.language is not None:
        settings_dict["language"] = payload.language
    if payload.dark_mode is not None:
        settings_dict["dark_mode"] = str(payload.dark_mode).lower()

    if settings_dict:
        await save_settings_bulk(settings_dict)

    farm_dict = {}
    for f in ["farmer_name", "farm_location", "latitude", "longitude", "primary_crop", "soil_type", "irrigation_type"]:
        val = getattr(payload, f)
        if val is not None:
            farm_dict[f] = val

    if farm_dict:
        await update_farm_profile(farm_dict)

    return {"status": "success", "message": "Settings and farm profile updated successfully in SQLite."}

# ─── SCAN HISTORY ENDPOINTS ───
@app.get("/api/history")
async def get_history_endpoint(limit: int = 50, offset: int = 0):
    """Fetches past scans from SQLite database."""
    scans = await get_scans(limit=limit, offset=offset)
    return {"count": len(scans), "scans": scans}

@app.delete("/api/history/{scan_id}")
async def delete_history_item(scan_id: str):
    """Deletes a single scan by ID."""
    await delete_scan(scan_id)
    return {"status": "success", "deleted_id": scan_id}

@app.delete("/api/history")
async def clear_all_history():
    """Clears all scan history from SQLite."""
    await clear_all_scans()
    return {"status": "success", "message": "All scan history cleared."}

# ─── KISAN AI ASSISTANT (TOOL-CALLING AGENT) ───
class ChatRequest(BaseModel):
    query: str
    crop: Optional[str] = "Tomato"
    disease: Optional[str] = "Early Blight"
    session_id: Optional[str] = "default"
    language: Optional[str] = "en"

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    """
    Multi-turn conversational assistant using NVIDIA NIM tool calling architecture.
    Automatically queries weather, irrigation formulas, and dosages when needed.
    """
    # 1. Fetch user API keys and farm profile from SQLite
    nvidia_key = await get_setting("nvidia_api_key")
    deepseek_key = await get_setting("deepseek_api_key")
    gemini_key = await get_setting("gemini_api_key")
    chosen_key = gemini_key or nvidia_key or deepseek_key
    ai_model = await get_setting("ai_model", "deepseek-ai/deepseek-v3")

    farm = await get_farm_profile()

    # 2. Fetch past conversation turns for session
    past_messages = await get_chat_history(session_id=req.session_id, limit=6)
    history_formatted = [
        {"role": m["sender"], "content": m["text"]}
        for m in past_messages
    ]

    # 3. Save user message to SQLite
    await save_chat_message(
        sender="user",
        text=req.query,
        session_id=req.session_id or "default"
    )

    # 4. Invoke Tool-Calling Agent Loop
    ow_key = await get_setting("openweather_api_key")
    agent_res = await run_conversational_agent(
        user_query=req.query,
        crop=req.crop or farm.get("primary_crop", "Tomato"),
        disease=req.disease or "Healthy",
        farm_location=farm.get("farm_location", "Pune, Maharashtra"),
        soil_type=farm.get("soil_type", "Loamy"),
        language=req.language or "en",
        api_key=chosen_key,
        model_name=ai_model,
        history=history_formatted,
        openweather_key=ow_key
    )

    # 5. Save assistant reply to SQLite
    await save_chat_message(
        sender="assistant",
        text=agent_res.get("answer_en", ""),
        text_hi=agent_res.get("answer_hi"),
        tool_calls=agent_res.get("tool_calls_performed"),
        session_id=req.session_id or "default"
    )

    return agent_res

# ─── MODEL STATUS & ADAPTER INTROSPECTION ───
@app.get("/api/model-status")
async def get_model_status():
    """
    Provides plug-and-play status for teammate:
    Shows whether Teammate ONNX model is loaded or if default engine is active.
    """
    engine = get_model_engine()
    teammate_weights_exist = os.path.exists(TEAMMATE_ONNX_PATH)
    teammate_labels_exist = os.path.exists(TEAMMATE_LABELS_PATH)

    return {
        "active_adapter": ACTIVE_ADAPTER,
        "is_ready": engine.is_ready(),
        "teammate_ready": teammate_weights_exist and teammate_labels_exist,
        "details": {
            "teammate_onnx_path": TEAMMATE_ONNX_PATH,
            "teammate_onnx_found": teammate_weights_exist,
            "teammate_labels_path": TEAMMATE_LABELS_PATH,
            "teammate_labels_found": teammate_labels_exist,
        },
        "instructions": (
            "To switch to your teammate's model: "
            "1. Place your model file at 'model_engine/weights/teammate_model.onnx'. "
            "2. Place your labels JSON at 'model_engine/weights/labels.json'. "
            "3. Set ACTIVE_ADAPTER = 'teammate' in 'model_engine/config.py'."
        )
    }

# ─── PRESERVED AGRONOMIC MODULES ───
class CropRecommendRequest(BaseModel):
    nitrogen: float = 90.0
    phosphorus: float = 42.0
    potassium: float = 43.0
    temperature: float = 20.8
    humidity: float = 82.0
    ph: float = 6.5
    rainfall: float = 202.9

@app.post("/api/recommend-crop")
async def recommend_crop_endpoint(req: CropRecommendRequest):
    try:
        res = recommend_crop(
            n=req.nitrogen,
            p=req.phosphorus,
            k=req.potassium,
            temperature=req.temperature,
            humidity=req.humidity,
            ph=req.ph,
            rainfall=req.rainfall
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class IrrigationRequest(BaseModel):
    soil_moisture: float = 24.0
    crop_type: str = "Tomato"
    growth_stage: str = "mid"
    rain_prob_next24h: float = 20.0
    temperature: float = 28.0

@app.post("/api/irrigation-advice")
async def irrigation_endpoint(req: IrrigationRequest):
    return calculate_irrigation(
        soil_moisture=req.soil_moisture,
        crop_type=req.crop_type,
        growth_stage=req.growth_stage,
        rain_prob_next24h=req.rain_prob_next24h,
        temp_c=req.temperature
    )

class WeatherRiskRequest(BaseModel):
    temperature: float = 26.0
    humidity: float = 85.0
    rain_hours: float = 4.0

@app.post("/api/weather-risk")
async def weather_risk_endpoint(req: WeatherRiskRequest):
    return calculate_weather_disease_risk(
        temp_c=req.temperature,
        humidity_pct=req.humidity,
        rain_hours=req.rain_hours
    )

class SustainabilityRequest(BaseModel):
    water_saved_pct: float = 25.0
    chemical_reduction_pct: float = 35.0
    organic_matter_pct: float = 3.5
    monitoring_freq_days: int = 2

@app.post("/api/sustainability-score")
async def sustainability_endpoint(req: SustainabilityRequest):
    return compute_sustainability_score(
        water_saved_pct=req.water_saved_pct,
        chemical_reduction_pct=req.chemical_reduction_pct,
        organic_matter_pct=req.organic_matter_pct,
        monitoring_freq_days=req.monitoring_freq_days
    )

@app.get("/api/iot-telemetry")
async def iot_telemetry_endpoint():
    return get_simulated_iot_telemetry()

class AgenticCycleRequest(BaseModel):
    sensor_data: dict
    forecast_data: dict
    crop_status: dict

@app.post("/api/agentic-cycle")
async def agentic_cycle_endpoint(req: AgenticCycleRequest):
    return run_agentic_advisor_cycle(
        sensor_data=req.sensor_data,
        forecast_data=req.forecast_data,
        crop_status=req.crop_status
    )

if __name__ == "__main__":
    uvicorn.run("app.app:app", host="0.0.0.0", port=8000, reload=True)
