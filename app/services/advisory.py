import math
import random
from datetime import datetime

# ═══════════════════════════════════════════════════════
#   BONUS MODULE B: SMART IRRIGATION ADVISORY (FAO-56)
# ═══════════════════════════════════════════════════════
CROP_KC = {
    "Tomato": {"initial": 0.6, "mid": 1.15, "late": 0.8},
    "Potato": {"initial": 0.5, "mid": 1.15, "late": 0.75},
    "Corn": {"initial": 0.4, "mid": 1.20, "late": 0.6},
    "Apple": {"initial": 0.5, "mid": 0.95, "late": 0.75},
    "Grape": {"initial": 0.3, "mid": 0.85, "late": 0.45},
    "Default": {"initial": 0.5, "mid": 1.0, "late": 0.7}
}

def calculate_irrigation(soil_moisture: float, crop_type: str, growth_stage: str, rain_prob_next24h: float, temp_c: float = 28.0):
    """
    FAO-56 Penman-Monteith inspired soil depletion & irrigation logic.
    - Field Capacity: ~35% volumetric
    - Wilting Point: ~15% volumetric
    - Readily Available Water threshold: ~22%
    """
    kc_dict = CROP_KC.get(crop_type, CROP_KC["Default"])
    kc = kc_dict.get(growth_stage.lower(), 1.0)

    # Reference Evapotranspiration estimate (Hargreaves formula simplification)
    et0 = 0.0023 * (temp_c + 17.8) * math.sqrt(max(1.0, temp_c - 15.0)) * 4.5
    crop_water_demand_mm = round(et0 * kc, 1)

    # Decision logic
    action = "NO_IRRIGATION"
    water_volume_liters_per_sqm = 0.0
    reason_en = ""
    reason_hi = ""

    if rain_prob_next24h >= 60:
        action = "DELAY_IRRIGATION"
        reason_en = f"Rain likely in next 24h ({rain_prob_next24h}% chance). Delay irrigation to prevent waterlogging and disease onset."
        reason_hi = f"अगले 24 घंटों में बारिश की संभावना ({rain_prob_next24h}%) है। जलभराव और फफूंद से बचने के लिए सिंचाई टालें।"
    elif soil_moisture < 20.0:
        action = "IRRIGATE_NOW"
        water_volume_liters_per_sqm = round(crop_water_demand_mm * 1.2, 1)
        reason_en = f"Soil moisture critically low ({soil_moisture}%). Apply {water_volume_liters_per_sqm} L/m² immediately to restore root zone moisture."
        reason_hi = f"मिट्टी की नमी बहुत कम ({soil_moisture}%) है। जड़ क्षेत्र की नमी बनाए रखने के लिए तुरंत {water_volume_liters_per_sqm} ली/वर्ग मी सिंचाई करें।"
    elif soil_moisture < 28.0 and rain_prob_next24h < 30:
        action = "SCHEDULE_IRRIGATION"
        water_volume_liters_per_sqm = round(crop_water_demand_mm, 1)
        reason_en = f"Moderate moisture ({soil_moisture}%). Schedule drip irrigation of {water_volume_liters_per_sqm} L/m² within 12 hours during early morning."
        reason_hi = f"नमी मध्यम ({soil_moisture}%) है। अगले 12 घंटों के भीतर सुबह के समय {water_volume_liters_per_sqm} ली/वर्ग मी ड्रिप सिंचाई करें।"
    else:
        action = "MAINTAIN"
        reason_en = f"Soil moisture is optimal ({soil_moisture}%). No irrigation required."
        reason_hi = f"मिट्टी में पर्याप्त नमी ({soil_moisture}%) है। अभी अतिरिक्त सिंचाई की आवश्यकता नहीं है।"

    return {
        "action": action,
        "soil_moisture_pct": soil_moisture,
        "crop_water_demand_mm_day": crop_water_demand_mm,
        "recommended_volume_L_sqm": water_volume_liters_per_sqm,
        "guidance_en": reason_en,
        "guidance_hi": reason_hi
    }

