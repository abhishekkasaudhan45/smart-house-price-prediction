"""Tests for the Bengaluru House Price Predictor API."""

import pytest
import sys
import os

_BACKEND_DIR = os.path.join(os.path.dirname(__file__), "..", "Backend_API")
sys.path.insert(0, _BACKEND_DIR)
os.chdir(_BACKEND_DIR)

from app import app  # noqa: E402


@pytest.fixture
def client():
    """Flask test client."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


VALID_INPUT = {
    "location": "Whitefield",
    "total_sqft": 1200,
    "bhk": 2,
    "bath": 2,
    "balcony": 1,
    "ready_to_move": "yes",
}


class TestHealth:
    """GET / — health check."""

    def test_health_returns_status(self, client):
        resp = client.get("/")
        data = resp.get_json()
        assert resp.status_code == 200
        assert "status" in data
        assert "Bengaluru" in data["status"]
        assert "database" in data


class TestLocations:
    """GET /locations — supported location list."""

    def test_locations_returns_list(self, client):
        resp = client.get("/locations")
        data = resp.get_json()
        assert resp.status_code == 200
        assert "locations" in data
        assert data["count"] == len(data["locations"])
        assert "Whitefield" in data["locations"]


class TestPredictValidation:
    """POST /predict — validation edge cases."""

    def test_valid_input_returns_prediction(self, client):
        resp = client.post("/predict", json=VALID_INPUT)
        data = resp.get_json()
        assert resp.status_code == 200
        assert "predicted_price" in data
        assert isinstance(data["predicted_price"], float)
        assert data["predicted_price"] > 0
        assert data["currency"] == "INR"
        assert "predicted_price_lakhs" in data
        assert "price_display" in data
        assert data["price_display"].startswith("₹")

    def test_valid_input_has_conformal_interval(self, client):
        resp = client.post("/predict", json=VALID_INPUT)
        data = resp.get_json()
        assert "confidence_interval" in data
        ci = data["confidence_interval"]
        assert "low" in ci and "high" in ci
        assert ci["low"] < data["predicted_price"] < ci["high"]
        assert ci["low"] > 0
        assert data["interval_method"] == "split_conformal_90"

    def test_prediction_is_believable_for_bengaluru(self, client):
        # A 1200 sqft 2BHK in Whitefield should be Rs 30L - Rs 3Cr
        resp = client.post("/predict", json=VALID_INPUT)
        data = resp.get_json()
        lakhs = data["predicted_price_lakhs"]
        assert 20 <= lakhs <= 300

    def test_missing_field_returns_422(self, client):
        resp = client.post("/predict", json={"total_sqft": 1200})
        data = resp.get_json()
        assert resp.status_code == 422
        assert "details" in data
        assert len(data["details"]) > 0

    def test_unknown_location_returns_422(self, client):
        payload = VALID_INPUT.copy()
        payload["location"] = "Atlantis"
        resp = client.post("/predict", json=payload)
        data = resp.get_json()
        assert resp.status_code == 422
        assert any(d["field"] == "location" for d in data["details"])

    def test_other_location_is_accepted(self, client):
        payload = VALID_INPUT.copy()
        payload["location"] = "other"
        resp = client.post("/predict", json=payload)
        assert resp.status_code == 200

    def test_invalid_range_returns_422(self, client):
        payload = VALID_INPUT.copy()
        payload["bath"] = 99
        resp = client.post("/predict", json=payload)
        data = resp.get_json()
        assert resp.status_code == 422
        assert any("Bathrooms" in d["message"] for d in data["details"])

    def test_empty_body_returns_error(self, client):
        resp = client.post("/predict", data="not-json", content_type="application/json")
        assert resp.status_code >= 400


class TestMetrics:
    """GET /metrics — model comparison data."""

    def test_metrics_returns_comparison(self, client):
        resp = client.get("/metrics")
        data = resp.get_json()
        assert resp.status_code == 200
        assert "comparison" in data
        assert "best_model" in data
        assert "dataset_size" in data
        assert data["dataset_size"] > 10000
        assert "feature_importance" in data
        assert data["currency"] == "INR"


class TestDatabaseEndpoints:
    """GET /history and /stats — work offline."""

    def test_history_returns_predictions_or_error(self, client):
        resp = client.get("/history")
        data = resp.get_json()
        assert resp.status_code in (200, 503)
        if resp.status_code == 503:
            assert "Database not available" in data["error"]

    def test_stats_returns_aggregates_or_error(self, client):
        resp = client.get("/stats")
        data = resp.get_json()
        assert resp.status_code in (200, 503)
        if resp.status_code == 503:
            assert "Database not available" in data["error"]
