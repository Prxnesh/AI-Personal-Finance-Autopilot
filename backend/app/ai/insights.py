from typing import List, Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict
import statistics
from sqlalchemy.orm import Session
from app.models import Transaction, Insight



class InsightsEngine:
    """
    AI engine for generating financial insights
    """
    
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id
    
    def generate_all_insights(self) -> List[Insight]:
        """
        Generate all types of insights
        """
        insights = []
        
        # Get recent transactions
        transactions = self.db.query(Transaction).filter(
            Transaction.user_id == self.user_id
        ).order_by(Transaction.date.desc()).all()
        
        if not transactions:
            return insights
        
        # Generate different insight types
        insights.extend(self._detect_spending_anomalies(transactions))
        insights.extend(self._analyze_month_over_month(transactions))
        insights.extend(self._detect_recurring_subscriptions(transactions))
        insights.extend(self._identify_spending_patterns(transactions))
        
        return insights
    
    def _detect_spending_anomalies(self, transactions: List[Transaction]) -> List[Insight]:
        """
        Detect unusual spending patterns
        """
        insights = []
        
        # Group by category
        category_amounts = defaultdict(list)
        for t in transactions:
            if not t.is_credit:  # Only expenses
                category_amounts[t.category].append(t.amount)
        
        # Detect anomalies in each category
        for category, amounts in category_amounts.items():
            if len(amounts) < 5:  # Need enough data
                continue
            
            mean_amount = statistics.mean(amounts)
            stdev_amount = statistics.stdev(amounts) if len(amounts) > 1 else 0
            
            # Find transactions that are 2 standard deviations above mean
            for t in transactions:
                if t.category == category and not t.is_credit:
                    if stdev_amount > 0 and t.amount > mean_amount + 2 * stdev_amount:
                        insight = Insight(
                            user_id=self.user_id,
                            insight_type="anomaly",
                            title=f"Unusually High {category} Expense",
                            description=f"You spent ${t.amount:.2f} on {t.description}, which is significantly higher than your average {category} spending of ${mean_amount:.2f}",
                            data_used={
                                "transaction_id": t.id,
                                "amount": t.amount,
                                "average": round(mean_amount, 2),
                                "std_dev": round(stdev_amount, 2),
                                "category": category
                            },
                            reasoning=f"This transaction is {((t.amount - mean_amount) / stdev_amount):.1f} standard deviations above your average {category} spending. This could indicate an unusual purchase or potential error.",
                            confidence=min(0.95, 0.6 + min(0.35, (t.amount - mean_amount) / (mean_amount + 1))),
                            period_start=t.date,
                            period_end=t.date
                        )
                        insights.append(insight)
        
        return insights[:5]  # Limit to top 5
    
    def _analyze_month_over_month(self, transactions: List[Transaction]) -> List[Insight]:
        """
        Analyze spending changes month over month
        """
        insights = []
        
        # Group by month
        monthly_spending = defaultdict(lambda: {"income": 0, "expenses": 0})
        
        for t in transactions:
            month_key = t.date.strftime("%Y-%m")
            if t.is_credit:
                monthly_spending[month_key]["income"] += t.amount
            else:
                monthly_spending[month_key]["expenses"] += t.amount
        
        # Sort months
        sorted_months = sorted(monthly_spending.keys(), reverse=True)
        
        if len(sorted_months) >= 2:
            current_month = sorted_months[0]
            previous_month = sorted_months[1]
            
            current_expenses = monthly_spending[current_month]["expenses"]
            previous_expenses = monthly_spending[previous_month]["expenses"]
            
            if previous_expenses > 0:
                change_pct = ((current_expenses - previous_expenses) / previous_expenses) * 100
                
                if abs(change_pct) > 15:  # Significant change
                    direction = "increased" if change_pct > 0 else "decreased"
                    insight = Insight(
                        user_id=self.user_id,
                        insight_type="trend",
                        title=f"Monthly Spending {direction.capitalize()} by {abs(change_pct):.1f}%",
                        description=f"Your expenses {direction} from ${previous_expenses:.2f} in {previous_month} to ${current_expenses:.2f} in {current_month}",
                        data_used={
                            "current_month": current_month,
                            "current_expenses": round(current_expenses, 2),
                            "previous_month": previous_month,
                            "previous_expenses": round(previous_expenses, 2),
                            "change_percentage": round(change_pct, 2)
                        },
                        reasoning=f"Comparing your spending in {current_month} to {previous_month}, there's a {abs(change_pct):.1f}% {direction}. This could be due to seasonal changes, one-time purchases, or lifestyle adjustments.",
                        confidence=0.85,
                        period_start=datetime.strptime(previous_month, "%Y-%m"),
                        period_end=datetime.strptime(current_month, "%Y-%m")
                    )
                    insights.append(insight)
        
        return insights
    
    def _detect_recurring_subscriptions(self, transactions: List[Transaction]) -> List[Insight]:
        """
        Detect recurring subscriptions that user might want to review
        """
        insights = []
        
        # Group similar transactions
        description_groups = defaultdict(list)
        
        for t in transactions:
            if not t.is_credit and t.category == "Subscriptions":
                # Normalize description for grouping
                desc_normalized = t.description.lower().strip()
                description_groups[desc_normalized].append(t)
        
        # Find recurring patterns
        for desc, trans_list in description_groups.items():
            if len(trans_list) >= 3:  # At least 3 occurrences
                avg_amount = statistics.mean([t.amount for t in trans_list])
                total_spent = sum([t.amount for t in trans_list])
                
                # Calculate frequency
                dates = sorted([t.date for t in trans_list])
                if len(dates) > 1:
                    intervals = [(dates[i+1] - dates[i]).days for i in range(len(dates)-1)]
                    avg_interval = statistics.mean(intervals)
                    
                    frequency = "monthly" if 25 <= avg_interval <= 35 else "regularly"
                    
                    insight = Insight(
                        user_id=self.user_id,
                        insight_type="subscription",
                        title=f"Recurring Subscription: {desc.title()}",
                        description=f"You're paying approximately ${avg_amount:.2f} {frequency} for {desc}. Total spent: ${total_spent:.2f} over {len(trans_list)} payments.",
                        data_used={
                            "description": desc,
                            "occurrences": len(trans_list),
                            "average_amount": round(avg_amount, 2),
                            "total_spent": round(total_spent, 2),
                            "frequency_days": round(avg_interval, 1)
                        },
                        reasoning=f"Based on {len(trans_list)} transactions with similar descriptions occurring every {avg_interval:.0f} days on average, this appears to be a recurring subscription. Consider reviewing if you're still using this service.",
                        confidence=0.9,
                        period_start=dates[0],
                        period_end=dates[-1]
                    )
                    insights.append(insight)
        
        return insights[:3]  # Top 3 subscriptions
    
    def _identify_spending_patterns(self, transactions: List[Transaction]) -> List[Insight]:
        """
        Identify high-risk spending patterns
        """
        insights = []
        
        # Analyze category distribution
        category_totals = defaultdict(float)
        total_expenses = 0
        
        for t in transactions:
            if not t.is_credit:
                category_totals[t.category] += t.amount
                total_expenses += t.amount
        
        if total_expenses > 0:
            # Find categories that are disproportionately high
            for category, total in category_totals.items():
                percentage = (total / total_expenses) * 100
                
                # Alert if category is > 40% of total spending (except Rent)
                if percentage > 40 and category != "Rent":
                    insight = Insight(
                        user_id=self.user_id,
                        insight_type="pattern",
                        title=f"High {category} Spending Pattern",
                        description=f"{category} represents {percentage:.1f}% of your total spending (${total:.2f} out of ${total_expenses:.2f})",
                        data_used={
                            "category": category,
                            "category_total": round(total, 2),
                            "total_expenses": round(total_expenses, 2),
                            "percentage": round(percentage, 2)
                        },
                        reasoning=f"Your {category} expenses are significantly high compared to other categories. Consider setting a budget limit for this category to maintain balanced spending.",
                        confidence=0.8,
                        period_start=None,
                        period_end=None
                    )
                    insights.append(insight)
        
        return insights[:2]  # Top 2 patterns
