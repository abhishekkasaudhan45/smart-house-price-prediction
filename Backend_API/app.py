from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pickle
import joblib
import numpy as np
import os

from database import get_db, init_db
from models import Prediction
from sqlalchemy import func

app = Flask(__name__)
CORS(app)

# Load ML artifacts
model = joblib.load("model.pkl")
scaler = joblib.load("scaler.pkl")
feature_columns = pickle.load(open("feature_columns.pkl", "rb"))
model_metrics = pickle.load(open("model_metrics.pkl", "rb"))

# Split-conformal 90% interval: relative residual quantile from calibration set
CONFORMAL_Q = model_metrics["conformal_q"]
LOCATIONS = model_metrics["locations"]
LAKH = 100000  # model predicts in INR lakhs

FIELD_RANGES = {
    "total_sqft": {
        "type": float,
        "min": 300,
        "max": 30000,
        "label": "Total Area (sq ft)",
    },
    "bhk": {"type": int, "min": 1, "max": 10, "label": "BHK"},
    "bath": {"type": int, "min": 1, "max": 10, "label": "Bathrooms"},
    "balcony": {"type": int, "min": 0, "max": 5, "label": "Balconies"},
}

# Initialize database tables on startup
_db_available = True
try:
    init_db()
except Exception:
    _db_available = False


def format_inr(lakhs):
    """Format a price in lakhs the way Indians read it: '₹85.2 Lakh' / '₹1.25 Cr'."""
    if lakhs >= 100:
        return f"₹{lakhs / 100:.2f} Cr"
    return f"₹{lakhs:.1f} Lakh"


def validate_input(data):
    """Validate all input fields and return a list of errors."""
    errors = []
    if not data:
        return [{"field": "body", "message": "Request body is required"}]

    for field, spec in FIELD_RANGES.items():
        value = data.get(field)
        if value is None:
            errors.append({"field": field, "message": f"{spec['label']} is required"})
            continue
        try:
            parsed = spec["type"](value)
            if parsed < spec["min"] or parsed > spec["max"]:
                errors.append(
                    {
                        "field": field,
                        "message": (
                            f"{spec['label']} must be between "
                            f"{spec['min']} and {spec['max']}"
                        ),
                    }
                )
        except (ValueError, TypeError):
            errors.append(
                {"field": field, "message": f"{spec['label']} must be a valid number"}
            )

    location = data.get("location")
    if not location:
        errors.append({"field": "location", "message": "Location is required"})
    elif location not in LOCATIONS and location != "other":
        errors.append(
            {
                "field": "location",
                "message": "Unknown location — pick one from /locations or 'other'",
            }
        )

    ready = data.get("ready_to_move")
    if ready is None:
        errors.append(
            {"field": "ready_to_move", "message": "ready_to_move is required (yes/no)"}
        )
    elif str(ready).lower() not in {"yes", "no", "0", "1"}:
        errors.append(
            {"field": "ready_to_move", "message": "ready_to_move must be 'yes' or 'no'"}
        )

    return errors


def build_feature_vector(total_sqft, bath, balcony, bhk, ready_to_move, location):
    """Build the input row in the exact order the model was trained on."""
    base = {
        "total_sqft": total_sqft,
        "bath": bath,
        "balcony": balcony,
        "bhk": bhk,
        "ready_to_move": ready_to_move,
    }
    loc_col = f"loc_{location}"
    row = []
    for col in feature_columns:
        if col in base:
            row.append(base[col])
        elif col == loc_col:
            row.append(1)
        else:
            row.append(0)
    return np.array([row])


@app.route("/")
def home():
    return jsonify(
        {
            "status": "Bengaluru House Price Predictor API running",
            "model": model_metrics["best_model"],
            "dataset": model_metrics.get("dataset_name", "Bengaluru House Data"),
            "dataset_size": model_metrics["dataset_size"],
            "database": "connected" if _db_available else "unavailable",
        }
    )


@app.route("/locations")
def locations():
    return jsonify({"locations": LOCATIONS, "count": len(LOCATIONS)})


