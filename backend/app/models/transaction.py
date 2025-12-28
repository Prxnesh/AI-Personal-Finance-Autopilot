from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Transaction details
    date = Column(DateTime, nullable=False, index=True)
    description = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    is_credit = Column(Boolean, default=False)  # True for income, False for expense
    
    # Categorization
    category = Column(String, nullable=False)
    category_confidence = Column(Float, default=0.0)
    user_overridden = Column(Boolean, default=False)  # Track manual category changes
    
    # Metadata
    original_file = Column(String)  # Track source file
    file_hash = Column(String, index=True)  # For duplicate detection
    transaction_hash = Column(String, unique=True, index=True)  # Unique transaction identifier
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="transactions")

    # Composite index for efficient queries
    __table_args__ = (
        Index('ix_user_date', 'user_id', 'date'),
        Index('ix_user_category', 'user_id', 'category'),
    )
