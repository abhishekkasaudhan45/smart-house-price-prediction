"""Train 4 models on Kaggle House Prices dataset."""

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
df = pd.read_csv("Data.csv")
print(f"Shape: {df.shape}")

# === Feature Engineering ===
print("Engineering features...")

# Map to our feature names
df["area"] = df["GrLivArea"]
df["bedrooms"] = df["BedroomAbvGr"]
df["bathrooms"] = df["FullBath"] + df["HalfBath"] * 0.5
df["overall_qual"] = df["OverallQual"]
df["year_built"] = df["YearBuilt"]
df["has_pool"] = (df["PoolArea"] > 0).astype(int)
df["has_garage"] = (df["GarageCars"] > 0).astype(int)
df["has_ac"] = (df["CentralAir"] == "Y").astype(int)

# Engineered features (matches existing model pattern)
df["total_rooms"] = df["bedrooms"] + np.ceil(df["bathrooms"]).astype(int)
df["bath_bed_ratio"] = df["bathrooms"] / (df["bedrooms"] + 1)

# Target
y = df["SalePrice"]

feature_cols = [
    "area",
    "bedrooms",
    "bathrooms",
    "overall_qual",
    "year_built",
    "has_pool",
    "has_garage",
    "has_ac",
    "total_rooms",
    "bath_bed_ratio",
]
X = df[feature_cols]

print(f"Features: {feature_cols}")
print(f"Samples: {len(X)}")
print(f"Price range: ${y.min():,.0f} — ${y.max():,.0f}")

# === Train/Test Split ===
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# === Scale ===
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# === Train 4 Models ===
models = {
    "Linear Regression": LinearRegression(),
    "Random Forest": RandomForestRegressor(
        n_estimators=100, max_depth=10, random_state=42
    ),
    "XGBoost": xgb.XGBRegressor(
        n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42, verbosity=0
    ),
    "MLPRegressor (Neural Net)": MLPRegressor(
        hidden_layer_sizes=(64, 32),
        activation="relu",
        solver="adam",
        max_iter=500,
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
        "RMSE": round(rmse, 2),
        "MAE": round(mae, 2),
    }
    trained_models[name] = model
    print(f"  R²: {r2:.4f}  RMSE: ${rmse:,.2f}  MAE: ${mae:,.2f}")

# === Comparison Table ===
print("\n" + "=" * 70)
print("MODEL COMPARISON")
print("=" * 70)
comparison_df = pd.DataFrame(results).T
comparison_df["Rank"] = comparison_df["RMSE"].rank().astype(int)
comparison_df = comparison_df.sort_values("RMSE")
for i, (name, row) in enumerate(comparison_df.iterrows()):
    print(
        f"  {i+1}. {name}: R²={row['R2']}, "
        f"RMSE=${row['RMSE']:,.2f}, MAE=${row['MAE']:,.2f}"
    )

# === Select Best ===
best_name = comparison_df.index[0]
best_model = trained_models[best_name]
print(f"\nBest model: {best_name} (lowest RMSE)")

# === Save Artifacts (joblib compress=3 for smaller files) ===
joblib.dump(best_model, "../Backend_API/model.pkl", compress=3)
print(">> Saved model.pkl (compressed)")

joblib.dump(scaler, "../Backend_API/scaler.pkl", compress=3)
print(">> Saved scaler.pkl (compressed)")

# Feature columns for API
with open("../Backend_API/feature_columns.pkl", "wb") as f:
    pickle.dump(feature_cols, f)
print(">> Saved feature_columns.pkl")

# Model metrics
fi_list = []
if hasattr(best_model, "coef_"):
    importances = np.abs(best_model.coef_)
else:
    importances = np.abs(best_model.feature_importances_)

fi_df = pd.DataFrame({"Feature": feature_cols, "Importance": importances})
fi_df = fi_df.sort_values("Importance", ascending=False)
fi_list = [
    {"Feature": row["Feature"], "Importance": round(row["Importance"], 4)}
    for _, row in fi_df.iterrows()
]

model_metrics = {
    "dataset_size": len(df),
    "feature_count": len(feature_cols),
    "best_model": best_name,
    "comparison": results,
    "feature_importance": fi_list,
}
with open("../Backend_API/model_metrics.pkl", "wb") as f:
    pickle.dump(model_metrics, f)
print(">> Saved model_metrics.pkl")

# Dummy label_encoders for backward compat (no categorical encoding needed)
label_encoders = {}
with open("../Backend_API/label_encoders.pkl", "wb") as f:
    pickle.dump(label_encoders, f)
print(">> Saved label_encoders.pkl")

print("\nTop Price Drivers:")
for _, row in fi_df.iterrows():
    print(f"  {row['Feature']}: {row['Importance']:.2f}")

print("\n>> Training complete!")
