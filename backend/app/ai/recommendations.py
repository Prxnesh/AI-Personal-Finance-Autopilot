from typing import List, Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict
import statistics
from sqlalchemy.orm import Session
from ..models import Transaction, Prediction
from ..schemas import RecommendationResponse


class RecommendationEngine:
    """
    AI engine for generating actionable recommendations
    """
    
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id
    
    def generate_recommendations(self) -> List[RecommendationResponse]:
        """
        Generate all types of recommendations
        """
        recommendations = []
        
        # Get recent transactions (last 3 months)
        three_months_ago = datetime.now() - timedelta(days=90)
        transactions = self.db.query(Transaction).filter(
            Transaction.user_id == self.user_id,
            Transaction.date >= three_months_ago
        ).all()
        
        if not transactions:
            return recommendations
        
        # Get predictions for next month
        predictions = self.db.query(Prediction).filter(
            Prediction.user_id == self.user_id
        ).order_by(Prediction.created_at.desc()).limit(10).all()
        
        # Generate different recommendation types
        recommendations.extend(self._suggest_budget_limits(transactions))
        recommendations.extend(self._suggest_subscription_cancellations(transactions))
        recommendations.append(self._calculate_safe_to_spend(transactions, predictions))
        recommendations.extend(self._suggest_savings_opportunities(transactions))
        
        return [r for r in recommendations if r is not None]
    
    def _suggest_budget_limits(self, transactions: List[Transaction]) -> List[RecommendationResponse]:
        """
        Suggest budget limits for high-spending categories
        """
        recommendations = []
        
        # Calculate category spending
        category_spending = defaultdict(float)
        total_expenses = 0
        
        for t in transactions:
            if not t.is_credit:
                category_spending[t.category] += t.amount
                total_expenses += t.amount
        
        if total_expenses == 0:
            return recommendations
        
        # Find categories to budget
        for category, total in category_spending.items():
            percentage = (total / total_expenses) * 100
            
            # Suggest budget if category is >20% of spending (except Rent)
            if percentage > 20 and category not in ["Rent", "Income"]:
                # Suggest 10% reduction
                current_monthly = total / 3  # 3 months of data
                suggested_limit = current_monthly * 0.9
                potential_savings = current_monthly * 0.1
                
                recommendations.append(RecommendationResponse(
                    type="budget_limit",
                    title=f"Set a Budget Limit for {category}",
                    description=f"You're spending an average of ${current_monthly:.2f}/month on {category}, which is {percentage:.1f}% of your total expenses.",
                    rationale=f"By setting a monthly budget of ${suggested_limit:.2f} for {category}, you can reduce spending by 10% while still maintaining your lifestyle. This category represents a significant portion of your expenses, so small reductions can have meaningful impact.",
                    supporting_data={
                        "category": category,
                        "current_monthly_average": round(current_monthly, 2),
                        "suggested_limit": round(suggested_limit, 2),
                        "percentage_of_total": round(percentage, 2)
                    },
                    estimated_impact=potential_savings * 12,  # Annual savings
                    confidence=0.8
                ))
        
        return recommendations[:3]  # Top 3
    
    def _suggest_subscription_cancellations(self, transactions: List[Transaction]) -> List[RecommendationResponse]:
        """
        Identify subscriptions that might be unused
        """
        recommendations = []
        
        # Find recurring subscription transactions
        subscription_groups = defaultdict(list)
        
        for t in transactions:
            if not t.is_credit and t.category == "Subscriptions":
                desc_normalized = t.description.lower().strip()
                subscription_groups[desc_normalized].append(t)
        
        # Analyze each subscription
        for desc, trans_list in subscription_groups.items():
            if len(trans_list) >= 2:  # At least 2 payments
                avg_amount = statistics.mean([t.amount for t in trans_list])
                total_spent = sum([t.amount for t in trans_list])
                
                # Calculate annual cost
                dates = sorted([t.date for t in trans_list])
                if len(dates) > 1:
                    intervals = [(dates[i+1] - dates[i]).days for i in range(len(dates)-1)]
                    avg_interval = statistics.mean(intervals)
                    
                    # Estimate annual cost
                    payments_per_year = 365 / avg_interval if avg_interval > 0 else 12
                    annual_cost = avg_amount * payments_per_year
                    
                    # Recommend review if annual cost > $100
                    if annual_cost > 100:
                        recommendations.append(RecommendationResponse(
                            type="subscription_review",
                            title=f"Review Subscription: {desc.title()}",
                            description=f"You're paying ${avg_amount:.2f} every {avg_interval:.0f} days for this subscription.",
                            rationale=f"This subscription costs approximately ${annual_cost:.2f} per year. Review your usage and consider canceling if you're not actively using it. Even subscriptions below $20/month can add up to significant amounts annually.",
                            supporting_data={
                                "subscription": desc,
                                "average_payment": round(avg_amount, 2),
                                "frequency_days": round(avg_interval, 1),
                                "estimated_annual_cost": round(annual_cost, 2),
                                "total_paid": round(total_spent, 2)
                            },
                            estimated_impact=annual_cost,
                            confidence=0.75
                        ))
        
        # Sort by annual cost
        recommendations.sort(key=lambda r: r.estimated_impact, reverse=True)
        return recommendations[:3]  # Top 3
    
    def _calculate_safe_to_spend(
        self, 
        transactions: List[Transaction],
        predictions: List[Prediction]
    ) -> RecommendationResponse:
        """
        Calculate safe-to-spend amount for current month
        """
        today = datetime.now()
        current_month_start = datetime(today.year, today.month, 1)
        
        # Calculate spending so far this month
        month_to_date_expenses = sum([
            t.amount for t in transactions 
            if not t.is_credit and t.date >= current_month_start
        ])
        
        month_to_date_income = sum([
            t.amount for t in transactions 
            if t.is_credit and t.date >= current_month_start
        ])
        
        # Get predicted expenses for this month
        predicted_expenses = None
        for p in predictions:
            if p.prediction_type == "expense" and p.target_month.month == today.month:
                predicted_expenses = p.predicted_value
                break
        
        # If no prediction, estimate from historical average
        if predicted_expenses is None:
            historical = [t.amount for t in transactions if not t.is_credit]
            if historical:
                # Rough monthly estimate
                days_of_data = (max([t.date for t in transactions]) - min([t.date for t in transactions])).days
                if days_of_data > 0:
                    predicted_expenses = (sum(historical) / days_of_data) * 30
                else:
                    predicted_expenses = month_to_date_expenses
            else:
                predicted_expenses = month_to_date_expenses
        
        # Calculate days remaining
        if today.month == 12:
            next_month = datetime(today.year + 1, 1, 1)
        else:
            next_month = datetime(today.year, today.month + 1, 1)
        
        days_remaining = (next_month - today).days
        days_in_month = (next_month - current_month_start).days
        
        # Calculate safe to spend
        remaining_budget = predicted_expenses - month_to_date_expenses
        safe_to_spend_total = max(0, remaining_budget)
        safe_to_spend_daily = safe_to_spend_total / max(1, days_remaining)
        
        # Create recommendation
        description = f"You've spent ${month_to_date_expenses:.2f} so far this month"
        
        if month_to_date_income > 0:
            description += f" and received ${month_to_date_income:.2f} in income"
        
        description += f". With {days_remaining} days left, you can safely spend ${safe_to_spend_total:.2f} (${safe_to_spend_daily:.2f}/day)."
        
        rationale = f"Based on your predicted monthly expenses of ${predicted_expenses:.2f} and your spending so far, "
        
        if safe_to_spend_total > 0:
            spending_pace = (month_to_date_expenses / max(1, days_in_month - days_remaining))
            if spending_pace * days_in_month > predicted_expenses * 1.1:
                rationale += "you're currently spending faster than usual. Try to limit daily spending to stay on budget."
            else:
                rationale += "you're on track with your budget. Continue monitoring your spending to stay within limits."
        else:
            rationale += "you've already exceeded your typical monthly spending. Consider deferring non-essential purchases until next month."
        
        return RecommendationResponse(
            type="safe_to_spend",
            title="Safe-to-Spend Budget",
            description=description,
            rationale=rationale,
            supporting_data={
                "month_to_date_expenses": round(month_to_date_expenses, 2),
                "month_to_date_income": round(month_to_date_income, 2),
                "predicted_monthly_expenses": round(predicted_expenses, 2),
                "days_remaining": days_remaining,
                "safe_to_spend_total": round(safe_to_spend_total, 2),
                "safe_to_spend_daily": round(safe_to_spend_daily, 2)
            },
            estimated_impact=0,  # Not applicable
            confidence=0.7
        )
    
    def _suggest_savings_opportunities(self, transactions: List[Transaction]) -> List[RecommendationResponse]:
        """
        Identify opportunities to save money
        """
        recommendations = []
        
        # Analyze discretionary spending
        discretionary_categories = ["Shopping", "Entertainment", "Food"]
        
        category_totals = defaultdict(float)
        for t in transactions:
            if not t.is_credit and t.category in discretionary_categories:
                category_totals[t.category] += t.amount
        
        # Calculate monthly average (3 months of data)
        for category, total in category_totals.items():
            monthly_avg = total / 3
            
            # Suggest 15% reduction in discretionary spending
            if monthly_avg > 100:  # Only if meaningful amount
                potential_savings = monthly_avg * 0.15
                
                recommendations.append(RecommendationResponse(
                    type="savings_opportunity",
                    title=f"Reduce {category} Spending by 15%",
                    description=f"You spend an average of ${monthly_avg:.2f}/month on {category}.",
                    rationale=f"By reducing {category} expenses by just 15% (${potential_savings:.2f}/month), you could save ${potential_savings * 12:.2f} annually. This is a discretionary category where small behavioral changes can lead to significant savings without major lifestyle impact. Consider setting specific limits or finding lower-cost alternatives.",
                    supporting_data={
                        "category": category,
                        "current_monthly_average": round(monthly_avg, 2),
                        "suggested_reduction": round(potential_savings, 2),
                        "annual_savings": round(potential_savings * 12, 2)
                    },
                    estimated_impact=potential_savings * 12,
                    confidence=0.7
                ))
        
        # Sort by potential impact
        recommendations.sort(key=lambda r: r.estimated_impact, reverse=True)
        return recommendations[:2]  # Top 2
