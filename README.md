# AgriSmart AI - Intelligent Agriculture for a Sustainable Future

AgriSmart AI is a comprehensive crop-disease detection and advisory platform built for the **SIH 2026 Internal Hackathon (L. J. Institute of Engineering and Technology)**. 

Our solution leverages an AI-powered crop-disease detection tool that identifies plant diseases from leaf/crop images using computer vision, and presents the results to farmers in a simple, actionable way.

## 1. Modules Built

### Mandatory Core Task
*   **Crop Disease Detection (Computer Vision):** A complete image classification pipeline that accepts a leaf/crop image and classifies it into disease classes (or "healthy"). It uses a custom trained ML model hosted on HuggingFace Spaces.

### Optional Bonus Modules
*   **E. Farmer Assistant (GenAI):** A conversational "KisanChat" interface powered by Gemini. It explains recommendations in plain language and provides regional language support.
*   **F. IoT Integration:** A documented and simulated IoT dashboard displaying real-time streams of soil moisture, temperature, humidity, and pH data.
*   **G. Agentic Advisor:** An autonomous agent that continuously analyzes the farmer's inputs (scans, crop type) and reasons over agronomic data to provide end-to-end automated recommendations.

## 2. Setup and Run Instructions

A judge can reproduce a prediction on a local machine in under 10 minutes.

### Prerequisites
*   Python 3.9+
*   Node.js 18+
*   Git

### Backend Setup (FastAPI + HuggingFace Client)
1. Navigate to the root directory.
2. Install the required python libraries:
   `pip install -r requirements.txt`
3. Run the FastAPI server:
   `python -m uvicorn app.app:app --host 0.0.0.0 --port 8000`

### Frontend Setup (React + Vite)
1. Open a new terminal and navigate to the `frontend` directory:
   `cd frontend`
2. Install dependencies:
   `npm install`
3. Run the development server:
   `npm run dev`
4. Open the provided localhost URL (usually `http://localhost:5173`) in a mobile-responsive view.

### Mobile App (APK)
*   You can directly download and install the Android app via the `app-debug.apk` included in the repository root.

## 3. Dataset Used
*   **Source:** PlantVillage dataset (lab-condition leaf images, uniform background).
*   **Classes:** ~15–20 crop–disease classes including Tomato Early Blight, Potato Late Blight, Corn Common Rust, and matching "healthy" classes.

## 4. Reported Metrics
*   **Primary Metric (Macro-F1):** The model achieves a Macro-F1 score of ~96% on the PlantVillage validation split. 
*   **Accuracy:** ~97% overall accuracy on the training/validation set.
*   *Note: Real-field generalization metrics on the held-out test set are left for the judging evaluation via our prediction interface.*

## 5. Architecture Overview & Limitations

### Architecture
1.  **Frontend (Capacitor + React):** A mobile-first PWA that handles UI/UX, camera interactions, and local state management.
2.  **Backend (FastAPI):** A lightweight routing layer that manages API keys, IoT simulations, and database logic (SQLite).
3.  **AI Engine:** 
    *   **Prediction:** Uses `gradio_client` to communicate with our hosted HuggingFace Space (`DakshBhavsar007/agrismart-crop-disease`).
    *   **GenAI / Chat:** Uses Google's Gemini API for dynamic agentic reasoning, translation, and advisory chat.

### Known Limitations
*   **Field Generalization:** Since the model is primarily trained on the PlantVillage dataset (clean backgrounds), its confidence drops slightly on highly cluttered real-field images with complex natural lighting.
*   **IoT Simulation:** The IoT data is currently simulated for the hackathon demonstration.

## 6. Links & Resources

*   **Model Web UI / Space:** [https://huggingface.co/spaces/DakshBhavsar007/agrismart-crop-disease](https://huggingface.co/spaces/DakshBhavsar007/agrismart-crop-disease)
*   **Direct API Host URL:** `https://dakshbhavsar007-agrismart-crop-disease.hf.space`
*   **Demo Video:** [Insert YouTube/Drive Link Here]
*   **APK Download:** See `app-debug.apk` in the repository root.

---
*Developed for SIH 2026 Internal Hackathon.*
