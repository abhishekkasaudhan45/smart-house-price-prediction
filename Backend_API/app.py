from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pickle
import numpy as np
import os

from database import get_db, init_db
from models import Prediction
from sqlalchemy import func

app = Flask(__name__)
CORS(app)

# Load ML artifacts
model = pickle.load(open("model.pkl", "rb"))
scaler = pickle.load(open("scaler.pkl", "rb"))
label_encoders = pickle.load(open("label_encoders.pkl", "rb"))
feature_columns = pickle.load(open("feature_columns.pkl", "rb"))
model_metrics = pickle.load(open("model_metrics.pkl", "rb"))

CONFIDENCE_INTERVAL = 0.15  # ±15%

VALID_BOOLEANS = {"yes", "no"}
FIELD_RANGES = {
    "area": {"type": float, "min": 100, "max": 50000, "label": "Area (sq ft)"},
    "bedrooms": {"type": int, "min": 1, "max": 10, "label": "Bedrooms"},
    "bathrooms": {"type": int, "min": 1, "max": 10, "label": "Bathrooms"},
    "stories": {"type": int, "min": 1, "max": 5, "label": "Stories"},
    "parking": {"type": int, "min": 0, "max": 10, "label": "Parking spaces"},
}

BOOLEAN_FIELDS = ["has_pool", "has_garage", "has_ac"]

# Initialize database tables on startup
_db_available = True
try:
    init_db()
except Exception:
    _db_available = False


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

    for field in BOOLEAN_FIELDS:
        value = data.get(field)
        if value is None:
            errors.append({"field": field, "message": f"{field} is required (yes/no)"})
        elif str(value).lower() not in VALID_BOOLEANS:
            errors.append({"field": field, "message": f"{field} must be 'yes' or 'no'"})

    return errors


@app.route("/")
def home():
    return jsonify(
        {
            "status": "Lucknow House Price Predictor API running",
            "model": model_metrics["best_model"],
            "dataset_size": model_metrics["dataset_size"],
            "database": "connected" if _db_available else "unavailable",
        }
    )


@app.route("/predict", methods=["POST"])
def predict():
    data = request.json

    errors = validate_input(data)
    if errors:
        return jsonify({"error": "Validation failed", "details": errors}), 422

    try:
        area = float(data["area"])
        bedrooms = int(data["bedrooms"])
        bathrooms = int(data["bathrooms"])
        stories = int(data["stories"])
        parking = int(data["parking"])

        has_pool = label_encoders["has_pool"].transform(
            [str(data["has_pool"]).lower()]
        )[0]
        has_garage = label_encoders["has_garage"].transform(
            [str(data["has_garage"]).lower()]
        )[0]
        has_ac = label_encoders["has_ac"].transform([str(data["has_ac"]).lower()])[0]

        total_rooms = bedrooms + bathrooms
        bath_bed_ratio = bathrooms / (bedrooms + 1)

        input_data = np.array(
            [
                [
                    area,
                    bedrooms,
                    bathrooms,
                    stories,
                    parking,
                    has_pool,
                    has_garage,
                    has_ac,
                    total_rooms,
                    bath_bed_ratio,
                ]
            ]
        )

        input_scaled = scaler.transform(input_data)
        prediction = float(model.predict(input_scaled)[0])

        ci_low = round(prediction * (1 - CONFIDENCE_INTERVAL), 2)
        ci_high = round(prediction * (1 + CONFIDENCE_INTERVAL), 2)

        if _db_available:
            try:
                db = next(get_db())
                record = Prediction(
                    area=area,
                    bedrooms=bedrooms,
                    bathrooms=bathrooms,
                    stories=stories,
                    parking=parking,
                    has_pool=str(data["has_pool"]).lower(),
                    has_garage=str(data["has_garage"]).lower(),
                    has_ac=str(data["has_ac"]).lower(),
                    predicted_price=round(prediction, 2),
                    confidence_low=ci_low,
                    confidence_high=ci_high,
                    model_used=model_metrics["best_model"],
                )
                db.add(record)
                db.commit()
            except Exception:
                pass

        response = {
            "predicted_price": round(prediction, 2),
            "confidence_interval": {"low": ci_low, "high": ci_high},
            "confidence_band": f"±{int(CONFIDENCE_INTERVAL * 100)}%",
            "model_used": model_metrics["best_model"],
            "model_metrics": model_metrics["comparison"],
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": "Prediction failed", "details": str(e)}), 500


@app.route("/history")
def history():
    """Return the last 20 predictions."""
    if not _db_available:
        return jsonify({"error": "Database not available"}), 503

    db = next(get_db())
    records = (
        db.query(Prediction)
        .order_by(Prediction.created_at.desc())
        .limit(20)
        .all()
    )
    return jsonify(
        {
            "predictions": [
                {
                    "id": r.id,
                    "area": r.area,
                    "bedrooms": r.bedrooms,
                    "bathrooms": r.bathrooms,
                    "predicted_price": r.predicted_price,
                    "confidence_low": r.confidence_low,
                    "confidence_high": r.confidence_high,
                    "model_used": r.model_used,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                }
                for r in records
            ],
            "count": len(records),
        }
    )


@app.route("/stats")
def stats():
    """Return aggregate statistics about all predictions."""
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
            "average_price": round(float(result.avg_price), 2) if result.avg_price else None,
            "min_price": round(float(result.min_price), 2) if result.min_price else None,
            "max_price": round(float(result.max_price), 2) if result.max_price else None,
        }
    )


@app.route("/metrics")
def metrics():
    return jsonify(
        {
            "dataset_size": model_metrics["dataset_size"],
            "feature_count": model_metrics["feature_count"],
            "best_model": model_metrics["best_model"],
            "comparison": model_metrics["comparison"],
            "feature_importance": model_metrics["feature_importance"],
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
