FROM python:3.12-slim

WORKDIR /app

# Install system dependencies required by scikit-learn / numpy
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (leverage Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy model artifacts and source code
COPY model.pkl scaler.pkl label_encoders.pkl feature_columns.pkl model_metrics.pkl ./
COPY feature_importance.png actual_vs_predicted.png ./
COPY app.py .

EXPOSE 10000

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000"]
