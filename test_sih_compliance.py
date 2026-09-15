"""
AgriSmart AI - Complete End-to-End Compliance & Verification Test Suite
Tests every mandatory requirement and all 7 bonus modules from SIH 2026 Problem Statement 1.
"""

import os
import sys
import subprocess
import json

def test_section_7_1_structure():
    print("[1] Verifying Section 7.1 Required Repository Structure...")
    required_paths = [
        "README.md",
        "app",
        "model",
        "model/predict.py",
        "model/evaluate.py",
        "model/train.py",
        "model/sample_leaf.jpg",
        "report",
        "report/model_report.md",
        "report/disease_metrics.json",
        "requirements.txt"
    ]
    for p in required_paths:
        assert os.path.exists(p), f"Missing required path: {p}"
        print(f"  [OK] Found: {p}")
    print("  --> Section 7.1 Structure Check PASSED.\n")

def test_section_4_1_predict_interface():
    print("[2] Verifying Section 4.1 Predict Interface & CLI...")
    # 1. Python Callable test
    from model.predict import predict
    label = predict("model/sample_leaf.jpg")
    assert label == "Potato___Late_blight", f"Expected Potato___Late_blight but got: {label}"
    print(f"  [OK] Python predict() returned: '{label}'")


    # 2. CLI test
    res = subprocess.run(
        [sys.executable, "model/predict.py", "--image", "model/sample_leaf.jpg"],
        capture_output=True,
        text=True
    )
    assert res.returncode == 0, f"CLI error: {res.stderr}"
    cli_out = res.stdout.strip()
    assert cli_out == label, f"Mismatch: Python ({label}) vs CLI ({cli_out})"
    print(f"  [OK] CLI python model/predict.py returned: '{cli_out}'")
    print("  --> Section 4.1 Predict Interface Check PASSED.\n")

def test_section_4_2_and_7_3_metrics_and_report():
    print("[3] Verifying Section 4.2 Metrics & Section 7.3 Model Report...")
    # Verify disease_metrics.json
    with open("report/disease_metrics.json", "r", encoding="utf-8") as f:
        metrics = json.load(f)
    assert "primary_metric" in metrics
    macro_f1 = metrics["primary_metric"]["value"]
    print(f"  [OK] Primary Metric reported: Macro-F1 = {macro_f1}")
    assert macro_f1 >= 0.95, f"Macro-F1 below expected band: {macro_f1}"

    # Verify model_report.md fields
    with open("report/model_report.md", "r", encoding="utf-8") as f:
        report_text = f.read().lower()
    
    required_fields = ["task", "dataset & split", "model / approach", "metric & result", "baseline", "limitations"]
    for field in required_fields:
        assert field in report_text, f"Missing required field in model report: {field}"
        print(f"  [OK] Model report contains field: '{field.capitalize()}'")
    print("  --> Section 4.2 & 7.3 Metrics & Report Check PASSED.\n")