# ═══════════════════════════════════════════════════════
#   BONUS MODULE C: WEATHER-BASED DISEASE RISK INTELLIGENCE
# ═══════════════════════════════════════════════════════
def calculate_weather_disease_risk(temp_c: float, humidity_pct: float, rain_hours: float):
    """
    Computes fungal & bacterial disease vulnerability index (0 to 100).
    High risk: Temp 20-30°C and Humidity > 80% with prolonged leaf wetness.
    """
    temp_factor = 0.0
    if 18 <= temp_c <= 30:
        temp_factor = 1.0 - (abs(temp_c - 24.0) / 10.0)
    
    humidity_factor = max(0.0, (humidity_pct - 60.0) / 40.0)
    wetness_factor = min(1.0, rain_hours / 6.0)

    risk_score = round((0.4 * temp_factor + 0.4 * humidity_factor + 0.2 * wetness_factor) * 100, 1)

    if risk_score > 70:
        level = "HIGH"
        advisory_en = "High disease outbreak risk (favorable temperature & prolonged moisture). Inspect crops and apply preventive bio-fungicide (Trichoderma or copper oxychloride)."
        advisory_hi = "फसल में रोग फैलने का भारी खतरा है (अधिक नमी व अनुकूल तापमान)। तुरंत पत्तों की जांच करें और सुरक्षात्मक जैव-फफूंदनाशक का छिड़काव करें।"
    elif risk_score > 40:
        level = "MODERATE"
        advisory_en = "Moderate risk. Ensure field drainage and avoid sprinkler irrigation on leaf canopies."
        advisory_hi = "मध्यम जोखिम। खेत में जल निकासी सुनिश्चित करें और पत्तों पर सीधे पानी का छिड़काव न करें।"
    else:
        level = "LOW"
        advisory_en = "Favorable weather conditions with low fungal spore germination pressure."
        advisory_hi = "मौसम अनुकूल है, फफूंद व रोग फैलने का जोखिम न्यूनतम है।"

    return {
        "risk_level": level,
        "risk_score": risk_score,
        "conditions": {
            "temperature_c": temp_c,
            "humidity_pct": humidity_pct,
            "rain_duration_hours": rain_hours
        },
        "advisory_en": advisory_en,
        "advisory_hi": advisory_hi
    }

# ═══════════════════════════════════════════════════════
#   BONUS MODULE D: SUSTAINABILITY SCORE FORMULA
# ═══════════════════════════════════════════════════════
def compute_sustainability_score(water_saved_pct: float, chemical_reduction_pct: float, organic_matter_pct: float, monitoring_freq_days: int):
    """
    Transparent, reproducible formula:
    Sustainability Score (0-100) =
        0.35 * WaterEfficiencyScore
      + 0.30 * ChemicalReductionScore
      + 0.20 * SoilOrganicHealthScore
      + 0.15 * MonitoringDisciplineScore
    """
    # 1. Water efficiency (0-100): target 30%+ savings
    s_water = min(100.0, (water_saved_pct / 30.0) * 100.0)

    # 2. Chemical reduction (0-100): target 40%+ reduction
    s_chem = min(100.0, (chemical_reduction_pct / 40.0) * 100.0)

    # 3. Soil organic matter (0-100): ideal range 3.0% - 5.0%
    s_soil = min(100.0, (organic_matter_pct / 4.0) * 100.0)

    # 4. Monitoring discipline (0-100): inspecting every 1-3 days
    s_monitor = max(0.0, 100.0 - (monitoring_freq_days - 1) * 15.0)

    total_score = round(0.35 * s_water + 0.30 * s_chem + 0.20 * s_soil + 0.15 * s_monitor, 1)

    if total_score >= 80:
        grade = "A+ (Exemplary Eco-Farming)"
    elif total_score >= 65:
        grade = "B (Sustainable Practices Active)"
    else:
        grade = "C (Needs Resource Optimization)"

    return {
        "sustainability_score": total_score,
        "grade": grade,
        "breakdown": {
            "water_efficiency": round(s_water, 1),
            "chemical_reduction": round(s_chem, 1),
            "soil_health": round(s_soil, 1),
            "monitoring_discipline": round(s_monitor, 1)
        },
        "formula": "Score = 0.35 * WaterScore + 0.30 * ChemicalScore + 0.20 * SoilScore + 0.15 * MonitoringScore",
        "co2_reduction_estimate_kg": round(total_score * 4.2, 1)
    }

# ═══════════════════════════════════════════════════════
#   BONUS MODULE E & G: BILINGUAL ASSISTANT & AGENTIC ADVISOR
# ═══════════════════════════════════════════════════════
def generate_farmer_assistant_reply(user_query: str, current_crop: str = "Tomato", detected_disease: str = "Early Blight"):
    """
    Grounded, farmer-centric Q&A responding in simple terms with English and Hindi.
    """
    q_lower = user_query.lower()

    if "drip" in q_lower or "irrigation" in q_lower or "paani" in q_lower or "water" in q_lower:
        return {
            "answer_en": f"For {current_crop}, maintain moist but well-drained soil. Use drip irrigation directly near roots and avoid wetting foliage to stop fungal spread.",
            "answer_hi": f"{current_crop} की फसल में ड्रिप सिंचाई का प्रयोग करें। पत्तों पर पानी न गिरने दें ताकि फफूंद न फैले।"
        }
    elif "fertilizer" in q_lower or "khad" in q_lower or "npk" in q_lower:
        return {
            "answer_en": f"Balanced fertilization is vital. If foliage shows yellowing, apply vermicompost with bio-fertilizers (Azotobacter). Avoid excessive nitrogen during flowering.",
            "answer_hi": f"संतुलित खाद डालें। अगर पत्ते पीले पड़ रहे हैं, तो वर्मीकम्पोस्ट और जैव-उर्वरक डालें। फूल आने के समय अत्यधिक यूरिया (नाइट्रोजन) से बचें।"
        }
    elif "organic" in q_lower or "neem" in q_lower or "jaivik" in q_lower:
        return {
            "answer_en": f"Organic spray recipe: Mix 5ml cold-pressed Neem oil + 2ml mild liquid soap per 1 liter of water. Spray during late afternoon once every 7 days.",
            "answer_hi": f"जैविक कीटनाशक: 5 मिली नीम का तेल + 2 मिली शैम्पू प्रति 1 लीटर पानी में घोलें। शाम के समय हर 7 दिन में छिड़काव करें।"
        }
    else:
        return {
            "answer_en": f"Regarding your {current_crop} showing {detected_disease}: Ensure prompt removal of heavily spotted leaves and sanitize all pruning tools.",
            "answer_hi": f"आपकी {current_crop} की फसल में {detected_disease} की रोकथाम के लिए: रोगग्रस्त पत्तों को तुरंत काटकर नष्ट करें और उपकरणों को साफ रखें।"
        }

