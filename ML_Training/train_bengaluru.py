"""Train 4 models on the Bengaluru House Data dataset (prices in INR lakhs)."""

import warnings

import numpy as np
import pandas as pd
import pickle
import joblib

from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
import xgboost as xgb

warnings.filterwarnings("ignore")

print("Loading dataset...")
df = pd.read_csv("Bengaluru_House_Data.csv")
print(f"Raw shape: {df.shape}")

# === Cleaning ===
print("Cleaning data...")

# Drop columns we don't use
df = df.drop(columns=["area_type", "society"])

# bhk from size ("2 BHK" / "4 Bedroom" -> int)
df = df.dropna(subset=["size", "location"])
df["bhk"] = df["size"].str.extract(r"(\d+)").astype(int)


# total_sqft: parse ranges ("1000-1200" -> mean), drop non-numeric units
def parse_sqft(x):
    try:
        if "-" in str(x):
            lo, hi = str(x).split("-")
            return (float(lo) + float(hi)) / 2
        return float(x)
    except ValueError:
        return np.nan


df["total_sqft"] = df["total_sqft"].apply(parse_sqft)
df = df.dropna(subset=["total_sqft"])

# bath/balcony: fill missing with median
df["bath"] = df["bath"].fillna(df["bath"].median())
df["balcony"] = df["balcony"].fillna(df["balcony"].median())

# ready_to_move flag
df["ready_to_move"] = (df["availability"] == "Ready To Move").astype(int)

# Drop data-error rows: less than 300 sqft per BHK
df = df[df["total_sqft"] / df["bhk"] >= 300]

# Drop absurd bath counts (bath > bhk + 2)
df = df[df["bath"] <= df["bhk"] + 2]

# Group rare locations into "other"
df["location"] = df["location"].str.strip()
loc_counts = df["location"].value_counts()
rare = loc_counts[loc_counts < 10].index
df["location"] = df["location"].apply(lambda x: "other" if x in rare else x)
print(f"Locations after grouping: {df['location'].nunique()}")

# Remove price-per-sqft outliers (beyond 1 std within each location)
df["price_per_sqft"] = df["price"] * 100000 / df["total_sqft"]


def remove_pps_outliers(frame):
    keep = []
    for _, group in frame.groupby("location"):
        mu, sigma = group.price_per_sqft.mean(), group.price_per_sqft.std()
        keep.append(
            group[
                (group.price_per_sqft > mu - sigma)
                & (group.price_per_sqft <= mu + sigma)
            ]
        )
    return pd.concat(keep)


df = remove_pps_outliers(df)

# Trim the extreme luxury tail (top 1%): a handful of Rs 10-22 Cr mansions
# dominate RMSE and aren't the use case for this predictor.
price_cap = df["price"].quantile(0.99)
df = df[df["price"] <= price_cap]
print(f"Price cap (99th pct): Rs {price_cap:,.0f}L")

df = df.drop(columns=["price_per_sqft", "size", "availability"])
print(f"Clean shape: {df.shape}")

# === Features ===
base_features = ["total_sqft", "bath", "balcony", "bhk", "ready_to_move"]
location_dummies = pd.get_dummies(df["location"], prefix="loc").astype(int)
X = pd.concat([df[base_features], location_dummies], axis=1)
y = df["price"]  # in INR lakhs — native, no conversion

feature_cols = list(X.columns)
locations = sorted(c.replace("loc_", "") for c in location_dummies.columns)

print(f"Features: {len(feature_cols)} ({base_features} + {len(locations)} locations)")
print(f"Samples: {len(X)}")
print(
    f"Price range: Rs {y.min():,.1f}L — Rs {y.max():,.1f}L "
    f"(median Rs {y.median():,.1f}L)"
)

# === Train/Calibration/Test Split ===
# Calibration set is held out for split-conformal prediction intervals.
X_train, X_temp, y_train, y_temp = train_test_split(
    X, y, test_size=0.3, random_state=42
)
X_calib, X_test, y_calib, y_test = train_test_split(
    X_temp, y_temp, test_size=0.5, random_state=42
)

# === Scale ===
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_calib_scaled = scaler.transform(X_calib)
X_test_scaled = scaler.transform(X_test)

# === Train 4 Models ===
models = {
    "Linear Regression": LinearRegression(),
    "Random Forest": RandomForestRegressor(
        n_estimators=300, max_depth=None, min_samples_leaf=2, random_state=42, n_jobs=-1
    ),
    "XGBoost": xgb.XGBRegressor(
        n_estimators=600,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        verbosity=0,
    ),
    "MLPRegressor (Neural Net)": MLPRegressor(
        hidden_layer_sizes=(128, 64),
        activation="relu",
        solver="adam",
        max_iter=800,
        random_state=42,
        early_stopping=True,
        validation_fraction=0.1,
    ),
}

results = {}
trained_models = {}

for name, model in models.items():
    print(f"\nTraining {name}...")
    model.fit(X_train_scaled, y_train)
    preds = model.predict(X_test_scaled)

    r2 = r2_score(y_test, preds)
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    mae = mean_absolute_error(y_test, preds)

    results[name] = {
        "R2": round(r2, 4),
        "RMSE": round(rmse, 2),  # in lakhs
        "MAE": round(mae, 2),  # in lakhs
    }
    trained_models[name] = model
    print(f"  R2: {r2:.4f}  RMSE: Rs {rmse:,.2f}L  MAE: Rs {mae:,.2f}L")

