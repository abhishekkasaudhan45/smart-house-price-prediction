# Spec: House Price Predictor — Phase 2 Upgrades

## Objective

Upgrade the house price prediction project from a basic EDA + single-model Flask demo into a production-quality ML portfolio piece with real metrics, multi-model comparison, deployed frontend, and professional documentation. Reframe as a **Smart Housing Price Predictor** to give it a local, original-data angle.

**User persona:** Recruiters / hiring managers evaluating ML portfolio projects.

**Success criteria:**
- Frontend deployed and accessible via Live Demo link
- Model comparison table showing R², RMSE, MAE across 4 models (Linear Regression, Random Forest, XGBoost, MLPRegressor)
- SHAP-based feature importance on the results page
- Prediction shown with confidence interval (±15%)
- Input validation and structured error handling on the API
- README with screenshots, metrics, and run instructions (framed as Smart predictor)
- API available and usable from the frontend

---

## Tech Stack

| Layer | Current | Target |
|---|---|---|
| ML Training | scikit-learn | + XGBoost, MLPRegressor |
| Backend | Flask + pickle | Same + SHAP + validation |
| Frontend | HTML/CSS/JS (not deployed) | Same + confidence interval UI + deployment |
| Deployment | Render (API only) | Render (API) + Vercel/Netlify (frontend) |
| Visualization | matplotlib/seaborn | + SHAP plots, model comparison chart |

**Dependencies to add:**
```
xgboost
shap
python-dotenv
```

---

## Commands

```bash
# Backend (development)
cd Backend_API
pip install -r requirements.txt
python app.py               # Starts Flask on port 10000

# Frontend (development)
cd Fronted_UI
# Open index.html directly or serve via:
npx serve .

# ML Training
cd ML_Training
jupyter notebook training.ipynb
```

---

## Project Structure (Target)

```
Backend_API/
├── app.py                       # Flask app with validation
├── model.pkl                    # Best model (Random Forest / XGBoost)
├── scaler.pkl
├── label_encoders.pkl
├── feature_columns.pkl
├── model_metrics.pkl            # All model comparison metrics (NEW)
├── feature_importance.png       # SHAP summary plot (NEW)
├── requirements.txt
└── .env

Fronted_UI/
├── index.html                   # Form + results with model comparison
├── style.css                    # Polished UI
├── script.js                    # Handles API calls, renders comparison table
└── assets/
    └── model_comparison.png     # Pre-generated comparison chart

ML_Training/
├── data.py                      # Synthetic data generator
├── house_data.csv               # 1000 houses
├── eda.ipynb                    # EDA notebook
├── training.ipynb               # Original training (Linear + RF)
└── advanced_training.ipynb      # NEW: 4-model comparison + SHAP

README.md                        # Full documentation
PRD.md                           # This spec
```

---

## Code Style

### Python (Flask API)
```python
@app.route("/predict", methods=["POST"])
def predict():
    errors = validate_input(request.json)
    if errors:
        return jsonify({"error": errors}), 422

    data = sanitize_input(request.json)
    features = engineer_features(data)
    scaled = scaler.transform([features])
    pred = model.predict(scaled)[0]
    ci = compute_confidence_interval(pred, model)

    return jsonify({
        "predicted_price": round(float(pred), 2),
        "confidence_interval": ci,
        "model_used": best_model_name,
        "model_metrics": MODEL_METRICS
    })
```

### JavaScript (Frontend)
```javascript
// API call with loading, error, and success states
async function getPrediction(formData) {
  showLoading(true);
  try {
    const res = await fetch(API_URL + "/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formData)
    });
    if (!res.ok) throw new Error((await res.json()).error || "Request failed");
    return await res.json();
  } catch (err) {
    showError(err.message);
  } finally {
    showLoading(false);
  }
}
```

### Naming conventions
- Python: `snake_case` for functions/variables, `PascalCase` for classes
- JS: `camelCase` for functions/variables
- HTML: `kebab-case` for IDs and classes
- API routes: lowercase, no trailing slashes

