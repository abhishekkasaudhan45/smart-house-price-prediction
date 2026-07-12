# Implementation Plan: Lucknow House Price Predictor — Phase 2 Upgrades

## Overview

Upgrade the existing house price prediction project with multi-model comparison (4 models), SHAP feature importance, API validation, a deployed frontend with confidence intervals, and a professional README. Reframe as a Lucknow-specific predictor.

## Architecture Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Neural net | MLPRegressor (scikit-learn) | Avoids heavy TensorFlow dep; keeps deployment small |
| Frontend host | Vercel | User preference; good free tier for static sites |
| Dataset framing | Lucknow Housing Predictor | Local angle = original portfolio piece |
| Confidence interval | Fixed ±15% band | Simple; good enough for demo |
| Best model picker | Lowest RMSE across 4 models | Standard ML evaluation practice |

## Dependency Graph

```
advanced_training.ipynb
    │
    ├── model.pkl (replaced)          ──→ API serves predictions
    ├── model_metrics.pkl (NEW)       ──→ API GET /metrics ──→ Frontend comparison table
    ├── feature_importance.png (NEW)  ──→ API GET /feature-importance ──→ Frontend displays
    │
    └── scaler.pkl, label_encoders.pkl, feature_columns.pkl (regenerated)
```

```
Backend API (app.py)
    │
    ├── POST /predict                 ──→ Frontend form submit
    │   └── input validation (NEW)
    │
    ├── GET /metrics (NEW)            ──→ Frontend comparison table
    ├── GET /feature-importance (NEW) ──→ Frontend image display
    └── GET / (health check)
```

```
Frontend (HTML/JS/CSS)
    │
    ├── Form with dropdowns/sliders
    ├── Result card with ±15% CI (NEW)
    ├── Model comparison table (NEW)
    ├── Feature importance image (NEW)
    └── Deployed to Vercel (NEW)
```

## Implementation Order

**Must be sequential within each phase. Some phases can be parallel.**

```
Phase 1: ML Training (foundation)
  Task 1: Advanced training notebook
    ↓
Phase 2: Backend API upgrades (depends on Task 1)
  Task 2: Input validation + metrics endpoints
    ↓
Phase 3: Frontend upgrades (depends on Task 2)
  Task 3: UI updates for CI + comparison + importance
  Task 4: Deploy frontend to Vercel
    ↓
Phase 4: Documentation (can overlap with 3)
  Task 5: README rewrite
    ↓
Phase 5: Polish + Verification
  Task 6: End-to-end verification
```

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| XGBoost install issues on Windows | Medium | Pin working version; fall back to just 3 models |
| CORS issues between Vercel frontend and Render API | Medium | Configure CORS properly; use env vars for API URL |
| SHAP computation slow on 1000 rows | Low | Use PermutationImportance as fallback |
| Render API cold start slow | Low | Add loading states in frontend; note in README |

## Open Questions

None — all 4 decisions resolved in the PRD.
