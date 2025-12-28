from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from .base import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Pattern learning
    description_pattern = Column(String, nullable=False, unique=True)
    learned_category = Column(String, nullable=False)
    confidence = Column(Float, default=1.0)
    usage_count = Column(Integer, default=1)  # Track how often this pattern is used
    
    # Relationships
    user = relationship("User")
