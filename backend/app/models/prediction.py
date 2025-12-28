from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Prediction details
    prediction_type = Column(String, nullable=False)  # expense, income, savings, category
    target_month = Column(DateTime, nullable=False, index=True)
    
    # Predicted values
    predicted_value = Column(Float, nullable=False)
    category = Column(String)  # For category-specific predictions
    
    # Explanation
    explanation = Column(Text, nullable=False)
    method_used = Column(String, nullable=False)  # rolling_average, trend_analysis, etc.
    confidence = Column(Float, nullable=False)
    supporting_data = Column(JSON)  # Historical data used
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="predictions")
