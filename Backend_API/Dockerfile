FROM python:3.12

WORKDIR /app

# Copy requirements first (leverage Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy model artifacts and source code
COPY model.pkl scaler.pkl feature_columns.pkl model_metrics.pkl ./
COPY feature_importance.png ./
COPY app.py database.py models.py ./

EXPOSE 10000

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000"]
