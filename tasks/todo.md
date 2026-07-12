# Task List: Lucknow House Price Predictor Upgrades

---

## Phase 1: ML Training (Foundation)

### Task 1: Advanced Multi-Model Training Notebook

**Description:** Create `ML_Training/advanced_training.ipynb` that trains 4 models on the existing synthetic dataset, compares them, selects the best by RMSE, generates SHAP feature importance, and saves all artifacts. Reframe the dataset as "Lucknow Housing Data."

**Acceptance criteria:**
- [ ] Trains 4 models: Linear Regression, Random Forest, XGBoost, MLPRegressor
- [ ] Prints a comparison table of R², RMSE, MAE for each model
- [ ] Picks the best model by RMSE and saves it as `Backend_API/model.pkl`
- [ ] Generates SHAP summary plot → `Backend_API/feature_importance.png`
- [ ] Saves model metrics dict to `Backend_API/model_metrics.pkl`
- [ ] Saves updated `scaler.pkl`, `label_encoders.pkl`, `feature_columns.pkl`
- [ ] Notebook runs end-to-end without errors

**Verification:**
- [ ] Jupyter notebook executes all cells cleanly
- [ ] All 6 output files exist in `Backend_API/`
- [ ] Model metrics have all 4 models with R², RMSE, MAE

**Dependencies:** None (uses existing dataset)

**Files likely touched:**
- `ML_Training/advanced_training.ipynb` (NEW)
- `Backend_API/model.pkl` (replaced)
- `Backend_API/model_metrics.pkl` (NEW)
- `Backend_API/feature_importance.png` (NEW)
- `Backend_API/scaler.pkl` (replaced)
- `Backend_API/label_encoders.pkl` (replaced)
- `Backend_API/feature_columns.pkl` (replaced)

**Scope:** Medium (5 files)

---

## Phase 2: Backend API Upgrades

### Task 2: Input Validation + New API Endpoints

**Description:** Upgrade `Backend_API/app.py` with field-level input validation, structured error responses, and two new endpoints: `GET /metrics` (model comparison data) and `GET /feature-importance` (SHAP plot image).

**Acceptance criteria:**
- [ ] POST /predict validates each field (type, range, required) and returns 422 with field-level errors on failure
- [ ] POST /predict returns `confidence_interval` in response (±15%)
- [ ] POST /predict returns `model_used` and `model_metrics` in response
- [ ] GET /metrics returns the full model comparison dict from `model_metrics.pkl`
- [ ] GET /feature-importance serves `feature_importance.png` as image/png
- [ ] Existing health check at GET / still works

**Verification:**
- [ ] curl POST with missing field → 422 + specific error
- [ ] curl POST with valid data → 200 + prediction + CI
- [ ] curl GET /metrics → JSON with 4 models
- [ ] curl GET /feature-importance → PNG image
- [ ] App starts without errors

**Dependencies:** Task 1 (needs updated model files)

**Files likely touched:**
- `Backend_API/app.py` (major edits)
- `Backend_API/requirements.txt` (add shap, xgboost)

**Scope:** Medium (2 files)

---

## Phase 3: Frontend Upgrades + Deployment

### Task 3: Frontend UI — Confidence Interval, Model Comparison, Feature Importance

**Description:** Update the frontend HTML/JS/CSS to display the confidence interval on predictions, a model comparison table, and the SHAP feature importance image. Reframe branding as "Lucknow House Price Predictor."

**Acceptance criteria:**
- [ ] Result card shows "Predicted Price: ₹X — ₹Y (95% confidence)" using ±15% band
- [ ] Model comparison table rendered below the form with R², RMSE, MAE columns
- [ ] SHAP feature importance image displayed on the page
- [ ] Loading skeleton/spinner during API calls
- [ ] Client-side form validation (matches backend rules)
- [ ] Error states displayed inline (not alert boxes)
- [ ] Branding updated to "Lucknow House Price Predictor"
- [ ] Responsive on mobile

**Verification:**
- [ ] Open index.html → form renders correctly
- [ ] Submit with missing field → client-side error shown
- [ ] Submit valid data → loading → result with CI and comparison table
- [ ] Feature importance image loads
- [ ] Mobile layout looks correct (<768px)

**Dependencies:** Task 2 (frontend calls the updated API)

**Files likely touched:**
- `Fronted_UI/index.html`
- `Fronted_UI/style.css`
- `Fronted_UI/script.js`

**Scope:** Medium (3 files)

---

### Task 4: Deploy Frontend to Vercel

**Description:** Deploy the static frontend files to Vercel, configure the API URL to point to the live Render backend, and set up any needed rewrites.

**Acceptance criteria:**
- [ ] Frontend accessible at a public Vercel URL
- [ ] API URL configured for production (Render backend)
- [ ] Form submits to live API and shows results
- [ ] No CORS errors in browser console
- [ ] Custom domain or vercel.app URL works

**Verification:**
- [ ] Open Vercel URL in browser
- [ ] Fill form, submit → prediction returned
- [ ] Check browser console for 0 CORS/network errors
- [ ] Test on mobile via DevTools

**Dependencies:** Task 3 (needs updated frontend files)

**Files likely touched:**
- `Fronted_UI/script.js` (API_URL update)
- `vercel.json` (NEW, for SPA routing if needed)

**Scope:** Small (1-2 files)

---

## Phase 4: Documentation

### Task 5: README Rewrite

**Description:** Rewrite README.md with a professional description of the Lucknow House Price Predictor, including screenshots, model comparison table, dataset details, tech stack badges, live demo link, and how-to-run instructions.

**Acceptance criteria:**
- [ ] Project description framed as Lucknow Housing Predictor
- [ ] Screenshots of the frontend (deployed)
- [ ] Model comparison table (R², RMSE, MAE for all 4 models)
- [ ] Dataset description (synthetic Lucknow housing data, 1000 houses, 8 features)
- [ ] Live Demo link (Vercel frontend)
- [ ] "How to Run Locally" section (backend + frontend)
- [ ] Tech stack badges with links
- [ ] SHAP feature importance findings highlighted

**Verification:**
- [ ] README renders correctly on GitHub
- [ ] All links work
- [ ] Demo link navigates to working app

**Dependencies:** Tasks 1-4 (needs screenshots and live URLs)

**Files likely touched:**
- `README.md` (rewrite)

**Scope:** Small (1 file)

---

## Phase 5: Verification

### Checkpoint: After Tasks 1-3
- [ ] Training notebook runs cleanly
- [ ] API endpoints respond correctly to valid/invalid input
- [ ] Frontend renders all new features (CI, comparison, importance)
- [ ] No console errors in frontend

### Checkpoint: After Tasks 4-5 (Complete)
- [ ] Vercel URL loads and works end-to-end
- [ ] Render API responds correctly
- [ ] README has working demo link and screenshots
- [ ] Full flow: open README → click demo → submit form → see prediction + CI + comparison
