import os
import json
import logging
from typing import Optional, Dict, Any, List
from openai import AsyncOpenAI
from services.weather import get_live_weather, evaluate_spray_safety
from app.services.advisory import (
    calculate_irrigation,
    calculate_weather_disease_risk,
    generate_farmer_assistant_reply
)

logger = logging.getLogger("agrismart.agent")

NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
DEFAULT_MODEL = "deepseek-ai/deepseek-v3"
KIMI_MODEL = "moonshotai/kimi-k1.5"
DEEPSEEK_R1_MODEL = "deepseek-ai/deepseek-r1"

# Curated high-fidelity agronomic fallback database (offline guarantee)
OFFLINE_AGRI_KB: Dict[str, Dict[str, Any]] = {
    "Tomato___Early_blight": {
        "scientific_name": "Solanum lycopersicum (Fungal: Alternaria solani)",
        "pathogen": "Alternaria solani",
        "biology": "Produces circular to angular dark brown target-spots with concentric ridges on mature foliage, leading to premature chlorosis and defoliation.",
        "favorable_conditions": "Warm temperatures (24-29°C) accompanied by frequent dew, rain, or high canopy humidity above 75%.",
        "organic_remedies": [
            "Foliar spray of cold-pressed Neem Oil (1500 ppm) @ 5 ml/L + 2 ml mild liquid soap emulsifier every 6-7 days.",
            "Apply Trichoderma viride or Bacillus subtilis bio-fungicide foliar solution (5 g/L) during early morning.",
            "Dust foliage with wettable sulfur (80% WP) @ 2 g/L to arrest fungal conidia germination."
        ],
        "chemical_remedies": [
            "Foliar spray of Copper Oxychloride 50% WP @ 2.5 g/L water upon first lesion appearance.",
            "For active spreading blight, alternate with Mancozeb 75% WP @ 2.0 g/L or Azoxystrobin 23% SC @ 1.0 ml/L."
        ],
        "cultural_remedies": [
            "Prune and safely burn or bury all infected leaves within 15cm of soil level.",
            "Transition immediately from overhead sprinkler to drip irrigation to prevent spore splash.",
            "Rotate solanaceous crops with legumes, maize, or brassicas for 2 consecutive seasons."
        ]
    },
    "Tomato___Late_blight": {
        "scientific_name": "Solanum lycopersicum (Oomycete: Phytophthora infestans)",
        "pathogen": "Phytophthora infestans",
        "biology": "Aggressive water mold causing irregular water-soaked pale green lesions that turn purplish-brown. Distinct white fuzzy downy mildew develops on leaf undersides in cool damp weather.",
        "favorable_conditions": "Cool to moderate temperatures (15-22°C) and relative humidity > 85% for more than 10 consecutive hours.",
        "organic_remedies": [
            "Preventive spray of Bordeaux mixture (1% w/v copper sulfate + slaked lime) before seasonal rain showers.",
            "Copper hydroxide (Kocide 2000) @ 2.0 g/L as a protective bio-barrier."
        ],
        "chemical_remedies": [
            "Curative systemic spray: Cymoxanil 8% + Mancozeb 64% WP (Curzate) @ 2.5 g/L water.",
            "Metalaxyl-M 4% + Mancozeb 64% WP @ 2.5 g/L or Dimethomorph 50% WP @ 1.0 g/L."
        ],
        "cultural_remedies": [
            "Uproot and bury severely infected plants immediately away from irrigation canals.",
            "Increase plant row spacing to 75-90 cm to encourage wind penetration and solarization."
        ]
    },
    "Potato___Late_blight": {
        "scientific_name": "Solanum tuberosum (Oomycete: Phytophthora infestans)",
        "pathogen": "Phytophthora infestans",
        "biology": "Water-soaked dark lesions spreading rapidly across foliage and stems. Can cause total crop collapse within 7 to 10 days if unmanaged in damp microclimates.",
        "favorable_conditions": "High relative humidity (>80%) and temperatures between 16°C and 21°C.",
        "organic_remedies": [
            "Bordeaux mixture (10:10:100) applied at early canopy closure as protective shield.",
            "Liquid seaweed extract (Ascophyllum nodosum) @ 3 ml/L to stimulate systemic acquired resistance."
        ],
        "chemical_remedies": [
            "Curative foliar spray of Cymoxanil + Mancozeb @ 2.5 g/L water.",
            "Infinito (Fluopicolide + Propamocarb) @ 1.5 ml/L during high disease pressure."
        ],
        "cultural_remedies": [
            "High earthing-up (minimum 10-12 cm soil cover) to protect subterranean tubers from spore wash.",
            "Terminate irrigation 10-12 days prior to haulm destruction and harvest."
        ]
    },
    "Potato___Early_blight": {
        "scientific_name": "Solanum tuberosum (Fungal: Alternaria solani)",
        "pathogen": "Alternaria solani",
        "biology": "Target-board circular necrotic spots on older potato leaves. Lesions gradually merge causing yellowing and premature leaf senescence.",
        "favorable_conditions": "Alternating dry and wet periods with temperatures around 25-28°C.",
        "organic_remedies": [
            "Spray fermented cow urine (Gomutra 1:10) + Neem seed kernel extract (5%) weekly.",
            "Foliar spray with Trichoderma harzianum @ 5 g/L."
        ],
        "chemical_remedies": [
            "Chlorothalonil 75% WP @ 2 g/L or Mancozeb 75% WP @ 2.5 g/L.",
            "Difenoconazole 25% EC @ 0.5 ml/L for acute systemic control."
        ],
        "cultural_remedies": [
            "Balanced nitrogen fertilization; avoid excessive vegetative growth without potassium balance.",
            "Prompt destruction of crop residues after harvest."
        ]
    },
    "Corn_(maize)___Common_rust_": {
        "scientific_name": "Zea mays (Fungal: Puccinia sorghi)",
        "pathogen": "Puccinia sorghi",
        "biology": "Golden-brown to cinnamon powdery pustules breaking through leaf epidermal layers on both leaf surfaces, impeding photosynthesis.",
        "favorable_conditions": "Cool to moderate temperatures (16-24°C) with high relative humidity (>90%).",
        "organic_remedies": [
            "Spray 1% potassium bicarbonate solution with 0.1% horticultural mineral oil.",
            "Sour buttermilk (chaach) diluted 1:10 sprayed as a bio-fungal inhibitor."
        ],
        "chemical_remedies": [
            "Propiconazole 25% EC (Tilt) @ 1.0 ml/L at first visible pustule emergence.",
            "Azoxystrobin 18.2% + Difenoconazole 11.4% SC @ 1.0 ml/L."
        ],
        "cultural_remedies": [
            "Sow certified rust-resistant maize hybrids adapted to regional rainfall.",
            "Eliminate alternate weed hosts (Oxalis species) in field bunds."
        ]
    },
    "Apple___Apple_scab": {
        "scientific_name": "Malus domestica (Fungal: Venturia inaequalis)",
        "pathogen": "Venturia inaequalis",
        "biology": "Velvety olive-green to black crusty lesions on leaves and fruit, causing leaf curling, premature fruit drop, and fruit cracking.",
        "favorable_conditions": "Spring rains and extended leaf wetness for 9+ hours at 17-24°C.",
        "organic_remedies": [
            "Lime sulfur spray during silver tip to green tip bud growth stage.",
            "Serenade bio-fungicide (Bacillus subtilis) foliar application."
        ],
        "chemical_remedies": [
            "Captan 50% WP @ 2.5 g/L or Dodine 65% WP @ 1.0 g/L.",
            "Myclobutanil 10% WP @ 0.5 g/L or Difenoconazole 25% EC @ 0.4 ml/L."
        ],
        "cultural_remedies": [
            "Rake and shred fallen autumn leaves or apply 5% urea spray to accelerate decomposition.",
            "Prune inner orchard canopy annually to foster rapid drying after morning mist."
        ]
    }
}

