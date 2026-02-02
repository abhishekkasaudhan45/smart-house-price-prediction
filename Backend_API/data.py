from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import numpy as np
import os

app = Flask(__name__)
CORS(app)

# Load ML artifacts
model = pickle.load(open("model.pkl", "rb"))
scaler = pickle.load(open("scaler.pkl", "rb"))
label_encoders = pickle.load(open("label_encoders.pkl", "rb"))
feature_columns = pickle.load(open("feature_columns.pkl", "rb"))

@app.route("/")
def home():
    return jsonify({"status": "Smart House Price Prediction API running"})

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.json

        area = float(data["area"])
        bedrooms = int(data["bedrooms"])
        bathrooms = int(data["bathrooms"])
        stories = int(data["stories"])
        parking = int(data["parking"])

        has_pool = label_encoders["has_pool"].transform([data["has_pool"]])[0]
        has_garage = label_encoders["has_garage"].transform([data["has_garage"]])[0]
        has_ac = label_encoders["has_ac"].transform([data["has_ac"]])[0]

        total_rooms = bedrooms + bathrooms
        bath_bed_ratio = bathrooms / (bedrooms + 1)

        input_data = np.array([[ 
            area, bedrooms, bathrooms, stories, parking,
            has_pool, has_garage, has_ac,
            total_rooms, bath_bed_ratio
        ]])

        input_scaled = scaler.transform(input_data)
        prediction = model.predict(input_scaled)[0]

        return jsonify({
            "predicted_price": round(float(prediction), 2)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400

# ✅ RENDER-SAFE FLASK START
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
