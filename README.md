# Bengaluru House Price Predictor

<p align="center">
  <a href="https://blrpricer.abhishektech.me"><strong>Live Demo</strong></a> ·
  <a href="https://lucknow-house-price-api.onrender.com"><strong>API Health</strong></a> ·
  <a href="https://github.com/abhishekkasaudhan45/smart-house-price-prediction"><strong>GitHub</strong></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Flask-3.0-black?logo=flask" alt="Flask">
  <img src="https://img.shields.io/badge/scikit--learn-1.9-orange?logo=scikit-learn" alt="scikit-learn">
  <img src="https://img.shields.io/badge/PostgreSQL-16-blue?logo=postgresql" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/Docker-24-blue?logo=docker" alt="Docker">
  <img src="https://img.shields.io/badge/CI-GitHub_Actions-green?logo=githubactions" alt="CI">
  <img src="https://img.shields.io/badge/License-MIT-yellow" alt="License">
</p>

A full-stack machine learning web application that predicts Bengaluru house prices in INR from **10,224 real listings** (Kaggle Bengaluru House Data). It compares 4 ML models (Linear Regression, Random Forest, XGBoost, MLPRegressor), explains predictions with feature importance, and provides **calibrated 90% prediction intervals via split-conformal calibration**. Every prediction is stored in PostgreSQL.

---

## Architecture

```text
User Browser (Vercel)
     │
     ▼
Flask API (Render, Docker container)
     │
     ├── ML Engine (XGBoost + 3 challengers, 241 features)
     ├── Input Validation (client + server)
     ├── Split-Conformal Prediction Intervals (90% coverage)
     └── PostgreSQL Database (Render)
           └── Prediction history + stats
```

---

## Model Performance

Trained on 10,224 cleaned Bengaluru listings (236 locations one-hot encoded). Errors in INR lakhs.

| Model | R² Score | RMSE (₹ Lakh) | MAE (₹ Lakh) | Rank |
| :--- | :---: | :---: | :---: | :---: |
| **XGBoost** | **0.8292** | **₹26.15L** | **₹15.72L** | 1 |
| MLPRegressor (Neural Net) | 0.8064 | ₹27.84L | ₹16.10L | 2 |
| Random Forest | 0.7900 | ₹28.99L | ₹16.72L | 3 |
| Linear Regression | 0.7819 | ₹29.55L | ₹17.74L | 4 |

> **Winner:** XGBoost selected by lowest RMSE on a held-out test set.
> **Intervals:** Split-conformal ±35.5% band, **89.6% empirical coverage** on the test set (target 90%).

**Top price drivers:**
1. **Location:** Dominates Bengaluru pricing (Whitefield vs Electronic City)
2. **Total Area (sq ft)**
3. **Bathrooms**
4. **BHK**
5. **Ready to Move** availability

---

## Features

### ML Pipeline
- Real-world data cleaning: sqft range parsing, BHK extraction, per-location price-per-sqft outlier removal, and rare-location grouping (1,305 to 236)
- 4-model comparison with automated best-model selection (lowest RMSE)
- **Split-conformal prediction intervals:** Calibrated on a held-out set with verified 89.6% coverage
- 241 features (5 numeric + 236 one-hot locations)

### Engineering
- **PostgreSQL persistence:** Every prediction saved with full input and output
- **Docker containerization:** Single-command build and deploy
- **CI/CD:** Automated testing and deployment via GitHub Actions
- **Input validation:** Dual-layer validation on both client and server
- **pytest test suite:** Covers health, prediction, validation, locations, history, and stats

### API
| Endpoint | Method | Description |
| :--- | :---: | :--- |
| `/` | GET | Health check + DB status |
| `/predict` | POST | Predict house price (INR, with 90% interval) |
| `/locations` | GET | Supported Bengaluru locations |
| `/history` | GET | Last 20 predictions |
| `/stats` | GET | Aggregate stats (total, avg, min, max) |
| `/metrics` | GET | Model comparison data |
| `/feature-importance` | GET | Feature importance plot PNG |

---

## Tech Stack

| Layer | Technology |
| :--- | :--- |
| **ML Training** | Pandas, NumPy, scikit-learn, XGBoost |
| **Backend** | Flask, Flask-CORS, Gunicorn |
| **Database** | PostgreSQL 16, SQLAlchemy ORM, Alembic |
| **Frontend** | HTML5, CSS3 (Inter font, Grid/Flexbox), Vanilla JS |
| **Containerization** | Docker (python:3.12) |
| **CI/CD** | GitHub Actions, Render Deploy Hooks |
| **Deployment** | Render (API), Vercel (Frontend + custom domain) |
| **Dataset** | Kaggle "Bengaluru House Data" (13,320 raw listings) |

---

## Project Structure

```text
Backend_API/                 # Flask REST API
├── app.py                   # Application + 7 endpoints
├── database.py              # SQLAlchemy engine + session
├── models.py                # Prediction ORM model
├── Dockerfile               # Container image (python:3.12)
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variable template
├── alembic/                 # Schema migrations (0001, 0002)
└── *.pkl / *.png            # ML artifacts

Fronted_UI/                  # Static frontend (Vercel)
├── index.html
├── style.css
└── script.js

ML_Training/                 # Model training
├── Bengaluru_House_Data.csv # 13,320 raw listings
├── train_bengaluru.py       # Cleaning + 4-model comparison + conformal calibration
└── eda.ipynb                # Exploratory analysis

tests/                       # pytest test suite
└── test_api.py

.github/workflows/
└── ci.yml                   # GitHub Actions pipeline
```

---

## Quick Start

### Prerequisites
- Python 3.12+
- Docker (optional, for containerized run)

### Backend (local)

```bash
pip install -r Backend_API/requirements.txt
python Backend_API/app.py
# Runs at http://localhost:10000
```

### Frontend (local)

```bash
python -m http.server 8080 --directory Fronted_UI
# Runs at http://localhost:8080
```

### With Docker

```bash
make docker-build
make docker-run
# Runs at http://localhost:10000
```

### Retrain the model

```bash
python ML_Training/train_bengaluru.py
# Writes model.pkl, scaler.pkl, feature_columns.pkl, model_metrics.pkl to Backend_API/
```

### Tests

```bash
make test
# or
python -m pytest tests/ -v
```

---

## Deployment

### Render (API)
1. Push repo to GitHub
2. Render -> New Web Service -> connect repo
3. Settings:
   - **Docker Context:** `./Backend_API`
   - **Dockerfile Path:** `./Backend_API/Dockerfile`
   - **Build Command:** *(empty)*
   - **Start Command:** *(empty)*
4. Add env var `DATABASE_URL` (Render PostgreSQL internal URL)
5. Deploy

### Vercel (Frontend)
1. Push `Fronted_UI/` to GitHub
2. Vercel -> Import Project -> connect repo
3. Auto-deploys at the custom domain `blrpricer.abhishektech.me`

---

## What I Built

- End-to-end ML system on real Indian housing data, from raw-data cleaning to production deployment
- Statistically calibrated prediction intervals using split-conformal calibration with verified coverage
- Production-grade Flask API backed by PostgreSQL, Docker, and GitHub Actions CI/CD
- Clean engineering workflow with automated tests, linting, and database migrations

---

<p align="center">
  Created by <strong>Abhishek Kasaudhan</strong>
</p>