def get_client(api_key: Optional[str] = None) -> Optional[AsyncOpenAI]:
    key = api_key or os.environ.get("NVIDIA_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not key or not key.strip():
        return None
    key = key.strip()
    
    if key.startswith("AIza"):
        # Gemini API Key (OpenAI Compatible Endpoint)
        return AsyncOpenAI(api_key=key, base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
    elif key.startswith("sk-"):
        return AsyncOpenAI(api_key=key)
    
    # If key starts with nvapi-, it is an NVIDIA NIM key
    base_url = NVIDIA_BASE_URL if key.startswith("nvapi-") else os.environ.get("OPENAI_BASE_URL", NVIDIA_BASE_URL)
    return AsyncOpenAI(api_key=key, base_url=base_url)

# ═══════════════════════════════════════════════════════════════════════
#   DYNAMIC REMEDY GENERATOR (NVIDIA NIM / DEEPSEEK / KIMI)
# ═══════════════════════════════════════════════════════════════════════
async def generate_dynamic_remedy(
    plant: str,
    disease: str,
    weather_ctx: Optional[Dict[str, Any]] = None,
    soil_type: str = "Loamy",
    api_key: Optional[str] = None,
    model_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generates precision biological explanation and actionable organic/chemical remedies.
    Uses NVIDIA NIM (DeepSeek / Kimi) when API key is provided, or curated agronomic knowledge base.
    """
    is_healthy = "healthy" in disease.lower() or "normal" in disease.lower()
    clean_disease = disease.replace("___", " - ").replace("_", " ").strip()
    key_variant = f"{plant.capitalize()}___{disease.split('___')[-1]}" if "___" in disease else disease

    # Check offline KB first for solid foundation
    norm_dis = disease.replace(" ", "_")
    key_variant = f"{plant.capitalize()}___{norm_dis.split('___')[-1]}"
    offline_data = (
        OFFLINE_AGRI_KB.get(key_variant) or 
        OFFLINE_AGRI_KB.get(f"{plant}___{norm_dis}") or
        OFFLINE_AGRI_KB.get(disease)
    )

    client = get_client(api_key)
    
    # Auto-correct model name based on API key type
    if api_key and client:
        if api_key.startswith("AIza") and "gemini" not in (model_name or "").lower():
            model_name = "gemini-2.5-flash"
        elif api_key.startswith("sk-") and "gpt" not in (model_name or "").lower():
            model_name = "gpt-4o-mini"

    if client and not is_healthy:
        try:
            weather_str = ""
            if weather_ctx:
                curr = weather_ctx.get("current", {})
                weather_str = f"Current Farm Weather: Temp {curr.get('temperature', 26)}°C, Humidity {curr.get('humidity', 70)}%, Wind {curr.get('wind_speed_kmh', 10)} km/h, Rain Prob {curr.get('rainfall_probability', 15)}%."

            system_prompt = (
                "You are Dr. AgriSmart, an expert Precision Plant Pathologist and Agronomist. "
                "The user will provide a crop and detected disease along with local weather and soil conditions. "
                "Respond ONLY with a valid, clean JSON object (no markdown quotes, no extra text) conforming to this exact structure:\n"
                "{\n"
                '  "pathogen": "Scientific name of pathogen",\n'
                '  "biology": "Detailed 2-sentence explanation of foliar pathology and how current weather/soil contributes",\n'
                '  "favorable_conditions": "Specific temperature, humidity, and leaf wetness ranges",\n'
                '  "organic_remedies": ["Specific organic recipe 1 with exact dosage (e.g. 5ml Neem / L)", "Recipe 2"],\n'
                '  "chemical_remedies": ["Specific chemical fungicide/bactericide with exact concentration (e.g. Mancozeb 75% WP @ 2g/L)", "Chemical 2"],\n'
                '  "cultural_remedies": ["Field sanitation, pruning, and spacing practice 1", "Practice 2"],\n'
                '  "spray_window_advice": "Actionable advice on whether to spray today considering rain probability and wind"\n'
                "}"
            )

            user_msg = (
                f"Crop: {plant}\n"
                f"Detected Condition: {clean_disease}\n"
                f"Soil Type: {soil_type}\n"
                f"{weather_str}"
            )

            chosen_model = model_name or DEFAULT_MODEL
            response = await client.chat.completions.create(
                model=chosen_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_msg}
                ],
                temperature=0.2,
                max_tokens=900,
                response_format={"type": "json_object"} if "deepseek" in chosen_model or "kimi" in chosen_model else None
            )

            raw_text = response.choices[0].message.content.strip()
            # Clean possible markdown wrapping
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.startswith("```"):
                raw_text = raw_text[3:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]

            parsed = json.loads(raw_text.strip())
            return {
                "pathogen": parsed.get("pathogen", "Identified Plant Pathogen"),
                "biology": parsed.get("biology", "Characteristic leaf tissue infection and vascular degradation."),
                "favorable_conditions": parsed.get("favorable_conditions", "High humidity and warm canopy temperature."),
                "organic_remedies": parsed.get("organic_remedies", []),
                "chemical_remedies": parsed.get("chemical_remedies", []),
                "cultural_remedies": parsed.get("cultural_remedies", []),
                "spray_window_advice": parsed.get("spray_window_advice", "Follow local spray window recommendations.")
            }
        except Exception as e:
            logger.warning(f"NVIDIA NIM Dynamic Remedy call failed: {e}. Falling back to agronomic knowledge base.")

    # Intelligent agronomic fallback
    if is_healthy:
        return {
            "pathogen": "None (Healthy Foliage)",
            "biology": f"Turgid, active photosynthetic cellular matrix with healthy chlorophyll density on {plant} leaf margins.",
            "favorable_conditions": "Optimal balanced vegetative growth.",
            "organic_remedies": [
                "Apply well-rotted vermicompost (250 g/plant) around the drip line every 4 weeks.",
                "Foliar spray of fermented Panchagavya (3% dilution) early morning as an organic growth tonic."
            ],
            "chemical_remedies": [
                "Maintain standard 19:19:19 water-soluble foliar fertilizer @ 3 g/L during vegetative phase."
            ],
            "cultural_remedies": [
                "Maintain uniform root zone moisture through regulated drip irrigation.",
                "Conduct routine weekly scouting for early sucking pest infestations."
            ],
            "spray_window_advice": "Foliar nutritional sprays can proceed under current calm weather."
        }

    if offline_data:
        return {
            "pathogen": offline_data["pathogen"],
            "biology": offline_data["biology"],
            "favorable_conditions": offline_data["favorable_conditions"],
            "organic_remedies": offline_data["organic_remedies"],
            "chemical_remedies": offline_data["chemical_remedies"],
            "cultural_remedies": offline_data["cultural_remedies"],
            "spray_window_advice": "Delay foliar treatment if rain is imminent within 24 hours."
        }

    # Generic robust disease fallback
    return {
        "pathogen": f"Pathogen affecting {plant}",
        "biology": f"Necrotic lesion spots and chlorotic halo observed on {plant} foliage under {soil_type} soil conditions.",
        "favorable_conditions": "Elevated moisture and stagnant canopy air.",
        "organic_remedies": [
            "Foliar spray with cold-pressed Neem Oil (1500 ppm) @ 5 ml/L with soap emulsifier weekly.",
            "Apply Trichoderma viride bio-fungicide @ 5 g/L near root collar."
        ],
        "chemical_remedies": [
            "Apply Copper Oxychloride 50% WP @ 2.5 g/L water upon lesion expansion."
        ],
        "cultural_remedies": [
            "Sanitize pruning tools with 70% isopropyl alcohol between plants.",
            "Thin dense lower foliage to promote air circulation."
        ],
        "spray_window_advice": "Spray during calm weather with wind speed below 15 km/h."
    }

# ═══════════════════════════════════════════════════════════════════════
#   TOOL-CALLING AGENT ARCHITECTURE (NVIDIA NIM / OPENAI)
# ═══════════════════════════════════════════════════════════════════════

AGENT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather_and_spray_window",
            "description": "Fetch real-time weather (temperature, humidity, wind, rainfall probability) and spray safety window for a given location or coordinates.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City or farm location (e.g. 'Nashik, Maharashtra', 'Pune')"
                    }
                },
                "required": ["location"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_irrigation_demand",
            "description": "Calculates crop water requirement and automated irrigation recommendation using FAO-56 Penman-Monteith logic.",
            "parameters": {
                "type": "object",
                "properties": {
                    "crop_type": {"type": "string", "description": "Name of crop, e.g. Tomato, Potato, Corn, Apple"},
                    "soil_moisture": {"type": "number", "description": "Current volumetric soil moisture percentage (e.g. 18.5)"},
                    "growth_stage": {"type": "string", "enum": ["initial", "mid", "late"], "description": "Crop growth stage"},
                    "rain_prob_next24h": {"type": "number", "description": "Rainfall probability in percentage (0-100)"}
                },
                "required": ["crop_type", "soil_moisture", "growth_stage"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_disease_risk_index",
            "description": "Computes fungal/bacterial disease outbreak risk index (0-100) based on canopy microclimate.",
            "parameters": {
                "type": "object",
                "properties": {
                    "temperature": {"type": "number", "description": "Ambient temperature in Celsius"},
                    "humidity": {"type": "number", "description": "Relative humidity percentage"},
                    "rain_hours": {"type": "number", "description": "Expected or observed rain hours"}
                },
                "required": ["temperature", "humidity"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_treatment_dosage",
            "description": "Returns exact measured dosages for organic (Neem, Trichoderma) and chemical (Mancozeb, Copper Oxychloride) crop treatments.",
            "parameters": {
                "type": "object",
                "properties": {
                    "crop": {"type": "string", "description": "Crop name"},
                    "disease": {"type": "string", "description": "Disease or pest name"},
                    "treatment_type": {"type": "string", "enum": ["organic", "chemical", "both"], "description": "Treatment category"}
                },
                "required": ["crop", "disease"]
            }
        }
    }
]

async def execute_tool_call(name: str, args: Dict[str, Any], openweather_key: Optional[str] = None) -> Dict[str, Any]:
    """Dispatches tool calls from the AI agent."""
    if name == "get_weather_and_spray_window":
        loc = args.get("location", "Pune, Maharashtra")
        w = await get_live_weather(location_name=loc, openweather_api_key=openweather_key)
        return {
            "location": w["location"],
            "temperature_c": w["current"]["temperature"],
            "humidity_pct": w["current"]["humidity"],
            "wind_kmh": w["current"]["wind_speed_kmh"],
            "rain_prob_24h": w["current"]["rainfall_probability"],
            "spray_status": w["spray_advisory"]["status"],
            "spray_message": w["spray_advisory"]["message_en"]
        }

    elif name == "calculate_irrigation_demand":
        res = calculate_irrigation(
            soil_moisture=float(args.get("soil_moisture", 22.0)),
            crop_type=args.get("crop_type", "Tomato"),
            growth_stage=args.get("growth_stage", "mid"),
            rain_prob_next24h=float(args.get("rain_prob_next24h", 20.0))
        )
        return res

    elif name == "calculate_disease_risk_index":
        res = calculate_weather_disease_risk(
            temp_c=float(args.get("temperature", 26.0)),
            humidity_pct=float(args.get("humidity", 80.0)),
            rain_hours=float(args.get("rain_hours", 2.0))
        )
        return res

    elif name == "get_treatment_dosage":
        crop = args.get("crop", "Tomato")
        dis = args.get("disease", "Early Blight")
        key = f"{crop}___{dis}".replace(" ", "_")
        kb = OFFLINE_AGRI_KB.get(key, OFFLINE_AGRI_KB.get("Tomato___Early_blight"))
        return {
            "crop": crop,
            "disease": dis,
            "organic_remedies": kb.get("organic_remedies", []),
            "chemical_remedies": kb.get("chemical_remedies", [])
        }

    return {"error": f"Unknown tool: {name}"}

async def run_conversational_agent(
    user_query: str,
    crop: str = "Tomato",
    disease: str = "Early Blight",
    farm_location: str = "Pune, Maharashtra",
    soil_type: str = "Loamy",
    language: str = "en",
    api_key: Optional[str] = None,
    model_name: Optional[str] = None,
    history: Optional[List[Dict[str, str]]] = None,
    openweather_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Autonomous tool-calling loop for Kisan AI Assistant.
    Supports multiple tool iterations when needed.
    """
    client = get_client(api_key)
    
    # Auto-correct model name based on API key type
    if api_key and client:
        if api_key.startswith("AIza") and "gemini" not in (model_name or "").lower():
            model_name = "gemini-2.5-flash"
        elif api_key.startswith("sk-") and "gpt" not in (model_name or "").lower():
            model_name = "gpt-4o-mini"


    # If no API key provided, fall back to grounded bilingual rules engine
    if not client:
        reply = generate_farmer_assistant_reply(
            user_query=user_query,
            current_crop=crop,
            detected_disease=disease
        )
        return {
            "answer_en": reply["answer_en"],
            "answer_hi": reply["answer_hi"],
            "tool_calls_performed": []
        }

    chosen_model = model_name or DEFAULT_MODEL

    system_prompt = (
        "You are AgriSmart Kisan AI, an expert autonomous agricultural assistant for farmers. "
        "You have access to tools for querying real-time weather, spray windows, irrigation calculations (FAO-56), "
        "disease risk indices, and treatment dosages. "
        "Always invoke relevant tools when the farmer asks about spraying, watering, weather, or treatments. "
        "Provide direct, compassionate, highly practical answers. "
        "Talk in English by default. Only talk in Hindi or Hinglish if the user explicitly asks for it."
    )
    messages = [{"role": "system", "content": system_prompt}]

    if history:
        for h in history[-4:]:
            content_val = h.get("content", "").strip()
            if content_val:
                messages.append({"role": h.get("role", "user"), "content": content_val})

    # Provide context
    messages.append({
        "role": "user",
        "content": (
            f"[FARM CONTEXT]\n"
            f"Crop: {crop}\n"
            f"Detected Disease: {disease}\n"
            f"Farm Location: {farm_location}\n"
            f"Soil: {soil_type}\n"
            f"[QUERY]: {user_query}"
        )
    })

    executed_tools = []
    max_tool_iterations = 4

    try:
        for _ in range(max_tool_iterations):
            response = await client.chat.completions.create(
                model=chosen_model,
                messages=messages,
                tools=AGENT_TOOLS,
                tool_choice="auto",
                temperature=0.3,
                max_tokens=1000
            )

            msg = response.choices[0].message
            messages.append(msg)

            if not msg.tool_calls:
                # Model finished reasoning and delivered final answer
                final_content = msg.content or ""
                return {
                    "answer_en": final_content,
                    "answer_hi": "",
                    "tool_calls_performed": executed_tools
                }

            # Execute tool calls
            for tc in msg.tool_calls:
                t_name = tc.function.name
                t_args = json.loads(tc.function.arguments or "{}")
                tool_result = await execute_tool_call(t_name, t_args, openweather_key)
                executed_tools.append({"tool": t_name, "args": t_args, "result": tool_result})

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps(tool_result)
                })

        # Max iterations reached, request final answer
        final_resp = await client.chat.completions.create(
            model=chosen_model,
            messages=messages,
            temperature=0.3,
            max_tokens=800
        )
        return {
            "answer_en": final_resp.choices[0].message.content,
            "answer_hi": "",
            "tool_calls_performed": executed_tools
        }

    except Exception as e:
        logger.warning(f"Agent tool-calling failed: {e}. Falling back to rules engine.")
        fallback = generate_farmer_assistant_reply(user_query, crop, disease)
        return {
            "answer_en": fallback["answer_en"],
            "answer_hi": fallback["answer_hi"],
            "tool_calls_performed": executed_tools,
            "error_fallback": str(e)
        }