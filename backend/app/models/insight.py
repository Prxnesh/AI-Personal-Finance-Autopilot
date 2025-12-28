from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class Insight(Base):
    __tablename__ = "insights"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Insight details
    insight_type = Column(String, nullable=False)  # anomaly, trend, pattern, subscription
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    
    # AI explanation
    data_used = Column(JSON)  # Store the data points used for this insight
    reasoning = Column(Text, nullable=False)
    confidence = Column(Float, nullable=False)
    
    # Time period
    period_start = Column(DateTime)
    period_end = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="insights")
