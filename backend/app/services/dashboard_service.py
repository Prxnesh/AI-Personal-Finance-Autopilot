from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import List, Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict
from app.models import Transaction
from app.schemas import MonthlySummary, CategorySummary, CashflowPoint, DashboardResponse



def get_dashboard_data(db: Session, user_id: int) -> DashboardResponse:
    """
    Get comprehensive dashboard data
    """
    # Get current month summary
    current_month = get_monthly_summary(db, user_id, datetime.now())
    
    # Get cashflow trend (last 6 months)
    cashflow_trend = get_cashflow_trend(db, user_id, months=6)
    
    # Get top categories
    top_categories = get_top_categories(db, user_id, limit=5)
    
    return DashboardResponse(
        current_month=current_month,
        cashflow_trend=cashflow_trend,
        top_categories=top_categories
    )


def get_monthly_summary(
    db: Session,
    user_id: int,
    target_date: datetime
) -> MonthlySummary:
    """
    Get summary for a specific month
    """
    # Get transactions for the month
    month_start = datetime(target_date.year, target_date.month, 1)
    
    if target_date.month == 12:
        month_end = datetime(target_date.year + 1, 1, 1)
    else:
        month_end = datetime(target_date.year, target_date.month + 1, 1)
    
    transactions = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.date >= month_start,
        Transaction.date < month_end
    ).all()
    
    # Calculate totals
    total_income = sum([t.amount for t in transactions if t.is_credit])
    total_expenses = sum([t.amount for t in transactions if not t.is_credit])
    net_savings = total_income - total_expenses
    
    # Category breakdown
    category_data = defaultdict(lambda: {"total": 0, "count": 0})
    
    for t in transactions:
        if not t.is_credit:  # Only expenses
            category_data[t.category]["total"] += t.amount
            category_data[t.category]["count"] += 1
    
    # Create category summaries
    categories = []
    for cat, data in category_data.items():
        percentage = (data["total"] / total_expenses * 100) if total_expenses > 0 else 0
        categories.append(CategorySummary(
            category=cat,
            total=data["total"],
            count=data["count"],
            percentage=percentage
        ))
    
    # Sort by total
    categories.sort(key=lambda c: c.total, reverse=True)
    
    return MonthlySummary(
        month=month_start.strftime("%Y-%m"),
        total_income=total_income,
        total_expenses=total_expenses,
        net_savings=net_savings,
        categories=categories
    )


def get_cashflow_trend(
    db: Session,
    user_id: int,
    months: int = 6
) -> List[CashflowPoint]:
    """
    Get cashflow trend over time
    """
    # Get transactions from last N months
    cutoff_date = datetime.now() - timedelta(days=months * 30)
    
    transactions = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.date >= cutoff_date
    ).order_by(Transaction.date).all()
    
    # Group by month
    monthly_data = defaultdict(lambda: {"income": 0, "expenses": 0})
    
    for t in transactions:
        month_key = t.date.strftime("%Y-%m")
        if t.is_credit:
            monthly_data[month_key]["income"] += t.amount
        else:
            monthly_data[month_key]["expenses"] += t.amount
    
    # Create cashflow points
    cashflow = []
    running_balance = 0
    
    for month in sorted(monthly_data.keys()):
        data = monthly_data[month]
        running_balance += data["income"] - data["expenses"]
        
        cashflow.append(CashflowPoint(
            date=month,
            income=data["income"],
            expenses=data["expenses"],
            balance=running_balance
        ))
    
    return cashflow


def get_top_categories(
    db: Session,
    user_id: int,
    limit: int = 5
) -> List[CategorySummary]:
    """
    Get top spending categories (all time)
    """
    # Get all expense transactions
    transactions = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.is_credit == False
    ).all()
    
    # Group by category
    category_data = defaultdict(lambda: {"total": 0, "count": 0})
    total_expenses = 0
    
    for t in transactions:
        category_data[t.category]["total"] += t.amount
        category_data[t.category]["count"] += 1
        total_expenses += t.amount
    
    # Create summaries
    categories = []
    for cat, data in category_data.items():
        percentage = (data["total"] / total_expenses * 100) if total_expenses > 0 else 0
        categories.append(CategorySummary(
            category=cat,
            total=data["total"],
            count=data["count"],
            percentage=percentage
        ))
    
    # Sort and limit
    categories.sort(key=lambda c: c.total, reverse=True)
    return categories[:limit]