# === Comparison Table ===
print("\n" + "=" * 70)
print("MODEL COMPARISON (errors in INR lakhs)")
print("=" * 70)
comparison_df = pd.DataFrame(results).T
comparison_df["Rank"] = comparison_df["RMSE"].rank().astype(int)
comparison_df = comparison_df.sort_values("RMSE")
for i, (name, row) in enumerate(comparison_df.iterrows()):
    print(
        f"  {i+1}. {name}: R2={row['R2']}, "
        f"RMSE=Rs {row['RMSE']:,.2f}L, MAE=Rs {row['MAE']:,.2f}L"
    )

# === Select Best ===
best_name = comparison_df.index[0]
best_model = trained_models[best_name]
print(f"\nBest model: {best_name} (lowest RMSE)")

# === Split-Conformal Prediction Intervals ===
# On a held-out calibration set, take the 90th percentile of relative absolute
# residuals |y - yhat| / yhat. At predict time: interval = yhat * (1 +/- q).
# Guarantees ~90% empirical coverage regardless of model family.
calib_preds = best_model.predict(X_calib_scaled)
rel_residuals = np.abs(y_calib.values - calib_preds) / np.maximum(calib_preds, 1e-9)
conformal_q = float(np.quantile(rel_residuals, 0.90))

test_preds = best_model.predict(X_test_scaled)
covered = np.mean(
    (y_test.values >= test_preds * (1 - conformal_q))
    & (y_test.values <= test_preds * (1 + conformal_q))
)
print(f"\nConformal interval: +/-{conformal_q*100:.1f}% (target 90% coverage)")
print(f"Empirical coverage on test set: {covered*100:.1f}%")

# === Save Artifacts (joblib compress=3 for smaller files) ===
joblib.dump(best_model, "../Backend_API/model.pkl", compress=3)
print(">> Saved model.pkl (compressed)")

joblib.dump(scaler, "../Backend_API/scaler.pkl", compress=3)
print(">> Saved scaler.pkl (compressed)")

with open("../Backend_API/feature_columns.pkl", "wb") as f:
    pickle.dump(feature_cols, f)
print(">> Saved feature_columns.pkl")

# Feature importance (aggregate one-hot locations into a single "location" entry).
# Fall back to Random Forest importances when the best model exposes none (e.g. MLP).
if hasattr(best_model, "coef_"):
    importances = np.abs(best_model.coef_)
elif hasattr(best_model, "feature_importances_"):
    importances = np.abs(best_model.feature_importances_)
else:
    importances = np.abs(trained_models["Random Forest"].feature_importances_)

fi_raw = dict(zip(feature_cols, importances))
fi_agg = {f: fi_raw[f] for f in base_features}
fi_agg["location"] = sum(v for k, v in fi_raw.items() if k.startswith("loc_"))
fi_df = pd.DataFrame(
    {"Feature": list(fi_agg.keys()), "Importance": list(fi_agg.values())}
).sort_values("Importance", ascending=False)
fi_list = [
    {"Feature": row["Feature"], "Importance": round(row["Importance"], 4)}
    for _, row in fi_df.iterrows()
]

model_metrics = {
    "dataset_size": len(df),
    "dataset_name": "Bengaluru House Data (Kaggle)",
    "currency": "INR",
    "unit": "lakhs",
    "feature_count": len(feature_cols),
    "best_model": best_name,
    "conformal_q": conformal_q,
    "interval_method": "split_conformal_90",
    "comparison": results,
    "feature_importance": fi_list,
    "locations": locations,
}
with open("../Backend_API/model_metrics.pkl", "wb") as f:
    pickle.dump(model_metrics, f)
print(">> Saved model_metrics.pkl")

# Dummy label_encoders for backward compat
with open("../Backend_API/label_encoders.pkl", "wb") as f:
    pickle.dump({}, f)
print(">> Saved label_encoders.pkl")

print("\nTop Price Drivers:")
for _, row in fi_df.iterrows():
    print(f"  {row['Feature']}: {row['Importance']:.4f}")

# === Charts ===
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

fig, ax = plt.subplots(figsize=(8, 5))
fi_plot = fi_df.sort_values("Importance")
ax.barh(fi_plot["Feature"], fi_plot["Importance"], color="#6366f1")
ax.set_title(f"Feature Importance — {best_name} (Bengaluru House Data)")
ax.set_xlabel("Importance")
plt.tight_layout()
plt.savefig("../Backend_API/feature_importance.png", dpi=120)
print(">> Saved feature_importance.png")

fig, ax = plt.subplots(figsize=(8, 5))
names = list(comparison_df.index)
rmses = comparison_df["RMSE"].values
colors = ["#22c55e" if n == best_name else "#94a3b8" for n in names]
ax.bar(names, rmses, color=colors)
ax.set_title("Model Comparison — RMSE (INR lakhs, lower is better)")
ax.set_ylabel("RMSE (Rs lakhs)")
plt.xticks(rotation=15, ha="right")
plt.tight_layout()
plt.savefig("../Backend_API/model_comparison.png", dpi=120)
print(">> Saved model_comparison.png")

print("\n>> Training complete!")