@app.route("/predict", methods=["POST"])
def predict():
    data = request.json
    errors = validate_input(data)
    if errors:
        return jsonify({"error": "Validation failed", "details": errors}), 422

    try:
        total_sqft = float(data["total_sqft"])
        bhk = int(data["bhk"])
        bath = int(data["bath"])
        balcony = int(data["balcony"])
        location = data["location"]
        ready_to_move = 1 if str(data["ready_to_move"]).lower() in {"yes", "1"} else 0

        input_data = build_feature_vector(
            total_sqft, bath, balcony, bhk, ready_to_move, location
        )
        input_scaled = scaler.transform(input_data)
        pred_lakhs = float(model.predict(input_scaled)[0])
        pred_lakhs = max(pred_lakhs, 1.0)  # floor at Rs 1L

        # Split-conformal 90% prediction interval (calibrated, not hardcoded)
        ci_low_lakhs = round(pred_lakhs * (1 - CONFORMAL_Q), 2)
        ci_high_lakhs = round(pred_lakhs * (1 + CONFORMAL_Q), 2)

        prediction = round(pred_lakhs * LAKH, 2)
        ci_low = round(ci_low_lakhs * LAKH, 2)
        ci_high = round(ci_high_lakhs * LAKH, 2)

        if _db_available:
            try:
                db = next(get_db())
                record = Prediction(
                    total_sqft=total_sqft,
                    bhk=bhk,
                    bath=bath,
                    balcony=balcony,
                    location=location,
                    ready_to_move=ready_to_move,
                    predicted_price=prediction,
                    confidence_low=ci_low,
                    confidence_high=ci_high,
                    model_used=model_metrics["best_model"],
                )
                db.add(record)
                db.commit()
            except Exception:
                pass

        return jsonify(
            {
                "predicted_price": prediction,
                "predicted_price_lakhs": round(pred_lakhs, 2),
                "price_display": format_inr(pred_lakhs),
                "confidence_interval": {
                    "low": ci_low,
                    "high": ci_high,
                    "low_display": format_inr(ci_low_lakhs),
                    "high_display": format_inr(ci_high_lakhs),
                },
                "confidence_band": f"±{CONFORMAL_Q * 100:.0f}%",
                "interval_method": "split_conformal_90",
                "model_used": model_metrics["best_model"],
                "model_metrics": model_metrics["comparison"],
                "currency": "INR",
            }
        )

    except Exception as e:
        return jsonify({"error": "Prediction failed", "details": str(e)}), 500


@app.route("/history")
def history():
    if not _db_available:
        return jsonify({"error": "Database not available"}), 503
    db = next(get_db())
    records = (
        db.query(Prediction).order_by(Prediction.created_at.desc()).limit(20).all()
    )
    return jsonify(
        {
            "predictions": [
                {
                    "id": r.id,
                    "total_sqft": r.total_sqft,
                    "bhk": r.bhk,
                    "bath": r.bath,
                    "location": r.location,
                    "predicted_price": r.predicted_price,
                    "confidence_low": r.confidence_low,
                    "confidence_high": r.confidence_high,
                    "model_used": r.model_used,
                    "created_at": (r.created_at.isoformat() if r.created_at else None),
                }
                for r in records
            ],
            "count": len(records),
        }
    )


@app.route("/stats")
def stats():
    if not _db_available:
        return jsonify({"error": "Database not available"}), 503
    db = next(get_db())
    result = db.query(
        func.count(Prediction.id).label("total"),
        func.avg(Prediction.predicted_price).label("avg_price"),
        func.min(Prediction.predicted_price).label("min_price"),
        func.max(Prediction.predicted_price).label("max_price"),
    ).first()
    return jsonify(
        {
            "total_predictions": result.total,
            "average_price": (
                round(float(result.avg_price), 2) if result.avg_price else None
            ),
            "min_price": (
                round(float(result.min_price), 2) if result.min_price else None
            ),
            "max_price": (
                round(float(result.max_price), 2) if result.max_price else None
            ),
        }
    )


@app.route("/metrics")
def metrics():
    return jsonify(
        {
            "dataset_size": model_metrics["dataset_size"],
            "dataset_name": model_metrics.get("dataset_name"),
            "feature_count": model_metrics["feature_count"],
            "best_model": model_metrics["best_model"],
            "comparison": model_metrics["comparison"],
            "feature_importance": model_metrics.get("feature_importance", []),
            "currency": "INR",
            "unit": "lakhs",
        }
    )


@app.route("/feature-importance")
def feature_importance():
    image_path = os.path.join(os.path.dirname(__file__), "feature_importance.png")
    if os.path.exists(image_path):
        return send_file(image_path, mimetype="image/png")
    return jsonify({"error": "Feature importance image not found"}), 404


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
