import os
import json
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import pickle

# Crop profile reference dataset representing standard N-P-K, temp, humidity, pH, rainfall distributions
# Derived from authoritative Kaggle Crop Recommendation Dataset
CROP_DATA_SYNTHESIS = {
    "rice": {"N": (60, 100), "P": (35, 60), "K": (35, 45), "temp": (20, 27), "hum": (80, 85), "ph": (5.0, 6.5), "rain": (200, 300)},
    "maize": {"N": (60, 100), "P": (35, 60), "K": (15, 25), "temp": (18, 27), "hum": (55, 75), "ph": (5.5, 7.0), "rain": (60, 100)},
    "chickpea": {"N": (20, 60), "P": (55, 80), "K": (75, 85), "temp": (17, 20), "hum": (15, 20), "ph": (6.0, 8.5), "rain": (65, 95)},
    "kidneybeans": {"N": (15, 40), "P": (55, 80), "K": (15, 25), "temp": (15, 24), "hum": (18, 25), "ph": (5.5, 6.0), "rain": (60, 150)},
    "pigeonpeas": {"N": (15, 40), "P": (55, 75), "K": (18, 25), "temp": (20, 35), "hum": (30, 65), "ph": (4.5, 7.5), "rain": (90, 198)},
    "mothbeans": {"N": (15, 40), "P": (35, 60), "K": (15, 25), "temp": (24, 32), "hum": (40, 65), "ph": (3.5, 9.5), "rain": (30, 75)},
    "mungbean": {"N": (15, 40), "P": (35, 60), "K": (15, 25), "temp": (27, 30), "hum": (80, 90), "ph": (6.2, 7.2), "rain": (35, 60)},
    "blackgram": {"N": (35, 60), "P": (55, 80), "K": (18, 25), "temp": (25, 35), "hum": (60, 70), "ph": (6.5, 7.5), "rain": (60, 75)},
    "lentil": {"N": (15, 40), "P": (55, 80), "K": (15, 25), "temp": (18, 30), "hum": (60, 70), "ph": (5.9, 7.8), "rain": (35, 55)},
    "pomegranate": {"N": (15, 40), "P": (10, 30), "K": (35, 45), "temp": (18, 25), "hum": (85, 95), "ph": (5.5, 7.2), "rain": (100, 115)},
    "banana": {"N": (80, 120), "P": (70, 95), "K": (45, 55), "temp": (25, 30), "hum": (75, 85), "ph": (5.5, 6.5), "rain": (90, 120)},
    "mango": {"N": (15, 40), "P": (15, 35), "K": (25, 35), "temp": (27, 36), "hum": (45, 55), "ph": (4.5, 7.0), "rain": (90, 105)},
    "grapes": {"N": (15, 40), "P": (120, 145), "K": (195, 205), "temp": (8, 42), "hum": (80, 85), "ph": (5.5, 6.5), "rain": (65, 75)},
    "watermelon": {"N": (80, 120), "P": (5, 30), "K": (45, 55), "temp": (24, 27), "hum": (80, 90), "ph": (6.0, 7.0), "rain": (40, 60)},
    "muskmelon": {"N": (80, 120), "P": (5, 30), "K": (45, 55), "temp": (27, 30), "hum": (90, 95), "ph": (6.0, 6.8), "rain": (20, 30)},
    "apple": {"N": (15, 40), "P": (120, 145), "K": (195, 205), "temp": (21, 24), "hum": (90, 95), "ph": (5.5, 6.5), "rain": (110, 125)},
    "orange": {"N": (15, 40), "P": (5, 30), "K": (5, 15), "temp": (15, 35), "hum": (90, 95), "ph": (6.0, 7.5), "rain": (100, 120)},
    "papaya": {"N": (40, 75), "P": (45, 70), "K": (45, 55), "temp": (23, 44), "hum": (90, 95), "ph": (6.5, 7.0), "rain": (140, 250)},
    "coconut": {"N": (15, 40), "P": (5, 30), "K": (25, 35), "temp": (25, 30), "hum": (95, 100), "ph": (5.5, 6.5), "rain": (130, 230)},
    "cotton": {"N": (100, 140), "P": (35, 60), "K": (15, 25), "temp": (22, 26), "hum": (75, 85), "ph": (6.0, 8.0), "rain": (60, 100)},
    "jute": {"N": (60, 100), "P": (35, 60), "K": (35, 45), "temp": (23, 27), "hum": (70, 90), "ph": (6.0, 7.5), "rain": (150, 200)},
    "coffee": {"N": (80, 120), "P": (15, 35), "K": (25, 35), "temp": (23, 28), "hum": (50, 70), "ph": (6.0, 7.5), "rain": (115, 200)}
}

_GLOBAL_MODEL = None

def get_or_train_model():
    global _GLOBAL_MODEL
    if _GLOBAL_MODEL is not None:
        return _GLOBAL_MODEL

    np.random.seed(42)
    X = []
    y = []

    for crop, ranges in CROP_DATA_SYNTHESIS.items():
        for _ in range(120):
            n = np.random.uniform(ranges["N"][0], ranges["N"][1])
            p = np.random.uniform(ranges["P"][0], ranges["P"][1])
            k = np.random.uniform(ranges["K"][0], ranges["K"][1])
            temp = np.random.uniform(ranges["temp"][0], ranges["temp"][1])
            hum = np.random.uniform(ranges["hum"][0], ranges["hum"][1])
            ph = np.random.uniform(ranges["ph"][0], ranges["ph"][1])
            rain = np.random.uniform(ranges["rain"][0], ranges["rain"][1])
            X.append([n, p, k, temp, hum, ph, rain])
            y.append(crop)

    X = np.array(X)
    y = np.array(y)
    clf = RandomForestClassifier(n_estimators=60, random_state=42)
    clf.fit(X, y)
    _GLOBAL_MODEL = clf
    return _GLOBAL_MODEL

def recommend_crop(n: float, p: float, k: float, temperature: float, humidity: float, ph: float, rainfall: float):
    model = get_or_train_model()
    features = np.array([[n, p, k, temperature, humidity, ph, rainfall]])
    probs = model.predict_proba(features)[0]
    classes = model.classes_

    top3_idx = np.argsort(probs)[::-1][:3]
    recommendations = []
    for idx in top3_idx:
        crop_name = classes[idx]
        confidence = round(float(probs[idx]) * 100, 2)
        recommendations.append({
            "crop": crop_name.capitalize(),
            "confidence": confidence,
            "suitability": "Highly Suitable" if confidence > 50 else "Moderately Suitable" if confidence > 20 else "Marginally Suitable"
        })

    primary = recommendations[0]
    return {
        "recommended_crop": primary["crop"],
        "confidence": primary["confidence"],
        "all_recommendations": recommendations,
        "input_parameters": {
            "nitrogen": n,
            "phosphorus": p,
            "potassium": k,
            "temperature": temperature,
            "humidity": humidity,
            "ph": ph,
            "rainfall": rainfall
        }
    }
