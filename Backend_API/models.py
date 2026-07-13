"""SQLAlchemy models for the house price predictor."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, String, DateTime
from database import Base


class Prediction(Base):
    """Stores each prediction request and result."""

    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    area = Column(Float, nullable=False)
    bedrooms = Column(Integer, nullable=False)
    bathrooms = Column(Integer, nullable=False)
    stories = Column(Integer, nullable=False)
    parking = Column(Integer, nullable=False)
    has_pool = Column(String(5), nullable=False)
    has_garage = Column(String(5), nullable=False)
    has_ac = Column(String(5), nullable=False)
    predicted_price = Column(Float, nullable=False)
    confidence_low = Column(Float, nullable=False)
    confidence_high = Column(Float, nullable=False)
    model_used = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
