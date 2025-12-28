from typing import List, Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict
import statistics
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from ..models import Transaction, Prediction


class PredictionEngine:
    """
    AI engine for predicting future expenses and income
    """
    
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id
    
    def generate_predictions(self, target_month: datetime = None) -> List[Prediction]:
        """
        Generate predictions for next month
        """
        if target_month is None:
            # Predict for next month
            today = datetime.now()
            if today.month == 12:
                target_month = datetime(today.year + 1, 1, 1)
            else:
                target_month = datetime(today.year, today.month + 1, 1)
        
        predictions = []
        
        # Get transactions from last 6 months
        six_months_ago = target_month - timedelta(days=180)
        transactions = self.db.query(Transaction).filter(
            Transaction.user_id == self.user_id,
            Transaction.date >= six_months_ago,
            Transaction.date < target_month
        ).all()
        
        if not transactions:
            return predictions
        
        # Generate different prediction types
        predictions.append(self._predict_total_expenses(transactions, target_month))
        predictions.append(self._predict_total_income(transactions, target_month))
        predictions.append(self._predict_savings(transactions, target_month))
        predictions.extend(self._predict_by_category(transactions, target_month))
        
        return [p for p in predictions if p is not None]
    
    def _predict_total_expenses(self, transactions: List[Transaction], target_month: datetime) -> Prediction:
        """
        Predict total expenses for next month using rolling average
        """
        # Group by month
        monthly_expenses = defaultdict(float)
        
        for t in transactions:
            if not t.is_credit:
                month_key = t.date.strftime("%Y-%m")
                monthly_expenses[month_key] += t.amount
        
        if not monthly_expenses:
            return None
        
        amounts = list(monthly_expenses.values())
        
        # Use 3-month rolling average with trend adjustment
        if len(amounts) >= 3:
            recent_avg = statistics.mean(amounts[-3:])
            
            # Calculate trend
            if len(amounts) >= 6:
                older_avg = statistics.mean(amounts[-6:-3])
                trend = (recent_avg - older_avg) / older_avg if older_avg > 0 else 0
            else:
                trend = 0
            
            # Adjust prediction with trend
            predicted = recent_avg * (1 + trend * 0.5)  # 50% trend weight
            confidence = 0.75
            method = "3-month rolling average with trend adjustment"
        else:
            # Simple average
            predicted = statistics.mean(amounts)
            confidence = 0.6
            method = "simple average"
        
        explanation = f"Based on your spending over the last {len(amounts)} months, we predict you'll spend approximately ${predicted:.2f} in {target_month.strftime('%B %Y')}. "
        
        if len(amounts) >= 3:
            explanation += f"Your average spending over the last 3 months was ${statistics.mean(amounts[-3:]):.2f}. "
            if trend > 0.1:
                explanation += f"We've detected an upward trend in your spending ({trend*100:.1f}%), so the prediction is adjusted higher."
            elif trend < -0.1:
                explanation += f"We've detected a downward trend in your spending ({abs(trend)*100:.1f}%), so the prediction is adjusted lower."
            else:
                explanation += "Your spending has been relatively stable."
        
        return Prediction(
            user_id=self.user_id,
            prediction_type="expense",
            target_month=target_month,
            predicted_value=predicted,
            explanation=explanation,
            method_used=method,
            confidence=confidence,
            supporting_data={
                "monthly_expenses": {k: round(v, 2) for k, v in list(monthly_expenses.items())[-6:]},
                "recent_average": round(statistics.mean(amounts[-3:]) if len(amounts) >= 3 else statistics.mean(amounts), 2),
                "trend": round(trend, 3) if len(amounts) >= 6 else 0
            }
        )
    
    def _predict_total_income(self, transactions: List[Transaction], target_month: datetime) -> Prediction:
        """
        Predict total income for next month
        """
        # Group by month
        monthly_income = defaultdict(float)
        
        for t in transactions:
            if t.is_credit:
                month_key = t.date.strftime("%Y-%m")
                monthly_income[month_key] += t.amount
        
        if not monthly_income:
            return None
        
        amounts = list(monthly_income.values())
        
        # Income is usually stable, use simple average
        predicted = statistics.mean(amounts[-3:]) if len(amounts) >= 3 else statistics.mean(amounts)
        std_dev = statistics.stdev(amounts) if len(amounts) > 1 else 0
        
        # Confidence based on stability
        if std_dev > 0:
            coefficient_of_variation = std_dev / predicted
            confidence = max(0.5, 0.9 - coefficient_of_variation)
        else:
            confidence = 0.95
        
        explanation = f"Based on your income history over the last {len(amounts)} months, we predict you'll receive approximately ${predicted:.2f} in {target_month.strftime('%B %Y')}. "
        
        if std_dev / predicted < 0.1:
            explanation += "Your income has been very stable."
        elif std_dev / predicted < 0.3:
            explanation += "Your income shows some variation but is relatively consistent."
        else:
            explanation += "Your income varies significantly month-to-month, so this prediction is less certain."
        
        return Prediction(
            user_id=self.user_id,
            prediction_type="income",
            target_month=target_month,
            predicted_value=predicted,
            explanation=explanation,
            method_used="rolling average",
            confidence=confidence,
            supporting_data={
                "monthly_income": {k: round(v, 2) for k, v in list(monthly_income.items())[-6:]},
                "average": round(predicted, 2),
                "std_dev": round(std_dev, 2)
            }
        )
    
    def _predict_savings(self, transactions: List[Transaction], target_month: datetime) -> Prediction:
        """
        Predict savings for next month
        """
        # Group by month
        monthly_data = defaultdict(lambda: {"income": 0, "expenses": 0})
        
        for t in transactions:
            month_key = t.date.strftime("%Y-%m")
            if t.is_credit:
                monthly_data[month_key]["income"] += t.amount
            else:
                monthly_data[month_key]["expenses"] += t.amount
        
        if not monthly_data:
            return None
        
        # Calculate historical savings
        monthly_savings = {k: v["income"] - v["expenses"] for k, v in monthly_data.items()}
        savings_list = list(monthly_savings.values())
        
        # Predict
        predicted = statistics.mean(savings_list[-3:]) if len(savings_list) >= 3 else statistics.mean(savings_list)
        
        explanation = f"Based on your income and expense patterns, we predict you'll save approximately ${predicted:.2f} in {target_month.strftime('%B %Y')}. "
        
        if predicted > 0:
            explanation += f"This represents a positive savings rate. "
            avg_income = statistics.mean([monthly_data[k]["income"] for k in list(monthly_data.keys())[-3:]])
            if avg_income > 0:
                savings_rate = (predicted / avg_income) * 100
                explanation += f"Your predicted savings rate is {savings_rate:.1f}%."
        else:
            explanation += "Warning: Based on trends, you may spend more than you earn this month. Consider reducing discretionary spending."
        
        return Prediction(
            user_id=self.user_id,
            prediction_type="savings",
            target_month=target_month,
            predicted_value=predicted,
            explanation=explanation,
            method_used="income minus expenses projection",
            confidence=0.7,
            supporting_data={
                "monthly_savings": {k: round(v, 2) for k, v in list(monthly_savings.items())[-6:]},
                "average": round(predicted, 2)
            }
        )
    
    def _predict_by_category(self, transactions: List[Transaction], target_month: datetime) -> List[Prediction]:
        """
        Predict spending by category
        """
        predictions = []
        
        # Group by month and category
        category_monthly = defaultdict(lambda: defaultdict(float))
        
        for t in transactions:
            if not t.is_credit:
                month_key = t.date.strftime("%Y-%m")
                category_monthly[t.category][month_key] += t.amount
        
        # Predict for top categories
        for category, monthly_data in category_monthly.items():
            if len(monthly_data) < 2:  # Need at least 2 months
                continue
            
            amounts = list(monthly_data.values())
            predicted = statistics.mean(amounts[-3:]) if len(amounts) >= 3 else statistics.mean(amounts)
            
            explanation = f"You typically spend ${predicted:.2f} per month on {category}. "
            
            # Add context
            if len(amounts) >= 2:
                recent = amounts[-1]
                if recent > predicted * 1.2:
                    explanation += "Last month was higher than usual, but we expect spending to normalize."
                elif recent < predicted * 0.8:
                    explanation += "Last month was lower than usual, but we expect spending to return to normal levels."
            
            predictions.append(Prediction(
                user_id=self.user_id,
                prediction_type="category",
                target_month=target_month,
                predicted_value=predicted,
                category=category,
                explanation=explanation,
                method_used="category rolling average",
                confidence=0.65,
                supporting_data={
                    "monthly_amounts": {k: round(v, 2) for k, v in list(monthly_data.items())[-6:]},
                    "average": round(predicted, 2)
                }
            ))
        
        # Return top 5 categories by predicted amount
        predictions.sort(key=lambda p: p.predicted_value, reverse=True)
        return predictions[:5]
