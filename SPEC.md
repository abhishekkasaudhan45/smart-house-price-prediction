# Spec: Phase 4 — Real Indian Dataset, Statistical Intervals & Naming Cleanup

## Objective

Replace the US Ames/Iowa dataset (whose prices were dishonestly "converted" to INR by
multiplying by 85) with the real **Bengaluru House Data** dataset (13,320 real Indian
listings, prices natively in ₹ lakhs). Replace the hardcoded ±15% confidence interval
with statistical prediction intervals derived from Random Forest per-tree quantiles.
Clean up naming leftovers (`stories`/`parking` DB columns storing quality/year).

**Success criteria:**
- Model trained on 13,320 real Bengaluru listings, target in ₹ lakhs (no currency conversion)
- Best model R² ≥ 0.75 on held-out test set
- `/predict` returns per-prediction 90% intervals from RF tree quantiles (`interval_method: "rf_quantile_90"`)
- `/locations` endpoint serves the location dropdown
- Frontend shows prices in Indian format ("₹85.2 Lakh" / "₹1.2 Cr")
- DB schema columns match real features; Alembic migration `0002` applied
- All pytest tests green; live site verified end-to-end

---

## Dataset

| Property | Value |
|---|---|
| Source | Kaggle "Bengaluru House Data" (CC license) |
| Rows | 13,320 |
| Target | `price` in ₹ lakhs (min 8, median 72, max 3600) |
| Raw columns | area_type, availability, location, size, society, total_sqft, bath, balcony, price |
| Locations | 1,305 unique (grouped: <10 listings → "other") |

### Cleaning rules
- `total_sqft`: parse ranges ("1000-1200" → mean), drop non-numeric units (e.g. "34.46Sq. Meter")
- `bhk`: extract int from `size` ("2 BHK" → 2)
- Drop rows: sqft/bhk < 300 (data errors), price-per-sqft outliers beyond 1 std within location
- `ready_to_move`: 1 if availability == "Ready To Move" else 0
- One-hot encode `location` after grouping rare ones into "other"

### Features
`total_sqft`, `bath`, `balcony`, `bhk`, `ready_to_move`, `location_*` (one-hot, ~56+)

---

## API Contract Changes

### POST /predict (new request shape)
```json
{
  "total_sqft": 1200, "bhk": 2, "bath": 2, "balcony": 1,
  "location": "Whitefield", "ready_to_move": 1
}
```

### POST /predict (new response shape)
```json
{
  "predicted_price": 8520000,
  "predicted_price_lakhs": 85.2,
  "price_display": "₹85.2 Lakh",
  "ci_low": 7100000, "ci_high": 10200000,
  "interval_method": "rf_quantile_90",
  "currency": "INR", "model_used": "Random Forest"
}
```

### GET /locations (new)
```json
{ "locations": ["Whitefield", "Sarjapur Road", ...], "count": 56 }
```

---

## Prediction Intervals

Instead of `price * 0.85 / 1.15`:
```python
tree_preds = np.array([t.predict(x_scaled) for t in model.estimators_])
ci_low, ci_high = np.percentile(tree_preds, [5, 95])
```
This is a real 90% prediction interval from the ensemble distribution — resume-defensible.

---

## Database Schema (migration 0002)

`predictions` table columns replaced:
- REMOVE: `area`, `stories`, `parking` (misnamed leftovers)
- ADD: `total_sqft` Float, `bhk` Int, `bath` Int, `balcony` Int, `location` String(100), `ready_to_move` Int
- KEEP: `predicted_price`, `confidence_low`, `confidence_high`, `model_used`, `created_at`

Demo data — drop & recreate is acceptable.

---

## Boundaries

- **Always do:** train in ₹ lakhs natively; keep 4-model comparison; joblib compress=3; keep all existing endpoints working
- **Ask first:** changing hosting, adding new services, renaming the Render service URL
- **Never do:** fake currency conversions; hardcoded intervals; committing the raw CSV to git if > 1MB (it's 916KB — OK to commit)

---

## Success Criteria Checklist

- [ ] `train_bengaluru.py` runs clean, R² ≥ 0.75, artifacts saved
- [ ] `/predict` returns lakh-denominated prices with quantile intervals
- [ ] `/locations` returns location list
- [ ] Alembic migration 0002 applies
- [ ] Frontend form matches new features; prices display as "₹X Lakh / ₹X Cr"
- [ ] All tests green in CI
- [ ] Live site returns believable Bengaluru prices