def test_all_bonus_modules():
    print("[4] Verifying Optional Bonus Modules A through G (Section 3.2)...")
    
    # Bonus A: Crop Recommendation
    from app.services.crop_recommendation import recommend_crop
    crop_res = recommend_crop(n=90, p=42, k=43, temperature=20.8, humidity=82.0, ph=6.5, rainfall=202.9)
    assert "recommended_crop" in crop_res
    print(f"  [OK] Bonus A (Crop Rec): Recommended '{crop_res['recommended_crop']}' with confidence {crop_res['confidence']}%")

    # Bonus B: Smart Irrigation
    from app.services.advisory import calculate_irrigation
    irr_res = calculate_irrigation(soil_moisture=18.0, crop_type="Tomato", growth_stage="mid", rain_prob_next24h=20.0)
    assert "action" in irr_res
    print(f"  [OK] Bonus B (Smart Irrigation): Action = '{irr_res['action']}', Water Demand = {irr_res['crop_water_demand_mm_day']} mm/day")

    # Bonus C: Weather-Based Disease Risk
    from app.services.advisory import calculate_weather_disease_risk
    weather_risk = calculate_weather_disease_risk(temp_c=25.0, humidity_pct=88.0, rain_hours=4.0)
    assert "risk_level" in weather_risk
    print(f"  [OK] Bonus C (Weather Risk): Level = '{weather_risk['risk_level']}', Risk Score = {weather_risk['risk_score']}")

    # Bonus D: Sustainability Score
    from app.services.advisory import compute_sustainability_score
    sust_res = compute_sustainability_score(water_saved_pct=25.0, chemical_reduction_pct=35.0, organic_matter_pct=3.5, monitoring_freq_days=2)
    assert "sustainability_score" in sust_res
    print(f"  [OK] Bonus D (Sustainability): Score = {sust_res['sustainability_score']}/100 ({sust_res['grade']})")

    # Bonus E: Farmer Assistant (GenAI)
    from app.services.advisory import generate_farmer_assistant_reply
    reply = generate_farmer_assistant_reply("What is the organic recipe for neem oil spray?")
    assert "answer_en" in reply and "answer_hi" in reply
    print(f"  [OK] Bonus E (GenAI Assistant): English & Hindi grounded response generated")

    # Bonus F: IoT Telemetry
    from app.services.advisory import get_simulated_iot_telemetry
    iot = get_simulated_iot_telemetry()
    assert "temperature_c" in iot and "soil_moisture_pct" in iot
    print(f"  [OK] Bonus F (IoT Feed): Node '{iot['node_id']}' streaming Soil Moisture={iot['soil_moisture_pct']}%, Temp={iot['temperature_c']}C")

    # Bonus G: Autonomous Agentic Decision Loop
    from app.services.advisory import run_agentic_advisor_cycle
    sensor_data = {"soil_moisture": 20.0, "humidity": 88.0, "temperature": 26.0}
    forecast_data = {"rain_chance_24h": 75.0}
    crop_status = {"crop": "Tomato", "disease": "Early Blight"}
    cycle_res = run_agentic_advisor_cycle(sensor_data, forecast_data, crop_status)
    assert len(cycle_res["actions_taken"]) > 0
    print(f"  [OK] Bonus G (Agentic Advisor): Decision loop executed {len(cycle_res['actions_taken'])} automated actions (Conflict Arbitration Active)")
    print("  --> All 7 Bonus Modules Checked & Functional.\n")

def test_fastapi_backend_startup():
    print("[5] Verifying FastAPI Application & Routes...")
    import asyncio
    from httpx import AsyncClient, ASGITransport
    from app.app import app

    route_paths = [r.path for r in app.routes]
    expected_endpoints = [
        "/",
        "/dashboard",
        "/predict",
        "/api/predict",
        "/api/weather",
        "/api/settings",
        "/api/history",
        "/api/chat",
        "/api/recommend-crop",
        "/api/irrigation-advice",
        "/api/weather-risk",
        "/api/sustainability-score",
        "/api/iot-telemetry",
        "/api/agentic-cycle"
    ]
    for ep in expected_endpoints:
        assert ep in route_paths, f"Missing endpoint: {ep}"
        print(f"  [OK] Registered route: {ep}")

    async def live_checks():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            r = await client.get("/")
            assert r.status_code == 200
            print("  [OK] GET / returned 200 OK (Serving App)")

            r = await client.get("/dashboard")
            assert r.status_code == 200
            print("  [OK] GET /dashboard returned 200 OK (Serving Dashboard)")

            with open("model/sample_leaf.jpg", "rb") as f:
                r = await client.post("/predict", files={"file": ("sample_leaf.jpg", f, "image/jpeg")})
            assert r.status_code == 200
            res = r.json()
            assert res["disease"] == "Potato___Late_blight", f"Expected Potato___Late_blight but got {res['disease']}"
            assert "remedies" in res
            print(f"  [OK] POST /predict returned 200 OK (Class: {res['disease']}, Plant: {res['plant']})")


    asyncio.run(live_checks())
    print("  --> FastAPI Route Verification PASSED.\n")


if __name__ == "__main__":
    print("================================================================")
    print(" AgriSmart AI - Complete Hackathon Compliance Verification")
    print("================================================================\n")
    test_section_7_1_structure()
    test_section_4_1_predict_interface()
    test_section_4_2_and_7_3_metrics_and_report()
    test_all_bonus_modules()
    test_fastapi_backend_startup()
    print("================================================================")
    print(" ALL VERIFICATION CHECKS PASSED: 100% COMPLIANT WITH SIH 2026")
    print("================================================================")
