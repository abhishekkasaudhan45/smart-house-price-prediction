# Lucknow House Price Predictor

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0%2B-black?logo=flask)](https://flask.palletsprojects.com)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3%2B-orange?logo=scikit-learn)](https://scikit-learn.org)
[![XGBoost](https://img.shields.io/badge/XGBoost-2.0%2B-green)](https://xgboost.readthedocs.io)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

A full-stack machine learning web application that predicts house prices for the Lucknow housing market. Compares 4 ML models, shows SHAP feature importance, and provides predictions with confidence intervals.

**Live Demo:** [Coming Soon — Deploying Frontend](#-deployment)
**API:** `https://your-app.onrender.com/`

---

## Performance Summary

| Model | R² Score | RMSE (₹) | MAE (₹) | Rank |
|---|---|---|---|---|
| **Linear Regression** | **0.9733** | **₹26,739** | **₹21,019** | 🏆 **1** |
| XGBoost | 0.9387 | ₹40,489 | ₹32,748 | 2 |
| Random Forest | 0.8971 | ₹52,448 | ₹41,756 | 3 |
| MLPRegressor (Neural Net) | -25.30 | ₹8,38,508 | ₹8,22,413 | 4 |

> **Winner:** Linear Regression selected by lowest RMSE on the test set (20% holdout).

---

## Top Price Drivers

SHAP analysis identifies the most influential features in Lucknow housing prices:

1. **Area (sq ft)** — strongest price determinant
2. **Swimming Pool** — premium feature
3. **Bedrooms** — more rooms = higher price
4. **Garage** — adds significant value
5. **Total Rooms** — overall size signal

---

## Features

- **4 Model Comparison** — Linear Regression, Random Forest, XGBoost, MLPRegressor
- **SHAP Feature Importance** — interactive visualization of price drivers
- **Confidence Interval** — ±15% band on every prediction
- **Input Validation** — client + server side validation
- **Clean UI** — responsive, mobile-friendly design
- **REST API** — JSON endpoints for easy integration

---

## Tech Stack

| Layer | Technology |
|---|---|
| **ML Training** | Pandas, NumPy, scikit-learn, XGBoost, SHAP |
| **Backend** | Flask, Flask-CORS, gunicorn |
| **Frontend** | HTML, CSS (Inter font, CSS Grid/Flexbox), Vanilla JS |
| **Deployment** | Render (API), Vercel (Frontend) |
| **Dataset** | 1,000 synthetic Lucknow house listings, 8 features |

---

## Project Structure

```
Backend_API/       # Flask REST API & trained models
  app.py            — main Flask application
  model.pkl         — best trained model
  model_metrics.pkl — comparison data for frontend
  feature_importance.png — SHAP summary plot
  requirements.txt

Fronted_UI/        # Static frontend
  index.html
  style.css
  Script.js

ML_Training/       # Data generation & model training
  data.py           — synthetic dataset generator
  house_data.csv    — 1,000 house listings
  eda.ipynb         — exploratory data analysis
  training.ipynb    — original (2 models)
  advanced_training.ipynb — 4-model comparison + SHAP
```

---

## How to Run Locally

### Backend

```bash
cd Backend_API
pip install -r requirements.txt
python app.py
```

The API starts on `http://localhost:10000`.

### Frontend

```bash
cd Fronted_UI
python -m http.server 8080
# or: npx serve .
```

Open `http://localhost:8080` in your browser. The frontend connects to `http://localhost:10000`.

### Training

```bash
cd ML_Training
jupyter notebook advanced_training.ipynb
```

---

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Health check & model info |
| `/predict` | POST | Predict house price (JSON body) |
| `/metrics` | GET | Model comparison data |
| `/feature-importance` | GET | SHAP feature importance image |

### Example Prediction Request

```bash
curl -X POST http://localhost:10000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "area": 2500,
    "bedrooms": 3,
    "bathrooms": 2,
    "stories": 2,
    "parking": 2,
    "has_pool": "no",
    "has_garage": "yes",
    "has_ac": "yes"
  }'
```

### Response

```json
{
  "predicted_price": 790439.95,
  "confidence_interval": { "low": 671873.96, "high": 909005.94 },
  "confidence_band": "±15%",
  "model_used": "Linear Regression",
  "model_metrics": { ... }
}
```

---

## Deployment

### API (Render)
1. Push the `Backend_API/` directory to a new GitHub repo
2. Create a **Web Service** on Render
3. Set **Build Command:** `pip install -r requirements.txt`
4. Set **Start Command:** `gunicorn app:app`
5. Deploy

### Frontend (Vercel)
1. Push the `Fronted_UI/` directory to a GitHub repo
2. Import project on Vercel
3. Set **Output Directory:** `.` (root)
4. Add `vercel.json` with a rewrite rule pointing `/api/*` to your Render URL
5. Deploy

---

## What I Learned

- Building a full ML pipeline from synthetic data generation through deployment
- Comparing multiple models systematically with proper holdout evaluation
- Using SHAP for model interpretability beyond simple feature importance
- Deploying a Flask API with fallbacks for cold-start scenarios
- Cleaning validation as a two-layer strategy (client-side UX + server-side security)

---

Created by **Abhishek Kasaudhan**
