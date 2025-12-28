from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# User Schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


# Transaction Schemas
class TransactionBase(BaseModel):
    date: datetime
    description: str
    amount: float
    is_credit: bool
    category: str
    category_confidence: float = 0.0


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    category: Optional[str] = None


class TransactionResponse(BaseModel):
    id: int
    user_id: int
    date: datetime
    description: str
    amount: float
    is_credit: bool
    category: str
    category_confidence: float
    user_overridden: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Upload Response
class UploadResponse(BaseModel):
    message: str
    transactions_processed: int
    transactions_added: int
    duplicates_skipped: int
    errors: List[str] = []


# Dashboard Schemas
class CategorySummary(BaseModel):
    category: str
    total: float
    count: int
    percentage: float


class MonthlySummary(BaseModel):
    month: str
    total_income: float
    total_expenses: float
    net_savings: float
    categories: List[CategorySummary]


class CashflowPoint(BaseModel):
    date: str
    income: float
    expenses: float
    balance: float


class DashboardResponse(BaseModel):
    current_month: MonthlySummary
    cashflow_trend: List[CashflowPoint]
    top_categories: List[CategorySummary]


# Insight Schemas
class InsightResponse(BaseModel):
    id: int
    insight_type: str
    title: str
    description: str
    data_used: dict
    reasoning: str
    confidence: float
    period_start: Optional[datetime]
    period_end: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# Prediction Schemas
class PredictionResponse(BaseModel):
    id: int
    prediction_type: str
    target_month: datetime
    predicted_value: float
    category: Optional[str]
    explanation: str
    method_used: str
    confidence: float
    supporting_data: dict
    created_at: datetime

    class Config:
        from_attributes = True


# Recommendation Schemas
class RecommendationResponse(BaseModel):
    type: str
    title: str
    description: str
    rationale: str
    supporting_data: dict
    estimated_impact: float
    confidence: float
