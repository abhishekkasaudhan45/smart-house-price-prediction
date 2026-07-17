"""SQLAlchemy models for the house price predictor."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, String, DateTime
from database import Base


class Prediction(Base):
    """Stores each prediction request and result (Bengaluru schema)."""

    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    total_sqft = Column(Float, nullable=False)
    bhk = Column(Integer, nullable=False)
    bath = Column(Integer, nullable=False)
    balcony = Column(Integer, nullable=False)
    location = Column(String(100), nullable=False)
    ready_to_move = Column(Integer, nullable=False)
    predicted_price = Column(Float, nullable=False)
    confidence_low = Column(Float, nullable=False)
    confidence_high = Column(Float, nullable=False)
    model_used = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