def run_agentic_advisor_cycle(sensor_data: dict, forecast_data: dict, crop_status: dict):
    """
    Autonomous decision loop:
    1. Ingest IoT telemetry + weather forecast + vision crop disease diagnosis
    2. Reason over conflict (e.g. low soil moisture vs high rain probability)
    3. Output prioritized autonomous actions
    """
    decisions = []

    # Check 1: Irrigation Conflict Resolution
    if sensor_data.get("soil_moisture", 30) < 22 and forecast_data.get("rain_chance_24h", 0) > 65:
        decisions.append({
            "domain": "Irrigation",
            "priority": "HIGH",
            "action": "OVERRIDE_VALVE_OFF",
            "explanation_en": "Soil is dry, but heavy rain is forecasted within 12 hours. Holding automated irrigation saved approximately 180 Liters of water and averted root rot.",
            "explanation_hi": "मिट्टी सूखी है परंतु 12 घंटे में भारी वर्षा होने वाली है। स्वचालित पंप को रोककर 180 लीटर पानी बचाया गया।"
        })
    elif sensor_data.get("soil_moisture", 30) < 18:
        decisions.append({
            "domain": "Irrigation",
            "priority": "CRITICAL",
            "action": "AUTO_DRIP_ENGAGED",
            "explanation_en": "Critically low root moisture. Auto-drip scheduled for 25 minutes.",
            "explanation_hi": "जड़ों की नमी गंभीर रूप से कम है। 25 मिनट के लिए ड्रिप शुरू किया गया।"
        })

    # Check 2: Microclimate Disease Alert
    if sensor_data.get("humidity", 60) > 85 and sensor_data.get("temperature", 25) > 22:
        decisions.append({
            "domain": "Disease Prevention",
            "priority": "WARNING",
            "action": "TRIGGER_PREVENTIVE_NOTIFICATION",
            "explanation_en": f"High humidity ({sensor_data.get('humidity')}%) detected in canopy. Automated warning issued to farmer for {crop_status.get('crop', 'Crop')} fungal prevention.",
            "explanation_hi": f"फसल के पास अत्यधिक नमी ({sensor_data.get('humidity')}%) पाई गई। फफूंद से बचाव की चेतावनी जारी की गई।"
        })

    return {
        "timestamp": datetime.now().isoformat(),
        "autonomous_status": "ACTIVE_MONITORING",
        "actions_taken": decisions,
        "energy_state": "OPTIMAL"
    }

# ═══════════════════════════════════════════════════════
#   BONUS MODULE F: SIMULATED IOT SENSOR STREAM
# ═══════════════════════════════════════════════════════
def get_simulated_iot_telemetry():
    """
    Produces realistic physical agricultural sensor telemetry.
    """
    hour = datetime.now().hour
    # Diurnal temperature cycle: coolest at dawn (hour 6), warmest at 14:00
    temp_base = 22.0 + 8.0 * math.sin(math.pi * (hour - 6) / 12) if 6 <= hour <= 18 else 20.0
    temp = round(temp_base + random.uniform(-1.2, 1.2), 1)

    # Inverted humidity cycle
    hum_base = 85.0 - (temp - 18.0) * 2.2
    hum = round(min(98.0, max(40.0, hum_base + random.uniform(-3.0, 3.0))), 1)

    moisture = round(random.uniform(22.0, 34.0), 1)
    ph = round(random.uniform(6.2, 6.8), 2)
    npk = {
        "nitrogen_ppm": random.randint(75, 110),
        "phosphorus_ppm": random.randint(38, 55),
        "potassium_ppm": random.randint(140, 185)
    }

    return {
        "node_id": "ESP32_AGRI_NODE_01",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "temperature_c": temp,
        "humidity_pct": hum,
        "soil_moisture_pct": moisture,
        "soil_ph": ph,
        "npk": npk,
        "battery_voltage": round(random.uniform(3.9, 4.2), 2),
        "status": "ONLINE"
    }
