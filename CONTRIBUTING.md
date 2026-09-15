# Contributing to AgriSmart AI

Thank you for your interest in contributing to **AgriSmart AI**! We welcome bug fixes, documentation improvements, new crop-disease models, and agronomic algorithm enhancements.

---

## Code of Conduct

We are committed to providing a welcoming, inclusive, and harassment-free environment for all contributors. Please treat fellow contributors with respect and professionalism.

---

## How to Contribute

### 1. Fork and Clone
```bash
git clone https://github.com/your-username/agrismart.git
cd agrismart
```

### 2. Set Up Virtual Environment
```bash
python -m venv venv
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

pip install -r requirements.txt
```

### 3. Create a Feature Branch
```bash
git checkout -b feat/your-feature-name
```

### 4. Code Standards & Guidelines
- **Python Backend:** Follow PEP 8 guidelines. Write type hints (`typing`) wherever applicable.
- **Model Engine:** Ensure custom models implement `BaseModelAdapter` in `model_engine/base.py` and return valid `ModelPrediction` objects.
- **Prediction CLI:** Keep `model/predict.py` interface compliant with Section 4.1 (`predict(image_path) -> class_label`).
- **Frontend:** Format TypeScript code cleanly, ensure responsive design across mobile and desktop viewport widths.

### 5. Run Compliance & Automated Tests
Before submitting a PR, verify that all test suites pass:
```bash
python test_sih_compliance.py
```

### 6. Submit a Pull Request
1. Commit your changes with clear, conventional commit messages (`feat: ...`, `fix: ...`, `docs: ...`).
2. Push your branch to GitHub:
   ```bash
   git push origin feat/your-feature-name
   ```
3. Open a Pull Request on the main repository describing:
   - Summary of changes
   - Issue/feature addressed
   - Testing steps and verification evidence