---

## Testing Strategy

| Level | Tool | Scope |
|---|---|---|
| API smoke test | Manual + curl | Each endpoint returns correct status + shape |
| Input validation | Manual | Each edge case (missing field, wrong type, out of range) returns 422 |
| Model comparison | Script | All 4 models train+eval without error |
| Frontend | Manual | Form submit → loading → result displays correctly |
| Deployment | URL check | Both API health and frontend load successfully |

No unit test framework for now — API surface is small. Add `pytest` if it grows beyond 5 endpoints.

---

## Phase 1: Immediate Upgrades (1-2 days)

### 1.1 Multi-Model Training Pipeline
- Train 4 models: Linear Regression, Random Forest, XGBoost, Neural Network (Keras, 2 hidden layers)
- Collect R², RMSE, MAE for each on test set
- Persist metrics to `model_metrics.pkl`
- Pick best model by RMSE, save as `model.pkl` as before
- Generate `model_comparison.png` (grouped bar chart)

**Files:** `ML_Training/advanced_training.ipynb`, `Backend_API/model_metrics.pkl`

### 1.2 SHAP Feature Importance
- Run SHAP on the best model
- Save summary plot to `Backend_API/feature_importance.png`
- Serve via new API endpoint: `GET /feature-importance` returns image URL

**Files:** `ML_Training/advanced_training.ipynb`, `Backend_API/app.py`

### 1.3 API Input Validation
Replace bare try/except with structured validation:
- Validate each field: type, range, required
- Return 422 with field-level error messages
- Sanitize and transform before model input

**Files:** `Backend_API/app.py`

### 1.4 API Metrics Endpoint
- `GET /metrics` returns model comparison table data
- Frontend fetches and renders this

**Files:** `Backend_API/app.py`

### 1.5 Frontend Deploy + Polish
- Deploy `Fronted_UI/` to Vercel
- Add confidence interval display to results card (±15% band)
- Add model comparison table below the form
- Add input validation on client side (mirrors backend)
- CSS: loading skeleton, error states, responsive polish
- Reframe as "Smart House Price Predictor" in branding text

**Files:** `Fronted_UI/index.html`, `Fronted_UI/style.css`, `Fronted_UI/script.js`

### 1.6 README Rewrite
- Project description with screenshot
- Model comparison table (R², RMSE, MAE)
- Dataset description and size
- How to run locally (backend + frontend)
- Live Demo link
- Tech stack badges

**Files:** `README.md`

---

## Phase 2: Stronger Upgrade (1 week)

### 2.1 Real Dataset from Smart/Noida
- Scrape property listings from 99acres / Magicbricks for Smart and Noida
- Clean and structure into training CSV
- Retrain all models on real data
- Compare performance vs synthetic data

**Files:** `ML_Training/scraper.py`, `ML_Training/lucknow_noida_data.csv`

### 2.2 Geo-Aware Features
- Add location/neighborhood as a feature
- Price per sqft by locality
- Distance to key landmarks (optional via geocoding)

**Files:** `ML_Training/geo_features.py`

---

## Boundaries

- **Always do:** Validate inputs server-side, handle errors gracefully, display loading states, show metrics prominently
- **Ask first:** Adding new dependencies (especially heavy ones like TensorFlow), changing API response shape, switching deployment platform, scraping real data (legal/ToS check)
- **Never do:** Commit API keys or .env files, remove the existing model without keeping a fallback, break backward compatibility of `/predict` endpoint

---

## Resolved Decisions

| Question | Decision | Rationale |
|---|---|---|
| Neural net library | MLPRegressor (scikit-learn) | Avoids ~500MB TensorFlow dependency; keeps deployment lightweight |
| Frontend deployment | Vercel | Preferred platform |
| Dataset framing | Smart Housing Predictor | Local angle makes it stand out as original work |
| Confidence interval | Fixed ±15% band | Simple to implement, good enough for demo purposes |
