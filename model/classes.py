"""
Canonical Class Definitions for AgriSmart AI (SIH 2026 Problem Statement 1)
Aligned with PlantVillage and PlantDoc shared classes (38 classes).
"""

PLANT_DISEASE_CLASSES = [
    "Apple___Apple_scab",
    "Apple___Black_rot",
    "Apple___Cedar_apple_rust",
    "Apple___healthy",
    "Blueberry___healthy",
    "Cherry_(including_sour)___Powdery_mildew",
    "Cherry_(including_sour)___healthy",
    "Corn_(maize)___Cercospora_leaf_spot_Gray_leaf_spot",
    "Corn_(maize)___Common_rust_",
    "Corn_(maize)___Northern_Leaf_Blight",
    "Corn_(maize)___healthy",
    "Grape___Black_rot",
    "Grape___Esca_(Black_Measles)",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)",
    "Grape___healthy",
    "Orange___Haunglongbing_(Citrus_greening)",
    "Peach___Bacterial_spot",
    "Peach___healthy",
    "Pepper,_bell___Bacterial_spot",
    "Pepper,_bell___healthy",
    "Potato___Early_blight",
    "Potato___Late_blight",
    "Potato___healthy",
    "Raspberry___healthy",
    "Soybean___healthy",
    "Squash___Powdery_mildew",
    "Strawberry___Leaf_scorch",
    "Strawberry___healthy",
    "Tomato___Bacterial_spot",
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Tomato___Leaf_Mold",
    "Tomato___Septoria_leaf_spot",
    "Tomato___Spider_mites_Two-spotted_spider_mite",
    "Tomato___Target_Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
    "Tomato___Tomato_mosaic_virus",
    "Tomato___healthy"
]

CLASS_TO_IDX = {cls_name: i for i, cls_name in enumerate(PLANT_DISEASE_CLASSES)}
IDX_TO_CLASS = {i: cls_name for i, cls_name in enumerate(PLANT_DISEASE_CLASSES)}

def parse_class_label(label: str):
    """
    Parses a class string like 'Tomato___Early_blight' into (plant, disease, is_healthy).
    """
    if "___" in label:
        parts = label.split("___", 1)
        plant = parts[0].replace("_", " ").replace("(", "").replace(")", "").strip()
        disease = parts[1].replace("_", " ").strip()
    else:
        plant = "Crop"
        disease = label.replace("_", " ").strip()

    is_healthy = "healthy" in label.lower()
    return plant, disease, is_healthy
