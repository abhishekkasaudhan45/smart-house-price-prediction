"""Tests for the House Price Predictor API."""

import pytest
import sys
import os

_BACKEND_DIR = os.path.join(os.path.dirname(__file__), "..", "Backend_API")
sys.path.insert(0, _BACKEND_DIR)
os.chdir(_BACKEND_DIR)

from app import app


@pytest.fixture
def client():
    """Flask test client."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


VALID_INPUT = {
    "area": 2000,
    "bedrooms": 3,
    "bathrooms": 2,
    "overall_qual": 7,
    "year_built": 2005,
    "has_pool": "no",
    "has_garage": "yes",
    "has_ac": "yes",
}


class TestHealth:
    """GET / — health check."""

    def test_health_returns_status(self, client):
        resp = client.get("/")
        data = resp.get_json()
        assert resp.status_code == 200
        assert "status" in data
        assert "Smart" in data["status"]
        assert "database" in data


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

    def test_valid_input_has_confidence_interval(self, client):
        resp = client.post("/predict", json=VALID_INPUT)
        data = resp.get_json()
        assert "confidence_interval" in data
        ci = data["confidence_interval"]
        assert "low" in ci and "high" in ci
        assert ci["low"] < ci["high"]
        assert ci["low"] > 0

    def test_missing_field_returns_422(self, client):
        resp = client.post("/predict", json={"area": 2500})
        data = resp.get_json()
        assert resp.status_code == 422
        assert "details" in data
        assert len(data["details"]) > 0

    def test_invalid_range_returns_422(self, client):
        payload = VALID_INPUT.copy()
        payload["bedrooms"] = 99
        resp = client.post("/predict", json=payload)
        data = resp.get_json()
        assert resp.status_code == 422
        assert any("Bedrooms" in d["message"] for d in data["details"])

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
        assert data["dataset_size"] == 1460
        assert "feature_importance" in data


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
