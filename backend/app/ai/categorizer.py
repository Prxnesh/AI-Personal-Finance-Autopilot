from typing import Dict, Tuple
import re
from datetime import datetime


# Predefined categories
CATEGORIES = [
    "Food",
    "Rent",
    "Transport",
    "Shopping",
    "Subscriptions",
    "Utilities",
    "Income",
    "Entertainment",
    "Healthcare",
    "Education",
    "Other"
]


# Rule-based patterns for categorization
CATEGORY_PATTERNS = {
    "Food": [
        r'\b(restaurant|cafe|coffee|food|pizza|burger|meal|dining|takeout|delivery|uber\s*eats|doordash|grubhub|zomato|swiggy|mcdonald|kfc|subway|starbucks|dunkin)\b',
        r'\b(grocery|supermarket|walmart|target|whole\s*foods|trader\s*joe|safeway|kroger|publix|aldi)\b',
    ],
    "Rent": [
        r'\b(rent|landlord|property\s*management|housing|lease)\b',
    ],
    "Transport": [
        r'\b(uber|lyft|taxi|cab|metro|subway|bus|train|gas|fuel|petrol|parking|toll|vehicle|car\s*payment|auto|transport)\b',
    ],
    "Shopping": [
        r'\b(amazon|ebay|shop|store|retail|mall|purchase|clothing|fashion|nike|adidas|zara|h&m)\b',
    ],
    "Subscriptions": [
        r'\b(subscription|netflix|spotify|hulu|disney|prime|apple\s*music|youtube\s*premium|membership|recurring)\b',
    ],
    "Utilities": [
        r'\b(electric|electricity|water|gas|utility|internet|phone|mobile|telecom|att|verizon|t-mobile)\b',
    ],
    "Income": [
        r'\b(salary|payroll|wage|income|deposit|transfer\s*from|received|payment\s*received|refund)\b',
    ],
    "Entertainment": [
        r'\b(movie|cinema|theater|game|gaming|xbox|playstation|steam|entertainment|concert|ticket|event)\b',
    ],
    "Healthcare": [
        r'\b(pharmacy|medical|doctor|hospital|clinic|health|medicine|prescription|dental|vision|insurance)\b',
    ],
    "Education": [
        r'\b(tuition|education|school|college|university|course|training|book|learning)\b',
    ],
}


class RuleBasedCategorizer:
    """
    Rule-based categorization using pattern matching
    """
    
    def __init__(self):
        # Compile all patterns for efficiency
        self.compiled_patterns = {}
        for category, patterns in CATEGORY_PATTERNS.items():
            self.compiled_patterns[category] = [
                re.compile(pattern, re.IGNORECASE) for pattern in patterns
            ]
    
    def categorize(self, description: str, is_credit: bool) -> Tuple[str, float]:
        """
        Categorize a transaction based on description
        Returns: (category, confidence)
        """
        # Default to Income for credits if no other pattern matches
        if is_credit:
            default_category = "Income"
        else:
            default_category = "Other"
        
        # Clean description
        desc_lower = description.lower()
        
        # Try to match patterns
        matches = []
        for category, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                if pattern.search(desc_lower):
                    matches.append((category, 0.8))  # Base confidence for pattern match
                    break
        
        # If multiple matches, prefer non-Income for debits, Income for credits
        if len(matches) > 1:
            if is_credit:
                # Prefer Income for credits
                income_match = [m for m in matches if m[0] == "Income"]
                if income_match:
                    return income_match[0]
            else:
                # Prefer non-Income for debits
                non_income = [m for m in matches if m[0] != "Income"]
                if non_income:
                    return non_income[0]
        
        # Return first match or default
        if matches:
            return matches[0]
        else:
            return (default_category, 0.3)  # Low confidence for default


class LearnedCategorizer:
    """
    Learns from user overrides to improve categorization
    """
    
    def __init__(self, learned_patterns: Dict[str, str] = None):
        """
        learned_patterns: dict of {description_pattern: category}
        """
        self.learned_patterns = learned_patterns or {}
    
    def categorize(self, description: str) -> Tuple[str, float]:
        """
        Try to categorize based on learned patterns
        Returns: (category, confidence) or (None, 0) if no match
        """
        desc_lower = description.lower()
        
        # Exact match first
        if desc_lower in self.learned_patterns:
            return (self.learned_patterns[desc_lower], 1.0)
        
        # Fuzzy match - check if any learned pattern is in description
        for pattern, category in self.learned_patterns.items():
            if pattern in desc_lower or desc_lower in pattern:
                # Calculate similarity-based confidence
                similarity = len(pattern) / max(len(desc_lower), len(pattern))
                confidence = min(0.95, 0.7 + similarity * 0.25)
                return (category, confidence)
        
        return (None, 0.0)


class HybridCategorizer:
    """
    Combines rule-based and learned categorization
    """
    
    def __init__(self, learned_patterns: Dict[str, str] = None):
        self.rule_categorizer = RuleBasedCategorizer()
        self.learned_categorizer = LearnedCategorizer(learned_patterns)
    
    def categorize(self, description: str, is_credit: bool) -> Tuple[str, float]:
        """
        Categorize using hybrid approach
        Learned patterns take precedence over rules
        Returns: (category, confidence)
        """
        # Try learned patterns first
        learned_cat, learned_conf = self.learned_categorizer.categorize(description)
        
        if learned_cat and learned_conf > 0.6:
            return (learned_cat, learned_conf)
        
        # Fall back to rule-based
        rule_cat, rule_conf = self.rule_categorizer.categorize(description, is_credit)
        
        # If learned has low confidence but exists, blend with rules
        if learned_cat and learned_conf > 0.3:
            # Prefer learned if confidence is close
            if learned_conf > rule_conf - 0.2:
                return (learned_cat, learned_conf)
        
        return (rule_cat, rule_conf)
    
    def update_learned_patterns(self, patterns: Dict[str, str]):
        """
        Update learned patterns
        """
        self.learned_categorizer.learned_patterns.update(patterns)
